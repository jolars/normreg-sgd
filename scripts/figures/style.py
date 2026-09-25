"""Shared ALT typography and figure exports for the manuscript."""

import tomllib
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "figures"
PAPER_WIDTH = 6.0
SINGLE_PANEL_WIDTH = (PAPER_WIDTH - 0.2) / 2

with Path(__file__).with_name("palette.toml").open("rb") as source:
    PALETTE = tomllib.load(source)
COLORS = PALETTE["colors"]


def _styles(section):
    return {
        key: {**style, "color": COLORS[style["color"]]}
        for key, style in PALETTE[section].items()
    }


METHOD_STYLES = _styles("methods")
VALIDATION_STYLES = _styles("validation")
BUDGET_STYLES = {float(key): value for key, value in _styles("budgets").items()}
PREVALENCE_STYLES = {float(key): value for key, value in _styles("prevalences").items()}
ARM_STYLES = _styles("arms")
COMPONENT_STYLES = _styles("components")
CLIPPING_STYLES = _styles("clipping")
SEARCH_STYLES = PALETTE["searches"]
INTERCEPT_STYLES = PALETTE["intercepts"]
SAMPLE_SIZE_STYLES = {int(key): value for key, value in PALETTE["sample_sizes"].items()}
RISK_COLORMAP = PALETTE["defaults"]["risk_colormap"]
BAR_EDGE_COLOR = COLORS[PALETTE["defaults"]["bar_edgecolor"]]
METHOD_LABELS = {
    "none": "Unscaled",
    "sd": "Standardized",
    "damped": "Damped",
    "variance": "Variance",
}

# LaTeX renders text and math with the same font package as the manuscript.
RC_PARAMS = {
    "text.usetex": True,
    "text.latex.preamble": r"\usepackage[T1]{fontenc}\usepackage{times}",
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "font.sans-serif": ["Computer Modern Sans Serif"],
    "font.monospace": ["Computer Modern Typewriter"],
    "font.size": 9,
    "axes.labelsize": 9,
    "axes.titlesize": 10,
    "figure.titlesize": 11,
    "figure.labelsize": 9,
    "legend.fontsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.prop_cycle": plt.cycler(
        color=[COLORS[name] for name in PALETTE["defaults"]["cycle"]]
    ),
    "svg.fonttype": "path",
    "svg.hashsalt": "normreg-paper-figures",
    "savefig.dpi": 160,
}


def apply_style():
    """Apply the common defaults before creating any artists."""
    plt.rcParams.update(RC_PARAMS)


def save(figure, directory, name, *, tight=True):
    """Export PDF, SVG, and PNG files with portable fonts."""
    directory.mkdir(parents=True, exist_ok=True)
    for extension in ("pdf", "svg", "png"):
        metadata = {
            "pdf": {"CreationDate": None, "ModDate": None},
            "svg": {"Date": None},
            "png": {},
        }[extension]
        destination = directory / f"{name}.{extension}"
        figure.savefig(
            destination,
            metadata=metadata,
            bbox_inches="tight" if tight else None,
            pad_inches=0.02,
        )
        if extension == "svg":
            # Strip exporter whitespace so diffs remain readable when sharing SVGs.
            destination.write_text(
                "\n".join(
                    line.rstrip() for line in destination.read_text().splitlines()
                )
                + "\n"
            )
    plt.close(figure)
    print(f"Exported {directory.relative_to(ROOT) / name} (PDF, SVG, PNG).")
