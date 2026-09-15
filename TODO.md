# Research tasks

The active direction is **Normalization and Implicit Regularization in
Stochastic Learning**. The [research plan](notes/research-plan.md) studies how
normalization, learning rate, batch size, and stopping time jointly determine
the fitted model and its statistical properties. It builds on `../normreg` and
retains SGD and implicit regularization as the follow-up's ML direction.

The completed calculations and pilot below provide a foundation. The next
milestone is to explain their joint interactions and resulting models. Johan
will conduct the literature review separately; novelty and publication format
remain undecided.

## Current priorities: joint interactions

- [ ] Specify the normalization family, learning-rate schedules, batch sizes,
  stopping counts, sampling assumptions, and outcomes in
  `notes/joint-interactions.md`. Include fixed-update and fixed-observation
  comparisons, plus global-rescaling controls.
- [ ] Use the exact moments to derive a comparison across normalization and
  optimization settings. Explain learning, noise, and risk changes in a
  feasible two-feature model, with independent proof and numerical checks.
- [ ] Design a separate follow-up to the frozen pilot that retains the joint
  configuration grid and training paths. Test predicted interactions and
  reversals, wider learning-rate ranges, uncertainty, and budget
  sensitivity.
- [ ] Test practical preprocessing and validation-based choices, then a stated
  real-data task. Compare defaults and joint tuning with equal search
  effort, while preserving the fixed-configuration results that explain the
  effects.

The research plan gives the scope and completion criteria for these steps.

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
  observations.
- [ ] Identify conditions recovering the independent-feature trajectory and a
  useful approximation bound when dependence is weak relative to feature
  variance. Avoid relying on Pearson correlation alone.
- [ ] Study early stopping chosen in advance before validation-based stopping.
  Do not infer finite-budget performance from population-flow time alone.

## Literature and novelty: separate review

Johan owns the next literature review. The earlier audit and checklist are
retained as inputs. For each source, record the exact theorem or equation, its
assumptions and conclusions, and whether it already implies a candidate result.
Relevant core optimization references are in `paper/references.bib`; the
comparisons remain open except for the bounded eight-source [theorem-level
audit](notes/novelty-audit.md). It identifies established operator and stability
frameworks; priority for the specific rare-limit calculations remains
unresolved.

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
- [ ] Write the novelty assessment around whichever dependence, sampling, or
  rare-subgroup risk result survives these comparisons. The coordinate
  change, bivariate matrix exponential, and scalar stability calculation are
  supporting material unless the literature comparison warrants more.

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
- [ ] Add a separately specified fresh-sample experiment and compare its
  conclusions with repeated passes over a fixed training sample.
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
  rare-feature definition. Start with linear models, then test the proposed
  mechanism in a small neural model with comparable tuning effort.
- [x] Complete a bounded foundation milestone: an independently reviewed
  joint-budget theorem, an eight-source overlap audit, and a reproducible
  controlled experiment with substantial risk differences and reversals.
  Broader novelty comparisons and empirical usefulness remain open.
- [ ] Assess novelty and publication scope using the separate literature review
  and the results of the joint-interaction study. Earlier overlap findings
  concern selected mathematical tools and do not determine the final format.
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
