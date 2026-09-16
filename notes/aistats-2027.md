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

The existing C1 and C2 comparisons establish bounded statements about specified
training procedures. Both original anchor comparisons disappear after the
declared oracle adjustments. Estimated preprocessing and validation selection
retain scaling effects, but the categorical result is limited by its rate grid,
single dataset, and validation coverage. These findings belong in the paper.
They do not yet establish a contribution beyond the closest preconditioning and
target-risk results. The template conversion is a concrete draft, not a decision
that the present contribution is ready for submission.

## Draft organization

The anonymous [conference manuscript](../paper/main.tex) uses the official 2027
style. Its main text contains:

1. Normalization as part of the finite-budget learning procedure, with the
   closest preconditioning and target-risk literature.
2. Original-scale updates, resource accounting, and aggregate versus
   rare-presence prediction.
3. C1's stopping reversal and C2's objective disagreement, with their exact
   scope.
4. What rate/stopping adjustment removes, followed by estimated preprocessing,
   validation selection, and the sparse categorical study.
5. The conclusions these comparisons support and their limits.

The single-column supplement contains the comparison proofs and additional
practical-study details. The earlier full manuscript is preserved in
[research-notes.tex](../paper/research-notes.tex), including common-block
theory, sampling distinctions, joint-budget limits, the controlled pilot, and
shrinkage baselines. Its existing section files remain available for reuse.
Preserve the frozen experiment protocols, results, and diagnostic failures.

## Contribution work before submission

- State the strongest defensible central claim in one sentence and compare it
  theorem by theorem with the closest source. In particular, distinguish this
  work from preconditioned least squares, sparse aggregation, and target-aware
  prediction. A change in terminology or a two-feature example is insufficient.
- Resolve the rate-boundary issue in the practical comparison under a declared
  follow-up protocol. Match meaningful calibration and tuning effort across
  scaling rules, retain failed candidates, and report when a ranking disappears.
  Extend the search only through a separate study; do not rewrite the frozen
  one.
- Decide whether the main contribution is a quantitative comparison that remains
  informative after calibration, or a characterization of the limits of
  normalization selection under rare-group coverage. Neither is established by
  choosing the framing alone. Avoid treating unfilled scope as a theorem.
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
