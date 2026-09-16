# Research tasks

The target is **AISTATS 2027**, with working title **Feature Normalization under
Finite Training Budgets**. The [research plan](notes/research-plan.md) centers
normalization and its interaction with learning rate, batch size, and stopping.
The [conference plan](notes/aistats-2027.md) records the paper structure,
requirements, and deadlines. The project builds on `../normreg` and retains SGD
and implicit regularization as the follow-up's ML direction.

The completed calculations and experiments below provide a foundation. Johan's
[research report](deep-research-report.md) now informs the plan. The [comparison
proofs](notes/normalization-risk-theorem.md) establish C1's stopping reversal
and C2's aggregate/subgroup disagreement under declared budgets. The [robustness
study](notes/normalization-robustness-results.md) now shows that both original
anchor comparisons disappear after declared rate and stopping adjustments, while
other laws retain reversals and objective disagreements. The [practical
study](notes/practical-selection-results.md) now tests estimated preprocessing,
intercepts, absent rare groups, and validation selection, followed by a sparse
categorical benchmark. It retains scaling effects and exposes missing-group
failures and tuning boundaries. The next milestone is **one central theorem
candidate and one decisive rate-search experiment** for the
normalization-focused conference draft. The report's positive novelty assessment
remains provisional.

## Next milestone: predictive theory and a resolved rate comparison

Prioritize the first two deliverables over the next two or three days. Use them
to decide the central contribution and the remaining work for AISTATS.

- [ ] Write a one-page proposed claim with explicit assumptions, intended
  conclusion, and closest antecedents. Starting from the two-feature model
  and exact moment recurrences, target a risk approximation with a
  controlled remainder that explains when faster rare-feature learning
  outweighs additional noise as prevalence and training budget change. It
  should explain observed reversals and why rate adjustment can remove them,
  with conclusions beyond the existing certified parameter boxes. Compare
  the precise statement with Su–Zou–Wu, AdaBatch, and target-risk
  preconditioning before committing to a substantial proof effort. Build on
  the [existing audit](notes/normalization-risk-audit.md) and [target-risk
  comparison](notes/target-risk-comparison.md); novelty remains to be
  established.
- [ ] Resolve the Mushroom rate-search boundary in a separate declared
  follow-up. Every large-sample unscaled aggregate selection chose the
  largest available rate factor. Specify a broader search with comparable
  tuning effort, retain failed candidates, and report original-scale
  coefficient paths and both aggregate and rare-subgroup risks alongside
  selected endpoints. Deliver a comparison that identifies which
  normalization effects persist, disappear, or remain unresolved. Preserve
  the [frozen practical study](notes/practical-selection.md) and its
  artifacts.
- [ ] Develop and verify the theorem if the proposed claim offers a substantive
  advance over its closest antecedents. Separate mathematical correctness
  from novelty, and obtain human review of the final result.
- [ ] Once the theory predicts a concrete regime where scaling should help or
  hurt, test that prediction on synthetic configurations held out from claim
  development and an additional sparse categorical task. Declare the
  prediction and evaluation protocol before running the tests. Retain the
  failure caused by missing rare validation observations as a limitation of
  normalization selection.

## AISTATS 2027 preparation

- [x] Vendor the official 2027 template and create an anonymous conference draft
  with the AI Use Statement, original checklist questions, and single-column
  supplement. Preserve the longer manuscript separately.
- [x] Reorganize the main text around normalization, quantitative risk
  comparisons, retuning, and validation selection. Retain disappearing
  comparisons and numerical failures.
- [ ] Obtain human review of final mathematical claims, certificates, source
  comparisons, and experimental interpretation.
- [ ] Finalize title, abstract, author list, profiles, and reciprocal-reviewer
  nomination by September 29, 2026, 23:59 AoE.
- [ ] Package anonymous reproducibility artifacts, document hardware and
  licenses, finalize the disclosure and checklist, and inspect the
  submission PDF before October 6, 2026, 23:59 AoE. Supplementary material
  shares this deadline.

## Current priorities: comparative results and their limits

Follow this order, developing the candidate statement alongside its source
comparison. The research plan gives the completion criteria.

- [x] Formulate the observed no-scaling versus standard-deviation-scaling
  stopping reversal as an explicit conjecture.
  [C1](notes/normalization-risk-comparison.md) specifies the risk
  inequalities, feasible law, signal, noise, rate calibration, and budgets.
  The two-dimensional reduction and 225-point exploratory grid are retained;
  a [uniform proof](notes/normalization-risk-theorem.md) is now available.
- [x] Complete a bounded theorem-level comparison with Su–Zou–Wu, Seesaw, and
  AdaBatch. The [focused audit](notes/normalization-risk-audit.md) maps
  assumptions, output iterates, risk objectives, moment constants, and
  budgets. It identifies strong overlap in the general mechanism. The
  expanded audit adds nine sources. The bounded target-risk comparison is
  complete below; the broader novelty assessment remains open.
- [x] Derive sufficient conditions or a controlled threshold bound for the
  normalization-risk reversal. Separate squared bias, multiplicative update
  variance, and observation-noise variance. Obtain independent proof review
  and numerical checks; a grid crossing alone does not complete this task.
  [C1](notes/normalization-risk-theorem.md) has a scalar approximation with
  a controlled remainder and a continuous-box certificate, with four uniform
  risk-gap bounds. The [independent agent
  review](notes/normalization-risk-review.md) also checks the certificates
  through a separate implementation.
- [x] Test whether the same two configurations can favor opposite orderings
  under aggregate and rare-presence risk at a common budget and test law. If
  supported, characterize the risk gap and conditions, including how
  feasible dependence and signal signs change them. Treat this as the
  stronger follow-up target, not an assumed result or a claim about globally
  optimal tuning. [C2](notes/normalization-risk-theorem.md) gives opposite
  orderings at 100 observations throughout declared dependence and noise
  intervals. Scaling increases both coefficient MSEs while improving
  rare-presence prediction; the cross moment of the coefficient errors
  explains the difference.
- [x] Specify a focused robustness experiment varying prevalence, dependence,
  signal, noise, rates, and stopping resolution. Include global-rescaling
  and common-learning controls, fixed-update and fixed-observation
  comparisons, paired simulation uncertainty, and failures. Preserve both
  existing studies. The [declared
  protocol](notes/normalization-robustness.md) specifies 228 data laws, a
  16-law resolution check, both budget conventions, paired simulations, and
  separate artifacts. Execution is recorded below.
- [x] Determine which conclusions survive learning-rate and stopping adjustments
  over a declared range at comparable budgets. Retain fixed-configuration
  results and report reversals that disappear. Add tail averaging if needed
  for the closest literature comparison. The
  [results](notes/normalization-robustness-results.md) retain all 228 laws
  and 2,571,800 endpoints. Both original anchor comparisons disappear after
  retuning; other laws retain reversals or produce objective disagreement.
  Grid refinements, paired uncertainty, the investigated covariance
  diagnostic, and unresolved unrestricted comparisons are reported. Tail
  averaging remains deferred under the declared final-iterate protocol.
- [x] After the controlled result, test estimated preprocessing, intercepts,
  absent rare observations, and validation-based selection. Then evaluate
  one stated sparse linear-model task with equal tuning effort and both risk
  objectives. Broader optimizer and neural-model comparisons follow a
  specific hypothesis. The [protocol](notes/practical-selection.md) and
  [results](notes/practical-selection-results.md) retain 637,440 endpoints
  across eight sampled laws and UCI Mushroom, with equal tuning effort, both
  objectives, independent reconstruction, and a decimal precision
  investigation. Missing validation groups can hide explosive rare error;
  benchmark gains remain limited by the declared grid and task. Broader
  comparisons are not needed for this hypothesis and remain deferred.

## Completed first comparison and remaining review

- [x] Specify the normalization family, learning-rate schedules, batch sizes,
  stopping counts, sampling assumptions, and outcomes in
  `notes/joint-interactions.md`. Include fixed-update and fixed-observation
  comparisons, plus global-rescaling controls. The [first
  comparison](notes/joint-interactions.md) specifies constant steps, fresh
  samples, four normalization exponents, both budget conventions, and
  numerical acceptance checks. Decreasing schedules are an explicit
  extension.
- [ ] Obtain independent proof review of the draft global-rescaling,
  relative-learning, and batch-order arguments. Local proofs and independent
  numerical checks are complete. Independent proof review remains pending
  because Coterie was unavailable. These controls support the comparative
  theorem above; they do not by themselves establish the main contribution.
- [x] Complete a separate follow-up to the frozen pilot that retains the joint
  configuration grid and training paths. The [first fresh-sample
  study](notes/joint-interactions-results.md) retains 1,056 configurations,
  60 stopping counts, four figures, paired simulation uncertainty, and a
  local batch-comparison sensitivity check. The normalization-risk proofs
  are now separate results above; broader robustness remains open.

## Established starting calculations

- [x] Document feature scaling as a fixed diagonal preconditioner and
  distinguish full-rank OLS convergence from early stopping and
  interpolation bias.
- [x] Prove the bivariate population gradient-flow limit containing
  $\kappa T e^{-T}\beta_1^*$ at fixed training time.
- [x] Prove the scalar fresh-batch SGD second-moment recurrence and stability
  threshold, including the role of $Bq$.
- [x] Add independent ODE and exact batch-enumeration checks to the standard
  validation commands. These validate formulas, not optimizer performance.

## Foundation: learning dynamics and sampling

- [x] Extend the population early-stopping result to a fixed block of common
  predictors and one rare binary feature. State the assumptions on $A_n$,
  $c_n/b_n$, feature scales, and initialization. See the common-block
  proposition in [gradient flow](paper/sections/gradient-flow.tex).
- [x] Derive finite-time mean-error and covariance formulas or bounds for
  discrete GD and fresh-sample SGD. Separate incomplete common-feature
  learning, observation noise, and stochastic update moments. See the exact
  formulas in [discrete dynamics](paper/sections/discrete-dynamics.tex).
- [x] Characterize stability and learning rates across small, intermediate, and
  large $Bq$. Identify what dependence changes beyond the scalar
  fourth-moment calculation and whether a common learning rate limits
  progress. Established for a uniformly bounded fixed common block with
  known population standard-deviation scales in [stochastic
  stability](paper/sections/stochastic-gradient.tex).
- [x] Compare distributions with matched covariance but different update moments
  to isolate what population gradient flow cannot explain about SGD. A
  feasible three-binary-feature family has identical means and covariance
  but different two-update rare-coefficient error and stability thresholds;
  see [sampling schemes](paper/sections/sampling-schemes.tex).
- [x] Specify joint limits for sample size, prevalence, learning rate, batch
  size, and stopping time. Start with $nq_n \to \infty$ and fixed error
  variance; compare error terms with the $(nq_n)^{-1/2}$ uncertainty scale
  under stated regularity assumptions. Check whether the order of limits
  matters. The [joint-budget theorem](notes/joint-budget-limits.md) and
  [independent review](notes/joint-budget-review.md) establish one explicit
  fresh-sample regime: $B_n = 1$, $k_n = n$, $q_n = n^{-1/2}$, and shifted
  inverse-time steps under known population preprocessing. Broader sampling,
  batch, and estimated-preprocessing limits remain open.
- [x] Distinguish online fresh samples, fixed-data sampling with replacement,
  and random reshuffling. Establish which conclusions extend to each scheme.
  Exact conditional replacement and reshuffling epoch identities, first-pass
  unconditional equivalence, and counterexamples are in [sampling
  schemes](notes/sampling-schemes.md). Population centering, scales, and the
  intercept remain known and fixed.
- [ ] Analyze estimated feature scales, training centering, and intercept
  handling. State what happens when a training sample has no rare
  observations. The [practical study](notes/practical-selection-results.md)
  now supplies numerical evidence and an explicit absent-column policy;
  finite-sample theoretical guarantees remain open.
- [ ] Identify conditions recovering the independent-feature trajectory and a
  useful approximation bound when dependence is weak relative to feature
  variance. Avoid relying on Pearson correlation alone.
- [x] Retain trajectories at stopping counts specified in advance in the first
  fresh-sample study. Broader fixed-stopping comparisons and
  validation-based choices remain in the priorities above. Do not infer
  finite-budget performance from population-flow time alone.

## Literature and novelty: integrate the report

The report supplies the broader assessment; the earlier audit supplies bounded
theorem-level comparisons. For each additional source, record the version,
theorem or equation, assumptions, conclusions, and whether it already implies
the candidate result. Relevant core optimization references are in
`paper/references.bib`. The eight-source [audit](notes/novelty-audit.md)
identifies established operator and stability frameworks; priority for the
specific rare-limit calculations remains unresolved.

- [x] Incorporate the report into the research plan and prioritize comparative
  risk statements. Keep its novelty judgments distinct from established
  mathematical and literature results.

- [x] Audit [Su, Zou, and Wu](https://arxiv.org/html/2403.08585v3), especially
  Assumption 3.2, equation (3.2), and Theorem 4.2. Check what aggregate-risk
  bounds for tail-averaged preconditioned SGD imply for our final-iterate,
  prevalence-dependent comparison and what they leave unresolved.

- [x] Audit [Meterez et al., Seesaw](https://arxiv.org/html/2510.14717v2),
  especially Theorem 1, before claiming that learning-rate and batch changes
  cannot compensate for normalization. Distinguish mean-vector, risk, and
  pathwise equivalence under their respective assumptions.

- [x] Audit [Défossez and Bach, AdaBatch](https://arxiv.org/html/1711.01761v1)
  on sparse gradient aggregation and coordinate rescaling. Account for the
  difference between uncentered sparsity and our centered indicators.

- [x] Complete the candidate-specific comparison with Ali–Dobriban–Tibshirani on
  stochastic gradient flow and Zou et al. on SGD versus ridge. Use the
  existing Jain et al. audit for mini-batch and averaging baselines. See
  S12–S13 in the [expanded audit](notes/normalization-risk-audit.md).

- [ ] Incorporate the verified references from S9–S16 of the expanded audit into
  `paper/references.bib` when revising the manuscript's related-work
  section.

- [x] Extend the C2 comparison with target-risk and subgroup-risk antecedents,
  starting from Liu et al.'s covariate-shift preconditioning analysis (S15).
  Subgroup conditioning is already a target-risk problem; test whether the
  strict configuration comparison adds a substantive conclusion. The
  [follow-up comparison](notes/target-risk-comparison.md) and S17–S20 in the
  [audit](notes/normalization-risk-audit.md) trace target-aware shrinkage,
  final-iterate SGD, and subgroup-risk antecedents. A deterministic control
  reproduces C2's coefficient-error sign pattern. Its stable SGD realization
  remains useful, but the current fixed-pair statement does not establish a
  substantive advance; tuning robustness and priority remain open.

- [ ] Resolve the report's exported citation markers into usable sources for
  claims retained in the manuscript, including its recent-paper claims.
  Verify versions and conclusions before treating them as evidence.

- [x] Compare the trajectory and risk claims with [Ali, Kolter, and
  Tibshirani](https://proceedings.mlr.press/v89/ali19a.html) on early
  stopping and ridge regression. Do not claim exact general equivalence
  between the early-stopping and ridge paths.

- [x] Compare with [Duchi, Hazan, and
  Singer](https://jmlr.org/papers/v12/duchi11a.html) on adaptive methods for
  rare predictive features, including the distinction between regret
  guarantees and the proposed statistical conclusions.

- [x] Compare with [Amari et al.](https://arxiv.org/abs/2006.10732) on
  preconditioning and generalization, and [Gunasekar et
  al.](https://proceedings.mlr.press/v80/gunasekar18a.html) on optimization
  geometry. A fixed preconditioner does not describe all of AdaGrad's or
  Adam's dynamics.

- [ ] Compare input-feature rarity with the output-class imbalance studied by
  [Kunstner et al.](https://arxiv.org/abs/2402.19449) and [Yadav et
  al.](https://arxiv.org/abs/2512.00763). Identify an additional conclusion
  beyond slow learning of infrequent classes.

- [ ] Check batch-size and tuning implications against [Srećković, Geiping, and
  Orvieto](https://arxiv.org/abs/2506.12543). Include momentum, clipping,
  and learning-rate tuning in optimizer comparisons.

- [ ] Trace related stochastic least-squares moment and stability results and
  [gradient starvation](https://arxiv.org/abs/2011.09468). Determine which
  conclusions concern fixed-feature fitting and which require feature
  learning. The moment and stability comparison is in the audit; gradient
  starvation and dedicated reshuffling literature remain open.

- [ ] Write the novelty assessment around the comparative risk result that
  survives these checks. Treat coordinate changes, matrix exponentials,
  scalar stability, and generic fourth-moment dependence as supporting
  tools. The existing matched-covariance example already illustrates the
  limits of $Bq$; an extension should add a quantitative statistical
  consequence. The [expanded audit](notes/normalization-risk-audit.md) now
  gives a bounded assessment and a working claim around C2. Retuning and
  further target-risk comparisons remain prerequisites for the
  manuscript-level assessment.

## Existing pilot and experimental extensions

The bounded [pilot](notes/rare-subgroup-pilot.md) completes the two-feature,
fixed-count comparison below. It uses known population preprocessing and
separate oracle tuning on a frozen finite grid. Grid boundary selections limit
robustness; the reversals establish no general scaling recommendation.

- [x] Build feasible two-binary-feature designs with independent, nested, and
  negatively associated features. Include common-only, rare-only,
  equal-sign, and opposite-sign signals.
- [ ] Expand the verified pilot to several common predictors.
- [x] Compare no scaling, standard-deviation scaling, variance scaling, and
  damped scaling using GD and SGD. Tune learning rates separately and record
  instability rather than silently discarding failed runs.
- [x] Vary prevalence, batch size, dependence, and stopping time in the bounded
  fixed-data grid. Compare at matched numbers of processed observations, and
  report update count.
- [x] Add a separately specified [fresh-sample
  experiment](notes/joint-interactions-results.md) with retained paths.
- [ ] Compare the fresh-sample findings with repeated passes over a fixed
  training sample under matched budgets and explicit data-access accounting.
- [x] Hold noise variance fixed and use fixed cell counts to isolate
  empirical-design effects, pairing the same noisy data across comparisons.
- [ ] Study SNR-matched comparisons and sampled designs with growing rare
  counts.
- [x] Measure original-scale coefficient bias, covariance, and error; aggregate
  excess prediction risk; and excess prediction risk within the rare
  subgroup. Distinguish transient nonzero GD coefficients from lasso
  selection.
- [ ] Evaluate a specified test prevalence shift preserving the conditional
  response model. Apply the training centering and scales at test time, and
  account explicitly for the intercept.
- [x] Quantify why an isolated $O(1)$ rare-coefficient error has only $O(q_n)$
  weight in aggregate risk. Demonstrate a consequential difference for a
  stated prediction or estimation objective.
- [ ] Include ridge and weighted lasso or elastic net as explicit-regularization
  baselines. Use the existing exact integration and coordinate-descent
  checks for their bias, covariance, selection, and false-selection
  calculations.
- [ ] Add AdaGrad and Adam as empirical comparators. Record momentum,
  stabilizing constants, clipping, schedules, and weight decay. Separate
  these comparisons from claims proved only for fixed preconditioning.
- [x] Store cell counts, Gram matrices, normalization conventions, optimizer
  settings, seeds, and software versions. Verify simulation against the
  exact calculations before larger experiments.

## Empirical extension and manuscript decision

- [ ] Check sensitivity to a wider learning-rate grid, including near-zero
  steps: 195 of 864 pilot settings select the smallest factor. Keep this
  follow-up separate from the frozen pilot evaluation.
- [ ] Evaluate validation-based stopping and tuning after fixed-budget and
  fixed-penalty comparisons. Avoid general recommendations from a small
  grid.
- [ ] Select a sparse text or categorical dataset with an interpretable
  rare-feature definition after the controlled comparison. Start with linear
  models; add a small neural model only for a stated mechanism with
  comparable tuning effort.
- [x] Complete a bounded foundation milestone: an independently reviewed
  joint-budget theorem, an eight-source overlap audit, and a reproducible
  controlled experiment with substantial risk differences and reversals.
  Broader novelty comparisons and empirical usefulness remain open.
- [ ] Assess novelty and publication scope using the report, focused theorem
  audit, accepted comparison, and robustness results. If no substantive
  result survives, reconsider the claim and scope before broad empirical
  expansion.
- [ ] Align the manuscript's title, abstract, and contribution claims with the
  resulting account of normalization, optimization choices, and fitted
  models.
- [ ] Consider bounded rare counts, multiple rare features, and
  overparameterized interpolation as separate extensions after the first
  milestone.

## Deferred shrinkage theory and supporting comparisons

These items preserve the earlier research program. The original paper supplies
the conceptual foundation; these technical extensions can support specific
joint-interaction questions without becoming prerequisites for every step.

- [ ] Establish the fixed-dimensional Gaussian coupling result for a rare
  feature and penalized nuisance block. Specify the penalty, uniform strong
  convexity of the nuisance problem, moment bounds, and errors sufficient
  for convergence of expectations.
- [ ] Prove the corresponding actual-binary sampling theorem with
  $nq_n \to \infty$, fixed error variance, explicit $t_n = \lambda_{1,n}/n$
  and $r_n = \lambda_{2,n}/n$, and changing supports. Keep formal
  fixed-score-noise limits separate; characterize persistent thresholding
  and the order of limits.
- [ ] Characterize persistent versus vanishing nuisance bias under fixed and
  vanishing effective penalties. Compare transferred bias with sampling
  uncertainty, and recover orthogonal shrinkage under explicit conditions.
- [ ] Extend the shrinkage perturbation bound based on $\max(|c|/a,|c|/b)$
  beyond a fixed active-sign region.
- [ ] Write and check the noiseless single-signal theorem for any number of
  binary predictors with positive-definite centered Gram matrix and variance
  weights. Each inactive KKT inequality follows from $|C_{jk}| \le C_{jj}$.
- [ ] Compare nuisance bias transfer with [Hahn et al., Section 2 and equation
  (2.3)](https://arxiv.org/html/1602.02176). The general mechanism and
  covariance-over-variance factor already appear there. Add the relevant
  reference when incorporating this comparison.
- [ ] Compare penalized sampling limits with [Knight and Fu, Section 5 and
  Theorem
  6](https://public.websites.umich.edu/~jizhu/jizhu/KnightFu-AoS00.pdf) and
  [Knight](https://doi.org/10.1017/S0266466608080146). A singular limiting
  Gram matrix alone does not establish novelty.
- [ ] Document overlap with [Ewald and
  Schneider](https://arxiv.org/html/1708.09608v3), [Lee et
  al.](https://arxiv.org/html/1311.6238v8), weighted irrepresentable
  conditions, model-selection theory, rare binary predictors, and penalized
  nuisance adjustment. Treat exact KKT regions, sign dependence, and the
  diagonal impossibility result as supporting material.
- [ ] Compare with [Larsson and Wallin, especially Appendix
  A](https://arxiv.org/html/2501.03821v3). Identify which orthogonal
  conclusions survive and which extrapolations need stronger conditions,
  while preserving the scope of the valid original theorems.
- [ ] Study nuisance residualization against the exact unpenalized-nuisance
  result and existing adjustments. Account for penalized nuisance
  coefficients and unknown supports and signs; residual-variance weights
  alone do not establish a correction.

## Separate task in the original project

- [ ] Resolve the $\omega = 1/2$ boundary correction in the earlier
  weighted-elastic-net variance theorem in `normreg`. The derivation is in
  [the initial investigation](notes/two-feature-investigation.md). Keep this
  correction separate from the present paper's contribution.
