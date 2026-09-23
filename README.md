# Feature normalization under finite training budgets

This repository contains the experiments, numerical checks, and
[manuscript](paper/main.tex) for the study. Run commands from the repository
root inside `devenv shell`.

```sh
task experiment:mushroom     # Run and summarize Mushroom comparisons.
task experiment:synthetic    # Run and summarize synthetic-data comparisons.
task experiment:exact-risk   # Compute exact risks and paired simulations.
task figures                # Plot saved results.
task paper                  # Generate figures and compile build/main.pdf.
task check                  # Check code, numerics, illustrations, and the paper.
```

## Running experiments

Each experiment has a directory in `experiments/` and a task named
`experiment:<name>`. Shared data loading, random streams, SGD updates, and
statistics live in `experiments/common/`. The Mushroom and synthetic experiments
run independently.

  | Experiment          | Purpose                                                     | Results                      |
  | ------------------- | ----------------------------------------------------------- | ---------------------------- |
  | `mushroom`          | Categorical scaling, rate searches, and damping sensitivity | `results/mushroom/`          |
  | `synthetic`         | Sampled training, estimated preprocessing, and selection    | `results/synthetic/`         |
  | `exact-risk`        | Exact moments, rate comparisons, and paired simulations     | `results/exact-risk/`        |
  | `predictive-intro`  | Finite-grid oracle illustration                             | `results/predictive-intro/`  |
  | `signal-allocation` | Intermediate signal-allocation illustration                 | `results/signal-allocation/` |
  | `diagnostics`       | Numerical discrepancies and prediction clipping             | `results/diagnostics/`       |
  | `precision`         | Decimal replay of selected synthetic paths                  | `results/synthetic/rates5/`  |

Mushroom supports `rates5`, `rates17`, `rates25`, and `damping`. Synthetic data
supports `rates5` and `rates25`. The default runs every configuration for that
experiment. Select one configuration with:

```sh
task experiment:mushroom -- --config rates17
```

Run or summarize separately when changing the analysis:

```sh
task experiment:mushroom:run -- --config rates17
task experiment:mushroom:summarize -- --config rates17
```

These tasks also work for synthetic data. Exact-risk calculations have separate
`:run` and `:summarize` tasks. The two illustrations compute their summaries in
one step. `task experiment:diagnostics` reconstructs discrepancies from saved
paths and updates the diagnostic tables in the manuscript. Run `task --list` to
see all tasks.

Experiments can take substantial time and replace the saved outputs for the
selected configuration. Summarizing reads those outputs without retraining.
Building figures or the paper never launches experiments. Saved summaries are
included so the manuscript can be built immediately. The two large exact-risk
files, `paths.npz` and `summary.json`, are ignored; regenerate them explicitly
with `task experiment:exact-risk` when needed.

## Editing experiments

Configurations are ordinary Python values. Mushroom's 17-factor grid is in
[experiments/mushroom/rates17.py](experiments/mushroom/rates17.py), and its
damping offsets are in
[experiments/mushroom/damping.py](experiments/mushroom/damping.py). The shared
25-factor comparison is in
[experiments/common/rates25.py](experiments/common/rates25.py). Data generation,
the five-factor grid, sample sizes, and seeds are in
[experiments/common/data.py](experiments/common/data.py).

To add an experiment, create `experiments/<name>/` with `__init__.py` and
`run.py`, add a `summarize.py` when useful, and register its task in
`Taskfile.yml`. Use `python -m experiments.<name>.run` from the repository root.
Save numerical outputs and settings under `results/<name>/`. New experiments can
reuse functions in `experiments/common/` without depending on another
experiment's command-line entry point.

Git records changes to code, settings, and reported results. There are no
checksum checks, locked declarations, or dependencies on old Git revisions.
Commit the code, settings, and reported results together when recording a paper
version. Seeds, candidate settings, selections, and numerical failures remain in
the saved results.

## Checks and figures

`checks/` contains executable numerical checks, including independent SGD
updates, moment identities, selection rules, and theorem certificates.
`task check` runs these checks and builds the paper without running full
experiments.

```sh
task check:results             # Reconstruct saved losses and selections.
task check:exact-risk-results  # Check the large exact-risk outputs, if generated.
```

Checks retain and report the known numerical discrepancies in extreme synthetic
paths. They do not certify those paths merely because structural checks pass.

Edit manuscript plots in [scripts/figures/](scripts/figures/README.md).
Generated PDF, SVG, and PNG files go in `figures/`; LaTeX output goes in
`build/`. The generated diagnostic table is
`paper/generated/review-diagnostics.tex`. Formal proofs live in `lean/` and are
checked separately with `task prepare-lean` and `task check-lean`.
