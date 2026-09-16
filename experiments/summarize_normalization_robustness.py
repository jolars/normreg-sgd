"""Fixed contrasts and finite-grid oracle envelopes with explicit incompleteness."""

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
from robustness_spec import KC, KF, MC, MF, OUTPUT, SIGN_TOL, sha256, write_json

ENVELOPE_FIELDS = [
    "law",
    "rate_grid",
    "stop_grid",
    "budget",
    "cap",
    "batch",
    "eligibility",
    "adjustment",
    "objective",
    "U_endpoint",
    "S_endpoint",
    "U_ties",
    "S_ties",
    "U_eligible",
    "S_eligible",
    "U_invalid",
    "S_invalid",
    "U_boundary",
    "S_boundary",
    "U_minimum",
    "S_minimum",
    "gap",
    "sign",
    "relative_to_U",
    "relative_to_initial",
    "selected_pair_aggregate_gap",
    "selected_pair_rare_gap",
    "U_search_boundary",
    "S_search_boundary",
]


def classification(left, right, complete=True):
    if not complete:
        return "incomplete"
    gap = right - left
    tolerance = SIGN_TOL * max(1.0, abs(left), abs(right))
    return (
        "positive"
        if gap > tolerance
        else "negative"
        if gap < -tolerance
        else "unresolved"
    )


def runs(indices):
    """Inclusive ID ranges retain every tied endpoint without repeating baselines."""
    indices = np.sort(np.asarray(indices, dtype=int))
    if not len(indices):
        return []
    breaks = np.flatnonzero(np.diff(indices) != 1) + 1
    chunks = np.split(indices, breaks)
    return [[int(c[0]), int(c[-1])] for c in chunks]


def unpack_ranges(ranges):
    return (
        np.concatenate([np.arange(a, b + 1) for a, b in ranges])
        if ranges
        else np.array([], dtype=int)
    )


def select(ids, data, config, objective, eligibility, maximum_stop):
    ids = np.asarray(ids, dtype=int)
    cids = data["configuration"][ids]
    baseline = (data["k"][ids] == 0) | (config["h"][cids] == 0)
    eligible = (
        np.ones(len(ids), dtype=bool)
        if eligibility == "unrestricted"
        else (baseline | (config["stability"][cids] == "stable"))
    )
    boundary = (
        np.count_nonzero((~baseline) & (config["stability"][cids] == "boundary"))
        if eligibility == "stable"
        else 0
    )
    candidates = ids[eligible]
    invalid = np.count_nonzero(data["failure"][candidates])
    valid = candidates[data["failure"][candidates] == 0]
    assert len(valid), "Every grid includes a valid zero predictor."
    minimum = float(np.min(data["risks"][valid, objective]))
    values = data["risks"][valid, objective]
    tolerance = SIGN_TOL * np.maximum(1, np.maximum(abs(values), abs(minimum)))
    tied = valid[np.abs(values - minimum) <= tolerance]
    tc = data["configuration"][tied]
    order = np.lexsort((tied, config["batch"][tc], config["h"][tc], data["M"][tied]))
    chosen = int(tied[order[0]])
    cid = data["configuration"][chosen]
    positive_h = config["h"][data["configuration"][ids]]
    positive_h = positive_h[positive_h > 0]
    flags = []
    h, k = config["h"][cid], data["k"][chosen]
    if h == 0 or k == 0:
        flags.append("zero_predictor")
    if len(positive_h) and h == min(positive_h):
        flags.append("smallest_positive_rate")
    if len(positive_h) and h == max(positive_h):
        flags.append("largest_rate")
    consumed = data[maximum_stop][chosen]
    if consumed == np.min(data[maximum_stop][ids]):
        flags.append("earliest_stop")
    if consumed == np.max(data[maximum_stop][ids]):
        flags.append("latest_stop")
    return dict(
        endpoint=chosen,
        ties=tied,
        eligible=int(len(candidates)),
        invalid=int(invalid),
        boundary=int(boundary),
        minimum=minimum,
        complete=not (invalid or boundary),
        search_boundary=flags,
    )


def fixed_contrasts(spec, data):
    paired = {}
    config = spec["configurations"]
    for c in config:
        law = spec["laws"][c["law"]]
        if c["h"] not in law["fixed_h"]:
            continue
        key = (c["law"], c["h"], c["batch"])
        paired.setdefault(key, {})[c["scaling"]] = c
    fields = [
        "law",
        "h",
        "batch",
        "k",
        "M",
        "U_endpoint",
        "S_endpoint",
        "aggregate_gap",
        "rare_gap",
        "aggregate_sign",
        "rare_sign",
        "common_mean_gap",
        "mse_common_gap",
        "cross_moment_gap",
        "mse_rare_gap",
        "aggregate_bias_gap",
        "aggregate_design_gap",
        "aggregate_noise_gap",
        "rare_bias_gap",
        "rare_design_gap",
        "rare_noise_gap",
        "valid",
        "stability_U",
        "stability_S",
        "aggregate_relative_to_U",
        "rare_relative_to_U",
        "aggregate_relative_to_initial",
        "rare_relative_to_initial",
    ]
    rows = []
    for (law, h, batch), pair in paired.items():
        u, s = pair["U"], pair["S"]
        for position in range(u["size"]):
            ui, si = u["offset"] + position, s["offset"] + position
            valid = data["failure"][ui] == data["failure"][si] == 0
            with np.errstate(invalid="ignore", over="ignore"):
                risk_gap = data["risks"][si] - data["risks"][ui]
                v = data["second"][si] - data["second"][ui]
                parts = (data["risk_parts"][si] - data["risk_parts"][ui]).ravel()
                common = data["bias"][si, 0] - data["bias"][ui, 0]
            signs = [
                classification(data["risks"][ui, w], data["risks"][si, w], valid)
                for w in (0, 1)
            ]
            rows.append(
                [
                    law,
                    h,
                    batch,
                    data["k"][ui],
                    data["M"][ui],
                    ui,
                    si,
                    *risk_gap,
                    *signs,
                    common,
                    v[0, 0],
                    v[0, 1],
                    v[1, 1],
                    *parts,
                    valid,
                    u["stability"],
                    s["stability"],
                    *[
                        risk_gap[w] / data["risks"][ui, w]
                        if data["risks"][ui, w] > 0
                        else None
                        for w in (0, 1)
                    ],
                    *[
                        risk_gap[w] / data["risks"][u["offset"], w]
                        if data["risks"][u["offset"], w] > 0
                        else None
                        for w in (0, 1)
                    ],
                ]
            )
    return dict(fields=fields, rows=rows)


def envelopes(spec, data):
    cs = spec["configurations"]
    config = {
        key: np.array([c[key] for c in cs]) for key in ("h", "batch", "stability")
    }
    by_law = {}
    for c in cs:
        by_law.setdefault((c["law"], c["scaling"]), []).append(c)
    rows, tie_groups, tie_cache = [], [], {}

    def tie_id(tied):
        key = tuple(map(tuple, runs(tied)))
        if key not in tie_cache:
            tie_cache[key] = len(tie_groups)
            tie_groups.append(key)
        return tie_cache[key]

    for law in spec["laws"]:
        resolutions = [("coarse", "coarse")]
        if law["refined"]:
            resolutions += [("fine", "coarse"), ("coarse", "fine"), ("fine", "fine")]
        for rate_grid, stop_grid in resolutions:
            for budget, caps in (
                ("updates", KF if stop_grid == "fine" else KC),
                ("observations", MF if stop_grid == "fine" else MC),
            ):
                variable = "k" if budget == "updates" else "M"
                candidates = {}
                for scaling in ("U", "S"):
                    for batch in (1, 10, 100):
                        ids = []
                        for c in by_law[law["id"], scaling]:
                            if c["batch"] != batch or (
                                rate_grid == "coarse" and not c["coarse_rate"]
                            ):
                                continue
                            endpoints = np.arange(c["offset"], c["offset"] + c["size"])
                            ids.extend(
                                endpoints[np.isin(data[variable][endpoints], caps)]
                            )
                        candidates[scaling, batch] = np.array(ids, dtype=int)
                    if budget == "observations":
                        candidates[scaling, 0] = np.concatenate(
                            [candidates[scaling, b] for b in (1, 10, 100)]
                        )
                for batch in (
                    (1, 10, 100, 0) if budget == "observations" else (1, 10, 100)
                ):
                    for cap in caps:
                        for adjustment in ("rate", "rate_stop"):
                            chosen_ids = {}
                            for scaling in ("U", "S"):
                                ids = candidates[scaling, batch]
                                mask = (
                                    data[variable][ids] == cap
                                    if adjustment == "rate"
                                    else data[variable][ids] <= cap
                                )
                                chosen_ids[scaling] = ids[mask]
                            for eligibility in ("stable", "unrestricted"):
                                for objective in (0, 1):
                                    u, s = [
                                        select(
                                            chosen_ids[scaling],
                                            data,
                                            config,
                                            objective,
                                            eligibility,
                                            variable,
                                        )
                                        for scaling in ("U", "S")
                                    ]
                                    complete = u["complete"] and s["complete"]
                                    gap = s["minimum"] - u["minimum"]
                                    initial = (
                                        np.array(law["signal"])
                                        @ np.array(
                                            law[
                                                "gram"
                                                if objective == 0
                                                else "rare_second"
                                            ]
                                        )
                                        @ law["signal"]
                                        / 2
                                    )
                                    cross_gaps = (
                                        data["risks"][s["endpoint"]]
                                        - data["risks"][u["endpoint"]]
                                    )
                                    rows.append(
                                        [
                                            law["id"],
                                            rate_grid,
                                            stop_grid,
                                            budget,
                                            cap,
                                            batch,
                                            eligibility,
                                            adjustment,
                                            "aggregate" if objective == 0 else "rare",
                                            u["endpoint"],
                                            s["endpoint"],
                                            tie_id(u["ties"]),
                                            tie_id(s["ties"]),
                                            u["eligible"],
                                            s["eligible"],
                                            u["invalid"],
                                            s["invalid"],
                                            u["boundary"],
                                            s["boundary"],
                                            u["minimum"],
                                            s["minimum"],
                                            gap,
                                            classification(
                                                u["minimum"], s["minimum"], complete
                                            ),
                                            gap / u["minimum"]
                                            if u["minimum"] > 0
                                            else None,
                                            gap / initial if initial > 0 else None,
                                            *cross_gaps,
                                            u["search_boundary"],
                                            s["search_boundary"],
                                        ]
                                    )
        print(
            f"Envelopes: law {law['id'] + 1}/228; {len(rows)} comparisons", flush=True
        ) if (law["id"] + 1) % 12 == 0 else None
    return dict(fields=ENVELOPE_FIELDS, rows=rows, ties_inclusive_ranges=tie_groups)


def batch_contrasts(spec, data):
    configurations = {
        (c["law"], c["scaling"], c["batch"], c["h"]): c for c in spec["configurations"]
    }
    rows = []
    for c in spec["configurations"]:
        if c["h"] not in spec["laws"][c["law"]]["fixed_h"]:
            continue
        for larger in (10, 100):
            if larger <= c["batch"]:
                continue
            other = configurations[c["law"], c["scaling"], larger, c["h"]]
            left = np.arange(c["offset"], c["offset"] + c["size"])
            right = np.arange(other["offset"], other["offset"] + other["size"])
            for variable in ("k", "M"):
                shared, ai, bi = np.intersect1d(
                    data[variable][left], data[variable][right], return_indices=True
                )
                for budget, a, b in zip(shared, left[ai], right[bi], strict=True):
                    complete = data["failure"][a] == data["failure"][b] == 0
                    with np.errstate(invalid="ignore", over="ignore"):
                        gaps = data["risks"][b] - data["risks"][a]
                    signs = [
                        classification(
                            data["risks"][a, w], data["risks"][b, w], complete
                        )
                        for w in (0, 1)
                    ]
                    rows.append(
                        [
                            c["law"],
                            c["scaling"],
                            c["h"],
                            c["batch"],
                            larger,
                            variable,
                            budget,
                            a,
                            b,
                            *gaps,
                            *signs,
                        ]
                    )
    return dict(
        direction="larger minus smaller batch",
        fields=[
            "law",
            "scaling",
            "h",
            "smaller_batch",
            "larger_batch",
            "budget",
            "value",
            "smaller_endpoint",
            "larger_endpoint",
            "aggregate_gap",
            "rare_gap",
            "aggregate_sign",
            "rare_sign",
        ],
        rows=rows,
    )


def controls(spec, data):
    configurations = {
        (c["law"], c["scaling"], c["batch"], c["h"]): c for c in spec["configurations"]
    }
    common_residual = rare_residual = 0.0
    mean_tolerance_ratio = 0.0
    mean_endpoints = 0
    batch_psd = 0.0
    batch_comparisons = 0
    rescaling = []
    from robustness_spec import PANELS, model
    from run_normalization_robustness import moment_path, parameters

    for c in spec["configurations"]:
        law = spec["laws"][c["law"]]
        ids = np.arange(c["offset"], c["offset"] + c["size"])
        valid = np.isfinite(data["bias"][ids]).all(axis=1)
        if law["ell"] == 0:
            assert np.all(valid), "Every declared independent mean is finite."
            mean_endpoints += len(ids)
            counts = data["k"][ids][valid]
            expected_common = -((1 - c["h"]) ** counts) * law["signal"][0]
            rate = (
                c["h"]
                if c["scaling"] == "S"
                else 4 * c["h"] * law["q"] * (1 - law["q"])
            )
            expected_rare = -((1 - rate) ** counts) * law["signal"][1]
            if len(counts):
                expected = np.column_stack([expected_common, expected_rare])
                mean_tolerance_ratio = max(
                    mean_tolerance_ratio,
                    float(
                        np.max(
                            abs(data["bias"][ids[valid]] - expected)
                            / (2e-11 + 2e-10 * abs(expected))
                        )
                    ),
                )
                common_residual = max(
                    common_residual,
                    float(np.max(abs(data["bias"][ids[valid], 0] - expected_common))),
                )
                rare_residual = max(
                    rare_residual,
                    float(np.max(abs(data["bias"][ids[valid], 1] - expected_rare))),
                )
        if c["batch"] in (1, 10):
            other = configurations[c["law"], c["scaling"], 10 * c["batch"], c["h"]]
            oi = np.arange(other["offset"], other["offset"] + other["size"])
            shared, a, b = np.intersect1d(
                data["k"][ids], data["k"][oi], return_indices=True
            )
            good = (data["failure"][ids[a]] == 0) & (data["failure"][oi[b]] == 0)
            delta = data["second"][ids[a[good]]] - data["second"][oi[b[good]]]
            scale = np.maximum(
                1,
                np.maximum(
                    np.max(abs(data["second"][ids[a[good]]]), axis=(1, 2)),
                    np.max(abs(data["second"][oi[b[good]]]), axis=(1, 2)),
                ),
            )
            if len(delta):
                batch_psd = min(
                    batch_psd,
                    float(np.min(np.linalg.eigvalsh(delta / scale[:, None, None]))),
                )
            batch_comparisons += int(sum(good))
    for panel, (q, ell, signal, sigma2, h, stops) in enumerate(PANELS):
        m = model(q, ell)
        for scaling in ("U", "S"):
            scales, step = parameters(m, scaling, h)
            for batch in (1, 10):
                base = moment_path(m, scales, step, batch, stops, signal, sigma2)
                for g in (0.1, 10):
                    changed = moment_path(
                        m, g * scales, g * g * step, batch, stops, signal, sigma2
                    )
                    residual = {
                        key: float(np.max(abs(changed[key] - base[key])))
                        for key in ("bias", "second", "design", "noise", "risk_parts")
                    }
                    rescaling.append(
                        dict(
                            panel=panel,
                            scaling=scaling,
                            batch=batch,
                            g=g,
                            residual=residual,
                        )
                    )
    return dict(
        common_mean_max_absolute=common_residual,
        independent_mean_max_tolerance_ratio=mean_tolerance_ratio,
        independent_mean_compared_endpoints=mean_endpoints,
        rare_mean_max_absolute=rare_residual,
        batch_order_minimum_relative_eigenvalue=batch_psd,
        batch_order_compared_endpoints=batch_comparisons,
        global_rescaling_moments=rescaling,
    )


def resolution_changes(envelope):
    positions = {k: i for i, k in enumerate(envelope["fields"])}
    baseline = {}
    changes = []
    for index, row in enumerate(envelope["rows"]):
        key = tuple(
            row[positions[k]]
            for k in (
                "law",
                "budget",
                "cap",
                "batch",
                "eligibility",
                "adjustment",
                "objective",
            )
        )
        if row[1:3] == ["coarse", "coarse"]:
            baseline[key] = index
        elif key in baseline:
            other = baseline[key]
            changes.append([other, index, envelope["rows"][other][22] != row[22]])
    return dict(
        fields=["coarse_row", "refined_row", "classification_changed"], rows=changes
    )


def detailed_counts(spec, data):
    cs = spec["configurations"]
    result = {}
    for name in ("law", "scaling", "h", "batch"):
        config_values = np.array([c[name] for c in cs])
        values = config_values[data["configuration"]]
        categories, indices = np.unique(values, return_inverse=True)
        total = np.bincount(indices)
        invalid = np.bincount(indices[data["failure"] != 0], minlength=len(categories))
        result[name] = [
            dict(
                value=v,
                configurations=int(np.count_nonzero(config_values == v)),
                endpoints=n,
                invalid=bad,
            )
            for v, n, bad in zip(categories, total, invalid, strict=True)
        ]
    for name in ("k", "M"):
        categories, indices = np.unique(data[name], return_inverse=True)
        total = np.bincount(indices)
        invalid = np.bincount(indices[data["failure"] != 0], minlength=len(categories))
        result[name] = [
            dict(value=v, endpoints=n, invalid=bad)
            for v, n, bad in zip(categories, total, invalid, strict=True)
        ]
    return result


def produce(output):
    spec = json.loads((output / "specification.json").read_text())
    with np.load(output / "paths.npz", allow_pickle=False) as archive:
        data = {name: archive[name] for name in archive.files}
    env = envelopes(spec, data)
    fixed = fixed_contrasts(spec, data)
    codes, counts = np.unique(data["failure"], return_counts=True)
    failure_ledger = {
        str(int(code)): runs(np.flatnonzero(data["failure"] == code))
        for code in codes
        if code
    }
    summary = dict(
        schema_version=1,
        sign_direction="S minus U",
        risk_convention="excess risk with factor one half",
        specification_sha256=sha256(output / "specification.json"),
        paths_sha256=sha256(output / "paths.npz"),
        simulation_sha256=sha256(output / "paired-simulation.npz"),
        boundary_probes_sha256=sha256(output / "boundary-probes.json"),
        simulation_summary_sha256=sha256(output / "simulation-summary.json"),
        fixed=fixed,
        fixed_h_batch_contrasts=batch_contrasts(spec, data),
        envelopes=env,
        resolution=resolution_changes(env),
        controls=controls(spec, data),
        boundary_probes=json.loads((output / "boundary-probes.json").read_text()),
        simulation=json.loads((output / "simulation-summary.json").read_text()),
        failures=dict(
            codes=spec["failure_codes"],
            counts=dict(zip(map(int, codes), map(int, counts), strict=True)),
            endpoint_ranges=failure_ledger,
            meaning=(
                "Finite-support finite-time moments exist; "
                "invalid floating-point entries remain unresolved."
            ),
        ),
        counts_by_dimension=detailed_counts(spec, data),
        counts=dict(
            **spec["counts"],
            envelope_comparisons=len(env["rows"]),
            fixed_contrasts=len(fixed["rows"]),
            envelope_signs=Counter(row[22] for row in env["rows"]),
            configuration_stability=Counter(
                c["stability"] for c in spec["configurations"]
            ),
        ),
        archive_fields={
            "paths": list(data),
            "risk_parts": ["squared_bias", "design_variance", "noise_variance"],
            "risk_objectives": ["aggregate", "rare"],
            "psd_minimum": ["second", "design", "noise"],
        },
    )
    write_json(output / "summary.json", summary)
    print(json.dumps(summary["counts"]), flush=True)


if __name__ == "__main__":
    assert __debug__, "Run ordinary Python without -O."
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    produce(parser.parse_args().output)
