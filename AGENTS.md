# Project guidance

This repository contains the AISTATS 2027 manuscript **Feature Normalization
under Finite Training Budgets** and its supporting calculations. As of September
22, 2026, the main contribution is the opposite rare-subgroup risk orderings
after oracle tuning of every nonnegative constant learning rate and
deterministic stop under a common observation cap. The theorem assumes two
independent binary features, known population preprocessing, zero
initialization, a fixed zero intercept, and one fresh observation per update.
Its gaps hold for the stated signal families when $0 < q \leq 10^{-4}$ and
$1 \leq Mq(1-q) \leq 4$.

The bounded-rate proof has a separate Codex review. Independent review of the
unrestricted-rate addendum, human mathematical review, and source-comparison
review remain open. The Lean pilot proves only the two large-rate lower bounds,
conditional on the moment recurrence. Existing experiments informed the theory;
they are development evidence. The prospective evaluation in
`notes/predictive-holdout.md` is still a draft, without a frozen implementation
or execution. Do not present these results as a general normalization
recommendation or claim that the manuscript is ready for submission.

## Active sources and archive

- `paper/main.tex` contains the main text and proof and experiment appendices
  inline. Edit the manuscript there. The only section it inputs is
  `paper/sections/checklist.tex`. `paper/references.bib` is the bibliography.
  Keep `paper/vendor/aistats2027/` unmodified.
- `TODO.md` tracks the current paper's unfinished work. `notes/research-plan.md`
  gives the current scope, and `notes/aistats-2027.md` records submission
  preparation. `notes/predictive-contribution.md` records the decision to lead
  with the oracle comparison.
- Historical manuscripts, unused section copies, and the previous research
  backlog are preserved in the neighboring project
  [`../normreg-multi-archive`](../normreg-multi-archive/README.md), also hosted
  in the private [GitHub
  archive](https://github.com/jolars/normreg-multi-archive). See [the archive
  inventory](notes/archive.md) for the source snapshot and preservation
  boundary. The archive includes the original Git history and a complete source
  snapshot so historical builds and audits retain their context. New paper work
  belongs here; consult the archive for deferred shrinkage, common-block,
  sampling, and joint-budget directions.
- Older scripts, notes, and results that remain here are dependencies of the
  current calculations or frozen provenance checks. Preserve them at their
  existing paths and with their recorded bytes. In particular, the two retained
  sections `discrete-dynamics.tex` and `stochastic-gradient.tex` supply
  derivations referenced by frozen proof notes; they are not manuscript inputs.
  The original `Makefile` is also a hashed input. Use `GNUmakefile` for build
  changes. Archiving a topic does not authorize breaking these dependencies.

## Theory, experiments, and evidence

- `notes/predictive-theorem.md` gives the direct bounded-rate proof.
  `notes/predictive-proof-review.md` records the separate review and the
  unrestricted-rate addendum. `notes/predictive-claim.md`,
  `notes/predictive-claim-feasibility.md`, and `notes/predictive-regime.md`
  preserve the preceding derivations. Their `check_predictive_*.py` scripts
  provide rational certificates, tensor checks, and finite bounds. Preserve the
  reviewed versions and hashes.
- `notes/normalization-risk-theorem.md` and its review support the calibrated C1
  and C2 comparisons. The joint-interaction and normalization-robustness
  protocols and reports explain the paths, variance decompositions, and retuning
  limitations. Both original anchors disappear after retuning. Preserve the
  robustness Monte Carlo covariance gate violation and its conditional-absence
  investigation.
- The practical-selection, Mushroom rate-search, Mushroom scaling-sensitivity,
  and variance-scaling-followup studies remain part of the paper and supplement.
  Each has protocol and results notes under `notes/`, scripts under
  `experiments/`, and separate artifacts under `results/`. Attributed input data
  are in `data/mushroom/`. Preserve declarations, preceding-study hashes, all
  candidate paths, missing-group failures, tuning boundaries, the post hoc
  decimal investigation, and the numerical gate violations in `audit.json`.
  Successful structural checks do not erase those limitations.
- Damping offset 0.01 is a prespecified heuristic. The five-offset sensitivity
  study does not select a deployable rule or establish an optimal offset.
  Compare fixed rules at equal tuning effort; the five-offset family uses more
  total work. The four-rule extension resolves Mushroom rate edges but retains
  synthetic boundaries and numerical discrepancies.
- `notes/novelty-audit.md`, `notes/normalization-risk-audit.md`, and the
  target-risk and predictive contribution notes record source comparisons.
  Mathematical correctness, priority, and empirical usefulness require separate
  evidence. Earlier supporting-theory recommendations are superseded by the
  contribution decision, not by rewriting the reviewed records.

## Mathematical conventions

This is a Python script project, not an installable library. The manuscript uses
the averaged half squared loss and $C = X_c^\top X_c/n$ for empirical designs.
The preserved shrinkage script uses $G = nC$, with $\lambda_1 = nt$ and
$\lambda_2 = nr$. Report coefficients on the original feature scale.

Use $T$ for gradient-flow time, $k$ for update count, $B$ for batch size, and
$\eta$ for learning rate. Keep training time separate from penalty $t$.
Distinguish population dynamics, fixed-data sampling, and fresh-sample SGD.
State centering, scale estimation, initialization, and intercept assumptions.
Compare processed observations as well as update counts. Binary simulations must
satisfy the joint-cell probability bounds.

Full-rank convergence to OLS, early-stopping regularization, and selection among
interpolating solutions are separate questions. Fixed diagonal preconditioning
does not describe the complete dynamics of AdaGrad or Adam. Keep noiseless
active-sign formulas, unconditional Gaussian moments, truncated moments in
selected regions, formal Gram limits, and actual binary-sample asymptotics
distinct.

## Development and validation

Enter `devenv shell` before running:

```sh
make paper
make check-python
make check-optimization
make check-quick
make check
```

`make paper` builds `build/main.pdf` and its figures, enforcing the eight-page
main-text limit. `make check-python` checks formatting and lint in
`experiments/` and `scripts/`. `make check-optimization` runs the theory and
empirical audits, including preserved foundational checks, without rewriting
results. `make check-quick` adds configuration, Markdown, the paper, and a
smaller shrinkage baseline check; `make check` uses the full baseline check.
Assertions must stay enabled: use ordinary Python without `-O`.

The archive retains `make paper-notes` and `make paper-claim`. These targets are
not part of the active project. Inside `devenv shell`, run `make prepare-lean`
and `make check-lean` for the separate Lean v4.30.0/Mathlib pilot and axiom
audit. See `lean/README.md` for its exact scope. Keep `.lake/` ignored and the
Lake manifest tracked.

Use `make format` for Markdown, Nix, and Python. The environment supplies Nix's
Ruff and installs Python runtime dependencies from `uv.lock`. Refresh `uv.lock`
with uv and `devenv.lock` with devenv when changing inputs. Preserve
frozen-study dependencies; changes require a deliberate reproduction plan. Keep
the Panache version in CI aligned with the devenv package.

## Frozen results and figures

`make prepare-results` recreates the ignored robustness `paths.npz` and
`summary.json` and verifies their SHA-256 hashes. Dependent targets run it
automatically. Do not track these files or use Git LFS. The unpublished history
was cleaned on September 16, 2026. `scripts/frozen_experiment.py` substitutes
recorded file-hash checks for removed historical commit lookups without changing
frozen scripts or declarations. See `notes/generated-results.md`.

Use the matching `reproduce-` and `check-` targets for `joint-interactions`,
`normalization-robustness`, `practical-selection`, `mushroom-rate-search`,
`mushroom-sensitivity`, `variance-scaling`, and `predictive-intro`. Regenerate
artifacts after changing their nonfrozen sources or locked dependencies; never
hand-edit numerical values or provenance. Keep later studies separate from their
frozen predecessors. The intro figure is a finite-grid illustration of the
theorem, not a prospective evaluation. The preserved shrinkage baseline uses
`make reproduce` and `make verify`.

Editable figure generators are in `scripts/figures/`, sharing the Matplotlib
settings in `style.py` and LaTeX text with `lmodern`. `make figures` exports
presentation figures from saved results to the ignored `build/figures/`.
`make paper` rebuilds its three figures automatically. Keep the historical
generators in `experiments/` and their hashed outputs frozen. Never set width or
height in `\includegraphics`; set figure dimensions in the Python generators.

Versionary manages the project version, lockfile, and `CHANGELOG.md` when
releases are enabled. Do not hand-edit that changelog. Releases require
`ENABLE_RELEASES=true` and `RELEASE_TOKEN`; package publication and a license
have not been configured.
