# Current paper tasks

Keep the manuscript theory-led. Prioritize the revisions below, informed by the
[mock-review synthesis](reviews/2026-09-23-aistats/synthesis.md), before adding
another empirical study. Human mathematical verification remains a separate
submission requirement.

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
- [ ] Resolve citation markers and verify any claims retained from [the research
  report](deep-research-report.md). Add verified references from the audits
  only where they support the current manuscript.

## Determine the impact of numerical discrepancies

- [ ] Add a compact table to Appendix G identifying the affected configurations,
  selections, reported summaries, and status of higher-precision checks for
  the discrepant synthetic paths.
- [ ] Determine which empirical conclusions depend on those paths. Resolve or
  qualify affected claims, keeping diagnostic sensitivity calculations
  separate from the original results. Preserve extreme paths and frozen
  summaries.

## Clarify the final empirical comparisons

- [ ] Make the final matched search prominent in Section 5.3, Figure 2, and
  Table 3. Preserve earlier comparisons in the supplement as evidence of
  what changed with tuning.
- [ ] Add a protocol table distinguishing rate grids, stopping checkpoints,
  processed-observation costs, and remaining search boundaries.
- [ ] Replace Section 3's initialization wording with "may stop at the
  prescribed zero initialization."

## Package the reproducibility artifacts

- [ ] Prepare a self-contained anonymous supplement with the exact certificate
  implementations and inputs, complete experimental configurations,
  selection rules, audit outputs, locked dependencies, and reproduction
  commands. Include all eight synthetic laws explicitly.
- [ ] Include instructions for the large generated files and frozen-study
  checks. Preserve recorded failures and study boundaries, and document
  hardware, computation, data provenance, and asset licenses.

## Complete human mathematical verification

- [ ] Complete human review of the theorem and proofs, including the
  unrestricted-rate extension. Record the scope and unresolved questions
  before updating the verification disclosures. Packaging artifacts and
  additional AI reviews do not complete this task.

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
  configurations and an additional sparse categorical task. Start within the
  theorem's regime, then vary preprocessing, intercept fitting, and
  selection separately. Consider a conservative-rate comparator for the
  validation failures.
- [ ] Freeze the prediction, protocol, implementation, and declaration before
  running the evaluation.
- [ ] Execute the frozen study and report theorem-domain checks separately from
  extrapolation and validation selection. Retain failed candidates, missing
  groups, boundaries, numerical discrepancies, and null or unfavorable
  outcomes.
- [ ] Reassess the manuscript's empirical conclusions against those results.
  Earlier experiments remain development evidence.
