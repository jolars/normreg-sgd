"""Plot saved exploratory dimension comparisons without running experiments."""

import json

import matplotlib.pyplot as plt
import numpy as np
from style import (
    BUDGET_STYLES,
    OUTPUT,
    PAPER_WIDTH,
    PREVALENCE_STYLES,
    ROOT,
    apply_style,
    save,
)


def budget_slice(settings, gaps):
    fig, axes = plt.subplots(1, 2, figsize=(PAPER_WIDTH, 2.55), sharex=True)
    counts = settings["common_counts"]
    cap = settings["target_scaled_budgets"].index(2.0)
    for signal, ax in enumerate(axes):
        ax.axhline(0, linestyle="--", color="0.55", linewidth=0.7)
        for q in (0.02, 0.0001):
            qi = settings["prevalences"].index(q)
            label = r"$q=0.02$" if q == 0.02 else r"$q=10^{-4}$"
            ax.plot(
                counts,
                gaps[qi, cap, :, signal],
                **PREVALENCE_STYLES[q],
                markersize=3,
                label=label,
            )
        ax.set_title(settings["signal_names"][signal])
        ax.set_xscale("log", base=2)
        ax.set_xticks([1, 4, 16, 64], labels=[1, 4, 16, 64])
        ax.set_xlabel("Number of common features")
    axes[0].set_ylabel("SD minus unscaled rare risk\n(negative favors SD)")
    axes[0].legend(frameon=False)
    fig.tight_layout(pad=0.5)
    save(fig, OUTPUT / "common-block", "budget-slice")


def main():
    report = json.loads((ROOT / "results/common-block/summary.json").read_text())
    settings = report["settings"]
    counts = settings["common_counts"]
    gaps = np.array(report["sd_minus_unscaled"])
    apply_style()
    budget_slice(settings, gaps)
    fig, axes = plt.subplots(
        2, 3, figsize=(PAPER_WIDTH, 4.5), sharex=True, sharey="row"
    )
    for qi, q in enumerate(settings["prevalences"]):
        for signal in range(2):
            ax = axes[signal, qi]
            ax.axhline(0, linestyle="--", color="0.55", linewidth=0.7)
            for cap, target in enumerate(settings["target_scaled_budgets"]):
                ax.plot(
                    counts,
                    gaps[qi, cap, :, signal],
                    **BUDGET_STYLES[target],
                    markersize=3,
                    label=rf"$Mq(1-q)\approx {target:g}$",
                )
            ax.set_xscale("log", base=2)
            ax.set_xticks([1, 4, 16, 64], labels=[1, 4, 16, 64])
            if signal == 0:
                ax.set_title(rf"$q={q:g}$")
            if qi == len(settings["prevalences"]) - 1:
                ax.text(
                    1.08,
                    0.5,
                    settings["signal_names"][signal],
                    transform=ax.transAxes,
                    rotation=270,
                    ha="center",
                    va="center",
                    fontsize=plt.rcParams["axes.labelsize"],
                )
    fig.supylabel("SD minus unscaled risk\n(negative favors SD)", x=0.015)
    fig.supxlabel("Number of common features", y=0.015)
    axes[0, 0].legend(frameon=False)
    fig.tight_layout(pad=0.5, rect=(0.035, 0.035, 0.96, 1))
    save(fig, OUTPUT / "common-block", "dimension-gaps")


if __name__ == "__main__":
    main()
