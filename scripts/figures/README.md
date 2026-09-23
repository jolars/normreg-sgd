# Manuscript figures

Edit the plotting scripts in this directory. All use `style.py` for Matplotlib's
`rcParams`, font sizes, and export settings. Text and equations render through
LaTeX with `lmodern`, matching the manuscript. Change `RC_PARAMS` to adjust the
shared typography. Set figure dimensions in each script; `PAPER_WIDTH` is the
manuscript's full text width in inches.

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
  | `plot_predictive_intro.py`     | `predictive-intro/`               |
  | `plot_signal_allocation.py`    | `signal-allocation/`              |
  | `plot_mushroom_final.py`       | `mushroom-final/`                 |
  | `plot_practical_selection.py`  | `practical-selection/`            |
  | `plot_mushroom_rate_search.py` | `mushroom-rate-search/`           |

Run a single generator while editing, for example:

```sh
python scripts/figures/plot_predictive_intro.py
```

Only figures included by `paper/main.tex` are generated. The Mushroom
rate-search script exports the $n = 2048$ paths under aggregate validation used
in the supplement.

`task paper` rebuilds its five figures when the corresponding scripts, shared
style, Taskfile, environment configuration, or saved summaries change. Missing
PDF, SVG, or PNG exports also trigger a rebuild. `task paper-figures` performs
that step without compiling LaTeX.

Numerical results and summaries live in `results/<experiment>/`. These scripts
read saved summaries and write the figures used by the manuscript. They do not
train models or select new configurations. To change an analysis, run the
experiment's `:summarize` task before regenerating figures. Git preserves
earlier versions of plotting code and results.
