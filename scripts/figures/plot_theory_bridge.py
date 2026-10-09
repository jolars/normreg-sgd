"""Plot the saved controlled interventions and validation comparisons."""

import json

import numpy as np
from style import (
    ARM_STYLES,
    BUDGET_STYLES,
    METHOD_STYLES,
    OUTPUT,
    PAPER_WIDTH,
    ROOT,
    apply_style,
    plt,
    save,
)

LABELS = (
    "Fresh observations",
    "Fresh + fitted intercept",
    "Reuse observations",
    "Reuse + estimated scales",
    "Reuse + fitted intercept",
    "Reuse + scales + intercept",
    "Also estimate centering",
    "Also initialize at sample mean",
)


def select(report, q, signal, arm, policy):
    return sorted(
        (
            row
            for row in report["rows"]
            if row["q"] == q
            and row["signal"] == signal
            and row["arm"] == arm
            and row["policy"] == policy
        ),
        key=lambda row: row["cap"],
    )


def controlled(report):
    figure, axes = plt.subplots(
        2, 2, figsize=(PAPER_WIDTH, 5.2), sharex="col", sharey=True
    )
    figure.subplots_adjust(
        left=0.32, right=0.94, bottom=0.14, top=0.94, hspace=0.22, wspace=0.14
    )
    for row, q in enumerate((0.02, 0.005)):
        for col, signal in enumerate(("rare", "common")):
            axis = axes[row, col]
            for budget, offset in enumerate((-0.22, 0, 0.22)):
                style = BUDGET_STYLES[2**budget]
                values = [
                    select(report, q, signal, arm, "calibrated")[budget]["gap"]
                    for arm in report["arms"]
                ]
                axis.errorbar(
                    [v["mean"] for v in values],
                    np.arange(len(values)) + offset,
                    xerr=[2 * v["mcse"] for v in values],
                    marker=style["marker"],
                    linestyle="none",
                    markersize=3.2,
                    color=style["color"],
                    capsize=2,
                    label=rf"$Mq\approx {2**budget}$",
                )
            axis.axvline(0, color="0.35", linewidth=0.8, linestyle="--")
            axis.set(
                title=f"{signal.capitalize()} signal" if row == 0 else "",
                yticks=np.arange(8),
                yticklabels=LABELS,
                ylim=(7.65, -0.65),
            )
            axis.grid(axis="y", color="0.92", linewidth=0.5)
            axis.set_axisbelow(True)
            axis.set_xticks(
                [-0.12, -0.08, -0.04, 0] if col == 0 else [0, 0.04, 0.08, 0.12]
            )
        axes[row, 1].text(
            1.08,
            0.5,
            rf"$q={q:g}$",
            transform=axes[row, 1].transAxes,
            rotation=270,
            ha="center",
            va="center",
            fontsize=plt.rcParams["axes.labelsize"],
        )
    figure.supxlabel("SD minus unscaled rare risk (negative favors SD)", y=0.075)
    figure.legend(
        *axes[0, 0].get_legend_handles_labels(),
        loc="lower center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.65, 0.005),
    )
    save(figure, OUTPUT / "theory-bridge", "controlled-gaps")


def validation(report):
    figure, axes = plt.subplots(2, 2, figsize=(PAPER_WIDTH, 5.2), sharex=True)
    figure.subplots_adjust(
        left=0.11, right=0.94, bottom=0.21, top=0.94, hspace=0.25, wspace=0.16
    )
    policies = ("calibrated", "validation_128", "validation_512", "validation_2048")
    arms = ("fresh", "reuse", "reuse_mean_initialized")
    names = ("Fresh", "Reuse only", "Reuse + all preprocessing/intercept changes")
    for row, q in enumerate((0.02, 0.005)):
        for col, signal in enumerate(("rare", "common")):
            axis = axes[row, col]
            bounds = [0.0]
            for arm, name in zip(arms, names, strict=True):
                values = [
                    select(report, q, signal, arm, policy)[-1]["gap"]
                    for policy in policies
                ]
                axis.errorbar(
                    np.arange(4),
                    [v["mean"] for v in values],
                    yerr=[2 * v["mcse"] for v in values],
                    **ARM_STYLES[arm],
                    label=name,
                    markersize=3.5,
                    capsize=2,
                )
                bounds.extend(v["mean"] - 2 * v["mcse"] for v in values)
                bounds.extend(v["mean"] + 2 * v["mcse"] for v in values)
            axis.axhline(0, color="0.35", linestyle="--", linewidth=0.8)
            axis.set_yscale("symlog", linthresh=0.05)
            transform = axis.yaxis.get_transform()
            lower, upper = transform.transform([min(bounds), max(bounds)])
            margin = 0.08 * (upper - lower)
            lower, upper = transform.inverted().transform(
                [lower - margin, upper + margin]
            )
            axis.set_ylim(lower, upper)
            ticks = [
                v for v in (-0.1, -0.05, 0, 0.05, 0.1, 0.5, 1, 2) if lower <= v <= upper
            ]
            axis.set_yticks(ticks, [f"{v:g}" for v in ticks])
            axis.set(
                title=f"{signal.capitalize()} signal" if row == 0 else "",
                xticks=np.arange(4),
                xticklabels=("Calibrated", "128", "512", "2048"),
            )
            axis.grid(axis="y", color="0.92", linewidth=0.5)
            axis.set_axisbelow(True)
        axes[row, 1].text(
            1.08,
            0.5,
            rf"$q={q:g}$",
            transform=axes[row, 1].transAxes,
            rotation=270,
            ha="center",
            va="center",
            fontsize=plt.rcParams["axes.labelsize"],
        )
    figure.supylabel(
        "SD minus unscaled rare risk\n(negative favors SD; symmetric log scale)",
        x=0.015,
    )
    figure.supxlabel("Selection policy / validation sample size", y=0.13)
    figure.text(
        0.54, 0.09, r"Linear for $|\mathrm{gap}|\leq 0.05$", ha="center", fontsize=7
    )
    figure.legend(
        *axes[0, 0].get_legend_handles_labels(),
        loc="lower center",
        frameon=False,
        ncol=2,
        bbox_to_anchor=(0.52, 0.005),
    )
    save(figure, OUTPUT / "theory-bridge", "validation-gaps")


def selection_gains():
    figure, axes = plt.subplots(2, 2, figsize=(PAPER_WIDTH, 4.5), sharey=True)
    with np.load(ROOT / "results/theory-bridge/selection-gains.npz") as archive:
        gains = archive["q0_gain"][:, -1, :, :, 0]
    for arm, title in enumerate(LABELS[:2]):
        for column, policy in enumerate((0, 3)):
            axis = axes[arm, column]
            for scaling, name in enumerate(("none", "sd")):
                values = np.sort(gains[:, arm, scaling, policy])
                style = METHOD_STYLES[name]
                axis.step(
                    values,
                    np.arange(1, len(values) + 1) / len(values),
                    where="post",
                    color=style["color"],
                    linestyle=style["linestyle"],
                    label="U" if scaling == 0 else "SD",
                )
            axis.axvline(0, color="0.35", linewidth=0.8, linestyle="--")
            axis.set_xscale("symlog", linthresh=0.05)
            axis.set_xlim(-0.5, 2.5)
            axis.set_ylim(0, 1)
            axis.set_xticks(
                [-0.5, -0.1, 0, 0.1, 0.5, 2], ["-.5", "-.1", "0", ".1", ".5", "2"]
            )
            axis.set_title(
                ("Exact risk" if policy == 0 else "Validation (2048)")
                if arm == 0
                else ""
            )
            axis.grid(axis="y", color="0.92", linewidth=0.5)
        axes[arm, 1].text(
            1.08,
            0.5,
            title,
            transform=axes[arm, 1].transAxes,
            rotation=270,
            ha="center",
            va="center",
            fontsize=plt.rcParams["axes.labelsize"],
        )
    figure.supylabel("Fraction of evaluation runs", x=0.015)
    figure.supxlabel(
        "Calibrated minus selected rare risk (symmetric log scale)", y=0.01
    )
    axes[0, 0].legend(frameon=False, loc="lower right")
    figure.tight_layout(rect=(0.025, 0.035, 0.94, 1))
    save(figure, OUTPUT / "theory-bridge", "selection-gains")


if __name__ == "__main__":
    report = json.loads((ROOT / "results/theory-bridge/summary.json").read_text())
    apply_style()
    controlled(report)
    validation(report)
    selection_gains()
