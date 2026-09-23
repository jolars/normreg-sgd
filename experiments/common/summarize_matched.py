"""Summarize paired risks, tails, absence strata, paths, and equal tuning work."""

import json
from contextlib import ExitStack

import numpy as np

from experiments.common.data import LAWS, REPS, SIZES, result_dir, write_json
from experiments.common.rates25 import (
    BATCHES,
    CHECKPOINTS,
    SCALES,
    eligible_ids,
    search_grid,
)
from experiments.common.statistics import statistics


def read_case(manifest, case):
    output = result_dir(("synthetic", "mushroom")[manifest["stage"]], "rates25")
    metas = [m for m in manifest["replications"] if m["case"] == case]
    data = {
        k: []
        for k in (
            "test",
            "validation",
            "selections",
            "status",
            "failure_update",
            "parameter_eta",
            "features",
        )
    }
    with ExitStack() as stack:
        archives = {
            p: stack.enter_context(np.load(output / p))
            for p in {m["archive"] for m in metas}
        }
        for meta in metas:
            archive, prefix = archives[meta["archive"]], meta["prefix"]
            for key in data:
                if key != "features":
                    data[key].append(archive[prefix + key])
            coef = archive[prefix + "coefficients"]
            name = "rare" if manifest["stage"] == 0 else "spore-print-color=r"
            j = meta["names"].index(name) + 1 if name in meta["names"] else None
            rare_coef = (
                coef[..., j] if j else np.where(np.isfinite(coef[..., 0]), 0, np.nan)
            )
            data["features"].append(
                np.stack(
                    (coef[..., 0], rare_coef, archive[prefix + "centered_intercepts"]),
                    axis=-1,
                )
            )
    return metas, {k: np.array(v) for k, v in data.items()}


def summarize_case(manifest, case):
    stage = manifest["stage"]
    metas, data = read_case(manifest, case)
    rows, qs, configs = (
        manifest[k] for k in ("candidates", "queries", "configurations")
    )
    reps = REPS[stage]
    ids = data["selections"][:, :, 0]
    tests = data["test"].reshape(reps, -1, 2)
    validation = data["validation"].reshape(reps, -1, 2)
    features = data["features"].reshape(reps, -1, 3)
    selected = tests[np.arange(reps)[:, None], ids]
    selected_features = features[np.arange(reps)[:, None], ids]
    strata = dict(
        all=np.ones(reps, dtype=bool),
        train_absent=np.array([m["train_rare"] == 0 for m in metas]),
        train_present=np.array([m["train_rare"] > 0 for m in metas]),
        validation_absent=np.array([m["validation_rare"] == 0 for m in metas]),
        validation_present=np.array([m["validation_rare"] > 0 for m in metas]),
    )
    result = dict(
        stage=stage,
        case=case,
        label=LAWS[case]["name"] if stage == 0 else f"n={SIZES[case][0]}",
        endpoints=int(data["status"].size),
        failed_endpoints=int(data["status"].sum()),
        failed_paths=int(np.count_nonzero(data["failure_update"])),
        train_rare=[m["train_rare"] for m in metas],
        validation_rare=[m["validation_rare"] for m in metas],
        test_rare=[m["test_rare"] for m in metas],
        failures=[],
        selections=[],
        contrasts=[],
        paths=[],
    )
    for arm in dict.fromkeys(c["arm"] for c in configs):
        for scale in SCALES:
            ci = [
                i
                for i, c in enumerate(configs)
                if c["arm"] == arm and c["scale"] == scale
            ]
            result["failures"].append(
                dict(
                    arm=arm,
                    scale=scale,
                    paths=int(np.count_nonzero(data["failure_update"][:, :, ci])),
                    endpoints=int(data["status"][:, :, :, ci].sum()),
                )
            )
    # Arrays retain every neighbor diagnostic without duplicating query metadata.
    neighbors = np.full((reps, len(qs), 2), -1, dtype=np.int32)
    scores = np.full((reps, len(qs), 2), np.nan)
    neighbor_failed = np.zeros((reps, len(qs), 2), dtype=np.uint8)
    row_lookup = {
        (r["arm"], r["scale"], r["batch"], r["observations"], r["factor"]): i
        for i, r in enumerate(rows)
    }
    for qi, q in enumerate(qs):
        chosen = [rows[i] for i in ids[:, qi]]
        factors, stops = search_grid(stage, q["search"])
        ci = [
            i
            for i, c in enumerate(configs)
            if c["arm"] == q["arm"]
            and c["scale"] == q["scale"]
            and c["factor"] in factors
        ]
        used = np.zeros(reps)
        for bi, batch in enumerate(BATCHES[stage]):
            failure = data["failure_update"][:, bi, ci] * batch
            used += np.minimum(np.where(failure > 0, failure, q["cap"]), q["cap"]).sum(
                axis=1
            )
        eligible = eligible_ids(stage, **q)
        for rep, row in enumerate(chosen):
            if row["observations"] == 0:
                continue
            effective = 0 if data["selections"][rep, qi, 1] else q["objective"]
            fi = factors.index(row["factor"])
            for j, other in enumerate((fi - 1, fi + 1)):
                if other in range(len(factors)):
                    key = (
                        row["arm"],
                        row["scale"],
                        row["batch"],
                        row["observations"],
                        factors[other],
                    )
                    nid = row_lookup[key]
                    neighbors[rep, qi, j] = nid
                    scores[rep, qi, j] = validation[rep, nid, effective]
                    neighbor_failed[rep, qi, j] = data["status"].reshape(reps, -1)[
                        rep, nid
                    ]
        for stratum, mask in strata.items():
            entries = [r for r, keep in zip(chosen, mask, strict=True) if keep]
            result["selections"].append(
                dict(
                    query=qi,
                    **q,
                    stratum=stratum,
                    aggregate=statistics(selected[mask, qi, 0]),
                    rare=statistics(selected[mask, qi, 1]),
                    **{
                        name: statistics(selected_features[mask, qi, j])
                        for j, name in enumerate(
                            ("raw_intercept", "rare_coefficient", "centered_intercept")
                        )
                    },
                    eta=statistics(
                        np.array(
                            [
                                data["parameter_eta"][rep, r["index"][2]]
                                for rep, r in enumerate(chosen)
                            ]
                        )[mask]
                    ),
                    initialization=sum(r["observations"] == 0 for r in entries),
                    lower_rate=sum(
                        r["observations"] > 0 and r["factor"] == factors[0]
                        for r in entries
                    ),
                    upper_rate=sum(
                        r["observations"] > 0 and r["factor"] == factors[-1]
                        for r in entries
                    ),
                    rate_histogram={
                        str(f): sum(
                            r["observations"] > 0 and r["factor"] == f for r in entries
                        )
                        for f in factors
                    },
                    batch_histogram={
                        str(b): sum(r["batch"] == b for r in entries)
                        for b in BATCHES[stage]
                    },
                    stop_histogram={
                        str(m): sum(r["observations"] == m for r in entries)
                        for m in stops
                    },
                    rare_fallbacks=int(data["selections"][mask, qi, 1].sum()),
                    nominal_tuning_observations=2 * len(factors) * q["cap"],
                    executed_live_observations=statistics(used[mask]),
                    scored_endpoints=len(eligible),
                    failed_eligible_endpoints=int(
                        data["status"].reshape(reps, -1)[mask][:, eligible].sum()
                    ),
                )
            )
            for reference in SCALES[: SCALES.index(q["scale"])]:
                ri = qs.index(q | {"scale": reference})
                delta = selected[mask, qi] - selected[mask, ri]
                result["contrasts"].append(
                    dict(
                        query=qi,
                        **q,
                        reference=reference,
                        stratum=stratum,
                        aggregate=statistics(delta[:, 0]),
                        rare=statistics(delta[:, 1]),
                    )
                )
        if q["cap"] == max(CHECKPOINTS[stage]):
            for mi, m in enumerate(CHECKPOINTS[stage]):
                risk = np.array(
                    [
                        data["test"][rep, r["index"][0], mi, r["index"][2]]
                        for rep, r in enumerate(chosen)
                    ]
                )
                feature = np.array(
                    [
                        data["features"][rep, r["index"][0], mi, r["index"][2]]
                        for rep, r in enumerate(chosen)
                    ]
                )
                result["paths"].append(
                    dict(
                        query=qi,
                        observations=m,
                        aggregate=statistics(risk[:, 0]),
                        rare=statistics(risk[:, 1]),
                        rare_coefficient=statistics(feature[:, 1]),
                        raw_intercept=statistics(feature[:, 0]),
                    )
                )
    return result, dict(
        neighbor_candidates=neighbors,
        neighbor_scores=scores,
        neighbor_failed=neighbor_failed,
    )


def summarize(label):
    output = result_dir(label, "rates25")
    manifest = json.loads((output / f"{label}.json").read_text())
    for case in sorted({m["case"] for m in manifest["replications"]}):
        result, boundaries = summarize_case(manifest, case)
        write_json(output / f"{label}-summary-c{case}.json", result)
        np.savez_compressed(output / f"{label}-boundaries-c{case}.npz", **boundaries)
        print(f"Summarized {label} case {case + 1}.", flush=True)
