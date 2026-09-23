"""Independent updates, selections, paired summaries, and shared-study audit."""

import argparse
import json
from contextlib import ExitStack

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
from scipy import sparse

from experiments.common.data import ROOT, SCALES, load_mushroom, mushroom_data
from experiments.common.dynamics import path as shared_path
from experiments.common.dynamics import prepare
from experiments.common.dynamics import recorded_path as path
from experiments.mushroom.rates17 import (
    ARMS,
    BATCHES,
    CHECKPOINTS,
    FACTORS,
    ORIGINAL_FACTORS,
    ORIGINAL_STOPS,
    OUTPUT,
    REPS,
    candidate_rows,
    configurations,
    pool,
    queries,
    select,
)


def reference_path(x, y, params, indices, batch, checkpoints):
    """Use explicitly transformed features and coefficients in optimizer coordinates."""
    x = x.toarray() if sparse.issparse(x) else x
    z = (x[None, :, :] - params["mu"][:, None, :]) / params["divisor"][:, None, :]
    z *= params["active"][:, None, :]
    theta = np.zeros_like(params["mu"])
    intercept = params["initial"].copy()
    failures = np.zeros(len(theta), dtype=np.int32)
    coefs, status, centered_intercepts = [], [], []

    def save():
        beta = theta / params["divisor"]
        value = np.column_stack((intercept - np.sum(params["mu"] * beta, axis=1), beta))
        value[failures > 0] = np.nan
        coefs.append(value)
        status.append((failures > 0).astype(np.uint8))
        centered_intercepts.append(np.where(failures > 0, np.nan, intercept))

    save()
    for update, start in enumerate(range(0, max(checkpoints), batch), start=1):
        ids = indices[start : start + batch]
        features = z[:, ids, :]
        with np.errstate(over="ignore", invalid="ignore"):
            error = (
                np.einsum("cbd,cd->cb", features, theta) + intercept[:, None] - y[ids]
            )
            theta -= (
                params["eta"][:, None]
                * np.einsum("cbd,cb->cd", features, error)
                / batch
            )
            intercept -= (
                params["eta"] * params["fit_intercept"] * np.mean(error, axis=1)
            )
            beta = theta / params["divisor"]
        bad = (
            ~np.isfinite(beta).all(axis=1)
            | ~np.isfinite(intercept)
            | (np.max(np.abs(beta), axis=1) > 1e100)
            | (np.abs(intercept) > 1e100)
        )
        failures[(failures == 0) & bad] = update
        theta[failures > 0] = 0
        intercept[failures > 0] = 0
        if update * batch in checkpoints:
            save()
    return np.array(coefs), np.array(status), failures, np.array(centered_intercepts)


def independent_loss(x, y, rare, coefficients):
    flat = coefficients.reshape(-1, coefficients.shape[-1])
    design = x.toarray() if sparse.issparse(x) else x
    result = []
    for start in range(0, len(flat), 128):
        block = flat[start : start + 128]
        prediction = np.einsum("nd,cd->nc", design, block[:, 1:]) + block[:, 0]
        error = (prediction - y[:, None]) ** 2 / 2
        result.append(
            np.column_stack(
                (
                    error.mean(axis=0),
                    error[rare].mean(axis=0)
                    if rare.any()
                    else np.full(len(block), np.nan),
                )
            )
        )
    return np.concatenate(result).reshape(*coefficients.shape[:-1], 2)


def independent_components(coeff, params, names, test, centered_intercepts):
    x, _, rare = test
    flat = coeff.reshape(-1, coeff.shape[-1])
    shifts = np.tile(params["mu"], (coeff.shape[0] * coeff.shape[1], 1))
    centered = centered_intercepts.ravel()
    if "spore-print-color=r" in names:
        j = names.index("spore-print-color=r")
        green = flat[:, j + 1]
        contribution = green * (1 - shifts[:, j])
    else:
        green = np.zeros(len(flat))
        contribution = green.copy()
    prediction = (
        np.asarray(x[rare] @ flat[:, 1:].T + flat[:, 0]).mean(axis=0)
        if rare.any()
        else np.full(len(flat), np.nan)
    )
    result = dict(
        raw_intercept=flat[:, 0],
        green_coefficient=green,
        centered_intercept=centered,
        green_contribution=contribution,
        other_contribution=prediction - centered - contribution,
        rare_mean_prediction=prediction,
    )
    for value in result.values():
        value[~np.isfinite(flat).all(axis=1)] = np.nan
    return result


def expected_selection(validation, rows, query, rare_count):
    objective = 0 if query["objective"] == 1 and rare_count == 0 else query["objective"]
    allowed = ORIGINAL_FACTORS if query["search"] in ("fixed", "original") else FACTORS
    stops = CHECKPOINTS if query["search"] == "expanded_stops" else ORIGINAL_STOPS
    options, initial = [], []
    for i, r in enumerate(rows):
        if (
            r["arm"] != query["arm"]
            or r["scale"] != query["scale"]
            or r["factor"] not in allowed
        ):
            continue
        score = validation[tuple(r["index"])][objective]
        key = (
            score if np.isfinite(score) else np.inf,
            r["observations"],
            r["batch"],
            r["factor"],
            i,
        )
        if r["observations"] == 0:
            initial.append((key, i))
        if r["observations"] not in stops:
            continue
        if query["rule"] == "fixed" and (
            r["observations"] != query["cap"] or r["batch"] != 16 or r["factor"] != 0.05
        ):
            continue
        if query["rule"] == "rate_batch" and r["observations"] != query["cap"]:
            continue
        if query["rule"] == "joint" and r["observations"] > query["cap"]:
            continue
        options.append((key, i))
    winner = min(options)
    failed = not np.isfinite(winner[0][0])
    if failed:
        winner = min(initial)
        assert np.isfinite(winner[0][0])
    return [winner[1], int(objective != query["objective"]), int(failed)]


def check_numerics():
    x = np.array([[0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 0, 1]], dtype=float)
    y = np.array([1, -1, 0, 2], dtype=float)
    params = prepare(x, y, configurations())
    indices = np.tile([0, 1, 3, 2, 1, 1, 0, 2], 4)
    for batch in (1, 4):
        expected = reference_path(x, y, params, indices, batch, (0, 8, 32))
        for design in (x, sparse.csr_matrix(x)):
            actual = path(design, y, params, indices, batch, (0, 8, 32))
            norm = 1 + np.max(np.abs(expected[0]), axis=-1)
            assert np.nanmax(np.abs(actual[0] - expected[0]) / norm[..., None]) < 2e-11
            assert_array_equal(actual[1], expected[1])
            assert_array_equal(actual[2], expected[2])
            fixed = ~params["fit_intercept"]
            assert_allclose(
                actual[3][:, fixed],
                np.broadcast_to(params["initial"][fixed], actual[3][:, fixed].shape),
            )
            if batch == 1:
                recovered = actual[0][..., 0] + np.sum(
                    params["mu"] * actual[0][..., 1:], axis=-1
                )
                assert np.max(np.abs(recovered[:, fixed] - actual[3][:, fixed])) > 1e-8
            shared = shared_path(design, y, params, indices, batch, (0, 8, 32))
            assert_allclose(actual[0], shared[0])
            assert_array_equal(actual[1], shared[1])
    assert not params["active"][:, 2].any()
    assert_allclose(actual[0][..., 3], 0)
    failure_params = {k: v.copy() for k, v in params.items()}
    failure_params["eta"][:] = 1e120
    broken = path(x, y, failure_params, indices, 1, (0, 8, 32))
    ref_broken = reference_path(x, y, failure_params, indices, 1, (0, 8, 32))
    assert_array_equal(broken[2], np.ones(len(configurations())))
    assert_array_equal(broken[1], ref_broken[1])
    assert np.isnan(broken[0][1:]).all()
    rows = candidate_rows()
    assert len(FACTORS) == 17 and len(set(FACTORS)) == 17
    assert set(ORIGINAL_FACTORS) <= set(FACTORS)
    assert len(rows) == 2448
    assert [len(pool(rows, s)) for s in ("original", "expanded", "expanded_stops")] == [
        360,
        1224,
        2448,
    ]
    for arm in ARMS:
        for scale in SCALES:
            assert (
                sum(c["arm"] == arm and c["scale"] == scale for c in configurations())
                == 17
            )
    validation = np.ones((2, 8, 153, 2))
    for q in queries():
        for count in (0, 2):
            assert select(validation, rows, q, count)[0] == expected_selection(
                validation, rows, q, count
            )
    # A new rate and a new stop must enter only their declared candidate pools.
    for factor, observations in ((1.2, 2048), (1.2, 1024)):
        val = validation.copy()
        i = next(
            i
            for i, r in enumerate(rows)
            if r["arm"] == "centered_fitted"
            and r["scale"] == "none"
            and r["factor"] == factor
            and r["observations"] == observations
            and r["batch"] == 16
        )
        val[tuple(rows[i]["index"])] = 0
        q = dict(
            arm="centered_fitted", scale="none", objective=0, cap=8192, rule="joint"
        )
        assert select(val, rows, q | {"search": "original"}, 2)[0][0] != i
        assert (select(val, rows, q | {"search": "expanded"}, 2)[0][0] == i) == (
            observations in ORIGINAL_STOPS
        )
        assert select(val, rows, q | {"search": "expanded_stops"}, 2)[0][0] == i
    validation[:, 1:] = np.nan
    for q in queries():
        actual = select(validation, rows, q, 0)[0]
        assert actual == expected_selection(validation, rows, q, 0)
        assert rows[actual[0]]["observations"] == 0
        assert bool(actual[2]) == (q["rule"] != "joint")
    print(
        "Rate-search updates, failure times, candidate pools, ties, "
        "and fallbacks: passed"
    )


def check_stat(actual, values):
    values = np.asarray(values)
    good = values[np.isfinite(values)]
    assert actual["n"] == len(good)
    assert actual["missing"] == len(values) - len(good)
    if len(good):
        scale = max(np.max(np.abs(good)), 1e-300)
        normalized = good / scale
        for key, value in (
            ("mean", np.mean(normalized)),
            ("median", np.median(normalized)),
            ("p95", np.quantile(normalized, 0.95)),
            ("maximum", np.max(normalized)),
        ):
            assert_allclose(actual[key] / scale, value, rtol=2e-10, atol=2e-12)
        if len(good) > 1:
            assert_allclose(
                actual["mcse"] / scale,
                np.std(normalized, ddof=1) / np.sqrt(len(good)),
                rtol=2e-10,
                atol=2e-12,
            )
    else:
        assert actual["mean"] is None


def check_artifacts():
    manifest = json.loads((OUTPUT / "manifest.json").read_text())
    summary = json.loads((OUTPUT / "summary.json").read_text())
    assert manifest["configurations"] == configurations()
    assert manifest["candidates"] == candidate_rows()
    assert manifest["queries"] == queries()
    assert len(manifest["replications"]) == 64
    rows = manifest["candidates"]
    shared_dir = ROOT / "results/mushroom/rates5"
    shared_manifest = json.loads((shared_dir / "mushroom.json").read_text())
    old_configs = shared_manifest["configurations"]
    old_ci = [configurations().index(c) for c in old_configs]
    old_mi = [CHECKPOINTS.index(m) for m in ORIGINAL_STOPS]
    raw = load_mushroom()
    caches = {}
    max_path_error, max_prediction_error = 0.0, 0.0
    with ExitStack() as stack:
        archives = {
            name: stack.enter_context(np.load(OUTPUT / name))
            for name in manifest["archives"]
        }
        shared = stack.enter_context(np.load(shared_dir / "mushroom.npz"))
        for meta in manifest["replications"]:
            archive = archives[meta["archive"]]
            case, rep = meta["case"], meta["rep"]
            prefix = f"c{case}_r{rep}_"
            coeff, status, selections = (
                archive[prefix + key]
                for key in ("coefficients", "status", "selections")
            )
            centered = archive[prefix + "centered_intercepts"]
            assert coeff.shape == (2, 8, 153, meta["dimension"] + 1)
            assert_array_equal(np.isnan(coeff).all(axis=-1), status > 0)
            parts, details = mushroom_data(raw, case, rep)
            assert (
                details["names"] == meta["names"]
                and details["unknown"] == meta["unknown"]
            )
            params = prepare(*parts[0][:2], configurations())
            raw_norm = 1 + np.sum(np.abs(coeff), axis=-1)
            reconstructed = coeff[..., 0] + np.einsum(
                "bmcd,cd->bmc", coeff[..., 1:], params["mu"]
            )
            assert np.nanmax(np.abs(centered - reconstructed) / raw_norm) < 1e-12
            fixed = ~params["fit_intercept"]
            fixed_expected = np.broadcast_to(
                params["initial"][fixed], centered[:, :, fixed].shape
            ).copy()
            fixed_expected[status[:, :, fixed] > 0] = np.nan
            assert_array_equal(centered[:, :, fixed], fixed_expected)
            for name, value in params.items():
                assert_allclose(
                    archive[prefix + "parameter_" + name], value, rtol=1e-13, atol=1e-13
                )
            for name, expected, part in zip(
                ("train", "validation", "test"),
                details["partitions"],
                parts,
                strict=True,
            ):
                assert_array_equal(archive[prefix + "partition_" + name], expected)
                assert_array_equal(
                    archive[prefix + "partition_" + name],
                    shared[prefix + "partition_" + name],
                )
                assert meta[name + "_rare"] == part[2].sum()
                assert_allclose(
                    archive[prefix + name],
                    independent_loss(*part, coeff),
                    rtol=2e-9,
                    atol=2e-10,
                )
            assert_array_equal(archive[prefix + "indices"], shared[prefix + "indices"])
            old_coeff = coeff[:, old_mi][:, :, old_ci]
            assert_allclose(
                old_coeff, shared[prefix + "coefficients"], rtol=2e-10, atol=2e-10
            )
            validation = archive[prefix + "validation"]
            for qi, q in enumerate(queries()):
                assert_array_equal(
                    selections[qi],
                    expected_selection(validation, rows, q, meta["validation_rare"]),
                )
                if q["search"] in ("original", "fixed"):
                    oq = {k: v for k, v in q.items() if k != "search"}
                    oqi = shared_manifest["queries"].index(oq)
                    old_id = shared[prefix + "selections"][oqi, 0]
                    old_row = shared_manifest["candidates"][old_id]
                    new_row = rows[selections[qi, 0]]
                    assert all(
                        new_row[k] == old_row[k] for k in old_row if k != "index"
                    )
            for bi, batch in enumerate(BATCHES):
                ci = (
                    list(range(153))
                    if rep == 0
                    else sorted(
                        {
                            rows[i]["index"][2]
                            for i in selections[:, 0]
                            if rows[i]["index"][0] == bi
                        }
                    )
                )
                if not ci:
                    continue
                parameters = {k: v[ci] for k, v in params.items()}
                expected, flags, times, expected_centered = reference_path(
                    *parts[0][:2],
                    parameters,
                    archive[prefix + "indices"],
                    batch,
                    CHECKPOINTS,
                )
                actual = coeff[bi][:, ci]
                assert_array_equal(status[bi][:, ci], flags)
                assert_array_equal(archive[prefix + "failure_update"][bi, ci], times)
                live = flags == 0
                scale = 1 + np.max(np.abs(expected[live]), axis=-1)
                error = np.max(np.abs(actual[live] - expected[live]), axis=-1) / scale
                max_path_error = max(max_path_error, float(error.max()))
                assert np.all(error < 2e-9)
                centered_error = (
                    np.abs(centered[bi][:, ci][live] - expected_centered[live]) / scale
                )
                assert np.all(centered_error < 2e-9)
                for candidate in set(selections[:, 0]):
                    cbi, mi, config = rows[candidate]["index"]
                    if cbi != bi:
                        continue
                    reference = expected[mi, ci.index(config)]
                    actual_pred = (
                        parts[1][0] @ coeff[bi, mi, config, 1:]
                        + coeff[bi, mi, config, 0]
                    )
                    ref_pred = parts[1][0] @ reference[1:] + reference[0]
                    discrepancy = float(
                        np.max(np.abs(actual_pred - ref_pred) / (1 + np.abs(ref_pred)))
                    )
                    max_prediction_error = max(max_prediction_error, discrepancy)
                    assert discrepancy <= 1e-8, (case, rep, candidate, discrepancy)
            test = archive[prefix + "test"].reshape(-1, 2)
            caches[(case, rep)] = dict(
                test=test,
                train=archive[prefix + "train"].reshape(-1, 2),
                validation=validation.reshape(-1, 2),
                features=independent_components(
                    coeff, params, meta["names"], parts[2], centered
                ),
                eta=params["eta"],
                curvature=params["curvature"],
                selection=selections,
                status=status.ravel(),
                failure_update=archive[prefix + "failure_update"],
            )
            if (rep + 1) % 8 == 0:
                print(
                    f"Independent replay and all losses/selections: "
                    f"size {case}, {rep + 1}/32",
                    flush=True,
                )
    for case in range(2):
        metas = [m for m in manifest["replications"] if m["case"] == case]
        cache = [caches[case, rep] for rep in range(REPS)]
        selected = np.array([c["test"][c["selection"][:, 0]] for c in cache])
        stats = next(c for c in summary["cases"] if c["case"] == case)
        assert stats["endpoints"] == sum(c["status"].size for c in cache)
        assert stats["failed_endpoints"] == sum(c["status"].sum() for c in cache)
        assert stats["failed_paths"] == sum(
            np.count_nonzero(c["failure_update"]) for c in cache
        )
        for record in summary["selections"] + summary["contrasts"]:
            if record["case"] != case:
                continue
            stratum = record["stratum"]
            mask = np.array(
                [
                    stratum == "all"
                    or (
                        stratum.endswith("absent")
                        and m[stratum.split("_")[0] + "_rare"] == 0
                    )
                    or (
                        stratum.endswith("present")
                        and m[stratum.split("_")[0] + "_rare"] > 0
                    )
                    for m in metas
                ]
            )
            values = selected[:, record["query"]]
            if "reference" in record:
                values = values - selected[:, record["reference"]]
            for j, metric in enumerate(("aggregate", "rare")):
                check_stat(record[metric], values[mask, j])
            if "reference" not in record:
                chosen = [rows[c["selection"][record["query"], 0]] for c in cache]
                factors = (
                    ORIGINAL_FACTORS
                    if record["search"] in ("fixed", "original")
                    else FACTORS
                )
                for name in cache[0]["features"]:
                    check_stat(
                        record[name],
                        [
                            c["features"][name][c["selection"][record["query"], 0]]
                            for i, c in enumerate(cache)
                            if mask[i]
                        ],
                    )
                for metric, source in (
                    ("absolute_eta", "eta"),
                    ("curvature", "curvature"),
                ):
                    check_stat(
                        record[metric],
                        [
                            cache[i][source][r["index"][2]]
                            for i, r in enumerate(chosen)
                            if mask[i]
                        ],
                    )
                for j, metric in enumerate(("validation_aggregate", "validation_rare")):
                    check_stat(
                        record[metric],
                        [
                            c["validation"][c["selection"][record["query"], 0], j]
                            for i, c in enumerate(cache)
                            if mask[i]
                        ],
                    )
                for key, column in (("rare_fallbacks", 1), ("failed_fallbacks", 2)):
                    assert record[key] == sum(
                        c["selection"][record["query"], column]
                        for i, c in enumerate(cache)
                        if mask[i]
                    )
                configs = [
                    i
                    for i, c in enumerate(configurations())
                    if c["arm"] == record["arm"]
                    and c["scale"] == record["scale"]
                    and c["factor"] in factors
                    and (record["rule"] != "fixed" or c["factor"] == 0.05)
                ]
                batch_ids = [0] if record["rule"] == "fixed" else [0, 1]
                assert record["nominal_tuning_observations"] == record["cap"] * len(
                    configs
                ) * len(batch_ids)
                costs = []
                for i, c in enumerate(cache):
                    if not mask[i]:
                        continue
                    cost = 0
                    for bi in batch_ids:
                        for ci in configs:
                            failure = int(c["failure_update"][bi, ci])
                            cost += (
                                min(record["cap"], failure * BATCHES[bi])
                                if failure
                                else record["cap"]
                            )
                    costs.append(cost)
                check_stat(record["executed_live_observations"], costs)
                assert record["largest_rate"] == sum(
                    mask[i] and r["observations"] > 0 and r["factor"] == factors[-1]
                    for i, r in enumerate(chosen)
                )
                for key, histogram in record["selection_counts"].items():
                    for value, count in histogram.items():
                        assert count == sum(
                            mask[i] and r[key] == float(value)
                            for i, r in enumerate(chosen)
                        )
        for curve in (c for c in summary["curves"] if c["case"] == case):
            i = curve["candidate"]
            for j, metric in enumerate(("aggregate", "rare")):
                check_stat(curve[metric], [c["test"][i, j] for c in cache])
                check_stat(
                    curve["validation_" + metric],
                    [c["validation"][i, j] for c in cache],
                )
                check_stat(curve["train_" + metric], [c["train"][i, j] for c in cache])
            for name in cache[0]["features"]:
                check_stat(curve[name], [c["features"][name][i] for c in cache])
            assert curve["failed_endpoints"] == sum(c["status"][i] for c in cache)
        for record in (p for p in summary["selected_paths"] if p["case"] == case):
            path_ids = []
            selected_rows = []
            for c in cache:
                chosen = rows[c["selection"][record["query"], 0]]
                selected_rows.append(chosen)
                path_ids.append(
                    next(
                        i
                        for i, r in enumerate(rows)
                        if r["observations"] == record["observations"]
                        and all(
                            r[k] == chosen[k]
                            for k in ("arm", "scale", "factor", "batch")
                        )
                    )
                )
            for j, metric in enumerate(("aggregate", "rare")):
                check_stat(
                    record[metric],
                    [c["test"][i, j] for c, i in zip(cache, path_ids, strict=True)],
                )
            for name in cache[0]["features"]:
                check_stat(
                    record[name],
                    [
                        c["features"][name][i]
                        for c, i in zip(cache, path_ids, strict=True)
                    ],
                )
            assert record["stopped_by_checkpoint"] == sum(
                r["observations"] <= record["observations"] for r in selected_rows
            )
            assert record["failed_endpoints"] == sum(
                c["status"][i] for c, i in zip(cache, path_ids, strict=True)
            )
        for boundary in (b for b in summary["boundaries"] if b["case"] == case):
            c = cache[boundary["rep"]]
            q = queries()[boundary["query"]]
            candidate = int(c["selection"][boundary["query"], 0])
            assert boundary["candidate"] == candidate
            row = rows[candidate]
            objective = (
                0
                if q["objective"] == 1
                and metas[boundary["rep"]]["validation_rare"] == 0
                else q["objective"]
            )
            assert boundary["initialization"] == (row["observations"] == 0)
            for direction, neighbor in boundary["neighbors"].items():
                pos = FACTORS.index(row["factor"]) + (
                    1 if direction == "higher" else -1
                )
                if pos not in range(len(FACTORS)):
                    assert neighbor is None
                    continue
                other = rows[neighbor["candidate"]]
                assert other["factor"] == FACTORS[pos]
                assert all(
                    other[k] == row[k]
                    for k in ("arm", "scale", "batch", "observations")
                )
                score = c["validation"][neighbor["candidate"], objective]
                assert neighbor["failed"] == bool(c["status"][neighbor["candidate"]])
                assert neighbor["finite_score"] == bool(np.isfinite(score))
                assert neighbor["no_better"] == bool(
                    not np.isfinite(score)
                    or score >= c["validation"][candidate, objective]
                )
                if np.isfinite(score):
                    assert_allclose(neighbor["score"], score)
    print(
        "All 156672 endpoints, 20736 selections, paired summaries, boundaries, "
        f"and consistency: passed; maximum path error {max_path_error:.3g}, "
        f"selected validation prediction error {max_prediction_error:.3g}"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--numerics-only", action="store_true")
    args = parser.parse_args()
    check_numerics()
    if not args.numerics_only:
        check_artifacts()


if __name__ == "__main__":
    main()
