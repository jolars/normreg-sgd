"""Post-run precision investigation of extreme validation-selected synthetic fits."""

import json
from decimal import Decimal, localcontext

import numpy as np
from practical_dynamics import choose, losses
from practical_spec import (
    LAWS,
    OUTPUT,
    ROOT,
    SCALES,
    SYNTHETIC_M,
    sha256,
    synthetic_data,
    write_json,
)


def decimal_path(x, y, parameters, ids, batch):
    """Use 160-digit decimal arithmetic on the declared float64 input constants."""
    with localcontext() as context:
        context.prec = 160

        def convert(x):
            return Decimal(float(x))

        mu = list(map(convert, parameters["mu"]))
        divisor = list(map(convert, parameters["divisor"]))
        eta = convert(parameters["eta"])
        intercept = convert(parameters["initial"])
        centered = [
            [convert(value) - shift for value, shift in zip(row, mu, strict=True)]
            for row in x
        ]
        response = list(map(convert, y))
        beta = [Decimal(0)] * x.shape[1]
        result = []
        failed = False

        def record():
            raw_intercept = intercept - sum(
                a * b for a, b in zip(mu, beta, strict=True)
            )
            result.append(
                [float(raw_intercept), *map(float, beta)]
                if not failed
                else [np.nan] * (len(beta) + 1)
            )

        record()
        for m in range(batch, max(SYNTHETIC_M) + 1, batch):
            if not failed:
                selected = ids[m - batch : m]
                residual = [
                    intercept
                    + sum(a * b for a, b in zip(centered[i], beta, strict=True))
                    - response[i]
                    for i in selected
                ]
                for j in range(len(beta)):
                    if parameters["active"][j]:
                        gradient = (
                            sum(
                                centered[i][j] * error
                                for i, error in zip(selected, residual, strict=True)
                            )
                            / batch
                        )
                        beta[j] -= eta * gradient / (divisor[j] * divisor[j])
                if parameters["fit_intercept"]:
                    intercept -= eta * sum(residual) / batch
                failed = max(map(abs, [intercept, *beta])) > Decimal("1e100")
            if m in SYNTHETIC_M:
                record()
        return np.array(result)


def investigate():
    manifest = json.loads((OUTPUT / "synthetic.json").read_text())
    rows = manifest["candidates"]
    records = []
    with np.load(OUTPUT / "synthetic.npz") as archive:
        for case in range(len(LAWS)):
            for scale in SCALES:
                query = dict(
                    arm="centered_fitted",
                    cap=2048,
                    objective=0,
                    scale=scale,
                    rule="joint",
                )
                qi = manifest["queries"].index(query)
                values = []
                for rep in range(128):
                    prefix = f"c{case}_r{rep}_"
                    selected = int(archive[prefix + "selections"][qi, 0])
                    values.append(
                        archive[prefix + "test"][tuple(rows[selected]["index"])][1]
                    )
                rep = int(np.argmax(values))
                prefix = f"c{case}_r{rep}_"
                parts, test, weights, _ = synthetic_data(case, rep)
                parameters = {
                    key: archive[prefix + "parameter_" + key]
                    for key in (
                        "mu",
                        "divisor",
                        "eta",
                        "initial",
                        "active",
                        "fit_intercept",
                    )
                }
                coefficients = np.full_like(archive[prefix + "coefficients"], np.nan)
                for ci, config in enumerate(manifest["configurations"]):
                    if config["arm"] != query["arm"] or config["scale"] != scale:
                        continue
                    params = {key: value[ci] for key, value in parameters.items()}
                    for bi, batch in enumerate((1, 16)):
                        coefficients[bi, :, ci] = decimal_path(
                            *parts[0][:2], params, archive[prefix + "indices"], batch
                        )
                validation = losses(*parts[1], coefficients)
                selected, _, _, eligible = choose(
                    validation,
                    rows,
                    **query,
                    validation_rare_count=int(parts[1][2].sum()),
                )
                original = int(archive[prefix + "selections"][qi, 0])
                oi, si = tuple(rows[original]["index"]), tuple(rows[selected]["index"])
                original_coef = archive[prefix + "coefficients"][oi]
                exact_coef = coefficients[oi]
                predictions = (
                    parts[1][0] @ (original_coef[1:] - exact_coef[1:])
                    + original_coef[0]
                    - exact_coef[0]
                )
                score = validation[oi][0]
                competitors = [
                    validation[tuple(rows[i]["index"])][0]
                    for i in eligible
                    if i != selected
                ]
                finite = [x for x in competitors if np.isfinite(x)]
                refined_loss = losses(*test, coefficients, weights)
                records.append(
                    dict(
                        case=case,
                        scale=scale,
                        rep=rep,
                        train_rare=int(parts[0][2].sum()),
                        validation_rare=int(parts[1][2].sum()),
                        original_candidate=original,
                        decimal_candidate=selected,
                        selection_changed=selected != original,
                        original_coefficients=original_coef,
                        decimal_coefficients=exact_coef,
                        original_validation=archive[prefix + "validation"][oi][0],
                        decimal_validation=float(score),
                        decimal_selection_margin=min(finite) - float(validation[si][0]),
                        max_validation_prediction_difference=float(
                            np.max(np.abs(predictions))
                        ),
                        original_rare_loss=float(values[rep]),
                        decimal_original_rare_loss=float(refined_loss[oi][1]),
                        decimal_selected_rare_loss=float(refined_loss[si][1]),
                    )
                )
    return records


def main():
    records = investigate()
    sources = [
        OUTPUT / "synthetic.json",
        OUTPUT / "synthetic.npz",
        ROOT / "experiments/audit_practical_precision.py",
    ]
    write_json(
        OUTPUT / "precision-audit.json",
        dict(
            scope="Post-run diagnostic: worst rare test loss in each of 24 "
            "centered-fitted, aggregate-joint-selected law/scaling panels. "
            "Replay all eligible trajectories at 160-digit precision; "
            "no primary selection or result replaced.",
            sources={str(p.relative_to(ROOT)): sha256(p) for p in sources},
            records=records,
        ),
    )
    print(
        "Decimal tail audit:",
        sum(r["selection_changed"] for r in records),
        "of",
        len(records),
        "selections changed",
        flush=True,
    )


if __name__ == "__main__":
    main()
