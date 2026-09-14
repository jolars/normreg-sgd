# Normalization and Shrinkage with Correlated Binary Features

Working foundation for a follow-up to *The Choice of Normalization Influences
Shrinkage in Regularized Regression* by Johan Larsson and Jonas Wallin. The
project investigates which normalization results survive correlated designs,
starting with two binary features and progressing toward rare-feature theory
with several nuisance predictors.

The current title is provisional. The manuscript contains bivariate derivations
and examples; the general theorem and the novelty review remain research work.

## Start here

- [Manuscript](paper/main.tex): the working paper, with proofs and explicit
  scope conditions.
- [Research tasks](TODO.md): the consolidated checklist for theory, novelty
  comparisons, experiments, and manuscript development.
- [Research plan](notes/research-plan.md): the proposed contribution, current
  evidence, mathematical setup, and first milestone.
- [Initial investigation](notes/two-feature-investigation.md): detailed
  derivations and a separate boundary correction to the earlier paper.
- [Provenance](notes/provenance.md): where the initial theory and code came
  from.

## Work locally

The development environment supplies Python, NumPy, SciPy, Ruff, LaTeX, and the
repository checks. Nix inputs are pinned in `devenv.lock`, and Python
dependencies are pinned in `uv.lock`.

```sh
devenv shell
make paper
make check
```

The manuscript builds to `build/main.pdf`. `make check` checks formatting and
configuration, verifies the exact calculations against coordinate descent and
Monte Carlo, and builds the manuscript. `make check-quick` uses fewer Monte
Carlo draws for iteration. `make format` formats Markdown, Nix, and Python.

To regenerate the numerical reference results:

```sh
make reproduce
```

This writes `results/two-feature-check.json`, including the seed, parameters,
dependency versions, and comparison results. `make verify` runs the same full
calculation without rewriting that file. For an individual run:

```sh
python experiments/check_two_features.py --draws 20000 --check-only
```

Outside NixOS, the numerical environment can also be installed with
`uv sync --locked`; run calculations with
`uv run python experiments/check_two_features.py --check-only`. Building the
paper additionally requires a LaTeX installation with `latexmk` and the packages
used in `paper/main.tex`.

## Research conventions

The manuscript uses the averaged loss, with $t = \lambda_1/n$ and
$r = \lambda_2/n$. The experiment code uses the equivalent unaveraged Gram
matrix $G = X_c^\top X_c$. All reported coefficients are on the original feature
scale. Finite-sample distribution calculations condition on the design and fixed
penalty parameters. A continuous Gram-matrix limit is labeled separately from an
asymptotic sequence of actual binary designs.

## Repository administration

This is a local Git repository on `main`. No GitHub remote or license has been
selected. GitHub Actions and Dependabot configurations are included for future
hosting; they have not run remotely.

Versionary uses the Python version in `pyproject.toml` for research-code
snapshots and manages `CHANGELOG.md` when releases begin. Its workflow is
inactive until `ENABLE_RELEASES=true` is set and `RELEASE_TOKEN` is configured
in the eventual GitHub repository. No package publication is configured.
