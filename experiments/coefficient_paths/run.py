"""Save full-gradient paths to a shared OLS solution in a noiseless example."""

import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "results/coefficient-paths"


def calculate():
    q = 0.02
    counts = [98, 2, 98, 2]
    cells = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    x = np.repeat(cells, counts, axis=0) - [0.5, q]
    y = x @ np.ones(2)
    gram = x.T @ x / len(x)
    ols = np.linalg.lstsq(x, y, rcond=None)[0]
    np.testing.assert_allclose(gram, np.diag([0.25, q * (1 - q)]), atol=1e-14)
    np.testing.assert_allclose(ols, [1, 1], atol=1e-14)
    np.testing.assert_allclose(x.T @ (x @ ols - y), 0, atol=1e-12)
    common_step = 0.1
    stop = 20
    last = 2000
    methods = []
    for scaling, name in enumerate(["Unscaled", "Standardized"]):
        divisor = np.ones(2) if scaling == 0 else np.sqrt(np.diag(gram))
        rate = common_step * divisor[0] ** 2 / gram[0, 0]
        step = rate / divisor**2
        beta = np.zeros(2)
        path = [beta.copy()]
        for _ in range(last):
            beta -= step * (x.T @ (x @ beta - y) / len(x))
            path.append(beta.copy())
        path = np.array(path)
        exact = ols * (1 - (1 - step * np.diag(gram)) ** np.arange(last + 1)[:, None])
        np.testing.assert_allclose(path, exact, atol=1e-13)
        np.testing.assert_allclose(path[-1], ols, atol=2e-7)
        losses = np.mean((x @ path.T - y[:, None]) ** 2, axis=0) / 2
        assert np.all(np.diff(losses) <= 1e-14)
        methods.append(
            dict(
                name=name,
                rate=float(rate),
                divisor=divisor.tolist(),
                path=path.tolist(),
                loss=losses.tolist(),
                stopped_coefficients=path[stop].tolist(),
            )
        )
    np.testing.assert_allclose(
        methods[0]["stopped_coefficients"][0],
        methods[1]["stopped_coefficients"][0],
        atol=1e-13,
    )
    print("Checked analytical paths, OLS convergence, and decreasing training loss.")
    return dict(
        purpose="Constructed least-squares geometry; no stochastic risk claim.",
        q=q,
        cell_counts=counts,
        x=x.tolist(),
        y=y.tolist(),
        gram=gram.tolist(),
        noise_variance=0,
        intercept="fixed zero after centering",
        ols=ols.tolist(),
        initialization=[0, 0],
        stop=stop,
        last=last,
        stop_rule="Illustrative stop after 20 full-gradient updates, not selected.",
        calibration="Both common-coordinate error multipliers equal 0.9.",
        methods=methods,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = calculate()
    if args.check:
        assert json.loads((OUTPUT / "summary.json").read_text()) == report
        print("Coefficient-path illustration numerical checks passed.")
    else:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        (OUTPUT / "summary.json").write_text(
            json.dumps(report, indent=2, allow_nan=False) + "\n"
        )


if __name__ == "__main__":
    main()
