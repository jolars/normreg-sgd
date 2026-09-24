# Manuscript figures

Edit the plotting scripts in this directory. All use `style.py` for Matplotlib's
`rcParams`, font sizes, and export settings. Text and equations render through
LaTeX with `lmodern`, matching the manuscript. Change `RC_PARAMS` to adjust the
shared typography. Set figure dimensions in each script; `PAPER_WIDTH` is the
manuscript's full text width in inches. `COLUMN_WIDTH` accounts for the gap
between columns and is used by the two single-column introductory figures.

Inside `devenv shell`, run:

```sh
task figures
```

This reads saved experiment summaries and moment archives, then writes PDF, SVG,
and PNG files under `figures/`. PDFs embed Latin Modern fonts, and SVGs contain
glyph outlines so their appearance does not depend on installed viewer fonts.
The environment includes the LaTeX packages and `dvipng` needed by [Matplotlib's
LaTeX renderer](https://matplotlib.org/stable/users/explain/text/usetex.html).

  | Script                         | Output directory under `figures/` |
  | ------------------------------ | --------------------------------- |
  | `plot_coefficient_paths.py`    | `coefficient-paths/`              |
  | `plot_signal_crossing.py`      | `signal-crossing/`                |
  | `plot_predictive_intro.py`     | `predictive-intro/`               |
  | `plot_signal_allocation.py`    | `signal-allocation/`              |
  | `plot_theory_bridge.py`        | `theory-bridge/`                  |
  | `plot_mushroom_final.py`       | `mushroom-final/`                 |
  | `plot_practical_selection.py`  | `practical-selection/`            |
  | `plot_mushroom_rate_search.py` | `mushroom-rate-search/`           |

Run a single generator while editing, for example:

```sh
python scripts/figures/plot_predictive_intro.py
```

Run `task figure:theory-bridge` to export the controlled study's
`figures/theory-bridge/controlled-gaps` and `validation-gaps` in all three
formats. It reads `results/theory-bridge/summary.json` and never trains models.
Both figures are also included in `task figures` and `task paper`.

Only figures included by `paper/main.tex` are generated. The Mushroom
rate-search script exports the $n = 2048$ paths under aggregate validation used
in the supplement.

`task paper` rebuilds its figures when the corresponding scripts, shared style,
Taskfile, environment configuration, or saved summaries change. Missing PDF,
SVG, or PNG exports also trigger a rebuild. `task paper-figures` performs that
step without compiling LaTeX.

Numerical results and summaries live in `results/<experiment>/`. These scripts
read saved summaries and write the figures used by the manuscript. They do not
train models or select new configurations. To change an analysis, run the
experiment's `:summarize` task before regenerating figures. Git preserves
earlier versions of plotting code and results.

The coefficient-path illustration reads a constructed full-gradient example from
`results/coefficient-paths/summary.json`. Regenerate it explicitly with
`task experiment:coefficient-paths`. The signal-crossing figure reads a single
budget and noise slice from the existing signal-allocation summary. Its simpler
axis labels describe the same squared-coefficient allocation as the full map.
