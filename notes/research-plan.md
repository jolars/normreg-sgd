# Research plan

The active direction is **Learning Rare Features: Normalization, Stochastic
Optimization, and Early Stopping**. The consolidated checklist is in
[TODO.md](../TODO.md).

## Research question

When does normalization accelerate the learning of rare input features under a
finite training budget, and when do dependence and stochastic updates offset
that benefit? The intended contribution connects learning trajectories to
prediction within rare subgroups and under specified prevalence shifts.

The starting model is linear regression with common and rare binary features.
Full-rank convergence to the unregularized optimum gives OLS. Our initial
question concerns early stopping and stochastic error. Selecting among
interpolating solutions is a possible later extension and requires a different
setting.

The elementary calculations below establish a foundation, not standalone
novelty. Early-stopping regularization, geometry-dependent implicit bias, and
adaptive optimization for rare features already have substantial literatures.
The first milestone must identify an additional conclusion about their
interaction with dependence, feature rarity, and batch size.

## Mathematical setup

Use the averaged squared loss. For a fixed centered sample, write
$C = X_c^\top X_c/n$ and $z = X_c^\top y_c/n$. Population calculations instead
use a centered random feature vector $x$, covariance $C = E(xx^\top)$, and
$y = x^\top\beta^* + \varepsilon$ with $E(\varepsilon \mid x) = 0$. Always
identify which experiment a statement describes.

Dividing features by positive scales $s_j$ gives $S = \operatorname{diag}(s)$,
transformed coefficients $\theta = S\beta$, and preconditioner $P = S^{-2}$.
Report $\beta$ on the original feature scale. Population gradient flow from zero
satisfies

$$
  \dot\beta(T) = PC\{\beta^* - \beta(T)\}.
$$

Use $T$ for gradient-flow time, $k$ for update count, $B$ for batch size, and
$\eta$ for the learning rate. For discrete GD, $T = k\eta$ is a time
calibration, while $kB$ counts processed observations in fresh-batch SGD. The
explicit-penalty baselines retain $t = \lambda_1/n$ and $r = \lambda_2/n$;
neither symbol denotes training time.

For the multivariate population setup, partition the covariance as

$$
  C_n = \begin{pmatrix}
          A_n      & c_n \\
          c_n^\top & b_n
        \end{pmatrix},\qquad A_n
      \to A
      \succ 0,\quad b_n
      \downarrow 0,\quad c_n/b_n
      \to \kappa.
$$

The common block initially has fixed dimension. The rare coordinate is binary,
with prevalence $q_n$ and variance $b_n = q_n(1 - q_n)$. Actual binary designs
must satisfy their joint-cell bounds. The finite-time formulas separate
incomplete learning of the common coefficients, rare-feature learning, and
stochastic update moments under known population centering and fixed scales.

## Current foundation

  | Result                                            | Status and scope                                                                                                                                                                                     |
  | ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | Feature scaling as preconditioning                | Standard exact change of coordinates for fixed scales.                                                                                                                                               |
  | Transient dependence under early stopping         | Proved for a fixed common block and one rare binary feature, uniformly on bounded population-flow time intervals, with convergent original-scale initialization.                                     |
  | Scalar SGD stability                              | Exact second-moment recurrence for a noiseless standardized Bernoulli predictor and fresh independent batches.                                                                                       |
  | Finite-update GD and fresh-sample SGD moments     | Exact mean, second-moment, and centered covariance formulas, with initial uncertainty, multiplicative update variance, and observation noise separated.                                              |
  | Multivariate batch-rarity stability               | Exact operator criterion and three-regime threshold limits for a uniformly bounded fixed common block with positive definite limiting covariance.                                                    |
  | Matched covariance and sampling schemes           | Feasible binary distributions with different fourth update moments, exact conditional replacement and reshuffling epoch identities, and first-pass equivalence under fixed population preprocessing. |
  | Independent numerical checks                      | Support-based ODE integration, block limits, exact batch and short-trajectory enumeration, mixed moments, and stability eigenvalues.                                                                 |
  | Explicit-regularization baselines                 | Existing bivariate lasso and elastic-net formulas, ridge moments, and binary counterexamples are retained in the appendices.                                                                         |
  | Joint sampling limits and comparative experiments | Open research objectives, including estimated centering/scales and fixed-data sampling.                                                                                                              |
  | Standalone novelty                                | Unresolved; the elementary calculations are supporting results.                                                                                                                                      |

For standard-deviation scaling in the two-feature population model,
$c/b \to \kappa$ gives, at fixed $T$,

$$
  \beta_2(T) \longrightarrow (1 - e^{-T})\beta_2^* + \kappa T e^{-T}\beta_1^*.
$$

Thus a common feature can contribute to the rare coefficient during training
even while Pearson correlation vanishes. This transient contribution can exist
when the true rare coefficient is zero. It is not a lasso selection event or a
claim of asymptotic inconsistency.

For a standardized Bernoulli predictor $Z$, the population curvature is one, but
$\mu_4 = E(Z^4) \sim q^{-1}$. In the scalar noiseless model with fresh
independent batches, mean-square contraction requires

$$
  0 < \eta < \frac{2}{1 + (\mu_4 - 1)/B}.
$$

The upper bound is asymptotic to $2Bq$ when $Bq \to 0$. This example separates
population curvature from stochastic stability. Scalar rescaling can be absorbed
into the learning rate; the substantive normalization question involves relative
updates across several feature frequencies. Population scales and centering are
known here. The result is not a guarantee for adaptive optimizers or for random
reshuffling of a fixed dataset.

The block extension allows common scales $D_n \to D \succ 0$ and rare scales
with $b_n/s_{R,n}^2 \to \rho \in [0,\infty)$. Its rare-coordinate limit is a
convolution of the remaining common error with the rare response at rate $\rho$.
Discrete GD and the fresh-SGD mean have the corresponding finite-sum formula at
each fixed update count. Exact covariance formulas require finite fourth feature
moments and finite gradient-noise moments in each population; these conditions
alone give no uniform rare-limit covariance bound.

For a uniformly bounded common block under population standard-deviation
scaling, the all-initializations mean-square stability threshold is
$\Theta(\min\{1,Bq\})$. It is asymptotic to $2Bq$ for small $Bq$. The
intermediate limit also depends on the largest eigenvalue of the standardized
common covariance, and the large-$Bq$ limit recovers the population GD
threshold. Mixed fourth moments affect finite-prevalence stability. With small
$Bq$, a stable shared learning rate can also slow common-feature learning. These
results distinguish updates from processed observations and noiseless
contraction from a nonzero observation-noise floor.

A three-binary-feature construction keeps the means, covariance, and marginal
distributions fixed while changing mixed fourth moments. The resulting SGD
second moments and finite-prevalence stability thresholds differ, although
population flow and the fresh-SGD mean agree. Conditional fixed-data replacement
requires an empirical score and curvature-residual cross terms. Random
reshuffling instead has an exact recurrence at epoch boundaries; its first pass
has the fresh-sample law only unconditionally over an iid dataset, with fixed
population preprocessing and independent initialization. The full proofs and
counterexamples are in [sampling schemes](sampling-schemes.md).

The derivations are in [the manuscript](../paper/main.tex). Run all
deterministic checks with `make check-optimization` inside `devenv shell`: the
[elementary checks](../experiments/check_optimization.py), [block-flow
checks](../experiments/check_block_flow.py), [finite-update moment
checks](../experiments/check_discrete_dynamics.py), and [multivariate stability
checks](../experiments/check_multivariate_stability.py), together with
[sampling-scheme checks](../experiments/check_sampling_schemes.py).

## First milestone and empirical objective

The first milestone combines a checked finite-time result for a rare feature
with common predictors, a comparison with the closest prior theorems, and one
controlled experiment showing a consequential difference. The population-flow
and fresh-SGD results now supply the initial theory under their stated
assumptions. Joint sampling limits, finite-data resampling, empirical
normalization, validation-based stopping, and adaptive optimizers need explicit
additional assumptions.

The primary outcomes are original-scale coefficient error, aggregate excess
prediction risk, and excess prediction risk conditional on rare-feature
presence. An isolated constant rare-coefficient error has only $O(q_n)$ weight
in aggregate risk. A test prevalence shift should preserve the conditional
response model and retain training centering and scales at prediction time. This
makes the shift interpretable and avoids conflating coefficient effects with a
changed intercept.

Comparisons should use matched numbers of processed observations and separately
tuned learning rates. Update count alone is insufficient when batch size
changes. Synthetic binary designs provide exact controls. Sparse text or
categorical data, first with linear models and then a small neural model,
provide the intended empirical progression. This is a research design, not an
empirical result or a claim that one normalization is universally preferable.

## Role of the earlier investigation

The original shrinkage analysis supplies explicit-regularization baselines and
examples of why covariance divided by feature variance matters. Exact Gaussian
region integration remains useful for checking those baselines; it does not
validate stochastic optimization dynamics.

The former main objective, a general sampling theorem for penalized nuisance
bias transfer, is deferred. Its formal fixed-score-noise precursor must remain
separate from actual binary sampling limits. Related theory, literature
comparisons, and the boundary correction in the original `normreg` project are
preserved in [TODO.md](../TODO.md). The initial derivations remain in
[two-feature-investigation.md](two-feature-investigation.md).
