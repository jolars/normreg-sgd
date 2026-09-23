"""Paired uncertainty, absence strata, complete curves, and selection diagnostics."""

import json

import numpy as np

from experiments.common.data import (
    FACTORS,
    LAWS,
    load_mushroom,
    mushroom_data,
    result_dir,
    write_json,
)
from experiments.common.statistics import statistics


def summarize_stage(label):
    output = result_dir(label, "rates5")
    manifest = json.loads((output / f"{label}.json").read_text())
    archive = np.load(output / f"{label}.npz")
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


def summarize(label):
    output = result_dir(label, "rates5")
    write_json(output / "summary.json", summarize_stage(label))
