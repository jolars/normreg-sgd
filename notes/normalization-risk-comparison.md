# Candidate comparison: normalization, stopping, and batch size

September 15, 2026. Follows the plan committed at `1b2024d` and the [first
fresh-sample study](joint-interactions-results.md).

## Status and decision

**C1 now has a written proof and a continuous-box certificate.** The [proof
note](normalization-risk-theorem.md) gives a scalar threshold bound with a
controlled remainder, proves the four signs over the original parameter box, and
adds a dependent-feature aggregate/subgroup comparison, C2. Independent proof
review is tracked there. The [expanded source
audit](normalization-risk-audit.md) identifies close prior art. The [target-risk
comparison](target-risk-comparison.md) retains C2 as the stronger quantitative
illustration, but its current fixed-pair statement does not establish a
substantive advance over that literature. Novelty remains unresolved.

This note preserves the original conjecture and exploratory calculations. Those
numerical checks alone cover only a finite grid. Both the box and the
noise-threshold analysis were chosen after inspecting the earlier results. The
frozen study is unchanged.

## Model and matched training configurations

Let $I\sim\operatorname{Bernoulli}(1/2)$ and $J\sim\operatorname{Bernoulli}(q)$
be independent, with $0<q<1/2$. Set

$$
  x=(I-1/2,J-q)^\top,\qquad
  y=x^\top\beta^*+\varepsilon,\qquad
  E(\varepsilon\mid x)=0,\qquad E(\varepsilon^2\mid x)=\sigma^2.
$$

The four joint-cell probabilities are $((1-q)/2,q/2,(1-q)/2,q/2)$ in
lexicographic order. Population centering, scales, and the zero intercept are
known and fixed. Start from zero and use fresh independent batches, including
fresh response noise. The test point is independent of training and follows the
same law. No Gaussian assumption is needed for these second moments.

Write $a=1/4$ and $b=q(1-q)$. Compare no scaling, denoted U, with
standard-deviation scaling, denoted S:

$$
  P_U=I_2,\qquad \eta_U=h/a=4h,
  \qquad P_S=\operatorname{diag}(a^{-1},b^{-1}),\qquad \eta_S=h.
$$

Here $h>0$ is the common-coordinate mean contraction per update. It calibrates
the learning rates, rather than introducing an additional training parameter.
Both methods have common mean error $-(1-h)^k\beta_C^*$. Their rare mean errors
are $-(1-4hb)^k\beta_R^*$ and $-(1-h)^k\beta_R^*$, respectively. Batch size does
not enter these mean formulas.

Use the same $B$, $k$, signal, and noise variance within every U/S comparison.
Each method then consumes $M=kB$ distinct observations. Across batch sizes,
report both $k$ and $M$; there is no claim of equal wall-clock cost. Steps are
constant and fixed by the calibration, with no oracle or validation tuning and
no iterate averaging.

For the original-scale error second moment $V_k$, define

$$
  R_k=\tfrac12\{a V_{CC,k}+b V_{RR,k}\},\qquad
  R_{R,k}=\tfrac12\{a V_{CC,k}+(1-q)^2 V_{RR,k}\}.
$$

The rare test second moment is $\operatorname{diag}(a,(1-q)^2)$, including its
conditional mean. These are excess risks, excluding irreducible test noise.
Define the comparison as SD scaling minus no scaling:

$$
  \Delta_{B,k}=R_{R,k}^{S}-R_{R,k}^{U}.
$$

## A two-dimensional moment reduction

Let $d=(d_C,d_R)$ be the diagonal of $\eta P$, so that $d_U=(4h,4h)$ and
$d_S=(4h,h/b)$. Put $v_k=(V_{CC,k},V_{RR,k})^\top$. The proposed reduction is

$$
  v_{k+1}=K_d v_k+\sigma^2 g_d,\qquad
  v_0=((\beta_C^*)^2,(\beta_R^*)^2)^\top,
$$

$$
  K_d=
  \begin{pmatrix}
    (1-d_Ca)^2 & d_C^2 ab/B\\
    d_R^2 ab/B & (1-d_Rb)^2+d_R^2 b(1-4b)/B
  \end{pmatrix},\qquad
  g_d=\frac1B(d_C^2a,d_R^2b)^\top.
$$

To derive it, expand one original-scale update and use $E x_C^4=a^2$,
$E x_R^4=b(1-3b)$, and $E x_C^2x_R^2=ab$. Independence and
$E x_C=E x_R=E x_C^3=0$ eliminate the terms coupling diagonal moments to
$V_{CR,k}$. Cross-coordinate squared errors still couple through the
off-diagonal entries of $K_d$. This is a specialization of the existing [moment
identities](../paper/sections/discrete-dynamics.tex).

Consequently,

$$
  v_k=K_d^k v_0+\sigma^2\sum_{j=0}^{k-1}K_d^j g_d.
$$

The homogeneous term includes squared bias and variance from sampling features.
Subtract the squared mean errors to separate those components. The sum is
observation-noise variance after propagation through the random updates.

With $w_R=(a,(1-q)^2)^\top/2$, define

$$
  F_{B,k}=w_R^\top(K_S^k-K_U^k)v_0,\qquad
  N_{B,k}=w_R^\top\sum_{j=0}^{k-1}(K_S^j g_S-K_U^j g_U).
$$

Then $\Delta_{B,k}=F_{B,k}+\sigma^2N_{B,k}$. Whenever $F_{B,k}<0<N_{B,k}$, the
noise-variance threshold is $\tau_{B,k}=-F_{B,k}/N_{B,k}$: SD scaling has lower
rare risk below this threshold and higher rare risk above it. This affine
dependence is useful machinery; it is not itself the proposed novel result.

## Numerical anchor and conjecture C1

At $q=0.02$, $h=0.002$, and $\beta^*=(1,1)^\top$, the checked calculations give:

  | $B$ | $k$    | $M$     | $F_{B,k}$       | $N_{B,k}$      | $\tau_{B,k}$     |
  | --- | ------ | ------- | --------------- | -------------- | ---------------- |
  | 1   | 1,000  | 1,000   | -0.340294500216 | 0.024674678258 | 13.791243665305  |
  | 1   | 10,000 | 10,000  | -0.021107501896 | 0.023916966352 | 0.882532574787   |
  | 10  | 1,000  | 10,000  | -0.341998835428 | 0.002366751306 | 144.501382354516 |
  | 10  | 10,000 | 100,000 | -0.020886937184 | 0.002280475639 | 9.159026664873   |

The original noise variance one lies between the late thresholds. The calculated
interval approximately $(0.882533,9.159027)$ gives all four signs below at this
anchor. These floating-point values are not certified bounds.

**Conjecture C1.** For every parameter choice in

$$
  q\in[0.019,0.021],\qquad h\in[0.0019,0.0021],\qquad
  \beta_C^*,\beta_R^*\in[0.95,1.05],\qquad \sigma^2\in[1.5,5],
$$

the two training rules are mean-square stable for $B\in\{1,10\}$ and satisfy

$$
  \Delta_{1,1000}<0<\Delta_{1,10000},\qquad
  \Delta_{10,1000}<0,\qquad \Delta_{10,10000}<0.
$$

This single statement supplies a stopping reversal at $B=1$, a normalization
ordering change across batches at fixed $k=10{,}000$, and an ordering change
across batches at fixed $M=10{,}000$ using $(B,k)=(1,10{,}000)$ and
$(10,1{,}000)$. It does not order batch sizes within either normalization rule.

The exploratory grid uses five equally spaced values each of $q$ and $h$, three
values per signal coefficient, and the two endpoints of the noise interval.
Across its 225 choices of $(q,h,\beta_C^*,\beta_R^*)$:

- The largest lower noise threshold is 1.309861513678.
- The smallest of the upper thresholds is 6.039409999202.
- The smallest signed rare-risk gap is 0.002356210411.
- The largest spectral radius of the reduced moment matrices is 0.999717703610.

These checks leave gaps between grid points. The noise interval starts at 1.5 to
allow simultaneous variation of the other parameters; the original $\sigma^2=1$
anchor does not imply this wider-box statement.

## Original completion criteria

The [proof note](normalization-risk-theorem.md) now supplies the reduction,
stability proof, uniform bounds, and a controlled threshold approximation
requested below. Independent review and subsequent robustness work are tracked
separately.

1. Verify the reduction and give uniform stability bounds, including control of
   the cross moment.
2. Bound the four contrasts over the continuous box, with positive risk-gap
   bounds. They are affine in $\sigma^2$, $(\beta_C^*)^2$, and $(\beta_R^*)^2$,
   so those variables reduce to endpoint checks. The dependence on $q$ and $h$
   needs separate uniform control.
3. Explain the threshold bounds using relative learning, batch size, and the
   noise contribution. A certificate for a small box establishes existence;
   useful threshold or prevalence bounds are the stronger scientific target.
4. Obtain independent proof review and preserve numerical checks as a separate
   form of validation. Evaluate retuning and dependence in the subsequent
   robustness study before making practical recommendations.

There is no claimed unique crossing in $k$, universal normalization preference,
or optimal configuration. Under independence, the diagonal reduction depends on
squared signal coefficients, so changing signal signs alone cannot change these
risks. Sign-dependent conclusions need an additional mechanism, such as feature
dependence.

Aggregate-versus-subgroup disagreement was a separate target. At the anchor with
$B=1$, $k=10{,}000$, its two calculated noise thresholds are 0.882605636639 and
0.882532574787, respectively. Their small difference permits opposite signs only
in a narrow noise interval here. That observation motivates seeking a
consequential risk gap, rather than using the mere existence of an objective
reversal as sufficient evidence of scientific importance. C2 now supplies a
larger disagreement under feasible dependence, including a sign-dependent
mechanism.

## Reproduction

Inside `devenv shell`, run `make check-normalization-risk`. The [check
script](../experiments/check_normalization_risk_candidate.py) prints the anchor
table and exploratory summary without writing reference artifacts. It checks 80
endpoints against the existing full moment implementation, including short paths
independently enumerated from individual gradient updates. The checks cover two
prevalences, two rates, both normalization rules, both batch sizes one and two,
and a mixed-sign signal. They do not constitute independent proof review. The
target also runs the separate [interval
certificate](../experiments/check_normalization_risk_theorem.py), and both run
through `make check-optimization`.
