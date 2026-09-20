# AISTATS 2027 paper

Target adopted September 16, 2026. Working title: **Feature Normalization under
Finite Training Budgets**.

## The paper we are trying to write

**How does feature normalization change prediction at a finite training budget,
and which effects remain after learning-rate, batch-size, and stopping
calibration?**

Normalization is the subject. Rare features supply a controlled setting in which
relative learning, stochastic noise, and prediction objectives can be separated.
SGD, batching, and early stopping explain how normalization affects the fitted
predictor. The main paper should support one quantitative conclusion about that
interaction, with assumptions and resource accounting that make the comparison
useful.

The [September 20 contribution decision](predictive-contribution.md) adopts the
opposite rare-risk orderings after oracle tuning as the main theoretical
comparison. Each rule may choose every nonnegative constant rate and every
deterministic stop within a common observation cap. The result is restricted to
the stated two-feature independent model, signal families, and regime with
roughly one to four expected rare observations. The unrestricted-rate extension
still needs independent review, and human and source-comparison reviews remain
open. The next scientific milestone is a [prospective
evaluation](predictive-holdout.md).

The existing C1 and C2 comparisons establish bounded statements about specified
training procedures. Both original anchor comparisons disappear after the
declared oracle adjustments. Estimated preprocessing and validation selection
retain scaling effects. The separate [rate
expansion](mushroom-rate-search-results.md) now resolves the primary categorical
upper edge: the large-sample SD rare advantage under aggregate selection is no
longer resolved, while damping's advantage persists. The separate [four-rule
extension](variance-scaling-followup-results.md) includes variance scaling
across all practical arms and resolves the remaining Mushroom rate edges. Its
primary rare disadvantage persists, with an unresolved aggregate contrast.
Synthetic rate boundaries and numerical discrepancies, a single categorical
dataset, and validation coverage still limit the conclusions. These findings
belong in the paper as development evidence and limitations. They do not provide
a prospective test of the oracle prediction. The contribution decision does not
establish that the draft is ready for submission.

## Draft organization

The anonymous [conference manuscript](../paper/main.tex) uses the official 2027
style. Its main text contains:

1. Normalization as part of the finite-budget learning procedure, with the
   closest preconditioning and target-risk literature.
2. Original-scale updates, resource accounting, and aggregate versus
   rare-presence prediction.
3. Opposite oracle rare-risk orderings over all nonnegative constant rates and
   deterministic stops, followed by C1's and C2's calibrated comparisons.
4. What rate/stopping adjustment removes from the original anchors, followed by
   estimated preprocessing, validation selection, and the sparse categorical
   study.
5. The conclusions these comparisons support and their limits.

The single-column supplement contains the oracle proof, including the rate-cap
removal, the calibrated comparison proofs, and additional practical-study
details. The earlier full manuscript is preserved in
[research-notes.tex](../paper/research-notes.tex), including common-block
theory, sampling distinctions, joint-budget limits, the controlled pilot, and
shrinkage baselines. Its existing section files remain available for reuse.
Preserve the frozen experiment protocols, results, and diagnostic failures.

## Contribution work before submission

- State the strongest defensible central claim in one sentence and compare it
  theorem by theorem with the closest source. In particular, distinguish this
  work from preconditioned least squares, sparse aggregation, and target-aware
  prediction. A change in terminology or a two-feature example is insufficient.
- Use the completed [rate-search follow-up](mushroom-rate-search-results.md) to
  distinguish the disappearing primary SD rare advantage from persistent damping
  and shorter-budget effects. It matches tuning effort across scalings, retains
  failures and original-scale paths, and preserves the frozen study. Keep the
  unresolved secondary uncentered boundaries explicit.
- Execute the separately declared evaluation of the oracle prediction on new
  synthetic configurations and an additional categorical task. Distinguish
  checks inside the theorem's assumptions from directional extrapolations and
  validation-selection outcomes. Keep empty-group failures visible.
- Obtain human mathematical review of the final claims, interval certificates,
  literature comparisons, and interpretation. Existing agent reviews and
  independent numerical checks provide evidence, not human sign-off.
- Keep broader optimizers, neural models, and general shrinkage extensions
  deferred unless they become necessary to test the central claim.

## Conference requirements and dates

Verified against the [official call for
papers](https://virtual.aistats.org/Conferences/2027/CallForPapers) on September
16, 2026:

  | Item                                      | Requirement                                                             |
  | ----------------------------------------- | ----------------------------------------------------------------------- |
  | Abstract                                  | September 29, 2026, 23:59 AoE                                           |
  | Full paper and all supplementary material | October 6, 2026, 23:59 AoE                                              |
  | Main text                                 | At most eight pages in the official style                               |
  | Excluded from the limit                   | AI Use Statement, references, reproducibility checklist, and appendices |
  | Review format                             | Anonymous, double blind                                                 |
  | Supplement                                | Single column, following the checklist in this draft                    |
  | Authorship                                | Author list freezes at the abstract deadline                            |
  | Conference                                | May 3–6, 2027, Montréal                                                 |

The initial submission keeps author–year citations, which are also required for
the camera-ready version. The AI Use Statement precedes references and describes
the substantial assistance used. The checklist preserves the template questions
and marks incomplete items honestly. Neither currently claims that human
verification or anonymous artifact packaging is complete.

Before the abstract deadline, settle the central claim, title, abstract, author
list, and required OpenReview profiles and reciprocal-reviewer nomination.
Before the paper deadline, complete human verification, anonymize and package
the code and data instructions, record computing infrastructure and asset
licenses, resolve checklist answers, and inspect the exact PDF to be uploaded.
There is no later supplementary-material deadline. No submission has been made
by this repository setup.

## Build and inspect

Inside `devenv shell`:

```sh
make paper
make paper-notes
make check-quick
```

The outputs are `build/main.pdf` and `build/research-notes.pdf`. The conference
source flushes main-text floats before the excluded sections and fails the build
if the main text exceeds eight pages. `AISTATS-MAIN-PAGES` in `build/main.log`
records the count. The vendored style files are unchanged; source provenance is
recorded in [the template README](../paper/vendor/aistats2027/README.md).
