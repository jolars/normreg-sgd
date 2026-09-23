"""Independent audit of variance scaling, paths, selections, and artifacts."""

import argparse
import json
from contextlib import ExitStack
from functools import lru_cache

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
from scipy import sparse

from checks.mushroom_rate_search import check_stat, reference_path
from experiments.common.data import (
    LAWS,
    REPS,
    ROOT,
    SIZES,
    encode,
    encode_fit,
    jsonable,
    load_mushroom,
    result_dir,
    rng,
    write_json,
)
from experiments.common.dynamics import prepare as shared_prepare
from experiments.common.dynamics import recorded_path as path
from experiments.common.matched import dataset, prepare
from experiments.common.rates25 import (
    BATCHES,
    CHECKPOINTS,
    FACTORS,
    MUSHROOM_FACTORS,
    ORIGINAL_STOPS,
    PRACTICAL_FACTORS,
    candidate_rows,
    configurations,
    queries,
    select,
)


def expected_parameters(x, y, configs, population_mean=None):
    x = x.toarray() if sparse.issparse(x) else x
    result = {
        k: []
        for k in (
            "mu",
            "divisor",
            "active",
            "initial",
            "fit_intercept",
            "curvature",
            "eta",
        )
    }
    cache = {}
    for config in configs:
        arm, scale = config["arm"], config["scale"]
        key = arm, scale
        if key not in cache:
            mu = (
                population_mean
                if arm in ("known", "estimated_scale")
                else np.zeros(x.shape[1])
                if arm == "uncentered_fitted"
                else x.mean(axis=0)
            )
            variance = (
                population_mean * (1 - population_mean)
                if arm == "known"
                else np.var(x, axis=0)
            )
            active = (
                np.ones(x.shape[1], dtype=bool)
                if arm == "known"
                else np.var(x, axis=0) > 1e-14
            )
            divisor = {
                "none": np.ones(x.shape[1]),
                "sd": np.sqrt(variance),
                "damped": np.sqrt(variance + 0.01),
                "variance": variance,
            }[scale]
            divisor = np.where(active, divisor, 1)
            z = (x - mu) * active / divisor
            fitted = arm.endswith("fitted")
            if fitted:
                z = np.column_stack((z, np.ones(len(x))))
            curvature = max(float(np.linalg.eigvalsh(z.T @ z / len(x))[-1]), 1e-12)
            initial = 0.0 if arm in ("known", "estimated_scale") else float(y.mean())
            cache[key] = (mu, divisor, active, initial, fitted, curvature)
        values = (*cache[key], config["factor"] / cache[key][-1])
        for name, value in zip(result, values, strict=True):
            result[name].append(value)
    return {k: np.asarray(v) for k, v in result.items()}


def allowed(stage, query):
    factors = (
        PRACTICAL_FACTORS
        if query["search"] == "practical"
        else MUSHROOM_FACTORS
        if query["search"] == "previous"
        else FACTORS
    )
    stops = (
        CHECKPOINTS[stage]
        if query["search"] == "expanded_stops"
        else ORIGINAL_STOPS[stage]
    )
    return factors, stops


@lru_cache(maxsize=None)
def ordered_eligible(stage, arm, scale, objective, cap, search):
    query = dict(arm=arm, scale=scale, objective=objective, cap=cap, search=search)
    rows = candidate_rows(stage)
    factors, stops = allowed(stage, query)
    options = []
    for i, row in enumerate(rows):
        if (
            row["arm"] != query["arm"]
            or row["scale"] != query["scale"]
            or row["factor"] not in factors
            or row["observations"] not in stops
            or row["observations"] > query["cap"]
        ):
            continue
        options.append((row["observations"], row["batch"], row["factor"], i))
    return np.array([entry[-1] for entry in sorted(options)])


def expected_selection(validation, rows, query, rare_count, stage):
    objective = query["objective"] if rare_count or query["objective"] == 0 else 0
    ids = ordered_eligible(stage, **query)
    values = validation.reshape(-1, 2)[ids, objective]
    chosen = ids[np.argmin(np.where(np.isfinite(values), values, np.inf))]
    return [int(chosen), int(objective != query["objective"]), 0]


def independent_loss(part, coefficients, weights=None):
    x, y, rare = part
    x = x.toarray() if sparse.issparse(x) else x
    flat = coefficients.reshape(-1, coefficients.shape[-1])
    w = np.full(len(y), 1 / len(y)) if weights is None else weights
    result = []
    for start in range(0, len(flat), 128):
        block = flat[start : start + 128]
        prediction = np.einsum("nd,cd->nc", x, block[:, 1:]) + block[:, 0]
        errors = (prediction - y[:, None]) ** 2 / 2
        result.append(
            np.column_stack(
                (
                    np.sum(errors * w[:, None], axis=0),
                    np.sum(errors[rare] * w[rare, None], axis=0) / w[rare].sum()
                    if rare.any()
                    else np.full(len(block), np.nan),
                )
            )
        )
    return np.concatenate(result).reshape(*coefficients.shape[:-1], 2)


def norm_error(actual, expected, allow_status=False):
    if not allow_status:
        assert_array_equal(np.isfinite(actual), np.isfinite(expected))
    denominator = 1 + np.max(
        np.where(np.isfinite(expected), np.abs(expected), 0), axis=-1, keepdims=True
    )
    with np.errstate(invalid="ignore"):
        errors = np.abs(actual - expected) / denominator
    return float(np.nanmax(errors)) if np.isfinite(errors).any() else 0.0


def check_numerics():
    # A missing subgroup must not mask an error in the aggregate loss.
    assert norm_error(np.array([[2.0, np.nan]]), np.array([[1.0, np.nan]])) == 0.5
    assert len(FACTORS) == 25 and list(FACTORS) == sorted(set(FACTORS))
    x = np.array([[0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 0, 1]], dtype=float)
    y, mu = np.array([1, -1, 0, 2.0]), np.array([0.5, 0.1, 0.2])
    configs = configurations(0)
    params = prepare(x, y, configs, mu)
    expected = expected_parameters(x, y, configs, mu)
    for key in params:
        assert_allclose(params[key], expected[key], rtol=2e-12, atol=2e-12)
    ci = [i for i, c in enumerate(configs) if c["scale"] != "variance"]
    old = shared_prepare(x, y, [configs[i] for i in ci], mu)
    for key in params:
        assert_array_equal(params[key][ci], old[key])
    indices = np.tile([0, 1, 3, 2, 1, 1, 0, 2], 4)
    for batch in (1, 4):
        reference = reference_path(x, y, params, indices, batch, (0, 8, 32))
        for design in (x, sparse.csr_matrix(x)):
            actual = path(design, y, params, indices, batch, (0, 8, 32))
            assert norm_error(actual[0], reference[0]) < 2e-9
            assert_array_equal(actual[1], reference[1])
            assert_array_equal(actual[2], reference[2])
            inactive = [i for i, c in enumerate(configs) if c["arm"] != "known"]
            assert_allclose(
                actual[0][..., inactive, 3][np.isfinite(actual[0][..., inactive, 3])], 0
            )
    broken = {k: v.copy() for k, v in params.items()}
    broken["eta"][:] = 1e120
    actual = path(x, y, broken, indices, 1, (0, 8, 32))
    assert_array_equal(actual[2], 1)
    assert np.isnan(actual[0][1:]).all()
    vocabulary = encode_fit(np.array([["a"], ["b"]]))
    unknown, counts = encode(np.array([["c"]]), vocabulary)
    assert counts == [1] and unknown.nnz == 0
    for stage in (0, 1):
        rows, qs = candidate_rows(stage), queries(stage)
        values = np.random.default_rng(13).uniform(
            size=(2, len(CHECKPOINTS[stage]), len(configurations(stage)), 2)
        )
        for validation in (values, np.ones_like(values)):
            for q in qs:
                for count in (0, 2):
                    assert select(
                        validation, rows, q, count, stage
                    ) == expected_selection(validation, rows, q, count, stage)
        values[:, 1:] = np.nan
        for q in qs:
            selected = select(values, rows, q, 0, stage)
            assert rows[selected[0]]["observations"] == 0
            assert selected == expected_selection(values, rows, q, 0, stage)
    print(
        "Divisors, all arms, transformed updates, failures, and selection: passed.",
        flush=True,
    )


def audit_summary(manifest, case, cache):
    stage = manifest["stage"]
    label = ("synthetic", "mushroom")[stage]
    output = result_dir(label, "rates25")
    summary = json.loads((output / f"{label}-summary-c{case}.json").read_text())
    rows, qs, configs = (
        manifest[k] for k in ("candidates", "queries", "configurations")
    )
    assert summary["endpoints"] == sum(d["status"].size for d in cache)
    assert summary["failed_endpoints"] == sum(int(d["status"].sum()) for d in cache)
    assert summary["failed_paths"] == sum(
        np.count_nonzero(d["failure_update"]) for d in cache
    )
    for group in ("train", "validation", "test"):
        assert summary[group + "_rare"] == [d["meta"][group + "_rare"] for d in cache]

    def mask_for(stratum):
        return np.array(
            [
                True
                if stratum == "all"
                else (d["meta"][stratum.split("_")[0] + "_rare"] == 0)
                == stratum.endswith("absent")
                for d in cache
            ]
        )

    tests = np.array([d["test"][d["selections"][:, 0]] for d in cache])
    for entry in summary["selections"]:
        qi, q = entry["query"], qs[entry["query"]]
        assert all(entry[k] == v for k, v in q.items())
        mask = mask_for(entry["stratum"])
        group = [d for d, keep in zip(cache, mask, strict=True) if keep]
        chosen = [rows[d["selections"][qi, 0]] for d in group]
        for j, name in enumerate(("aggregate", "rare")):
            check_stat(entry[name], tests[mask, qi, j])
        for j, name in enumerate(
            ("raw_intercept", "rare_coefficient", "centered_intercept")
        ):
            check_stat(
                entry[name], [d["features"][d["selections"][qi, 0], j] for d in group]
            )
        check_stat(
            entry["eta"],
            [d["eta"][r["index"][2]] for d, r in zip(group, chosen, strict=True)],
        )
        factors, stops = allowed(stage, q)
        assert entry["nominal_tuning_observations"] == 2 * len(factors) * q["cap"]
        assert entry["initialization"] == sum(r["observations"] == 0 for r in chosen)
        assert entry["rare_fallbacks"] == sum(d["selections"][qi, 1] for d in group)
        for name, factor in (("lower_rate", factors[0]), ("upper_rate", factors[-1])):
            assert entry[name] == sum(
                r["observations"] > 0 and r["factor"] == factor for r in chosen
            )
        for name, key, values in (
            ("rate_histogram", "factor", factors),
            ("batch_histogram", "batch", BATCHES[stage]),
            ("stop_histogram", "observations", stops),
        ):
            assert entry[name] == {
                str(v): sum(
                    r[key] == v and (key != "factor" or r["observations"] > 0)
                    for r in chosen
                )
                for v in values
            }
        ci = [
            i
            for i, c in enumerate(configs)
            if c["arm"] == q["arm"]
            and c["scale"] == q["scale"]
            and c["factor"] in factors
        ]
        used = [
            sum(
                min(int(d["failure_update"][bi, i]) * b or q["cap"], q["cap"])
                for bi, b in enumerate(BATCHES[stage])
                for i in ci
            )
            for d in group
        ]
        check_stat(entry["executed_live_observations"], used)
        eligible = [
            i
            for i, r in enumerate(rows)
            if r["arm"] == q["arm"]
            and r["scale"] == q["scale"]
            and r["factor"] in factors
            and r["observations"] in stops
            and r["observations"] <= q["cap"]
        ]
        assert entry["scored_endpoints"] == len(eligible)
        assert entry["failed_eligible_endpoints"] == sum(
            int(d["status"][eligible].sum()) for d in group
        )
    for entry in summary["contrasts"]:
        qi = entry["query"]
        ri = qs.index(qs[qi] | {"scale": entry["reference"]})
        mask = mask_for(entry["stratum"])
        for j, name in enumerate(("aggregate", "rare")):
            check_stat(entry[name], tests[mask, qi, j] - tests[mask, ri, j])
    for entry in summary["failures"]:
        ci = [
            i
            for i, c in enumerate(configs)
            if c["arm"] == entry["arm"] and c["scale"] == entry["scale"]
        ]
        assert entry["paths"] == sum(
            np.count_nonzero(d["failure_update"][:, ci]) for d in cache
        )
        assert entry["endpoints"] == sum(
            int(d["status"].reshape(2, len(CHECKPOINTS[stage]), -1)[:, :, ci].sum())
            for d in cache
        )
    for entry in summary["paths"]:
        qi, mi = entry["query"], CHECKPOINTS[stage].index(entry["observations"])
        ids = []
        for d in cache:
            row = rows[d["selections"][qi, 0]]
            ids.append(
                np.ravel_multi_index(
                    (row["index"][0], mi, row["index"][2]),
                    (2, len(CHECKPOINTS[stage]), len(configs)),
                )
            )
        for j, name in enumerate(("aggregate", "rare")):
            check_stat(
                entry[name], [d["test"][i, j] for d, i in zip(cache, ids, strict=True)]
            )
        for j, name in enumerate(("raw_intercept", "rare_coefficient")):
            check_stat(
                entry[name],
                [d["features"][i, j] for d, i in zip(cache, ids, strict=True)],
            )
    lookup = {
        (r["arm"], r["scale"], r["batch"], r["observations"], r["factor"]): i
        for i, r in enumerate(rows)
    }
    with np.load(output / f"{label}-boundaries-c{case}.npz") as neighbor_archive:
        neighbors = {k: neighbor_archive[k] for k in neighbor_archive.files}
        for rep, d in enumerate(cache):
            for qi, q in enumerate(qs):
                row = rows[d["selections"][qi, 0]]
                factors, _ = allowed(stage, q)
                fi = factors.index(row["factor"])
                effective = 0 if d["selections"][qi, 1] else q["objective"]
                for j, other in enumerate((fi - 1, fi + 1)):
                    ni = int(neighbors["neighbor_candidates"][rep, qi, j])
                    if row["observations"] == 0 or other not in range(len(factors)):
                        assert ni == -1
                        continue
                    assert (
                        ni
                        == lookup[
                            (
                                row["arm"],
                                row["scale"],
                                row["batch"],
                                row["observations"],
                                factors[other],
                            )
                        ]
                    )
                    score = d["validation"][ni, effective]
                    assert_allclose(neighbors["neighbor_scores"][rep, qi, j], score)
                    assert neighbors["neighbor_failed"][rep, qi, j] == d["status"][ni]
                    assert (
                        not np.isfinite(score)
                        or score >= d["validation"][d["selections"][qi, 0], effective]
                    )


def check_artifacts():
    audit = dict(
        max_path_error=0.0,
        max_prediction_error=0.0,
        max_shared_path_error=0.0,
        max_loss_error=0.0,
        gate_violations=[],
        endpoints=0,
        decisions=0,
        replayed_paths=0,
    )
    raw = load_mushroom()
    for stage, label in enumerate(("synthetic", "mushroom")):
        output = result_dir(label, "rates25")
        manifest = json.loads((output / f"{label}.json").read_text())
        rows, qs, configs = candidate_rows(stage), queries(stage), configurations(stage)
        assert (
            manifest["candidates"] == rows
            and manifest["queries"] == qs
            and manifest["configurations"] == configs
        )
        expected_cases = len(LAWS) if stage == 0 else len(SIZES)
        assert [(m["case"], m["rep"]) for m in manifest["replications"]] == [
            (c, r) for c in range(expected_cases) for r in range(REPS[stage])
        ]
        old_manifest = json.loads(
            (result_dir(label, "rates5") / f"{label}.json").read_text()
        )
        old_ci = [configs.index(c) for c in old_manifest["configurations"]]
        old_mi = [CHECKPOINTS[stage].index(m) for m in ORIGINAL_STOPS[stage]]
        with ExitStack() as stack:
            old = stack.enter_context(
                np.load(result_dir(label, "rates5") / f"{label}.npz")
            )
            for case in range(expected_cases):
                cache = []
                metas = [m for m in manifest["replications"] if m["case"] == case]
                with ExitStack() as shards:
                    archives = {
                        p: shards.enter_context(np.load(output / p))
                        for p in {m["archive"] for m in metas}
                    }
                    for meta in metas:
                        rep, prefix = meta["rep"], meta["prefix"]
                        archive = archives[meta["archive"]]
                        data = {
                            k: archive[prefix + k]
                            for k in (
                                "coefficients",
                                "centered_intercepts",
                                "status",
                                "failure_update",
                                "indices",
                                "test",
                                "train",
                                "validation",
                                "selections",
                            )
                        }
                        coeff, chosen = data["coefficients"], data["selections"]
                        assert coeff.shape == (
                            2,
                            len(CHECKPOINTS[stage]),
                            len(configs),
                            meta["dimension"] + 1,
                        )
                        assert_array_equal(
                            np.isnan(coeff).all(axis=-1), data["status"] > 0
                        )
                        for bi, batch in enumerate(BATCHES[stage]):
                            for mi, m in enumerate(CHECKPOINTS[stage]):
                                failed = data["failure_update"][bi]
                                assert_array_equal(
                                    data["status"][bi, mi],
                                    (failed > 0) & (failed * batch <= m),
                                )
                        parts, details, weights, mu = dataset(stage, case, rep, raw)
                        assert details["names"] == meta["names"]
                        expected = expected_parameters(*parts[0][:2], configs, mu)
                        params = {
                            k: archive[prefix + "parameter_" + k] for k in expected
                        }
                        for key in expected:
                            assert_allclose(
                                params[key], expected[key], rtol=2e-10, atol=2e-11
                            )
                        assert_array_equal(
                            data["indices"],
                            rng(stage, case, rep, 2).integers(
                                len(parts[0][1]), size=max(CHECKPOINTS[stage])
                            ),
                        )
                        reconstruction = None
                        for ni, (name, part) in enumerate(
                            zip(("train", "validation", "test"), parts, strict=True)
                        ):
                            assert meta[name + "_rare"] == int(part[2].sum()) and meta[
                                "n_" + name
                            ] == len(part[1])
                            if stage:
                                assert_array_equal(
                                    archive[prefix + "partition_" + name],
                                    details["partitions"][ni],
                                )
                                assert details["unknown"] == meta["unknown"]
                            loss = independent_loss(
                                part, coeff, weights if name == "test" else None
                            )
                            error = norm_error(data[name], loss)
                            audit["max_loss_error"] = max(
                                audit["max_loss_error"], error
                            )
                            if error > 2e-9:
                                audit["gate_violations"].append(
                                    dict(
                                        stage=stage,
                                        case=case,
                                        rep=rep,
                                        kind=name + "_loss",
                                        error=error,
                                    )
                                )
                            if name == "validation":
                                reconstruction = loss
                        for qi, query in enumerate(qs):
                            assert_array_equal(
                                chosen[qi],
                                expected_selection(
                                    data["validation"],
                                    rows,
                                    query,
                                    meta["validation_rare"],
                                    stage,
                                ),
                            )
                            restored = expected_selection(
                                reconstruction,
                                rows,
                                query,
                                meta["validation_rare"],
                                stage,
                            )[0]
                            if restored != chosen[qi, 0]:
                                audit["gate_violations"].append(
                                    dict(
                                        stage=stage,
                                        case=case,
                                        rep=rep,
                                        kind="reconstructed_selection",
                                        query=qi,
                                        candidate=int(chosen[qi, 0]),
                                        reconstructed=restored,
                                    )
                                )
                        op = f"c{case}_r{rep}_"
                        old_choices = old[op + "selections"]
                        assert_array_equal(data["indices"], old[op + "indices"])
                        error = norm_error(
                            coeff[:, old_mi][:, :, old_ci], old[op + "coefficients"]
                        )
                        audit["max_shared_path_error"] = max(
                            audit["max_shared_path_error"], error
                        )
                        if error > 2e-9:
                            audit["gate_violations"].append(
                                dict(
                                    stage=stage,
                                    case=case,
                                    rep=rep,
                                    kind="shared_path",
                                    error=error,
                                )
                            )
                        for qi, query in enumerate(qs):
                            if (
                                query["search"] == "practical"
                                and query["scale"] != "variance"
                            ):
                                oq = {
                                    k: v for k, v in query.items() if k != "search"
                                } | {"rule": "joint"}
                                old_id = old_choices[
                                    old_manifest["queries"].index(oq), 0
                                ]
                                old_row = old_manifest["candidates"][old_id]
                                new_row = rows[chosen[qi, 0]]
                                assert all(
                                    old_row[k] == new_row[k]
                                    for k in (
                                        "arm",
                                        "scale",
                                        "factor",
                                        "batch",
                                        "observations",
                                    )
                                )
                        if stage:
                            prior_dir = ROOT / "results/mushroom/damping"
                            with np.load(
                                prior_dir / f"paths-c{case}-r{rep:02d}.npz"
                            ) as sensitivity:
                                old_configs = json.loads(
                                    (prior_dir / "manifest.json").read_text()
                                )["configurations"]
                                pairs = [
                                    (
                                        i,
                                        configs.index(
                                            c
                                            | {
                                                "scale": "damped"
                                                if c["scale"] == "damped_0.01"
                                                else c["scale"]
                                            }
                                        ),
                                    )
                                    for i, c in enumerate(old_configs)
                                    if c["scale"]
                                    in ("none", "sd", "variance", "damped_0.01")
                                ]
                                error = norm_error(
                                    coeff[:, :, [p[1] for p in pairs]],
                                    sensitivity["coefficients"][
                                        :, :, [p[0] for p in pairs]
                                    ],
                                )
                                audit["max_shared_path_error"] = max(
                                    audit["max_shared_path_error"], error
                                )
                                assert error < 2e-9
                        for bi, batch in enumerate(BATCHES[stage]):
                            ci = (
                                list(range(len(configs)))
                                if rep == 0
                                else sorted(
                                    {
                                        rows[i]["index"][2]
                                        for i in chosen[:, 0]
                                        if rows[i]["index"][0] == bi
                                    }
                                )
                            )
                            if not ci:
                                continue
                            reference = reference_path(
                                *parts[0][:2],
                                {k: v[ci] for k, v in params.items()},
                                data["indices"],
                                batch,
                                CHECKPOINTS[stage],
                            )
                            different = np.flatnonzero(
                                data["failure_update"][bi, ci] != reference[2]
                            )
                            for j in different:
                                audit["gate_violations"].append(
                                    dict(
                                        stage=stage,
                                        case=case,
                                        rep=rep,
                                        batch=batch,
                                        kind="failure_update",
                                        configuration=ci[j],
                                        archived=int(data["failure_update"][bi, ci[j]]),
                                        reference=int(reference[2][j]),
                                    )
                                )
                            status_difference = np.argwhere(
                                data["status"][bi][:, ci] != reference[1]
                            )
                            for mi, j in status_difference:
                                audit["gate_violations"].append(
                                    dict(
                                        stage=stage,
                                        case=case,
                                        rep=rep,
                                        batch=batch,
                                        kind="checkpoint_status",
                                        configuration=ci[j],
                                        observations=CHECKPOINTS[stage][mi],
                                        archived=int(data["status"][bi, mi, ci[j]]),
                                        reference=int(reference[1][mi, j]),
                                    )
                                )
                            # Status disagreements are retained separately from errors
                            # measured where both implementations remain finite.
                            error = norm_error(
                                coeff[bi][:, ci], reference[0], allow_status=True
                            )
                            audit["max_path_error"] = max(
                                audit["max_path_error"], error
                            )
                            audit["replayed_paths"] += len(ci)
                            if error > 2e-9:
                                audit["gate_violations"].append(
                                    dict(
                                        stage=stage,
                                        case=case,
                                        rep=rep,
                                        batch=batch,
                                        kind="transformed_path",
                                        error=error,
                                    )
                                )
                            for qi, candidate in enumerate(chosen[:, 0]):
                                b, mi, c = rows[candidate]["index"]
                                if b != bi:
                                    continue
                                actual = coeff[b, mi, c]
                                ref = reference[0][mi, ci.index(c)]
                                if not np.isfinite(ref).all():
                                    audit["gate_violations"].append(
                                        dict(
                                            stage=stage,
                                            case=case,
                                            rep=rep,
                                            query=qi,
                                            kind="selected_reference_failed",
                                        )
                                    )
                                    continue
                                x = parts[1][0]
                                prediction = x @ actual[1:] + actual[0]
                                other = x @ ref[1:] + ref[0]
                                error = float(
                                    np.max(np.abs(prediction - other))
                                    / (1 + np.max(np.abs(other)))
                                )
                                audit["max_prediction_error"] = max(
                                    audit["max_prediction_error"], error
                                )
                                if error > 1e-8:
                                    audit["gate_violations"].append(
                                        dict(
                                            stage=stage,
                                            case=case,
                                            rep=rep,
                                            query=qi,
                                            kind="selected_prediction",
                                            error=error,
                                        )
                                    )
                        rare_name = "rare" if stage == 0 else "spore-print-color=r"
                        flat = coeff.reshape(-1, coeff.shape[-1])
                        j = (
                            meta["names"].index(rare_name) + 1
                            if rare_name in meta["names"]
                            else None
                        )
                        rare_coef = (
                            flat[:, j]
                            if j
                            else np.where(np.isfinite(flat[:, 0]), 0, np.nan)
                        )
                        cache.append(
                            dict(
                                meta=meta,
                                selections=chosen,
                                status=data["status"].ravel(),
                                failure_update=data["failure_update"],
                                test=data["test"].reshape(-1, 2),
                                validation=data["validation"].reshape(-1, 2),
                                eta=params["eta"],
                                features=np.column_stack(
                                    (
                                        flat[:, 0],
                                        rare_coef,
                                        data["centered_intercepts"].ravel(),
                                    )
                                ),
                            )
                        )
                        audit["endpoints"] += data["status"].size
                        audit["decisions"] += len(chosen)
                audit_summary(manifest, case, cache)
                print(
                    f"Audited {label} case {case + 1}; "
                    f"{len(audit['gate_violations'])} retained gate violations.",
                    flush=True,
                )
    return audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--numerics-only", action="store_true")
    parser.add_argument("--write-audit", action="store_true")
    args = parser.parse_args()
    check_numerics()
    if not args.numerics_only:
        result = check_artifacts()
        if args.write_audit:
            write_json(ROOT / "results/diagnostics/numerical-audit.json", result)
        else:
            assert json.loads(
                (ROOT / "results/diagnostics/numerical-audit.json").read_text()
            ) == jsonable(result)
        print(
            "Structural and summary audit passed; "
            f"{len(result['gate_violations'])} numerical gate violations retained."
        )


if __name__ == "__main__":
    main()
