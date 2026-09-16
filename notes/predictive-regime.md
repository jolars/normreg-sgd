# A predictive rare-prevalence regime over continuous tuning sets

September 16, 2026. This note completes the predictive-regime and
declared-tuning comparison in [TODO.md](../TODO.md), using the
[expansion](predictive-claim.md) and its [uniform
remainder](predictive-claim-feasibility.md). It gives a local proof and an exact
rational certificate, with independent proof review and human review still
pending. The accompanying calculations are claim development, not held-out
tests. The conference manuscript and frozen experiments retain their claims.

The subsequent [self-contained theorem](predictive-theorem.md) gives a shorter
direct proof of the same advertised guarantees, with a separately implemented
rational certificate. It also separates mathematical completion from the
decision about the result's role in the paper. The original expansion-based
derivation and certificate below remain available.

**At budgets proportional to inverse prevalence, SD scaling wins throughout one
signal family and loses throughout another, even after each method chooses its
constant rate and stopping time.** The statement covers independent binary
features, all sufficiently small positive prevalences, and continuous rate sets.
It does not resolve dependence, optimal schedules, batching, or practical
validation selection. The source comparison below supports retaining it as a
quantitative specialization; it does not yet justify a broader central-theorem
effort on novelty grounds.

## Model, budget, and declared oracle sets

Use the binary population model of (P1) with $\ell=0$:

$$
  I\sim\operatorname{Bernoulli}(1/2),\qquad
  J\sim\operatorname{Bernoulli}(q),\qquad I\perp J,
  \qquad x=(I-1/2,J-q)^\top.
$$

The response is $y=x^\top\beta^*+\varepsilon$, where $E(\varepsilon\mid x)=0$
and $E(\varepsilon^2\mid x)=\sigma^2>0$. Centering and scales are known
population quantities, the intercept is fixed at zero, initialization is zero,
and the loss is averaged squared loss. Each update uses one fresh observation,
so $B=1$ and $k$ updates consume $k$ distinct observations. Test observations
are independent of training. Write

$$
  b=q(1-q),\qquad 0<q\leq Q:=10^{-4},\qquad
  M\in\mathbb N,\qquad 1\leq\tau:=Mb\leq4. \tag{R1}
$$

Thus $M$ lies between $1/b$ and $4/b$, subject to integer endpoints. No positive
lower bound on $q$ is imposed. Define the two complete rate/stopping sets

$$
  \begin{aligned}
  \mathcal A_U(M)&=\{(u,v,k)=(\theta/4,b\theta,k):
                 0\leq\theta\leq1,\ k\in\{0,\ldots,M\}\},\\
  \mathcal A_S(M)&=\{(u,v,k)=(b\theta,b\theta,k):
                 0\leq\theta\leq1,\ k\in\{0,\ldots,M\}\}.
  \end{aligned} \tag{R2}
$$

Here $D=\eta P=\operatorname{diag}(4u,v/b)$. U divides columns by one and has
absolute learning rate $\eta_U=\theta$. S divides columns by population standard
deviations $(1/2,\sqrt b)$ and has $\eta_S=b\theta$. Both sets therefore allow
the same rare drift $v=b\theta$ and rare-update size $v/b=\theta$. They comprise
all U and S rates in (P1) for $B=1$, plus the zero predictor. They are not all
mean-square-stable rates outside that domain.

Evaluate the original-scale final iterate on rare presence:

$$
  R_{R,k}=\frac12 E[(x^\top(\hat\beta_k-\beta^*))^2\mid J=1]
    =\frac18 V_{CC,k}+\frac{(1-q)^2}{2}V_{RR,k},\qquad
  R_U^*=\inf_{\mathcal A_U(M)}R_{R,k},\quad
  R_S^*=\inf_{\mathcal A_S(M)}R_{R,k}. \tag{R3}
$$

Write $w_R=(1/8,0,(1-q)^2/2)^\top$ for the corresponding moment weights.
Irreducible test noise is excluded. The infima describe population oracle
envelopes, not data-driven selectors or finite searches with equal computational
cost. Every candidate obeys the same observation cap. There is no claim about
aggregate-risk ordering.

## Explicit prediction

For every $q,M$ in (R1), both signs of each coefficient are allowed:

  | Signal and noise conditions                               | Oracle prediction              | One candidate that suffices to beat the other entire family |
  | --------------------------------------------------------- | ------------------------------ | ----------------------------------------------------------- |
  | $(\beta_R^*)^2=\sigma^2$, $(\beta_C^*)^2\leq\sigma^2/100$ | $R_U^*-R_S^*\geq0.007\sigma^2$ | S with $\theta=2/(\tau+4)$, $k=M$                           |
  | $(\beta_C^*)^2=\sigma^2$, $(\beta_R^*)^2\leq\sigma^2/100$ | $R_S^*-R_U^*\geq0.005\sigma^2$ | U with $u=\sqrt b$, $\theta=4\sqrt b$, $k=M$                |

These are sufficient conditions, not a phase boundary or a general normalization
recommendation. The equality between the dominant signal square and noise
variance is part of the declared family. The proof does not establish an
interval of signal-to-noise ratios. The bounds are conservative, particularly
$q\leq10^{-4}$, and do not explain C2's dependence-sensitive disagreement.

The prediction separates where the signal lies from how rare the feature is. For
the first family, U must inject common-coordinate noise to learn the rare signal
quickly. S can achieve the same rare drift with a much smaller common step. For
the second family, that small common step leaves substantial common bias within
the budget. U can instead learn the common signal at a small original-scale rate
while doing little to the nearly inactive rare coordinate. Neither choice needs
the other method's rate to remain fixed.

## Reduction of the expansion

By homogeneity, set $\sigma^2=1$ in the proof and multiply risks by $\sigma^2$
afterward. Write $s=(\beta_C^*)^2$, $r=(\beta_R^*)^2$. With $\ell=0$, the cross
moment evolves separately and has zero weight in (R3). The common and rare
diagonal moments obey

$$
  \begin{pmatrix}V_{CC,k+1}\\V_{RR,k+1}\end{pmatrix}
  =\begin{pmatrix}A&4u^2b\\ b\theta^2/4&D_b\end{pmatrix}
    \begin{pmatrix}V_{CC,k}\\V_{RR,k}\end{pmatrix}
    +\begin{pmatrix}4u^2\\b\theta^2\end{pmatrix},
  \quad
  A=(1-u)^2,\quad
  D_b=1-b\theta(2-\theta+3b\theta). \tag{R4}
$$

All entries are nonnegative. These are (P3)'s two diagonal coordinates, not an
assumption that stochastic feature updates decouple. The triangular surrogate
sets $4u^2b$ to zero. The first correction reinserts this feedback once, and the
existing $q^2$ remainder controls subsequent insertions. In particular, both
diagonal components of the correction and residual are nonnegative.

For any of the present rates, (F12)–(F13) and (F1) imply

$$
  \begin{aligned}
  |w_R^\top\xi_k|&\leq\mu q[2(s+r)+4\zeta],\\
  E_{R,k}&\leq\frac{8\mu q^2}{1-4q}[s+r+2\zeta],
  \qquad \mu=1/8+(1-q)^2\leq9/8,\quad\zeta=u+\theta.
  \end{aligned} \tag{R5}
$$

We dropped the homogeneous decay factor only to simplify constants. The first
line follows from the first-insertion bounds in the feasibility proof, rather
than treating the $q^2$ remainder as a bound on the entire leading
approximation.

Define the scalar functions

$$
   \begin{gathered}
   d(\theta)=\theta(2-\theta),\qquad Z=e^{-\tau d(\theta)},\\
   F_S(\theta,\tau;s,r)
   =\frac12\left[(r+s/4)Z+
                \frac{\theta}{2-\theta}(1-Z)\right],\\
   F_U^-(\theta,\tau)
   =\frac12\left[Z+
         \left\{\frac{\theta}{2-\theta}+\frac{\theta}{8-\theta}\right\}(1-Z)
              \right].
  \end{gathered} \tag{R6}
$$

$F_S$ is the leading small-prevalence expression for S. $F_U^-$ is a lower
comparison function for U when $r=1$, not its exact limiting risk. It discards
common-to-rare propagation of observation noise. The decay $d(\theta)$ includes
multiplicative update variance; replacing it by the squared-mean rate $2\theta$
would change the comparison.

At matched $\theta$, the leading lower contrast is

$$
  F_U^-(\theta,\tau)-F_S(\theta,\tau;s,1)
  =\frac{\theta}{2(8-\theta)}(1-Z)-\frac{s}{8}Z. \tag{R7}
$$

Thus $s<4\theta(e^{\tau d(\theta)}-1)/(8-\theta)$ is an interpretable sufficient
leading condition for S to beat the matched U rate. It is not yet an oracle
comparison. The next steps control finite prevalence and all competing rates and
stops.

## Rare-signal family: transfer to all rates and stops

Assume $r=1$ and $0\leq s\leq1/100$. For U, $u=\theta/4$ gives $A\leq D_b$.
Dropping nonnegative terms from the surrogate in (R4) gives, with $z=D_b^k$,

$$
  R_{R,k}^U\geq\frac12\left[
   (1-q)^2z+
   \left\{\frac{(1-q)^2\theta}{2-\theta+3b\theta}
                        +\frac{\theta}{8-\theta}\right\}(1-z)\right]. \tag{R8}
$$

The last term uses common observation-noise variance $4\theta(1-A^k)/(8-\theta)$
and $1-A^k\geq1-D_b^k$. The right side is affine in $z$. Because $k\leq M$, its
minimum over all stops is bounded by its values at $z=1$ and $z=D_b^M$. This
includes the zero-step predictor and rates arbitrarily close to zero without a
limiting interchange.

For $0\leq\theta\leq1$, put $d_b=d(\theta)+3b\theta^2$. The elementary logarithm
remainder gives

$$
  0\leq-\frac{\log(1-bd_b)}b-d(\theta)
  \leq b\left[3+\frac{(1+3Q)^2}{2\{1-Q(1+3Q)\}}\right]<4b.
$$

Consequently $|D_b^M-e^{-\tau d(\theta)}|\leq16q$. The initial coefficient in
(R8) differs from one by at most $2q$, and its noise coefficient differs from
that of $F_U^-$ by at most $5q$. Also
$|1-\theta/(2-\theta)-\theta/(8-\theta)|\leq1$. Combining these facts proves the
uniform finite bound

$$
  R_{R,k}^U\geq
        \min\{1/2,F_U^-(\theta,\tau)\}-11q,
  \qquad 0\leq k\leq M. \tag{R9}
$$

For S use $\theta_S=2/(\tau+4)\in[1/4,2/5]$ and $k=M$. For its surrogate, let
$Y_k=z_{CC,k}/4+z_{RR,k}$. Equation (R4) with the feedback removed gives

$$
  Y_{k+1}\leq\widetilde D Y_k+b\theta^2(1+b),\qquad
  \widetilde D=1-bd(\theta)+b^2\theta^2,\qquad Y_0=r+s/4.
$$

Since the finite-$q$ rare weight is at most $1/2$, its surrogate risk is at most

$$
  \frac12\left[(r+s/4)\widetilde D^M+
     \frac{\theta(1+b)}{2-\theta-b\theta}(1-\widetilde D^M)\right].
$$

Uniformly for $b\leq Q$, $\tau\leq4$, and $\theta\leq1$,

$$
  \begin{aligned}
  |\widetilde D^M-e^{-\tau d(\theta)}|
    &\leq4b\left[1+\frac1{2(1-Q)}\right],\\
  0\leq\frac{\theta(1+b)}{2-\theta-b\theta}
            -\frac{\theta}{2-\theta}&\leq\frac{2b}{1-Q}.
  \end{aligned}
$$

The surrogate upper bound therefore exceeds $F_S$ by at most $4.1q$. For the
candidate rate, $\zeta\leq(2/5)(1+Q)$ and $s+r\leq101/100$. The first correction
in (R5) is less than $4.1q$ and its remainder is less than $0.002q$. Hence

$$
  R_{R,M}^S(\theta_S)
  \leq F_S(\theta_S,\tau;1/100,1)+9q. \tag{R10}
$$

The [rational checker](../experiments/check_predictive_regime.py) establishes
the final, continuous two-variable inequality

$$
  \min\{1/2,F_U^-(\theta,\tau)\}
        -F_S(2/(\tau+4),\tau;1/100,1)\geq1/100,
  \qquad (\theta,\tau)\in[0,1]\times[1,4]. \tag{R11}
$$

This is a certificate of the full rectangle, not a grid-minimum assertion.
Together (R9)–(R11) give

$$
  R_U^*-R_S^*\geq1/100-20q\geq0.008>0.007.
$$

### How the rational certificate covers the continuum

Both $d(\theta)$ and $N(\theta)=\theta/(2-\theta)+\theta/(8-\theta)$ increase on
$[0,1]$. On a rectangle $[a,b]\times[c,d]$, bound $N$ below by $N(a)$ and
enclose $Z$ between $e^{-d\,d(b)}$ and $e^{-c\,d(a)}$. The function
$(N+(1-N)Z)/2$ increases in $N$; choose the lower $Z$ endpoint when $N(a)\leq1$
and the upper endpoint otherwise.

The S candidate's plateau is $1/(\tau+3)$ and its exponent is
$4\tau(\tau+3)/(\tau+4)^2$. The former decreases and the latter increases on
$[1,4]$, so its candidate risk decreases. Its upper bound on the same rectangle
is therefore attained at $\tau=c$.

For each rational $x\in[0,4]$, the degree-25 and degree-24 Taylor polynomials of
$e^{-x}$ enclose it below and above. The signed integral remainder proves these
inequalities even where the first Taylor terms do not decrease. All polynomial
operations, endpoints, comparisons, and rectangle areas use exact Python
fractions. Bisection continues until every leaf has margin at least $1/100$. The
3,197 leaves cover area exactly three, with maximum depth 18; the smallest
certified lower margin is greater than $0.01000005$. The baseline $1/2$ is
checked separately using the same monotonicity. Displayed decimals are for
readability; decisions use rational numbers.

## Common-signal family: the reverse oracle ordering

Now let $s=1$ and $0\leq r\leq1/100$. For every S rate and stop, the exact mean
common error is $-(1-b\theta)^k\beta_C^*$. If $\theta\leq1/4$,

$$
  R_{R,k}^S\geq\frac18(1-b\theta)^{2k}
  \geq\frac18\exp\left\{-\frac2{1-Q/4}\right\}>\frac1{60}. \tag{R12}
$$

If $\theta\geq1/4$, let $z=(1-b\theta)^k$. We have $D_b\leq1-b\theta$ and
$\theta/(2-\theta+3b\theta)\geq\theta/2$. Common squared bias and direct rare
observation noise alone therefore give

$$
  R_{R,k}^S\geq z^2/8+\frac{(1-q)^2\theta}{4}(1-z)
  \geq z^2/8+\frac3{50}(1-z)\geq\frac{33}{625}>\frac1{60}. \tag{R13}
$$

These lower bounds cover every stop, including zero. Thus $R_S^*>1/60$.

For U choose $h=\sqrt b$, $u=h$, $\theta=4h$, $k=M$. Here $h\leq1/100$, so the
candidate belongs to (R2). From the surrogate in (R4), dropping rare contraction
only for an upper bound,

$$
  \begin{aligned}
  z_{CC,M}/8&\leq e^{-2/h}/8+\frac{h}{2(2-h)},\\
  z_{RR,M}/2&\leq\frac12\left[
    \frac1{100}+\frac{4h^3}{2-h}+\frac{64h^3}{2-h}+64b\right].
  \end{aligned} \tag{R14}
$$

The first rare term from the common coordinate sums its decaying initial error
using $\sum A^j\leq1/(2h-h^2)$. The second uses its common-noise plateau
$4h/(2-h)$ and $M\leq4/b$. The final $64b$ bounds direct observation noise over
$M$ updates. Here $\zeta=5h$. Adding (R5) and substituting the upper endpoints
$b,q\leq Q$ and $h\leq1/100$ gives

$$
  R_{R,M}^U<0.01097950<11/1000,\qquad
  R_S^*-R_U^*>1/60-11/1000>1/200. \tag{R15}
$$

The checker verifies these constants rationally, using $e^{-200}\leq2^{-200}$
and the same Taylor bounds for (R12). This proves the second prediction.

## Verification and scope

Inside `devenv shell`, run `make check-predictive-regime`. It writes no result
artifacts and is included in `make check-predictive-claim` and integrated
optimization checks. It verifies (R11), the transfer constants, and (R12)–(R15)
with exact fractions. It also constructs 12 scalar moment maps directly from
rational observation updates and checks 2,718 finite endpoints and candidate
bounds against the full moment map and corrected expansion. The latter use
floating point and support the implementation; the continuous conclusions rely
on the analytic inequalities and rational certificate.

The statement predicts signs on an infinite prevalence family and a fourfold
observation-budget interval, while covering rates arbitrarily close to zero and
every earlier stop. This goes beyond reproducing C1/C2 anchors. It does not
claim that all fixed-rate reversals survive tuning or that the candidate rates
are optimal. A lower envelope for every competitor and one admissible candidate
suffice; the proof neither locates nor discretizes an unknown oracle optimum.

Independence makes the covariance weights diagonal and removes C2's cross-error
mechanism. The signal-to-noise equality, small prevalence ceiling, single-sample
batches, population preprocessing, fixed intercept, and final-iterate output are
explicit restrictions. Validation noise and absent rare validation groups are
outside this oracle comparison. Their failures in the frozen practical studies
remain intact. An evaluation on held-out configurations and an additional
categorical task requires a separately declared protocol, as tracked in TODO.

## Precise antecedents and decision before further theorem work

The passages below were rechecked on September 16, 2026. Primary HTML was used
for the first three sources, and rendered published PDF pages for the last two.
This is a bounded statement comparison, not a review of their proofs or an
exhaustive priority search. Assessments of what (R1)–(R15) add are ours.

  | Source and inspected passage                                                                                                                                                                     | Overlap with this exact conclusion                                                                                                                                                                                                              | Remaining calculation and assessment                                                                                                                                                                                                                           |
  | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | [Su, Zou, and Wu, v3](https://arxiv.org/html/2403.08585v3), Assumptions 3.1–3.3, Theorem 4.2, Appendix A.1                                                                                       | Their constant-step fresh SGD with a fixed preconditioner has the same underlying moment machinery. Their output is tail averaged and their displayed bound is aggregate risk.                                                                  | Their bound does not directly order the final-iterate U/S infima in (R2). Our rare binary fourth-moment constant is prevalence dependent. The scalar reduction and feedback control are additional calculations within that established framework.             |
  | [Défossez and Bach, AdaBatch v1](https://arxiv.org/html/1711.01761v1), Table 1, Appendix C.2, (7.21)–(7.23)                                                                                      | Frequency-dependent learning, noise inflation, and batch-dependent rate restrictions are already central. They also analyze deterministic preconditioning. Literal support-based AdaBatch sees both centered coordinates as always active here. | The explicit two-sided oracle separation is not their displayed conclusion. The explanation based on differing coordinate noise and learning times is established, so the separation's numerical constants do not by themselves establish substantive novelty. |
  | [Liu et al., v1](https://arxiv.org/html/2502.09047v1), Sections 3.1–5.1, Theorems 2–4                                                                                                            | Map their source and target moments to $C$ and $C_R$. Target-aware linear preconditioning and scheduled accelerated SGD already address target risk. Their criterion is minimax over a signal class.                                            | Our fixed-signal families and conventional U/S constant-step sets differ from their estimator and optimizer. Independent coordinates make the present geometry especially elementary. No minimax advantage or improvement over their method follows.           |
  | [Lei, Hu, and Lee, ICML 2021](https://proceedings.mlr.press/v139/lei21a/lei21a.pdf#page=3), Theorems 3.2 and 3.4, Remark 3.1, PDF pp.3–4                                                         | Their fixed-design Gaussian model already admits diagonal source/target risk geometry and a separation from optimally tuned ridge. The present $C,C_R$ commute.                                                                                 | Their minimax linear estimator is not either SGD family, so (R2)'s signs need a further calculation. A separation after scalar retuning, or conditioning on a subgroup, cannot serve as the novelty claim.                                                     |
  | [Wu et al., NeurIPS 2022](https://papers.nips.cc/paper_files/paper/2022/file/d5c04aa72b92c53bda5b525b60958295-Paper-Conference.pdf#page=4), SGD definition, Assumption 1, Corollary 3.3, pp.4, 6 | Source-only online training with last-iterate target risk is already analyzed, using geometric step decay.                                                                                                                                      | Their lower fourth-moment assumption fails for the common centered Bernoulli coordinate, whose square is constant. Their bounds do not directly certify (R11), but the output iterate and target criterion themselves are established.                         |

For Su–Zou–Wu, the necessary rare-coordinate moment constant is
$\alpha\geq1/b-4$. For Liu et al.'s displayed full fourth-moment assumption, it
is $\psi\geq1/b-3$; their finite-signal remark also provides a weaker
alternative assumption, so this divergence must not be described as excluding
their entire theory. For Wu et al.'s lower condition, testing the common
coordinate gives $E x_C^4-(E x_C^2)^2=0$, which cannot dominate a positive
multiple of $(E x_C^2)^2$. These substitutions are our calculations and agree
with the [earlier source audit](normalization-risk-audit.md).

**Decision:** the requested predictive comparison is available locally, but the
present independent-feature result should remain a supporting proposition. It
adds explicit prevalence, signal, budget, and continuous-tuning guarantees to
the repository's anchor checks. Its proof still specializes established moment
and target-risk analysis, and the source comparison does not establish a
substantive publication-level advance. Do not expand the theorem program or
promote the result into the main contribution on this basis alone. Independent
proof review, human mathematical and novelty review, and a decision about a
stronger dependence-sensitive statement remain the next milestone. The later
[assessment](predictive-theorem.md) clarifies that this is a decision about
expanding and positioning the result, not a reason to defer checking it.
