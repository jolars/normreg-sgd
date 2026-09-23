# Current paper tasks

Keep the manuscript theory-led. Prioritize the revisions below, informed by the
[mock-review synthesis](reviews/2026-09-23-aistats/synthesis.md), before adding
another empirical study.

## Review the claims

- [x] Review the closest-source comparison, especially Amari et al.'s optimally
  stopped bias result, Su et al.'s preconditioned-SGD results, and the
  target-risk antecedents. Compare assumptions, risk objectives, iterates,
  and tuning domains, and determine whether existing results imply the
  oracle comparison. Check versions and precise statements before making a
  priority claim, then revise the related-work discussion to reflect the
  verified distinctions. Completed in the [bounded source
  review](notes/predictive-source-comparison.md); the related-work
  discussion and references now reflect it. Exhaustive priority is not
  established.
- [x] Resolve citation markers and verify any claims retained from [the research
  report](deep-research-report.md). Add verified references from the audits
  only where they support the current manuscript. Completed in the [citation
  resolution record](notes/research-report-citations.md), including the
  disposition of unverified attributions and three additions to Appendix C.

## Determine the impact of numerical discrepancies

- [x] Add a compact table beside Appendix G identifying the affected
  configurations, selections, reported summaries, and status of
  higher-precision checks for the discrepant synthetic paths.
- [x] Determine which empirical conclusions depend on those paths. Resolve or
  qualify affected claims, keeping diagnostic sensitivity calculations
  separate from the original results. Preserve extreme paths and saved
  summaries. Completed in Appendix H and the [review
  diagnostics](notes/review-diagnostics.md). Flagged selections dominate
  four extreme synthetic means; their magnitudes and rankings are qualified.
  Expanded-search high-precision replay remains open.
- [ ] If restoring claims based on those extreme means, replay the affected
  expanded candidate searches at higher precision and repeat selection, or
  establish that the retained conclusions are insensitive to the numerical
  disagreement. This is deferred while those claims remain withdrawn. Keep
  this investigation separate from the original 160-digit replay.

## Clarify the final empirical comparisons

- [x] Make the final matched search prominent in Section 5.3 and the main figure
  and table. Preserve earlier comparisons in the supplement as evidence of
  what changed with tuning.
- [x] Add a protocol table distinguishing rate grids, stopping checkpoints,
  processed-observation costs, and remaining search boundaries.
- [x] Replace Section 3's initialization wording with "may stop at the
  prescribed zero initialization."
- [x] Report clipping of the saved Mushroom selections separately from raw
  predictions. Retain original validation selection and all partitions.
- [x] Add a finite-grid signal-allocation illustration under the theorem's data
  model, varying budget and noise. Keep it separate from prospective
  evaluation and unrestricted oracle guarantees. See the [illustration
  record](notes/signal-allocation.md).

## Package the reproducibility artifacts

- [ ] Prepare a self-contained anonymous supplement with the exact certificate
  implementations and inputs, complete experimental configurations,
  selection rules, audit outputs, locked dependencies, and reproduction
  commands. All eight synthetic laws are now explicit in Appendix D; the
  anonymous executable distribution remains to be packaged.
- [ ] Include instructions for the large generated files and numerical checks.
  Preserve recorded failures and study boundaries, and document hardware,
  computation, data provenance, and asset licenses.

## Prepare the submission

- [ ] Review the final claims, experimental interpretation, references, and
  disclosure.
- [ ] Finalize title, abstract, author list, OpenReview profiles, and the
  reciprocal-reviewer nomination for the abstract deadline recorded in [the
  conference plan](notes/aistats-2027.md).
- [ ] Finalize the AI Use Statement and checklist.
- [ ] Run integrated validation and inspect the exact submission PDF, including
  figures, references, supplement, anonymity, and the eight-page main-text
  limit.

## Deferred: evaluate the prediction prospectively

Reconsider this extension after the literature comparison and targeted revisions
above, if the paper needs a stronger practical contribution. It is not a repair
to an identified theorem error.

- [ ] Implement and check data ingestion, population and sampled-data
  evaluation, selection rules, and reporting for the new synthetic
  configurations. Begin with the theorem's model, then change fresh versus
  reused observations, known versus estimated preprocessing, intercept
  fitting, and validation selection one assumption at a time.
- [ ] Compare the current candidate family with a separately declared
  stability-screened search at matched tuning effort.
- [ ] Report results by rare-validation coverage: empty groups, small positive
  counts, and better-covered groups. Prespecify the strata and catastrophic
  event criteria, and report event frequencies and quantiles alongside
  means.
- [ ] Record the prediction and evaluation protocol in Git before running the
  evaluation.
- [ ] Execute the planned study and report theorem-domain checks separately from
  extrapolation and validation selection. Retain failed candidates, missing
  groups, boundaries, numerical discrepancies, and null or unfavorable
  outcomes.
- [ ] Reassess the manuscript's empirical conclusions against those results.
  Earlier experiments remain development evidence.

## Deferred: further empirical and theoretical extensions

These are optional ways to strengthen the contribution, not requirements for the
narrowly stated oracle theorem. Choose among them rather than treating every
suggestion as part of the current submission.

- [ ] Add a converged prediction reference and identifiable prediction contrasts
  for Mushroom to separate transient learning from solution selection in its
  rank-deficient representation.
- [ ] Evaluate selection using clipped validation predictions, separately from
  the completed diagnostic that clips already-selected predictors. Preserve
  the original raw-selection results and declare the new procedure before
  execution.
- [ ] Consider an additional sparse categorical task if it answers a specific
  robustness question left open by the controlled synthetic study.
- [ ] Derive a limiting-risk characterization or certify a transition between
  oracle orderings beyond the two sufficient-condition families. The
  completed finite-grid map is an illustration, not such a characterization.
- [ ] Analyze when damping improves attainable risk and how that depends on
  signal, noise, and budget. The algebraic connection to prior
  preconditioners does not explain the observed empirical advantage or
  justify an optimal offset.
