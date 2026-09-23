"""Independent transformed-design paths, split checks, and artifact audit."""

import argparse
import json

import numpy as np
from numpy.testing import assert_allclose
from scipy import sparse

from experiments.common.data import (
    LAWS,
    MUSHROOM_M,
    REPS,
    SCALES,
    SIZES,
    SYNTHETIC_M,
    configurations,
    encode,
    encode_fit,
    load_mushroom,
    mushroom_data,
    result_dir,
    synthetic_data,
)
from experiments.common.dynamics import candidates, choose, losses, path, prepare


def reference_path(x, y, parameters, indices, batch, checkpoints):
    """Use explicit scaled features and optimizer coordinates, never raw gradients."""
    if sparse.issparse(x):
        x = x.toarray()
    mu, divisor, active = (parameters[name] for name in ("mu", "divisor", "active"))
    z = (x[None, :, :] - mu[:, None, :]) / divisor[:, None, :] * active[:, None, :]
    theta = np.zeros_like(mu)
    intercept = parameters["initial"].copy()
    result = []

    def record():
        beta = theta / divisor
        result.append(np.column_stack((intercept - (mu * beta).sum(axis=1), beta)))

    record()
    for m in range(batch, max(checkpoints) + 1, batch):
        idx = indices[m - batch : m]
        features = z[:, idx, :]
        error = np.einsum("cbd,cd->cb", features, theta) + intercept[:, None] - y[idx]
        theta -= (
            parameters["eta"][:, None]
            * np.einsum("cbd,cb->cd", features, error)
            / batch
        )
        intercept -= (
            parameters["eta"] * parameters["fit_intercept"] * error.mean(axis=1)
        )
        if m in checkpoints:
            record()
    return np.array(result)


def independent_loss(x, y, rare, coefficients, weights=None):
    if sparse.issparse(x):
        x = x.toarray()
    augmented = np.column_stack((np.ones(len(y)), x))
    flat = coefficients.reshape(-1, coefficients.shape[-1])
    prediction = np.einsum("nd,cd->nc", augmented, flat)
    error = (prediction - y[:, None]) ** 2 / 2
    w = np.ones(len(y)) if weights is None else weights
    aggregate = np.average(error, weights=w, axis=0)
    subgroup = (
        np.average(error[rare], weights=w[rare], axis=0)
        if rare.any()
        else np.full(len(flat), np.nan)
    )
    return np.stack((aggregate, subgroup), axis=-1).reshape(*coefficients.shape[:-1], 2)


def check_numerics():
    from experiments.common.summarize_five_rates import statistics

    large = statistics([1e200, 2e200])
    assert_allclose(large["mean"], 1.5e200)
    assert_allclose(large["mcse"], 0.5e200)
    x = np.array([[0.0, 0.0, 1.0], [1.0, 0.0, 1.0], [1.0, 0.0, 1.0], [0.0, 0.0, 1.0]])
    y = np.array([1.0, -1.0, 2.0, 0.0])
    configs = configurations(0)
    params = prepare(x, y, configs, np.array([0.5, 0.1, 0.9]))
    indices = np.array([0, 1, 1, 3, 2, 0, 3, 1])
    for batch in (1, 2, 4):
        for matrix in (x, sparse.csr_matrix(x)):
            coef, status = path(matrix, y, params, indices, batch, (0, 4, 8))
            expected = reference_path(x, y, params, indices, batch, (0, 4, 8))
            assert_allclose(coef, expected, atol=2e-13, rtol=2e-13)
            assert not status.any()
            for rare in (
                np.array([False, False, True, False]),
                np.zeros(4, dtype=bool),
            ):
                assert_allclose(
                    losses(matrix, y, rare, coef),
                    independent_loss(x, y, rare, coef),
                    atol=2e-13,
                )
    empirical = np.array([c["arm"] != "known" for c in configs])
    assert not params["active"][empirical, 1:].any()
    assert_allclose(params["divisor"][empirical, 1:], 1)
    assert_allclose(coef[:, empirical, 2:], 0)
    centered = [
        i
        for i, c in enumerate(configs)
        if c["arm"] == "centered_fitted" and c["scale"] == "sd"
    ]
    assert_allclose(params["mu"][centered], np.tile(x.mean(axis=0), (len(centered), 1)))
    assert_allclose(params["divisor"][centered, 0], np.std(x[:, 0]))
    # An intercept-only full-batch fit initialized at the mean is a fixed point.
    only = np.ones((4, 2))
    pp = prepare(only, y, configurations(1))
    cc, _ = path(only, y, pp, np.arange(4), 4, (0, 4))
    assert_allclose(cc[0], cc[1], atol=1e-14)
    assert_allclose(cc[..., 0], y.mean())
    # Unknown levels are handled with the training vocabulary, including missingness.
    raw = np.array([["a", "?"], ["b", "x"]])
    vocabulary = encode_fit(raw)
    xx, unknown = encode(np.array([["unseen", "?"]]), vocabulary)
    assert xx.shape == (1, 4) and xx.nnz == 1 and unknown == [1, 0]
    assert vocabulary == [["a", "b"], ["?", "x"]]
    rows = candidates(configurations(1), (16, 128), MUSHROOM_M)
    val = np.ones((2, 4, 45, 2))
    args = dict(
        arm="centered_fitted",
        scale="all",
        cap=8192,
        objective=1,
        rule="joint_scaling",
        validation_rare_count=0,
    )
    result = choose(val, rows, **args)
    assert result[1] and not result[2]
    selected = rows[result[0]]
    assert (
        selected["observations"],
        selected["batch"],
        selected["factor"],
        selected["scale"],
    ) == (0, 16, 0.001, "none")
    val[:, 1:, :, :] = np.nan
    fallback = choose(
        val, rows, **(args | {"rule": "rate_batch", "validation_rare_count": 1})
    )
    assert fallback[2] and rows[fallback[0]]["observations"] == 0
    # Overflow is retained as a failed path, while the baseline remains selectable.
    pp["eta"][:] = 1e200
    cc, ss = path(
        np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 0.0], [0.0, 1.0]]),
        y,
        pp,
        indices,
        1,
        (0, 4, 8),
    )
    fitted = pp["fit_intercept"]
    assert not ss[0].any() and ss[1:, fitted].all() and np.isnan(cc[1:, fitted]).all()
    assert not ss[:, ~fitted].any()
    print(
        "Independent dense/sparse paths, preprocessing, intercepts, unknowns, "
        "failures, and selection: passed"
    )


def expected_selection(validation, rows, query, rare_count):
    objective = 0 if query["objective"] == 1 and rare_count == 0 else query["objective"]
    pool = []
    for i, row in enumerate(rows):
        if row["arm"] != query["arm"] or query["scale"] not in ("all", row["scale"]):
            continue
        m = row["observations"]
        rule = query["rule"]
        if rule == "fixed" and (
            m != query["cap"] or row["batch"] != 16 or row["factor"] != 0.05
        ):
            continue
        if rule == "rate_batch" and m != query["cap"]:
            continue
        if rule.startswith("joint") and m > query["cap"]:
            continue
        score = validation[tuple(row["index"])][objective]
        key = (
            score if np.isfinite(score) else np.inf,
            m,
            row["batch"],
            row["factor"],
            SCALES.index(row["scale"]),
        )
        pool.append((key, i))
    best = sorted(pool)[0]
    if not np.isfinite(best[0][0]):
        zeros = [
            (r["batch"], r["factor"], SCALES.index(r["scale"]), i)
            for i, r in enumerate(rows)
            if r["arm"] == query["arm"]
            and r["observations"] == 0
            and query["scale"] in ("all", r["scale"])
        ]
        return sorted(zeros)[0][-1], True
    return best[1], False


def check_artifacts():
    raw = load_mushroom()
    counts = dict(replications=0, endpoints=0, selections=0)
    maximum_path_error = 0.0
    caches = {}
    for stage, label in enumerate(("synthetic", "mushroom")):
        output = result_dir(label, "rates5")
        manifest = json.loads((output / f"{label}.json").read_text())
        assert manifest["stage"] == stage
        assert manifest["configurations"] == configurations(stage)
        assert len(manifest["queries"]) == (300 if stage == 0 else 180)
        batches = (1, 16) if stage == 0 else (16, 128)
        checkpoints = SYNTHETIC_M if stage == 0 else MUSHROOM_M
        assert manifest["candidates"] == candidates(
            configurations(stage), batches, checkpoints
        )
        assert len(manifest["replications"]) == REPS[stage] * (
            len(LAWS) if stage == 0 else len(SIZES)
        )
        with np.load(output / f"{label}.npz") as archive:
            selected_by_case = {}
            for meta in manifest["replications"]:
                case, rep = meta["case"], meta["rep"]
                prefix = f"c{case}_r{rep}_"
                coefficients, validation, test, selections, status = (
                    archive[prefix + key]
                    for key in (
                        "coefficients",
                        "validation",
                        "test",
                        "selections",
                        "status",
                    )
                )
                assert coefficients.shape == (
                    (2, 4, 75, 3) if stage == 0 else (2, 4, 45, meta["dimension"] + 1)
                )
                assert np.array_equal(np.isnan(coefficients).all(axis=-1), status != 0)
                rows = manifest["candidates"]
                selected_by_case.setdefault(case, []).append(
                    np.array([test[tuple(rows[i]["index"])] for i in selections[:, 0]])
                )
                if stage == 0:
                    parts, population, weights, mu = synthetic_data(case, rep)
                    assert meta["train_rare"] == parts[0][2].sum()
                    assert meta["validation_rare"] == parts[1][2].sum()
                else:
                    parts, details = mushroom_data(raw, case, rep)
                    population, weights, mu = parts[2], None, None
                    assert (
                        details["names"] == meta["names"]
                        and details["unknown"] == meta["unknown"]
                    )
                    train_ids, val_ids, test_ids = (
                        archive[prefix + "partition_" + name]
                        for name in ("train", "validation", "test")
                    )
                    assert np.array_equal(
                        np.sort(np.concatenate((train_ids, val_ids, test_ids))),
                        np.arange(8124),
                    )
                    for actual, expected in zip(
                        (train_ids, val_ids, test_ids),
                        details["partitions"],
                        strict=True,
                    ):
                        assert np.array_equal(actual, expected)
                    assert meta["test_rare"] == population[2].sum()
                assert_allclose(
                    validation,
                    independent_loss(*parts[1], coefficients),
                    rtol=2e-10,
                    atol=2e-10,
                )
                assert_allclose(
                    test,
                    independent_loss(*population, coefficients, weights),
                    rtol=2e-10,
                    atol=2e-10,
                )
                for qi, query in enumerate(manifest["queries"]):
                    selected, failed = expected_selection(
                        validation, rows, query, meta["validation_rare"]
                    )
                    assert selected == selections[qi, 0]
                    assert failed == bool(selections[qi, 2])
                    assert bool(selections[qi, 1]) == (
                        query["objective"] == 1 and meta["validation_rare"] == 0
                    )
                    assert rows[selected]["observations"] <= query["cap"]
                if rep == 0:
                    params = prepare(
                        parts[0][0], parts[0][1], configurations(stage), mu
                    )
                    for name, value in params.items():
                        assert_allclose(
                            archive[prefix + "parameter_" + name], value, atol=1e-13
                        )
                    batches = (1, 16) if stage == 0 else (16, 128)
                    checkpoints = SYNTHETIC_M if stage == 0 else MUSHROOM_M
                    for bi, batch in enumerate(batches):
                        expected = reference_path(
                            parts[0][0],
                            parts[0][1],
                            params,
                            archive[prefix + "indices"],
                            batch,
                            checkpoints,
                        )
                        good = status[bi] == 0
                        # Divergent vectors can have tiny coordinates formed by
                        # cancellation. Compare at the scale of the whole vector.
                        scale = 1 + np.max(np.abs(expected[good]), axis=-1)
                        error = (
                            np.max(
                                np.abs(coefficients[bi][good] - expected[good]), axis=-1
                            )
                            / scale
                        )
                        maximum_path_error = max(maximum_path_error, float(error.max()))
                        assert np.all(error < 2e-9)
                counts["replications"] += 1
                counts["endpoints"] += status.size
                counts["selections"] += len(selections)
            caches[label] = (
                manifest,
                {c: np.array(v) for c, v in selected_by_case.items()},
            )
        print(
            f"{label}: complete loss, selection, split, audit passed",
            flush=True,
        )
    print(counts)
    print(f"Maximum independent path normwise error: {maximum_path_error:.3g}")
    check_summary(caches)
    precision = json.loads(
        (result_dir("synthetic", "rates5") / "precision-audit.json").read_text()
    )
    assert {(r["case"], r["scale"]) for r in precision["records"]} == {
        (i, s) for i in range(8) for s in ("none", "sd", "damped")
    }
    assert len(precision["records"]) == 24


def check_summary(caches):
    for label, (manifest, values) in caches.items():
        summary = json.loads((result_dir(label, "rates5") / "summary.json").read_text())
        for group in ("selections", "contrasts"):
            for row in summary[group]:
                metas = [
                    m for m in manifest["replications"] if m["case"] == row["case"]
                ]
                stratum = row["stratum"]
                mask = np.array(
                    [
                        stratum == "all"
                        or (stratum == "train_absent" and m["train_rare"] == 0)
                        or (stratum == "train_present" and m["train_rare"] > 0)
                        or (
                            stratum == "validation_absent" and m["validation_rare"] == 0
                        )
                        or (
                            stratum == "validation_present" and m["validation_rare"] > 0
                        )
                        for m in metas
                    ]
                )
                sample = values[row["case"]][:, row["query"]].copy()
                if group == "contrasts":
                    sample -= values[row["case"]][:, row["reference"]]
                sample = sample[mask]
                for objective, name in enumerate(("aggregate", "rare")):
                    x = sample[:, objective].astype(np.longdouble)
                    x = x[np.isfinite(x)]
                    expected = row[name]
                    assert expected["n"] == len(x)
                    assert expected["missing"] == len(sample) - len(x)
                    if len(x):
                        mean = x.sum() / len(x)
                        assert_allclose(
                            expected["mean"], float(mean), rtol=1e-12, atol=1e-13
                        )
                        for key, value in (
                            ("median", np.median(x)),
                            ("p95", np.quantile(x, 0.95)),
                            ("maximum", x.max()),
                        ):
                            assert_allclose(
                                expected[key], float(value), rtol=1e-12, atol=1e-13
                            )
                    else:
                        assert expected["mean"] is None
                    if len(x) > 1:
                        se = np.sqrt(np.sum((x - mean) ** 2) / (len(x) * (len(x) - 1)))
                        assert_allclose(
                            expected["mcse"], float(se), rtol=1e-12, atol=1e-13
                        )
                    else:
                        assert expected["mcse"] is None
    print(
        "Every selected-loss mean, absence stratum, paired contrast, and MCSE: passed"
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
