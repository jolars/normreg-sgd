# C2 against target-risk and subgroup-risk antecedents

September 15, 2026. This note completes the bounded C2 literature task in
[TODO.md](../TODO.md), starting with Liu et al. (S15) and extending the [source
audit](normalization-risk-audit.md) through S17–S20. It assesses the scientific
content of the [existing C2 theorem](normalization-risk-theorem.md). It does not
change its proof or claim exhaustive priority coverage.

## Decision

**Retain C2 as a quantitative SGD illustration; its present statement does not
yet establish a substantive advance over target-risk theory.** Subgroup
conditioning is exactly a change of test distribution. Strict benefits of
target-aware regularization and average/subgroup tradeoffs have antecedents.
Even the combination of larger coefficient MSEs and smaller subgroup prediction
risk follows from a simple deterministic construction below.

What C2 supplies beyond that construction is a realization by two conventional
normalization rules, with stable fresh-sample SGD, matched observation budgets,
and certified dependence and noise intervals. None of the inspected statements
directly gives those inequalities. That is a useful calculation, but absence of
the particular U/S pair from a paper is insufficient evidence of novelty.

## Conditioning gives an ordinary target-risk problem

Use the theorem's binary law, original-scale coefficients, known population
centering and scales, fixed zero intercept, zero initialization, and independent
training and test samples. Risks exclude irreducible test noise. Let $P$ be the
training law of $(x,y)$ and let $Q_R=P(\cdot\mid J=1)$. Because $J$ is
determined by $x$,

$$
  \frac{dQ_R}{dP}(x,y)=\frac{\mathbf{1}\{J=1\}}q,
  \qquad Q_R(y\mid x)=P(y\mid x)
$$

on the target support. This is well-specified covariate shift. For an
independent test point and
$V_k=E[(\hat\beta_k-\beta^*)(\hat\beta_k-\beta^*)^\top]$,

$$
  R_{R,k}=\frac12\operatorname{tr}(C_RV_k),\qquad
  C_R=E_{Q_R}[xx^\top]
  =\begin{pmatrix}
    1/4&\ell(1-q)/2\\
    \ell(1-q)/2&(1-q)^2
  \end{pmatrix}.
$$

Keep the source centering when evaluating this matrix. Subtracting the target
mean would remove part of the prediction error and change the question. At
$\ell=1$, $C_R=vv^\top$ for $v=(1/2,1-q)^\top$, so subgroup prediction measures
the error in a single linear combination of coefficients. Rank-one targets
already appear in Liu et al. and Lei et al.; the former's spectral-decay theorem
is not automatically applicable to this fixed-dimensional example. [Liu et al.,
Sections 3.1 and 5.3.1](https://arxiv.org/html/2502.09047v1), [Lei et al.,
Theorem 3.4](https://proceedings.mlr.press/v139/lei21a/lei21a.pdf#page=4).

Let $C_0=E[xx^\top\mid J=0]$. Conditioning also gives

$$
  C=(1-q)C_0+qC_R,\qquad C_R\preceq C/q,
  \qquad R_{R,k}\leq R_k/q.
$$

The stronger bound $R_k\leq R_{R,k}$ in the earlier audit used independence; it
does not hold for every dependent law. At nesting, an error orthogonal to $v$
has zero rare risk and positive aggregate risk. An aggregate upper bound can
therefore bound subgroup risk, but need not identify a preferred configuration.

Under the convention $D_{\chi^2}(Q\|P)=E_P[(dQ/dP-1)^2]$, direct conditioning
gives

$$
  D_{\chi^2}(Q_R\|P)=1/q-1.
$$

Thus the subgroup is also a particular reweighting inside a divergence-ball
formulation. The mixture-to-group-risk connection is explicit in [Hashimoto et
al., Proposition
2](https://proceedings.mlr.press/v80/hashimoto18a/hashimoto18a.pdf#page=5). The
exact divergence above is our calculation for the conditioning law, not their
displayed general choice of robustness radius. C2 neither trains a DRO estimator
nor controls every distribution in that ball.

## What the inspected results establish

The audit records versions, inspected passages, assumptions, and
classifications. The implications for C2 are:

  | Source                | Consequence for the proposed contribution                                                                                                                        |
  | --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | S15: Liu et al.       | Different source and target moments already guide preconditioning. Their minimax and scheduled-SGD results do not directly order C2's fixed configurations.      |
  | S17: Lei, Hu, and Lee | A target-aware estimator already separates from optimally tuned ridge in a worst-case comparison. A strict comparison alone is insufficient.                     |
  | S18: Wu et al.        | Target risk of the last online-SGD iterate is established territory. Their lower fourth-moment assumption fails for our common binary feature.                   |
  | S19: Hashimoto et al. | Minority-group risk is already represented by population reweighting and bounded through distributional robustness.                                              |
  | S20: Sagawa et al.    | Regularization and early stopping already enter empirical average/worst-group tradeoffs. C2 evaluates one fixed subgroup rather than optimizing the worst group. |

## A control that reproduces the coefficient-error feature without SGD

Write $\Delta V=V^S-V^U$. The comparisons in C2 have the form

$$
  \operatorname{tr}(C\Delta V)>0,\qquad
  \operatorname{tr}(C_R\Delta V)<0,
  \qquad \Delta V_{CC},\Delta V_{RR}>0.
$$

These conditions imply that $\Delta V$ is indefinite: neither estimator
dominates in the positive-semidefinite matrix order. Comparing its diagonal
entries alone cannot rank all prediction losses. This is elementary quadratic
geometry, and the diagonal comparison depends on the chosen feature basis.

To test how much the sign pattern itself says, keep the same feature law with
$q=1/50$ and $\ell\in[0.9,1]$. At C2's fixed signal $\beta^*=(2,1)^\top$, the
constant estimators $(2,2)^\top$ and $(3,-1/5)^\top$ have errors

$$
  e^{(a)}=(0,1)^\top,\qquad e^{(b)}=(1,-6/5)^\top.
$$

Their error-moment contrast is

$$
  \Delta V=e^{(b)}e^{(b)\top}-e^{(a)}e^{(a)\top}
  =\begin{pmatrix}1&-6/5\\-6/5&11/25\end{pmatrix}.
$$

Both coefficient MSEs increase. Direct multiplication by the theorem's test
matrices gives the exact terminating decimals

$$
  \Delta_A=0.129312-0.012\ell\in[0.117312,0.118512],
$$

$$
  \Delta_R=0.336288-0.588\ell\in[-0.251712,-0.192912].
$$

This reproduces all four signs throughout the same dependence interval,
including interior laws with four positive cells. It requires neither response
noise nor stochastic optimization. These are constructed errors for fixed
estimators, not outputs of C2's training procedure. The construction therefore
does not derive C2 or contradict it; it isolates the elementary part of its
interpretation. The additional work in C2 is to show how actual training
produces such an error matrix.

## Translate C2 into a target-mixture comparison

An interpretable consequence uses test laws
$Q_\pi=(1-\pi)P(\cdot\mid J=0)+\pi P(\cdot\mid J=1)$. The training law,
centering, scales, and fitted configurations remain fixed. Only the test mixture
weight changes. Write $R_{0,k}$ for risk conditional on $J=0$. For each fit,

$$
  R_{\pi,k}=(1-\pi)R_{0,k}+\pi R_{R,k}.
$$

For S-minus-U contrasts, C2's signs yield a unique crossing

$$
  \pi_* = q+\frac{(1-q)\Delta_A}{\Delta_A-\Delta_R},
  \qquad q<\pi_*<1.
$$

At the theorem's nested anchor ($\ell=1$, $\sigma^2=4$, and 100 source
observations), $\pi_*\approx0.03721957$. U has smaller test risk below this
weight and S above it. Thus the original 2% mixture and the rare-only target
favor different fits, with the switch at about 3.72%. This is an algebraic
restatement of the existing risk values, not evidence from training at another
prevalence or a new distribution-shift theorem. A maximum over group risks is a
different objective from evaluating one chosen $\pi$.

## Scope of the retained claim and next scientific test

C2 supports the following limited conclusion: conventional relative feature
scaling can produce coefficient-error cross moments that improve a designated
rare subgroup while worsening aggregate prediction and both original-scale
coefficient MSEs, under explicit finite-budget training conditions. The cross
moment includes products of biases as well as centered covariance. The result
does not require misspecification, interpolation, or a change of response law.

Before making this the principal contribution:

1. Test whether the disagreement survives a declared learning-rate and stopping
   range at comparable observation budgets. Report both objective minima over
   that range, and preserve fixed-pair results and failures.
2. Seek a condition involving prevalence, feasible dependence, signal, and noise
   that predicts when SGD produces the required indefinite error contrast.
   Changing target weights after the error matrix is known does not supply that
   training explanation.
3. Compare any resulting claim with target-aware and subgroup-aware baselines
   under matched information and budgets. Avoid inferring different global
   optima from one pair: target weights can share an optimal estimator, as [Lei
   et al., Proposition
   3.5](https://proceedings.mlr.press/v139/lei21a/lei21a.pdf#page=4)
   demonstrates under its Bayesian assumptions.

These are the remaining robustness and contribution decisions, not unfinished
parts of the bounded source comparison. The current assessment is provisional
and separate from C2's completed mathematical review.

## Verification

The conditioning, mixture, and deterministic-error calculations above have
direct algebraic proofs. As arithmetic checks, exact rational four-cell sums
verified the identities at 20 feasible prevalence/dependence choices. A separate
two-by-two rational update calculation at the C2 anchor reproduced its risks and
the displayed mixture crossing without calling the existing moment routines.
Those checks are distinct from uniform certificates and literature judgments.

Inside `devenv shell`, `make check-normalization-risk` passes the existing
independent update checks and both continuous-box certificates. Its C2 anchor
risks, together with the displayed formula for $\pi_*$, reproduce the new
rounded mixture weight. No reference artifacts were regenerated.
