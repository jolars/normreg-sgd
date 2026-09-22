"""Plot the saved practical-selection summary."""

import json

import numpy as np
from style import OUTPUT, PAPER_WIDTH, ROOT, apply_style, plt, save

SCALES = ("none", "sd", "damped")


def plot(summary):
    apply_style()
    fig, axes = plt.subplots(2, 2, figsize=(PAPER_WIDTH, 5), layout="constrained")
    for ax, case in zip(axes[0], (0, 2), strict=True):
        for scale, color in zip(("none", "sd"), ("#276678", "#c45c32"), strict=True):
            for arm, style in (("known", "--"), ("centered_fitted", "-")):
                rows = [
                    r
                    for r in summary["synthetic"]["curves"]
                    if r["case"] == case
                    and r["arm"] == arm
                    and r["scale"] == scale
                    and r["factor"] == 0.05
                    and r["batch"] == 16
                ]
                ax.plot(
                    [r["observations"] for r in rows],
                    [r["rare"]["mean"] for r in rows],
                    style,
                    color=color,
                    label=f"{scale}, {arm}",
                )
        ax.set(
            title=(
                f"Sampled {summary['synthetic']['cases'][case]['name']}:\n"
                "fixed rate and stopping"
            ),
            xlabel="Processed observations",
            ylabel="Rare excess half squared loss",
        )
        ax.set_xscale("symlog", linthresh=128)
        ax.legend(fontsize=7)
    for ax, objective in zip(axes[1], ("aggregate", "rare"), strict=True):
        for size, marker in ((0, "o"), (1, "s")):
            for selection, offset in ((0, -0.12), (1, 0.12)):
                rows = [
                    r
                    for r in summary["mushroom"]["selections"]
                    if r["case"] == size
                    and r["arm"] == "centered_fitted"
                    and r["cap"] == 8192
                    and r["rule"] == "joint"
                    and r["objective"] == selection
                    and r["stratum"] == "all"
                ]
                rows.sort(key=lambda r: SCALES.index(r["scale"]))
                ax.errorbar(
                    np.arange(3) + offset,
                    [r[objective]["mean"] for r in rows],
                    yerr=[r[objective]["mcse"] for r in rows],
                    fmt=marker,
                    linestyle="none",
                    capsize=3,
                    label=f"n={256 if size == 0 else 2048}, "
                    f"{'rare' if selection else 'aggregate'} selection",
                )
        ax.set(
            xticks=range(3),
            xticklabels=SCALES,
            title=f"Mushroom: {objective} test loss",
            ylabel="Half squared loss",
        )
        ax.legend(fontsize=7)
    save(fig, OUTPUT / "practical-selection", "practical-selection")


if __name__ == "__main__":
    plot(json.loads((ROOT / "results/practical-selection/summary.json").read_text()))
