"""Paired uncertainty, absence strata, complete curves, and selection diagnostics."""

import json

import numpy as np
from practical_spec import (
    FACTORS,
    LAWS,
    OUTPUT,
    ROOT,
    SCALES,
    load_mushroom,
    mushroom_data,
    sha256,
    write_json,
)


def statistics(values):
    values = np.asarray(values)
    good = np.isfinite(values)
    n = int(good.sum())
    # Rescaling avoids overflow when summarizing retained unstable candidates.
    scale = max(float(np.max(np.abs(values[good]))), 1e-300) if n else 1
    normalized = values[good] / scale
    return dict(
        n=n,
        missing=int((~good).sum()),
        mean=float(normalized.mean() * scale) if n else None,
        mcse=float(normalized.std(ddof=1) / np.sqrt(n) * scale) if n > 1 else None,
        median=float(np.median(normalized) * scale) if n else None,
        p95=float(np.quantile(normalized, 0.95) * scale) if n else None,
        maximum=float(normalized.max() * scale) if n else None,
        aggregation="finite_replicates_only" if n < len(values) else "all_replicates",
    )


def summarize_stage(label):
    manifest = json.loads((OUTPUT / f"{label}.json").read_text())
    archive = np.load(OUTPUT / f"{label}.npz")
    summaries, contrasts, curves, mechanisms, cases = [], [], [], [], []
    queries, rows = manifest["queries"], manifest["candidates"]
    raw = load_mushroom() if label == "mushroom" else None
    for case in sorted({r["case"] for r in manifest["replications"]}):
        metas = [r for r in manifest["replications"] if r["case"] == case]
        selected_loss, selected_coefs, selected_ids, fallbacks, failures = (
            [],
            [],
            [],
            [],
            [],
        )
        endpoint_losses, endpoint_coefficients, oracle_regret = [], [], []
        invalid = 0
        contributions = []
        for meta in metas:
            prefix = f"c{case}_r{meta['rep']}_"
            test, coef, selections = (
                archive[prefix + k] for k in ("test", "coefficients", "selections")
            )
            indices = [tuple(rows[i]["index"]) for i in selections[:, 0]]
            selected_loss.append(np.array([test[i] for i in indices]))
            # Unseen categories cannot acquire a fitted effect.
            name = "rare" if label == "synthetic" else "spore-print-color=r"
            rare_id = meta["names"].index(name) + 1 if name in meta["names"] else None
            rare_coef = np.array(
                [coef[i][rare_id] if rare_id else 0.0 for i in indices]
            )
            raw_intercept = np.array([coef[i][0] for i in indices])
            selected_coefs.append(np.column_stack((raw_intercept, rare_coef)))
            shifts = archive[prefix + "parameter_mu"]
            if label == "synthetic":
                conditional_mean = np.array([(1 + LAWS[case]["ell"]) / 2, 1])
            else:
                parts, _ = mushroom_data(raw, case, meta["rep"])
                tx, _, tr = parts[2]
                conditional_mean = (
                    np.asarray(tx[tr].mean(axis=0)).ravel()
                    if tr.any()
                    else np.full(tx.shape[1], np.nan)
                )
            components = []
            for idx in indices:
                b, mu = coef[idx], shifts[idx[2]]
                centered_intercept = b[0] + b[1:] @ mu
                rare_contribution = (
                    b[rare_id] * (1 - mu[rare_id - 1]) if rare_id else 0.0
                )
                other_contribution = (conditional_mean - mu) @ b[1:] - rare_contribution
                components.append(
                    [centered_intercept, rare_contribution, other_contribution]
                )
            contributions.append(components)
            selected_ids.append(selections[:, 0])
            fallbacks.append(selections[:, 1])
            failures.append(selections[:, 2])
            endpoint_losses.append(test)
            endpoint_coefficients.append(
                np.stack(
                    (
                        coef[..., 0],
                        coef[..., rare_id] if rare_id else np.zeros(coef.shape[:-1]),
                    ),
                    axis=-1,
                )
            )
            invalid += int(np.count_nonzero(archive[prefix + "status"]))
            oracle_regret.append(
                [
                    test[indices[qi]][q["objective"]]
                    - test[tuple(rows[oracle]["index"])][q["objective"]]
                    if oracle >= 0
                    else np.nan
                    for qi, (q, oracle) in enumerate(
                        zip(queries, selections[:, 3], strict=True)
                    )
                ]
            )
        selected_loss, selected_coefs, selected_ids = map(
            np.array, (selected_loss, selected_coefs, selected_ids)
        )
        fallbacks, failures, endpoint_losses, endpoint_coefficients, oracle_regret = (
            map(
                np.array,
                (
                    fallbacks,
                    failures,
                    endpoint_losses,
                    endpoint_coefficients,
                    oracle_regret,
                ),
            )
        )
        train_absent = np.array([m["train_rare"] == 0 for m in metas])
        contributions = np.array(contributions)
        val_absent = np.array([m["validation_rare"] == 0 for m in metas])
        strata = dict(
            all=np.ones(len(metas), dtype=bool),
            train_absent=train_absent,
            train_present=~train_absent,
            validation_absent=val_absent,
            validation_present=~val_absent,
        )
        cases.append(
            dict(
                case=case,
                name=LAWS[case]["name"]
                if label == "synthetic"
                else f"Mushroom n={metas[0]['n']}",
                replications=len(metas),
                train_absent=int(train_absent.sum()),
                validation_absent=int(val_absent.sum()),
                test_absent=sum(m["test_rare"] == 0 for m in metas),
                invalid_endpoints=invalid,
                train_rare=[m["train_rare"] for m in metas],
                validation_rare=[m["validation_rare"] for m in metas],
                test_rare=[m["test_rare"] for m in metas],
                dimension=[m["dimension"] for m in metas],
                n=metas[0]["n"],
                n_validation=metas[0]["n_validation"],
                n_test=metas[0]["n_test"],
                calibration_gram_count_per_replication=15
                if label == "synthetic"
                else 9,
            )
        )
        for qi, q in enumerate(queries):
            chosen = [rows[i] for i in selected_ids[:, qi]]
            histograms = {
                key: {
                    str(v): sum(row[key] == v for row in chosen)
                    for v in sorted({r[key] for r in chosen})
                }
                for key in ("batch", "factor", "observations", "scale")
            }
            for stratum, mask in strata.items():
                summaries.append(
                    dict(
                        case=case,
                        query=qi,
                        **q,
                        stratum=stratum,
                        aggregate=statistics(selected_loss[mask, qi, 0]),
                        rare=statistics(selected_loss[mask, qi, 1]),
                        hindsight_regret=statistics(oracle_regret[mask, qi]),
                        rare_fallbacks=int(fallbacks[mask, qi].sum()),
                        failed_fallbacks=int(failures[mask, qi].sum()),
                        nominal_tuning_observations=q["cap"]
                        * (
                            30
                            if q["scale"] == "all"
                            else 1
                            if q["rule"] == "fixed"
                            else 10
                        ),
                    )
                )
            mechanisms.append(
                dict(
                    case=case,
                    query=qi,
                    **q,
                    raw_intercept=statistics(selected_coefs[:, qi, 0]),
                    rare_coefficient=statistics(selected_coefs[:, qi, 1]),
                    centered_intercept=statistics(contributions[:, qi, 0]),
                    centered_rare_contribution=statistics(contributions[:, qi, 1]),
                    other_subgroup_contribution=statistics(contributions[:, qi, 2]),
                    initialization_selections=sum(
                        r["observations"] == 0 for r in chosen
                    ),
                    smallest_rate=sum(
                        r["factor"] == FACTORS[0] and r["observations"] > 0
                        for r in chosen
                    ),
                    largest_rate=sum(
                        r["factor"] == FACTORS[-1] and r["observations"] > 0
                        for r in chosen
                    ),
                    selection_counts=histograms,
                )
            )
        # Pair first to retain shared data and optimization noise.
        lookup = {
            (q["arm"], q["cap"], q["objective"], q["scale"], q["rule"]): i
            for i, q in enumerate(queries)
        }
        for qi, q in enumerate(queries):
            comparisons = []
            if q["scale"] in ("sd", "damped"):
                comparisons.append(
                    (
                        "scaling_minus_none",
                        lookup[(q["arm"], q["cap"], q["objective"], "none", q["rule"])],
                    )
                )
            if q["objective"] == 1:
                comparisons.append(
                    (
                        "rare_selection_minus_aggregate",
                        lookup[(q["arm"], q["cap"], 0, q["scale"], q["rule"])],
                    )
                )
            if q["arm"] == "centered_fitted":
                comparisons.append(
                    (
                        "fitted_minus_fixed_intercept",
                        lookup[
                            (
                                "centered_fixed",
                                q["cap"],
                                q["objective"],
                                q["scale"],
                                q["rule"],
                            )
                        ],
                    )
                )
            if label == "synthetic" and q["arm"] != "known":
                comparisons.append(
                    (
                        "estimated_minus_known",
                        lookup[
                            ("known", q["cap"], q["objective"], q["scale"], q["rule"])
                        ],
                    )
                )
            for kind, reference in comparisons:
                delta = selected_loss[:, qi] - selected_loss[:, reference]
                for stratum, mask in strata.items():
                    contrasts.append(
                        dict(
                            case=case,
                            query=qi,
                            reference=reference,
                            kind=kind,
                            **q,
                            stratum=stratum,
                            aggregate=statistics(delta[mask, 0]),
                            rare=statistics(delta[mask, 1]),
                            different_selections=int(
                                np.sum(
                                    selected_ids[mask, qi]
                                    != selected_ids[mask, reference]
                                )
                            ),
                        )
                    )
        for row in rows:
            idx = tuple(row["index"])
            values = endpoint_losses[(slice(None), *idx)]
            features = endpoint_coefficients[(slice(None), *idx)]
            curves.append(
                dict(
                    case=case,
                    **row,
                    aggregate=statistics(values[:, 0]),
                    rare=statistics(values[:, 1]),
                    raw_intercept=statistics(features[:, 0]),
                    rare_coefficient=statistics(features[:, 1]),
                )
            )
    archive.close()
    return dict(
        cases=cases,
        selections=summaries,
        contrasts=contrasts,
        mechanisms=mechanisms,
        curves=curves,
    )


def plot(summary):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"svg.hashsalt": "practical-selection", "font.size": 9})
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), layout="constrained")
    for ax, case in zip(axes[0], (0, 2), strict=True):
        for scale, color in zip(("none", "sd"), ("#276678", "#c45c32"), strict=True):
            for arm, style in (("known", "--"), ("centered_fitted", "-")):
                rows = [
                    r
                    for r in summary["synthetic"]["curves"]
                    if r["case"] == case
                    and r["arm"] == arm
                    and r["scale"] == scale
                    and r["factor"] == 0.05
                    and r["batch"] == 16
                ]
                ax.plot(
                    [r["observations"] for r in rows],
                    [r["rare"]["mean"] for r in rows],
                    style,
                    color=color,
                    label=f"{scale}, {arm}",
                )
        ax.set(
            title=f"Sampled {LAWS[case]['name']}: fixed rate and stopping",
            xlabel="Processed observations",
            ylabel="Rare excess half squared loss",
        )
        ax.set_xscale("symlog", linthresh=128)
        ax.legend(fontsize=7)
    for ax, objective in zip(axes[1], ("aggregate", "rare"), strict=True):
        for size, marker in ((0, "o"), (1, "s")):
            for selection, offset in ((0, -0.12), (1, 0.12)):
                rows = [
                    r
                    for r in summary["mushroom"]["selections"]
                    if r["case"] == size
                    and r["arm"] == "centered_fitted"
                    and r["cap"] == 8192
                    and r["rule"] == "joint"
                    and r["objective"] == selection
                    and r["stratum"] == "all"
                ]
                rows.sort(key=lambda r: SCALES.index(r["scale"]))
                ax.errorbar(
                    np.arange(3) + offset,
                    [r[objective]["mean"] for r in rows],
                    yerr=[r[objective]["mcse"] for r in rows],
                    fmt=marker,
                    linestyle="none",
                    capsize=3,
                    label=f"n={256 if size == 0 else 2048}, "
                    f"{'rare' if selection else 'aggregate'} selection",
                )
        ax.set(
            xticks=range(3),
            xticklabels=SCALES,
            title=f"Mushroom: {objective} test loss",
            ylabel="Half squared loss",
        )
        ax.legend(fontsize=7)
    paths = []
    for suffix in ("svg", "pdf"):
        target = OUTPUT / f"practical-selection.{suffix}"
        metadata = (
            {"Date": None}
            if suffix == "svg"
            else {"CreationDate": None, "ModDate": None}
        )
        fig.savefig(target, metadata=metadata)
        paths.append(target)
    (ROOT / "build").mkdir(exist_ok=True)
    fig.savefig(ROOT / "build/practical-selection.png", dpi=140)
    plt.close(fig)
    return paths


def main():
    summary = {label: summarize_stage(label) for label in ("synthetic", "mushroom")}
    summary["provenance"] = {
        str(p.relative_to(ROOT)): sha256(p)
        for p in [
            ROOT / "experiments/summarize_practical_selection.py",
            OUTPUT / "synthetic.json",
            OUTPUT / "synthetic.npz",
            OUTPUT / "mushroom.json",
            OUTPUT / "mushroom.npz",
        ]
    }
    summary["figures"] = {str(p.relative_to(ROOT)): sha256(p) for p in plot(summary)}
    write_json(OUTPUT / "summary.json", summary)
    for label in ("synthetic", "mushroom"):
        print(label, summary[label]["cases"], flush=True)


if __name__ == "__main__":
    main()
