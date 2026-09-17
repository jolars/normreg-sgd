# Project guidance

This is an AISTATS 2027 research manuscript with supporting Python calculations.
The conference paper centers feature normalization under finite training
budgets. It studies rare-feature learning under normalization, early stopping,
and stochastic optimization, with an emphasis on rare-subgroup prediction.
Elementary population-flow and scalar SGD results are extended to a fixed common
block, exact finite-update moments, and batch-rarity stability under explicit
population assumptions. Joint sampling guarantees, novelty, and empirical
usefulness remain research objectives. Earlier shrinkage results are supporting
baselines.

## Sources and mathematical conventions

- `paper/main.tex` is the anonymous AISTATS 2027 draft; its main sections use
  the `conference-` prefix. `paper/research-notes.tex` preserves the longer
  manuscript and earlier section files. `paper/references.bib` is shared.
  `notes/aistats-2027.md` records the conference scope and preparation tasks.
  Keep the official files under `paper/vendor/aistats2027/` unmodified.
- `notes/research-plan.md` records the research program and the scope of
  candidate claims. `TODO.md` is the consolidated task checklist, with earlier
  shrinkage extensions marked as deferred. `notes/two-feature-investigation.md`
  preserves the initial derivations; its references to the original paper
  concern the earlier `normreg` project.
- `experiments/check_two_features.py` contains exact region integration and
  independent checks of the explicit-penalty baselines.
  `experiments/check_optimization.py` checks the population gradient-flow and
  scalar fresh-batch SGD formulas. `experiments/check_block_flow.py`,
  `experiments/check_discrete_dynamics.py`, and
  `experiments/check_multivariate_stability.py` check the corresponding block,
  finite-update, and stability extensions. This is a script project, not an
  installable Python library.
- `notes/predictive-claim-feasibility.md` proves the proposed population
  stability and uniform quadratic remainder locally, with explicit constants.
  `experiments/check_predictive_feasibility.py` independently constructs
  rational moment operators and checks the proof inequalities and finite
  remainders. `notes/predictive-regime.md` derives opposite oracle rare-risk
  orderings for independent-feature signal families over continuous rates and
  all earlier stops. `experiments/check_predictive_regime.py` verifies its
  rational certificate and finite bounds. `notes/predictive-theorem.md` gives a
  self-contained direct proof of the same predictive guarantees and separates
  mathematical completion from the contribution assessment.
  `experiments/check_predictive_theorem.py` supplies a separate rational
  certificate and tensor moment checks. `notes/predictive-proof-review.md`
  records a separate Codex mathematical review, with an independent checker in
  `experiments/check_predictive_review.py`. Its new addendum removes the
  predictive rate cap but still needs independent review. Human review,
  source-comparison review, and novelty remain open; do not promote these
  results into a general normalization recommendation.
- `notes/joint-interactions.md` specifies the first joint training comparison;
  `notes/joint-interactions-results.md` records its numerical findings and
  pending independent proof review. `experiments/run_joint_interactions.py`
  computes fresh-sample paths, and `experiments/check_joint_interactions.py`
  independently checks them against enumerated updates and prior operators.
- `notes/normalization-robustness.md` is the frozen robustness protocol;
  `notes/normalization-robustness-results.md` records its execution and limits.
  `experiments/robustness_spec.py` defines its sets. The runner, simulator,
  summarizer, plotter, and independent checker use the
  `*_normalization_robustness.py` filenames. Their separate artifacts live in
  `results/normalization-robustness/`. Preserve the reported Monte Carlo
  covariance gate violation and its conditional-absence investigation.
- `notes/practical-selection.md` freezes the estimated-preprocessing and
  validation-selection protocol; `notes/practical-selection-results.md` reports
  the sampled binary and sparse categorical evaluations. The six
  `*practical*.py` scripts define, run, summarize, independently check, and
  investigate numerical precision for this study. Separate artifacts live in
  `results/practical-selection/`; attributed source data live in
  `data/mushroom/`. Preserve missing-group failures, boundary selections, and
  the post hoc decimal investigation.
- `notes/mushroom-rate-search.md` declares the separate rate expansion of the
  frozen categorical study. Its results belong in
  `notes/mushroom-rate-search-results.md`, with artifacts under
  `results/mushroom-rate-search/`. The four `*mushroom_rate*.py` scripts retain
  all candidate paths, failures, and nested selections. Preserve the declaration
  hashes and the earlier practical study.
- `notes/mushroom-scaling-sensitivity.md` declares five fixed damping offsets
  and a variance-scaling comparator in the primary centered/fitted Mushroom arm.
  Its four `*mushroom*sensitivity*.py` scripts and separate artifacts under
  `results/mushroom-scaling-sensitivity/` preserve the earlier studies. Treat
  0.01 as a prespecified heuristic; a fixed-offset sensitivity comparison does
  not select a deployable damping rule or establish an optimal offset.
- `notes/variance-scaling-followup.md` declares the four-rule comparison across
  all practical synthetic and Mushroom preprocessing arms, with 25 rate factors
  per rule. The four `*variance_scaling*.py` scripts and separate artifacts
  under `results/variance-scaling-followup/` retain the nested earlier searches,
  failures, absence strata, and numerical audit gates. Preserve the declaration
  and preceding studies. Results belong in
  `notes/variance-scaling-followup-results.md`.
- The paper and optimization checks use the averaged loss and
  $C = X_c^\top X_c/n$ for empirical designs, while the shrinkage script uses
  $G = nC$. Keep $\lambda_1 = nt$ and $\lambda_2 = nr$ consistent. Report
  coefficients on the original feature scale.
- Use $T$ for gradient-flow time, $k$ for update count, $B$ for batch size, and
  $\eta$ for learning rate. Keep training time separate from penalty $t$.
  Distinguish population dynamics, fixed-data sampling, and fresh-sample SGD;
  state centering, scale estimation, initialization, and intercept assumptions.
  Compare batch sizes using processed observations as well as update count.
- Full-rank convergence to OLS, early-stopping regularization, and selection
  among interpolating solutions are distinct questions. Do not equate fixed
  diagonal preconditioning with the complete dynamics of AdaGrad or Adam.
- Distinguish noiseless active-sign formulas, unconditional Gaussian moments,
  formal Gram-matrix limits, and asymptotics of actual binary samples. A
  selected region uses truncated Gaussian moments. Binary simulations must
  satisfy the joint-cell probability bounds.

## Development and validation

`lean/` contains a Lean v4.30.0/Mathlib proof pilot for the two large-rate lower
bounds, conditional on the predictive moment recurrence. Its README maps the
formal statements to the notes and records the scope. Inside `devenv shell`, run
`make prepare-lean` to fetch dependencies and `make check-lean` to build the
proofs and check their axiom dependencies. Keep `.lake/` ignored and commit the
Lake manifest. These targets are separate from numerical and manuscript checks.

Enter `devenv shell` before running these commands:

```sh
make paper
make paper-notes
make check-python
make check-optimization
make check-quick
make check
```

`make check-python` checks experiment formatting and lint.
`make check-optimization` runs deterministic optimization checks without writing
reference results. `make check-quick` also checks repository configuration and
Markdown, builds the paper, and runs the smaller numerical validation.
`make check` runs the full validation. The mathematical checks use assertions,
so run ordinary Python without `-O`.

Use `make format` for Markdown, Nix, and Python formatting. The devenv shell
uses Nix's Ruff executable and installs runtime Python dependencies from
`uv.lock`. The optional uv development group supports environments outside
NixOS.

## Generated files and releases

The robustness `paths.npz` and `summary.json` are ignored local artifacts. Use
`make prepare-results` to recreate missing copies and verify their frozen
SHA-256 hashes; dependent checks run it automatically. Do not add them to Git or
use Git LFS. The unpublished history was cleaned on September 16, 2026. Use the
Make targets for the later studies: `scripts/frozen_experiment.py` checks their
recorded preserved-file hashes in place of the removed commit references,
without changing frozen source files or declarations. See
`notes/generated-results.md` for details.

`build/` contains generated LaTeX output and is ignored. Regenerate
`results/two-feature-check.json` with `make reproduce`; do not hand-edit the
numerical values or provenance. `make verify` validates without rewriting it.
Use `make reproduce-joint-interactions` inside `devenv shell` to regenerate the
joint-interaction JSON, compressed moment archive, and SVG/PDF figures. Its
focused checks verify source and archive hashes; regenerate after changing its
scripts or `uv.lock`. Keep the frozen fixed-data pilot separate. Use
`make reproduce-normalization-robustness` to regenerate the robustness extension
and `make check-normalization-robustness` to verify it. Its source, archive,
figure, and preserved-study hashes are checked. Regenerate after changing its
sources or locked dependencies, and retain invalid candidates in unrestricted
envelope reports. Refresh `uv.lock` with uv and `devenv.lock` with devenv when
changing inputs. Keep the Panache version in the Markdown CI job aligned with
the devenv package when updating the Nix inputs.

Use `make reproduce-practical-selection` for its offline regeneration and
`make check-practical-selection` for the focused audit. Its protocol, six
scripts, locked dependencies, input data, and earlier-study hashes are checked;
regenerate after changing those inputs. Keep post-result numerical diagnostics
separate from primary selection rules. `GNUmakefile` includes the original
`Makefile` and adds these targets to integrated validation. Keep the original
file unchanged while its hash remains part of the preserved robustness study.

Use `make reproduce-mushroom-rate-search` for the separately declared rate
expansion and `make check-mushroom-rate-search` for its focused audit. The
latter reconstructs all losses and selections, replays selected paths in
transformed coordinates, and verifies the nested original search against the
frozen archive. The declaration freezes the protocol and specification before
execution; source changes require regenerating the new artifacts, not the
earlier study.

Use `make reproduce-mushroom-sensitivity` to regenerate the separate damping and
variance-scaling comparison, and `make check-mushroom-sensitivity` for its
focused audit. Keep its protocol and specification declaration fixed, retain
failures and tuning boundaries, and compare each fixed offset at equal tuning
effort. The five-offset family has greater total work than one fixed rule.

Use `make reproduce-variance-scaling` for the four-rule practical extension and
`make check-variance-scaling` for its focused audit. The new declaration uses
file hashes directly, without historical commit lookups. Summaries are separated
by law or sample size, and neighbor diagnostics use compressed arrays. Retain
numerical gate violations in `audit.json`; successful structural checks do not
erase those limitations or change the frozen selection rule.

Versionary manages the version in `pyproject.toml`, its lockfile update, and
`CHANGELOG.md` once releases are enabled. Do not hand-edit that changelog. The
release job requires `ENABLE_RELEASES=true` and `RELEASE_TOKEN`; package
publication and a license have not been configured.
