# Repository Guidelines

## Project Structure & Module Organization

This research repository studies feature normalization under finite training
budgets.

- `paper/` contains `main.tex`, the bibliography, and vendored AISTATS styles.
- `experiments/` contains numerical checks, experiment specifications, runners,
  and summary generators.
- `scripts/` contains artifact preparation and diagnostics. Editable manuscript
  plots live in `scripts/figures/`, with shared styling in `style.py`.
- `lean/NormReg/` contains formal proofs and axiom audits.
- `data/mushroom/` stores source data; `results/` stores numerical arrays,
  summaries, and provenance records. Generated figures go in root `figures/`;
  tracked historical exports live in `figures/frozen/`. LaTeX build files go in
  ignored `build/`, and the generated diagnostic table lives in
  `paper/generated/`.

## Build, Test, and Development Commands

Run commands from the repository root inside `devenv shell`, which supplies
Task, Python, LaTeX, Lean, and validation tools. Run `task --list` to list
tasks.

- `task paper`: regenerate required figures and compile `build/main.pdf`.
- `task figures`: regenerate manuscript plots from saved results.
- `task check`: run formatting, configuration, numerical checks, and the paper
  build, matching CI.
- `task check-quick`: alias for `task check`; the unused Monte Carlo study was
  removed.
- `task check-python`: check Python formatting and lint with Ruff.
- `task prepare-lean`, then `task check-lean`: fetch Mathlib caches and build
  proofs; these checks run separately from `task check`.
- `task format`: format Markdown, Nix, and Python sources.

## Coding Style & Naming Conventions

Use four-space Python indentation, an 88-character line limit, `snake_case`
functions and modules, and `UPPER_CASE` constants. Ruff checks errors and import
ordering. Follow existing `check_*.py`, `run_*.py`, `summarize_*.py`, and
`plot_*.py` naming patterns. Panache formats Markdown at 80 columns; nixfmt
formats Nix. Preserve manuscript notation and explain why in code comments using
complete sentences.

## Testing Guidelines

Tests are executable numerical checks in `experiments/check_*.py`, using
assertions and NumPy/SciPy comparisons rather than a dedicated test framework.
No coverage percentage is configured. For bug fixes, add a failing regression
check before changing behavior. Run the relevant check, such as
`task check-predictive-theorem`, then broader validation appropriate to the
change.

## Reproducibility

Preserve seeds, declarations, raw data, and archived inputs checked by hashes.
Add build tasks to `Taskfile.yml`. Retired provenance inputs, including the
original `Makefile`, are listed in `scripts/archived_inputs.json` and checked
against their pinned Git revision. Full Git history is required for these
checks. Make presentation changes in `scripts/figures/`. Use the relevant
`task reproduce-*` task when intentionally regenerating a study. The provenance
adapter maps historical figure and table paths through
`scripts/relocated_outputs.json`; use the Task commands so frozen sources and
manifests remain unchanged.

## Commit & Pull Request Guidelines

Use Conventional Commits, ASCII messages, and short titles, ideally under 60
characters. Link issues with `Fixes #N`, `Closes #N`, or `Refs #N` as
appropriate. Pull requests should explain the change, identify affected
scientific claims or artifacts, and report validation commands. Include figure
previews when changing plots.
