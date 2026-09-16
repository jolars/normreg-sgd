# Normalization and Implicit Regularization

Working direction: *Normalization and Implicit Regularization in Stochastic
Learning*. The project studies how normalization, learning rate, batch size, and
stopping jointly determine the fitted model and its statistical properties.
Common and rare features provide the initial controlled setting.

The manuscript begins with two elementary calculations: a transient dependence
effect in population gradient flow and a scalar SGD stability bound for rare
binary observations. It extends these to a fixed common block, exact
finite-update GD and fresh-sample SGD error moments, and batch-rarity stability
under a bounded common-block assumption. A matched-covariance binary comparison
isolates higher update moments, while conditional identities and counterexamples
distinguish replacement sampling and reshuffling from fresh observations.
Population centering and feature scales are known. An independently reviewed
joint-budget theorem gives a rare-coefficient error limit under specified
decreasing steps. A controlled fixed-data pilot finds subgroup-risk differences
that reverse across signals and training budgets. Broader sampling limits,
adaptive-optimizer comparisons, real-data validation, and standalone novelty
remain research objectives. Earlier correlated-feature shrinkage results are
retained as explicit-regularization baselines in the appendices, following *The
Choice of Normalization Influences Shrinkage in Regularized Regression* by Johan
Larsson and Jonas Wallin.

## Start here

- [Manuscript](paper/main.tex): the working paper, with proofs and explicit
  scope conditions.
- [Research tasks](TODO.md): the consolidated checklist for theory, novelty
  comparisons, experiments, and manuscript development.
- [Research plan](notes/research-plan.md): the proposed contribution, current
  evidence, mathematical setup, and first milestone.
- [Joint-interaction specification](notes/joint-interactions.md) and [first
  results](notes/joint-interactions-results.md): exact fresh-sample training
  paths, risk decompositions, figures, and paired simulations. Independent
  review of the new analytical deductions remains pending.
- [Robustness protocol](notes/normalization-robustness.md): the declared
  follow-up to C1 and C2, including parameter slices, rate and stopping
  adjustments, controls, paired uncertainty, and failure reporting. The
  [results](notes/normalization-robustness-results.md) show that both original
  anchor comparisons disappear after retuning, while other laws retain reversals
  and objective disagreements.
- [Joint-budget theorem](notes/joint-budget-limits.md) and [independent
  review](notes/joint-budget-review.md): the scoped fresh-sample limit.
- [Literature audit](notes/novelty-audit.md): theorem-level overlap and
  unresolved novelty comparisons.
- [Controlled pilot](notes/rare-subgroup-pilot.md): protocol, results, and
  limits of the fixed-data subgroup-risk comparison.
- [Initial investigation](notes/two-feature-investigation.md): detailed
  derivations and a separate boundary correction to the earlier paper.
- [Provenance](notes/provenance.md): where the initial theory and code came
  from.

## Work locally

The development environment supplies Python, NumPy, SciPy, Matplotlib, Ruff,
LaTeX, and the repository checks. Nix inputs are pinned in `devenv.lock`, and
Python dependencies are pinned in `uv.lock`.

```sh
devenv shell
make paper
make check
```

The manuscript builds to `build/main.pdf`. `make check` checks formatting and
configuration, verifies the optimization formulas against an independent ODE
solution and exact batch enumeration, validates the shrinkage baselines against
coordinate descent and Monte Carlo, and builds the manuscript.
`make check-quick` uses fewer Monte Carlo draws for iteration. `make format`
formats Markdown, Nix, and Python.

To check just the optimization calculations inside `devenv shell`:

```sh
make check-optimization
```

This runs the elementary checks in `experiments/check_optimization.py`,
block-flow checks in `experiments/check_block_flow.py`, finite-update moment
checks in `experiments/check_discrete_dynamics.py`, and stability checks in
`experiments/check_multivariate_stability.py`, plus covariance and
sampling-scheme checks in `experiments/check_sampling_schemes.py`.
`experiments/check_joint_budget.py` adds growing-budget and short-path checks;
`experiments/check_rare_subgroup_pilot.py` checks the pilot's conditional
moments and prediction risks. These use independent ODE solutions and exact
support, batch, and short-trajectory enumeration without rewriting results.
`experiments/check_joint_interactions.py` checks the new fresh-sample study and
the provenance of its saved artifacts.

To reproduce the joint-interaction grid, paired simulation, and SVG/PDF figures:

```sh
make reproduce-joint-interactions
```

This writes `results/joint-interactions.json`, `results/joint-interactions.npz`,
and figures under `results/figures/`. Run `make check-joint-interactions` for
its focused numerical and provenance checks. The
[specification](notes/joint-interactions.md) records the complete comparison and
distinguishes it from the fixed-data pilot.

To reproduce the declared robustness extension inside `devenv shell`:

```sh
make reproduce-normalization-robustness
```

This writes the complete grid, paired simulations, summaries, and six SVG/PDF
figures under `results/normalization-robustness/`. Run
`make check-normalization-robustness` for independent numerical, selection,
uncertainty, and provenance checks. The
[report](notes/normalization-robustness-results.md) retains disappearing
comparisons, unresolved unrestricted envelopes, and one investigated Monte Carlo
covariance diagnostic. Both preceding studies remain unchanged. The full moment
archive is about 441 MiB.

To reproduce the controlled pilot inside `devenv shell`:

```sh
python experiments/run_rare_subgroup_pilot.py
```

This writes `results/rare-subgroup-pilot.json`. The [pilot
report](notes/rare-subgroup-pilot.md) records the frozen tuning grid, seeds,
uncertainty convention, and interpretation. Its reported excess squared
prediction errors omit the factor of one half in the training loss.

To regenerate the numerical reference results for the shrinkage baselines:

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

The manuscript and optimization checks use the averaged loss and covariance
$C = X_c^\top X_c/n$ for empirical designs. The shrinkage script uses the
equivalent unaveraged Gram matrix $G = nC$, with $t = \lambda_1/n$ and
$r = \lambda_2/n$. All reported coefficients are on the original feature scale.

Use $T$ for gradient-flow time, $k$ for update count, $B$ for batch size, and
$\eta$ for learning rate. Distinguish population flow, fixed-design fits, and
SGD using fresh observations. Finite-sample penalty distributions condition on
the design and fixed penalties; formal Gram limits are separate from actual
binary sampling limits. A fixed diagonal preconditioner does not represent the
complete dynamics of AdaGrad or Adam.

## Repository administration

This is a local Git repository on `main`. No GitHub remote or license has been
selected. GitHub Actions and Dependabot configurations are included for future
hosting; they have not run remotely.

Versionary uses the Python version in `pyproject.toml` for research-code
snapshots and manages `CHANGELOG.md` when releases begin. Its workflow is
inactive until `ENABLE_RELEASES=true` is set and `RELEASE_TOKEN` is configured
in the eventual GitHub repository. No package publication is configured.
