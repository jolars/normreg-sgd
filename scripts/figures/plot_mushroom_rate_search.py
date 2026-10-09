"""Compare five- and 17-rate searches in the manuscript supplement."""

import json

from style import (
    METHOD_LABELS,
    METHOD_STYLES,
    OUTPUT,
    PAPER_WIDTH,
    ROOT,
    SEARCH_STYLES,
    apply_style,
    plt,
    save,
)

SCALES = ("none", "sd", "damped")


def plot(summary):
    apply_style()
    directory = OUTPUT / "mushroom-rate-search"
    case, objective = 1, 0
    fig, axes = plt.subplots(2, 3, figsize=(PAPER_WIDTH, 5.3), constrained_layout=True)
    metrics = (
        "aggregate",
        "rare",
        "green_coefficient",
        "centered_intercept",
        "green_contribution",
        "other_contribution",
    )
    for ax, metric in zip(axes.flat, metrics, strict=True):
        for scale in SCALES:
            method = METHOD_STYLES[scale]
            for search in ("original", "expanded"):
                search_style = SEARCH_STYLES[search]
                values = [
                    p
                    for p in summary["selected_paths"]
                    if p["case"] == case
                    and p["objective"] == objective
                    and p["arm"] == "centered_fitted"
                    and p["scale"] == scale
                    and p["search"] == search
                ]
                ax.plot(
                    [p["observations"] for p in values],
                    [p[metric]["mean"] for p in values],
                    **(method | search_style),
                    markevery=max(1, len(values) // 5),
                    markersize=3,
                    label=f"{METHOD_LABELS[scale]}, "
                    f"{5 if search == 'original' else 17} rates",
                )
                endpoint = next(
                    s
                    for s in summary["selections"]
                    if s["case"] == case
                    and s["objective"] == objective
                    and s["arm"] == "centered_fitted"
                    and s["scale"] == scale
                    and s["cap"] == 8192
                    and s["rule"] == "joint"
                    and s["search"] == search
                    and s["stratum"] == "all"
                )
                ax.plot(
                    10496,
                    endpoint[metric]["mean"],
                    color=method["color"],
                    marker=method["marker"],
                    fillstyle=search_style["fillstyle"],
                    linestyle="none",
                    markersize=5,
                )
        ax.axvline(9216, linestyle="--", color="0.7", linewidth=0.8)
        ax.set_xticks(
            (0, 2048, 4096, 8192, 10496),
            ("0", "2048", "4096", "8192", "Selected"),
        )
        ax.set_xlabel("Processed observations M")
        ax.set_title(metric.replace("_", " ").capitalize(), wrap=True)
        ax.tick_params(axis="x", labelrotation=30)
        ax.set_yscale(
            "log" if metric in ("aggregate", "rare") else "symlog",
            **({} if metric in ("aggregate", "rare") else {"linthresh": 0.1}),
        )
        ax.grid(alpha=0.2)
    axes[0, 0].legend(fontsize=7)
    fig.suptitle(
        f"n={summary['cases'][case]['n']}, "
        f"{'rare' if objective else 'aggregate'} validation: "
        "trajectories selected at cap 8192\nMeans across 32 partitions; "
        "continuation after each selected stop is descriptive"
    )
    save(
        fig,
        directory,
        f"paths-n{summary['cases'][case]['n']}-{'rare' if objective else 'aggregate'}",
    )


if __name__ == "__main__":
    plot(json.loads((ROOT / "results/mushroom/rates17/summary.json").read_text()))
