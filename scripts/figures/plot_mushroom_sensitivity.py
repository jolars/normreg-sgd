"""Plot the saved fixed-offset Mushroom sensitivity comparison."""

import json

from style import OUTPUT, ROOT, apply_style, plt, save


def plot(summary):
    apply_style()
    levels = [
        "sd",
        "damped_0.001",
        "damped_0.003",
        "damped_0.01",
        "damped_0.03",
        "damped_0.1",
    ]
    fig, axes = plt.subplots(2, 4, figsize=(14, 6), layout="constrained")
    for case in range(2):
        for objective in range(2):
            entries = {
                s["scale"]: s
                for s in summary["selections"]
                if s["case"] == case
                and s["objective"] == objective
                and s["cap"] == 8192
                and s["search"] == "expanded"
                and s["stratum"] == "all"
            }
            for j, risk in enumerate(("aggregate", "rare")):
                ax = axes[case, 2 * objective + j]
                ax.plot(
                    range(len(levels)),
                    [entries[s][risk]["mean"] for s in levels],
                    "o-",
                    label="Fixed damping",
                )
                ax.axhline(
                    entries["none"][risk]["mean"], color="gray", ls="--", label="None"
                )
                ax.axhline(
                    entries["variance"][risk]["mean"],
                    color="darkorange",
                    ls=":",
                    label="Variance",
                )
                ax.set_xticks(
                    range(len(levels)),
                    ["0 (SD)", ".001", ".003", ".01", ".03", ".1"],
                    rotation=45,
                )
                ax.set_yscale("log")
                ax.set_title(
                    f"n={summary['cases'][case]['n']}, "
                    f"{('aggregate', 'rare')[objective]} selection\n"
                    f"{risk.capitalize()} test loss"
                )
                ax.set_xlabel("Fixed damping offset")
                ax.grid(alpha=0.2)
    axes[0, 0].legend(fontsize=8)
    save(fig, OUTPUT / "mushroom-scaling-sensitivity", "sensitivity")


if __name__ == "__main__":
    plot(
        json.loads(
            (ROOT / "results/mushroom-scaling-sensitivity/summary.json").read_text()
        )
    )
