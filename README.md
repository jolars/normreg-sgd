# Feature Normalization under Finite Training Budgets

Target: **AISTATS 2027**. The paper asks how feature normalization changes
prediction under a finite training budget, and which effects remain after
learning-rate, batch-size, and stopping calibration. Common and rare features
provide the controlled setting. The [conference plan](notes/aistats-2027.md)
records the scope, contribution work, and submission dates: September 29, 2026,
for the abstract and October 6 for the paper and all supplementary material
(23:59 AoE).

The broader research manuscript begins with two elementary calculations: a
transient dependence effect in population gradient flow and a scalar SGD
stability bound for rare binary observations. It extends these to a fixed common
block, exact finite-update GD and fresh-sample SGD error moments, and
batch-rarity stability under a bounded common-block assumption. A
matched-covariance binary comparison isolates higher update moments, while
conditional identities and counterexamples distinguish replacement sampling and
reshuffling from fresh observations. Population centering and feature scales are
known. An independently reviewed joint-budget theorem gives a rare-coefficient
error limit under specified decreasing steps. A controlled fixed-data pilot
finds subgroup-risk differences that reverse across signals and training
budgets. Broader sampling limits, adaptive-optimizer comparisons, generalization
beyond the categorical benchmark, and standalone novelty remain research
objectives. Earlier correlated-feature shrinkage results are retained as
explicit-regularization baselines in the appendices, following *The Choice of
Normalization Influences Shrinkage in Regularized Regression* by Johan Larsson
and Jonas Wallin.

## Start here

- [Conference manuscript](paper/main.tex): an anonymous AISTATS 2027 draft
  centered on normalization-risk comparisons, retuning, and validation
  selection.
- [Full research manuscript](paper/research-notes.tex): the preserved longer
  treatment, including earlier theory and shrinkage baselines.
- [AISTATS plan](notes/aistats-2027.md): paper organization, remaining
  contribution work, conference requirements, and artifact preparation.
- [Research tasks](TODO.md): the consolidated checklist for theory, novelty
  comparisons, experiments, and manuscript development.
- [Lean proof pilot](lean/README.md): formal large-rate lower bounds conditional
  on the predictive moment recurrence, with pinned dependencies and an axiom
  audit. Run `make prepare-lean` and `make check-lean` inside `devenv shell`.
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
- [Practical-selection protocol](notes/practical-selection.md) and
  [results](notes/practical-selection-results.md): training-estimated
  preprocessing, intercepts, missing rare groups, validation-based selection,
  and a sparse categorical linear-model evaluation on UCI Mushroom.
- [Mushroom rate-search protocol](notes/mushroom-rate-search.md) and
  [results](notes/mushroom-rate-search-results.md): a separately declared,
  equally allocated expansion with paired comparisons, original-scale paths, and
  retained failures. The primary unscaled search moves off its upper edge; the
  large-sample SD rare advantage under aggregate selection is no longer
  resolved, while damping's advantage persists.
- [Literature audit](notes/novelty-audit.md): theorem-level overlap and
  unresolved novelty comparisons.
- [Damping and variance-scaling protocol](notes/mushroom-scaling-sensitivity.md)
  and [results](notes/mushroom-scaling-sensitivity-results.md): five fixed
  damping offsets and variance scaling in the primary centered/fitted Mushroom
  arm, with equal tuning effort per rule and preserved preceding studies.
  Reproduce with `make reproduce-mushroom-sensitivity` and audit with
  `make check-mushroom-sensitivity` inside `devenv shell`.
- [Four-rule practical protocol](notes/variance-scaling-followup.md) and
  [results](notes/variance-scaling-followup-results.md): variance scaling across
  all synthetic and Mushroom preprocessing arms, with a common 25-factor rate
  grid and nested replications of the earlier searches. Reproduce with
  `make reproduce-variance-scaling` and audit with `make check-variance-scaling`
  inside `devenv shell`.
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

The large robustness moment archive and detailed summary are local generated
files, excluded from Git. `make prepare-results` recreates missing copies and
verifies their frozen SHA-256 hashes. The checks that require them run this step
automatically, including CI. The first run needs additional time and disk space;
later runs reuse the verified local files. Git LFS is not required.

```sh
devenv shell
make paper
make paper-notes
make check
```

The conference draft builds to `build/main.pdf`, with an eight-page main-text
limit enforced during compilation. The longer manuscript builds separately to
`build/research-notes.pdf`. `make check` checks formatting and configuration,
verifies the optimization formulas against an independent ODE solution and exact
batch enumeration, validates the shrinkage baselines against coordinate descent
and Monte Carlo, and builds the manuscript. `make check-quick` uses fewer Monte
Carlo draws for iteration. `make format` formats Markdown, Nix, and Python.

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
archive is about 441 MiB, and its detailed summary is about 203 MiB. Both are
excluded from Git. The tracked reports, figures, simulation archive, and frozen
hashes remain available. See the [storage migration](notes/generated-results.md)
for the preservation checks used after removing these files from unpublished
history.

To reproduce the controlled pilot inside `devenv shell`:

```sh
python experiments/run_rare_subgroup_pilot.py
```

This writes `results/rare-subgroup-pilot.json`. The [pilot
report](notes/rare-subgroup-pilot.md) records the frozen tuning grid, seeds,
uncertainty convention, and interpretation. Its reported excess squared
prediction errors omit the factor of one half in the training loss.

To reproduce the practical-selection extension inside `devenv shell`:

```sh
make reproduce-practical-selection
```

This writes all candidate paths, validation selections, summaries, and SVG/PDF
figures under `results/practical-selection/`. The attributed Mushroom input is
vendored under `data/mushroom/`, so reproduction requires no download. Run
`make check-practical-selection` for independent transformed-design updates,
loss and selection reconstruction, paired uncertainty, and provenance checks.
The earlier studies and the robustness covariance diagnostic are preserved.

To reproduce the separate Mushroom rate-search follow-up inside `devenv shell`:

```sh
make reproduce-mushroom-rate-search
```

This verifies the existing declaration, expands the rate grid on the same splits
and index streams, and writes paths, selections, paired summaries, and figures
under `results/mushroom-rate-search/`. `make check-mushroom-rate-search` checks
the independent transformed-design replay and reconstructs the nested original
search against the frozen practical archive. Both focused audits also run in the
integrated validation.

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
