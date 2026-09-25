"""Plot saved exploratory dimension comparisons without running experiments."""

import json

import matplotlib.pyplot as plt
import numpy as np
from style import OUTPUT, PAPER_WIDTH, ROOT, apply_style, save


def budget_slice(settings, gaps):
    fig, axes = plt.subplots(1, 2, figsize=(PAPER_WIDTH, 2.55), sharex=True)
    counts = settings["common_counts"]
    cap = settings["target_scaled_budgets"].index(2.0)
    for signal, ax in enumerate(axes):
        ax.axhline(0, color="0.55", linewidth=0.7)
        for q, color in ((0.02, "#0072B2"), (0.0001, "#009E73")):
            qi = settings["prevalences"].index(q)
            label = r"$q=0.02$" if q == 0.02 else r"$q=10^{-4}$"
            ax.plot(
                counts,
                gaps[qi, cap, :, signal],
                marker="o",
                markersize=3,
                color=color,
                label=label,
            )
        ax.set_title(settings["signal_names"][signal])
        ax.set_xscale("log", base=2)
        ax.set_xticks([1, 4, 16, 64], labels=[1, 4, 16, 64])
        ax.set_xlabel("Number of common features")
    axes[0].set_ylabel("SD minus unscaled rare risk")
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
    colors = ["#0072B2", "#009E73", "#D55E00"]
    for qi, q in enumerate(settings["prevalences"]):
        for signal in range(2):
            ax = axes[signal, qi]
            ax.axhline(0, color="0.55", linewidth=0.7)
            for cap, target in enumerate(settings["target_scaled_budgets"]):
                ax.plot(
                    counts,
                    gaps[qi, cap, :, signal],
                    marker="o",
                    markersize=3,
                    color=colors[cap],
                    label=rf"$Mq(1-q)\approx {target:g}$",
                )
            ax.set_xscale("log", base=2)
            ax.set_xticks([1, 4, 16, 64], labels=[1, 4, 16, 64])
            if signal == 0:
                ax.set_title(rf"$q={q:g}$")
            else:
                ax.set_xlabel("Number of common features")
            if qi == 0:
                ax.set_ylabel(
                    settings["signal_names"][signal] + "\nSD minus unscaled risk"
                )
    axes[0, 0].legend(frameon=False)
    fig.tight_layout(pad=0.5)
    save(fig, OUTPUT / "common-block", "dimension-gaps")


if __name__ == "__main__":
    main()
