"""Paired SGD paths and exact test risks for the controlled bridge study."""

import numpy as np

from experiments.theory_bridge import config as cfg

CELLS = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])


def sample(q_id, stage, first, count):
    q = cfg.PREVALENCES[q_id]
    maximum = int(cfg.budgets(q)[-1])
    length = max(cfg.TRAIN_SIZE, maximum)
    rows = []
    for rep in range(first, first + count):
        generators = [
            np.random.default_rng(
                np.random.SeedSequence([cfg.SEED, q_id, stage, rep, s])
            )
            for s in range(3)
        ]
        train, replacement, validation = generators
        cells = 2 * train.binomial(1, 0.5, length) + train.binomial(1, q, length)
        row = {
            "cells": cells.astype(np.uint8),
            "noise": train.normal(size=length),
            "indices": replacement.integers(
                cfg.TRAIN_SIZE, size=maximum, dtype=np.uint16
            ),
        }
        if stage == 1:
            n = max(cfg.VALIDATION_SIZES)
            row["validation_cells"] = (
                2 * validation.binomial(1, 0.5, n) + validation.binomial(1, q, n)
            ).astype(np.uint8)
            row["validation_noise"] = validation.normal(size=n)
        rows.append(row)
    return {key: np.stack([row[key] for row in rows]) for key in rows[0]}


def parameters(data, q, factors):
    n = len(data["cells"])
    pool = CELLS[data["cells"][:, : cfg.TRAIN_SIZE]]
    population = np.array([0.5, q])
    empirical = pool.mean(axis=1)
    mean = np.broadcast_to(population, (n, len(cfg.ARMS), 2)).copy()
    mean[:, cfg.ESTIMATE_CENTER] = empirical[:, None, :]
    variance = np.broadcast_to(population * (1 - population), mean.shape).copy()
    variance[:, cfg.ESTIMATE_SCALE] = (empirical * (1 - empirical))[:, None, :]
    divisor = np.ones((n, len(cfg.ARMS), 2, 2))
    divisor[:, :, 1] = np.where(variance > 0, np.sqrt(variance), 1)
    transformed = (CELLS[None, None, None] - mean[:, :, None, None]) / divisor[
        :, :, :, None
    ]
    curvature = np.max(np.sum(transformed**2, axis=-1), axis=-1)
    curvature += cfg.FIT_INTERCEPT[None, :, None]
    eta = factors[None, None, None] / curvature[..., None]
    initial = np.zeros((n, len(cfg.ARMS), len(cfg.SIGNALS)))
    response_mean = (empirical - population) @ cfg.SIGNALS.T
    response_mean += data["noise"][:, : cfg.TRAIN_SIZE].mean(axis=1)[:, None]
    initial[:, cfg.INITIALIZE_MEAN] = response_mean[:, None]
    return dict(mean=mean, divisor=divisor, eta=eta, initial=initial)


def validation_moments(data, q):
    """Preserve the exact validation quadratic while avoiding repeated prediction."""
    result = []
    for n in cfg.VALIDATION_SIZES:
        cells = data["validation_cells"][:, :n]
        x = CELLS[cells] - [0.5, q]
        design = np.concatenate((np.ones((*x.shape[:2], 1)), x), axis=-1)
        noise = data["validation_noise"][:, :n]
        rare = cells % 2 == 1
        counts = rare.sum(axis=1)
        weights = np.where(counts[:, None] > 0, rare, np.ones_like(rare))
        weights = weights / weights.sum(axis=1, keepdims=True)
        gram = np.einsum("ri,rij,rik->rjk", weights, design, design)
        linear = np.einsum("ri,rij,ri->rj", weights, design, noise)
        constant = 0.5 * np.sum(weights * noise**2, axis=1)
        result.append((gram, linear, constant, counts))
    return result


def error_coordinates(common, rare, intercept, mean, q):
    offset = intercept + (0.5 - mean[:, :, 0, None, None, None]) * common
    offset += (q - mean[:, :, 1, None, None, None]) * rare
    return (
        offset,
        common - cfg.SIGNALS[None, None, None, :, None, 0],
        rare - cfg.SIGNALS[None, None, None, :, None, 1],
    )


def risks(errors, q):
    offset, common, rare = errors
    aggregate = 0.5 * (offset**2 + 0.25 * common**2 + q * (1 - q) * rare**2)
    subgroup = 0.5 * (0.25 * common**2 + (offset + (1 - q) * rare) ** 2)
    return np.stack((aggregate, subgroup), axis=-1)


def predictor_risks(coefficients, q, signals=None):
    """Evaluate saved raw predictors, with signal and policy as the final axes."""
    signals = cfg.SIGNALS if signals is None else np.asarray(signals)
    signal_shape = (1,) * (coefficients.ndim - 3) + (len(signals), 1)
    offset = coefficients[..., 0] + 0.5 * coefficients[..., 1]
    offset += q * coefficients[..., 2]
    common = coefficients[..., 1] - signals[:, 0].reshape(signal_shape)
    rare = coefficients[..., 2] - signals[:, 1].reshape(signal_shape)
    return risks((offset, common, rare), q)


def validation_scores(errors, moments):
    gram, linear, constant, _ = moments
    expand = (slice(None), None, None, None, None)
    score = np.broadcast_to(constant[expand], errors[0].shape).copy()
    for j in range(3):
        score += 0.5 * gram[:, j, j][expand] * errors[j] ** 2
        score -= linear[:, j][expand] * errors[j]
        for k in range(j):
            score += gram[:, j, k][expand] * errors[j] * errors[k]
    return score


def exact_baseline(q, factors, checkpoints):
    """Propagate the independent diagonal moments under population preprocessing."""
    b = q * (1 - q)
    eta = np.stack((factors / (0.25 + (1 - q) ** 2), q * factors))
    dc = eta * np.array([1.0, 4.0])[:, None]
    dr = eta * np.array([1.0, 1 / b])[:, None]
    cc = (1 - dc / 4) ** 2
    cr = dc**2 * b / 4
    rc = dr**2 * b / 4
    rr = (1 - dr * b) ** 2 + dr**2 * b * (1 - 4 * b)
    common = np.broadcast_to(cfg.SIGNALS[None, :, 0, None] ** 2, (2, 2, len(factors)))
    rare = np.broadcast_to(cfg.SIGNALS[None, :, 1, None] ** 2, common.shape)
    saved = []
    wanted = set(checkpoints)
    for stop in range(int(max(checkpoints)) + 1):
        if stop in wanted:
            saved.append(
                np.stack(
                    (common / 8 + b * rare / 2, common / 8 + (1 - q) ** 2 * rare / 2),
                    axis=-1,
                )
            )
        common, rare = (
            cc[:, None] * common + cr[:, None] * rare + dc[:, None] ** 2 / 4,
            rc[:, None] * common + rr[:, None] * rare + dr[:, None] ** 2 * b,
        )
    return np.array(saved)


def choose_fixed(profile, q, coarse=False, *, checkpoints=None, caps=None):
    checkpoints = cfg.stops(q) if checkpoints is None else np.asarray(checkpoints)
    caps = cfg.budgets(q) if caps is None else np.asarray(caps)
    rate_count = profile.shape[-2]
    results = []
    for cap in caps:
        eligible_stops = checkpoints <= cap
        eligible_rates = np.ones(rate_count, dtype=bool)
        if coarse:
            coarse_stops = np.arange(len(checkpoints)) % 2 == 0
            coarse_stops |= np.isin(checkpoints, np.r_[0, caps])
            eligible_stops &= coarse_stops
            eligible_rates[2::2] = False
        eligible = eligible_stops[:, None, None, None, None] & eligible_rates
        risk = np.where(eligible, profile[..., 1], np.inf)
        order = risk.transpose(1, 2, 3, 0, 4).reshape(*risk.shape[1:4], -1).argmin(-1)
        results.append(np.stack((order // rate_count, order % rate_count), axis=-1))
    return np.array(results)


def simulate(data, q, fixed=None):
    """Train paired candidates; selection policies share every candidate path."""
    factors, checkpoints, caps = cfg.rates(), cfg.stops(q), cfg.budgets(q)
    params = parameters(data, q, factors)
    n, arms, scalings = params["eta"].shape[:3]
    shape = (n, arms, scalings, len(cfg.SIGNALS), len(factors))
    common = np.zeros(shape)
    rare = np.zeros(shape)
    intercept = np.broadcast_to(params["initial"][:, :, None, :, None], shape).copy()
    eta = params["eta"][:, :, :, None]
    step_c = eta / params["divisor"][:, :, :, None, 0, None] ** 2
    step_r = eta / params["divisor"][:, :, :, None, 1, None] ** 2
    step_i = eta * cfg.FIT_INTERCEPT[None, :, None, None, None]
    failures = np.zeros(shape, dtype=np.uint16)
    sums = np.empty((len(checkpoints), arms, scalings, 2, len(factors), 2))
    selected = np.zeros((n, len(caps), arms, scalings, 2, len(cfg.POLICIES), 2), int)
    coefficients = np.zeros((*selected.shape[:-1], 3))
    moments = validation_moments(data, q) if fixed is not None else []
    best_score = np.full((*shape[:-1], 1 + len(moments)), np.inf)
    best_indices = np.zeros((*best_score.shape, 2), int)
    best_coefficients = np.zeros((*best_score.shape, 3))
    check_index = 0
    rep = np.arange(n)

    def pick(values, index):
        return np.take_along_axis(values, index[..., None], axis=-1)[..., 0]

    with np.errstate(over="ignore", invalid="ignore"):
        for stop in range(int(caps[-1]) + 1):
            if stop == checkpoints[check_index]:
                bad = ~np.isfinite(common + rare + intercept)
                bad |= (
                    np.maximum.reduce((abs(common), abs(rare), abs(intercept))) > 1e100
                )
                failures[(failures == 0) & bad] = stop
                errors = error_coordinates(common, rare, intercept, params["mean"], q)
                risk = risks(errors, q)
                risk[failures > 0] = np.inf
                sums[check_index] = risk.sum(axis=0)
                raw_intercept = (
                    intercept - params["mean"][:, :, 0, None, None, None] * common
                )
                raw_intercept -= params["mean"][:, :, 1, None, None, None] * rare
                values = (raw_intercept, common, rare)
                if fixed is not None:
                    for cap_id in range(len(caps)):
                        for policy in range(2):
                            choice = fixed[cap_id, :, :, :, policy]
                            use = choice[..., 0] == check_index
                            index = np.broadcast_to(choice[None, ..., 1], shape[:-1])
                            for j, value in enumerate(values):
                                target = coefficients[:, cap_id, :, :, :, policy, j]
                                target[:] = np.where(
                                    use[None], pick(value, index), target
                                )
                            selected[:, cap_id, :, :, :, policy] = choice
                    criteria = [risk[..., 1]] + [
                        validation_scores(errors, m) for m in moments
                    ]
                    for policy, score in enumerate(criteria):
                        score = np.where(failures > 0, np.inf, score)
                        index = score.argmin(axis=-1)
                        candidate = pick(score, index)
                        improved = candidate < best_score[..., policy]
                        best_score[..., policy] = np.minimum(
                            candidate, best_score[..., policy]
                        )
                        best_indices[..., policy, 0][improved] = check_index
                        best_indices[..., policy, 1][improved] = index[improved]
                        for j, value in enumerate(values):
                            best_coefficients[..., policy, j][improved] = pick(
                                value, index
                            )[improved]
                    if stop in caps:
                        cap_id = int(np.flatnonzero(caps == stop)[0])
                        coefficients[:, cap_id, :, :, :, 2:] = best_coefficients
                        selected[:, cap_id, :, :, :, 2:] = best_indices
                check_index += 1
                if check_index == len(checkpoints):
                    break
            fresh = data["cells"][:, stop]
            reused = data["cells"][rep, data["indices"][:, stop]]
            cells = np.where(cfg.REUSE[None], reused[:, None], fresh[:, None])
            noise = np.where(
                cfg.REUSE[None],
                data["noise"][rep, data["indices"][:, stop]][:, None],
                data["noise"][:, stop, None],
            )
            x = CELLS[cells]
            y = (x - [0.5, q]) @ cfg.SIGNALS.T + noise[..., None]
            xc = (x[..., 0] - params["mean"][..., 0])[:, :, None, None, None]
            xr = (x[..., 1] - params["mean"][..., 1])[:, :, None, None, None]
            residual = intercept + common * xc + rare * xr - y[:, :, None, :, None]
            common -= step_c * xc * residual
            rare -= step_r * xr * residual
            intercept -= step_i * residual
    result = dict(sum_risk=sums, failure_checkpoint=failures)
    if fixed is not None:
        result.update(
            coefficients=coefficients,
            selected=selected.astype(np.uint16),
            validation_rare_count=np.stack([m[3] for m in moments], axis=-1),
        )
    return result
