"""Plot saved comparisons with the limiting formulas without new searches."""

import json

import matplotlib.pyplot as plt
import numpy as np
from style import (
    METHOD_STYLES,
    OUTPUT,
    PAPER_WIDTH,
    PREVALENCE_STYLES,
    ROOT,
    apply_style,
    save,
)


def main():
    report = json.loads((ROOT / "results/oracle-finite/summary.json").read_text())
    apply_style()
    fig, axes = plt.subplots(2, 2, figsize=(PAPER_WIDTH, 4.9))
    ax = axes[0, 0]
    q = [row["q"] for row in report["convergence"]]
    errors = np.array(
        [row["maximum_absolute_risk_error_U_S"] for row in report["convergence"]]
    )
    for scaling, key in enumerate(("none", "sd")):
        ax.loglog(
            q,
            errors[:, scaling],
            **METHOD_STYLES[key],
            markersize=3,
            label="Unscaled" if scaling == 0 else "Standardized",
        )
    ax.set_xlabel(r"Prevalence $q$")
    ax.set_ylabel("Largest absolute risk error")
    ax.set_title("(a) All 43 settings")
    ax.legend(frameon=False)

    prevalences = (0.02, 0.0002, 0.000002)
    specs = [
        (
            axes[0, 1],
            "allocation",
            "r",
            "finite_gap_S_minus_U",
            "nominal_limiting_gap_S_minus_U",
        ),
        (
            axes[1, 0],
            "noise",
            "noise",
            "finite_gap_S_minus_U",
            "nominal_limiting_gap_S_minus_U",
        ),
        (
            axes[1, 1],
            "budget",
            "tau",
            "finite_ratio_S_over_U",
            "nominal_limiting_ratio_S_over_U",
        ),
    ]
    for ax, group, xkey, ykey, limitkey in specs:
        for prevalence in prevalences:
            rows = sorted(
                [
                    row
                    for row in report["rows"]
                    if row["q"] == prevalence and row["group"] == group
                ],
                key=lambda row: row[xkey],
            )
            ax.plot(
                [row[xkey] for row in rows],
                [row[ykey] for row in rows],
                **PREVALENCE_STYLES[prevalence],
                markersize=3,
                linewidth=1,
                label=rf"$q={prevalence:g}$"
                if prevalence >= 1e-5
                else r"$q=2\times10^{-6}$",
            )
        ax.plot(
            [row[xkey] for row in rows],
            [row[limitkey] for row in rows],
            color="black",
            linestyle="--",
            linewidth=1,
            label=r"$q\to0$",
        )
        ax.axhline(1 if group == "budget" else 0, color="0.6", linewidth=0.6)
        if group != "budget":
            ax.set_ylabel("SD minus unscaled risk")
    axes[0, 1].set_xlabel(r"Rare signal fraction $r/(s/4+r)$")
    axes[0, 1].set_title(r"(b) Allocation, $s/4+r=1$, $\tau\approx2$")
    axes[0, 1].legend(frameon=False, fontsize=7)
    axes[1, 0].set_xscale("symlog", linthresh=0.1)
    axes[1, 0].set_xlim(-0.015, 150)
    axes[1, 0].set_xlabel(r"Noise variance $\nu$")
    axes[1, 0].set_title(r"(c) $s=0.1$, $r=1$, $\tau\approx2$")
    axes[1, 1].set_xscale("log")
    axes[1, 1].axhline(0.8, color="0.6", linestyle=":", linewidth=0.8)
    axes[1, 1].set_xlabel(r"Target rescaled budget $\tau$")
    axes[1, 1].set_ylabel("SD / unscaled risk")
    axes[1, 1].set_title(r"(d) $s=r=\nu=1$")
    fig.tight_layout(pad=0.6)
    save(fig, OUTPUT / "oracle-finite", "limit-comparison")


if __name__ == "__main__":
    main()
