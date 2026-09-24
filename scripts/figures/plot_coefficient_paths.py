"""Plot saved full-gradient paths at manuscript column width."""

import json

import numpy as np
from style import COLUMN_WIDTH, OUTPUT, ROOT, apply_style, plt, save

COLORS = ("#0072B2", "#D55E00")
STYLES = ("--", "-")


def plot(report):
    apply_style()
    figure, axis = plt.subplots(figsize=(COLUMN_WIDTH, 2.75))
    figure.subplots_adjust(left=0.18, right=0.97, bottom=0.18, top=0.84)
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
    for scaling, method in enumerate(report["methods"]):
        path = np.array(method["path"])
        color = COLORS[scaling]
        axis.plot(
            *path[stop:].T,
            color=color,
            linestyle=STYLES[scaling],
            linewidth=1.2,
            alpha=0.4,
        )
        axis.plot(
            *path[: stop + 1].T,
            color=color,
            linestyle=STYLES[scaling],
            linewidth=1.8,
            label=method["name"],
        )
        axis.scatter(
            *path[stop], s=32, color=color, edgecolors="white", linewidths=0.5, zorder=5
        )
        axis.annotate(
            rf"Stop: $k={stop}$",
            xy=path[stop],
            xytext=(0.30, 0.29 if scaling == 0 else 0.94),
            fontsize=8,
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
    axis.annotate("Start", xy=(0, 0), xytext=(0.06, -0.08), fontsize=8)
    axis.scatter(*ols, marker="*", s=80, color="0.15", zorder=6)
    axis.text(0.98, 1.055, "OLS", fontsize=8, ha="center")
    axis.set(
        xlim=(-0.06, 1.16),
        ylim=(-0.12, 1.18),
        xlabel=r"Common coefficient, $\beta_C$",
        ylabel=r"Rare coefficient, $\beta_R$",
        xticks=[0, 0.5, 1],
        yticks=[0, 0.5, 1],
    )
    figure.legend(
        *axis.get_legend_handles_labels(),
        loc="upper center",
        ncol=2,
        bbox_to_anchor=(0.56, 1.0),
        frameon=False,
        handlelength=2.2,
        columnspacing=1.2,
    )
    save(figure, OUTPUT / "coefficient-paths", "paths-to-ols")


if __name__ == "__main__":
    plot(json.loads((ROOT / "results/coefficient-paths/summary.json").read_text()))
