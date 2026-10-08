"""Verify gain distributions using independent rare-cell prediction errors."""

import json

import numpy as np
from numpy.testing import assert_allclose

from experiments.theory_bridge import config as cfg
from experiments.theory_bridge.engine import CELLS


def main():
    settings = json.loads((cfg.OUTPUT / "settings.json").read_text())
    report = json.loads((cfg.OUTPUT / "selection-gains.json").read_text())
    original = json.loads((cfg.OUTPUT / "summary.json").read_text())
    policy_ids = [settings["policies"].index(p) for p in report["policies"]]
    checked = 0
    with np.load(cfg.OUTPUT / "selection-gains.npz") as saved:
        for q_id, run in enumerate(settings["runs"]):
            chunks = []
            for record in run["evaluation"]:
                with np.load(cfg.OUTPUT / record["file"]) as archive:
                    chunks.append(archive["coefficients"][:, :, :2, :, :, policy_ids])
            coefficients = np.concatenate(chunks)
            truth = cfg.SIGNALS @ (CELLS[[1, 3]] - [0.5, run["q"]]).T
            residuals = coefficients[..., :1] + coefficients[..., 1:] @ CELLS[[1, 3]].T
            residuals -= truth[None, None, None, None, :, None, :]
            risk = np.mean(residuals**2, axis=-1) / 2
            assert_allclose(saved[f"q{q_id}_risk"], risk, atol=2e-14)
            assert_allclose(
                saved[f"q{q_id}_errors"][..., 1], residuals.mean(axis=-1), atol=2e-14
            )
            assert_allclose(
                saved[f"q{q_id}_errors"][..., 0],
                residuals[..., 1] - residuals[..., 0],
                atol=2e-14,
            )
            gains = risk[..., :1] - risk[..., 1:]
            assert_allclose(saved[f"q{q_id}_gain"], gains, atol=2e-14)
            assert (gains[..., 0] >= -2e-14).all()
            for row in report["rows"]:
                if row["q"] != run["q"]:
                    continue
                cap = run["caps"].index(row["cap"])
                arm = report["arms"].index(row["arm"])
                signal = report["signals"].index(row["signal"])
                policy = report["policies"].index(row["policy"])
                existing = next(
                    r
                    for r in original["rows"]
                    if all(
                        r[k] == row[k] for k in ("q", "cap", "arm", "signal", "policy")
                    )
                )
                advantage = (
                    gains[:, cap, arm, 0, signal, policy - 1]
                    - gains[:, cap, arm, 1, signal, policy - 1]
                )
                pairs = [(row["unscaled_minus_sd_gain"], advantage)]
                for s, name in enumerate(report["scalings"]):
                    values = gains[:, cap, arm, s, signal, policy - 1]
                    data = row["scaling"][name]
                    pairs.append((data["gain"], values))
                    assert_allclose(
                        values.mean(),
                        -existing["scaling"][name]["minus_calibrated"]["mean"],
                    )
                    positive = sorted(max(v, 0) for v in values)
                    tail = int(np.ceil(0.1 * len(values)))
                    if sum(positive):
                        assert_allclose(
                            data["positive_gain_top_decile_share"],
                            sum(positive[-tail:]) / sum(positive),
                        )
                    for source, p in (
                        ("calibrated_error", 0),
                        ("selected_error", policy),
                    ):
                        errors = residuals[:, cap, arm, s, signal, p]
                        for name, values in (
                            ("rare_mean_prediction", errors.mean(axis=-1)),
                            ("common_coefficient", errors[:, 1] - errors[:, 0]),
                        ):
                            assert_allclose(
                                data[source][name]["rms"], np.sqrt(np.mean(values**2))
                            )
                for summary, values in pairs:
                    assert summary["n"] == len(values)
                    assert_allclose(summary["mean"], values.mean(), atol=2e-14)
                    assert_allclose(
                        summary["mcse"], values.std(ddof=1) / np.sqrt(len(values))
                    )
                    assert_allclose(
                        [summary[k] for k in ("p05", "p25", "median", "p75", "p95")],
                        np.quantile(values, [0.05, 0.25, 0.5, 0.75, 0.95]),
                        atol=2e-14,
                    )
                    assert summary["positive_count"] == np.sum(values > 0)
                    assert summary["negative_count"] == np.sum(values < 0)
                assert_allclose(
                    row["selected_gap"]["mean"] - row["calibrated_gap"]["mean"],
                    advantage.mean(),
                    atol=2e-14,
                )
                checked += 1
    assert checked == 96
    print(f"{checked} paired distributions verified against rare-cell predictions.")


if __name__ == "__main__":
    main()
