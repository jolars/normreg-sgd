# Current paper tasks

The AISTATS 2027 draft leads with the opposite oracle rare-risk orderings under
a common observation budget. The [contribution
decision](notes/predictive-contribution.md) is complete; correctness review,
source comparison, and prospective evaluation remain separate tasks. See the
[research plan](notes/research-plan.md) for scope and the [archive
inventory](notes/archive.md) for the previous completed checklist and deferred
research directions.

## Review the claims

- [ ] Obtain independent review of the unrestricted-rate addendum in [the proof
  review](notes/predictive-proof-review.md), including its correspondence
  with the theorem and proof now inline in `paper/main.tex`.
- [ ] Obtain human mathematical review of the proofs and rational certificates.
  The Codex review and [conditional Lean bounds](lean/README.md) do not
  certify the full statistical theorem.
- [ ] Review the closest-source comparison, especially Amari et al.'s optimally
  stopped bias result and the preconditioned-SGD and target-risk
  antecedents. Check versions and precise statements before making a
  priority claim.
- [ ] Resolve citation markers and verify any claims retained from [the research
  report](deep-research-report.md). Add verified references from the audits
  only where they support the current manuscript.
- [ ] Complete independent review of any joint-interaction analytical deductions
  retained in the paper. The numerical checks do not replace proof review.

## Evaluate the prediction prospectively

- [ ] Finalize [the protocol draft](notes/predictive-holdout.md) and audit
  overlap with the development laws and budgets. New seeds alone do not make
  a configuration held out from claim development.
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

- [ ] Complete human review of the final claims, experimental interpretation,
  references, and disclosure.
- [ ] Finalize title, abstract, author list, OpenReview profiles, and the
  reciprocal-reviewer nomination for the abstract deadline recorded in [the
  conference plan](notes/aistats-2027.md).
- [ ] Package anonymous reproducibility artifacts, including instructions for
  the large generated files and frozen-study checks. Document hardware,
  computation, data provenance, and asset licenses.
- [ ] Finalize the AI Use Statement and checklist honestly; prospective evidence
  and human review must not be marked complete before they are done.
- [ ] Run integrated validation and inspect the exact submission PDF, including
  figures, references, supplement, anonymity, and the eight-page main-text
  limit.

## Preserve the completed evidence

The oracle theorem, calibrated C1/C2 comparisons, retuning study, practical
selection, expanded Mushroom rates, damping sensitivity, four-rule extension,
and introductory illustration are implemented. Preserve their protocols,
declarations, artifacts, and review hashes. The robustness covariance gate
violation, practical missing-group failures and decimal investigation, and
variance-scaling numerical gate violations remain limitations.

Broader shrinkage theory, common-block and sampling limits, adaptive optimizers,
and the original `normreg` boundary correction are deferred in the [archived
backlog](https://github.com/jolars/normreg-multi-archive/blob/main/TODO.md).
They are not requirements for completing this paper unless the scope is
explicitly changed.
