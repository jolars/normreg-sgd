"""Plot the saved Mushroom rate-search comparisons and selected paths."""

import json

import numpy as np
from style import OUTPUT, PAPER_WIDTH, ROOT, apply_style, plt, save

SCALES = ("none", "sd", "damped")


def plot(summary):
    apply_style()
    colors = ("#32688e", "#d66b24", "#31865a")
    directory = OUTPUT / "mushroom-rate-search"
    fig, axes = plt.subplots(4, 2, figsize=(10, 11), constrained_layout=True)
    for case in range(2):
        for objective in range(2):
            for metric_id, metric in enumerate(("aggregate", "rare")):
                ax = axes[2 * case + objective, metric_id]
                for si, (scale, color) in enumerate(zip(SCALES, colors, strict=True)):
                    values = [
                        next(
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
                        for search in ("original", "expanded", "expanded_stops")
                    ]
                    ax.errorbar(
                        np.arange(3) + (si - 1) * 0.1,
                        [v[metric]["mean"] for v in values],
                        yerr=[v[metric]["mcse"] for v in values],
                        color=color,
                        marker="o",
                        capsize=3,
                        label=scale,
                    )
                ax.set_xticks(range(3), ("Original", "Expanded", "+ stops"))
                ax.set_ylabel(f"{metric.capitalize()} test loss")
                ax.set_title(
                    f"n={summary['cases'][case]['n']}, "
                    f"{'rare' if objective else 'aggregate'} validation"
                )
                ax.set_yscale("log")
                ax.grid(alpha=0.2)
    axes[0, 0].legend()
    fig.suptitle(
        "Selected endpoints at cap M=8192: means and one MCSE\n"
        "Centered, fitted intercept; all 32 partitions per size"
    )
    save(fig, directory, "selected-risks")

    for case in range(2):
        for objective in range(2):
            fig, axes = plt.subplots(
                2, 3, figsize=(PAPER_WIDTH, 5.3), constrained_layout=True
            )
            metrics = (
                "aggregate",
                "rare",
                "green_coefficient",
                "centered_intercept",
                "green_contribution",
                "other_contribution",
            )
            for ax, metric in zip(axes.flat, metrics, strict=True):
                for scale, color in zip(SCALES, colors, strict=True):
                    for search, style in (("original", ":"), ("expanded", "-")):
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
                            color=color,
                            linestyle=style,
                            label=f"{scale}, {search}",
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
                        ax.scatter(
                            10496,
                            endpoint[metric]["mean"],
                            color=color,
                            marker="o" if search == "expanded" else "x",
                            s=26,
                        )
                ax.axvline(9216, color="0.7", linewidth=0.8)
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
                f"paths-n{summary['cases'][case]['n']}-"
                f"{'rare' if objective else 'aggregate'}",
            )


if __name__ == "__main__":
    plot(json.loads((ROOT / "results/mushroom-rate-search/summary.json").read_text()))
