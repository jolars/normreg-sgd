# Joint normalization and training interactions

## Question and status

How much of a normalization change can learning rate and stopping compensate
for, and how does batch size change the resulting coefficient error and
prediction risk? This is the first controlled comparison under the revised
[research plan](research-plan.md). It carries the original `normreg` paper's
view of normalization as a modeling choice into finite-time stochastic learning.

The grid below was specified before running this experiment. It is a separate
fresh-sample study from the [frozen fixed-data pilot](rare-subgroup-pilot.md).
The moment identities used here are already in the manuscript. The analytical
deductions below have local proofs and computational checks; independent proof
review is pending because the Coterie MCP server was unavailable during this
work. These deductions are not yet independently accepted research results.
Johan owns the separate literature and novelty assessment.

The [first results report](joint-interactions-results.md) records the numerical
findings, uncertainty, and figures separately from this specification. It also
labels the local sensitivity check added after inspecting the initial grid.

## Declared comparison

- Data: common indicator $I$ with $P(I=1)=1/2$ and rare indicator $J$ with
  $q=P(J=1)=0.02$. Use independent features and a nested design with $J\le I$.
  The four cell probabilities are $(1/2-q+r,q-r,1/2-r,r)$, with $r=q/2$ or
  $r=q$, respectively. These are actual feasible binary laws.
- **Response:** $x=(I-1/2,J-q)^\top$, $y=x^\top\beta^*+\varepsilon$,
  $\beta^*=(1,1)^\top$, and independent $\varepsilon\sim N(0,1)$. Initialization
  is zero. Population centering, feature scales, and the zero intercept are
  known and fixed. Each update receives new independent data.
- **Normalization:** $S_\delta=\operatorname{diag}(v_j^\delta)$,
  $v=(1/4,q(1-q))$, and $\delta\in\{0,1/4,1/2,1\}$. All coefficients are
  reported on the original scale. Damped scaling and estimated preprocessing are
  later comparisons.
- **Steps:** constant $\eta=\alpha/\lambda_{\max}(H)$, where
  $H=S_\delta^{-1}CS_\delta^{-1}$. Use 41 geometrically spaced values of
  $\alpha$ from $10^{-4}$ to $2.2$, plus $0.002$, $0.02$, and $0.2$. Save actual
  $\eta$, divisors, curvature, and a numerically computed second-moment
  stability boundary. This is curvature calibration, not tuning and not
  calibration to each batch's stability threshold.
- **Batches:** $B\in\{1,10,100\}$, giving $Bq\in\{0.02,0.2,2\}$.
- **Stopping:** the sorted unique union of zero, 61 rounded geometric counts
  from 1 to 10,000, and counts 5, 10, 20, 50, 100, 200, 500, 1,000, 2,000, and
  10,000. Retain each grid configuration at every declared count.
- **Budgets:** compare common update counts $k$ and common numbers of processed
  observations $M=kB$. In this fresh-sample study, the number of distinct
  observations also equals $M$. Figures use the overlap of the compared paths'
  domains. No fixed-dataset reuse or wall-clock equivalence is implied.
- **Outcomes:** coefficient mean, error second moment, design-induced
  covariance, and observation-noise covariance; aggregate and rare-presence
  excess risks $R=\operatorname{tr}(CV)/2$ and $R_R=\operatorname{tr}(C_RV)/2$,
  where $C_R=E[xx^\top\mid J=1]$. The conditional second moment includes its
  nonzero conditional mean. Test data are independent of training.

Here $V=E[(\beta_k-\beta^*)(\beta_k-\beta^*)^\top]$ is the original-scale error
second moment, including squared bias.

The full grid has 1,056 configurations before stopping counts. It includes
unstable configurations; finite-time existence of a moment differs from long-run
moment stability. Preserve invalid or nonfinite numerical endpoints with a
validity flag. Saturation or omission in a plot must be labeled.

The primary batch comparison uses the independent design, $\alpha=0.002$, no
scaling and standard-deviation scaling. Report $k=100$ and $M=1,000$, including
the risk decomposition. These choices precede inspecting results. The nested
design checks how the independent mechanism changes with dependence. Other
prevalences, signals, noise levels, and schedules remain extensions.

This addresses scientific questions 1–4 in the research plan: relative learning,
batch fluctuations, the training path, and the effect of dependence on risk.
Practical configuration selection, question 5, follows later. This grid contains
no selected optimum, validation-based stopping, or recommendation about
defaults.

## Exact calculations

Use the [finite-update identities](../paper/sections/discrete-dynamics.tex). For
$u_k=S(\beta_k-\beta^*)$, let $m_k=Eu_k$, $U_k=E[u_ku_k^\top]$, $R=I-\eta H$,
and $Q=H$ under the declared noise variance. Define

$$
  \mathcal V(U)=E[(zz^\top-H)U(zz^\top-H)],\qquad z=S^{-1}x,
$$

$$
  \mathcal T_B(U)=RUR+\frac{\eta^2}{B}\mathcal V(U).
$$

Then $m_k=R^km_0$ and

$$
  U_k=\mathcal T_B^k(m_0m_0^\top)
    +\frac{\eta^2}{B}\sum_{j=0}^{k-1}\mathcal T_B^j(Q).
$$

The first term minus $m_km_k^\top$ is the covariance of noiseless SGD caused by
sampling features. The sum is observation-noise covariance, including its
propagation through random updates. Conjugate by $S^{-1}$ for original-scale
moments. Bias plus these two covariance contributions gives the full risk.

The implementation uses powers of an augmented matrix to evaluate the noise sum,
avoiding inversion of $I-\mathcal T_B$ near a stability boundary. The spectral
radius of the homogeneous second-moment operator diagnoses stability; a
bracketed root gives its numerical threshold in learning rate.

## Analytical deductions awaiting independent review

### Global rescaling is an exact control

Replacing $S$ by $cS$ and every step $\eta_j$ by $c^2\eta_j$, for $c>0$,
preserves each original-scale update on a coupled observation stream:

$$
  (c^2\eta_j)(cS)^{-2}=\eta_jS^{-2}.
$$

With identical original-scale initialization, batches, and stopping, induction
gives identical paths and therefore identical moments and predictions. The claim
concerns fixed preprocessing and this SGD update; it does not cover adaptive
optimizers, clipping, or changes in the intercept update.

### Relative scaling cannot generally be absorbed into step and stopping

For independent features and constant steps, set $a_j=v_j^{1-2\delta}$. The
original-scale mean error is

$$
  E\beta_{k,j}-\beta_j^*=-(1-\eta a_j)^k\beta_j^*.
$$

Standard-deviation scaling gives $a_1=a_2=1$, so both coordinates have the same
relative mean deficit. With no scaling and unequal variances, any $k\ge1$ and
$0<\eta<1/\max(v_1,v_2)$ give unequal relative deficits: the two distinct
positive bases remain distinct after taking the same power. Thus no choice of
such a constant step and finite positive stopping count matches a nontrivial
standard-deviation-scaled mean in both nonzero signal coordinates. Batch size
does not change this mean formula.

This statement concerns the mean vector in the monotone regime. It does not rule
out matching a scalar risk, approximate agreement, oscillating steps, or
agreement at initialization or the converged population solution. General
learning-rate schedules require a separate comparison.

### Fixed-update batch ordering need not survive a fixed observation budget

Fix normalization, a constant step, initialization, and the data law. If
$B_s<B_l$, then for positive semidefinite $U$,

$$
  (\mathcal T_{B_s}-\mathcal T_{B_l})(U)
  =\eta^2(B_s^{-1}-B_l^{-1})\mathcal V(U)\succeq0.
$$

Both transition maps preserve positive semidefiniteness, and the additive noise
term has the same ordering. Starting with equal $U_0$, induction gives
$U_k^{(B_s)}-U_k^{(B_l)}\succeq0$: apply $\mathcal T_{B_s}$ to the preceding
difference, add the transition-map difference applied to $U_k^{(B_l)}$, and add
the ordered noise difference. The means agree, so covariance has the same
ordering. Conjugation by $S^{-1}$ preserves it, as does taking a trace against
either positive semidefinite test second moment. Larger batches therefore have
no greater risk at a common update count under these assumptions.

This finite-update argument does not require long-run stability. It does require
the same learning rate and fresh independent observations. At a common $M$, the
compared update counts become $M/B_s$ and $M/B_l$, so the induction does not
order those endpoints. Additional learning with smaller batches can outweigh
their greater variance. The declared numerical comparison tests that tradeoff
and how its size depends on normalization.

## Independent numerical checks and reproduction

The check script enumerates all short sampled gradient paths in scaled
coordinates, with two-point noise having the required conditional moments. It
compares their weighted moments with the matrix calculation, including noiseless
covariance, global rescaling, and conditional test risk. Separate checks cover
long horizons, batch ordering, stability thresholds, and overflow. This is an
independent computational route, not an independent human or agent proof review.

The direct Gaussian-noise simulation uses 32,768 repetitions and seed 20260915.
It pairs both normalization rules and batches 1 and 10 using the same ordered
observation stream, recording $M=100$ and $M=1,000$. It reports Monte Carlo
standard errors for means, second moments, risks, and paired risk differences.
The predeclared numerical check allows six standard errors plus $10^{-10}$; this
checks simulation agreement, not a scientific hypothesis. Exact finite support
calculations have floating-point error, but no Monte Carlo uncertainty.

Inside `devenv shell`:

```sh
make check-joint-interactions
make reproduce-joint-interactions
make check
```

The JSON records the specification, actual rates, source and lockfile hashes,
software versions, selected decompositions, and simulation uncertainty. The
compressed NumPy archive retains moments at all declared configurations and
stopping counts. Plots are exported as SVG and PDF. The frozen pilot remains a
separate artifact with its original risk convention.
