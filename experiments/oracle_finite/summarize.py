"""Compare saved finite-grid risks with the scalar limiting predictions."""

import argparse
import json

import numpy as np

from experiments.common.limiting_oracle import oracle_minimum
from experiments.oracle_finite.config import OUTPUT


def summarize(settings, archive):
    rows, convergence = [], []
    for qi, q in enumerate(settings["prevalences"]):
        b = q * (1 - q)
        risks = archive[f"q{qi}_risk"]
        alpha = archive[f"q{qi}_alpha"]
        stops = archive[f"q{qi}_stop"]
        caps = archive[f"q{qi}_cap"]
        errors, refinements = [], []
        disagreements = []
        away_from_ties = []
        for ci, case in enumerate(settings["cases"]):
            cap = int(caps[ci])
            budget = float(cap * b)
            signals = [case[key] for key in ("s", "r", "noise")]
            limit = np.array(
                [oracle_minimum(scaled, budget, *signals) for scaled in (False, True)]
            )
            nominal = np.array(
                [
                    oracle_minimum(scaled, case["tau"], *signals)[0]
                    for scaled in (False, True)
                ]
            )
            risk = risks[ci, 3]
            difference = risk - limit[:, 0]
            refinement = risks[ci, :3] - risk
            gap = float(risk[1] - risk[0])
            predicted_gap = float(limit[1, 0] - limit[0, 0])
            nominal_gap = float(nominal[1] - nominal[0])
            if abs(predicted_gap) > 1e-9 and gap * predicted_gap < 0:
                disagreements.append(case["name"])
                if abs(nominal_gap) > 1e-8:
                    away_from_ties.append(case["name"])
            errors.append(abs(difference))
            refinements.append(refinement)
            rows.append(
                dict(
                    **case,
                    q=q,
                    cap=cap,
                    actual_budget=budget,
                    finite_risk=risk.tolist(),
                    finite_alpha=alpha[ci, 3].tolist(),
                    finite_stop=stops[ci, 3].tolist(),
                    limiting_risk=limit[:, 0].tolist(),
                    limiting_alpha=limit[:, 1].tolist(),
                    nominal_limiting_risk=nominal.tolist(),
                    nominal_limiting_ratio_S_over_U=float(nominal[1] / nominal[0])
                    if nominal[0] > 0
                    else None,
                    finite_minus_limit=difference.tolist(),
                    finite_gap_S_minus_U=gap,
                    limiting_gap_S_minus_U=predicted_gap,
                    nominal_limiting_gap_S_minus_U=nominal_gap,
                    finite_ratio_S_over_U=float(risk[1] / risk[0])
                    if risk[0] > 0
                    else None,
                    limiting_ratio_S_over_U=float(limit[1, 0] / limit[0, 0])
                    if limit[0, 0] > 0
                    else None,
                    refinement_to_fine=refinement.tolist(),
                )
            )
        convergence.append(
            dict(
                q=q,
                maximum_absolute_risk_error_U_S=np.max(errors, axis=0).tolist(),
                maximum_refinement_by_search_U_S=np.max(refinements, axis=0).tolist(),
                strict_sign_disagreements=disagreements,
                sign_disagreements_away_from_nominal_ties=away_from_ties,
            )
        )
    return dict(
        purpose="Exact finite-grid risks versus limiting oracle predictions; "
        "search refinement is a sensitivity diagnostic, not an optimality bound.",
        scalings=settings["scalings"],
        refinement_rows=settings["searches"][:3],
        budget_comparison="Primary limits use the actual Mq(1-q); nominal limits "
        "are saved separately to expose integer-cap rounding.",
        convergence=convergence,
        rows=rows,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    settings = json.loads((OUTPUT / "settings.json").read_text())
    with np.load(OUTPUT / "search.npz") as archive:
        report = summarize(settings, archive)
    content = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.check:
        assert (OUTPUT / "summary.json").read_text() == content
        print("Saved finite-prevalence summary matches the search outputs.")
    else:
        (OUTPUT / "summary.json").write_text(content)
        print(f"Summarized {len(report['rows'])} finite-prevalence comparisons.")
    for row in report["convergence"]:
        print(
            f"q={row['q']:g}: "
            f"max risk errors U/S={row['maximum_absolute_risk_error_U_S']}; "
            f"strict sign disagreements={len(row['strict_sign_disagreements'])}."
        )


if __name__ == "__main__":
    main()
