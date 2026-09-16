# Proposed predictive risk expansion

September 16, 2026. The [one-page proposed claim](../paper/proposed-claim.tex)
addresses the first milestone in [TODO.md](../TODO.md). This note supplies its
definitions, source comparison, development checks, and proof decision. It
builds on the [risk audit](normalization-risk-audit.md), [target-risk
comparison](target-risk-comparison.md), and exact moments in [Proposition
1](normalization-risk-theorem.md). It does not promote the proposal into the
conference manuscript or alter the frozen studies.

**A prevalence-uniform risk expansion with the first feedback correction now has
a local feasibility proof.** The [proof note](predictive-claim-feasibility.md)
establishes stability and the uniform quadratic remainder with $K=104/3$, with
sharper constants by objective and error component. Independent proof review,
human review, and publication-level novelty remain open. The leading
approximation alone gets the small C2 aggregate contrast wrong; that failure is
retained below.

The subsequent [predictive-regime note](predictive-regime.md) derives explicit
rare- and common-signal families with opposite oracle rare-risk orderings over
continuous rate and stopping sets. It covers independent features,
$0<q\leq10^{-4}$, and $1\leq Mq(1-q)\leq4$. Its source comparison retains the
result as a supporting specialization, pending mathematical and novelty review.

A subsequent [self-contained theorem](predictive-theorem.md) proves those same
predictive guarantees directly from the independent-feature moment recurrence.
Its separate checker verifies the continuous certificate without importing the
earlier implementations. The general stability and remainder theorem remains
useful for dependence and batches. Mathematical correctness, the precise
addition to prior work, and the result's role in the paper are tracked
separately; independent proof review and human review remain open.

## Model and intended statement

Use the feasible binary law

$$
  P(I=1)=1/2,\quad P(J=1)=q,\quad
  P(I=1,J=1)=q(1+\ell)/2,\quad
  x=(I-1/2,J-q)^\top.
$$

Its four probabilities are those in the existing theorem, with no extra sampling
approximation. The response is $y=x^\top\beta^*+\varepsilon$, with
$E(\varepsilon\mid x)=0$ and $E(\varepsilon^2\mid x)=\sigma^2$. Training uses
known population centering and scales, a fixed zero intercept, zero
initialization, constant steps on the averaged loss, and $B$ new independent
observations at each update. The final iterate is evaluated on an independent
test point. All coefficients are on the original feature scale. Risks include
one half and exclude irreducible noise. There is no Gaussian-noise requirement.

Write $a=1/4$, $b=q(1-q)$, $c=q\ell/2$, and
$D=\eta P=\operatorname{diag}(u/a,v/b)$. Thus $u$ and $v$ are the common and
rare diagonal mean drifts per update, rather than two additional learning rates.
Dividing the columns by $(a^\delta,b^\delta)$ and taking $\eta=u a^{2\delta-1}$
gives $v=u(4b)^{1-2\delta}$. The proposed domain is

$$
  0<q\leq1/16,\quad |\ell|\leq1,\quad B\in\{1,2,\ldots\},\quad
  0<u\leq1/4,\quad 0\leq\delta\leq1/2,\quad
  \theta:=v/(bB)\leq1. \tag{P1}
$$

Unscaled U has $(u,v)=(h_U,4bh_U)$; SD-scaled S has $(u,v)=(h_S,h_S)$. The
common-learning calibration is $h_U=h_S$, and adjusted comparisons allow them to
differ. Rates outside (P1), schedules, averaging, estimated preprocessing, and
fitted intercepts are outside this proposed theorem. The zero-step predictor is
included separately and has exact zero approximation error. The feasibility
proof establishes $\rho(|L|)<1-v/4$ throughout (P1), independently of numerical
eigenvalue checks.

Let $W=C$ or $C_R$, where

$$
  C=\begin{pmatrix}a&c\\c&b\end{pmatrix},\qquad
  C_R=\begin{pmatrix}a&\ell(1-q)/2\\\ell(1-q)/2&(1-q)^2\end{pmatrix}.
$$

Source centering is retained in $C_R$, including its conditional mean. With
$w_W=(W_{CC}/2,W_{CR},W_{RR}/2)^\top$, the intended conclusion is

$$
  |R_{W,k}-\widehat R_{W,k}|\leq E_{W,k}
  \leq Kq^2\left[\|\beta^*\|_2^2e^{-kv/4}
        +\sigma^2\{u/B+\theta\}\right],\qquad k\geq0. \tag{P2}
$$

The original proposal conjectured the existence of an explicit $K$ independent
of every parameter in (P1), $k$, the signal, and the noise. The [feasibility
proof](predictive-claim-feasibility.md) now establishes (P2) with $K=104/3$,
without restricting $k$ or introducing hidden $q^{-1}$ constants. Its sharper
bound is

$$
  E_{W,k}\leq\frac{8\mu_Wq^2}{1-4q}
  \left[\|\beta^*\|_2^2(1-v/4)^k
        +2\sigma^2\{u/B+\theta\}\right],\qquad
  \mu_W=|w_W|^\top(1,1,2)^\top.
$$

This bounds the same finite remainder $E_{W,k}$ defined below. The constants are
sufficient rather than optimal; the proof is pending independent and human
review. A subsequent [local comparison](predictive-regime.md) supplies explicit
predictive regimes after calibration for independent features.

## Approximation from the exact recurrence

Put $d_C=u/a$, $d_R=v/b$,

$$
  t_B=c^2+(ab-c^2)/B,\qquad
  m_B=c\{b+(1-4b)/B\},\qquad
  g=(d_C^2a,d_Cd_Rc,d_R^2b)^\top/B.
$$

For the exact error vector $s_k=(V_{CC,k},V_{CR,k},V_{RR,k})^\top$, write its
existing recurrence as $s_{k+1}=Ls_k+\sigma^2g$. Split $L=L_0+H$, where

$$
  L_0=\begin{pmatrix}
  (1-u)^2&0&0\\
  -d_R(1-u)c&(1-u)(1-v)&0\\
  d_R^2t_B&-2d_Rc+2d_R^2m_B&(1-v)^2+d_R^2b(1-4b)/B
  \end{pmatrix},
$$

$$
  H=\begin{pmatrix}
  0&-2d_C(1-u)c&d_C^2t_B\\
  0&d_Cd_Rt_B&-d_Cc+d_Cd_Rm_B\\
  0&0&0
  \end{pmatrix}. \tag{P3}
$$

$L_0$ is the moment map of a surrogate update obtained by setting the upper
right entry of $I-D\widehat C$ to zero. The noise vector $D\bar{x\varepsilon}$
is unchanged, including its cross-coordinate covariance. This surrogate uses the
true rare contribution to remove rare-error feedback from the common equation.
It is an analytical device, not an implementable competitor. It keeps the common
error's effect on rare learning and retains multiplicative noise.

Define

$$
   z_{k+1}=L_0z_k+\sigma^2g,\qquad
  \xi_{k+1}=L_0\xi_k+Hz_k,\qquad
   z_0=((\beta_C^*)^2,\beta_C^*\beta_R^*,(\beta_R^*)^2)^\top,
  \quad \xi_0=0. \tag{P4}
$$

Then $\widehat R_{W,k}=w_W^\top(z_k+\xi_k)$. This is a computable approximation
using triangular recurrences and one feedback insertion, without a power of the
full exact moment map. The correction is signed and need not be a PSD moment
matrix on its own.

To see the scalar structure, write the three diagonal entries of $L_0$ as
$A,G_0,D_0$, and its lower entries as $p,f,r$. With
$\phi_k(z)=\sum_{j=0}^{k-1}z^j$,

$$
  z_{CC,k}=A^k(\beta_C^*)^2+\sigma^2g_C\phi_k(A),
$$

$$
  z_{CR,k}=G_0^k\beta_C^*\beta_R^*
    +\sum_{j<k}G_0^{k-1-j}(p z_{CC,j}+\sigma^2g_{CR}),
$$

$$
  z_{RR,k}=D_0^k(\beta_R^*)^2
    +\sum_{j<k}D_0^{k-1-j}(f z_{CC,j}+r z_{CR,j}+\sigma^2g_R).
$$

The same triangular solves give $\xi_k$. Finite sums also define coincident-root
cases, including $u=v$, without singular divisions. This matters for SD scaling.
There is no diffusion or Gaussian-design approximation.

For interpretation, the surrogate mean errors satisfy

$$
  \bar e_{C,k}=-(1-u)^k\beta_C^*,\qquad
  \bar e_{R,k}=-(1-v)^k\beta_R^*
  +d_Rc\beta_C^*\sum_{j<k}(1-v)^{k-1-j}(1-u)^j.
$$

The surrogate homogeneous second moment minus $\bar e_k\bar e_k^\top$ is its
multiplicative-update covariance. Its unit-noise solution gives the
observation-noise covariance. Both are PSD by their stochastic construction.
Keep the additional signed correction separate when reporting those three
components; do not call the whole homogeneous term squared bias or interpret
$V_{CR}$ as centered covariance alone.

## An explicit finite remainder and its uniform envelope

The following is an elementary consequence of (P3)–(P4), not the proposed new
theorem. All absolute values in this paragraph are entrywise. Set $Q=|L_0|$,
$J_H=|H|$, $v_0=|s_0|$, $a_0=r_0=0$, and propagate

$$
  v_{j+1}=Qv_j+\sigma^2|g|,\qquad
  a_{j+1}=Qa_j+J_Hv_j,\qquad
  r_{j+1}=|L|r_j+J_Ha_j. \tag{P5}
$$

Then $E_{W,k}=|w_W|^\top r_k$ is a finite error bound for every finite $k$.
Indeed, $|z_j|\leq v_j$, $|\xi_j|\leq a_j$, and the exact residual
$d_j=s_j-z_j-\xi_j$ obeys $d_{j+1}=Ld_j+H\xi_j$, $d_0=0$. Induction proves
$|d_j|\leq r_j$. Separate runs with $(\sigma^2,s_0)=(0,s_0)$ and $(1,0)$ give
$E_{W,k}=E^F_{W,k}+\sigma^2E^N_{W,k}$. These are real-arithmetic bounds;
floating-point evaluations in the checker are not outward-rounded certificates.

The feasibility proof controls the accumulation of each feedback insertion by
$O(q)$ through a weighted triangular resolvent. Feedback enters only the two
faster equations, whose contraction deficits are proportional to $u$; this
avoids an artificial $u/v$ factor over the rare learning time. It retains
$d_R^2t_B$, covers $u=v$, arbitrarily small positive $u$, and all batch-rarity
regimes within (P1). The uniform envelope resolves the fixed C1 rare-risk
reversal at the existing anchors. It is too loose for C2 and the adjusted C1
rare-risk comparison, for which (P5) remains useful. These arithmetic checks do
not establish a new predictive regime or an ordering over tuned families.

## Risk thresholds, budgets, and rate adjustment

For a fixed U/S pair and test weight, write
$\widehat\Delta=\widehat F+\sigma^2\widehat N$, and let $E_F=E^F_U+E^F_S$,
$E_N=E^N_U+E^N_S$. A negative upper bound $\widehat\Delta+E_F+\sigma^2E_N$
implies that S has lower risk. A positive lower bound implies that U has lower
risk. If $\widehat F+E_F<0<\widehat N-E_N$, the exact noise threshold is
enclosed by

$$
  \frac{-\widehat F-E_F}{\widehat N+E_N}
  \leq \tau\leq
  \frac{-\widehat F+E_F}{\widehat N-E_N}. \tag{P6}
$$

This gives conditions involving prevalence, dependence, both signal signs,
noise, and budget beyond the certified boxes. It does not assume that every
signal admits a positive threshold or that risk has only one crossing in $k$.

The direct rare-noise term of the leading surrogate is

$$
  \sigma^2g_R\phi_k(D_0)
  =\frac{\sigma^2\theta(1-D_0^k)}{2-v-\theta(1-4b)},\qquad
  kv=Mb\theta,\quad M=kB. \tag{P7}
$$

Its denominator is positive on (P1). Thus increased $\theta$ can shorten
rare-signal learning while increasing the noise plateau; the common-feature and
dependence contributions in (P3)–(P4) remain part of total risk. At fixed $B$,
lowering $v$ as the budget grows can keep a useful exposure $kv$ with a smaller
plateau. For example, $v=x/k$ gives $\theta=x/(Mb)$ when admissible. This
explains how the fixed-pair late reversal can disappear after adjustment. It
does not assert an optimal choice of $x$.

Matching rare drift across U and S requires $h_S=4bh_U$, rather than matching
the common drift. It matches (P7) and the isolated rare mean contraction, but
leaves different common transients, common-noise inputs, and dependent bias
terms. There is therefore no general equality of risks or full trajectories.

For a fixed law and batch size, let each method's declared admissible set
$\mathcal A_\delta(M)$ contain specified $(h,k)$ within (P1), with $kB\leq M$,
and optionally the zero predictor. For either finite sets or continuous rate
intervals, valid pointwise bounds imply

$$
  \inf_{\mathcal A_\delta(M)}(\widehat R-E)
  \leq\inf_{\mathcal A_\delta(M)}R
  \leq\inf_{\mathcal A_\delta(M)}(\widehat R+E). \tag{P8}
$$

Disjoint method intervals can establish an envelope ordering. Overlap leaves the
comparison unresolved. This elementary transfer is useful only if errors are
small enough and both sets are actually searched or bounded. Neither a grid
minimum nor these anchor calculations resolve a continuous optimum. Comparisons
at common $k$ across different batches instead cost different $M=kB$; do not
interpret them as equal-observation comparisons. A batch search can use (P8)
with explicitly enumerated $B$ and the same observation cap.

## Development checks and failures

Inside `devenv shell`, run `make check-predictive-claim`. The separate
[checker](../experiments/check_predictive_claim.py) writes no reference
artifacts. It checks 360 exact endpoints against the existing full moment
implementation, enumerates 72 actual batch-update operators for the surrogate,
and checks the finite residual bound. The checked operators include interior and
endpoint dependence, mixed signal signs, three normalization exponents, and
$B=1,2$.

At the original anchors, the following are rounded S-minus-U contrasts. The last
column is the sum of the two bounds (P5), evaluated in floating point.

  | Pair and objective                     | Exact gap    | Leading gap      | Corrected gap | Error bound          |
  | -------------------------------------- | -----------: | ---------------: | ------------: | -------------------: |
  | C1, $B=1,k=1{,}000$, rare              | -0.266270465 |     -0.266265216 |  -0.266270465 | $3.30\times10^{-12}$ |
  | C1, $B=1,k=10{,}000$, rare             |  0.050643397 |      0.050642323 |   0.050643397 | $1.88\times10^{-12}$ |
  | C1, adjusted late pair, rare           | -0.002561897 |     -0.002561431 |  -0.002561897 | $2.43\times10^{-13}$ |
  | C2, fixed, aggregate                   |  0.001300688 | **-0.001666466** |   0.001352481 |          0.000169979 |
  | C2, fixed, rare                        | -0.072724077 |     -0.081656833 |  -0.072677745 |          0.000318267 |
  | C2, aggregate-selected pair, aggregate |  0.024046278 |      0.022324491 |   0.024126836 |          0.000250500 |
  | C2, aggregate-selected pair, rare      |  0.779039166 |      0.771907996 |   0.779098394 |          0.000546240 |
  | C2, rare-selected pair, aggregate      |  0.067486074 |      0.069229094 |   0.067581893 |          0.000215915 |
  | C2, rare-selected pair, rare           |  0.239821136 |      0.235041635 |   0.239847544 |          0.000445617 |

The leading approximation's C2 aggregate sign is wrong. Its first correction is
needed to recover the disagreement. The corrected gaps exceed the computed
remainder margins, but the tiny independent-case bounds can be smaller than
floating-point evaluation error. Digits at that scale are not certified.

The fixed C1 law is $(q,\ell,\beta^*,\sigma^2)=(0.02,0,(1,1),3)$ with
$h_U=h_S=0.002$. Its adjusted late pair uses $(h_U,h_S)=(0.004,0.0003125)$. C2
uses $(q,\ell,\beta^*,\sigma^2)=(0.02,1,(2,1),4)$, $B=1,k=100$; its fixed pair
has $h_U=h_S=0.01$, aggregate-selected pair $(0.02,0.016)$, and rare-selected
pair $(0.04,0.008)$. These rates come from the [frozen robustness
results](normalization-robustness-results.md). Each adjusted row evaluates a
specific already selected pair, not a new optimization or validation study. The
checker also retains C1's $B=10$ endpoints.

An additional development screen takes independent features, signal $(1,1)$,
noise variance $\sigma^2=3$, $B=1$, $h=0.1b$, and stops at
$k_{\mathrm{early}}=\operatorname{round}(2/h)$ and
$k_{\mathrm{late}}=\operatorname{round}(0.4/(hb))$. Holding U at $h$ and
changing only S to $3/k_{\mathrm{late}}$ illustrates rate adjustment outside
C1's box:

  | $q$   | Early $k=M$ | Late $k=M$ | Early fixed rare gap | Late fixed rare gap | Late S-adjusted rare gap |
  | ----- | ----------: | ---------: | -------------------: | ------------------: | -----------------------: |
  | 0.006 |       3,353 |    112,457 |         -0.361566298 |         0.056042989 |             -0.017469187 |
  | 0.04  |         521 |      2,713 |         -0.173905487 |         0.043037479 |             -0.009806567 |
  | 0.06  |         355 |      1,257 |         -0.111834519 |         0.036323508 |             -0.005434474 |

These are post-development numerical examples, not held-out predictions, uniform
certificates, or comparisons of two optimized procedures. Their corrected gaps
have the same displayed signs, with computed bounds below $2.5\times10^{-10}$.

Before the feasibility proof, the proposed scale in (P2) was also screened on
14,688 endpoints: six prevalences $\{0.0006,0.002,0.006,0.02,0.06,1/16\}$, four
dependence values $\{-1,0,0.7,1\}$, $B\in\{1,10,100\}$,
$\delta\in\{0,1/4,1/2\}$, four signals $\{(1,1),(2,1),(1,-1),(0,1)\}$, and rate
fractions $\{0.1,0.5,1\}$ of the maximum allowed by (P1). Each configuration
uses distinct counts in $\{0,1,\lfloor1/u\rfloor,\lfloor1/v\rfloor,
\lfloor10/v\rfloor,\lfloor100/v\rfloor\}$. The largest error-to-proposed-scale
ratios are 0.196627 for the homogeneous part and 0.230118 for unit noise. For
(P5) itself the respective maxima are 0.626888 and 0.924497. These diagnostics
supported investigating the conjecture; they did not prove it, supply $K=1$,
cover all rates, or validate tuned envelopes. The checker reports these ratios
without treating them as theorem assertions. The separate feasibility checker
tests the now-proved envelope and its rational vector inequalities.

## Precise antecedent comparison

The primary passages below were rechecked on September 16, 2026. This is a
bounded comparison of the proposed statement, not an exhaustive priority search
or a review of the papers' proofs. Interpretations of what (P2) would add are
ours. The existing audits remain the broader source record.

  | Antecedent and inspected statement                                                                                                                            | Mapping and overlap                                                                                                                                                                                                                                                                                                                                                                                                | What would still need to be established for this proposal                                                                                                                                                                                                                                                             |
  | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | [Su, Zou, and Wu, arXiv v3](https://arxiv.org/html/2403.08585v3), Assumptions 3.1–3.3, (3.1)–(3.2), Theorem 4.2, and Appendix A.1                             | Set their $G=P$, $H=C$. They analyze fresh-sample, constant-step SGD with tail averaging and aggregate excess risk. Their appendix already propagates homogeneous and noise-driven moments. Their fourth-moment constant necessarily satisfies $\alpha\geq1/b-4$ here.                                                                                                                                             | (P2) must control final-iterate approximation error uniformly in prevalence and rates and give sign-resolving comparisons. Their aggregate upper bound alone does not do that, and substituting $P$ into the moment identity is established work. Changing the output iterate alone is not a novelty argument.        |
  | [Défossez and Bach, AdaBatch, arXiv v1](https://arxiv.org/html/1711.01761v1), (2.3)–(2.4), Assumption 1, Table 1, and Appendix C.2, (7.21)–(7.23)             | Their support-based aggregation and deterministic preconditioning connect faster frequency-dependent learning with increased noise and batch-dependent step limits. The bounds use curvature assumptions, projection, and weighted averages. Centered binary coordinates here have support probability one, so literal AdaBatch is ordinary batching; the deterministic-preconditioning analysis remains relevant. | The dependence-sensitive correction and a two-sided approximation uniform in $q$, budget, and admissible rates require an additional calculation. The basic tradeoff, $Bq$ dependence, and reducing a constant step for a longer horizon cannot be claimed as new.                                                    |
  | [Liu et al., arXiv v1](https://arxiv.org/html/2502.09047v1), Sections 3.1, 4, and 5.1, Assumptions 1–4, and Theorems 2–4                                      | Map their source and target moments to $C,C_R$. Their results concern minimax linear preconditioning and target-risk bounds for scheduled accelerated SGD. For the displayed fourth-moment condition, $\psi\geq1/b-3$ is necessary in this model. Conditioning on rare presence is ordinary covariate shift.                                                                                                       | The proposed fixed-signal, conventional-scaling, constant-step expansion is not the displayed minimax or scheduled-optimizer bound. Its candidate contribution must be prediction of the training-generated error contrast and its retuning sensitivity, not the use of target moments or their off-diagonal entries. |
  | [Lei, Hu, and Lee, ICML 2021](https://proceedings.mlr.press/v139/lei21a/lei21a.pdf#page=3), Theorems 3.2 and 3.4, Remark 3.1, and Proposition 3.5, PDF pp.3–4 | Their fixed-design Gaussian analysis allows noncommuting source/target matrices and rank-one targets. Remark 3.1 already separates a target-aware linear estimator from optimally tuned ridge; Proposition 3.5 gives a common Bayes-optimal ridge estimator across targets under an isotropic prior.                                                                                                               | A strict target-risk separation or different preferred configurations is not itself new. (P2) would instead quantify a particular training path and a declared tuning family. It does not establish minimax superiority, different global optima, or superiority over their estimator.                                |

The rare-coordinate substitutions yielding $1/b-4$ and $1/b-3$ are our
calculations: $E x_R^4=b(1-3b)$, and the first assumption subtracts $b^2$. They
are necessary lower bounds on constants, not sufficient verifications of the
full matrix assumptions. The [existing target-risk
comparison](target-risk-comparison.md) also covers Wu et al.'s final-iterate
covariate-shift bounds. A final-iterate subgroup objective alone does not
distinguish this proposal from that literature.

## Decision before a substantial proof effort

The exact recurrence, scalar geometric sums, feedback expansion, and finite
comparison inequality are supporting calculations within established moment
analysis. The additional scientific target couples the uniform $q^2$ error bound
to explicit sign and rate-adjustment conditions over a declared parameter
family. The local feasibility proof now supplies the stable domain and explicit
constants. The subsequent [predictive-regime note](predictive-regime.md) uses
the expansion to give explicit prevalence/budget and signal families with
opposite orderings over continuous rate/stopping sets. Its finite-prevalence
bounds and rational certificate extend beyond the anchor checks.

**The stability, remainder, and bounded predictive comparison are complete
locally; the central contribution decision remains open.** The comparison's
five-source audit retains the independent-feature result as a supporting
specialization. Its explicit oracle separations do not yet establish a
substantive novelty case for expanding the theorem effort.

Independent proof review, human mathematical and novelty review, and prediction
on held-out configurations remain later milestones. The separate [four-rule
follow-up](variance-scaling-followup-results.md) has resolved the Mushroom rate
edges within its finite grid. The frozen practical study's missing-group
failures and numerical investigation remain limitations. This proposal does not
prescribe a new practical selection rule or claim that the population
assumptions cover those failures.

Build the one-page review copy with `make paper-claim` inside `devenv shell`;
the generated PDF is `build/proposed-claim.pdf`. The official conference files
and manuscript claims are unchanged.
