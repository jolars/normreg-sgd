# Comparing the limiting oracles

The [oracle-limit derivation](oracle-limits.md) reduces unrestricted
constant-rate and deterministic-stop tuning to two scalar minimizations. This
note makes those minimizations usable and explains how signal allocation, noise,
and budget affect the preferred scaling. It concerns final iterates with
population preprocessing, fresh observations, zero initialization, and a fixed
zero intercept. The checked results and proofs are now integrated into the
[manuscript](../paper/oracle-proofs.tex).

Write $s = (\beta_C^*)^2$, $r = (\beta_R^*)^2$, $\nu = \sigma^2$, and
$v = s/4 + r$. First take $q \to 0$ with $Mq(1 - q) \to \tau \in (0,\infty)$ and
fixed finite $s,r,\nu \geq 0$. Let $L_S$ and $L_U$ denote the resulting oracle
risks. Statements below about small or large $\tau$, or changing noise, concern
these limiting functions. They do not interchange this limit with a joint limit
in budget or noise.

## A scalar decision rule

For $a \in[0,1]$, set

$$
  d = a(2 - a),\qquad z = e^{-\tau d},\qquad p
    = \frac{a}{2 - a},\qquad h = \frac{a}{8 - a},\qquad P = p(1 + h).
$$

When $\nu > 0$, define the dimensionless signal strengths $x = v/\nu$ and
$\rho = r/\nu$. The two problems are

$$
  J_S(x,\tau) = \min_{0 \leq a \leq 1}\{xz + p(1 - z)\},\qquad J_U(\rho,\tau)
              = \min_{0 \leq a \leq 1}\{\rho z + h + P(1 - z)\},
$$

with $L_S = \nu J_S/2$ and $L_U = \nu J_U/2$. Thus S is preferred exactly when
$J_S(x,\tau) < J_U(\rho,\tau)$, with equality meaning a tie. Only the two
signal-to-noise ratios and the rescaled observation cap enter this comparison.
Multiplying $s,r,\nu$ by the same positive number multiplies both risks by that
number and leaves the optimal rates and preferred scaling unchanged.

The endpoint $a = 0$ under U means using prevalence-dependent rates satisfying
$q \ll \alpha_q \ll 1$ at the full cap. Such rates learn the common signal and
leave the rare effect at initialization. They give $L_U = r/2$. Literal
zero-rate training instead retains the common signal error as well.

### Unique optimal rates

There is no need to search a rate grid. For $0 < a < 1$, define

$$
  Q_S(a) = p + \frac{p'(e^{\tau d} - 1)}{\tau d'},\qquad Q_U(a)
         = P + \frac{h'e^{\tau d} + P'(e^{\tau d} - 1)}{\tau d'}, \qquad d'
         = 2(1 - a).
$$

Both functions are strictly increasing. Indeed, $p,h,P$ have positive first and
second derivatives, $e^{\tau d}$ increases, and $1/d'$ increases on this
interval. Every summand in each displayed expression is nonnegative and
increasing, and at least one is strictly increasing. Their endpoint limits are

$$
  Q_S(0) = 0,\qquad Q_U(0) = \frac{1}{16\tau},\qquad Q_S(1-) = Q_U(1-) = \infty.
$$

Differentiating the objectives gives, respectively, $\tau d'z\{Q_S(a) - x\}$ and
$\tau d'z\{Q_U(a) - \rho\}$. Consequently:

- If $v > 0$ and $\nu > 0$, S has one minimizer in $(0,1)$, determined by
  $Q_S(a) = v/\nu$.
- If $\nu > 0$ and $r\tau > \nu/16$, U has one minimizer in $(0,1)$, determined
  by $Q_U(a) = r/\nu$.
- If $r\tau \leq \nu/16$ and $\nu > 0$, U has the unique minimizer $a = 0$. This
  includes equality, since $Q_U(a) > Q_U(0)$ for every $a > 0$.
- If $\nu = 0$, choosing $a = 1$ gives $L_S = ve^{-\tau}/2$ and
  $L_U = re^{-\tau}/2$. A zero initial signal makes the corresponding objective
  identically zero.

The [solver](../experiments/common/limiting_oracle.py) brackets the unique root
on $[0,1]$. It evaluates the derivative after multiplication by $z$, avoiding
the growing exponentials in $Q_S$ and $Q_U$. For example, run this inside
`devenv shell`:

```python
from experiments.common.limiting_oracle import oracle_minimum

for standardized in (False, True):
    risk, rate = oracle_minimum(standardized, tau=2, s=0.1, r=1, noise=1)
    print("S" if standardized else "U", risk, rate)
```

This gives risks approximately $0.256267$ for U and $0.232599$ for S. The root
solver is a floating-point implementation of the proved scalar characterization,
not an interval certificate for its numerical answers.

## Signal allocation

For fixed $r,\nu,\tau > 0$, increasing $s$ increases $L_S$ strictly and leaves
$L_U$ unchanged. The [crossing
argument](oracle-limits.md#consequences-for-signal-allocation) shows that
exactly one $s_* > 0$ gives equality. Its dimensionless form is

$$
  s_*(r,\nu,\tau)
  = 4\nu\max_{0 \leq a \leq 1} \left[ \{J_U(r/\nu,\tau) - p\}e^{\tau d} + p - r/\nu \right].
$$

S has smaller risk for $s < s_*$, and U for $s > s_*$. This is a usable
variational boundary even without a closed-form maximizer. Alternatively, find
the zero of $L_S(s) - L_U$ by scalar bisection. The bounds

$$
  0<s_*\leq4r(e^\tau-1),\qquad
  \frac{e^{-\tau}}8(s_2-s_1)
  \leq L_S(s_2)-L_S(s_1)\leq\frac18(s_2-s_1)
$$

give a bracket and a sensitivity bound. The upper bracket follows from
$L_S \geq (s/4 + r)e^{-\tau}/2$ and $L_U \leq r/2$. Large $\tau$ can make this
inverse problem poorly conditioned, despite uniqueness.

A second interpretation fixes $\nu > 0$ and holds the total initial
rare-subgroup signal error $v > 0$ fixed. Write $r = \theta v$ and
$s = 4(1 - \theta)v$ for $0 \leq \theta \leq 1$. Here allocation refers to the
risk contributions $s/4$ and $r$, rather than the unweighted sum $s + r$. The S
oracle is constant along this allocation path. The U oracle increases strictly
with $r$, since

$$
  \frac{e^{-\tau}}2(r_2-r_1)
  \leq L_U(r_2)-L_U(r_1)\leq\frac12(r_2-r_1).
$$

At $\theta = 0$, U has zero limiting risk and beats S. At $\theta = 1$, the
common signal is zero and S beats U when $\nu > 0$. Thus there is exactly one
$\theta_* \in (0,1)$: U wins below it, and S above it. Setting $x = v/\nu$, an
equivalent variational formula is

$$
  \theta_*
  = \frac1x\max_{0 \leq a \leq 1} \left[ \{J_S(x,\tau) - h - P(1 - z)\}e^{\tau d} \right].
$$

For each rate, the expression in brackets is the rare signal-to-noise ratio that
makes that U trajectory equal $J_S$. U beats S if at least one trajectory is
below $J_S$, which explains the maximum. These allocation results do not assert
a transition along every other way of holding signal strength fixed.

## Noise can produce two reversals

At fixed signals and budget, both oracle risks are nondecreasing, concave
functions of $\nu$: each is the minimum of affine functions with nonnegative
noise coefficients. Their difference need not be monotone.

For $s > 0$, zero noise favors U, with gap $L_S - L_U = se^{-\tau}/8 > 0$. By
continuity, sufficiently small positive noise also favors U. At the other
extreme, U stops learning the rare effect once $\nu \geq 16r\tau$, giving
$L_U = r/2$. As $\nu \to \infty$, the S minimizer must tend to zero, since every
rate bounded away from zero incurs unbounded noise cost. Its signal term tends
to $v/2$; initialization supplies the matching upper bound. Hence

$$
  L_S \longrightarrow v/2,\qquad L_U
      \longrightarrow r/2, \qquad L_S - L_U \longrightarrow s/8.
$$

U therefore also wins for sufficiently large noise when $s > 0$. S can win
between these two extremes. For $s = 0.1$, $r = 1$, and $\tau = 2$, numerical
roots give:

  | Noise variance $\nu$ | U risk   | S risk   | Preferred scaling |
  | -------------------: | -------: | -------: | ----------------- |
  |                    0 | 0.067668 | 0.069359 | U                 |
  |                  0.1 | 0.109877 | 0.103572 | S                 |
  |                    1 | 0.256267 | 0.232599 | S                 |
  |                  100 | 0.500000 | 0.502306 | U                 |

Continuity and these strict signs imply at least two crossings for this example.
No claim that there are exactly two, or that every signal pair exhibits them, is
needed. When $s = 0$, $r > 0$, and $\nu > 0$, S instead wins for every finite
positive budget. When $r = 0$, U has zero limiting risk and cannot lose.

## Budget changes the comparison

Each oracle risk is nonincreasing in $\tau$. One can retain the earlier stop
when the cap grows; equivalently, the limiting trajectory reduction in the
oracle-limit proof permits the old risk at every larger cap. A larger budget
also lowers U's rare-learning threshold $\nu/(16\tau)$.

For fixed $v,\nu > 0$ and $\tau \downarrow 0$, expansion uniformly in
$a \in[0,1]$ gives

$$
  L_S = \frac v2 - \frac{\tau v^2}{2(v + \nu)} + O(\tau^2),\qquad a_S
      \longrightarrow \frac{v}{v + \nu}.
$$

Indeed, the first-order improvement in twice the S risk is
$\tau\{2av - a^2(v + \nu)\}$, a strictly concave quadratic. For sufficiently
small $\tau$, U has risk $r/2$. Thus small positive rescaled budgets favor U
when $s > 0$. The common coordinate has already been learned in this ordered
limit, even as the rescaled number of rare observations tends to zero.

For fixed $r,\nu > 0$ and finite $s \geq 0$, the large-budget risks satisfy

$$
  \begin{aligned}
    L_S & = \frac{\nu}{8\tau}
    \left[ 1 + \log\!\left( \frac{4\tau v}{\nu} \right) \right]
    +o(\tau^{-1}), \\
    L_U & = \frac{5\nu}{32\tau}
    \left[ 1 + \log\!\left( \frac{16\tau r}{5\nu} \right) \right]
    +o(\tau^{-1}).
  \end{aligned}
$$

To justify the expansion, the candidate $a = (\log\tau)/(2\tau)$ gives risk
$O((\log\tau)/\tau)$. At any minimizer, the positive signal term then forces
$z = O((\log\tau)/\tau)$. Under S, $\nu p(1 - z)$ bounds $a$ by the same order;
under U, the common noise term $\nu h$ does so directly. Therefore
$a = O((\log\tau)/\tau)$ and $\tau a^2 \to 0$. In this region, twice the risks
equal, respectively,

$$
  v e^{-2\tau a} + \frac{\nu a}{2} + o(\tau^{-1}),\qquad r e^{-2\tau a}
  + \frac{5\nu a}{8} + o(\tau^{-1}).
$$

The remainder is bounded by $O((\log\tau)^3/\tau^2)$ both at the true minimizers
and at the minimizers of these approximations. Minimizing $B e^{-2\tau a} + ca$
gives $a = \log(2\tau B/c)/(2\tau)$ for large enough $\tau$, proving the
formulas. The U noise coefficient includes $\nu a/8$ from the common coordinate
and $\nu a/2$ from the rare coordinate. S retains only the latter at leading
order. Consequently,

$$
  \frac{L_S}{L_U} \longrightarrow \frac45.
$$

S wins for all sufficiently large rescaled budgets when rare signal and noise
are positive, however large the fixed common signal is. Together with the
small-budget result, this gives at least one budget crossing when $s > 0$. It
does not prove that the budget crossing is unique. For example, at
$s = r = \nu = 1$, U wins at $\tau = 1$ (risks $0.351676$ and $0.383051$),
whereas S wins at $\tau = 10$ (risks $0.078421$ and $0.070862$). Convergence can
be slow: for $s = 10$, $r = 0.1$, and $\nu = 2$, U still wins at $\tau = 10^5$,
while S wins at $\tau = 10^7$.

The positive-noise and positive-rare-signal assumptions matter. With $\nu = 0$,
U is always weakly better; with $r = 0$, U always has zero limiting risk. If
$s = r = 0$, both oracles have zero risk for every noise level.

## Reproducible checks

Run `devenv shell -- task check:oracle-variational`. The checker compares the
stationary-root solver with the separate grid-and-refinement implementation in
`checks/oracle_limits.py` and with objective derivatives obtained by
complex-step differentiation. It checks the two variational boundaries against
roots of the optimized risk difference, verifies signs on both sides, and
exercises noise, budget, scale invariance, and degenerate cases. It also checks
the small- and large-budget expansions. The [saved
output](../results/oracle-limits/variational-checks.json) records settings,
errors, transition examples, and the tables above.

Regenerate the record inside `devenv shell` with:

```sh
python -m checks.oracle_variational > results/oracle-limits/variational-checks.json
```

These are deterministic diagnostics of the limiting formulas. They neither
certify a continuous finite-prevalence oracle nor replace independent
mathematical review. The [finite-prevalence comparison](oracle-finite.md) tests
these predictions against exact moments over nested rate and stop grids. It
recovers the predicted signs away from limiting ties at small prevalence and
records a high-noise disagreement at larger prevalence. The existing theorem
remains the quantitative finite-prevalence guarantee.
