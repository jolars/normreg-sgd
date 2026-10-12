# Repository Guidelines

## Project Structure & Module Organization

This research repository studies feature normalization under finite training
budgets.

- `paper/` contains `main.tex`, the bibliography, and the vendored ALT 2027
  template.
- `normreg/` contains shared numerical routines with explicit inputs and no
  dependencies on experiment settings or repository paths.
- `experiments/<name>/` contains each experiment's configuration, runner, and
  summary generator. Shared result utilities live in `experiments/common/`.
- `checks/` contains mathematical, numerical, and saved-result checks.
- `scripts/figures/` contains editable manuscript plots and shared styling in
  `style.py`.
- `lean/NormReg/` contains formal proofs and axiom audits.
- `results/<experiment>/` stores numerical arrays, settings, and summaries.
  Generated figures go in root `figures/`, LaTeX build files go in ignored
  `build/`, and generated manuscript tables live in `paper/generated/`.

## Build, Test, and Development Commands

Run commands from the repository root. Install the locked Python dependencies
with `uv sync --locked --no-dev`, then activate `.venv`. A standard Python venv
with pip also works with the dependency ranges in `pyproject.toml`.

- `python -m experiments NAME`: run and summarize a named experiment. Use
  `--stage run` or `--stage summarize` to separate steps where a summary module
  exists.
- `python -m experiments.<name>.run` and
  `python -m experiments.<name>.summarize`: invoke individual modules with their
  additional options.
- `python -m checks.<name>`: run one numerical or saved-result check.

The optional `devenv shell` supplies pinned system tools, including Python,
LaTeX, Lean, Task, and validation tools, for stronger environment
reproducibility. Task provides convenience wrappers and uses the active Python
environment. Run `task --list` to list wrappers.

- `task paper`: regenerate required figures and compile `build/main.pdf`.
- `task figures`: regenerate manuscript plots from saved results.
- `task experiment:<name>`: run and summarize one experiment. Experiments with
  separate summary modules also provide `:run` and `:summarize` tasks.
- `task check:results`: reconstruct saved losses, selections, and summaries.
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
`python -m checks.predictive_theorem`, then broader validation appropriate to
the change.

## Reproducibility

Keep the repository focused on the current manuscript. Retain the seeds,
experiment settings, data, results, and numerical diagnostics needed to
reproduce and assess its claims. Obsolete experiments and their artifacts may be
removed; the working tree does not need to document every past experiment. Use
Git history to record changes; do not add checksum enforcement, locked
declarations, or dependencies on historical Git revisions. Add explicit entries
to `experiments/__main__.py` and `experiment:<name>` convenience tasks to
`Taskfile.yml`. Building the paper or its figures must never launch experiments.
Keep summarizing and plotting independent of training. Run Python modules from
the root with `python -m experiments.<name>.run` or `python -m checks.<name>`.

## Commit & Pull Request Guidelines

Use Conventional Commits, ASCII messages, and short titles, ideally under 60
characters. Link issues with `Fixes #N`, `Closes #N`, or `Refs #N` as
appropriate. Pull requests should explain the change, identify affected
scientific claims or artifacts, and report validation commands. Include figure
previews when changing plots.

## Paper Style and Format

- ALT 2027 has no page limit, but reviewers may stop after the first 12 pages,
  excluding references. Flag material beyond that point to the user instead of
  cutting the draft to fit.
