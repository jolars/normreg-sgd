"""Independent transformed updates, fixed-offset selections, and artifact audit."""

import argparse
import json
from contextlib import ExitStack

import numpy as np
from check_mushroom_rate_search import (
    check_stat,
    independent_components,
    independent_loss,
    reference_path,
)
from mushroom_sensitivity_spec import (
    BATCHES,
    CHECKPOINTS,
    FACTORS,
    ORIGINAL_STOPS,
    OUTPUT,
    REPS,
    SIZES,
    SOURCES,
    candidate_rows,
    configurations,
    declaration,
    queries,
    select,
)
from numpy.testing import assert_allclose, assert_array_equal
from practical_dynamics import prepare as original_prepare
from practical_spec import ROOT, load_mushroom, mushroom_data, sha256
from run_mushroom_rate_search import path
from run_mushroom_sensitivity import prepare
from scipy import sparse


def expected_selection(loss, rows, query, rare_count):
    objective = query["objective"] if rare_count or query["objective"] == 0 else 0
    choices = []
    for i, r in enumerate(rows):
        if r["scale"] != query["scale"] or r["observations"] > query["cap"]:
            continue
        if query["search"] == "expanded" and r["observations"] not in ORIGINAL_STOPS:
            continue
        value = loss[tuple(r["index"])][objective]
        score = float(value) if np.isfinite(value) else np.inf
        choices.append((score, r["observations"], r["batch"], r["factor"], i))
    chosen = sorted(choices)[0]
    return [chosen[-1], int(objective != query["objective"]), 0]


def check_numerics():
    x = np.array([[0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 0, 1]], dtype=float)
    y = np.array([1, -1, 0, 2], dtype=float)
    configs = configurations()
    params = prepare(x, y, configs)
    variance = np.var(x, axis=0)
    for ci, c in enumerate(configs):
        scale = c["scale"]
        if scale == "variance":
            expected = variance[:2]
        elif scale == "none":
            expected = np.ones(2)
        else:
            tau = 0 if scale == "sd" else float(scale.split("_")[1])
            expected = np.sqrt(variance[:2] + tau)
        assert_allclose(params["divisor"][ci, :2], expected)
        z = (x - x.mean(axis=0)) / params["divisor"][ci]
        z = np.column_stack((z, np.ones(len(x))))
        assert_allclose(
            params["curvature"][ci], np.linalg.eigvalsh(z.T @ z / len(x))[-1]
        )
    assert_allclose(params["divisor"][:, 2], 1)
    assert not params["active"][:, 2].any()
    indices = np.tile([0, 1, 3, 2, 1, 1, 0, 2], 4)
    for batch in (1, 4):
        expected = reference_path(x, y, params, indices, batch, (0, 8, 32))
        for design in (x, sparse.csr_matrix(x)):
            actual = path(design, y, params, indices, batch, (0, 8, 32))
            norm = 1 + np.max(np.abs(expected[0]), axis=-1)
            assert np.nanmax(np.abs(actual[0] - expected[0]) / norm[..., None]) < 2e-11
            assert_array_equal(actual[1], expected[1])
            assert_array_equal(actual[2], expected[2])
            assert_allclose(actual[0][..., 3], 0)
    broken = {k: v.copy() for k, v in params.items()}
    broken["eta"][:] = 1e120
    actual = path(x, y, broken, indices, 1, (0, 8, 32))
    assert_array_equal(actual[2], 1)
    assert np.isnan(actual[0][1:]).all()
    for scale in ("none", "sd", "damped_0.01"):
        ids = [i for i, c in enumerate(configs) if c["scale"] == scale]
        old = [
            configs[i] | {"scale": "damped" if scale == "damped_0.01" else scale}
            for i in ids
        ]
        ref = original_prepare(sparse.csr_matrix(x), y, old)
        for key in params:
            assert_allclose(params[key][ids], ref[key], rtol=1e-13, atol=1e-13)
    rows = candidate_rows()
    assert len(rows) == 2176 and len(configs) == 136 and len(queries()) == 96
    loss = np.random.default_rng(41).uniform(size=(2, 8, 136, 2))
    for values in (loss, np.ones_like(loss)):
        for q in queries():
            for count in (0, 2):
                assert select(values, rows, q, count)[0] == expected_selection(
                    values, rows, q, count
                )
    loss[:, 1:] = np.nan
    for q in queries():
        chosen = select(loss, rows, q, 0)[0]
        assert rows[chosen[0]]["observations"] == 0
        assert chosen == expected_selection(loss, rows, q, 0)
    print("Sensitivity divisors, curvature, updates, failures, and selection: passed.")


def check_artifacts():
    declared = declaration()
    manifest = json.loads((OUTPUT / "manifest.json").read_text())
    summary = json.loads((OUTPUT / "summary.json").read_text())
    assert manifest["started_utc"] >= declared["declared_utc"]
    assert manifest["declaration_sha256"] == sha256(OUTPUT / "declaration.json")
    assert summary["provenance"]["manifest_sha256"] == sha256(OUTPUT / "manifest.json")
    assert set(manifest["sources"]) == set(SOURCES)
    for name, digest in manifest["sources"].items():
        assert sha256(ROOT / name) == digest, name
    for name, digest in manifest["archives"].items():
        assert sha256(OUTPUT / name) == digest, name
    for name, digest in json.loads((OUTPUT / "artifacts.json").read_text()).items():
        assert sha256(OUTPUT / name) == digest, name
    assert manifest["configurations"] == configurations()
    assert manifest["candidates"] == candidate_rows()
    assert manifest["queries"] == queries()
    rows, configs, qs = candidate_rows(), configurations(), queries()
    old_dir = ROOT / "results/mushroom-rate-search"
    old_manifest = json.loads((old_dir / "manifest.json").read_text())
    raw = load_mushroom()
    caches = {}
    max_path, max_prediction = 0.0, 0.0
    with ExitStack() as stack:
        old_archives = {
            p: stack.enter_context(np.load(old_dir / p))
            for p in old_manifest["archives"]
        }
        for meta in manifest["replications"]:
            case, rep = meta["case"], meta["rep"]
            parts, details = mushroom_data(raw, case, rep)
            params = prepare(*parts[0][:2], configs)
            with np.load(OUTPUT / meta["archive"]) as archive:
                coeff, status, chosen = (
                    archive[k] for k in ("coefficients", "status", "selections")
                )
                assert coeff.shape == (2, 8, 136, meta["dimension"] + 1)
                assert_array_equal(np.isnan(coeff).all(axis=-1), status > 0)
                assert (
                    details["names"] == meta["names"]
                    and details["unknown"] == meta["unknown"]
                )
                for key in params:
                    assert_allclose(
                        archive["parameter_" + key], params[key], rtol=1e-13, atol=1e-13
                    )
                for name, ids, part in zip(
                    ("train", "validation", "test"),
                    details["partitions"],
                    parts,
                    strict=True,
                ):
                    assert_array_equal(archive["partition_" + name], ids)
                    assert meta[name + "_rare"] == int(part[2].sum())
                    assert_allclose(
                        archive[name],
                        independent_loss(*part, coeff),
                        rtol=2e-9,
                        atol=2e-10,
                    )
                old_meta = next(
                    m
                    for m in old_manifest["replications"]
                    if m["case"] == case and m["rep"] == rep
                )
                old = old_archives[old_meta["archive"]]
                prefix = f"c{case}_r{rep}_"
                assert_array_equal(archive["indices"], old[prefix + "indices"])
                for scale in ("none", "sd", "damped_0.01"):
                    ci = [i for i, c in enumerate(configs) if c["scale"] == scale]
                    oc = [
                        old_manifest["configurations"].index(
                            configs[i]
                            | {"scale": "damped" if scale == "damped_0.01" else scale}
                        )
                        for i in ci
                    ]
                    assert_allclose(
                        coeff[:, :, ci],
                        old[prefix + "coefficients"][:, :, oc],
                        rtol=2e-10,
                        atol=2e-10,
                    )
                for qi, query in enumerate(qs):
                    assert_array_equal(
                        chosen[qi],
                        expected_selection(
                            archive["validation"], rows, query, meta["validation_rare"]
                        ),
                    )
                    if query["scale"] in ("none", "sd", "damped_0.01"):
                        oq = query | {
                            "scale": "damped"
                            if query["scale"] == "damped_0.01"
                            else query["scale"]
                        }
                        old_id = old[prefix + "selections"][
                            old_manifest["queries"].index(oq), 0
                        ]
                        old_row, new_row = (
                            old_manifest["candidates"][old_id],
                            rows[chosen[qi, 0]],
                        )
                        assert all(
                            old_row[k] == new_row[k]
                            for k in ("factor", "batch", "observations")
                        )
                for bi, batch in enumerate(BATCHES):
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
                    reference, flags, failures, centered = reference_path(
                        *parts[0][:2],
                        {k: v[ci] for k, v in params.items()},
                        archive["indices"],
                        batch,
                        CHECKPOINTS,
                    )
                    assert_array_equal(status[bi][:, ci], flags)
                    assert_array_equal(archive["failure_update"][bi, ci], failures)
                    live = flags == 0
                    norm = 1 + np.max(np.abs(reference[live]), axis=-1)
                    error = (
                        np.max(
                            np.abs(coeff[bi][:, ci][live] - reference[live]), axis=-1
                        )
                        / norm
                    )
                    max_path = max(max_path, float(error.max()))
                    assert np.all(error < 2e-9)
                    assert np.all(
                        np.abs(
                            archive["centered_intercepts"][bi][:, ci][live]
                            - centered[live]
                        )
                        / norm
                        < 2e-9
                    )
                    for selected in set(chosen[:, 0]):
                        cbi, mi, config = rows[selected]["index"]
                        if cbi != bi:
                            continue
                        ref = reference[mi, ci.index(config)]
                        a = (
                            parts[1][0] @ coeff[bi, mi, config, 1:]
                            + coeff[bi, mi, config, 0]
                        )
                        b = parts[1][0] @ ref[1:] + ref[0]
                        discrepancy = float(np.max(np.abs(a - b) / (1 + np.abs(b))))
                        max_prediction = max(max_prediction, discrepancy)
                        assert discrepancy < 1e-8
                caches[(case, rep)] = dict(
                    test=archive["test"].reshape(-1, 2),
                    chosen=chosen[:, 0],
                    status=status,
                    failures=archive["failure_update"],
                    validation=archive["validation"].reshape(-1, 2),
                    features=independent_components(
                        coeff,
                        params,
                        meta["names"],
                        parts[2],
                        archive["centered_intercepts"],
                    ),
                    eta=params["eta"],
                )
            if (rep + 1) % 8 == 0:
                print(
                    f"Sensitivity audit n={SIZES[case][0]}: {rep + 1}/{REPS}",
                    flush=True,
                )
    for entry in (*summary["selections"], *summary["contrasts"]):
        case, qi = entry["case"], entry["query"]
        metas = [m for m in manifest["replications"] if m["case"] == case]
        values, kept = [], []
        for meta in metas:
            stratum = entry["stratum"]
            if stratum != "all":
                group, condition = stratum.split("_")
                if (meta[group + "_rare"] == 0) != (condition == "absent"):
                    continue
            data = caches[(case, meta["rep"])]
            kept.append((meta, data))
            value = data["test"][data["chosen"][qi]].copy()
            if "reference" in entry:
                ri = qs.index(qs[qi] | {"scale": entry["reference"]})
                value -= data["test"][data["chosen"][ri]]
            values.append(value)
        values = np.asarray(values).reshape(-1, 2)
        check_stat(entry["aggregate"], values[:, 0])
        check_stat(entry["rare"], values[:, 1])
        if "reference" not in entry:
            assert (
                entry["nominal_tuning_observations"] == 2 * len(FACTORS) * entry["cap"]
            )
            for field in next(iter(caches.values()))["features"]:
                check_stat(
                    entry[field],
                    [d["features"][field][d["chosen"][qi]] for _, d in kept],
                )
            chosen_rows = [rows[d["chosen"][qi]] for _, d in kept]
            check_stat(
                entry["eta"],
                [
                    d["eta"][r["index"][2]]
                    for (_, d), r in zip(kept, chosen_rows, strict=True)
                ],
            )
            assert entry["initialization"] == sum(
                r["observations"] == 0 for r in chosen_rows
            )
            for edge, factor in (
                ("lower_rate", FACTORS[0]),
                ("upper_rate", FACTORS[-1]),
            ):
                assert entry[edge] == sum(
                    r["observations"] > 0 and r["factor"] == factor for r in chosen_rows
                )
            for label, field, exclude_zero in (
                ("rate_histogram", "factor", True),
                ("batch_histogram", "batch", False),
                ("stop_histogram", "observations", False),
            ):
                for key, count in entry[label].items():
                    assert count == sum(
                        r[field] == float(key)
                        and (not exclude_zero or r["observations"] > 0)
                        for r in chosen_rows
                    )
            assert entry["rare_fallbacks"] == sum(
                qs[qi]["objective"] == 1 and m["validation_rare"] == 0 for m, _ in kept
            )
            eligible = [
                i
                for i, r in enumerate(rows)
                if r["scale"] == entry["scale"]
                and r["observations"] <= entry["cap"]
                and (
                    entry["search"] == "expanded_stops"
                    or r["observations"] in ORIGINAL_STOPS
                )
            ]
            assert entry["scored_endpoints"] == len(eligible)
            assert entry["failed_eligible_endpoints"] == sum(
                int(d["status"].ravel()[eligible].sum()) for _, d in kept
            )
            work = []
            for _, d in kept:
                cost = 0
                for bi, batch in enumerate(BATCHES):
                    for ci, c in enumerate(configs):
                        if c["scale"] == entry["scale"]:
                            failed = d["failures"][bi, ci]
                            cost += (
                                min(int(failed) * batch, entry["cap"])
                                if failed
                                else entry["cap"]
                            )
                work.append(cost)
            check_stat(entry["executed_live_observations"], work)
    for entry in summary["paths"]:
        case, qi, observations = entry["case"], entry["query"], entry["observations"]
        values, features = [], {k: [] for k in next(iter(caches.values()))["features"]}
        for rep in range(REPS):
            d = caches[(case, rep)]
            chosen = rows[d["chosen"][qi]]
            candidate = next(
                i
                for i, r in enumerate(rows)
                if r["index"][0] == chosen["index"][0]
                and r["index"][2] == chosen["index"][2]
                and r["observations"] == observations
            )
            values.append(d["test"][candidate])
            for k in features:
                features[k].append(d["features"][k][candidate])
        values = np.array(values)
        check_stat(entry["aggregate"], values[:, 0])
        check_stat(entry["rare"], values[:, 1])
        for k, v in features.items():
            check_stat(entry[k], v)
    for e in summary["cases"]:
        group = [d for (case, _), d in caches.items() if case == e["case"]]
        assert e["endpoints"] == sum(d["status"].size for d in group)
        assert e["failed_endpoints"] == sum(int(d["status"].sum()) for d in group)
        assert e["failed_paths"] == sum(np.count_nonzero(d["failures"]) for d in group)
        for entry in e["failures_by_scale"]:
            ci = [i for i, c in enumerate(configs) if c["scale"] == entry["scale"]]
            assert entry["paths"] == sum(
                np.count_nonzero(d["failures"][:, ci]) for d in group
            )
            assert entry["endpoints"] == sum(
                int(d["status"][:, :, ci].sum()) for d in group
            )
    for entry in summary["boundaries"]:
        data = caches[(entry["case"], entry["rep"])]
        candidate = int(data["chosen"][entry["query"]])
        assert entry["candidate"] == candidate
        query, row = qs[entry["query"]], rows[candidate]
        meta = next(
            m
            for m in manifest["replications"]
            if m["case"] == entry["case"] and m["rep"] == entry["rep"]
        )
        effective = (
            0
            if query["objective"] == 1 and meta["validation_rare"] == 0
            else query["objective"]
        )
        assert entry["initialization"] == (row["observations"] == 0)
        for name, other in entry["neighbors"].items():
            if other is None:
                assert row["factor"] == FACTORS[0 if name == "lower" else -1]
                continue
            r = rows[other["candidate"]]
            assert all(r[k] == row[k] for k in ("scale", "batch", "observations"))
            score = data["validation"][other["candidate"], effective]
            assert FACTORS.index(r["factor"]) == FACTORS.index(row["factor"]) + (
                -1 if name == "lower" else 1
            )
            assert other["failed"] == bool(data["status"].ravel()[other["candidate"]])
            assert other["finite_score"] == bool(np.isfinite(score))
            if np.isfinite(score):
                assert_allclose(other["score"], score)
                assert_allclose(
                    other["gap"], score - data["validation"][candidate, effective]
                )
            assert other["no_better"] == bool(
                not np.isfinite(score)
                or score >= data["validation"][candidate, effective]
            )
    print(
        "All sensitivity endpoints, selections, paired losses, and hashes passed; "
        f"maximum path error {max_path:.3g}, prediction error {max_prediction:.3g}."
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
