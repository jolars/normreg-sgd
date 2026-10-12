"""Plot the coefficient-path panel and the shared introduction legend."""

import json

import numpy as np
from style import (
    METHOD_STYLES,
    OUTPUT,
    PAPER_WIDTH,
    ROOT,
    SINGLE_PANEL_WIDTH,
    apply_style,
    plt,
    save,
)


def plot(report):
    apply_style()
    figure, axis = plt.subplots(figsize=(SINGLE_PANEL_WIDTH, 2.45))
    figure.subplots_adjust(left=0.18, right=0.97, bottom=0.25, top=0.97)
    ols = np.array(report["ols"])
    values = np.linspace(-0.08, 1.18, 250)
    xx, yy = np.meshgrid(values, values)
    gram = np.array(report["gram"])
    loss = (gram[0, 0] * (xx - ols[0]) ** 2 + gram[1, 1] * (yy - ols[1]) ** 2) / 2
    axis.contour(
        xx,
        yy,
        loss,
        levels=[0.0005, 0.002, 0.006, 0.015, 0.035, 0.075, 0.13],
        colors="0.85",
        linewidths=0.6,
    )
    stop = report["stop"]
    for scaling, (scale, method) in enumerate(
        zip(("none", "sd"), report["methods"], strict=True)
    ):
        path = np.array(method["path"])
        style = METHOD_STYLES[scale]
        color = style["color"]
        axis.plot(
            *path[stop:].T,
            color=color,
            linestyle=style["linestyle"],
            linewidth=1.2,
            alpha=0.4,
        )
        axis.plot(
            *path[: stop + 1].T,
            color=color,
            linestyle=style["linestyle"],
            linewidth=1.8,
            label=method["name"],
        )
        axis.scatter(
            *path[stop],
            s=32,
            color=color,
            marker=style["marker"],
            edgecolors="white",
            linewidths=0.5,
            zorder=5,
        )
        axis.annotate(
            rf"Stop: $k={stop}$",
            xy=path[stop],
            xytext=(0.5, 0.29 if scaling == 0 else 0.94),
            fontsize=9,
            color=color,
            arrowprops=dict(arrowstyle="-", color=color, lw=0.6),
        )
        axis.annotate(
            "",
            xy=path[7],
            xytext=path[4],
            arrowprops=dict(arrowstyle="->", color=color, lw=1.1),
        )
    axis.scatter(0, 0, s=16, color="0.2", zorder=5)
    axis.annotate("Start", xy=(0, 0), xytext=(0.06, -0.08), fontsize=9)
    axis.scatter(*ols, marker="*", s=80, color="0.15", zorder=6)
    axis.text(0.98, 1.055, "OLS", fontsize=9, ha="center")
    axis.set(
        xlim=(-0.06, 1.16),
        ylim=(-0.12, 1.18),
        xlabel=r"Common coefficient, $\beta_C$",
        ylabel=r"Rare coefficient, $\beta_R$",
        xticks=[0, 0.5, 1],
        yticks=[0, 0.5, 1],
    )
    handles, labels = axis.get_legend_handles_labels()
    # Equal canvases keep the axes aligned when LaTeX pairs the two panels.
    save(figure, OUTPUT / "coefficient-paths", "paths-to-ols", tight=False)
    legend = plt.figure(figsize=(PAPER_WIDTH, 0.25))
    legend.legend(
        handles,
        labels,
        loc="center",
        ncol=2,
        frameon=False,
        handlelength=2.2,
        columnspacing=1.2,
    )
    save(legend, OUTPUT / "coefficient-paths", "method-legend")


if __name__ == "__main__":
    plot(json.loads((ROOT / "results/coefficient-paths/summary.json").read_text()))
