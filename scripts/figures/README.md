# Manuscript figures

Edit the plotting scripts in this directory. All use `style.py` for Matplotlib's
`rcParams`, font sizes, and export settings. Text and equations render through
LaTeX with `times`, matching the ALT template. Change `RC_PARAMS` to adjust the
shared typography. Set figure dimensions in each script; `PAPER_WIDTH` is the
manuscript's six-inch text width. `SINGLE_PANEL_WIDTH` leaves room for two
introductory panels and a gap between them. They share a legend in the
manuscript.

Edit [`palette.toml`](palette.toml) to change colors and their meanings across
all figures. The `[colors]` table defines the Okabe–Ito colors, neutral grays,
and samples from viridis and plasma. The remaining tables assign those named
colors, markers, and line styles to methods, validation objectives, budgets,
prevalences, experimental arms, risk components, and clipping treatments. For
example, change `blue = "#0072B2"` to replace that color everywhere, or change
`color = "blue"` under `[methods.none]` to another named color to change only
the unscaled method's assignment. Run `task figures` after editing; the build
tracks the configuration and regenerates every manuscript figure automatically.

The method mapping is unscaled/blue, standardized/vermilion, damped/green, and
variance scaling/reddish purple. Simple method curves also use distinct line
styles. When line styles encode another factor, method markers preserve the
distinction. Aggregate and rare validation use charcoal and reddish purple;
budget levels 1, 2, and 4 use viridis, from dark purple through teal to green.
Prevalence curves use plasma, from dark purple through pink to orange as
prevalence increases. The oracle comparison retains method colors in panel (a)
and uses prevalence colors in panels (b)–(d). Risk components use charcoal,
orange, and sky blue with solid fills and thin borders. Colors can recur across
these explicitly labeled contexts, while the blue–vermilion pair stays
associated with the main method comparison.

The `[defaults]` table controls the fallback color cycle, bar borders, and
continuous risk colormap. The heatmap uses `RdBu_r`, with zero centered between
negative values favoring U and positive values favoring SD. Choose a diverging
colormap when revisiting that setting. The `[searches]`, `[intercepts]`, and
`[sample_sizes]` tables configure the secondary visual distinctions. Plotting
scripts request these mappings explicitly through `style.py`; their numeric
groupings and drawing order remain independent of the palette configuration.

Inside `devenv shell`, run:

```sh
task figures
```

This reads saved experiment summaries and moment archives, then writes PDF, SVG,
and PNG files under `figures/`. By default, the shared exporter crops every
format to the figure's content with Matplotlib's `bbox_inches="tight"` and a
0.02-inch margin. The introductory panels use `tight=False` to preserve equal
canvas dimensions and align their axes in LaTeX. PDFs embed their fonts, and
SVGs contain glyph outlines so their appearance does not depend on installed
viewer fonts. The environment includes the LaTeX packages and `dvipng` needed by
[Matplotlib's LaTeX
renderer](https://matplotlib.org/stable/users/explain/text/usetex.html).

  | Script                        | Output directory under `figures/` |
  | ----------------------------- | --------------------------------- |
  | `plot_coefficient_paths.py`   | `coefficient-paths/`              |
  | `plot_signal_crossing.py`     | `signal-crossing/`                |
  | `plot_predictive_intro.py`    | `predictive-intro/`               |
  | `plot_tuned_decomposition.py` | `tuned-decomposition/`            |
  | `plot_oracle_finite.py`       | `oracle-finite/`                  |
  | `plot_common_block.py`        | `common-block/`                   |
  | `plot_theory_bridge.py`       | `theory-bridge/`                  |

Run a single generator while editing, for example:

```sh
python scripts/figures/plot_predictive_intro.py
```

Run `task figure:intro` to regenerate both introductory panels and their shared
legend. The coefficient-path script also exports
`coefficient-paths/method-legend`. The manuscript uses the ALT template's
`\subfigure` command to place the panels side by side and keep their references
separate.

The signal-allocation panel reads the saved nominal limiting risks in
`results/oracle-finite/summary.json`. It follows the corollary's path at fixed
initial subgroup risk, with noise variance one and rescaled budget two. It does
not use the earlier fixed-coefficient-norm experiment in `signal-allocation/`.

Run `task figure:theory-bridge` to export the controlled study's
`figures/theory-bridge/controlled-gaps` and `validation-gaps` in all three
formats. It reads `results/theory-bridge/summary.json` and never trains models.
Both figures are also included in `task figures` and `task paper`.

Run `task figure:common-block` to export the dimension comparison's
`figures/common-block/budget-slice` and `dimension-gaps` in all three formats.
The budget-slice figure shows both signal allocations at two prevalences and the
middle observation cap; the full figure shows all prevalences and budgets. Both
appear in the supplement. Both read `results/common-block/summary.json` and are
included in `task figures` and `task paper`.

Only figures included by `paper/main.tex` are generated by `task figures`. Plots
for the earlier investigations remain available through their scripts:

  | Script                         | Output directory under `figures/` |
  | ------------------------------ | --------------------------------- |
  | `plot_signal_allocation.py`    | `signal-allocation/`              |
  | `plot_mushroom_final.py`       | `mushroom-final/`                 |
  | `plot_practical_selection.py`  | `practical-selection/`            |
  | `plot_mushroom_rate_search.py` | `mushroom-rate-search/`           |

The Mushroom rate-search script exports the $n = 2048$ paths under aggregate
validation.

Run `task figure:oracle-finite` to export
`figures/oracle-finite/limit-comparison` for the manuscript supplement. It reads
`results/oracle-finite/summary.json` and compares finite-prevalence errors,
signal allocation, noise reversals, and budget effects with the limiting
predictions. It does not rerun searches and is included in `task figures` and
`task paper`.

`task paper` rebuilds its figures when the corresponding scripts, shared style,
palette configuration, Taskfile, environment configuration, or saved summaries
change. Missing PDF, SVG, or PNG exports also trigger a rebuild.
`task paper-figures` performs that step without compiling LaTeX.

Numerical results and summaries live in `results/<experiment>/`. These scripts
read saved summaries and write the figures used by the manuscript. The
introductory allocation panel also evaluates the proved limiting formulas. They
do not train models or select new configurations. To change an analysis, run the
experiment's `:summarize` task before regenerating figures. Git preserves
earlier versions of plotting code and results.

The coefficient-path illustration reads a constructed full-gradient example from
`results/coefficient-paths/summary.json`. Regenerate it explicitly with
`task experiment:coefficient-paths`. The signal-crossing figure holds
$s/4 + r = 1$ fixed at noise variance one and rescaled budget two. It evaluates
the limiting scalar solver at 401 allocations and overlays eight saved
allocations at each of two prevalences from
`results/oracle-finite/summary.json`. Run it from the repository root with
`python -m scripts.figures.plot_signal_crossing`. The earlier allocation map
uses the different constraint on $s + r$ and is outside the manuscript.

The tuned decomposition reads the selected rates, stops, and weighted risk
components from `results/predictive-intro/summary.json` at cap $M = 20{,}503$.
Regenerate those components with `task experiment:predictive-intro`. Each common
and rare coefficient contributes squared mean error, feature-sampling variation,
and observation noise, weighted by its contribution to rare-subgroup risk. The
plot uses the same choices as the risk curves and performs no new tuning.

The Mushroom figure reads paired SD-minus-U rare-loss contrasts from
`results/mushroom/rates25/mushroom-summary-c1.json` and clipping summaries from
`results/diagnostics/summary.json`. Its panels compare the five- and 25-rate
searches and the raw and clipped aggregate losses of predictors selected by rare
validation. Both show one MCSE across the same 32 partitions. The diagnostics
also retain paired changes between the search gaps. Regenerate the diagnostic
summaries with `python -m experiments.diagnostics.run`; this reads saved
predictors without training or selecting new candidates.
