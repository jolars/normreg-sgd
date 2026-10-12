"""Check that the active Python environment can render LaTeX figure text."""

import tempfile
from pathlib import Path

import numpy as np

from scripts.figures.style import ROOT, apply_style, plt, save


def check_rendering():
    apply_style()
    with tempfile.TemporaryDirectory(prefix=".figure-render-", dir=ROOT) as directory:
        output = Path(directory)
        figure, axis = plt.subplots(figsize=(2, 1.5))
        axis.plot(np.array([0, 1]), np.array([0, 1]))
        axis.set(xlabel=r"$\alpha$", ylabel="Risk", title="Rendering check")
        save(figure, output, "rendering")
        for extension in ("pdf", "svg", "png"):
            assert (output / f"rendering.{extension}").stat().st_size > 0
    print("LaTeX figure rendering passed for PDF, SVG, and PNG.")


if __name__ == "__main__":
    check_rendering()
