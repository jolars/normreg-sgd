"""Plot the saved four-rule Mushroom comparisons."""

import json

from style import OUTPUT, ROOT, apply_style, plt, save

SCALES = ("none", "sd", "damped", "variance")


def plot(cases):
    apply_style()
    fig, axes = plt.subplots(2, 2, figsize=(8, 6), layout="constrained")
    colors = ("#444444", "#0072B2", "#009E73", "#D55E00")
    for case, result in enumerate(cases):
        for objective in range(2):
            ax = axes[case, objective]
            entries = {
                s["scale"]: s
                for s in result["selections"]
                if s["arm"] == "centered_fitted"
                and s["cap"] == 8192
                and s["search"] == "expanded"
                and s["objective"] == objective
                and s["stratum"] == "all"
            }
            for i, scale in enumerate(SCALES):
                ax.plot(
                    (0, 1),
                    [entries[scale][risk]["mean"] for risk in ("aggregate", "rare")],
                    "o-",
                    color=colors[i],
                    label="SD" if scale == "sd" else scale.capitalize(),
                )
            ax.set_xticks((0, 1), ("Aggregate loss", "Rare-group loss"))
            ax.set_yscale("log")
            ax.set_title(
                f"{result['label']}, {('aggregate', 'rare')[objective]} selection"
            )
            ax.grid(alpha=0.2)
    axes[0, 0].legend(fontsize=8)
    save(fig, OUTPUT / "variance-scaling-followup", "selected-risks")


if __name__ == "__main__":
    plot(
        [
            json.loads(path.read_text())
            for path in sorted(
                (ROOT / "results/variance-scaling-followup").glob(
                    "mushroom-summary-c*.json"
                )
            )
        ]
    )
