"""Plot the retained exact joint-interaction paths."""

import hashlib
import json

import numpy as np
from matplotlib.lines import Line2D
from style import OUTPUT, ROOT, apply_style, plt, save

COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7"]


def selected(configurations, **criteria):
    return [
        i
        for i, c in enumerate(configurations)
        if all(c[key] == value for key, value in criteria.items())
    ]


def plot(source, directory):
    metadata = json.loads(source.read_text())
    archive = source.with_suffix(".npz")
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == metadata["arrays_sha256"]
    data = np.load(archive, allow_pickle=False)
    configurations = metadata["configurations"]
    counts = data["updates"]
    deltas = [0.0, 0.25, 0.5, 1.0]
    apply_style()

    plt.rcParams["figure.constrained_layout.use"] = True

    for model in metadata["models"]:
        dependence = model["dependence"]
        gram = np.asarray(model["rare_second"])
        figure, axes = plt.subplots(3, 4, figsize=(12, 8), sharex=True)
        colormap = plt.get_cmap("viridis").copy()
        colormap.set_bad("#bdbdbd")
        for row, batch in enumerate([1, 10, 100]):
            for column, delta in enumerate(deltas):
                indices = selected(
                    configurations, dependence=dependence, delta=delta, batch=batch
                )
                rates = np.array([configurations[i]["step"] for i in indices])
                with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
                    risk = 0.5 * np.einsum("akij,ij->ak", data["second"][indices], gram)
                    log_risk = np.log10(np.maximum(risk, 1e-4))
                log_risk[~data["valid"][indices] | ~np.isfinite(log_risk)] = np.nan
                axis = axes[row, column]
                artist = axis.pcolormesh(
                    counts[1:],
                    rates,
                    log_risk[:, 1:],
                    shading="nearest",
                    cmap=colormap,
                    vmin=-4,
                    vmax=1,
                    rasterized=True,
                )
                limit = configurations[indices[0]]["stability_step"]
                axis.axhline(limit, color="white", linestyle="--", linewidth=1.4)
                axis.set_xscale("log")
                axis.set_yscale("log")
                axis.set_ylim(rates[0], rates[-1])
                axis.set_xlim(1, 10000)
                axis.set_title(rf"$\delta={delta:g}$, $B={batch}$")
                if column == 0:
                    axis.set_ylabel(r"Actual learning rate $\eta$")
                if row == 2:
                    axis.set_xlabel(r"Stopping update $k$")
        figure.colorbar(
            artist, ax=axes, label=r"$\log_{10}$ rare-presence excess risk", shrink=0.85
        )
        figure.suptitle(
            f"{dependence.capitalize()} binary features: "
            "normalization, step, batch, and stopping\n"
            "q = 0.02; signal = (1, 1); noise variance = 1; fresh samples\n"
            "Dashed: moment-stability boundary. Colors saturate outside [0.0001, 10]; "
            "gray: invalid/nonfinite.",
            fontsize=12,
        )
        save(figure, directory, f"joint-risk-{dependence}")

    figure, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for axis, dependence in zip(axes, ["independent", "nested"], strict=True):
        for color, delta in zip(COLORS, deltas, strict=True):
            (index,) = selected(
                configurations,
                dependence=dependence,
                delta=delta,
                batch=1,
                rate_factor=0.002,
            )
            mean = data["bias"][index] + metadata["signal"]
            axis.plot(mean[:, 0], mean[:, 1], color=color, label=rf"$\delta={delta:g}$")
            for count, marker in [(100, "o"), (1000, "s")]:
                position = np.flatnonzero(counts == count)[0]
                axis.plot(*mean[position], marker=marker, color=color, markersize=5)
        axis.plot([0, 1], [0, 1], color="0.7", linestyle=":", linewidth=1)
        axis.set_title(dependence.capitalize())
        axis.set_xlabel("Mean common coefficient")
        axis.set_ylabel("Mean rare coefficient")
        axis.grid(alpha=0.15)
    handles, labels = axes[0].get_legend_handles_labels()
    figure.legend(handles, labels, loc="outside lower center", ncol=4)
    figure.suptitle(
        "Relative feature learning along the mean path\n"
        r"$\eta\lambda_{\max}(H)=0.002$; $k=0$ to 10,000; "
        "circles: k = 100; squares: k = 1,000",
        fontsize=12,
    )
    save(figure, directory, "joint-mean-paths")

    model = next(m for m in metadata["models"] if m["dependence"] == "independent")
    gram = np.asarray(model["rare_second"])
    figure, axes = plt.subplots(2, 2, figsize=(10, 7))
    for row, delta in enumerate([0.0, 0.5]):
        for color, batch in zip(COLORS, [1, 10, 100], strict=False):
            (index,) = selected(
                configurations,
                dependence="independent",
                delta=delta,
                batch=batch,
                rate_factor=0.002,
            )
            risk = 0.5 * np.einsum("kij,ij->k", data["second"][index], gram)
            bias = data["bias"][index]
            squared_bias = 0.5 * np.einsum("ki,ij,kj->k", bias, gram, bias)
            for column, x in enumerate([counts, counts * batch]):
                axis = axes[row, column]
                axis.plot(x[1:], risk[1:], color=color, label=f"B = {batch}")
                axis.plot(
                    x[1:], squared_bias[1:], color=color, linestyle=":", linewidth=1
                )
                axis.set_xscale("log")
                axis.set_yscale("log")
                axis.set_xlim(1 if column == 0 else 100, 10000)
                axis.set_ylim(0.0001, 0.8)
                axis.grid(alpha=0.15)
                axis.set_xlabel(
                    "Updates k" if column == 0 else "Processed observations M = kB"
                )
                axis.axvline(100 if column == 0 else 1000, color="0.6", linewidth=0.7)
        step = configurations[index]["step"]
        label = "No scaling" if delta == 0 else "Standard-deviation scaling"
        for axis in axes[row]:
            axis.set_title(rf"{label}; $\eta = {step:g}$")
            axis.set_ylabel("Rare-presence excess risk")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    handles.append(Line2D([], [], color="0.3", linestyle=":"))
    labels.append("Squared bias contribution")
    figure.legend(handles, labels, loc="outside lower center", ncol=4)
    figure.suptitle(
        "Batch comparisons depend on what is held fixed\n"
        "Independent features; matched common-coordinate mean rate; "
        "vertical lines mark the declared comparisons",
        fontsize=12,
    )
    save(figure, directory, "joint-batch-budgets")
    data.close()
    print(f"Exported four figures as PDF, SVG, and PNG to {directory}")


if __name__ == "__main__":
    plot(ROOT / "results/joint-interactions.json", OUTPUT / "joint-interactions")
