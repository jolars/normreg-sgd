"""Export robustness figures from retained endpoints and oracle selection IDs."""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from plot_joint_interactions import save
from robustness_spec import OUTPUT, ROOT, sha256, write_json

COLORS = {"U": "#0072B2", "S": "#D55E00"}


def plot(output):
    spec = json.loads((output / "specification.json").read_text())
    summary = json.loads((output / "summary.json").read_text())
    assert sha256(output / "paths.npz") == spec["paths_sha256"]
    with np.load(output / "paths.npz", allow_pickle=False) as archive:
        data = {
            key: archive[key]
            for key in (
                "k",
                "M",
                "mean",
                "risks",
                "risk_parts",
                "second",
                "failure",
                "configuration",
            )
        }
    configurations = spec["configurations"]
    rows = [
        dict(zip(summary["envelopes"]["fields"], row, strict=True))
        for row in summary["envelopes"]["rows"]
    ]
    directory = output / "figures"

    def export(figure, name):
        preview = ROOT / "build/robustness"
        preview.mkdir(parents=True, exist_ok=True)
        figure.savefig(preview / f"{name}.png", dpi=120)
        save(figure, directory, name)

    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "svg.fonttype": "none",
            "svg.hashsalt": "normalization-robustness-v1",
            "pdf.fonttype": 42,
            "figure.constrained_layout.use": True,
        }
    )

    def law_id(q, ell, signal, sigma2):
        return next(
            law["id"]
            for law in spec["laws"]
            if law["q"] == q
            and law["ell"] == ell
            and law["signal"] == signal
            and law["sigma2"] == sigma2
        )

    c1 = law_id(0.02, 0, [1, 1], 3)
    c2 = law_id(0.02, 1, [2, 1], 4)

    def endpoints(law, scaling, batch, h):
        c = next(
            c
            for c in configurations
            if (c["law"], c["scaling"], c["batch"], c["h"]) == (law, scaling, batch, h)
        )
        ids = np.arange(c["offset"], c["offset"] + c["size"])
        assert np.all(data["failure"][ids] == 0), (
            "Label invalid anchors before plotting."
        )
        return ids[data["k"][ids] > 0]

    fig, axes = plt.subplots(2, 3, figsize=(12, 7), sharex=True, sharey="row")
    panels = [
        (c1, 1, 0.002, "C1, B = 1"),
        (c1, 10, 0.002, "C1, B = 10"),
        (c2, 1, 0.01, "C2, B = 1"),
    ]
    for col, (law, batch, h, title) in enumerate(panels):
        for scaling in ("U", "S"):
            ids = endpoints(law, scaling, batch, h)
            for objective in (0, 1):
                ax = axes[objective, col]
                ax.plot(
                    data["M"][ids],
                    data["risks"][ids, objective],
                    color=COLORS[scaling],
                    label=scaling,
                )
                ax.set_xscale("log")
                ax.set_yscale("log")
                ax.grid(alpha=0.2)
                ax.set_xlabel("Fresh observations M = kB")
                ax.set_ylabel(
                    ("Aggregate", "Rare-presence")[objective] + " excess risk"
                )
                ax.set_title(title)
        axes[0, col].legend()
    fig.suptitle(
        "Fixed pairs before adjustment: common h = 0.002 (C1), 0.01 (C2)\n"
        "All plotted anchors are stable and finite; no clipping"
    )
    export(fig, "fixed-risks")

    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True, sharey=True)
    for col, (law, h, title) in enumerate(((c1, 0.002, "C1"), (c2, 0.01, "C2"))):
        for row, scaling in enumerate(("U", "S")):
            ids = endpoints(law, scaling, 1, h)
            for part, label in enumerate(
                ("Squared bias", "Update variance", "Observation noise")
            ):
                axes[row, col].plot(
                    data["k"][ids], data["risk_parts"][ids, 1, part], label=label
                )
            axes[row, col].set(
                xscale="log",
                xlabel="Updates k = observations M (B = 1)",
                ylabel="Rare-risk contribution",
                title=f"{title}, {scaling}",
            )
            axes[row, col].grid(alpha=0.2)
    axes[0, 0].legend()
    fig.suptitle("Fixed-pair rare-risk decomposition; no clipping")
    export(fig, "fixed-decomposition")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)
    for ax, (law, h, title) in zip(
        axes, ((c1, 0.002, "C1: independent"), (c2, 0.01, "C2: nested")), strict=True
    ):
        for scaling in ("U", "S"):
            ids = endpoints(law, scaling, 1, h)
            for coordinate, linestyle in enumerate(("-", "--")):
                ax.plot(
                    data["k"][ids],
                    data["mean"][ids, coordinate],
                    linestyle=linestyle,
                    color=COLORS[scaling],
                    label=f"{scaling}, {('common', 'rare')[coordinate]}",
                )
        ax.set(
            xscale="log",
            xlabel="Updates k = observations M (B = 1)",
            ylabel="Original-scale mean coefficient",
            title=title,
        )
        ax.grid(alpha=0.2)
        ax.legend()
    fig.suptitle("Common learning is matched only for independent features")
    export(fig, "coefficient-means")

    fig, axes = plt.subplots(2, 3, figsize=(12, 7), sharex=True, sharey="col")
    for col, (law, objective, title) in enumerate(
        (
            (c1, "rare", "C1 rare risk"),
            (c2, "aggregate", "C2 aggregate risk"),
            (c2, "rare", "C2 rare risk"),
        )
    ):
        for row, adjustment in enumerate(("rate", "rate_stop")):
            selected = [
                r
                for r in rows
                if r["law"] == law
                and r["rate_grid"] == r["stop_grid"] == "coarse"
                and r["budget"] == "observations"
                and r["batch"] == 1
                and r["eligibility"] == "stable"
                and r["adjustment"] == adjustment
                and r["objective"] == objective
                and r["cap"] > 0
            ]
            assert all(r["sign"] != "incomplete" for r in selected)
            for scaling in ("U", "S"):
                axes[row, col].plot(
                    [r["cap"] for r in selected],
                    [r[f"{scaling}_minimum"] for r in selected],
                    color=COLORS[scaling],
                    marker="o",
                    markersize=3,
                    label=scaling,
                )
            axes[row, col].set(
                xscale="log",
                yscale="log",
                xlabel="Observation budget" if row == 0 else "Observation cap",
                ylabel="Oracle excess risk",
                title=f"{title}: {('rate', 'rate and stopping')[row]}",
            )
            axes[row, col].grid(alpha=0.2)
            axes[row, col].legend()
    fig.suptitle(
        "Declared coarse-grid adjustments, B = 1, stable steps plus zero predictor\n"
        "Each objective selects its own trained pair; "
        "consumed observations are retained in the archive"
    )
    export(fig, "adjusted-risks")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, adjustment in zip(axes, ("rate", "rate_stop"), strict=True):
        labels, changed, totals = [], [], []
        for resolution in (("fine", "coarse"), ("coarse", "fine"), ("fine", "fine")):
            comparisons = [
                (rows[a], rows[b], change)
                for a, b, change in summary["resolution"]["rows"]
                if rows[b]["adjustment"] == adjustment
                and rows[b]["eligibility"] == "stable"
                and (rows[b]["rate_grid"], rows[b]["stop_grid"]) == resolution
            ]
            labels.append("/".join(resolution))
            changed.append(sum(c[2] for c in comparisons))
            totals.append(len(comparisons))
        ax.bar(labels, changed, color="#009E73")
        for index, (count, total) in enumerate(zip(changed, totals, strict=True)):
            ax.annotate(
                f"{count}/{total}",
                (index, count),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                fontsize=9,
            )
        ax.set(
            xlabel="Rate / stopping grid",
            ylabel="Changed contrast classifications",
            title=adjustment.replace("_", " + "),
        )
        ax.margins(y=0.2)
    fig.suptitle(
        "Resolution sensitivity on the 16 declared laws, at shared coarse caps\n"
        "Stable envelopes; both objectives and budget conventions; "
        "pooled batches only at common observations"
    )
    export(fig, "resolution-sensitivity")

    pairs = []
    ui = endpoints(c2, "U", 1, 0.01)
    si = endpoints(c2, "S", 1, 0.01)
    pairs.append(
        (
            "Fixed h = .01",
            int(ui[data["k"][ui] == 100][0]),
            int(si[data["k"][si] == 100][0]),
        )
    )
    for objective in ("aggregate", "rare"):
        row = next(
            r
            for r in rows
            if r["law"] == c2
            and r["rate_grid"] == r["stop_grid"] == "coarse"
            and r["budget"] == "observations"
            and r["cap"] == 100
            and r["batch"] == 1
            and r["eligibility"] == "stable"
            and r["adjustment"] == "rate"
            and r["objective"] == objective
        )
        pairs.append(
            (f"{objective.capitalize()}-selected", row["U_endpoint"], row["S_endpoint"])
        )
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for objective, ax in enumerate(axes):
        w = np.asarray(spec["laws"][c2]["gram" if objective == 0 else "rare_second"])
        for index, (label, ui, si) in enumerate(pairs):
            v = data["second"][si] - data["second"][ui]
            components = [
                w[0, 0] * v[0, 0] / 2,
                w[0, 1] * v[0, 1],
                w[1, 1] * v[1, 1] / 2,
            ]
            for part, component in enumerate(components):
                ax.bar(
                    index + (part - 1) * 0.22,
                    component,
                    width=0.22,
                    color=("#0072B2", "#D55E00", "#009E73")[part],
                    label=("Common MSE", "Cross moment", "Rare MSE")[part]
                    if index == 0
                    else None,
                )
            ax.plot(index, sum(components), "k_", markersize=14)
        ax.axhline(0, color=".5", linewidth=0.7)
        ax.set_xticks(range(3), [p[0] for p in pairs])
        ax.set(
            ylabel="S minus U risk contribution",
            title=("Aggregate", "Rare-presence")[objective],
        )
        ax.legend(fontsize=8)
    fig.suptitle(
        "C2 at M = k = 100, B = 1: fixed and coarse rate-selected pairs\n"
        "Black marks show the total contrast; "
        "each pair is cross-evaluated on both objectives"
    )
    export(fig, "c2-cross-moment")
    manifest = {
        str(p.relative_to(output)): sha256(p) for p in sorted(directory.glob("*"))
    }
    write_json(
        output / "figures.json",
        dict(summary_sha256=sha256(output / "summary.json"), sha256=manifest),
    )
    print(f"Exported {len(manifest)} SVG/PDF figure files.", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    plot(parser.parse_args().output)
