# Research tasks

Consolidated checklist from the [research plan](notes/research-plan.md) and the
September 14, 2026 relevance and novelty assessment. The research plan retains
the mathematical setup and the status of existing results. Items below remain
open until their proofs, comparisons, or experiments are documented.

The strongest candidate contribution is a characterization of how binary rarity,
normalization, and thresholding interact with bias transmitted from nuisance
shrinkage. The targeted literature search has not established novelty.

## First milestone: theory

- [ ] Establish the fixed-dimensional block analogue of the Gaussian coupling
  argument for one rare feature and several common predictors. Specify the
  nuisance penalty, uniform strong convexity of the nuisance problem, moment
  bounds, and approximation errors sufficient for convergence of
  expectations.
- [ ] Prove a sampling theorem for actual binary designs with $n \to \infty$,
  $q_n \downarrow 0$, and $nq_n \to \infty$, using fixed error variance.
  State the rates of $t_n = \lambda_{1,n}/n$ and $r_n = \lambda_{2,n}/n$
  explicitly, and allow support changes rather than assuming a fixed
  active-sign region.
- [ ] Keep the fixed-score-noise Gram limit separate from sampling limits.
  Determine when thresholding persists and whether the order of tuning and
  imbalance limits changes the conclusions.
- [ ] Characterize when nuisance bias vanishes and when its transferred
  contribution persists. Compare fixed effective penalties with penalties
  that vanish as information grows.
- [ ] Compare transferred bias with rare-coefficient sampling uncertainty,
  typically of order $(nq_n)^{-1/2}$ under the proposed regularity
  conditions. Identify when the contribution is negligible on that scale,
  even if both bias and uncertainty vanish.
- [ ] Give conditions that recover the orthogonal answer and a useful finite
  sample or perturbation bound. Start from
  $\max(\lvert c\rvert/a,\lvert c\rvert/b)$, and extend beyond an assumed
  active-sign region to changing supports.
- [ ] Write and check the extension of exact noiseless single-signal shrinkage
  to any number of binary predictors with a positive-definite centered Gram
  matrix. With variance weights, each inactive KKT inequality follows from
  $|C_{jk}| \le C_{jj}$. State the uniqueness and noiseless scope
  explicitly.

## First milestone: literature and novelty

For each comparison, record the exact theorem or equation, assumptions,
conclusions, and whether it already implies a candidate claim here. Add the
relevant sources to `paper/references.bib` and discuss them in the manuscript.

- [ ] Compare bias transfer with [Hahn et al., regularization-induced
  confounding](https://arxiv.org/html/1602.02176), especially Section 2 and
  equation (2.3). The general mechanism and the covariance-over-variance
  factor already appear there; isolate what binary rarity, normalization,
  and thresholding add.
- [ ] Compare the proposed sampling theorem with [Knight and Fu, Section 5 and
  Theorem
  6](https://public.websites.umich.edu/~jizhu/jizhu/KnightFu-AoS00.pdf) and
  [Knight, nearly singular
  designs](https://doi.org/10.1017/S0266466608080146). Allowing a singular
  limiting Gram matrix alone is insufficient as a novelty claim. Check the
  penalty rates, design assumptions, and limiting conclusions.
- [ ] Establish the overlap with [Ewald and Schneider's weighted-lasso
  distribution theory](https://arxiv.org/html/1708.09608v3) and [Lee et
  al.'s polyhedral selection framework](https://arxiv.org/html/1311.6238v8).
  Identify the precise additional value of the explicit bivariate
  elastic-net selection integrals and moments.
- [ ] Trace weighted irrepresentable conditions, model-selection theory, rare
  binary predictors, and penalized nuisance adjustment. Assess the general
  single-signal result against the relevant weighted-lasso conditions.
- [ ] Compare with [Larsson and Wallin's original
  paper](https://arxiv.org/html/2501.03821v3), especially Appendix A.
  Identify which orthogonal conclusions survive and which extrapolations
  require stronger conditions than vanishing correlation. Preserve the
  distinction between the valid orthogonal theorems and arguments about
  their extension.
- [ ] Write a novelty assessment that distinguishes established general
  machinery, elementary binary consequences, and any new rare-feature
  theorem. Treat the KKT regions, sign-dependent shrinkage, and diagonal
  impossibility result as supporting material unless the comparison warrants
  a stronger claim.

## First milestone: empirical consequences

- [ ] Build a feasible binary-design grid using $(q_1,q_2,p_{11})$ within the
  joint-cell bounds. Include independent, nested, and negatively associated
  designs, with one signal, two equal-sign signals, and opposite-sign
  signals.
- [ ] Compare no scaling, standard-deviation scaling, variance scaling, and
  separate elastic-net weights. Report coefficients on the original feature
  scale and keep the averaged and unaveraged penalty conventions consistent.
- [ ] Use fixed cell counts to isolate conditional theory, then increasing
  samples with growing rare counts. Hold noise levels fixed first, and study
  SNR-matched comparisons separately.
- [ ] Compare numerical integration with simulations before expanding to several
  nuisance predictors. Store realized cell counts, Gram matrices, penalties,
  seeds, and software versions with the results.
- [ ] Measure bias, covariance, coefficient recovery, selection probabilities,
  false selections, and prediction risk. Include prediction within the rare
  subgroup alongside aggregate prediction.
- [ ] Quantify the distinction between coefficient error and prediction risk: an
  isolated $O(1)$ rare-coefficient error contributes only $O(q_n)$ to
  population prediction risk. Demonstrate a consequential effect for a
  stated estimation or prediction objective.
- [ ] Study response-dependent tuning, including cross-validation, separately
  from fixed effective penalties. Test any proposed normalization
  recommendation with tuning, and avoid general optimality claims from a
  small example grid.

## Milestone decision and manuscript

- [ ] Complete a checked sampling theorem, a written comparison with the closest
  prior results, and an experiment showing a consequential difference.
- [ ] Reassess whether the contribution supports a full follow-up paper or a
  focused theoretical note. Revise the title, abstract, and contribution
  claims around the established results.
- [ ] Use the bivariate results as introductory examples and tools for checking
  the general analysis. Keep unproved claims and unresolved novelty
  questions explicit in the manuscript's research-directions section.

## Subsequent research

- [ ] Treat bounded rare counts as a separate sampling regime, with explicit
  assumptions and comparisons to the growing-count regime.
- [ ] Investigate multiple rare features and identify which conclusions depend
  on having only one rare coordinate.
- [ ] Study an adjustment based on nuisance residualization. Compare with the
  exact unpenalized-nuisance result and existing adjustment methods.
  Determine what remains valid with penalized nuisance coefficients and
  unknown supports and signs; residual-variance weights alone do not
  establish a correction.

## Separate task in the original project

- [ ] Resolve the $\omega = 1/2$ boundary correction in the earlier
  weighted-elastic-net variance theorem in `normreg`. The derivation is in
  [the initial investigation](notes/two-feature-investigation.md). Keep this
  correction separate from the contribution of the present paper.
