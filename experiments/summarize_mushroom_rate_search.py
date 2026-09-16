"""Paired rate-search contrasts, boundaries, complete curves, and path figures."""

import json
from contextlib import ExitStack

import numpy as np
from mushroom_rate_spec import (
    BATCHES,
    CHECKPOINTS,
    FACTORS,
    ORIGINAL_FACTORS,
    OUTPUT,
    REPS,
    SIZES,
    configurations,
    select,
)
from practical_spec import SCALES, load_mushroom, mushroom_data, sha256, write_json
from summarize_practical_selection import statistics

FEATURES = (
    "raw_intercept",
    "green_coefficient",
    "centered_intercept",
    "green_contribution",
    "other_contribution",
    "rare_mean_prediction",
)
KEYS = ("arm", "scale", "objective", "cap", "search", "rule")


def query_key(query):
    return tuple(query[k] for k in KEYS)


def components(coefficients, shifts, names, conditional_mean, centered_intercepts):
    flat = coefficients.reshape(-1, coefficients.shape[-1])
    mu = np.broadcast_to(shifts, (*coefficients.shape[:-1], shifts.shape[-1])).reshape(
        -1, shifts.shape[-1]
    )
    rare_id = (
        names.index("spore-print-color=r") if "spore-print-color=r" in names else None
    )
    centered = centered_intercepts.ravel()
    green = flat[:, rare_id + 1] if rare_id is not None else np.zeros(len(flat))
    contribution = green * (1 - mu[:, rare_id]) if rare_id is not None else green.copy()
    prediction = flat[:, 0] + flat[:, 1:] @ conditional_mean
    values = np.column_stack(
        (
            flat[:, 0],
            green,
            centered,
            contribution,
            prediction - centered - contribution,
            prediction,
        )
    )
    values[~np.isfinite(flat).all(axis=1)] = np.nan
    return values


def neighbor_diagnostic(rows, chosen, validation, status, effective):
    row = rows[chosen]
    score = float(validation[chosen, effective])
    result = dict(candidate=chosen, factor=row["factor"], score=score, neighbors={})
    if row["observations"] == 0:
        result["initialization"] = True
        return result
    result["initialization"] = False
    fi = FACTORS.index(row["factor"])
    for label, other in (("lower", fi - 1), ("higher", fi + 1)):
        if other not in range(len(FACTORS)):
            result["neighbors"][label] = None
            continue
        neighbor = next(
            i
            for i, candidate in enumerate(rows)
            if all(
                candidate[k] == row[k]
                for k in ("arm", "scale", "batch", "observations")
            )
            and candidate["factor"] == FACTORS[other]
        )
        value = validation[neighbor, effective]
        result["neighbors"][label] = dict(
            candidate=neighbor,
            factor=FACTORS[other],
            failed=bool(status[neighbor]),
            finite_score=bool(np.isfinite(value)),
            score=float(value),
            gap=float(value - score),
            no_better=bool(not np.isfinite(value) or value >= score),
        )
    return result


def summarize():
    manifest = json.loads((OUTPUT / "manifest.json").read_text())
    rows, queries = manifest["candidates"], manifest["queries"]
    raw = load_mushroom()
    result = dict(
        cases=[],
        selections=[],
        contrasts=[],
        curves=[],
        selected_paths=[],
        boundaries=[],
    )
    lookup = {query_key(q): i for i, q in enumerate(queries)}
    with ExitStack() as stack:
        archives = {
            name: stack.enter_context(np.load(OUTPUT / name))
            for name in manifest["archives"]
        }
        for case in range(len(SIZES)):
            metas = [m for m in manifest["replications"] if m["case"] == case]
            tests, validations, trains, features, statuses, selected, failures = (
                [] for _ in range(7)
            )
            steps, curvatures = [], []
            for meta in metas:
                archive = archives[meta["archive"]]
                prefix = f"c{case}_r{meta['rep']}_"
                coef = archive[prefix + "coefficients"]
                for target, name in (
                    (tests, "test"),
                    (validations, "validation"),
                    (trains, "train"),
                ):
                    target.append(archive[prefix + name].reshape(-1, 2))
                parts, _ = mushroom_data(raw, case, meta["rep"])
                x, _, rare = parts[2]
                conditional = (
                    np.asarray(x[rare].mean(axis=0)).ravel()
                    if rare.any()
                    else np.full(x.shape[1], np.nan)
                )
                features.append(
                    components(
                        coef,
                        archive[prefix + "parameter_mu"],
                        meta["names"],
                        conditional,
                        archive[prefix + "centered_intercepts"],
                    )
                )
                statuses.append(archive[prefix + "status"].ravel())
                selected.append(archive[prefix + "selections"])
                failures.append(archive[prefix + "failure_update"])
                steps.append(archive[prefix + "parameter_eta"])
                curvatures.append(archive[prefix + "parameter_curvature"])
            tests, validations, trains, features, statuses, selected, failures = map(
                np.array,
                (tests, validations, trains, features, statuses, selected, failures),
            )
            ids = selected[:, :, 0]
            rep_idx = np.arange(REPS)[:, None]
            selected_test = tests[rep_idx, ids]
            selected_features = features[rep_idx, ids]
            selected_validation = validations[rep_idx, ids]
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
                    n_validation=SIZES[case][1],
                    replications=REPS,
                    endpoints=int(statuses.size),
                    failed_endpoints=int(statuses.sum()),
                    failed_paths=int(np.count_nonzero(failures)),
                    train_absent=int(strata["train_absent"].sum()),
                    validation_absent=int(strata["validation_absent"].sum()),
                    test_absent=sum(m["test_rare"] == 0 for m in metas),
                    train_rare=[m["train_rare"] for m in metas],
                    validation_rare=[m["validation_rare"] for m in metas],
                    test_rare=[m["test_rare"] for m in metas],
                )
            )
            for qi, query in enumerate(queries):
                chosen = [rows[i] for i in ids[:, qi]]
                selected_steps = np.array(
                    [steps[i][r["index"][2]] for i, r in enumerate(chosen)]
                )
                selected_curvatures = np.array(
                    [curvatures[i][r["index"][2]] for i, r in enumerate(chosen)]
                )
                factors = (
                    ORIGINAL_FACTORS
                    if query["search"] in ("original", "fixed")
                    else FACTORS
                )
                ci = [
                    i
                    for i, c in enumerate(configurations())
                    if c["arm"] == query["arm"]
                    and c["scale"] == query["scale"]
                    and c["factor"] in factors
                ]
                batches = [0] if query["rule"] == "fixed" else list(range(len(BATCHES)))
                if query["rule"] == "fixed":
                    ci = [i for i in ci if configurations()[i]["factor"] == 0.05]
                executed = np.zeros(REPS)
                for bi in batches:
                    failure_m = failures[:, bi, ci] * BATCHES[bi]
                    executed += np.minimum(
                        np.where(failure_m > 0, failure_m, query["cap"]), query["cap"]
                    ).sum(axis=1)
                _, eligible = select(
                    validations[0].reshape(len(BATCHES), len(CHECKPOINTS), -1, 2),
                    rows,
                    query,
                    metas[0]["validation_rare"],
                )
                for stratum, mask in strata.items():
                    result["selections"].append(
                        dict(
                            case=case,
                            query=qi,
                            **query,
                            stratum=stratum,
                            aggregate=statistics(selected_test[mask, qi, 0]),
                            rare=statistics(selected_test[mask, qi, 1]),
                            validation_aggregate=statistics(
                                selected_validation[mask, qi, 0]
                            ),
                            validation_rare=statistics(
                                selected_validation[mask, qi, 1]
                            ),
                            absolute_eta=statistics(selected_steps[mask]),
                            curvature=statistics(selected_curvatures[mask]),
                            **{
                                name: statistics(selected_features[mask, qi, j])
                                for j, name in enumerate(FEATURES)
                            },
                            rare_fallbacks=int(selected[mask, qi, 1].sum()),
                            failed_fallbacks=int(selected[mask, qi, 2].sum()),
                            nominal_tuning_observations=query["cap"]
                            * len(ci)
                            * len(batches),
                            executed_live_observations=statistics(executed[mask]),
                            scored_endpoints=len(eligible),
                            failed_eligible_endpoints=int(
                                statuses[mask][:, eligible].sum()
                            ),
                            initialization_selections=sum(
                                mask[i] and r["observations"] == 0
                                for i, r in enumerate(chosen)
                            ),
                            smallest_rate=sum(
                                mask[i]
                                and r["observations"] > 0
                                and r["factor"] == factors[0]
                                for i, r in enumerate(chosen)
                            ),
                            largest_rate=sum(
                                mask[i]
                                and r["observations"] > 0
                                and r["factor"] == factors[-1]
                                for i, r in enumerate(chosen)
                            ),
                            selection_counts={
                                key: {
                                    str(v): sum(
                                        mask[i] and r[key] == v
                                        for i, r in enumerate(chosen)
                                    )
                                    for v in sorted({r[key] for r in chosen})
                                }
                                for key in ("factor", "batch", "observations")
                            },
                        )
                    )
                references = []
                if query["scale"] != "none":
                    references.append(("scaling_minus_none", query | {"scale": "none"}))
                if query["objective"] == 1:
                    references.append(
                        ("rare_selection_minus_aggregate", query | {"objective": 0})
                    )
                if query["search"] == "expanded":
                    references.append(
                        ("expanded_minus_original", query | {"search": "original"})
                    )
                if query["search"] == "expanded_stops":
                    references.append(
                        ("extra_stops_minus_expanded", query | {"search": "expanded"})
                    )
                for kind, reference in references:
                    ri = lookup[query_key(reference)]
                    delta = selected_test[:, qi] - selected_test[:, ri]
                    for stratum, mask in strata.items():
                        result["contrasts"].append(
                            dict(
                                case=case,
                                query=qi,
                                reference=ri,
                                **query,
                                kind=kind,
                                stratum=stratum,
                                aggregate=statistics(delta[mask, 0]),
                                rare=statistics(delta[mask, 1]),
                                different_selections=int(
                                    np.count_nonzero(ids[mask, qi] != ids[mask, ri])
                                ),
                            )
                        )
                if query["search"].startswith("expanded") and query["rule"] == "joint":
                    for rep, meta in enumerate(metas):
                        effective = (
                            0
                            if query["objective"] == 1 and meta["validation_rare"] == 0
                            else query["objective"]
                        )
                        result["boundaries"].append(
                            dict(
                                case=case,
                                rep=rep,
                                query=qi,
                                **query,
                                **neighbor_diagnostic(
                                    rows,
                                    ids[rep, qi],
                                    validations[rep],
                                    statuses[rep],
                                    effective,
                                ),
                            )
                        )
                if query["rule"] == "joint" and query["cap"] == 8192:
                    for mi, m in enumerate(CHECKPOINTS):
                        path_ids = np.array(
                            [
                                r["index"][0] * len(CHECKPOINTS) * len(configurations())
                                + mi * len(configurations())
                                + r["index"][2]
                                for r in chosen
                            ]
                        )
                        value = tests[np.arange(REPS), path_ids]
                        feature = features[np.arange(REPS), path_ids]
                        result["selected_paths"].append(
                            dict(
                                case=case,
                                query=qi,
                                **query,
                                observations=m,
                                aggregate=statistics(value[:, 0]),
                                rare=statistics(value[:, 1]),
                                **{
                                    name: statistics(feature[:, j])
                                    for j, name in enumerate(FEATURES)
                                },
                                stopped_by_checkpoint=sum(
                                    r["observations"] <= m for r in chosen
                                ),
                                failed_endpoints=int(
                                    statuses[np.arange(REPS), path_ids].sum()
                                ),
                            )
                        )
            for i, row in enumerate(rows):
                result["curves"].append(
                    dict(
                        case=case,
                        candidate=i,
                        **row,
                        aggregate=statistics(tests[:, i, 0]),
                        rare=statistics(tests[:, i, 1]),
                        validation_aggregate=statistics(validations[:, i, 0]),
                        validation_rare=statistics(validations[:, i, 1]),
                        train_aggregate=statistics(trains[:, i, 0]),
                        train_rare=statistics(trains[:, i, 1]),
                        **{
                            name: statistics(features[:, i, j])
                            for j, name in enumerate(FEATURES)
                        },
                        failed_endpoints=int(statuses[:, i].sum()),
                    )
                )
    return result


def plot(summary):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 9, "svg.hashsalt": "mushroom-rate-search-v1"})
    colors = ("#32688e", "#d66b24", "#31865a")
    files = []

    def save(fig, stem):
        for extension in ("svg", "pdf"):
            target = OUTPUT / f"{stem}.{extension}"
            metadata = (
                {"Date": None}
                if extension == "svg"
                else {"CreationDate": None, "ModDate": None}
            )
            fig.savefig(target, metadata=metadata)
            files.append(target)
        preview = OUTPUT.parents[1] / "build" / f"{stem}.png"
        preview.parent.mkdir(exist_ok=True)
        fig.savefig(preview, dpi=130)
        plt.close(fig)

    fig, axes = plt.subplots(4, 2, figsize=(10, 11), constrained_layout=True)
    for case in range(2):
        for objective in range(2):
            for metric_id, metric in enumerate(("aggregate", "rare")):
                ax = axes[2 * case + objective, metric_id]
                for si, (scale, color) in enumerate(zip(SCALES, colors, strict=True)):
                    values = [
                        next(
                            s
                            for s in summary["selections"]
                            if s["case"] == case
                            and s["objective"] == objective
                            and s["arm"] == "centered_fitted"
                            and s["scale"] == scale
                            and s["cap"] == 8192
                            and s["rule"] == "joint"
                            and s["search"] == search
                            and s["stratum"] == "all"
                        )
                        for search in ("original", "expanded", "expanded_stops")
                    ]
                    ax.errorbar(
                        np.arange(3) + (si - 1) * 0.1,
                        [v[metric]["mean"] for v in values],
                        yerr=[v[metric]["mcse"] for v in values],
                        color=color,
                        marker="o",
                        capsize=3,
                        label=scale,
                    )
                ax.set_xticks(range(3), ("Original", "Expanded", "+ stops"))
                ax.set_ylabel(f"{metric.capitalize()} test loss")
                ax.set_title(
                    f"n={SIZES[case][0]}, "
                    f"{'rare' if objective else 'aggregate'} validation"
                )
                ax.set_yscale("log")
                ax.grid(alpha=0.2)
    axes[0, 0].legend()
    fig.suptitle(
        "Selected endpoints at cap M=8192: means and one MCSE\n"
        "Centered, fitted intercept; all 32 partitions per size"
    )
    save(fig, "selected-risks")

    for case in range(2):
        for objective in range(2):
            fig, axes = plt.subplots(2, 3, figsize=(13, 7), constrained_layout=True)
            metrics = (
                "aggregate",
                "rare",
                "green_coefficient",
                "centered_intercept",
                "green_contribution",
                "other_contribution",
            )
            for ax, metric in zip(axes.flat, metrics, strict=True):
                for scale, color in zip(SCALES, colors, strict=True):
                    for search, style in (("original", ":"), ("expanded", "-")):
                        values = [
                            p
                            for p in summary["selected_paths"]
                            if p["case"] == case
                            and p["objective"] == objective
                            and p["arm"] == "centered_fitted"
                            and p["scale"] == scale
                            and p["search"] == search
                        ]
                        ax.plot(
                            [p["observations"] for p in values],
                            [p[metric]["mean"] for p in values],
                            color=color,
                            linestyle=style,
                            label=f"{scale}, {search}",
                        )
                        endpoint = next(
                            s
                            for s in summary["selections"]
                            if s["case"] == case
                            and s["objective"] == objective
                            and s["arm"] == "centered_fitted"
                            and s["scale"] == scale
                            and s["cap"] == 8192
                            and s["rule"] == "joint"
                            and s["search"] == search
                            and s["stratum"] == "all"
                        )
                        ax.scatter(
                            10496,
                            endpoint[metric]["mean"],
                            color=color,
                            marker="o" if search == "expanded" else "x",
                            s=26,
                        )
                ax.axvline(9216, color="0.7", linewidth=0.8)
                ax.set_xticks(
                    (0, 2048, 4096, 8192, 10496),
                    ("0", "2048", "4096", "8192", "Selected"),
                )
                ax.set_xlabel("Processed observations M")
                ax.set_title(metric.replace("_", " ").capitalize())
                ax.set_yscale(
                    "log" if metric in ("aggregate", "rare") else "symlog",
                    **({} if metric in ("aggregate", "rare") else {"linthresh": 0.1}),
                )
                ax.grid(alpha=0.2)
            axes[0, 0].legend(fontsize=7)
            fig.suptitle(
                f"n={SIZES[case][0]}, "
                f"{'rare' if objective else 'aggregate'} validation: "
                "trajectories selected at cap 8192\nMeans across 32 partitions; "
                "continuation after each selected stop is descriptive"
            )
            save(fig, f"paths-n{SIZES[case][0]}-{'rare' if objective else 'aggregate'}")
    return {p.name: sha256(p) for p in files}


def main():
    summary = summarize()
    figures = plot(summary)
    summary["provenance"] = dict(
        manifest_sha256=sha256(OUTPUT / "manifest.json"),
        figures=figures,
        mcse="paired partition/optimizer variation conditional on the fixed dataset",
        curves=("finite-only means carry missing counts; failures are retained"),
        selected_paths=(
            "follow the cap-8192 selected batch/rate; continuation is descriptive"
        ),
    )
    write_json(OUTPUT / "summary.json", summary)
    manifest = json.loads((OUTPUT / "manifest.json").read_text())
    write_json(
        OUTPUT / "artifacts.json",
        {
            name: sha256(OUTPUT / name)
            for name in (
                "manifest.json",
                "summary.json",
                *manifest["archives"],
                *figures,
            )
        },
    )
    print("Saved all paired contrasts, rate diagnostics, curves, and figures.")


if __name__ == "__main__":
    main()
