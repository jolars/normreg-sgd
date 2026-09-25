# Limiting oracle risks for the two-feature model

This working derivation extends the fixed-rate limits in [the common-feature
notes](../experiments/common_block/README.md) to the unrestricted rate-and-stop
oracles in the manuscript. It covers arbitrary fixed signal strengths and noise
variance in the two-feature model. It has numerical checks, but has not received
an independent mathematical review and is not yet part of the manuscript.

The rate-and-stop analysis below includes the common-coordinate transient when
the unscaled rate vanishes. Uniform lower bounds over all rates and stops,
paired with explicit recovery choices, justify the passage to oracle infima. The
proof also gives error orders on compact positive rescaled-budget intervals. The
signal-allocation consequences remain working claims for separate review.

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

**Oracle-limit theorem.** Under these assumptions,

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

More precisely, write $T_q=M_qb$ and let $L_A(T)$ denote the displayed minimum
with budget $T$. Fix $0<T_0<T_1<\infty$. For all sufficiently small $q$ and
every integer cap with $T_q\in[T_0,T_1]$, constants depending only on
$s,r,\nu,T_0,T_1$ give

$$
  |R_S^*(M_q)-L_S(T_q)|\leq C_S b,\qquad
  |R_U^*(M_q)-L_U(T_q)|\leq C_U b\log(1/b).
$$

These bounds apply to the unrestricted infima, including prevalence-dependent
rates and stops. Their constants are not optimized, and the bounds are not
numerical certificates at a specified prevalence.

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

At $k=0$, both scalings have risk $(s/4+wr)/2$, regardless of the rate. Literal
zero-rate training has this same risk at every stop. Its limit is $v/2$, where
$v=s/4+r$. All sequences below satisfy $0\leq k_q\leq M_q$. Each rate is
constant during a training run and varies only with prevalence.

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

In particular, under S every vanishing-rate sequence retains both initial
moments: $G_{k_q}\to s/4$ and $H_{k_q}\to r$. This holds uniformly over all
allowed stops. A bounded rate with $k_qb\to0$ also retains both initial moments.
Thus no additional limit arises from coupling a vanishing rate with an earlier
stop under S.

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

The same bound covers arbitrarily early stops, even when $b\alpha$ does not
vanish. More explicitly, positivity gives, for every integer $k\geq0$,

$$
  R_{R,k}\geq\frac w2\left[
    \lambda_b^k v+b\alpha^2\nu\sum_{j=0}^{k-1}\lambda_b^j
  \right],
$$

with an empty sum at initialization. The bound still applies when the noise or
either signal is zero.

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

### Vanishing rates: the common-coordinate transient

Suppose $\alpha_q\to0$. There is an explicit bound uniform over every allowed
stop, not just a lower bound on the rare moment. To derive it, take
$0\leq\alpha\leq1$, write $T=M_qb$, and set

$$
  A=(1-\alpha/4)^2,\qquad
  c=\frac{b\alpha}{8-\alpha},\qquad
  B=\frac{r+T\alpha^2\{s/4+g(\alpha)+\nu\}}
           {1-T\alpha^2c}.
$$

The denominator is positive for all sufficiently small $q$. Iterating the common
recurrence and using $D_b\leq1$ gives

$$
  \begin{aligned}
  G_j&\leq A^j s/4+g(\alpha)(1-A^j)+cH_{\max},\\
  H_{\max}&\leq r+T\alpha^2\{s/4+g(\alpha)+\nu+cH_{\max}\}.
  \end{aligned}
$$

Moving the feedback term to the left yields $H_{\max}\leq B$. Positivity,
$D_b\geq1-2b\alpha\geq0$, and Bernoulli's inequality then give the following
bounds for every $0\leq j\leq M_q$:

$$
  \begin{aligned}
  r-2rT\alpha&\leq H_j\leq B=r+O(\alpha^2),\\
  0&\leq G_j-A^j s/4\leq g(\alpha)+cB=O(\alpha).
  \end{aligned}
$$

The constants depend only on fixed $s,r,\nu$ and an upper bound for $M_qb$.
These estimates also include $\alpha=0$ and zero signal or noise.

Consequently, if $k_q\alpha_q\to\ell\in[0,\infty]$, then

$$
  G_{k_q}\longrightarrow\frac s4e^{-\ell/2},\qquad
  H_{k_q}\longrightarrow r,\qquad
  R_{R,k_q}\longrightarrow\frac s8e^{-\ell/2}+\frac r2,
$$

where $e^{-\infty}=0$. For finite $\ell$, use $\log A=-\alpha/2+O(\alpha^2)$ and
$k_q\alpha_q^2\to0$. For infinite $\ell$,
$0\leq A^{k_q}\leq e^{-k_q\alpha_q/2}\to0$ suffices; no additional restriction
on $k_q\alpha_q^2$ is needed.

At the full cap, this separates the vanishing rates into three regimes:

  | Rate regime                    | Limiting common moment | Limiting risk           |
  | ------------------------------ | ---------------------- | ----------------------- |
  | $\alpha_q/b\to0$               | $s/4$                  | $s/8+r/2$               |
  | $\alpha_q/b\to c\in(0,\infty)$ | $(s/4)e^{-c\tau/2}$    | $(s/8)e^{-c\tau/2}+r/2$ |
  | $b\ll\alpha_q\ll1$             | $0$                    | $r/2$                   |

Since $b/q\to1$, the last row is exactly $q\ll\alpha_q\ll1$. It learns the
common signal while leaving the rare moment at its initialization value. The
choice $\alpha_q=\sqrt b$ is one recovery sequence; $b\log(1/b)$ also works.
Under earlier stopping, the rate condition alone does not suffice: common
learning requires $k_q\alpha_q\to\infty$ when $s>0$. It can finish even with
$k_qb\to0$, for example at $\alpha_q=b^{1/2}$ and $k_q=\lfloor b^{-3/4}\rfloor$.
The same rate stopped at $\lfloor\ell/\alpha_q\rfloor$ instead retains the
fraction $e^{-\ell/2}$ of the initial common moment.

### Positive rates and short stops

Suppose $\alpha_q\to a\in(0,2]$ but $k_qb\to0$. The uniform moment bound from
the positive-time argument gives $H_{k_q}=r+O(k_qb)\to r$. Solving the common
recurrence more precisely gives

$$
  G_{k_q}=A_q^{k_q}s/4+g(\alpha_q)(1-A_q^{k_q})+O(b),
  \qquad A_q=(1-\alpha_q/4)^2.
$$

Along a subsequence, the integer stops either equal a fixed $K\geq0$ or tend to
infinity. Writing $A(a)=(1-a/4)^2$, the limiting risk is respectively

$$
  \frac12\left[r+A(a)^K s/4+\{1-A(a)^K\}g(a)\right],
  \qquad\frac12\{r+g(a)\}.
$$

Both are at least $r/2$. The first includes initialization at $K=0$; the second
includes stops that diverge more slowly than $1/b$. Substituting $t=0$ into the
positive-time U formula gives only the second value and would miss the
finite-stop transient.

### Large rates

For $\alpha\geq2/(1-3b)$, $D_b\geq1$, so $H_k\geq r$ at every stop and
$R_{R,k}\geq wr/2$. These rates cannot improve on the vanishing-rate recovery
sequence in the limit. All other rates have subsequences converging into
$[0,2]$, already covered above. No stability assumption is needed.

As with S, the exclusion is uniform over stops, including initialization and
stops chosen to offset a diverging rate. The explicit bound is

$$
  R_{R,k}\geq\frac w2\left[
    D_b^k r+b\alpha^2\nu\sum_{j=0}^{k-1}D_b^j
  \right].
$$

Together, these cases exhaust arbitrary prevalence-dependent choices. Split each
sequence according to whether its rate exceeds the relevant large-rate cutoff.
The bounds apply on that part. On the remaining part, the rates are bounded by
$2+O(b)$, and $k_qb$ is bounded by $M_qb\to\tau$. Extract limits of both. For U,
further extract a limit of $k_q\alpha_q$ in $[0,\infty]$ when the rate vanishes,
or of $k_q$ in $\{0,1,\ldots,\infty\}$ when the rate is positive and rescaled
time vanishes. This also covers oscillating choices without assuming that the
original sequence has a risk limit. No positivity assumption on $s$, $r$, or
$\nu$ was used.

## Completing the oracle argument

The following uniform estimates strengthen the preceding sequence analysis.
Throughout this section, $T=M_qb\in[T_0,T_1]$, $G_0=s/4$, and $v=G_0+r$. Every
$O(b)$ constant is independent of the rate, stop, and cap in its stated range.
Take $q$ small enough that $q\leq1/2$ and both large-rate cutoffs lie below
three. Then $1-w\leq4b$.

### Uniform approximation with the U transient retained

For U, let $0\leq\alpha\leq c_U(b):=2/(1-3b)$. Set

$$
  A=(1-\alpha/4)^2,\qquad h=\frac{\alpha}{8-\alpha},
  \qquad g=\nu h,\qquad c=bh,
$$

and define

$$
  B=\frac{r+T\alpha^2(G_0+g+\nu)}{1-T\alpha^2c}.
$$

Here $D_b\leq1$, $h\leq3/5$, and $T\alpha^2c\leq27T_1b/5$. Thus the denominator
is at least $1/2$ for sufficiently small $b$, uniformly even when $\alpha$ tends
to zero. The common recurrence and positivity give

$$
  H_{\max}\leq B\leq
    2\{r+9T_1(G_0+8\nu/5)\},
  \qquad
  0\leq G_j-A^jG_0-(1-A^j)g\leq cB.
$$

To justify the first inequality, bound the common moment by $G_0+g+cH_{\max}$,
sum the rare recurrence using $D_b\leq1$, and move $T\alpha^2cH_{\max}$ to the
left. This is the same absorption argument as for vanishing rates, now over the
entire retained rate interval.

Let $\widetilde H_0=r$ and
$\widetilde H_{j+1}=D_b\widetilde H_j+b\alpha^2(\nu+g)$. Since $0\leq D_b\leq1$,

$$
  \begin{aligned}
  |H_k-\widetilde H_k|
    &\leq b\alpha^2\sum_{j<k}|G_j-g|\\
    &\leq b\{16h|G_0-g|+T\alpha^2hB\}.
  \end{aligned}
$$

For $\alpha>0$, use $\alpha^2/(1-A)=16h$ in the geometric sum. At $\alpha=0$,
both sides are zero. The factor $\alpha^2$ cancels the apparently singular
common-coordinate relaxation time. No lower bound on $\alpha$ is needed.

Write $H^\circ_\alpha(t)$ for the solution of

$$
  \dot H^\circ=-d(\alpha)H^\circ+f,\qquad
  H^\circ(0)=r,\qquad f=\alpha^2(\nu+g).
$$

The affine scalar map for $\widetilde H$ differs from this flow over one step
$b$ by $O(b^2)$, uniformly for $\alpha\in[0,3]$. Telescoping gives
$\widetilde H_k=H^\circ_\alpha(kb)+O(b)$ for $k\leq M_q$. An explicit bound,
also used by the numerical checks, is

$$
  |\widetilde H_k-H^\circ_\alpha(kb)|
  \leq Tb\left[
    \left\{3\alpha^2+\tfrac12d(\alpha)^2e^{b|d(\alpha)|}\right\}\overline H
    +\tfrac12|d(\alpha)|e^{b|d(\alpha)|}f
  \right],
  \qquad
  \overline H=e^{T\max\{-d(\alpha),0\}}(r+Tf).
$$

Indeed, $H^\circ_\alpha(t)\leq\overline H$ for $t\leq T$. The exponential Taylor
remainder bounds the coefficient error in one step by
$b^2\{3\alpha^2+d(\alpha)^2e^{b|d(\alpha)|}/2\}$ and the forcing error by
$b^2|d(\alpha)|e^{b|d(\alpha)|}f/2$. Errors propagate with multiplier
$D_b\leq1$.

Consequently, uniformly over every retained U rate and every allowed stop,

$$
  R^U_{R,k}(\alpha)
    =\frac12\{A^kG_0+(1-A^k)g+H^\circ_\alpha(kb)\}+O(b).
$$

This approximation retains the finite-stop transient. Replacing its common term
by $g$ uniformly would be false, including at initialization.

### Reducing the limiting trajectories

Define $\Psi_S(a,t)=W_a(t)/2$ using the scalar S equation and
$\Psi_U(a,t)=\{g(a)+H^\circ_a(t)\}/2$. These formulas extend smoothly through
$a=0$ and $a=2$ by their differential equations. In particular,
$\Psi_S(0,t)=v/2$ and $\Psi_U(0,t)=r/2$.

For $0<a<2$, each trajectory is monotone in $t$. Under S, an increasing
trajectory stays above $v/2$. Under U, an increasing trajectory stays above
$(g(a)+r)/2\geq r/2$. Both baselines occur at $a=0$ in the corresponding
limiting minimization. A decreasing trajectory is smallest at $t=T$.

Rates in $(1,2)$ are dominated by $2-a\in(0,1)$ at the same time. The decay
$d(a)$ is unchanged, while each of

$$
  g(a),\qquad \frac{\nu a}{2-a},\qquad
  \frac{a\{\nu+g(a)\}}{2-a}
$$

is nondecreasing in $a$. At $a=2$, the trajectories are respectively
$(v+4\nu t)/2$ and $\{g(2)+r+4(\nu+g(2))t\}/2$, again above their baselines. It
follows that, for $A\in\{S,U\}$,

$$
  \Psi_A(a,t)\geq L_A(T)
  \qquad(0\leq a\leq2,\ 0\leq t\leq T).
$$

On $[0,3]\times[0,T_1]$, both flows and their derivatives with respect to $a$
are bounded. One can see this by differentiating their finite-dimensional matrix
exponentials. Thus a retained rate in $(2,c_A(b)]$ changes $\Psi_A$ by only
$O(b)$ when replaced by two, since $c_A(b)-2=O(b)$. This treats the small
interval above two without imposing a stability restriction.

### A lower bound over all rates and stops

For S, the uniform matrix approximation from the bounded-rate argument and
$1-w=O(b)$ give

$$
  R^S_{R,k}(\alpha)=\Psi_S(\alpha,kb)+O(b)
    \geq L_S(T)-O(b)
  \qquad(0\leq\alpha\leq c_S(b)).
$$

Above $c_S(b)=2/(1-3b+b^2)$, the exact scalar bound gives
$R^S_{R,k}\geq wv/2\geq L_S(T)-2bv$. Therefore the same lower bound holds for
**every** $\alpha\geq0$ and $0\leq k\leq M_q$.

For U, split the retained rates and stops using $J_b=2\log(1/b)$. If
$k\alpha\geq J_b$, then $A^k\leq e^{-k\alpha/2}\leq b$. The uniform
approximation above therefore gives
$R^U_{R,k}(\alpha)=\Psi_U(\alpha,kb)+O(b)\geq L_U(T)-O(b)$.

If $k\alpha<J_b$, take $b$ small enough that $1-2b\alpha\geq0$. Positivity and
Bernoulli's inequality give

$$
  H_k\geq D_b^kr\geq(1-2b\alpha)^kr
      \geq r(1-2bk\alpha),
$$

and hence

$$
  R^U_{R,k}(\alpha)\geq\frac r2-2br-rbJ_b
       \geq L_U(T)-2br-2rb\log(1/b).
$$

Finally, rates above $c_U(b)$ satisfy $R^U_{R,k}\geq wr/2\geq L_U(T)-2br$.
Combining these three cases gives a lower bound uniform over the entire oracle
domain:

$$
  \inf_{\alpha\geq0,\ 0\leq k\leq M_q}R^U_{R,k}(\alpha)
       \geq L_U(T)-O\{b\log(1/b)\}.
$$

These bounds allow the infima directly. They do not require finite-prevalence
minimizers to exist, or near-minimizing controls to converge.

### Recovery choices and convergence of the infima

Let $a_A(T)\in[0,1]$ minimize $F_A$ at budget $T$. For S, choose $\alpha=a_S(T)$
and $k=M_q$. Uniform convergence on the compact rate interval gives risk
$L_S(T)+O(b)$, including when $a_S(T)=0$.

For U, use the full cap and choose

$$
  \alpha_q=\max\left\{a_U(T),\frac{2b\log(1/b)}{T}\right\}.
$$

The second term is at most one for sufficiently small $b$, uniformly for
$T\geq T_0$. This choice ensures $M_q\alpha_q\geq J_b$, so the common transient
is $O(b)$. The bounded rate derivative of $F_U$ on $[0,1]\times[T_0,T_1]$ gives

$$
  R^U_{R,M_q}(\alpha_q)
    =F_U(\alpha_q;r,\nu,T)+O(b)
    \leq L_U(T)+O\{b\log(1/b)\}.
$$

This recovery works even when the minimizing rate is zero or approaches zero as
$T$ varies. It also covers $s=0$, $r=0$, $\nu=0$, and the all-zero case.
Together with the lower bounds, it proves the two error orders in the theorem.

For passage to a specified $\tau$, the limiting minima are Lipschitz in budget.
The defining formulas on $[0,1]$ give

$$
  |L_S(T)-L_S(\tau)|\leq\frac{v+\nu}{2}|T-\tau|,
  \qquad
  |L_U(T)-L_U(\tau)|\leq\frac{r+8\nu/7}{2}|T-\tau|.
$$

These follow by bounding the time derivatives uniformly in the rate and then
taking minima. Since $T_q\to\tau\in(0,\infty)$, both oracle limits follow. If
$M_q$ rounds $\tau/b$ to an integer, the budget discrepancy is $O(b)$.

### Restrictions and boundary cases

No signal dominance, positive signal, positive noise, or stability assumption is
needed. Signals and noise must be finite and fixed as $q\to0$. The error
constants can grow with these quantities and with the budget interval; the
theorem does not assert uniformity for diverging signals, noise, or budgets. The
upper bound for U uses a positive lower bound on $M_qb$ to remove the common
transient at a vanishing rate.

The condition $\tau>0$ cannot simply be dropped while keeping the same formula
for every cap sequence. For example, take $s=4$, $r=0$, and $\nu=1$. When
$M_q=1$, exact one-step minimization for U gives

$$
  R_U^*(1)=\frac12-\frac{1}{4(1+16bw)}\longrightarrow\frac14.
$$

In contrast, if $M_q\to\infty$ but $M_qb\to0$, the choice $\alpha_q=M_q^{-1/2}$
makes the U risk tend to zero for the same signals and noise. The vanishing-rate
bounds prove this since $M_q\alpha_q\to\infty$. Both cap sequences have
$\tau=0$. Thus that boundary requires additional information about the unscaled
number of observations. The case $M_qb\to\infty$ also requires a separate
argument.

The controls here are deterministic constant rates and deterministic stops for
final iterates. The proof does not cover rates or stops selected from realized
training paths, step schedules, averaging, fitted intercepts, or estimated
preprocessing.

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

Run `devenv shell -- task check:oracle-limits`. The checkers reconstruct moment
updates from individual observations, checks the scalar lower bound, compares
finite-prevalence risks with the limiting formulas, and exercises
vanishing-rate, short-stop, large-rate, and zero-noise cases. Joint
rate-and-stop sequences check the common and rare moments separately, so a
correct total risk cannot conceal an incorrect allocation between coordinates. A
finite rate grid with every integer stop provides a separate diagnostic of the
optimized limit. That search does not certify a continuous finite-prevalence
optimum.

The [recorded output](../results/oracle-limits/checks.json) includes 30 exact
rational checks of the large-rate bounds, 486 fixed-rate comparisons, ten
boundary-sequence comparisons, and 51 checks of the signal consequences. Across
the fixed-rate cases, the largest discrepancy decreases from $5.35\times10^{-3}$
at $q=10^{-3}$ to $5.37\times10^{-7}$ at $q=10^{-7}$. For four signal pairs at
$\tau=2$, the largest finite-grid risk discrepancy from the limiting oracle
decreases from 0.01234 at $q=0.02$ to 0.0001311 at $q=0.0002$. The largest
change on rate-grid refinement is $7.76\times10^{-6}$.

The expanded rate-and-stop checks add 768 moment comparisons: 32 sequences at
four prevalences for six signal-and-noise configurations, including zero common
signal, zero rare signal, zero noise, pure noise, and the all-zero case. The
largest error in either moment decreases from 0.9752 at $q=10^{-3}$ to
$9.43\times10^{-4}$ at $q=10^{-9}$. These sequences include rates approaching
two from both sides and recovery with vanishing rescaled time. Another 240
comparisons test the explicit vanishing-rate bounds before taking a limit, and
72 exact rational comparisons test the geometric large-rate bounds at
initialization and positive stops. The saved output records rates, stops, and
separate moment errors for each sequence.

The [uniform-control checker](../checks/oracle_infima.py) adds 168 exact
rational checks of the U tracking bounds, 3,570 moment comparisons across the
retained rate intervals and short-stop boundaries, 756 checks of the limiting
trajectory reduction, and 126 recovery comparisons. It tests pure common signal,
pure rare signal, and pure noise separately when checking moment approximations.
The recovery comparisons also include zero signal, zero noise, and the all-zero
case. The [recorded output](../results/oracle-limits/infimum-checks.json) gives
the settings and errors, including the two different limits at zero rescaled
budget. Across recovery comparisons, the largest risk discrepancy decreases from
$0.00437$ at $q=10^{-3}$ to $8.53\times10^{-7}$ at $q=10^{-7}$.

To regenerate the two records separately, run these commands inside
`devenv shell`:

```sh
python -m checks.oracle_limits > results/oracle-limits/checks.json
python -m checks.oracle_infima > results/oracle-limits/infimum-checks.json
```

The proof gives uniform error orders for the optimized risks on compact positive
rescaled-budget intervals, including boundary minimizers. It does not supply
optimized numerical constants or interval certificates at a specified
prevalence. Numerical checks exercise the estimates but do not prove coverage of
a continuous rate domain or replace independent mathematical review, which
remains outstanding. The manuscript's existing theorem remains the certified
quantitative finite-prevalence guarantee.
