"""Independently verify saved rare-risk terms using binary-cell predictions."""

import json
from itertools import product

import numpy as np
from numpy.testing import assert_allclose

from experiments.theory_bridge import config as cfg
from experiments.theory_bridge.engine import CELLS
from experiments.theory_bridge.risk_decomposition import cancellation_summary, decompose


def check_statistics(summary, values):
    assert summary["n"] == len(values)
    assert summary["missing"] == 0
    assert_allclose(summary["mean"], np.mean(values), atol=2e-14)
    assert_allclose(
        summary["mcse"], np.std(values, ddof=1) / np.sqrt(len(values)), atol=2e-14
    )
    assert_allclose(summary["median"], np.median(values), atol=2e-14)
    assert_allclose(summary["p95"], np.quantile(values, 0.95), atol=2e-14)
    assert_allclose(summary["maximum"], np.max(values), atol=2e-14)


def check_examples():
    q = 0.2
    truth = np.array([[0.4, 1.0]])
    # These endpoints isolate common error, each mean-error term, cancellation,
    # reinforcement, and a zero denominator, including a nonzero raw intercept.
    centered = np.array(
        [
            [1.2, 0.0, 0.0],
            [0.0, 2.0, 0.0],
            [0.0, 0.0, -2.0],
            [0.0, 2.0, -2.0],
            [0.0, 2.0, 2.0],
            [0.0, 0.0, 0.0],
        ]
    )
    coefficients = np.zeros((len(centered), 1, 2, 1, 1, 1, 3))
    coefficients[..., 1] = truth[0, 0]
    coefficients[..., 2] = truth[0, 1]
    for i, (common, intercept, rare) in enumerate(centered):
        coefficients[i, 0, 1, 0, 0, 0, 1:] += [common, rare / (1 - q)]
        coefficients[i, 0, 1, 0, 0, 0, 0] = intercept
    coefficients[..., 0] -= 0.5 * coefficients[..., 1] + q * coefficients[..., 2]
    errors, terms = decompose(coefficients, truth, q)
    assert_allclose(errors[:, 0, 1, 0, 0, 0], centered, atol=1e-15)
    assert_allclose(
        terms[:, 0, 1, 0, 0, 0],
        [
            [0.18, 0, 0, 0],
            [0, 2, 0, 0],
            [0, 0, 2, 0],
            [0, 2, 2, -4],
            [0, 2, 2, 4],
            [0, 0, 0, 0],
        ],
        atol=1e-15,
    )
    for i, fraction in ((3, 1), (4, -1), (5, 0)):
        repeated_errors = np.repeat(errors[i, 0, 1, 0, 0], 2, axis=0)
        repeated_terms = np.repeat(terms[i, 0, 1, 0, 0], 2, axis=0)
        summary = cancellation_summary(repeated_errors, repeated_terms)
        assert_allclose(summary["fraction"]["mean"], fraction)
        if i == 5:
            assert summary["pooled_fraction"] is None
        else:
            assert_allclose(summary["pooled_fraction"], fraction)


def main():
    check_examples()
    settings = json.loads((cfg.OUTPUT / "settings.json").read_text())
    report = json.loads((cfg.OUTPUT / "risk-decomposition.json").read_text())
    original = json.loads((cfg.OUTPUT / "summary.json").read_text())
    assert report["arms"] == settings["arms"][:2]
    assert report["signals"] == settings["signal_names"]
    assert report["scalings"] == settings["scalings"]
    assert (
        report["policies"] == ["calibrated", "path_oracle"] + settings["policies"][3:]
    )
    fields = ("q", "cap", "arm", "signal", "policy")
    identities = [tuple(row[k] for k in fields) for row in report["rows"]]
    expected = {
        (run["q"], cap, arm, signal, policy)
        for run in settings["runs"]
        for cap, arm, signal, policy in product(
            run["caps"], report["arms"], report["signals"], report["policies"]
        )
    }
    assert len(identities) == len(set(identities))
    assert set(identities) == expected
    policy_ids = [settings["policies"].index(p) for p in report["policies"]]
    checked = 0
    with (
        np.load(cfg.OUTPUT / "risk-decomposition.npz") as saved,
        np.load(cfg.OUTPUT / "selection-gains.npz") as gain_archive,
    ):
        for q_id, run in enumerate(settings["runs"]):
            chunks = []
            for record in run["evaluation"]:
                with np.load(cfg.OUTPUT / record["file"]) as archive:
                    chunks.append(archive["coefficients"][:, :, :2, :, :, policy_ids])
            coefficients = np.concatenate(chunks)
            truth = np.asarray(settings["signals"]) @ (CELLS - [0.5, run["q"]]).T
            predictions = coefficients[..., :1] + coefficients[..., 1:] @ CELLS.T
            residuals = predictions - truth[None, None, None, None, :, None, :]
            weights = np.array([(1 - run["q"]) / 2, run["q"] / 2] * 2)
            intercept = predictions @ weights
            assert_allclose(intercept[:, :, 0], 0, atol=5e-14)
            intercept[:, :, 0] = 0
            rare_mean = residuals[..., [1, 3]].mean(axis=-1)
            rare = rare_mean - intercept
            # Cell subtraction can leave roundoff when the saved rare coefficient
            # is exactly correct; preserve those exact zeros for sign counts.
            rare[
                coefficients[..., 2] == np.asarray(settings["signals"])[:, None, 1]
            ] = 0
            common = residuals[..., 3] - residuals[..., 1]
            errors = np.stack((common, intercept, rare), axis=-1)
            assert_allclose(saved[f"q{q_id}_errors"], errors, atol=5e-14)
            parts = np.stack((common / 2, -common / 2), axis=-1)
            common_term = np.mean(parts**2, axis=-1) / 2
            terms = np.stack(
                (common_term, intercept**2 / 2, rare**2 / 2, intercept * rare), axis=-1
            )
            assert_allclose(saved[f"q{q_id}_terms"], terms, atol=5e-14)
            risk = np.mean(residuals[..., [1, 3]] ** 2, axis=-1) / 2
            assert_allclose(terms.sum(axis=-1), risk, atol=5e-14)
            assert_allclose(risk, gain_archive[f"q{q_id}_risk"], atol=5e-14)
            zero_intercept_risk = (
                np.mean((residuals[..., [1, 3]] - intercept[..., None]) ** 2, axis=-1)
                / 2
            )
            for row in report["rows"]:
                if row["q"] != run["q"]:
                    continue
                cap = run["caps"].index(row["cap"])
                arm = report["arms"].index(row["arm"])
                signal = report["signals"].index(row["signal"])
                policy = report["policies"].index(row["policy"])
                selected = terms[:, cap, arm, :, signal, policy]
                calibrated = terms[:, cap, arm, :, signal, 0]
                gap = selected[:, 1] - selected[:, 0]
                gains = calibrated - selected
                for s, name in enumerate(report["scalings"]):
                    data = row["scaling"][name]
                    for i, term in enumerate(report["term_axis"]):
                        check_statistics(data["terms"][term], selected[:, s, i])
                        check_statistics(data["gain_terms"][term], gains[:, s, i])
                    check_statistics(data["risk"], risk[:, cap, arm, s, signal, policy])
                    cross = selected[:, s, 3]
                    squared = selected[:, s, 1:3].sum(axis=-1)
                    cancellation = data["cancellation"]
                    fractions = np.array(
                        [
                            -c / v if v else 0
                            for c, v in zip(cross, squared, strict=True)
                        ]
                    )
                    assert (np.abs(fractions) <= 1 + 1e-14).all()
                    check_statistics(cancellation["fraction"], fractions)
                    assert_allclose(
                        cancellation["pooled_fraction"], -cross.mean() / squared.mean()
                    )
                    assert cancellation["opposing_sign_count"] == np.sum(cross < 0)
                    assert cancellation["zero_product_count"] == np.sum(cross == 0)
                    for i, error in enumerate(report["error_axis"]):
                        assert_allclose(
                            cancellation["error_rms"][error],
                            np.sqrt(
                                np.mean(errors[:, cap, arm, s, signal, policy, i] ** 2)
                            ),
                            atol=5e-14,
                        )
                for i, term in enumerate(report["term_axis"]):
                    check_statistics(row["gap_terms"][term], gap[:, i])
                    check_statistics(
                        row["gap_change_terms"][term], gains[:, 0, i] - gains[:, 1, i]
                    )
                check_statistics(row["gap"], gap.sum(axis=-1))
                check_statistics(row["gap_without_cross"], gap[:, :3].sum(axis=-1))
                zero = zero_intercept_risk[:, cap, arm, :, signal, policy]
                check_statistics(
                    row["gap_with_zero_intercept"], zero[:, 1] - zero[:, 0]
                )
                existing = next(
                    r
                    for r in original["rows"]
                    if all(
                        r[k] == row[k] for k in ("q", "cap", "arm", "signal", "policy")
                    )
                )
                assert_allclose(row["gap"]["mean"], existing["gap"]["mean"], atol=5e-14)
                assert_allclose(row["gap"]["mcse"], existing["gap"]["mcse"], atol=5e-14)
                checked += 1
    assert checked == 120
    print(f"{checked} decompositions verified against cells, saved risks, and gains.")


if __name__ == "__main__":
    main()
