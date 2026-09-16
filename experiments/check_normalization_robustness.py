"""Independent numerical and artifact checks for the robustness experiment."""

import argparse
import itertools
import json

import numpy as np
from check_joint_interactions import enumerate_paths
from robustness_spec import (
    ATOL,
    BATCHES,
    HC,
    HF,
    KC,
    KF,
    LC,
    MC,
    MF,
    OUTPUT,
    QC,
    ROOT,
    RTOL,
    grid,
    laws,
    model,
    preserved,
    sha256,
)
from run_normalization_robustness import boundary, moment_path, parameters


def close(actual, expected):
    np.testing.assert_allclose(actual, expected, atol=ATOL, rtol=RTOL)
    return float(np.max(np.abs(actual - expected)))


def one_at_a_time(m, scales, step, batch, counts, signal, sigma2):
    """Form original-coordinate batch updates directly from the four cells."""
    d = step / scales**2
    updates = np.eye(2) - d[None, :, None] * m["x"][:, :, None] * m["x"][:, None, :]
    mean_update = np.einsum("c,cij->ij", m["probabilities"], updates)
    injection = sigma2 / batch * d[:, None] * m["gram"] * d[None, :]
    mean = -np.array(signal, dtype=float)
    homogeneous = np.outer(mean, mean)
    noise = np.zeros((2, 2))
    saved = []

    def propagate(v):
        independent = mean_update @ v @ mean_update.T
        single = np.einsum("c,cij,jk,clk->il", m["probabilities"], updates, v, updates)
        return (1 - 1 / batch) * independent + single / batch

    for k in range(max(counts) + 1):
        if k in counts:
            saved.append(
                dict(
                    bias=mean.copy(),
                    second=homogeneous + noise,
                    design=homogeneous - np.outer(mean, mean),
                    noise=noise.copy(),
                )
            )
        if k < max(counts):
            mean = mean_update @ mean
            homogeneous = propagate(homogeneous)
            noise = propagate(noise) + injection
    return {key: np.array([p[key] for p in saved]) for key in saved[0]}


def check_numerics():
    law_list = laws()
    assert len(law_list) == 228 and sum(law["refined"] for law in law_list) == 16
    assert (len(HC), len(HF), len(KF), len(MF)) == (35, 68, 269, 89)
    for coarse, fine in ((HC, HF), (KC, KF), (MC, MF)):
        assert set(coarse) <= set(fine)
    configurations = endpoints = 0
    for law in law_list:
        for batch in BATCHES:
            rates, counts, labels = grid(law, batch)
            configurations += 2 * len(rates)
            endpoints += 2 * len(rates) * len(counts)
            assert np.all(labels > 0)
            assert set(MC // batch) <= set(counts)
            assert not np.any(MF % batch)
    assert configurations == 51048 and endpoints == 2571800
    largest = 0.0
    for q, ell in itertools.product(QC, LC):
        m = model(q, ell)
        p, x = m["probabilities"], m["x"]
        assert min(p) >= 0 and abs(sum(p) - 1) < 1e-15
        close(p @ x, np.zeros(2))
        close(m["gram"], [[0.25, q * ell / 2], [q * ell / 2, q * (1 - q)]])
        close(
            m["rare_second"],
            [[0.25, ell * (1 - q) / 2], [ell * (1 - q) / 2, (1 - q) ** 2]],
        )
        assert np.linalg.eigvalsh(m["gram"])[0] > 0
        for scaling, batch in itertools.product(("U", "S"), BATCHES):
            scales, _ = parameters(m, scaling, 1)
            boundary(m, scales, batch)
    cases = 0
    for ell, scaling, batch, signal, sigma in itertools.product(
        (-1, 0, 1), ("U", "S"), (1, 2), ((0.8, -1.1), (2, 1)), (0, 1.3)
    ):
        m = model(0.02, ell)
        scales, step = parameters(m, scaling, 0.01)
        counts = [0, 1, 2]
        actual = moment_path(m, scales, step, batch, counts, signal, sigma**2)
        mean, second = enumerate_paths(
            m, scales, step, batch, np.array(signal), sigma, 2
        )
        _, noiseless = enumerate_paths(m, scales, step, batch, np.array(signal), 0, 2)
        for field, target in dict(
            bias=mean,
            second=second,
            design=noiseless - np.einsum("ki,kj->kij", mean, mean),
            noise=second - noiseless,
        ).items():
            largest = max(largest, close(actual[field], target))
        for g in (0.1, 10):
            rescaled = moment_path(
                m, scales * g, step * g * g, batch, counts, signal, sigma**2
            )
            for field in ("bias", "second", "design", "noise", "risks", "risk_parts"):
                largest = max(largest, close(rescaled[field], actual[field]))
        assert not np.any(actual["failure"])
        cases += 1
    for ell, signal, sigma2, h in (
        (0, [1, 1], 3, 0.002),
        (1, [2, 1], 4, 0.01),
        (-1, [2, -1], 4, 0.01),
    ):
        for scaling, batch in itertools.product(("U", "S"), (1, 10)):
            m = model(0.02, ell)
            scales, step = parameters(m, scaling, h)
            counts = [0, 1, 100, 1000, 10000]
            actual = moment_path(m, scales, step, batch, counts, signal, sigma2)
            independent = one_at_a_time(m, scales, step, batch, counts, signal, sigma2)
            for field in independent:
                largest = max(largest, close(actual[field], independent[field]))
            if ell == 0:
                rate = [h, 4 * h * 0.02 * 0.98] if scaling == "U" else [h, h]
                close(
                    actual["bias"],
                    -((1 - np.array(rate)) ** np.array(counts)[:, None]) * signal,
                )
    m = model(0.02, 1)
    scales, step = parameters(m, "S", 0)
    zero = moment_path(m, scales, step, 1, [0, 100000], [2, -1], 4)
    close(zero["bias"], [[-2, 1], [-2, 1]])
    assert not np.any(zero["failure"])
    for signal, sigma2 in (([0, 0], 0), ([0, 0], 4), ([1, 1], 0)):
        path = moment_path(m, scales, 0.01, 1, [0, 1, 100], signal, sigma2)
        assert not np.any(path["failure"])
        if sigma2 == 0:
            assert np.all(path["noise"] == 0)
    divergent = moment_path(m, scales, 3, 1, [0, 1, 10000], [1, 1], 3)
    assert list(divergent["failure"][[0, -1]]) == [0, 1]
    exact_zero = moment_path(m, scales, 3, 1, [10000], [0, 0], 0)
    assert not exact_zero["failure"][0] and np.all(exact_zero["second"] == 0)
    for scaling in ("U", "S"):
        scales, step = parameters(m, scaling, 0.01)
        paths = [
            moment_path(m, scales, step, b, [1, 100, 10000], [2, -1], 4)
            for b in BATCHES
        ]
        for left, right in zip(paths[:-1], paths[1:], strict=True):
            close(left["bias"], right["bias"])
            assert np.linalg.eigvalsh(left["second"] - right["second"]).min() >= -ATOL
    preserved()
    result = dict(
        enumerated_cases=cases,
        maximum_absolute_error=largest,
        feature_laws=36,
        boundary_brackets=216,
        configurations=configurations,
        endpoints=endpoints,
    )
    print(json.dumps(result), flush=True)
    return result


def check_mean_control_with_overflow():
    from summarize_normalization_robustness import controls

    m = model(0.002, 0)
    configurations, paths = [], []
    counts = np.array([0, 1000, 10000])
    for scaling in ("U", "S"):
        scales, step = parameters(m, scaling, 0.64)
        for batch in (1, 10, 100):
            configurations.append(
                dict(
                    law=0,
                    scaling=scaling,
                    batch=batch,
                    h=0.64,
                    offset=3 * len(paths),
                    size=3,
                )
            )
            paths.append(moment_path(m, scales, step, batch, counts, [1, 1], 3))
    data = {
        key: np.concatenate([p[key] for p in paths])
        for key in ("bias", "second", "failure")
    }
    data["k"] = np.tile(counts, 6)
    invalid = np.flatnonzero(data["failure"])[0]
    assert np.isfinite(data["bias"][invalid]).all()
    data["bias"][invalid, 0] = 0.125
    spec = dict(
        configurations=configurations, laws=[dict(q=0.002, ell=0, signal=[1, 1])]
    )
    # An overflowed second moment must not hide an incorrect, still-finite mean.
    assert controls(spec, data)["independent_mean_max_tolerance_ratio"] > 1
    print("Mean control detects errors even when second moments overflow.", flush=True)


def check_selection():
    from summarize_normalization_robustness import (
        classification,
        runs,
        select,
        unpack_ranges,
    )

    data = dict(
        configuration=np.arange(5),
        k=np.array([0, 1, 2, 3, 4]),
        M=np.array([0, 10, 20, 30, 40]),
        failure=np.array([0, 0, 0, 1, 0]),
        risks=np.array(
            [[1, 1], [0.2, 0.3], [0.1, 0.4], [np.nan, np.nan], [0.1 + 1e-9, 0.5]]
        ),
    )
    config = dict(
        h=np.array([0, 0.01, 0.02, 0.5, 0.04]),
        batch=np.full(5, 10),
        stability=np.array(["zero", "stable", "unstable", "unstable", "stable"]),
    )
    stable = select(np.arange(5), data, config, 0, "stable", "M")
    assert stable["complete"] and stable["endpoint"] == 4 and stable["eligible"] == 3
    unrestricted = select(np.arange(5), data, config, 0, "unrestricted", "M")
    assert not unrestricted["complete"] and unrestricted["invalid"] == 1
    assert list(unrestricted["ties"]) == [2, 4] and unrestricted["endpoint"] == 2
    assert classification(0.2, 0.1, unrestricted["complete"]) == "incomplete"
    config["stability"][2] = "boundary"
    assert not select(np.arange(5), data, config, 0, "stable", "M")["complete"]
    zero = select([0], data, config, 0, "stable", "M")
    assert zero["endpoint"] == 0 and "zero_predictor" in zero["search_boundary"]
    assert np.array_equal(unpack_ranges(runs([0, 1, 2, 7, 9, 10])), [0, 1, 2, 7, 9, 10])
    print(
        "Oracle eligibility, ties, boundary optima, and incomplete comparisons passed.",
        flush=True,
    )


def check_simulation_updates():
    import simulate_normalization_robustness as sim

    original = sim.PANELS
    sim.PANELS = [(0.02, -1, (2, -1), 4, 0.01, (1, 2, 10))]
    try:
        _, _, actual, masks, failures, controls = sim.simulate_block((0, 0))
        assert not failures and not masks.any()
        assert controls["iterate_tolerance_ratio"] < 1
        assert controls["prediction_tolerance_ratio"] < 1
        m = model(0.02, -1)
        feature_rng, noise_rng = [
            np.random.Generator(
                np.random.PCG64(np.random.SeedSequence([20260916, 0, 0, stream]))
            )
            for stream in (0, 1)
        ]
        indices = np.searchsorted(
            np.cumsum(m["probabilities"]), feature_rng.random((100, 256))
        )
        x = m["x"][indices]
        noise = 2 * noise_rng.standard_normal((100, 256))
        for bi, batch in enumerate((1, 10)):
            for si, scaling in enumerate(("U", "S")):
                scales, step = parameters(m, scaling, 0.01)
                for companion in (0, 1):
                    theta = np.zeros((256, 2))
                    for k in range(1, 11):
                        features = x[(k - 1) * batch : k * batch] / scales
                        y = x[(k - 1) * batch : k * batch] @ [2, -1]
                        if companion == 0:
                            y = y + noise[(k - 1) * batch : k * batch]
                        residual = np.einsum("bri,ri->br", features, theta) - y
                        theta -= step * np.mean(features * residual[:, :, None], axis=0)
                        if k in (1, 2, 10):
                            close(
                                actual[bi, si, (1, 2, 10).index(k), companion],
                                theta / scales,
                            )
        incomplete = sim.sample_summary(
            np.ones((256, 7)), np.ones(7), np.arange(256) == 3
        )
        assert not incomplete["complete"] and list(incomplete["failed_replicates"]) == [
            3
        ]
    finally:
        sim.PANELS = original
    print(
        "Paired updates, stream ordering, rescaling, and failure gate passed.",
        flush=True,
    )


def check_saved_oracles(spec, data, summary):
    """Independently reduce endpoint risks by exact stop and cumulative minima."""
    from summarize_normalization_robustness import unpack_ranges

    cs = spec["configurations"]
    meta = {
        key: np.array([c[key] for c in cs])
        for key in ("law", "scaling", "batch", "h", "stability", "coarse_rate")
    }
    tables = {}
    fields = summary["envelopes"]["fields"]
    groups = summary["envelopes"]["ties_inclusive_ranges"]
    checked_ties = set()
    count = 0
    for row in summary["envelopes"]["rows"]:
        rec = dict(zip(fields, row, strict=True))
        objective = 0 if rec["objective"] == "aggregate" else 1
        for scaling in ("U", "S"):
            key = tuple(
                rec[k]
                for k in (
                    "law",
                    "rate_grid",
                    "stop_grid",
                    "budget",
                    "batch",
                    "eligibility",
                    "objective",
                )
            ) + (scaling,)
            if key not in tables:
                fine = rec["stop_grid"] == "fine"
                caps = (
                    (KF if fine else KC)
                    if rec["budget"] == "updates"
                    else (MF if fine else MC)
                )
                variable = "k" if rec["budget"] == "updates" else "M"
                mask = (meta["law"] == rec["law"]) & (meta["scaling"] == scaling)
                if rec["batch"]:
                    mask &= meta["batch"] == rec["batch"]
                if rec["rate_grid"] == "coarse":
                    mask &= meta["coarse_rate"]
                ids = np.concatenate(
                    [
                        np.arange(cs[c]["offset"], cs[c]["offset"] + cs[c]["size"])
                        for c in np.flatnonzero(mask)
                    ]
                )
                ids = ids[np.isin(data[variable][ids], caps)]
                cids = data["configuration"][ids]
                baseline = (data["k"][ids] == 0) | (meta["h"][cids] == 0)
                boundary_mask = (~baseline) & (meta["stability"][cids] == "boundary")
                allowed = np.ones(len(ids), dtype=bool)
                if rec["eligibility"] == "stable":
                    allowed = baseline | (meta["stability"][cids] == "stable")
                else:
                    boundary_mask[:] = False
                positions = np.searchsorted(caps, data[variable][ids])
                eligible = np.bincount(positions[allowed], minlength=len(caps))
                invalid = allowed & (data["failure"][ids] != 0)
                missing = np.bincount(positions[invalid], minlength=len(caps))
                uncertain = np.bincount(positions[boundary_mask], minlength=len(caps))
                valid = allowed & ~invalid
                minimum = np.full(len(caps), np.inf)
                np.minimum.at(
                    minimum, positions[valid], data["risks"][ids[valid], objective]
                )
                tables[key] = dict(
                    caps=caps,
                    variable=variable,
                    ids=ids[valid],
                    rate=(minimum, eligible, missing, uncertain),
                    rate_stop=(
                        np.minimum.accumulate(minimum),
                        np.cumsum(eligible),
                        np.cumsum(missing),
                        np.cumsum(uncertain),
                    ),
                )
            table = tables[key]
            j = np.searchsorted(table["caps"], rec["cap"])
            expected = [values[j] for values in table[rec["adjustment"]]]
            assert rec[f"{scaling}_minimum"] == expected[0]
            for suffix, value in zip(
                ("eligible", "invalid", "boundary"), expected[1:], strict=True
            ):
                assert rec[f"{scaling}_{suffix}"] == value
            chosen = rec[f"{scaling}_endpoint"]
            cid = data["configuration"][chosen]
            assert meta["scaling"][cid] == scaling and meta["law"][cid] == rec["law"]
            value = data["risks"][chosen, objective]
            assert abs(value - expected[0]) <= 1e-8 * max(
                1, abs(value), abs(expected[0])
            )
            consumed = data[table["variable"]][chosen]
            assert (
                consumed == rec["cap"]
                if rec["adjustment"] == "rate"
                else consumed <= rec["cap"]
            )
            if rec["batch"]:
                assert meta["batch"][cid] == rec["batch"]
            if rec["rate_grid"] == "coarse":
                assert meta["coarse_rate"][cid]
            tie_id = rec[f"{scaling}_ties"]
            tie_key = (key, rec["adjustment"], rec["cap"], tie_id)
            # A deterministic subset checks exhaustive ties and their display order.
            if count % 997 == 0 and tie_key not in checked_ties:
                ids = table["ids"]
                admissible = (
                    data[table["variable"]][ids] == rec["cap"]
                    if rec["adjustment"] == "rate"
                    else data[table["variable"]][ids] <= rec["cap"]
                )
                ids = ids[admissible]
                values = data["risks"][ids, objective]
                tied = ids[
                    np.abs(values - expected[0])
                    <= 1e-8 * np.maximum(1, np.maximum(abs(values), abs(expected[0])))
                ]
                assert np.array_equal(np.sort(tied), unpack_ranges(groups[tie_id]))
                display = min(
                    tied,
                    key=lambda i: (
                        data["M"][i],
                        meta["h"][data["configuration"][i]],
                        meta["batch"][data["configuration"][i]],
                        i,
                    ),
                )
                assert display == chosen
                checked_ties.add(tie_key)
        incomplete = any(
            rec[f"{scaling}_{suffix}"]
            for scaling in ("U", "S")
            for suffix in ("invalid", "boundary")
        )
        gap = rec["S_minimum"] - rec["U_minimum"]
        tolerance = 1e-8 * max(1, abs(rec["U_minimum"]), abs(rec["S_minimum"]))
        sign = (
            "incomplete"
            if incomplete
            else "positive"
            if gap > tolerance
            else "negative"
            if gap < -tolerance
            else "unresolved"
        )
        assert rec["sign"] == sign and rec["gap"] == gap
        np.testing.assert_array_equal(
            data["risks"][rec["S_endpoint"]] - data["risks"][rec["U_endpoint"]],
            [rec["selected_pair_aggregate_gap"], rec["selected_pair_rare_gap"]],
        )
        count += 1
    expected_count = 0
    for law in spec["laws"]:
        resolutions = (
            [(KC, MC)]
            if not law["refined"]
            else [(KC, MC), (KC, MC), (KF, MF), (KF, MF)]
        )
        expected_count += sum(8 * (3 * len(k) + 4 * len(m)) for k, m in resolutions)
    assert count == expected_count
    assert summary["counts"]["envelope_comparisons"] == count
    print(
        f"Checked all {count} oracle minima, budgets, eligibility counts, and signs; "
        f"{len(checked_ties)} exhaustive tie checks.",
        flush=True,
    )


def check_saved_results(output, spec, data):
    from simulate_normalization_robustness import summarize
    from summarize_normalization_robustness import unpack_ranges

    summary = json.loads((output / "summary.json").read_text())
    assert summary["specification_sha256"] == sha256(output / "specification.json")
    assert summary["paths_sha256"] == sha256(output / "paths.npz")
    assert summary["simulation_sha256"] == sha256(output / "paired-simulation.npz")
    for code, intervals in summary["failures"]["endpoint_ranges"].items():
        assert np.array_equal(
            unpack_ranges(intervals), np.flatnonzero(data["failure"] == int(code))
        )
    assert sum(summary["failures"]["counts"].values()) == len(data["k"])
    assert summary["boundary_probes_sha256"] == sha256(output / "boundary-probes.json")
    assert summary["simulation_summary_sha256"] == sha256(
        output / "simulation-summary.json"
    )
    for records in summary["counts_by_dimension"].values():
        assert sum(row["endpoints"] for row in records) == 2571800
        assert sum(row["invalid"] for row in records) == np.count_nonzero(
            data["failure"]
        )
    valid = data["failure"] == 0
    np.testing.assert_allclose(
        data["second"][valid],
        np.einsum("ki,kj->kij", data["bias"][valid], data["bias"][valid])
        + data["design"][valid]
        + data["noise"][valid],
        atol=ATOL,
        rtol=RTOL,
    )
    for law in spec["laws"]:
        selected = np.flatnonzero(
            np.array([c["law"] for c in spec["configurations"]]) == law["id"]
        )
        ids = np.concatenate(
            [
                np.arange(
                    spec["configurations"][c]["offset"],
                    spec["configurations"][c]["offset"]
                    + spec["configurations"][c]["size"],
                )
                for c in selected
            ]
        )
        ids = ids[valid[ids]]
        close(data["mean"][ids], data["bias"][ids] + law["signal"])
        for objective, weight in enumerate((law["gram"], law["rare_second"])):
            expected = np.einsum("kij,ij->k", data["second"][ids], weight) / 2
            close(data["risks"][ids, objective], expected)
    for record in summary["fixed"]["rows"]:
        rec = dict(zip(summary["fixed"]["fields"], record, strict=True))
        if rec["valid"]:
            close(
                data["risks"][rec["S_endpoint"]] - data["risks"][rec["U_endpoint"]],
                [rec["aggregate_gap"], rec["rare_gap"]],
            )
    check_saved_oracles(spec, data, summary)
    with np.load(output / "paired-simulation.npz", allow_pickle=False) as saved:
        assert saved["error"].shape == (6, 2, 2, 3, 8192, 2)
        assert np.array_equal(saved["replicate_id"], np.arange(8192))
        assert np.array_equal(saved["block_id"], np.arange(8192) // 256)
        actual = summarize(saved["error"], saved["noiseless_error"], saved["failed"])
        for key in ("endpoints", "contrasts"):
            for left, right in zip(
                actual[key], summary["simulation"][key], strict=True
            ):
                assert left["complete"] == right["complete"]
                if left["complete"]:
                    for field in ("mean", "mcse", "exact", "residual"):
                        close(np.asarray(left[field]), np.asarray(right[field]))
                    if key == "endpoints":
                        for field in ("mean", "mcse", "exact", "residual"):
                            close(
                                np.asarray(left["covariance_diagnostics"][field]),
                                np.asarray(right["covariance_diagnostics"][field]),
                            )
    assert not summary["simulation"]["failures"]
    assert summary["simulation"]["diagnostic_gate_failures"] == [[29, "covariance"]]
    investigation = summary["simulation"]["diagnostic_investigations"][0]
    assert investigation["observed_absent_replicates"] == 0
    m = model(0.002, 0)
    scales, step = parameters(m, "S", 0.002)
    conditional = dict(m, probabilities=np.array([0.5, 0, 0.5, 0]))
    conditional["gram"] = m["x"].T @ (conditional["probabilities"][:, None] * m["x"])
    independent = one_at_a_time(conditional, scales, step, 1, [10000], [1, 1], 0)
    close(independent["second"][0], np.asarray(investigation["conditional_second"]))
    assert 0.79 < investigation["fraction_from_absence"] < 0.81
    for record in summary["simulation"]["global_rescaling"]:
        assert (
            record["iterate_tolerance_ratio"] < 1
            and record["prediction_tolerance_ratio"] < 1
        )
    assert summary["controls"]["independent_mean_max_tolerance_ratio"] < 1
    assert summary["controls"]["independent_mean_compared_endpoints"] == sum(
        c["size"] for c in spec["configurations"] if spec["laws"][c["law"]]["ell"] == 0
    )
    for record in summary["controls"]["global_rescaling_moments"]:
        assert max(record["residual"].values()) <= ATOL
    assert summary["controls"]["batch_order_minimum_relative_eigenvalue"] >= -RTOL
    figures = json.loads((output / "figures.json").read_text())
    assert figures["summary_sha256"] == sha256(output / "summary.json")
    assert len(figures["sha256"]) == 12
    for path, digest in figures["sha256"].items():
        assert sha256(output / path) == digest
    print(
        "Saved moments, risks, failures, paired uncertainty, controls, "
        "and figure hashes passed.",
        flush=True,
    )


def check_artifacts(output):
    spec = json.loads((output / "specification.json").read_text())
    for path, digest in spec["sha256"].items():
        assert sha256(ROOT / path) == digest, f"Stale source: {path}"
    assert preserved() == spec["preserved_sha256"]
    assert sha256(output / "paths.npz") == spec["paths_sha256"]
    with np.load(output / "paths.npz", allow_pickle=False) as archive:
        data = {key: archive[key] for key in archive.files}
        assert len(data["k"]) == 2571800
        assert len(spec["configurations"]) == 51048
        for c in spec["configurations"]:
            sl = slice(c["offset"], c["offset"] + c["size"])
            law = spec["laws"][c["law"]]
            _, counts, labels = grid(law, c["batch"])
            assert np.array_equal(data["k"][sl], counts)
            assert np.array_equal(data["M"][sl], counts * c["batch"])
            assert np.all(data["configuration"][sl] == c["id"])
            assert np.array_equal(data["grid_labels"][sl], labels)
        print("Artifact grid, hashes, and preservation checks passed.", flush=True)
        check_saved_results(output, spec, data)


if __name__ == "__main__":
    assert __debug__, "Run ordinary Python without -O."
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--numerics-only", action="store_true")
    args = parser.parse_args()
    check_numerics()
    check_simulation_updates()
    check_selection()
    check_mean_control_with_overflow()
    if not args.numerics_only:
        check_artifacts(OUTPUT)
