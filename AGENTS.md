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

Versionary manages the version in `pyproject.toml`, its lockfile update, and
`CHANGELOG.md` once releases are enabled. Do not hand-edit that changelog. The
release job requires `ENABLE_RELEASES=true` and `RELEASE_TOKEN`; package
publication and a license have not been configured.
