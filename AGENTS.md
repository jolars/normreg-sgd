# Repository Guidelines

## Project Structure & Module Organization

This research repository studies feature normalization under finite training
budgets.

- `paper/` contains `main.tex`, the bibliography, and vendored AISTATS styles.
- `experiments/<name>/` contains each experiment's configuration, runner, and
  summary generator. Shared numerical routines live in `experiments/common/`.
- `checks/` contains mathematical, numerical, and saved-result checks.
- `scripts/figures/` contains editable manuscript plots and shared styling in
  `style.py`.
- `lean/NormReg/` contains formal proofs and axiom audits.
- `data/mushroom/` stores source data; `results/<experiment>/` stores numerical
  arrays, settings, and summaries. Generated figures go in root `figures/`,
  LaTeX build files go in ignored `build/`, and the generated diagnostic table
  lives in `paper/generated/`.

## Build, Test, and Development Commands

Run commands from the repository root inside `devenv shell`, which supplies
Task, Python, LaTeX, Lean, and validation tools. Run `task --list` to list
tasks.

- `task paper`: regenerate required figures and compile `build/main.pdf`.
- `task figures`: regenerate manuscript plots from saved results.
- `task experiment:<name>`: run and summarize one experiment. Mushroom and
  synthetic data support `-- --config NAME`, plus separate `:run` and
  `:summarize` tasks.
- `task check:results`: reconstruct saved losses, selections, and summaries.
- `task check:exact-risk-results`: check the large exact-risk outputs after
  explicitly generating them with `task experiment:exact-risk`.
- `task check`: run formatting, configuration, numerical checks, and the paper
  build, matching CI.
- `task check-python`: check Python formatting and lint with Ruff.
- `task prepare-lean`, then `task check-lean`: fetch Mathlib caches and build
  proofs; these checks run separately from `task check`.
- `task format`: format Markdown, Nix, and Python sources.

## Coding Style & Naming Conventions

Use four-space Python indentation, an 88-character line limit, `snake_case`
functions and modules, and `UPPER_CASE` constants. Ruff checks errors and import
ordering. Use `run.py` and `summarize.py` for experiment entry points and
`plot_*.py` for figures. Panache formats Markdown at 80 columns; nixfmt formats
Nix. Preserve manuscript notation and explain why in code comments using
complete sentences.

## Testing Guidelines

Tests are executable numerical checks in `checks/`, using assertions and
NumPy/SciPy comparisons rather than a dedicated test framework. No coverage
percentage is configured. For bug fixes, add a failing regression check before
changing behavior. Run the relevant check, such as
`task check:predictive-theorem`, then broader validation appropriate to the
change.

## Reproducibility

Keep seeds, experiment settings, raw data, reported results, and numerical
failures. Use Git history to record changes; do not add checksum enforcement,
locked declarations, or dependencies on historical Git revisions. Add explicit
`experiment:<name>` tasks to `Taskfile.yml`. Building the paper or its figures
must never launch experiments. Keep summarizing and plotting independent of
training. Run Python modules from the root with
`python -m experiments.<name>.run` or `python -m checks.<name>`.

## Commit & Pull Request Guidelines

Use Conventional Commits, ASCII messages, and short titles, ideally under 60
characters. Link issues with `Fixes #N`, `Closes #N`, or `Refs #N` as
appropriate. Pull requests should explain the change, identify affected
scientific claims or artifacts, and report validation commands. Include figure
previews when changing plots.

## Paper Style and Format

- Maximum length for the paper is 8 pages, but don't force the draft into that
  limit. Instead raise this as an issue to the user.
