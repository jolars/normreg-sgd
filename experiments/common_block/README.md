# One rare feature and a common-feature block

This exploratory extension replaces the manuscript's single common feature with
an arbitrary fixed number of independent balanced binary features. The exact
aggregate moment recurrence remains two-dimensional. The calculations below
extend the model and identify a dimension effect; they do not establish an
extension of the manuscript's uniform oracle-separation theorem.

## Model and exact reduction

Let $I_1,\ldots,I_m$ be independent Bernoulli variables with prevalence $1/2$,
and let $J$ be an independent Bernoulli variable with prevalence $q$. Center all
features at their population means and write

$$
  y=\sum_{j=1}^m\beta_j^*(I_j-1/2)+\beta_R^*(J-q)+\varepsilon,
  \qquad
  \mathbb E[\varepsilon\mid x]=0,
  \quad \mathbb E[\varepsilon^2\mid x]=\sigma^2.
$$

Use fresh observations, zero initialization, a fixed zero intercept, and
constant-rate SGD. Let $b=q(1-q)$, $s=\sum_j(\beta_j^*)^2$, and
$r=(\beta_R^*)^2$. Hold $s$ and $r$ fixed when changing $m$. Spreading common
signal over several coordinates or concentrating it in one coordinate gives the
same risk in this model. Adding common features with zero coefficients also
changes the dynamics, because their fitted coefficients acquire noise.

Parameterize the update by its rare-coordinate step $\alpha$. The common step is
$\alpha$ under unscaled training and $4b\alpha$ under standardization. Put
$u=\alpha/4$ or $u=b\alpha$, respectively, and define

$$
  C_k=\frac14\sum_{j=1}^m\mathbb E[(\widehat\beta_{j,k}-\beta_j^*)^2],
  \qquad H_k=\mathbb E[(\widehat\beta_{R,k}-\beta_R^*)^2].
$$

The exact recurrence is

$$
  \begin{aligned}
  C_{k+1}&=(1-2u+mu^2)C_k+mu^2bH_k+mu^2\sigma^2,\\
  H_{k+1}&=\{1-b\alpha(2-\alpha+3b\alpha)\}H_k
            +b\alpha^2(C_k+\sigma^2),\\
  C_0&=s/4,\qquad H_0=r.
  \end{aligned}
$$

The excess half squared loss conditional on rare presence is

$$
  R_{R,k}=\frac12\{C_k+(1-q)^2H_k\}.
$$

To derive the common equation, expand each squared coefficient error after one
SGD update. The common feature has second moment $1/4$ and fourth moment $1/16$.
Independence and centering make every term involving two different coefficient
errors vanish from this diagonal update. Summing over common coordinates gives
$m-1$ off-coordinate contributions in addition to each coordinate's own squared
multiplier. This produces $(1-u)^2+(m-1)u^2=1-2u+mu^2$.

The rare equation uses $\mathbb E[(J-q)^4]=b(1-3b)$ and sums the common diagonal
moments. Cross-error moments can be nonzero, but do not enter these two
equations. The conditional test second-moment matrix is diagonal as well.

## An immediate dimension comparison

For either scaling, fixed $q,\alpha,k,s,r,\sigma^2$, and integers $m_2\geq m_1$,
the risk with $m_2$ common features is at least the risk with $m_1$.

Indeed, all recurrence coefficients are nonnegative for every $\alpha\geq0$. The
common diagonal coefficient is $(1-u)^2+(m-1)u^2$, and the rare diagonal
coefficient is $(1-b\alpha)^2+b\alpha^2(1-4b)$. At a fixed $\alpha$, increasing
$m$ increases only coefficients and forcing terms in the common equation. Both
systems start at the same $(s/4,r)$, so induction proves the comparison.

Taking the infimum over the same set of all nonnegative constant rates and
integer stops preserves this inequality. Thus each method's unrestricted oracle
risk is nondecreasing in common-feature dimension at fixed total signal
strength. This does not determine the difference between the two methods' oracle
risks. The numerical difference need not be monotone in dimension.

## Fixed-rate small-prevalence limits

Fix $m$ and take $q\to0$ with $kb\to t>0$. These limits fix $\alpha$ before
taking $q\to0$; they do not interchange a limit and an oracle infimum.

For standardization and $0<\alpha<2$, the limiting equations are

$$
  \dot C=-2\alpha C,\qquad
  \dot H=-\alpha(2-\alpha)H+\alpha^2(C+\sigma^2).
$$

Writing $W=C+H$, $W_0=s/4+r$, and $z=\exp\{-\alpha(2-\alpha)t\}$ gives

$$
  R_S^{\mathrm{lim}}(t,\alpha)
  =\frac12\left\{(s/4+r)z+\frac{\alpha\sigma^2}{2-\alpha}(1-z)\right\}.
$$

The leading limit is independent of fixed $m$ at fixed $s$. This follows by
expanding the exact transition as an Euler step of size $b$: the additional
common-block terms have order $mb^2$ per update. This argument does not cover
$m$ growing inversely with prevalence.

For unscaled training, fix $0<\alpha<\min(2,8/m)$. The common moment relaxes on
the ordinary iteration scale to

$$
  c_m(\alpha)=\frac{m\alpha\sigma^2}{8-m\alpha}.
$$

Its multiplier $1-\alpha/2+m\alpha^2/16$ lies below one. The rare-feedback
forcing in that equation is of order $b$. The initial common transient makes a
vanishing contribution to the rare equation on the rescaled time horizon.
Consequently the limiting rare moment obeys

$$
  \dot H=-\alpha(2-\alpha)H+\alpha^2\{\sigma^2+c_m(\alpha)\},
  \qquad H(0)=r,
$$

and the resulting fixed-rate expression is

$$
  R_U^{\mathrm{lim}}(t,\alpha)
  =\frac12\left\{c_m(\alpha)+rz+
  \frac{\alpha\{\sigma^2+c_m(\alpha)\}}{2-\alpha}(1-z)\right\}.
$$

This exposes the dimension-dependent cost of learning the rare signal: the
unscaled common block contributes a noise floor that grows with $m$ at fixed
$\alpha$. The expression describes positive rescaled time, after the fast common
transient; it does not give the original risk at stop zero.

Rates shrinking with $q$ require separate treatment. For example, at fixed $m$
and positive rescaled budget, an unscaled step proportional to $\sqrt b$ learns
the common signal with vanishing common noise while leaving the rare signal
asymptotically unlearned. Its limiting rare risk is $r/2$. A proof about oracle
limits must also control such rate sequences, short stopping sequences, and
rates near stability boundaries. The fixed-rate formulas alone do not settle
that problem.

## Numerical study

The deterministic study uses $m\in\{1,2,4,8,16,32,64\}$,
$q\in\{0.02,0.005,10^{-4}\}$, unit noise variance, and the manuscript's two
signal allocations $(s,r)=(0.01,1)$ and $(1,0.01)$. Observation caps approximate
$Mb=1,2,4$ and stay inside $1\leq Mb\leq4$.

For each model, each scaling searches 1,025 positive rates geometrically spaced
between $10^{-7}$ and $0.999$ times its mean-square stability limit, together
with zero. Every integer stop through the cap is searched. The coarse rate grid
retains alternate positive rates and zero. The searches minimize risk averaged
over training randomness, with deterministic rate and stop choices.

For reproducibility, the stability limit is the first positive root of
$\det(I-T)=0$, where $T$ is the homogeneous two-moment transition. With
$u=c\alpha$, define

$$
  L=2(1-3b+mc),\qquad K=mc(1-4b),\qquad
  \alpha_{\mathrm{stab}}=\frac{8}{L+\sqrt{L^2-16K}}.
$$

Here $c=1/4$ for U and $c=b$ for S. The calculation searches rates below this
limit. It does not compare all nonnegative rates, including unstable rates with
short finite stops, as the existing two-feature theorem does.

Both orderings persist in all 126 paired comparisons: SD wins for the dominant
rare signal, and U wins for the dominant common signal. There are no positive
stop selections at either edge of the positive rate grid. Refinement changes
individual selected risks by at most $3.50\times10^{-5}$ and changes no signs.
These observations support an extension, but do not certify continuous optima.

At $q=10^{-4}$ and $M=20{,}002$, the selected risks are:

  | Common features | Rare signal: U | Rare signal: SD | Common signal: U | Common signal: SD |
  | --------------: | -------------: | --------------: | ---------------: | ----------------: |
  |               1 |       0.256210 |        0.229307 |         0.005048 |          0.091264 |
  |               4 |       0.327134 |        0.229333 |         0.005221 |          0.091272 |
  |              16 |       0.467729 |        0.229434 |         0.005800 |          0.091303 |
  |              64 |       0.500344 |        0.229838 |         0.007699 |          0.091430 |

At the larger prevalence $q=0.02$ and $M=102$, both methods incur more visible
dimension costs. Increasing $m$ from one to 64 changes the common-signal U/SD
risks from $0.015782/0.090488$ to $0.098941/0.109008$. The unscaled advantage
narrows substantially. The rare-signal SD advantage reaches its largest tested
value at an intermediate dimension in some slices.

## Verification and reproduction

Run from the repository root inside `devenv shell`:

```sh
task check:common-block
task experiment:common-block
task check:common-block -- --saved
task figure:common-block
```

`check:common-block` verifies 60 one-step reductions with exact rational
arithmetic, enumerating individual observations in dimensions two through six.
The checks include nonzero cross-error moments and rates above the stability
range. Further checks use full second-moment tensor powers, compare concentrated
and spread common signals, verify a small rate-and-stop search independently,
check stability on both sides of each calculated threshold, and check
convergence to the fixed-rate formulas. The saved-result check replays all 252
selected risks with matrix powers instead of the search's sequential updates.

`results/common-block/search.npz` retains the risk minimum and earliest
attaining stop for every rate and cap. `settings.json` records all grids and the
numerical environment; this exact-moment experiment has no random sampling seed.
`summary.json` contains the selected risks, rates, stops, and refinement
diagnostics. Summarizing and plotting read saved results without rerunning the
search. The plots are exported to `figures/common-block/budget-slice` and
`figures/common-block/dimension-gaps` as PDF, SVG, and PNG. The main paper uses
the middle-budget slice at two prevalences; the supplement shows all prevalences
and budgets. Both plots are part of the manuscript build and read the saved
summary without running the experiment.

## Next theoretical target

The useful next result would compare the two tuned risks with explicit
dependence on common-feature dimension and signal allocation. The positive
recurrence and dimension monotonicity give tools for this comparison, but do not
by themselves establish either ordering. Two plausible routes are extending the
finite-prevalence lower and upper bounds to include $m$, or proving convergence
of the optimized risks after handling all relevant rate and stopping sequences.
The current fixed-$m$ limits also suggest examining when increasing $m$ with
$q^{-1}$ changes the limiting behavior, as a separate regime.
