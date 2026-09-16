"""Fixed-data SGD with algebraic centering and validation-only selection."""

import numpy as np
from practical_spec import SCALES
from scipy import sparse


def prepare(x, y, configurations, population_mean=None):
    n, d = x.shape
    mean = np.asarray(x.mean(axis=0)).ravel()
    raw_gram = x.T @ x / n
    if sparse.issparse(raw_gram):
        raw_gram = raw_gram.toarray()
    variance = np.maximum(0, np.diag(raw_gram) - mean**2)
    params = {
        name: []
        for name in (
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
    for config in configurations:
        arm, scale = config["arm"], config["scale"]
        key = (arm, scale)
        if key not in cache:
            known = arm == "known"
            oracle_intercept = arm in ("known", "estimated_scale")
            mu = (
                population_mean
                if oracle_intercept
                else (np.zeros(d) if arm == "uncentered_fitted" else mean)
            )
            v = population_mean * (1 - population_mean) if known else variance
            active = np.ones(d, dtype=bool) if known else variance > 1e-14
            divisor = (
                np.ones(d)
                if scale == "none"
                else np.sqrt(v + (0.01 if scale == "damped" else 0))
            )
            divisor = np.where(active, divisor, 1)
            inv = active / divisor
            gram = raw_gram - np.outer(mean, mu) - np.outer(mu, mean) + np.outer(mu, mu)
            gram = gram * np.outer(inv, inv)
            fitted = arm.endswith("fitted")
            if fitted:
                cross = (mean - mu) * inv
                gram = np.block(
                    [[gram, cross[:, None]], [cross[None, :], np.ones((1, 1))]]
                )
            curvature = max(float(np.linalg.eigvalsh(gram)[-1]), 1e-12)
            cache[key] = (
                mu,
                divisor,
                active,
                0.0 if oracle_intercept else float(y.mean()),
                fitted,
                curvature,
            )
        values = (*cache[key], config["factor"] / cache[key][-1])
        for name, value in zip(params, values, strict=True):
            params[name].append(value)
    return {key: np.asarray(value) for key, value in params.items()}


def path(x, y, params, indices, batch, checkpoints):
    """Return original-scale coefficients and raw intercepts at every checkpoint."""
    c, d = params["mu"].shape
    beta = np.zeros((c, d))
    intercept = params["initial"].copy()
    step = params["eta"][:, None] * params["active"] / params["divisor"] ** 2
    failed = np.zeros(c, dtype=np.uint8)
    coefs, statuses = [], []
    save = set(checkpoints)

    def record():
        raw_intercept = intercept - np.sum(params["mu"] * beta, axis=1)
        values = np.column_stack((raw_intercept, beta))
        values[failed != 0] = np.nan
        coefs.append(values)
        statuses.append(failed.copy())

    record()
    for processed in range(batch, max(checkpoints) + 1, batch):
        ids = indices[processed - batch : processed]
        xb = x[ids]
        raw_intercept = intercept - np.sum(params["mu"] * beta, axis=1)
        with np.errstate(over="ignore", invalid="ignore"):
            residual = xb @ beta.T + raw_intercept - y[ids, None]
            average = residual.mean(axis=0)
            gradient = (xb.T @ residual).T / batch - params["mu"] * average[:, None]
            beta -= step * gradient
            intercept -= params["eta"] * params["fit_intercept"] * average
        bad = (
            ~np.isfinite(beta).all(axis=1)
            | ~np.isfinite(intercept)
            | (np.max(np.abs(beta), axis=1) > 1e100)
            | (np.abs(intercept) > 1e100)
        )
        failed[(failed == 0) & bad] = 1
        # Zeroing dead paths prevents their arithmetic from contaminating live columns.
        beta[failed != 0] = 0
        intercept[failed != 0] = 0
        if processed in save:
            record()
    return np.array(coefs), np.array(statuses)


def losses(x, y, rare, coefficients, weights=None):
    shape = coefficients.shape[:-1]
    flat = coefficients.reshape(-1, coefficients.shape[-1])
    prediction = x @ flat[:, 1:].T + flat[:, 0]
    with np.errstate(over="ignore", invalid="ignore"):
        errors = 0.5 * (prediction - y[:, None]) ** 2
    w = np.ones(len(y)) / len(y) if weights is None else weights
    aggregate = w @ errors
    wr = w * rare
    subgroup = wr @ errors / wr.sum() if wr.sum() > 0 else np.full(len(flat), np.nan)
    return np.stack((aggregate, subgroup), axis=-1).reshape(*shape, 2)


def candidates(configs, batches, checkpoints):
    return [
        dict(
            **config,
            batch=batch,
            observations=m,
            updates=m // batch,
            index=[bi, mi, ci],
        )
        for bi, batch in enumerate(batches)
        for mi, m in enumerate(checkpoints)
        for ci, config in enumerate(configs)
    ]


def choose(validation, rows, arm, scale, cap, objective, rule, validation_rare_count):
    """Select using validation only; callers cannot pass test scores."""
    effective = 0 if objective == 1 and validation_rare_count == 0 else objective
    eligible = []
    for row_id, row in enumerate(rows):
        if row["arm"] != arm or (scale != "all" and row["scale"] != scale):
            continue
        if rule == "fixed":
            valid = (
                row["observations"] == cap
                and row["batch"] == 16
                and row["factor"] == 0.05
            )
        elif rule == "rate_batch":
            valid = row["observations"] == cap
        else:
            valid = row["observations"] <= cap
        if valid:
            eligible.append(row_id)
    assert eligible

    def order(i):
        row = rows[i]
        score = validation[tuple(row["index"])][effective]
        return (
            float(score) if np.isfinite(score) else np.inf,
            row["observations"],
            row["batch"],
            row["factor"],
            SCALES.index(row["scale"]),
        )

    selected = min(eligible, key=order)
    all_failed = not np.isfinite(order(selected)[0])
    if all_failed:
        initial = [
            i
            for i, row in enumerate(rows)
            if row["arm"] == arm
            and row["observations"] == 0
            and (scale == "all" or row["scale"] == scale)
        ]
        selected = min(initial, key=order)
        assert np.isfinite(order(selected)[0])
    return selected, effective != objective, all_failed, eligible
