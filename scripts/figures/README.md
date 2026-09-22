# Manuscript figures

Edit the plotting scripts in this directory. All seven use `style.py` for
Matplotlib's `rcParams`, font sizes, and export settings. Text and equations
render through LaTeX with `lmodern`, matching the manuscript. Change `RC_PARAMS`
to adjust the shared typography. Set figure dimensions in each script;
`PAPER_WIDTH` is the manuscript's full text width in inches.

Inside `devenv shell`, run:

```sh
make figures
```

This reads saved experiment summaries and moment archives, then writes PDF, SVG,
and PNG files under `build/figures/`. PDFs embed Latin Modern fonts, and SVGs
contain glyph outlines so their appearance does not depend on installed viewer
fonts. The environment includes the LaTeX packages and `dvipng` needed by
[Matplotlib's LaTeX
renderer](https://matplotlib.org/stable/users/explain/text/usetex.html).

  | Script                             | Output directory under `build/figures/` |
  | ---------------------------------- | --------------------------------------- |
  | `plot_predictive_intro.py`         | `predictive-intro/`                     |
  | `plot_joint_interactions.py`       | `joint-interactions/`                   |
  | `plot_normalization_robustness.py` | `normalization-robustness/`             |
  | `plot_practical_selection.py`      | `practical-selection/`                  |
  | `plot_mushroom_rate_search.py`     | `mushroom-rate-search/`                 |
  | `plot_mushroom_sensitivity.py`     | `mushroom-scaling-sensitivity/`         |
  | `plot_variance_scaling.py`         | `variance-scaling-followup/`            |

Run a single generator while editing, for example:

```sh
python scripts/figures/plot_predictive_intro.py
```

`make paper` rebuilds its three figures when the corresponding scripts, shared
style, environment configuration, or saved summaries change.
`make paper-figures` performs that step without compiling LaTeX.

The original plotting code embedded in `experiments/` remains an archival input
to the frozen studies and their hash checks. Their reproduction targets still
recreate the historical artifacts in `results/`. Make presentation changes here;
the manuscript loads the editable exports from `build/figures/`. These scripts
retain the plotted selections and diagnostics from the archived generators and
do not rerun training, tune rates, or rewrite numerical summaries.
