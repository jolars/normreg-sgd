# Current paper tasks

## Review the claims

- [ ] Review the closest-source comparison, especially Amari et al.'s optimally
  stopped bias result and the preconditioned-SGD and target-risk
  antecedents. Check versions and precise statements before making a
  priority claim.
- [ ] Resolve citation markers and verify any claims retained from [the research
  report](deep-research-report.md). Add verified references from the audits
  only where they support the current manuscript.

## Evaluate the prediction prospectively

- [ ] Implement and check data ingestion, population and sampled-data
  evaluation, selection rules, and reporting for the new synthetic
  configurations and an additional sparse categorical task.
- [ ] Freeze the prediction, protocol, implementation, and declaration before
  running the evaluation.
- [ ] Execute the frozen study and report theorem-domain checks separately from
  extrapolation and validation selection. Retain failed candidates, missing
  groups, boundaries, numerical discrepancies, and null or unfavorable
  outcomes.
- [ ] Reassess the manuscript's empirical conclusions against those results.
  Earlier experiments remain development evidence.

## Prepare the submission

- [ ] Review the final claims, experimental interpretation, references, and
  disclosure.
- [ ] Finalize title, abstract, author list, OpenReview profiles, and the
  reciprocal-reviewer nomination for the abstract deadline recorded in [the
  conference plan](notes/aistats-2027.md).
- [ ] Package anonymous reproducibility artifacts, including instructions for
  the large generated files and frozen-study checks. Document hardware,
  computation, data provenance, and asset licenses.
- [ ] Finalize the AI Use Statement and checklist.
- [ ] Run integrated validation and inspect the exact submission PDF, including
  figures, references, supplement, anonymity, and the eight-page main-text
  limit.
