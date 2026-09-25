"""Plot the saved practical-selection summary."""

import json

import numpy as np
from style import (
    INTERCEPT_STYLES,
    METHOD_LABELS,
    METHOD_STYLES,
    OUTPUT,
    PAPER_WIDTH,
    ROOT,
    SAMPLE_SIZE_STYLES,
    VALIDATION_STYLES,
    apply_style,
    plt,
    save,
)

SCALES = ("none", "sd", "damped")


def plot(summary):
    apply_style()
    fig, axes = plt.subplots(2, 2, figsize=(PAPER_WIDTH, 5), layout="constrained")
    for ax, case in zip(axes[0], (0, 2), strict=True):
        for scale in ("none", "sd"):
            for arm, label in (
                ("known", "known intercept"),
                ("centered_fitted", "fitted intercept"),
            ):
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
                    **(METHOD_STYLES[scale] | INTERCEPT_STYLES[arm]),
                    markevery=max(1, len(rows) // 5),
                    markersize=3.5,
                    label=f"{METHOD_LABELS[scale]}, {label}",
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
        for size, n in enumerate((256, 2048)):
            for selection, name in enumerate(("aggregate", "rare")):
                offset = (2 * size + selection - 1.5) * 0.13
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
                    **SAMPLE_SIZE_STYLES[n],
                    color=VALIDATION_STYLES[name]["color"],
                    linestyle="none",
                    capsize=3,
                    label=f"n={n}, {name} selection",
                )
        ax.set(
            xticks=range(3),
            xticklabels=[METHOD_LABELS[scale] for scale in SCALES],
            title=f"Mushroom: {objective} test loss",
            ylabel="Half squared loss",
        )
        ax.legend(fontsize=7)
    save(fig, OUTPUT / "practical-selection", "practical-selection")


if __name__ == "__main__":
    plot(
        {
            label: json.loads(
                (ROOT / "results" / label / "rates5/summary.json").read_text()
            )
            for label in ("synthetic", "mushroom")
        }
    )
