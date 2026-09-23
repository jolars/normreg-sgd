"""Map retained numerical discrepancies and clip saved Mushroom predictors.

These are post hoc diagnostics of frozen results. No candidates are retrained,
reselected, or removed from the original summaries.
"""

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from practical_spec import LAWS, load_mushroom, mushroom_data  # noqa: E402

ARCHIVE = ROOT / "results/variance-scaling-followup"
OUTPUT = ROOT / "results/review-diagnostics"
SCALES = ("none", "sd", "damped", "variance")
LABELS = ("None", "SD", "Damped", "Variance")


def statistics(values):
    values = np.asarray(values)
    assert np.isfinite(values).all()
    return {
        "n": len(values),
        "mean": float(values.mean()),
        "mcse": float(values.std(ddof=1) / np.sqrt(len(values))),
        "median": float(np.median(values)),
        "p95": float(np.quantile(values, 0.95)),
        "maximum": float(values.max()),
    }


def calculate():
    sources = {
        Path(__file__).relative_to(ROOT),
        Path("experiments/practical_spec.py"),
        Path("data/mushroom/agaricus-lepiota.data"),
        Path("uv.lock"),
    }

    def read_json(path):
        sources.add(path.relative_to(ROOT))
        return json.loads(path.read_text())

    audit = read_json(ARCHIVE / "audit.json")
    synthetic = read_json(ARCHIVE / "synthetic.json")
    metadata = {(m["case"], m["rep"]): m for m in synthetic["replications"]}
    grouped = defaultdict(list)
    records = []
    for violation in audit["gate_violations"]:
        assert violation["stage"] == 0
        meta = metadata[violation["case"], violation["rep"]]
        assert meta["validation_rare"] == 0
        record = dict(violation)
        if violation["kind"] == "selected_prediction":
            query = synthetic["queries"][violation["query"]]
            path = ARCHIVE / meta["archive"]
            sources.add(path.relative_to(ROOT))
            with np.load(path) as data:
                candidate = int(
                    data[meta["prefix"] + "selections"][violation["query"], 0]
                )
                test = data[meta["prefix"] + "test"].reshape(-1, 2)[candidate]
            record.update(
                selection=query,
                candidate=synthetic["candidates"][candidate],
                archived_test_risk=test.tolist(),
            )
            grouped[violation["case"], query["scale"]].append(record)
        elif "configuration" in violation:
            record["configuration_details"] = synthetic["configurations"][
                violation["configuration"]
            ]
        records.append(record)

    affected = []
    for (case, scale), entries in sorted(grouped.items()):
        primary = [
            e
            for e in entries
            if e["selection"]["search"] == "expanded"
            and e["selection"]["objective"] == 0
            and e["selection"]["cap"] == 2048
        ]
        summary = read_json(ARCHIVE / f"synthetic-summary-c{case}.json")
        row = next(
            s
            for s in summary["selections"]
            if s["arm"] == "centered_fitted"
            and s["scale"] == scale
            and s["objective"] == 0
            and s["cap"] == 2048
            and s["search"] == "expanded"
            and s["stratum"] == "all"
        )
        contribution = sum(e["archived_test_risk"][1] for e in primary) / 128
        affected.append(
            dict(
                case=case,
                law=LAWS[case]["name"],
                scale=scale,
                replications=sorted({e["rep"] for e in entries}),
                records=len(entries),
                primary_records=len(primary),
                primary_rare_mean=row["rare"]["mean"],
                primary_rare_mean_contribution=contribution,
                primary_rare_mean_fraction=contribution / row["rare"]["mean"],
                searches=sorted({e["selection"]["search"] for e in entries}),
                caps=sorted({e["selection"]["cap"] for e in entries}),
            )
        )

    manifest = read_json(ARCHIVE / "mushroom.json")
    raw_data = load_mushroom()
    clipping = []
    maximum_reconstruction_error = 0.0
    for case in range(2):
        queries = [
            (i, q)
            for i, q in enumerate(manifest["queries"])
            if q["arm"] == "centered_fitted"
            and q["cap"] == 8192
            and q["search"] == "expanded"
        ]
        observations = defaultdict(list)
        for meta in manifest["replications"]:
            if meta["case"] != case:
                continue
            parts, details = mushroom_data(raw_data, case, meta["rep"])
            assert details["names"] == meta["names"]
            x, y, rare = parts[2]
            assert np.isin(y, (0, 1)).all() and rare.any()
            path = ARCHIVE / meta["archive"]
            sources.add(path.relative_to(ROOT))
            with np.load(path) as data:
                prefix = meta["prefix"]
                coefficients = data[prefix + "coefficients"]
                coefficients = coefficients.reshape(-1, coefficients.shape[-1])
                selections = data[prefix + "selections"]
                stored = data[prefix + "test"].reshape(-1, 2)
                for qi, query in queries:
                    selected = int(selections[qi, 0])
                    coefficient = coefficients[selected]
                    prediction = x @ coefficient[1:] + coefficient[0]
                    raw = (prediction - y) ** 2 / 2
                    clipped = (np.clip(prediction, 0, 1) - y) ** 2 / 2
                    assert np.all(clipped <= raw + 1e-14)
                    assert np.all(clipped <= 0.5)
                    loss = np.array([raw.mean(), raw[rare].mean()])
                    error = float(np.max(np.abs(loss - stored[selected])))
                    maximum_reconstruction_error = max(
                        maximum_reconstruction_error, error
                    )
                    np.testing.assert_allclose(
                        loss, stored[selected], rtol=1e-11, atol=1e-12
                    )
                    observations[query["scale"], query["objective"]].append(
                        dict(
                            replication=meta["rep"],
                            validation_rare=meta["validation_rare"],
                            raw=loss.tolist(),
                            clipped=[
                                float(clipped.mean()),
                                float(clipped[rare].mean()),
                            ],
                        )
                    )
        for (scale, objective), values in observations.items():
            clipping.append(
                dict(
                    case=case,
                    scale=scale,
                    objective=objective,
                    replications=values,
                    **{
                        treatment: {
                            risk: statistics([v[treatment][i] for v in values])
                            for i, risk in enumerate(("aggregate", "rare"))
                        }
                        for treatment in ("raw", "clipped")
                    },
                )
            )
    return dict(
        purpose="Post hoc diagnostics; original candidates and selections retained.",
        numerical_records=records,
        affected_summaries=affected,
        clipping=clipping,
        clipping_scope={
            "arm": "centered_fitted",
            "cap": 8192,
            "search": "expanded",
            "selection": "original, unclipped validation scores",
            "interval": [0, 1],
            "retraining": False,
            "reselection": False,
            "max_raw_loss_reconstruction_error": maximum_reconstruction_error,
        },
        source_sha256={
            str(path): hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in sorted(sources)
        },
    )


def tables(report):
    lines = [
        r"\begin{table}[ht]",
        r"  \centering",
        r"  \small",
        r"  \begin{tabular}{llrrl}",
        r"    \toprule",
        r"    Law & Scaling & Checks & Primary share & Replications (zero-based) \\",
        r"    \midrule",
    ]
    names = {
        "rarer_C1": "Rarer C1",
        "rarer_C2": "Rarer C2",
        "opposite_disjoint": "Opposite, disjoint",
        "common_only": "Common only",
    }
    for row in report["affected_summaries"]:
        share = (
            f"{100 * row['primary_rare_mean_fraction']:.2f}\\%"
            if row["primary_records"]
            else "---"
        )
        reps = ", ".join(str(r) for r in row["replications"])
        label = LABELS[SCALES.index(row["scale"])]
        lines.append(
            f"    {names[row['law']]} & {label} & {row['records']} & {share} & {reps} "
            + r"\\"
        )
    lines.extend(
        [
            r"    \bottomrule",
            r"  \end{tabular}",
            r"  \caption{",
            "    Selected-prediction discrepancies in the centered/fitted synthetic",
            "    arm. Checks count selection queries, including repeated choices.",
            "    Primary share is the fraction of the archived mean rare risk",
            "    contributed by flagged selections at cap $2048$, under aggregate",
            "    validation and the expanded rate grid with original stops. A dash",
            "    means this primary query has no flagged selection. These shares",
            "    locate dependence on discrepant paths; they do not correct",
            "    their risks.",
            r"  }",
            r"  \label{tab:review-audit-impact}",
            r"\end{table}",
            "",
            r"\begin{table}[ht]",
            r"  \centering",
            r"  \small",
            r"  \begin{tabular}{llrrrr}",
            r"    \toprule",
            r"    Selection & Scaling & Raw aggregate & Clipped aggregate",
            r"      & Raw rare & Clipped rare \\",
            r"    \midrule",
        ]
    )
    for objective in range(2):
        for scale, label in zip(SCALES, LABELS, strict=True):
            row = next(
                r
                for r in report["clipping"]
                if r["case"] == 1
                and r["scale"] == scale
                and r["objective"] == objective
            )
            values = [
                row[treatment][risk]["mean"]
                for risk in ("aggregate", "rare")
                for treatment in ("raw", "clipped")
            ]
            lines.append(
                f"    {('Aggregate', 'Rare')[objective]} & {label} & "
                + " & ".join(f"{v:.6f}" for v in values)
                + r" \\"
            )
    lines.extend(
        [
            r"    \bottomrule",
            r"  \end{tabular}",
            r"  \caption{",
            "    Post hoc clipping to $[0,1]$ of the saved Mushroom predictors in",
            r"    \cref{tab:conference-mushroom}, with $n=2048$, cap $8192$,",
            "    centered predictors, and a fitted intercept. Means include all 32",
            "    partitions. Selection retains the original unclipped validation",
            "    scores; clipping requires no additional training. The diagnostic",
            "    archive also reports MCSEs, quantiles, and the smaller sample size.",
            r"  }",
            r"  \label{tab:review-clipping}",
            r"\end{table}",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--update-paper", action="store_true")
    args = parser.parse_args()
    report = calculate()
    artifacts = {
        "summary.json": json.dumps(report, indent=2, allow_nan=False) + "\n",
        "tables.tex": tables(report),
    }
    paper = ROOT / "paper/main.tex"
    manuscript = paper.read_text()
    for name, content in zip(
        ("AUDIT", "CLIPPING"),
        artifacts["tables.tex"].strip().split("\n\n"),
        strict=True,
    ):
        start = f"% BEGIN GENERATED REVIEW {name} TABLE\n"
        end = f"% END GENERATED REVIEW {name} TABLE"
        pattern = re.escape(start) + r".*?" + re.escape(end)
        assert len(re.findall(pattern, manuscript, re.DOTALL)) == 1
        if args.update_paper:
            assert not args.check
            manuscript = re.sub(
                pattern,
                lambda _: start + content + "\n" + end,
                manuscript,
                flags=re.DOTALL,
            )
        elif args.check:
            assert re.search(pattern, manuscript, re.DOTALL)[0] == (
                start + content + "\n" + end
            ), f"Regenerate the {name.lower()} table in paper/main.tex."
    if args.update_paper:
        paper.write_text(manuscript)
    if args.check:
        for name, content in artifacts.items():
            assert (OUTPUT / name).read_text() == content, name
        print("Review diagnostics, frozen-input hashes, and generated tables match.")
    else:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        for name, content in artifacts.items():
            (OUTPUT / name).write_text(content)
        print(f"Wrote {OUTPUT.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()
