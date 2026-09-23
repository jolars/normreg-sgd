# Research-report citation resolution

September 23, 2026. This closes the second claims task in [TODO.md](../TODO.md).
The [report](../deep-research-report.md) predates the oracle contribution. Its
novelty ratings and proposed directions remain historical judgments, superseded
by the [contribution decision](predictive-contribution.md) and [closest-source
review](predictive-source-comparison.md). They are not evidence of priority.

The starting revision was `83ef2db7a3e2f5ab0044a06339460a705fb62f04`. The
report's SHA-256 before editing was
`a040c8af6d2fdc563a13e6f3d1af88cb7890502b51038d56e122e6c02e6f0d3c`. The original
browsing log is unavailable. The table accounts for all 20 distinct search
identifiers by finding support for their surrounding claims, replacing
unsupported attributions, or withdrawing them. It does not claim to decode that
log. Ordinary links now replace every opaque citation marker in the report.

## Sources and dispositions

“Background only” means the source supports the report's brief literature
description but is not added to the manuscript. For those entries, abstract and
version checks establish the stated topic, not theorem applicability or a proof
audit. The historical audits remain unchanged.

  | Original identifier                  | Checked source and location                                                                                                                                                                                                                     | Disposition                                                                                                                                                                                                                                   |
  | ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | `turn1academia19`                    | [Larsson and Wallin, arXiv:2501.03821v3](https://arxiv.org/html/2501.03821v3), Sections 3 and 5                                                                                                                                                 | Supports explicit-penalty shrinkage and binary prevalence; already cited in Appendix C.                                                                                                                                                       |
  | `turn17search0`                      | [Ali, Kolter, and Tibshirani, AISTATS 2019](https://proceedings.mlr.press/v89/ali19a/ali19a.pdf), abstract and Section 3; audit S4                                                                                                              | Supports early-stopping regularization; already cited. No identity of ridge and flow paths is asserted.                                                                                                                                       |
  | `turn3academia30`                    | [Ali, Dobriban, and Tibshirani, ICML 2020](https://proceedings.mlr.press/v119/ali20a/ali20a.pdf), Lemma 1 and Remark 2, PDF p. 3; Theorem 2, p. 6                                                                                               | Added to Appendix C with the fixed-design and discretization qualifications.                                                                                                                                                                  |
  | `turn15academia29`                   | [Su, Zou, and Wu, arXiv:2403.08585v3](https://arxiv.org/html/2403.08585v3), Sections 3–4 and Appendix A.1                                                                                                                                       | Already cited; the precise aggregate, tail-average, and tuning comparison is in the closest-source review.                                                                                                                                    |
  | `turn19academia21`                   | [Zou et al., arXiv:2108.04552v2](https://arxiv.org/abs/2108.04552v2), abstract and audit S13, Sections 3–5                                                                                                                                      | Background only. The one-hot model is uncentered; comparisons allow sample inflation and return tail averages.                                                                                                                                |
  | `turn18search3`                      | [Jain et al., JMLR 2018](https://jmlr.org/papers/volume18/16-595/16-595.pdf), abstract and Section 1; audit S2                                                                                                                                  | Supports batching, averaging, and separate work/update accounting; already cited.                                                                                                                                                             |
  | `turn10search0`                      | [Défossez and Bach, arXiv:1711.01761v1](https://arxiv.org/html/1711.01761v1), Sections 1–3; audit S11                                                                                                                                           | Supports sparse aggregation as coordinate rescaling; already cited. Support probability is not binary prevalence after centering.                                                                                                             |
  | `turn20academia5`                    | [Meterez et al., arXiv:2510.14717v2](https://arxiv.org/html/2510.14717v2), Section 5 and Theorem 1; audit S10                                                                                                                                   | Background only. Replaced the priority language with the qualified phase-end risk comparison.                                                                                                                                                 |
  | `turn20academia6`                    | [Smith et al., arXiv:1711.00489v2](https://arxiv.org/abs/1711.00489v2), abstract                                                                                                                                                                | Background only: empirical batch/rate scheduling, not an exact path equivalence.                                                                                                                                                              |
  | `turn19academia20`                   | [Smith et al., arXiv:2101.12176v1](https://arxiv.org/abs/2101.12176v1), abstract                                                                                                                                                                | Background only: small finite steps and random reshuffling in a modified-loss analysis.                                                                                                                                                       |
  | `turn12search2`                      | [Sonthalia, Lok, and Rebrova, arXiv:2406.04425v2](https://arxiv.org/abs/2406.04425v2), abstract and July 3, 2026 revision date                                                                                                                  | Background only. The report now attributes the summary to the abstract; no arbitrary-step generalized-ridge theorem is imported.                                                                                                              |
  | `turn19academia19`                   | [Jahn, Pillaud-Vivien, and Schertzer, arXiv:2609.11273v1](https://arxiv.org/abs/2609.11273v1), abstract and September 10, 2026 submission date                                                                                                  | Background only. Restored the logarithmic factor, high-probability qualifier, and source/spectral conditions.                                                                                                                                 |
  | `turn15academia31`, `turn19search2`  | [Scott et al., arXiv:2511.19716v3](https://arxiv.org/abs/2511.19716v3), abstract                                                                                                                                                                | One checked source supports the conditioning/noise-floor description. Background only; two old markers do not establish two distinct papers.                                                                                                  |
  | `turn16search6`                      | [Everett and Paquette, arXiv:2605.28961v1](https://arxiv.org/abs/2605.28961v1), abstract and May 27, 2026 submission date                                                                                                                       | Background only: sparse momentum models, not conventional fixed feature scaling.                                                                                                                                                              |
  | `turn13search3`, `turn13search26`    | Original sources unidentified. Replacement: [Défossez and Bach, AISTATS 2015](https://proceedings.mlr.press/v38/defossez15.pdf), Section 2, and Jain et al. above; audits S1–S2                                                                 | Removed the attribution to high-dimensional trajectory analyses. The narrower claim about existing moment operators has direct support.                                                                                                       |
  | `turn16search3`                      | Original stochastic-reweighting source unidentified after searches for the stated method, regression, and rare one-hot features                                                                                                                 | Withdrew that attribution. The one-hot example now cites Zou; generic sparse-optimization statements cite [Duchi et al., JMLR 2011](https://jmlr.org/papers/v12/duchi11a.html), whose abstract explicitly motivates rare predictive features. |
  | `turn5academia17`, `turn5academia18` | Original source identities/order unverified. Replacement support: [Chen, Zhou, and Zhou, arXiv:2605.24316v3](https://arxiv.org/abs/2605.24316v3) and [Lin, Wu, and Bartlett, arXiv:2506.08415v2](https://arxiv.org/abs/2506.08415v2), abstracts | Background only. Both explicitly study one-pass versus reused-data linear regression. No scaling-law theorem is transferred to the binary model.                                                                                              |

## Claims retained in the manuscript

The report's overlap with the current manuscript falls into the following
claims. The speculative extensions, proposed phase diagrams, language-model
motivation, momentum analysis, and novelty ratings are not manuscript results.

  | Retained claim and location                                                                               | Evidence and scope                                                                                                                                                                                                                                                      |
  | --------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | Scaling affects explicit shrinkage; Introduction and Appendix C                                           | Larsson and Wallin's Sections 3 and 5 support the binary/continuous distinction and prevalence-dependent shrinkage. This concerns explicit penalties, not the oracle SGD theorem.                                                                                       |
  | Feature scaling is a fixed preconditioner; Section 2                                                      | Direct substitution of the scaled features and coefficients gives the displayed update. Su's fixed-preconditioner formulation overlaps directly; this identity is established background.                                                                               |
  | Global scaling can be offset by a scalar rate; Section 2                                                  | The update depends on the product of the rate and inverse squared scales. Multiplying all scales by a constant and the rate by its square leaves that product unchanged. Relative scales generally change its coordinate ratios. This is algebra, not a priority claim. |
  | Prevalence affects mean learning and noise; Sections 2 and 4                                              | The independent-coordinate mean multiplier and the two observation-noise terms are derived from the manuscript's update. Centered rare features are nonzero even on absence: the explanation does not require zero gradients on every rare-absent draw.                 |
  | Early stopping and stochastic risk along the path have antecedents; Appendix C                            | Ali 2019 supports the flow/ridge comparison. Ali 2020 supports the stochastic-flow extension. Its exact moment match is with an Euler discretization; it does not equate continuous flow and discrete SGD.                                                              |
  | Moment recurrences, sampling, batching, and stability are established machinery; Section 2 and Appendix C | Défossez–Bach, Jain, and [Mulayoff–Michaeli](https://proceedings.mlr.press/v247/mulayoff24a/mulayoff24a.pdf) support this background. Audits S1–S3 record sampling conventions and the fixed-data versus fresh-population distinction.                                  |
  | Rare-feature scaling can have a statistical cost; Introduction and Appendix C                             | The two passages below explicitly precede this paper's motivation. They are warnings and possible mechanisms, not proofs of the oracle gaps.                                                                                                                            |
  | Aggregate and subgroup risks can disagree; Sections 2–4                                                   | Conditional second moments weight the same training-error matrix differently. The target-risk antecedents and limits of the novelty claim were checked in the closest-source review. The report's suggestion that this is an unoccupied direction is not retained.      |
  | The two oracle gaps survive separate constant-rate/stop tuning; Section 3                                 | This is the manuscript's theorem, not a result verified by the planning report. The closest-source review compares its quantifiers with the prior results. Existing proof records and the separate human-verification requirement remain in force.                      |

The manuscript adds only three references from the audits:

- **Ali, Dobriban, and Tibshirani (audit S12).** The published ICML PDF and PMLR
  metadata were checked. PDF pp. 3 and 6 were rendered to inspect Lemma 1,
  Remark 2, and Theorem 2. Appendix C now makes the continuous/discrete
  distinction explicit.
- **Bordes et al. (audit S14).** [JMLR
  11(77):2229–2240](https://jmlr.org/papers/v11/bordes10a.html), Section 5.4,
  printed p. 2238 (PDF p. 10), warns about test performance when very rare
  features are standardized. The passage and metadata were checked, and the page
  was rendered. The citation is to the published erratum, not the flawed
  original optimizer paper.
- **Milligan et al. (audit S16).** The [OPT 2024 workshop
  PDF](https://opt-ml.org/papers/2024/paper107.pdf), p. 5, Sections 4–5,
  connects binary frequencies to conditioning and raises stochastic variance as
  a possible cost of standardization. The page was rendered and the author list
  checked on p. 1. The manuscript describes its deterministic training scope and
  does not claim it demonstrated a generalization result.

The other audited sources are either already cited for the oracle comparison or
concern directions not developed here. Bibliography entries for uncited
historical topics are not evidence of manuscript claims. No reviewed proof,
frozen study, result, figure generator, or vendor file was changed.

## Validation

In `devenv shell`, `make paper` produces a 23-page PDF and reports
`AISTATS-MAIN-PAGES: 8`. All 15 manuscript citation keys resolve, and the
bibliography has no duplicate keys or BibTeX warnings. The final LaTeX log has
no undefined citations or references. Its existing title-box overflow warning
remains; the added references and prose produce no overfull boxes.

The bibliography and Appendix C additions were visually checked on PDF pp. 9 and
14, along with the main-text boundary on p. 8. `make check-markdown` and
`git diff --check` pass. A separate text check matches all 20 original source
identifiers to the disposition table, verifies that all 18 report link
definitions resolve and are used, and finds no opaque citation markers in the
repaired report or manuscript. The changed-file list is limited to the report,
this record, TODO, and the manuscript text and bibliography.
