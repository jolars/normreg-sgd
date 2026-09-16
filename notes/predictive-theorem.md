# A checked predictive theorem and its contribution assessment

September 16, 2026. This note makes the [predictive-regime
result](predictive-regime.md) self-contained, with a shorter direct proof and a
separate computational certificate. It addresses the theorem-development item in
[TODO.md](../TODO.md). This is local mathematical development and checking, not
independent proof review, human review, or a held-out evaluation.

**Standard-deviation scaling can improve or worsen the best attainable
rare-presence risk, even when both methods choose their constant rate and stop
within the stated domain. Which ordering holds depends on the signal.** The
result below preserves the earlier signal families, prevalence range, budget
range, and advertised gaps. It supplies a direct proof from exact moments,
without the general feedback expansion. The [uniform stability and remainder
theorem](predictive-claim-feasibility.md) remains a separate result covering
dependence and batches.

## What the novelty condition means

The former TODO wording, “if the proposed claim offers a substantive advance
over its closest antecedents,” combined three different tasks:

1. Establish that the statement is correct under explicit assumptions.
2. Identify the conclusion it adds to the closest published results.
3. Judge whether that addition warrants a central role in the manuscript.

A useful new conclusion can follow from familiar tools. Conversely, a difficult
proof or a previously unreported constant need not add much scientific value.
The condition should govern expanding the research program and choosing the
paper's contribution, rather than prevent finishing and checking a bounded
result. Mathematical completion does not require deciding publication-level
novelty first.

For this theorem, the concrete addition to assess is a quantitative separation
of two entire rate/stopping families, in both directions on specified signal
families, uniformly as prevalence tends to zero. The source comparison below
distinguishes this statement from the established mechanisms. It does not settle
priority or publication significance.

## Model and theorem

Let $I\sim\operatorname{Bernoulli}(1/2)$ and $J\sim\operatorname{Bernoulli}(q)$
be independent, and set

$$
  x=(I-1/2,J-q)^\top,\qquad
  y=x^\top\beta^*+\varepsilon,\qquad
  E(\varepsilon\mid x)=0,\quad
  E(\varepsilon^2\mid x)=\sigma^2>0.
$$

All training observations are independent draws from this law. Centering and
scales are known population quantities, the intercept is fixed at zero, and
$\hat\beta_0=0$. Use the averaged squared loss and one fresh observation per
update ($B=1$). On the original coefficient scale, the update is

$$
  \hat\beta_{j+1}=\hat\beta_j+
  D x_{j+1}(y_{j+1}-x_{j+1}^\top\hat\beta_j).
$$

Put $b=q(1-q)$ and $Q=10^{-4}$. Fix any

$$
  0<q\leq Q,\qquad M\in\mathbb N,\qquad 1\leq\tau:=Mb\leq4. \tag{T1}
$$

Each method may choose any $\theta\in[0,1]$ and any integer stop
$0\leq k\leq M$:

$$
  D_U(\theta)=\operatorname{diag}(\theta,\theta),\qquad
  D_S(\theta)=\operatorname{diag}(4b\theta,\theta). \tag{T2}
$$

U leaves the columns unscaled and uses absolute learning rate $\eta_U=\theta$. S
divides the columns by $(1/2,\sqrt b)$ and uses $\eta_S=b\theta$. These are
exactly the U/S rate sets in the [expansion domain](predictive-claim.md) for
$B=1$, with the zero predictor added. They do not exhaust all stable rates. Both
methods have the same observation cap $M$ and may stop earlier. Rates and stops
are deterministic oracle choices, not functions of realized training or
validation data.

Evaluate the final iterate on an independent test observation conditioned on
$J=1$, retaining population centering. Exclude irreducible test noise and define

$$
  R_{R,k}^{A}(\theta)
  =\frac12 E[(x^\top(\hat\beta_k^A-\beta^*))^2\mid J=1],\qquad
  R_A^*=\inf_{\theta\in[0,1],\ k\in\{0,\ldots,M\}}R_{R,k}^{A}(\theta),
  \quad A\in\{U,S\}. \tag{T3}
$$

**Theorem (opposite oracle rare-risk orderings).** Under (T1)–(T3):

- If $(\beta_R^*)^2=\sigma^2$ and $(\beta_C^*)^2\leq\sigma^2/100$, then
  $R_U^*-R_S^*\geq7\sigma^2/1000$.
- If $(\beta_C^*)^2=\sigma^2$ and $(\beta_R^*)^2\leq\sigma^2/100$, then
  $R_S^*-R_U^*\geq\sigma^2/200$.

Either sign is allowed for each coefficient. The same inequalities hold if each
infimum is replaced by a minimum: for each of the finitely many stops, the risk
is continuous on the compact rate interval. No candidate rate below is asserted
to be optimal. A bound for every competitor and one admissible candidate
suffice.

## Proof

Normalize $\sigma^2=1$ by homogeneity, and write $s=(\beta_C^*)^2$,
$r=(\beta_R^*)^2$. Let $C_k=E e_{C,k}^2$ and $H_k=E e_{R,k}^2$, where
$e_k=\hat\beta_k-\beta^*$. Independence makes the conditional risk diagonal:

$$
  R_{R,k}=C_k/8+(1-q)^2H_k/2. \tag{T4}
$$

The common feature has $x_C^2=1/4$. The other required moments are $E x_R^2=b$,
$E x_R^4=b(1-3b)$, and $E x_C^2x_R^2=b/4$; the mixed odd common moments vanish.
Expanding the random update and using conditional mean-zero noise gives the
exact recurrence

$$
  \binom{C_{k+1}}{H_{k+1}}
  =\begin{pmatrix}
    A&4u^2b\\ b\theta^2/4&D_b
   \end{pmatrix}\binom{C_k}{H_k}
   +\binom{4u^2}{b\theta^2},\qquad
  \binom{C_0}{H_0}=\binom{s}{r}, \tag{T5}
$$

where $A=(1-u)^2$, $D_b=1-b\theta(2-\theta+3b\theta)$, and $u=\theta/4$ for U or
$u=b\theta$ for S. Stochastic coordinate updates remain coupled even though the
features are independent. The cross error moment affects neither diagonal
equation nor (T4), which also proves sign invariance.

All entries in (T5) are nonnegative. For $\theta>0$, the row sums are

$$
  1-u\{2-u(1+4b)\}<1,\qquad
  1-b\theta\{2-5\theta/4+3b\theta\}<1.
$$

Thus homogeneous diagonal moments contract, and the noise-driven moments remain
bounded. The remaining cross moment is controlled by
$|E e_Ce_R|\leq\sqrt{C_kH_k}$. This establishes mean-square stability for the
positive rates used here. The rate $\theta=0$ leaves the predictor at zero.

### Rare signal: a lower bound for every U rate and stop

Suppose $r=1$ and $s\leq1/100$. For U, $A\leq D_b$: for positive $\theta$, the
common deficit is at least $7\theta/16$, whereas the rare deficit is at most
$2b\theta\leq2Q\theta$. Dropping nonnegative terms in (T5) gives, with
$z=D_b^k$,

$$
  R_{R,k}^U\geq\frac12\left[
    (1-q)^2z+
    \left\{\frac{(1-q)^2\theta}{2-\theta+3b\theta}
                   +\frac{\theta}{8-\theta}\right\}(1-z)\right]. \tag{T6}
$$

The common-noise term uses $1-A^k\geq1-D_b^k$. At $\theta=0$, (T6) holds
directly. For fixed rate the right side is affine in $z$, so its minimum over
all $k\leq M$ is bounded by its two endpoint values at $z=1$ and $z=D_b^M$.

Write

$$
  d(\theta)=\theta(2-\theta),\quad Z=e^{-\tau d(\theta)},\quad
  N(\theta)=\frac{\theta}{2-\theta}+\frac{\theta}{8-\theta},\quad
  F_U^-(\theta,\tau)=\frac12[Z+N(\theta)(1-Z)].
$$

For $d_b=d(\theta)+3b\theta^2$, the logarithm series implies

$$
  0\leq-\frac{\log(1-bd_b)}b-d(\theta)
  \leq b\left[3+\frac{(1+3Q)^2}{2\{1-Q(1+3Q)\}}\right]<4b.
$$

Hence $|D_b^M-Z|\leq16q$. The initial and noise coefficients in (T6) differ from
$1$ and $N(\theta)$ by at most $2q$ and $5q$, respectively, and
$|1-N(\theta)|\leq1$. The endpoint argument therefore yields

$$
  R_{R,k}^U\geq\min\{1/2,F_U^-(\theta,\tau)\}-11q
  \quad\text{for every }\theta\in[0,1],\ 0\leq k\leq M. \tag{T7}
$$

### Rare signal: one S candidate and the continuous certificate

For S, use the exact scalar combination $Y_k=C_k/4+H_k$. Equation (T5) gives

$$
  Y_{k+1}=\frac{\widetilde D}{4}C_k+
      (D_b+b^3\theta^2)H_k+b\theta^2(1+b)
  \leq\widetilde D Y_k+b\theta^2(1+b),\qquad
  \widetilde D=1-bd(\theta)+b^2\theta^2. \tag{T8}
$$

Indeed, $\widetilde D-(D_b+b^3\theta^2)=b^2\theta^2(4-b)\geq0$. This inequality
holds for the full recurrence, so no feedback approximation is needed. Since
$R_{R,M}^S\leq Y_M/2$, geometric summation gives

$$
  R_{R,M}^S\leq\frac12\left[(r+s/4)\widetilde D^M+
    \frac{\theta(1+b)}{2-\theta-b\theta}(1-\widetilde D^M)\right].
$$

Define

$$
  F_S(\theta,\tau;s,r)=\frac12\left[(r+s/4)Z+
                         \frac{\theta}{2-\theta}(1-Z)\right].
$$

Because $0\leq d(\theta)-b\theta^2\leq1$, the logarithm remainder and the
explicit plateau difference give

$$
  |\widetilde D^M-Z|\leq4b\left[1+\frac1{2(1-Q)}\right],\qquad
  0\leq\frac{\theta(1+b)}{2-\theta-b\theta}
              -\frac{\theta}{2-\theta}\leq\frac{2b}{1-Q}.
$$

For $r=1$, $s\leq1/100$, these inequalities imply

$$
  R_{R,M}^S\leq F_S(\theta,\tau;1/100,1)+5q. \tag{T9}
$$

The coefficient of $q$ before rounding up to five is bounded by
$\{(401/400)4[1+1/(2(1-Q))]+2/(1-Q)\}/2<5$.

Choose $\theta_S=2/(\tau+4)\in[1/4,2/5]$. The remaining inequality is

$$
  \min\{1/2,F_U^-(\theta,\tau)\}
  -F_S(2/(\tau+4),\tau;1/100,1)\geq1/100
  \quad\text{on }[0,1]\times[1,4]. \tag{T10}
$$

Here is a reproducible rational certificate for the entire rectangle. Both
$d(\theta)$ and $N(\theta)$ increase on $[0,1]$. On $[a_0,a_1]\times[t_0,t_1]$,
set $N_0=N(a_0)$ and bound $Z$ between $e^{-t_1d(a_1)}$ and $e^{-t_0d(a_0)}$.
The expression $(N+(1-N)Z)/2$ increases in $N$ for $Z\in[0,1]$. Its lower bound
uses the lower $Z$ endpoint when $N_0\leq1$ and the upper endpoint otherwise.
Include the minimum with $1/2$ in this bound.

The S candidate has plateau $1/(\tau+3)$ and exponent
$4\tau(\tau+3)/(\tau+4)^2$. The plateau decreases and the exponent increases, so
its risk decreases on $[1,4]$. Its upper bound on the rectangle is attained at
$t_0$.

For each rational $x\in[0,4]$, let $P_{18}(x)=\sum_{j=0}^{18}x^j/j!$. Positivity
and a geometric bound on successive omitted terms give

$$
  P_{18}(x)\leq e^x\leq
  P_{18}(x)+\frac{x^{19}/19!}{1-x/20}. \tag{T11}
$$

Reciprocating encloses $e^{-x}$ using rational arithmetic. The
[checker](../experiments/check_predictive_theorem.py) divides each unresolved
rectangle into four equal rectangles and accepts a leaf only if its lower margin
is at least $1/100$. The 5,035 accepted leaves have maximum depth nine and total
area exactly three. The smallest rational lower margin exceeds $0.01000005$.
This is a finite certificate with interval bounds throughout each leaf, rather
than sampled function values. The earlier checker uses a different exponential
enclosure and subdivision and certifies the same inequality with 3,197 leaves.

Combining (T7), (T9), and (T10), then taking infima, proves

$$
  R_U^*-R_S^*\geq1/100-16q\geq0.0084>0.007. \tag{T12}
$$

### Common signal: a lower bound for every S rate and stop

Now suppose $s=1$ and $r\leq1/100$. The common mean error under S is
$-(1-b\theta)^k\beta_C^*$. If $\theta\leq1/4$, Jensen's inequality and the
logarithm bound imply

$$
  R_{R,k}^S\geq\frac18(1-b\theta)^{2k}
  \geq\frac18\exp\left\{-\frac2{1-Q/4}\right\}>\frac1{60}. \tag{T13}
$$

If $\theta\geq1/4$, let $z=(1-b\theta)^k$. Since $D_b\leq1-b\theta$ and
$\theta/(2-\theta+3b\theta)\geq\theta/2$, common squared bias and direct rare
observation noise give

$$
  R_{R,k}^S\geq z^2/8+\frac{(1-q)^2\theta}{4}(1-z)
  \geq z^2/8+\frac3{50}(1-z)
  \geq\frac{33}{625}>\frac1{60}. \tag{T14}
$$

The last bound minimizes a quadratic over $z\in[0,1]$. Both lower bounds are
uniform, so $R_S^*>1/60$.

### Common signal: one U candidate

Let $h=\sqrt b\leq1/100$, take $u=h$, $\theta_U=4h\leq1$, and stop at $M$.
Define $H_{\max}=\max_{0\leq j\leq M}H_j$. Geometric summation of the common
equation in (T5) gives, for every $j\leq M$,

$$
  C_j\leq A^j+\frac{4h}{2-h}+\frac{4h^3}{2-h}H_{\max}.
$$

Drop rare contraction only for an upper bound, sum this inequality, and use
$M\leq4/h^2$ and $\sum_{j\geq0}A^j=1/\{h(2-h)\}$. Then

$$
  H_{\max}\leq r+\frac{68h^3}{2-h}+64h^2+
                  \frac{64h^5}{2-h}H_{\max}.
$$

The final coefficient is less than one. Therefore

$$
  H_{\max}\leq H_*(h):=
  \frac{1/100+68h^3/(2-h)+64h^2}{1-64h^5/(2-h)},
$$

and $M\geq1/h^2$ yields

$$
  R_{R,M}^U\leq\frac{e^{-2/h}}8+
    \frac{h}{2(2-h)}+
    \left\{\frac12+\frac{h^3}{2(2-h)}\right\}H_*(h)
  <0.01072966<\frac{11}{1000}. \tag{T15}
$$

Every term in the upper bound increases with $h$ on this interval. The checker
verifies its value at $h=1/100$ rationally using $e^{-200}\leq2^{-200}$. It also
verifies the constants in (T13)–(T14) using (T11). Consequently

$$
  R_S^*-R_U^*>\frac1{60}-\frac{11}{1000}>\frac1{200}. \tag{T16}
$$

Multiplying (T12) and (T16) by $\sigma^2$ proves the theorem.

## Verification and remaining review

Inside `devenv shell`, run `make check-predictive-theorem`. The checker imports
none of the earlier experiment scripts. It certifies (T10), the transfer
constants, and the common-signal bounds with exact fractions. Separately, it
constructs a full four-coordinate tensor moment operator directly from the four
observation cells. Thirty rational cases verify the scalar reduction, absence of
cross-moment feedback, and contraction inequalities, including zero and tiny
rates. It checks 882 finite bounds using 70-digit arithmetic, including interior
and endpoint stops and both signal families. The square-root candidate rate is
approximated to 70 digits in those diagnostics.

The finite calculations support the implementation and are not outward-rounded
certificates. The continuous theorem relies on the displayed inequalities and
the exact rational certificate. The existing `make check-predictive-claim`
checks also pass, including the general remainder theorem and its original
predictive comparison. No frozen study is changed by these checks.

The new proof and independently implemented computation were produced in the
same local work session. This is additional verification, not an independent
researcher or agent review. Independent proof review and human review remain
open. A reviewer should check the oracle quantifiers and rate restrictions, the
finite-prevalence transfers, and the continuum certificate, then assess the
contribution separately.

## What the result adds, and what remains a judgment

These primary passages were rechecked on September 16, 2026. HTML was inspected
for the first three sources, and published PDF pages for the last two. This is a
bounded comparison of statements, not an exhaustive priority search or a review
of those papers' proofs. The assessments are ours.

  | Source and passage                                                                                                                                                                                | Established overlap                                                                                                  | Relation to this theorem                                                                                                                                                       |
  | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
  | [Su, Zou, and Wu, v3](https://arxiv.org/html/2403.08585v3), (3.1)–(3.2), Assumption 3.2, Theorem 4.2, Appendix A.1                                                                                | Constant-step preconditioned fresh SGD, moment analysis, and aggregate-risk bounds for tail averaging.               | The displayed bounds do not order the final-iterate U/S infima in (T3). The moment calculation is established machinery.                                                       |
  | [Défossez and Bach, AdaBatch v1](https://arxiv.org/html/1711.01761v1), Table 1 and Appendix C.2, (7.21)–(7.23)                                                                                    | Frequency-dependent learning, increased noise, batch-dependent step restrictions, and deterministic preconditioning. | These mechanisms explain the tradeoff. Their stated bounds do not give the two opposite rare-risk separations over (T2).                                                       |
  | [Liu et al., v1](https://arxiv.org/html/2502.09047v1), Sections 3.1–5.1, Theorems 2–4                                                                                                             | Target-aware minimax linear preconditioning and target-risk bounds for scheduled accelerated SGD.                    | Set their source and target moments to our $C$ and $C_R$. Their criterion and optimizer differ from the fixed-signal, constant-step comparison here.                           |
  | [Lei, Hu, and Lee, ICML 2021](https://proceedings.mlr.press/v139/lei21a/lei21a.pdf#page=3), Theorems 3.2 and 3.4, Remark 3.1, PDF pp. 3–4                                                         | Target-aware shrinkage and a separation from optimally tuned ridge, including commuting source/target geometry.      | A separation surviving scalar retuning is already an established type of result. Their estimator and comparison do not directly give (T3)'s orderings.                         |
  | [Wu et al., NeurIPS 2022](https://papers.nips.cc/paper_files/paper/2022/file/d5c04aa72b92c53bda5b525b60958295-Paper-Conference.pdf#page=4), SGD definition, Assumption 1, Corollary 3.3, pp. 4, 6 | Last-iterate target-risk analysis for online SGD with geometric step decay, including source-only training.          | The output iterate and target criterion are established. Their schedules differ, and their lower fourth-moment condition fails for the constant-square common coordinate here. |

For example, the rare fourth moment gives necessary constants $\alpha\geq1/b-4$
in Su–Zou–Wu's centered fourth-moment condition and $\psi\geq1/b-3$ in Liu et
al.'s displayed full fourth-moment condition. Liu et al. also state a weaker
alternative for finite-norm signals. Divergence of the displayed constant does
not exclude their entire theory. In Wu et al., the failure concerns the lower
condition, not the upper-bound framework.

**Concrete contribution:** the theorem identifies two signal families where
relative feature scaling changes the attainable rare-risk envelope by a gap
bounded away from zero as $q\downarrow0$, throughout a fourfold budget interval
and after separate scalar rate and stopping choices. It answers an ambiguity
left by fixed-configuration reversals: allowing those choices does not always
remove a difference between normalizations. Prevalence alone does not determine
which rule wins in this model.

**Current judgment:** this is a useful, restricted comparative result. None of
the inspected statements directly supplies its particular inequalities. That
supports describing the added calculation precisely; it does not establish
publication-level novelty. The short proof also makes clear how much it relies
on elementary moment analysis. Using that analysis is neither a novelty claim
nor a reason by itself to dismiss the conclusion.

The restrictions matter to the contribution assessment: independent features,
two dimensions, $q\leq10^{-4}$, $B=1$, exact dominant signal-to-noise equality,
known preprocessing, a fixed intercept, constant rates in a restricted domain,
and final iterates. There is no aggregate-risk ordering, general phase boundary,
minimax comparison, optimal schedule, or validation-selection guarantee here.
The missing-group failures in the practical studies remain limitations.

Retain the result as a supporting theorem while its mathematical and scientific
review is pending. Choosing it as a main contribution, or pursuing a stronger
dependence-sensitive statement, is a subsequent research decision. The held-out
prediction experiment and additional categorical task require their own declared
protocol; these development calculations do not complete that milestone.
