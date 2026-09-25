# Limiting oracle risks for the two-feature model

This working derivation extends the fixed-rate limits in [the common-feature
notes](../experiments/common_block/README.md) to the unrestricted rate-and-stop
oracles in the manuscript. It covers arbitrary fixed signal strengths and noise
variance in the two-feature model. It has numerical checks, but has not received
an independent mathematical review and is not yet part of the manuscript.

## Statement

Retain the independent binary model, population preprocessing, fresh
observations, zero initialization, fixed zero intercept, and final iterates.
Write

$$
  s=(\beta_C^*)^2,\qquad r=(\beta_R^*)^2,\qquad
  \nu=\sigma^2,\qquad b=q(1-q),\qquad w=(1-q)^2.
$$

Fix finite $s,r,\nu\geq0$ and $0<\tau<\infty$. Let $q\to0$ and let integer
observation caps satisfy $M_qb\to\tau$. Each oracle minimizes over all
nonnegative constant rare-coordinate steps $\alpha$ and deterministic integer
stops $0\leq k\leq M_q$, including rates that are not mean-square stable.

For $0\leq\alpha\leq1$, define

$$
  d(\alpha)=\alpha(2-\alpha),\qquad
  z(\alpha)=e^{-\tau d(\alpha)},\qquad
  g(\alpha)=\frac{\nu\alpha}{8-\alpha},
$$

and

$$
  \begin{aligned}
  F_S(\alpha;s,r,\nu,\tau)
    &=\frac12\left[
      (s/4+r)z(\alpha)
      +\frac{\nu\alpha}{2-\alpha}\{1-z(\alpha)\}
    \right],\\
  F_U(\alpha;r,\nu,\tau)
    &=\frac12\left[
      g(\alpha)+rz(\alpha)
      +\frac{\alpha\{\nu+g(\alpha)\}}{2-\alpha}
        \{1-z(\alpha)\}
    \right].
  \end{aligned}
$$

**Oracle-limit claim.** Under these assumptions,

$$
  \lim_{q\to0}R_S^*(M_q)
    =\min_{0\leq\alpha\leq1}F_S(\alpha;s,r,\nu,\tau),
  \qquad
  \lim_{q\to0}R_U^*(M_q)
    =\min_{0\leq\alpha\leq1}F_U(\alpha;r,\nu,\tau).
$$

Both minima exist by continuity. The endpoint $F_U(0)=r/2$ represents rates with
$b\ll\alpha_q\ll1$ at the full cap. It does **not** represent literal zero-rate
training, whose limiting risk is $s/8+r/2$. In contrast, $F_S(0)=(s/4+r)/2$ is
the initialization risk.

The proof below handles prevalence-dependent rates and stops explicitly. It does
not interchange an infimum and a pointwise limit without further control.

## Exact recurrence

Use the manuscript's unweighted common coefficient MSE $C_k$ and set
$G_k=C_k/4$. Then

$$
  \begin{aligned}
  G_{k+1}&=(1-u)^2G_k+u^2bH_k+u^2\nu,\\
  H_{k+1}&=D_b(\alpha)H_k+b\alpha^2(G_k+\nu),\\
  D_b(\alpha)&=1-b\alpha(2-\alpha+3b\alpha),\\
  G_0&=s/4,\qquad H_0=r,\qquad
  R_{R,k}=\tfrac12(G_k+wH_k),
  \end{aligned}
$$

where $u=b\alpha$ for S and $u=\alpha/4$ for U. All update coefficients are
nonnegative. In particular, $D_b=(1-b\alpha)^2+b\alpha^2(1-4b)\geq0$.

## Standardization

### Bounded rates

On any fixed compact rate interval, the augmented affine transition for
$(G,H,1)$ is $I+bL(\alpha)+O(b^2)$, uniformly in $\alpha$, where

$$
  L(\alpha)=
  \begin{pmatrix}
    -2\alpha&0&0\\
    \alpha^2&-d(\alpha)&\alpha^2\nu\\
    0&0&0
  \end{pmatrix}.
$$

For bounded $kb$, its powers converge uniformly to $e^{kbL(\alpha)}$. Indeed,
the one-step difference from $e^{bL(\alpha)}$ is $O(b^2)$, both operators have
norms bounded by $1+O(b)$, and telescoping over at most $T/b$ steps gives an
$O(b)$ error. Thus if $\alpha_q\to a<\infty$ and $k_qb\to t$, the limiting
equations are

$$
  \dot G=-2aG,\qquad
  \dot H=-d(a)H+a^2(G+\nu).
$$

Their sum $W=G+H$ satisfies the proposed scalar equation

$$
  \dot W=-d(a)W+a^2\nu,\qquad W(0)=v:=s/4+r.
$$

The limiting risk is $W(t)/2$. For $0<a<2$ this is $F_S$ with $\tau$ replaced by
$t$. At $a=0$ it is $v/2$, and at $a=2$ it is $(v+4\nu t)/2$.

### Rates escaping to infinity

An exact scalar lower bound controls this case. Summing the recurrences gives

$$
  W_{k+1}
  \geq\lambda_b(\alpha)W_k+b\alpha^2\nu,
  \qquad
  \lambda_b(\alpha)
    =1-2b\alpha+b\alpha^2(1-3b+b^2).
$$

The common-coordinate coefficient exceeds $\lambda_b$ by $b^2\alpha^2(4-b)$; the
rare-coordinate coefficient equals $\lambda_b$. The exact noise contribution is
$b\alpha^2(1+b)\nu$. Also $\lambda_b\geq0$: its minimum over $\alpha$ is
$1-b/(1-3b+b^2)>0$ for $0<b\leq1/4$.

For $\alpha\geq2/(1-3b+b^2)$, $\lambda_b\geq1$, so $W_k\geq v$ at every stop and
$R_{R,k}\geq wv/2$. These rates cannot beat initialization in the limit. This is
an asymptotic exclusion, not a claim that they are dominated at every finite
prevalence.

All remaining rates lie in a compact interval as $q\to0$. The bounded-rate limit
therefore covers every potentially improving sequence, including rates tending
to zero and stops with $k_qb\to0$.

## Unscaled training

### Positive limiting rates and positive rescaled time

Suppose $\alpha_q\to a\in(0,2]$ and $k_qb\to t>0$. The common multiplier
$A=(1-\alpha/4)^2$ is bounded above by a constant $\rho<1$ for all sufficiently
small $q$. Its noise-only equilibrium is

$$
  \frac{u^2\nu}{1-A}=g(\alpha)=\frac{\nu\alpha}{8-\alpha}.
$$

First, both moments are uniformly bounded up to $M_q$. To see this, put
$H_{\max}=\max_{j\leq M_q}H_j$. The common recurrence gives

$$
  G_j\leq A^j s/4+g(\alpha)
       +\frac{b\alpha}{8-\alpha}H_{\max}.
$$

On a compact rate interval around $a$, $D_b\leq1+Kb$ for a fixed $K$. Summing
the rare recurrence, with $M_qb$ bounded, bounds $H_{\max}$ by a fixed constant
plus $O(b)H_{\max}$. Absorb the latter term for small $b$.

More precisely, the common recurrence now gives

$$
  |G_j-g(\alpha)|
    \leq \rho^j|s/4-g(\alpha)|+O(b),
  \qquad
  b\sum_{j<M_q}|G_j-g(\alpha)|=O(b).
$$

Consequently, replacing $G_j$ by $g(\alpha)$ in the rare recurrence changes its
endpoint by $O(b)$. The remaining scalar recurrence converges to

$$
  \dot H=-d(a)H+a^2\{\nu+g(a)\},\qquad H(0)=r.
$$

At positive rescaled time, $G_{k_q}\to g(a)$. For $0<a<2$, the limiting risk is
$F_U$ with $\tau$ replaced by $t$. At $a=2$ the limit is
$\{g(2)+r+4(\nu+g(2))t\}/2\geq r/2$.

### Vanishing rates and short stops

If $\alpha_q\to0$, positivity and $D_b\geq1-2b\alpha_q$ give

$$
  H_{k_q}\geq D_b^{k_q}r
     \geq(1-2b\alpha_q)^{M_q}r\longrightarrow r.
$$

Thus the limiting lower bound is $r/2$, whatever happens to the common moment.
If rates instead have a positive bounded limit but $k_qb\to0$, the same
conclusion follows from $D_b=1+O(b)$ and $H_{k_q}\geq D_b^{k_q}r$.

The bound $r/2$ is attainable. Take $\alpha_q=\sqrt b$ and $k_q=M_q$. More
generally, any $b\ll\alpha_q\ll1$ works. The rare recurrence has $D_b\leq1$ for
small $q$, and the preceding common bound implies $H_{\max}\leq r+O(\alpha_q^2)$
after absorbing its feedback term. Together with the rare lower bound, this
yields $H_{M_q}\to r$. Meanwhile,

$$
  G_{M_q}\leq (1-\alpha_q/4)^{2M_q}s/4
    +g(\alpha_q)+\frac{b\alpha_q}{8-\alpha_q}H_{\max}
    \longrightarrow0,
$$

because $M_q\alpha_q\to\infty$ and $g(\alpha_q)\to0$.

### Large rates

For $\alpha\geq2/(1-3b)$, $D_b\geq1$, so $H_k\geq r$ at every stop and
$R_{R,k}\geq wr/2$. These rates cannot improve on the vanishing-rate recovery
sequence in the limit. All other rates have subsequences converging into
$[0,2]$, already covered above. No stability assumption is needed.

## Completing the oracle argument

For the lower bound, choose rates and stops within an error tending to zero of
each finite-prevalence infimum, then take a subsequence attaining the lower
limit. The large-rate bounds either finish the comparison or restrict the rates
to a compact interval. Extract convergent rate and rescaled-stop subsequences.
The preceding cases give exactly the limiting trajectories or the initialization
and $r/2$ lower bounds.

For a rate $0<a<2$, each limiting trajectory is monotone in $t$: it moves from
its initial rare moment toward a fixed equilibrium. Under S, stopping at zero
dominates any increasing trajectory. Under U, the attainable $r/2$ dominates any
increasing trajectory, whose initial value is $(g(a)+r)/2$. Every potentially
improving trajectory therefore takes $t=\tau$.

Rates in $(1,2)$ are dominated by $2-a\in(0,1)$ at the same rescaled time. The
decay $d(a)$ is unchanged, while each of

$$
  g(a),\qquad \frac{\nu a}{2-a},\qquad
  \frac{a\{\nu+g(a)\}}{2-a}
$$

is nondecreasing in $a$. Rates zero and two are covered by their boundary
values. The remaining lower bounds are therefore the displayed minima over
$[0,1]$.

For the upper bound, hold any positive minimizing rate fixed and use the full
cap $M_q$. The corresponding positive-time limit attains its displayed value.
Use literal initialization when the S minimizer is zero, and the vanishing-rate
recovery sequence when the U minimizer is zero. This proves both oracle limits.

## Consequences for signal allocation

The unscaled limiting oracle depends on $r,\nu,\tau$, but not on $s$.
Standardization depends on the signal through $v=s/4+r$. This difference is
specific to the scarce-occurrence limit; common signal strength still affects
the finite-prevalence unscaled oracle.

There is an explicit threshold for whether U learns the rare effect in the
limit:

$$
  \min_\alpha F_U(\alpha)=r/2
    \quad\Longleftrightarrow\quad r\tau\leq\nu/16.
$$

Indeed, $g(\alpha)\geq\nu\alpha/8$ and $1-z(\alpha)\leq2\tau\alpha$ imply

$$
  F_U(\alpha)-r/2
    \geq\alpha(\nu/16-r\tau).
$$

Conversely, $F_U'(0)=\nu/16-r\tau$, so a negative derivative gives a strict
improvement. Under S, $F_S'(0)=-\tau(s/4+r)$, and some positive rate improves on
initialization whenever the initial signal is nonzero.

For fixed $r>0$, $\nu>0$, and $\tau>0$, there is a unique common squared signal
$s_*(r,\nu,\tau)>0$ at which the two limiting oracles agree. Below it, S has
smaller risk; above it, U has smaller risk. To prove this, at $s=0$:

- If a minimizing U rate is positive, its S risk is strictly smaller because
  $g>0$ and the U rare-noise equilibrium is larger.
- If a minimizing U rate is zero, its risk is $r/2$, while a small positive S
  rate strictly improves on that value.

For $s_2>s_1$, minimizing affine functions of $s$ gives

$$
  \frac{e^{-\tau}}8(s_2-s_1)
  \leq L_S(s_2)-L_S(s_1)
  \leq\frac18(s_2-s_1),
$$

where $L_S(s)=\min_\alpha F_S(\alpha;s,r,\nu,\tau)$. Thus $L_S$ is continuous,
strictly increasing, and unbounded, while $L_U$ is constant in $s$. This proves
existence and uniqueness of the crossing without asserting a closed form.

The degenerate cases differ. If $r=0$, U has limiting risk zero. If $\nu=0$, the
minima are $re^{-\tau}/2$ for U and $(s/4+r)e^{-\tau}/2$ for S; S has no strict
advantage.

For an explicit variational expression for the crossing, put
$L_U=\min_\alpha F_U(\alpha;r,\nu,\tau)$ and $p(\alpha)=\nu\alpha/(2-\alpha)$.
Then

$$
  s_*=4\max_{0\leq\alpha\leq1}
    \left[\{2L_U-p(\alpha)\}e^{\tau d(\alpha)}
           +p(\alpha)-r\right].
$$

For each rate, the expression inside the maximum is the value of $s/4$ at which
that S trajectory equals $L_U$. The S oracle is smaller whenever at least one of
those trajectories is smaller, giving the maximum over rates.

With unit noise, numerical minimization gives the following limiting risks:

  | $\tau$ | $s$  | $r$  | U        | S        |
  | -----: | ---: | ---: | -------: | -------: |
  |      1 | 0.01 |    1 | 0.351676 | 0.322357 |
  |      2 | 0.01 |    1 | 0.256267 | 0.229363 |
  |      4 | 0.01 |    1 | 0.162930 | 0.141939 |
  |      1 |    1 | 0.01 | 0.005000 | 0.107443 |
  |      2 |    1 | 0.01 | 0.005000 | 0.091266 |
  |      4 |    1 | 0.01 | 0.005000 | 0.070019 |

For $r=\nu=1$, the numerical crossing values of $s$ are approximately 0.481885,
0.784648, and 1.448329 at $\tau=1,2,4$, respectively. These values come from
one-dimensional numerical optimization, not certified interval bounds.

## Numerical checks and current limits

Run `devenv shell -- task check:oracle-limits`. The checker reconstructs moment
updates from individual observations, checks the scalar lower bound, compares
finite-prevalence risks with the limiting formulas, and exercises
vanishing-rate, short-stop, large-rate, and zero-noise cases. A finite rate grid
with every integer stop provides a separate diagnostic of the optimized limit.
That search does not certify a continuous finite-prevalence optimum.

The [recorded output](../results/oracle-limits/checks.json) includes 30 exact
rational checks of the large-rate bounds, 486 fixed-rate comparisons, ten
boundary-sequence comparisons, and 51 checks of the signal consequences. Across
the fixed-rate cases, the largest discrepancy decreases from $5.35\times10^{-3}$
at $q=10^{-3}$ to $5.37\times10^{-7}$ at $q=10^{-7}$. For four signal pairs at
$\tau=2$, the largest finite-grid risk discrepancy from the limiting oracle
decreases from 0.01234 at $q=0.02$ to 0.0001311 at $q=0.0002$. The largest
change on rate-grid refinement is $7.76\times10^{-6}$.

The proof gives limiting oracle values for all fixed signal strengths and finite
positive rescaled budgets. It does not give a uniform finite-prevalence error
bound for the optimized risks, rates of convergence near a boundary minimizer,
or a result for adaptive stopping, averaging, schedules, fitted intercepts, or
estimated preprocessing. The manuscript's existing theorem remains the
quantitative finite-prevalence guarantee.
