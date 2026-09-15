# Normalization-risk reversals with controlled bounds

September 15, 2026. Develops [C1](normalization-risk-comparison.md) and the
aggregate-versus-rare-presence target in [TODO.md](../TODO.md).

## Status and interpretation

**There are two quantitative comparisons:** C1's stopping and batch reversal
holds throughout its declared parameter box, and a feasible dependent-feature
family gives opposite aggregate and rare-presence orderings at a common budget.
The proofs below include finite certificates using outward-rounded integer
arithmetic. Independent update enumeration and the existing moment operator
check the formulas separately. An independent agent's mathematical
[review](normalization-risk-review.md) is recorded separately from novelty.

The general moment framework and learning-versus-noise mechanism are prior work;
see the [source comparison](normalization-risk-audit.md). These results
establish explicit comparisons within that framework. They do not settle
priority, publication-level novelty, robustness to retuning, or practical
usefulness. The parameter choices are exploratory selections, not a
preregistered study.

## Model, training, and test risks

Let $I,J$ be binary, with $P(I=1)=1/2$, $P(J=1)=q$, $0<q<1/2$, and

$$
  P(I=1,J=1)=\frac{q(1+\ell)}2,\qquad -1\leq\ell\leq1.
$$

In cell order $(0,0),(0,1),(1,0),(1,1)$, the probabilities are

$$
  \left(\frac12-\frac{q(1-\ell)}2,
  \frac{q(1-\ell)}2,
  \frac12-\frac{q(1+\ell)}2,
  \frac{q(1+\ell)}2\right).
$$

All are nonnegative. Independence is $\ell=0$, nesting $J\leq I$ is $\ell=1$,
and $\ell=-1$ excludes simultaneous presence. Set

$$
  x=(I-1/2,J-q)^\top,\quad y=x^\top\beta^*+\varepsilon,\quad
  E(\varepsilon\mid x)=0,\quad E(\varepsilon^2\mid x)=\sigma^2.
$$

Population centering, feature scales, and the zero intercept are known and
fixed. Initialization is zero. Each update uses $B$ new independent
observations, with fresh response noise. The independent test point follows the
same law. No Gaussian assumption is needed. Risks exclude irreducible test
noise.

Write $a=1/4$, $b=q(1-q)$, and $c=q\ell/2$. The two configurations are

$$
  P_U=I_2,\quad\eta_U=4h,\qquad
  P_S=\operatorname{diag}(a^{-1},b^{-1}),\quad\eta_S=h.
$$

Thus $D=\eta P$ has diagonal $(d_C,d_R)=(4h,4h)$ for U and $(4h,h/b)$ for S.
These steps match the common-coordinate diagonal drift $d_Ca=h$. Under
independence they match the complete common-coordinate mean trajectory. Under
dependence the means also contain cross-coordinate drift and generally do not
match. This is a fixed calibration, without tuning or iterate averaging.

For $V_k=E[(\hat\beta_k-\beta^*)(\hat\beta_k-\beta^*)^\top]$, define

$$
  C=\begin{pmatrix}a&c\\c&b\end{pmatrix},\qquad
  C_R=E[xx^\top\mid J=1]
  =\begin{pmatrix}a&\ell(1-q)/2\\\ell(1-q)/2&(1-q)^2\end{pmatrix},
$$

$$
  R_k=\tfrac12\operatorname{tr}(CV_k),\qquad
  R_{R,k}=\tfrac12\operatorname{tr}(C_RV_k).
$$

The conditional second moment includes the conditional mean. Within each U/S
comparison, $B$, $k$, the signal, noise, and test law agree. Both methods use
$M=kB$ distinct observations. Define every contrast as S minus U.

## Proposition 1: exact moments and variance separation

Put $s_k=(V_{CC,k},V_{CR,k},V_{RR,k})^\top$. Define

$$
  t_B=c^2+\frac{ab-c^2}{B},\qquad
  m_B=c\left\{b+\frac{1-4b}{B}\right\}.
$$

Then $s_{k+1}=L_Ds_k+\sigma^2g_D$, where

$$
  L_D=\begin{pmatrix}
  (1-d_Ca)^2&-2d_C(1-d_Ca)c&d_C^2t_B\\
  -d_R(1-d_Ca)c&(1-d_Ca)(1-d_Rb)+d_Cd_Rt_B&-d_Cc+d_Cd_Rm_B\\
  d_R^2t_B&-2d_Rc+2d_R^2m_B&(1-d_Rb)^2+d_R^2b(1-4b)/B
  \end{pmatrix},
$$

$$
  g_D=\frac1B(d_C^2a,d_Cd_Rc,d_R^2b)^\top,
  \qquad s_0=((\beta_C^*)^2,\beta_C^*\beta_R^*,(\beta_R^*)^2)^\top.
$$

Let $\mathcal T_D$ be the corresponding map on symmetric matrices. For
$e_k=E(\hat\beta_k-\beta^*)=-(I-DC)^k\beta^*$, the exact decomposition is

$$
  V_k=e_ke_k^\top+A_k+\sigma^2N_k,
$$

$$
  A_k=\mathcal T_D^k(\beta^*\beta^{*\top})-e_ke_k^\top,\qquad
  N_k=\sum_{j=0}^{k-1}\mathcal T_D^j(DCD/B).
$$

Both $A_k$ and $N_k$ are positive semidefinite. Accordingly,
$\tfrac12e_k^\top We_k$, $\tfrac12\operatorname{tr}(WA_k)$, and
$\tfrac12\sigma^2\operatorname{tr}(WN_k)$ separate squared prediction bias,
multiplicative update variance, and propagated observation-noise variance for
$W=C$ or $C_R$.

### Proof

For a batch, write its second moment as
$\widehat C=\left(\begin{smallmatrix}a&\widehat c\\\widehat c&\widehat b\end{smallmatrix}\right)$.
The first diagonal is constant because $(I-1/2)^2=a$. The binary identities give

$$
  E x_R^4=b(1-3b),\qquad E x_C^2x_R^2=ab,\qquad
  E x_Cx_R^3=c(1-3b).
$$

Consequently $E\widehat c^2=t_B$, $E(\widehat c\widehat b)=m_B$, and
$E\widehat b^2=b^2+b(1-4b)/B$. Expanding $E[(I-D\widehat C)V_k(I-\widehat CD)]$
gives the displayed matrix. Conditional mean-zero noise eliminates its cross
terms with the previous error and the batch update matrix. Its unconditional
covariance is $\sigma^2DCD/B$. Fresh sampling makes the new update independent
of the previous error.

To identify the decomposition, run the noiseless process on the same feature
stream. Its mean is $e_k$, its second moment is
$\mathcal T_D^k(\beta^*\beta^{*\top})$, and its covariance is $A_k$. Conditional
on all features, the noise-driven process has mean zero. Its cross moment with
the noiseless process is zero, and its covariance is the finite sum
$\sigma^2N_k$. This proves the decomposition and positivity. This is a binary
specialization of the established [finite-update
identities](../paper/sections/discrete-dynamics.tex). $\square$

## Proposition 2: a scalar threshold with a controlled remainder

Assume independence, so $c=0$. The diagonal moments close under

$$
  K_D=\begin{pmatrix}A&e\\f&D_0\end{pmatrix},\qquad
  A=(1-h)^2,\quad e=\frac{d_C^2ab}{B},\quad f=\frac{d_R^2ab}{B},
$$

$$
  D_0=(1-d_Rb)^2+\frac{d_R^2b(1-4b)}B,
  \qquad g=(d_C^2a,d_R^2b)^\top/B.
$$

Here $D_0$ denotes a scalar, distinct from the effective-step matrix $D$. All
entries of $K_D$ and $g$ are nonnegative. Let

$$
  w=\tfrac12(a,(1-q)^2)^\top,\quad v_0=((\beta_C^*)^2,(\beta_R^*)^2)^\top,
  \quad E_0=\max(e,f),\quad \rho\geq\|K_D\|_\infty,\quad \rho<1.
$$

For $k\geq1$, define $\phi_k(z)=\sum_{j=0}^{k-1}z^j$ and the scalar proxy

$$
  \widetilde R_{R,k}=
  w_C\{A^k(\beta_C^*)^2+\sigma^2g_C\phi_k(A)\}
  +w_R\{D_0^k(\beta_R^*)^2+\sigma^2g_R\phi_k(D_0)\}.
$$

The omitted coupling is nonnegative and satisfies

$$
  0\leq R_{R,k}-\widetilde R_{R,k}
  \leq E_F+\sigma^2E_N,
$$

$$
  E_F=\|w\|_1\|v_0\|_\infty E_0k\rho^{k-1},\qquad
  E_N=\frac{\|w\|_1\|g\|_\infty E_0}{(1-\rho)^2}.
  \tag{1}
$$

This bound holds for every independent-design parameter choice satisfying its
stability condition, not only the boxes below. The homogeneous scalar term still
includes update variance: squared rare bias uses $(1-d_Rb)^{2k}$, whereas
$D_0^k$ also includes the rare fourth-moment contribution.

The common terms cancel in the U/S proxy contrast. With subscripts denoting the
two configurations, put

$$
  \widetilde F=w_R(\beta_R^*)^2(D_S^k-D_U^k),\qquad
  \widetilde N=w_R\{g_{R,S}\phi_k(D_S)-g_{R,U}\phi_k(D_U)\}.
$$

For the exact contrast $\Delta_{B,k}=F+\sigma^2N$, (1) gives

$$
  F_-:=\widetilde F-E_{F,U}\leq F\leq
  F_+:=\widetilde F+E_{F,S},
$$

$$
  N_-:=\widetilde N-E_{N,U}\leq N\leq
  N_+:=\widetilde N+E_{N,S}.
$$

If $F_+<0<N_-$, the exact noise-variance threshold $\tau=-F/N$ obeys

$$
  \frac{-F_+}{N_+}\leq\tau\leq\frac{-F_-}{N_-}. \tag{2}
$$

In particular, $F_++\sigma^2N_+<0$ guarantees lower rare risk for S, and
$F_-+\sigma^2N_->0$ guarantees lower rare risk for U. These are sufficient
conditions, with an explicit error bound, rather than a claim of a unique
crossing as the stopping count varies.

### Proof

Let $K_0=\operatorname{diag}(A,D_0)$ and $E=K_D-K_0\geq0$ entrywise. The
telescoping identity

$$
  K_D^k-K_0^k=\sum_{j=0}^{k-1}K_D^{k-1-j}EK_0^j
$$

is entrywise nonnegative. Since $\|K_0\|_\infty\leq\rho$ and $\|E\|_\infty=E_0$,
its norm is at most $k\rho^{k-1}E_0$. Multiplying by $w$ and $v_0$ proves the
homogeneous bound. Apply the same identity to each term of the finite noise sum
and use $\sum_{j=1}^{k-1}j\rho^{j-1}\leq(1-\rho)^{-2}$ to prove the noise bound.
Taking the difference between two nonnegative remainders gives the asymmetric
bounds above. Division by positive $N_-$ and $N_+$ proves (2). $\square$

### What the bound explains

SD scaling changes the rare mean contraction from $1-4hb$ to $1-h$. The noise
injection changes from $16h^2b/B$ to $h^2/(bB)$, and the rare fourth-moment
correction changes with it. The bias gain can dominate early, then decay below
the additional propagated noise. Increasing $B$ reduces both the fourth-moment
correction and the noise injection. Formula (2) makes this explanation
quantitative and includes the interaction with the common feature through (1).
The existence of this tradeoff is established prior art.

## Theorem C1: uniform stopping and batch reversal

For $\ell=0$, take

$$
  q\in[0.019,0.021],\quad h\in[0.0019,0.0021],\quad
  \beta_C^*,\beta_R^*\in[0.95,1.05],\quad \sigma^2\in[1.5,5].
$$

Both configurations are mean-square stable for $B\in\{1,10\}$. The following
closed enclosures hold throughout the box. The decimals are rational bounds,
rounded outward from the certificate.

  | $B$ | $k$    | $M$     | Exact rare-risk contrast $\Delta_{B,k}$ | Exact noise threshold $\tau_{B,k}$ |
  | --- | ------ | ------- | --------------------------------------- | ---------------------------------- |
  | 1   | 1,000  | 1,000   | $[-0.353,-0.160]$                       | $[10.46,17.76]$                    |
  | 1   | 10,000 | 10,000  | $[0.0021,0.125]$                        | $[0.53,1.405]$                     |
  | 10  | 1,000  | 10,000  | $[-0.386,-0.286]$                       | $[112.61,184.22]$                  |
  | 10  | 10,000 | 100,000 | $[-0.0281,-0.0016]$                     | $[5.69,14.49]$                     |

The threshold bounds apply without restricting $\sigma^2$. In particular, every
$\sigma^2\in(1.405,5.69)$ gives the four signs in C1 uniformly over the other
parameters. The displayed risk-gap bounds use $[1.5,5]$.

Thus there is a stopping reversal at $B=1$ and a change in normalization
ordering across batches at $k=10{,}000$. At $M=10{,}000$, comparing
$(B,k)=(1,10{,}000)$ with $(10,1{,}000)$ also changes the normalization
ordering. This does not order batch sizes within either normalization rule.

### Proof and finite certificate

Partition each of the $q$ and $h$ intervals into eight equal closed pieces. On
each of the resulting 64 rectangles, evaluate Proposition 2 with interval
arithmetic, using $(\beta_C^*)^2,(\beta_R^*)^2\in[0.9025,1.1025]$. For each
configuration use the upper row-sum bound $\rho=\max(A+e,D_0+f)$ and
$E_0=\max(e,f)$, enclosing both expressions over the rectangle. The certificate
obtains $\rho<0.999719$ throughout. The remaining cross moment propagates by

$$
  \gamma=(1-d_Ca)(1-d_Rb)+d_Cd_Rab/B,
$$

with no noise injection. The certificate also checks $0\leq\gamma<1$ on each
rectangle, proving stability of the full homogeneous second-moment map. With
fixed finite noise injection this gives bounded noisy second moments.

On every rectangle $F_+<0<N_-$. Formula (2) and the interval $F+\sigma^2N$ give
the displayed enclosures after taking their hull over all rectangles. Closed
rectangles cover their common boundaries; there are no unsampled gaps in this
argument.

The [certificate script](../experiments/check_normalization_risk_theorem.py)
represents every endpoint by an integer multiple of $10^{-60}$. Addition is
exact. Products take the minimum and maximum of all four endpoint products,
rounding down and up by integer division. For a positive denominator interval
$[l,u]$, its reciprocal is enclosed by

$$
  \left[\frac{\lfloor10^{120}/u\rfloor}{10^{60}},
  \frac{\lceil10^{120}/l\rceil}{10^{60}}\right],
$$

where $l,u$ are the stored integers. Negative denominators are reduced to this
case. Powers and finite sums use repeated squaring and addition. Induction on
these operations proves enclosure of every exact rational expression used above.
All inputs are rational strings or integers, and all acceptance checks compare
integer endpoints. Binary floating-point output is only a display. Assertions
also verify containment in the rational bounds reported here. This is a
computer-assisted proof using Proposition 2, not an empirical grid check.
$\square$

### Separating the mechanism at the original prevalence and rates

For $q=0.02$, $h=0.002$, $B=1$, $\beta^*=(1,1)$, and $\sigma^2=3$, the
exact-moment calculation gives the following rare-risk decomposition (displayed
values are rounded, not interval certificates).

  | $k$    | Scaling | Squared bias     | Update variance  | Observation-noise variance | Total    |
  | ------ | ------- | ---------------- | ---------------- | -------------------------- | -------- |
  | 1,000  | U       | 0.353207         | 0.000443         | 0.003028                   | 0.356678 |
  | 1,000  | S       | 0.011040         | 0.002315         | 0.077052                   | 0.090407 |
  | 10,000 | U       | 0.020863         | 0.000245         | 0.007037                   | 0.028145 |
  | 10,000 | S       | below $10^{-16}$ | below $10^{-16}$ | 0.078788                   | 0.078788 |

At the early stop, S's bias reduction exceeds its additional variance. Later, U
has learned enough of the rare signal for its smaller observation-noise variance
to give the lower risk. Update variance is included throughout.

## Theorem C2: aggregate and subgroup disagreement

Take

$$
  q=0.02,\quad \ell\in[0.9,1],\quad \beta^*=(2,1)^\top,\quad
  h=0.01,\quad B=1,\quad k=M=100,\quad \sigma^2\in[3.8,4.1].
$$

Both configurations are mean-square stable, and, uniformly over these dependence
and noise intervals,

$$
  0.00077\leq R_k^S-R_k^U\leq0.00194,
  \qquad
  -0.0983\leq R_{R,k}^S-R_{R,k}^U\leq-0.0233. \tag{3}
$$

Thus aggregate risk favors U while rare-presence risk favors S for the same two
fitted configurations, training budget, and test law. The result includes
interior feasible laws with all four cell probabilities positive, as well as the
nested endpoint. It is a fixed-prevalence result, without an asserted asymptotic
order as $q\to0$.

Throughout this same parameter rectangle, S has **larger mean squared error for
each coefficient separately**:

$$
  V_{CC,k}^S>V_{CC,k}^U,\qquad V_{RR,k}^S>V_{RR,k}^U.
$$

Its smaller rare-presence prediction risk therefore depends on the cross moment
of the coefficient errors. Ranking original-scale coefficient errors separately
would miss this advantage.

### Proof

For stability, any feature vector $z$ with $\|z\|^2\leq L$ satisfies

$$
  E[(I-\eta zz^\top)^2]\preceq I-\eta(2-\eta L)H,
  \qquad H=Ezz^\top.
$$

If $H\succ0$ and $0<\eta<2/L$, this contracts squared error in expectation. For
U, $L=0.25+0.98^2=1.2104$, $\eta=0.04$, and
$\lambda_{\min}(C)\geq0.0196-0.01=0.0096$ by the row-sum eigenvalue bound. For
S, the standardized feature has $L=50$, $\eta=0.01$, and

$$
  H=\begin{pmatrix}1&\ell/7\\\ell/7&1\end{pmatrix},\qquad
  \lambda_{\min}(H)\geq6/7.
$$

These sufficient bounds hold even over $\ell\in[-1,1]$.

For the risks, augment the matrix in Proposition 1 by its unit-noise column and
a final row $(0,0,0,1)$. Its $100$th power gives the homogeneous map and the
finite noise sum. Take the difference of its S and U powers. The risk weights on
$(V_{CC},V_{CR},V_{RR})$ are

$$
  w_A=(a/2,c,b/2)^\top,\qquad
  w_R=(a/2,\ell(1-q)/2,(1-q)^2/2)^\top.
$$

Partition $[0.9,1]$ into 128 equal closed intervals. On each, the same integer
interval arithmetic encloses the two augmented powers, multiplication by
$s_0=(4,2,1)^\top$, and both weighted contrasts $F_W+\sigma^2N_W$ for
$\sigma^2\in[3.8,4.1]$. Signed matrix entries use all four endpoint products;
entrywise positivity is not assumed here. The union is enclosed by (3), with
integer assertions checking these rational bounds. The same augmented powers,
before risk weighting, certify the two positive diagonal contrasts and a
negative cross-moment contrast on every dependence interval. $\square$

### Size of the effect and dependence on signal signs

At $\ell=1$ and $\sigma^2=4$, the risks are

  | Risk          | U          | S          | S minus U   |
  | ------------- | ---------- | ---------- | ----------- |
  | Aggregate     | 0.08545538 | 0.08675606 | 0.00130069  |
  | Rare presence | 0.75545570 | 0.68273163 | -0.07272408 |

Relative to U, S increases aggregate excess risk by about 1.52% and decreases
rare-presence excess risk by about 9.63%. These percentages describe this
selected example only. Its rare-risk advantage is not a nearly zero threshold
artifact. On the original response scale the signal coefficients are two and
one, and the noise standard deviation is two.

More specifically, let $\Delta V=V_k^S-V_k^U$. The two test weights give the
identity

$$
  \Delta_R-\Delta_A=
  \frac{1-2q}{2}\{(1-q)\Delta V_{RR}+\ell\Delta V_{CR}\}. \tag{4}
$$

At this endpoint,

$$
  \Delta V\approx
  \begin{pmatrix}0.022743&-0.615146\\-0.615146&0.470335\end{pmatrix}.
$$

The aggregate risk weights the cross moment by $c=0.01$, while rare-presence
risk weights it by $\ell(1-q)/2=0.49$. The much smaller joint error product
under S outweighs its larger individual errors for rare-presence prediction.
This product includes the product of the biases as well as centered covariance;
it must not be interpreted as covariance alone. Equation (4) states exactly how
dependence can change the objective comparison.

The exact contrast for an arbitrary signal has the form

$$
  \Delta_W=A_W(\beta_C^*)^2+2B_W\beta_C^*\beta_R^*
  +D_W(\beta_R^*)^2+\sigma^2N_W. \tag{5}
$$

These coefficients are obtained by weighting the three columns of $L_S^k-L_U^k$
(with $2B_W$ the middle-column coefficient). Therefore, when $N_W>0$, (5) gives
the precise signal-dependent noise threshold. The coefficients $A_W,D_W,N_W$ are
even in $\ell$ and $B_W$ is odd: reflecting $I$ to $1-I$ reverses $\ell$ and the
common coefficient, while reversing both signal coefficients leaves every
second-moment risk unchanged. This also proves that replacing $(\ell,\beta_R^*)$
with $(-\ell,-\beta_R^*)$ preserves both risks with $\beta_C^*$ fixed. Under
independence, $B_W=0$ and signal signs cannot matter.

At $q=0.02,h=0.01,B=1,k=100,\beta_C^*=2$, the certified calculations give these
thresholds (decimals are rounded displays):

  | $\ell$ | $\beta_R^*$ | Aggregate threshold | Rare threshold | Ordering at $\sigma^2=4$                                      |
  | ------ | ----------- | ------------------- | -------------- | ------------------------------------------------------------- |
  | 0      | 1           | 2.118182            | 2.118399       | U has lower risk for both objectives.                         |
  | 1      | 1           | 3.495006            | 4.574740       | U has lower aggregate risk; S has lower rare risk.            |
  | 1      | -1          | 0.909952            | 0.711041       | U has lower risk for both objectives.                         |
  | -1     | -1          | 3.495006            | 4.574740       | The same disagreement as positive dependence and equal signs. |

For the opposite-sign nested signal, noise variance strictly between its two
thresholds gives the other orientation: S has lower aggregate risk and higher
rare risk. The signal sign therefore changes both the interval and its
orientation; the result does not extend to every dependence or signal.

## Reproduction and remaining research work

Inside `devenv shell`, run `make check-normalization-risk`. The new certificate
script writes no reference artifacts. Its three-moment formulas agree at 64
endpoints with the existing full moment implementation, including short paths
checked by enumeration of actual gradient updates, a mixed-sign signal,
dependence endpoints and an interior law, and $B=1,2$. These comparisons use
floating point and serve a different role from the exact interval certificates.
The frozen pilot and the first fresh-sample artifacts are preserved.

The independent [review](normalization-risk-review.md) assesses both the algebra
and the certificate's enclosure argument. Robustness over prevalence, rates,
stopping counts, signal magnitudes, averaging, estimated preprocessing, and
validation-based selection remains separate work. Neither (2) nor (3)
establishes different globally optimal configurations for the two risk
objectives. The [novelty audit](normalization-risk-audit.md) distinguishes these
concrete contributions from the established general mechanism.
