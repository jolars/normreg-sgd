# Feature Normalization under Finite Training Budgets

This is an anonymous AISTATS 2027 manuscript with supporting Python
calculations. The main theorem gives opposite rare-subgroup risk orderings for
standardization and unscaled training after each chooses any nonnegative
constant learning rate and deterministic stop under a common observation cap. It
covers two independent binary features with known population preprocessing, one
fresh observation per update, and the stated signal and rare-observation
regimes.

The bounded-rate proof has a separate Codex review. Independent review of the
unrestricted-rate extension, human mathematical review, and source-comparison
review remain open. The empirical studies informed the theory; the prospective
evaluation is still a protocol draft. These results do not establish a general
normalization recommendation.

## Start here

- [Manuscript](paper/main.tex): the main text and appendices are inline; only
  the [checklist](paper/sections/checklist.tex) is a separate input.
- [Current tasks](TODO.md), [research plan](notes/research-plan.md), and
  [conference preparation](notes/aistats-2027.md).
- [Contribution decision](notes/predictive-contribution.md), [direct
  proof](notes/predictive-theorem.md), and [proof review and unrestricted-rate
  addendum](notes/predictive-proof-review.md).
- [Prospective evaluation draft](notes/predictive-holdout.md): implementation,
  declaration, and execution remain open.
- [Lean pilot](lean/README.md): two large-rate lower bounds conditional on the
  moment recurrence, with pinned dependencies and an axiom audit.
- [Archive inventory](notes/archive.md): historical manuscripts and the previous
  research backlog now live in
  [`../normreg-multi-archive`](../normreg-multi-archive/README.md), backed by a
  [private GitHub repository](https://github.com/jolars/normreg-multi-archive).

## Evidence retained for the paper

The [calibrated comparison proofs](notes/normalization-risk-theorem.md) and
[joint-interaction study](notes/joint-interactions-results.md) explain
particular learning paths. The [robustness
study](notes/normalization-robustness-results.md) shows that retuning removes
both original anchors, while other laws retain reversals or objective
disagreements. Its covariance diagnostic failure remains part of the record.

The [practical-selection study](notes/practical-selection-results.md) examines
estimated preprocessing, fitted intercepts, missing rare groups, and validation
selection on synthetic data and UCI Mushroom. The separate [rate
expansion](notes/mushroom-rate-search-results.md), [damping
sensitivity](notes/mushroom-scaling-sensitivity-results.md), and [four-rule
extension](notes/variance-scaling-followup-results.md) retain the earlier
studies and their failures. The expanded search removes the resolved
large-sample SD rare-risk advantage under aggregate selection, while damping
retains lower risks. Synthetic tuning boundaries and numerical discrepancies
still limit the four-rule comparison.

Protocols and reports live in `notes/`, scripts in `experiments/`, and artifacts
in separate `results/` directories. Attributed source data are in
`data/mushroom/`. Older calculations still used by the audits or frozen
file-hash checks remain at their original paths.

## Work locally

The pinned devenv environment supplies Python, NumPy, SciPy, Matplotlib, Ruff,
LaTeX, and repository checks. Run:

```sh
devenv shell
make paper
make check
```

The paper builds to `build/main.pdf`; compilation enforces the eight-page
main-text limit. `make check` validates formatting, configuration, theory,
empirical audits, preserved baselines, and the manuscript. `make check-quick`
uses fewer Monte Carlo draws for the shrinkage baseline.
`make check-optimization` runs the numerical audits alone; `make check-python`
checks Python formatting and lint. Keep Python assertions enabled. `make format`
formats Markdown, Nix, and Python.

Two large robustness outputs are ignored local files. `make prepare-results`
recreates missing copies and verifies their frozen hashes; dependent checks run
it automatically. The first run takes additional time and disk space. See
[generated result storage](notes/generated-results.md) for the history cleanup
and preserved-file verification. No Git LFS is needed.

Each study has matching `reproduce-` and `check-` targets:

  | Study                      | Target suffix              |
  | -------------------------- | -------------------------- |
  | First fresh-sample study   | `joint-interactions`       |
  | Retuning and robustness    | `normalization-robustness` |
  | Estimated preprocessing    | `practical-selection`      |
  | Expanded categorical rates | `mushroom-rate-search`     |
  | Fixed damping sensitivity  | `mushroom-sensitivity`     |
  | Four-rule practical study  | `variance-scaling`         |
  | Oracle illustration        | `predictive-intro`         |

For example, `make check-mushroom-rate-search` audits the saved study, whereas
`make reproduce-mushroom-rate-search` regenerates its artifacts. Use the Make
targets so frozen studies receive the required preservation checks. Do not
hand-edit results, declarations, or recorded hashes.

Edit presentation figures in [scripts/figures/](scripts/figures/README.md).
`make figures` exports all seven sets to `build/figures/`; `make paper` rebuilds
the three it uses. Set dimensions in Python, never in `\includegraphics`.
Historical plotting code and outputs remain frozen.

The separate Lean checks use `make prepare-lean` followed by `make check-lean`.
The older manuscript and proposed-claim builds are available in the archive.

See [AGENTS.md](AGENTS.md) for mathematical conventions and preservation rules.
The active repository is
[jolars/normreg-multi](https://github.com/jolars/normreg-multi). Releases
require `ENABLE_RELEASES=true` and `RELEASE_TOKEN`; no package publication or
license is configured. Versionary manages `CHANGELOG.md` when releases begin.
