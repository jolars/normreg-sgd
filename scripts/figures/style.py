"""Shared Latin Modern typography and figure exports for the manuscript."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "figures"
PAPER_WIDTH = 6.75

# LaTeX renders text and math with the same font package as the manuscript.
RC_PARAMS = {
    "text.usetex": True,
    "text.latex.preamble": r"\usepackage[T1]{fontenc}\usepackage{lmodern}",
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
    "svg.fonttype": "path",
    "svg.hashsalt": "normreg-paper-figures",
    "savefig.dpi": 160,
}


def apply_style():
    """Apply the common defaults before creating any artists."""
    plt.rcParams.update(RC_PARAMS)


def save(figure, directory, name):
    """Export embedded fonts in PDF, portable SVG paths, and a PNG preview."""
    directory.mkdir(parents=True, exist_ok=True)
    for extension in ("pdf", "svg", "png"):
        metadata = {
            "pdf": {"CreationDate": None, "ModDate": None},
            "svg": {"Date": None},
            "png": {},
        }[extension]
        destination = directory / f"{name}.{extension}"
        figure.savefig(destination, metadata=metadata)
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
