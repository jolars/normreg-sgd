"""Paired fixed-offset sensitivity, selected paths, and tuning diagnostics."""

import json

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mushroom_sensitivity_spec import (
    BATCHES,
    CHECKPOINTS,
    FACTORS,
    OUTPUT,
    REPS,
    SCALES,
    SIZES,
    configurations,
    select,
)
from practical_spec import load_mushroom, mushroom_data, sha256, write_json
from summarize_mushroom_rate_search import FEATURES, components, neighbor_diagnostic
from summarize_practical_selection import statistics


def summarize():
    manifest = json.loads((OUTPUT / "manifest.json").read_text())
    rows, queries = manifest["candidates"], manifest["queries"]
    raw = load_mushroom()
    result = dict(cases=[], selections=[], contrasts=[], boundaries=[], paths=[])
    for case in range(len(SIZES)):
        metas = [m for m in manifest["replications"] if m["case"] == case]
        tests, validations, selections, statuses, failures, features, etas = (
            [] for _ in range(7)
        )
        for meta in metas:
            with np.load(OUTPUT / meta["archive"]) as archive:
                coeff = archive["coefficients"]
                tests.append(archive["test"])
                validations.append(archive["validation"])
                selections.append(archive["selections"])
                statuses.append(archive["status"])
                failures.append(archive["failure_update"])
                etas.append(archive["parameter_eta"])
                parts, _ = mushroom_data(raw, case, meta["rep"])
                x, _, rare = parts[2]
                conditional = np.asarray(x[rare].mean(axis=0)).ravel()
                features.append(
                    components(
                        coeff,
                        archive["parameter_mu"],
                        meta["names"],
                        conditional,
                        archive["centered_intercepts"],
                    ).reshape(*coeff.shape[:-1], len(FEATURES))
                )
        tests, validations, selections, statuses, failures, features, etas = map(
            np.array,
            (tests, validations, selections, statuses, failures, features, etas),
        )
        ids = selections[:, :, 0]
        flat_tests, flat_features = (
            tests.reshape(REPS, -1, 2),
            features.reshape(REPS, -1, len(FEATURES)),
        )
        selected_test = flat_tests[np.arange(REPS)[:, None], ids]
        selected_features = flat_features[np.arange(REPS)[:, None], ids]
        strata = dict(
            all=np.ones(REPS, dtype=bool),
            train_absent=np.array([m["train_rare"] == 0 for m in metas]),
            train_present=np.array([m["train_rare"] > 0 for m in metas]),
            validation_absent=np.array([m["validation_rare"] == 0 for m in metas]),
            validation_present=np.array([m["validation_rare"] > 0 for m in metas]),
        )
        result["cases"].append(
            dict(
                case=case,
                n=SIZES[case][0],
                endpoints=int(statuses.size),
                failed_endpoints=int(statuses.sum()),
                failed_paths=int(np.count_nonzero(failures)),
                train_rare=[m["train_rare"] for m in metas],
                validation_rare=[m["validation_rare"] for m in metas],
                test_rare=[m["test_rare"] for m in metas],
                failures_by_scale=[
                    dict(
                        scale=scale,
                        paths=int(np.count_nonzero(failures[:, :, ci])),
                        endpoints=int(statuses[:, :, :, ci].sum()),
                    )
                    for scale in SCALES
                    for ci in [
                        [
                            i
                            for i, c in enumerate(configurations())
                            if c["scale"] == scale
                        ]
                    ]
                ],
            )
        )
        for qi, q in enumerate(queries):
            chosen = [rows[i] for i in ids[:, qi]]
            ci = [i for i, c in enumerate(configurations()) if c["scale"] == q["scale"]]
            used = np.zeros(REPS)
            for bi, batch in enumerate(BATCHES):
                stop = failures[:, bi, ci] * batch
                used += np.minimum(np.where(stop > 0, stop, q["cap"]), q["cap"]).sum(
                    axis=1
                )
            _, eligible = select(validations[0], rows, q, metas[0]["validation_rare"])
            for stratum, mask in strata.items():
                entries = [r for r, keep in zip(chosen, mask, strict=True) if keep]
                result["selections"].append(
                    dict(
                        case=case,
                        query=qi,
                        **q,
                        stratum=stratum,
                        aggregate=statistics(selected_test[mask, qi, 0]),
                        rare=statistics(selected_test[mask, qi, 1]),
                        **{
                            name: statistics(selected_features[mask, qi, j])
                            for j, name in enumerate(FEATURES)
                        },
                        eta=statistics(
                            np.array(
                                [
                                    etas[r, row["index"][2]]
                                    for r, row in enumerate(chosen)
                                ]
                            )[mask]
                        ),
                        initialization=sum(r["observations"] == 0 for r in entries),
                        lower_rate=sum(
                            r["observations"] > 0 and r["factor"] == FACTORS[0]
                            for r in entries
                        ),
                        upper_rate=sum(
                            r["observations"] > 0 and r["factor"] == FACTORS[-1]
                            for r in entries
                        ),
                        rate_histogram={
                            str(f): sum(
                                r["observations"] > 0 and r["factor"] == f
                                for r in entries
                            )
                            for f in FACTORS
                        },
                        batch_histogram={
                            str(b): sum(r["batch"] == b for r in entries)
                            for b in BATCHES
                        },
                        stop_histogram={
                            str(m): sum(r["observations"] == m for r in entries)
                            for m in CHECKPOINTS
                        },
                        rare_fallbacks=int(selections[mask, qi, 1].sum()),
                        nominal_tuning_observations=34 * q["cap"],
                        executed_live_observations=statistics(used[mask]),
                        scored_endpoints=len(eligible),
                        failed_eligible_endpoints=int(
                            statuses.reshape(REPS, -1)[mask][:, eligible].sum()
                        ),
                    )
                )
            for reference in ("none", "sd", "damped_0.01", "variance"):
                if q["scale"] == reference:
                    continue
                ri = queries.index(q | {"scale": reference})
                for stratum, mask in strata.items():
                    delta = selected_test[mask, qi] - selected_test[mask, ri]
                    result["contrasts"].append(
                        dict(
                            case=case,
                            query=qi,
                            **q,
                            reference=reference,
                            stratum=stratum,
                            aggregate=statistics(delta[:, 0]),
                            rare=statistics(delta[:, 1]),
                        )
                    )
            for rep, row_id in enumerate(ids[:, qi]):
                effective = 0 if selections[rep, qi, 1] else q["objective"]
                result["boundaries"].append(
                    dict(
                        case=case,
                        rep=rep,
                        query=qi,
                        **neighbor_diagnostic(
                            rows,
                            int(row_id),
                            validations[rep].reshape(-1, 2),
                            statuses[rep].ravel(),
                            effective,
                        ),
                    )
                )
            if q["cap"] == max(CHECKPOINTS):
                for mi, m in enumerate(CHECKPOINTS):
                    risk, feature = [], []
                    for rep, row in enumerate(chosen):
                        bi, _, ci = row["index"]
                        risk.append(tests[rep, bi, mi, ci])
                        feature.append(features[rep, bi, mi, ci])
                    risk, feature = np.array(risk), np.array(feature)
                    result["paths"].append(
                        dict(
                            case=case,
                            query=qi,
                            observations=m,
                            aggregate=statistics(risk[:, 0]),
                            rare=statistics(risk[:, 1]),
                            **{
                                name: statistics(feature[:, j])
                                for j, name in enumerate(FEATURES)
                            },
                        )
                    )
    return result


def plot(summary):
    levels = ["sd", *[s for s in SCALES if s.startswith("damped_")]]
    fig, axes = plt.subplots(2, 4, figsize=(14, 6), layout="constrained")
    for case in range(2):
        for objective in range(2):
            entries = {
                s["scale"]: s
                for s in summary["selections"]
                if s["case"] == case
                and s["objective"] == objective
                and s["cap"] == 8192
                and s["search"] == "expanded"
                and s["stratum"] == "all"
            }
            for j, risk in enumerate(("aggregate", "rare")):
                ax = axes[case, 2 * objective + j]
                ax.plot(
                    range(len(levels)),
                    [entries[s][risk]["mean"] for s in levels],
                    "o-",
                    label="Fixed damping",
                )
                ax.axhline(
                    entries["none"][risk]["mean"], color="gray", ls="--", label="None"
                )
                ax.axhline(
                    entries["variance"][risk]["mean"],
                    color="darkorange",
                    ls=":",
                    label="Variance",
                )
                ax.set_xticks(
                    range(len(levels)),
                    ["0 (SD)", ".001", ".003", ".01", ".03", ".1"],
                    rotation=45,
                )
                ax.set_yscale("log")
                ax.set_title(
                    f"n={SIZES[case][0]}, "
                    f"{('aggregate', 'rare')[objective]} selection\n"
                    f"{risk.capitalize()} test loss"
                )
                ax.set_xlabel("Fixed damping offset")
                ax.grid(alpha=0.2)
    axes[0, 0].legend(fontsize=8)
    for suffix in ("pdf", "png"):
        fig.savefig(OUTPUT / f"sensitivity.{suffix}", dpi=160)
    plt.close(fig)


def main():
    result = summarize()
    plot(result)
    result["provenance"] = dict(manifest_sha256=sha256(OUTPUT / "manifest.json"))
    write_json(OUTPUT / "summary.json", result)
    write_json(
        OUTPUT / "artifacts.json",
        {
            p: sha256(OUTPUT / p)
            for p in ("summary.json", "sensitivity.pdf", "sensitivity.png")
        },
    )
    print("Saved fixed-offset summaries, paired contrasts, paths, and figures.")


if __name__ == "__main__":
    main()
