# Focused robustness experiment for C1 and C2

September 16, 2026. Protocol version 1, specified after the [C1 and C2
proofs](normalization-risk-theorem.md) and the [target-risk
comparison](target-risk-comparison.md), before executing this extension.

## Status and questions

This note completes the experiment-specification item in [TODO.md](../TODO.md).
It declares the parameter sets, controls, resource accounting, uncertainty, and
reporting rules. Implementation, execution, and conclusions about robustness
belong to the following task. No new robustness results are asserted here.

The [fixed-data pilot](rare-subgroup-pilot.md) and [first fresh-sample
study](joint-interactions-results.md) remain separate records. Neither their
protocols nor their scripts, numerical artifacts, figures, or provenance will be
overwritten. This study uses a new output directory and retains its own
specification and results. The preservation baseline is repository commit
`a47cbfb`. Its design is informed by those studies and the theorems; it is not
an independent confirmatory test of how the anchors were discovered.

The questions are:

1. Where do C1's stopping reversal and C2's aggregate/subgroup disagreement
   persist when prevalence, feasible dependence, signal, and noise change?
2. Which signs change after adjusting the constant learning rate, or both the
   rate and stopping, over the declared sets at comparable budgets?
3. Do relative feature learning, bias, update variance, and observation noise
   explain the retained and disappearing comparisons? Does grid resolution
   change the answer on the declared refinement subset?

A disappearance, null contrast, unresolved numerical comparison, or advantage
for no scaling is a reportable outcome. This is a finite-grid, final-iterate
study under known preprocessing. It does not establish continuous optima,
uniform parameter bounds, novelty, or a practical tuning recommendation.

## Model and outcomes

Use the theorem's feasible binary family. Let $P(I=1)=1/2$, $P(J=1)=q$, and
$P(I=1,J=1)=q(1+\ell)/2$. In cell order $(0,0),(0,1),(1,0),(1,1)$, use

$$
  p=\left(\frac12-\frac{q(1-\ell)}2,\frac{q(1-\ell)}2,
  \frac12-\frac{q(1+\ell)}2,\frac{q(1+\ell)}2\right).
$$

Set $x=(I-1/2,J-q)^\top$ and $y=x^\top\beta^*+\varepsilon$. Direct simulations
use independent $\varepsilon\sim N(0,\sigma^2)$; zero variance means identically
zero noise. The exact moment calculation needs only conditional mean zero and
conditional variance $\sigma^2$. Batches contain fresh independent observations
and fresh noise. The independent test point follows the same law as training.
Population centering, scales, and the zero intercept are known and fixed. All
runs start with $\hat\beta_0=0$, and all reported coefficients use the original
feature scale. Use averaged squared loss with its factor $1/2$.

With $a=1/4$, $b=q(1-q)$, and $c=q\ell/2$, retain

$$
  C=\begin{pmatrix}a&c\\c&b\end{pmatrix},\qquad
  C_R=E[xx^\top\mid J=1]
  =\begin{pmatrix}a&\ell(1-q)/2\\\ell(1-q)/2&(1-q)^2\end{pmatrix}.
$$

Keep source centering in $C_R$, including its conditional mean. For every
endpoint, save coefficient means, bias $e_k$, full error second moment $V_k$,
and the decomposition

$$
  V_k=e_ke_k^\top+A_k+\sigma^2N_k.
$$

Here $A_k$ is covariance from sampling features in noiseless SGD, and
$\sigma^2N_k$ is propagated observation-noise covariance. Save both diagonal
MSEs and the signed cross moment $V_{CR,k}$. For $W=C,C_R$, report
$R_{W,k}=\operatorname{tr}(WV_k)/2$ and its three additive contributions. These
are excess prediction risks, excluding irreducible test noise. Always define
contrasts as standard-deviation scaling minus no scaling.

Also record $\beta^{*\top}C\beta^*$, $\sigma^2$, and $Bq$. Signals stay fixed on
their original scale as prevalence changes; this is not SNR matching. Do not
silently rescale signals to hold their marginal predictive variance fixed.

## Data-law slices and anchors

Use the union of the following two slices, deduplicated by
$(q,\ell,\beta_C^*,\beta_R^*,\sigma^2)$. A law retains all slice labels when it
belongs to both. Do not take the Cartesian product of the two slices.

  | Slice                     | Declared values                                                                                                                          | Purpose                                                                                                          |
  | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
  | Prevalence and dependence | $q\in\{0.002,0.005,0.01,0.02,0.05,0.1\}$; $\ell\in\{-1,-0.5,0,0.5,0.9,1\}$; $(\beta^*,\sigma^2)\in\{((1,1),3),((2,1),4)\}$               | Follow both anchors through rarity and feasible negative, independent, interior positive, and nested dependence. |
  | Signal and noise          | $q=0.02$; $\ell\in\{-1,0,1\}$; $\beta^*\in\{(0,0),(1,0),(0,1),(1,1),(1,-1),(2,1),(2,-1),(0.5,1),(1,0.5)\}$; $\sigma^2\in\{0,1,3,4,5,9\}$ | Isolate sign, relative magnitude, common-only, rare-only, pure-noise, and noiseless effects.                     |

There are 72 and 162 laws, with six shared laws: **228 distinct laws**. This
design does not assess every joint interaction between prevalence, signal, and
noise. Both slices include unfavorable and null cases without selecting them
from the new results. Zero cell probabilities at $\ell=\pm1$ are valid boundary
laws; $C$ remains positive definite at all declared prevalences.

Retain these fixed anchors before summarizing any adjusted configurations:

  | Anchor | Law and common step $h$                                      | Required comparisons                                                                                                                                                                                         |
  | ------ | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
  | C1     | $q=0.02$, $\ell=0$, $\beta^*=(1,1)$, $\sigma^2=3$, $h=0.002$ | Rare-risk contrasts at $(B,k)=(1,1000),(1,10000),(10,1000),(10,10000)$. The two $k=10000$ endpoints compare normalization orderings at fixed updates; $(1,10000)$ and $(10,1000)$ compare them at $M=10000$. |
  | C2     | $q=0.02$, $\ell=1$, $\beta^*=(2,1)$, $\sigma^2=4$, $h=0.01$  | Both risks and both coefficient MSE contrasts at $B=1$, $k=M=100$, including the cross-moment contribution. Retain $\ell=0.9$ as the interior theorem endpoint.                                              |

Use $h=0.002$ for the C1 signal/noise pair throughout the first slice and
$h=0.01$ for the C2 pair. Report both fixed values in the signal/noise slice.
They remain fixed comparisons even where they cease to be stable. Existing
continuous-box certificates check the theorem boundaries separately; this grid
does not replace them or extend their certified scope.

## Normalization, rates, and controls

Compare only no scaling U and standard-deviation scaling S:

$$
  S_U=I_2,\quad S_S=\operatorname{diag}(\sqrt a,\sqrt b),\qquad
  \eta_U=4h,\quad\eta_S=h,\quad P=S^{-2}.
$$

Steps are constant. Save actual divisors, $\eta$, $D=\eta P$, largest curvature
$\lambda_{\max}(S^{-1}CS^{-1})$, curvature-scaled rate, and moment stability.
Use $B\in\{1,10,100\}$ for every law and normalization. Across this grid, $Bq$
ranges from 0.002 to 10. No decreasing schedule, damped normalization, estimated
preprocessing, fitted intercept, or validation selection is added.

The coarse rate set is

$$
  H_c=\{0\}\cup\{0.002\,2^j,\;0.01\,2^j:j=-10,-9,\ldots,6\}.
$$

It has 35 values: zero and 34 positive values between $1.953125\times10^{-6}$
and $0.64$, including both anchors. Zero is the unchanged-initialization
baseline, not a convergence claim. This common $h$ grid affords both scalings
the same evaluated candidates before a stated stability restriction. It is not a
common absolute-$\eta$ grid or equal approximation error to a continuous
optimum.

For resolution checks, sort the positive coarse values $r_1<\cdots<r_{34}$ and
set

$$
  H_f=H_c\cup\{\sqrt{r_i r_{i+1}}:i=1,\ldots,33\}.
$$

The fine grid has 68 values with the same bounds. It adds resolution without
extending the search range. Use it only on the following **16 laws**, all chosen
now from the 228:

- The 12 combinations of $q\in\{0.002,0.02,0.1\}$, $\ell\in\{0,1\}$, and the two
  anchor signal/noise pairs.
- The three laws with $q=0.02$, $\ell\in\{-1,0,1\}$, $\beta^*=(2,-1)$, and
  $\sigma^2=4$.
- The pure-noise law $q=0.02$, $\ell=1$, $\beta^*=(0,0)$, $\sigma^2=4$.

Any later expansion is a separately labeled protocol amendment. Do not infer
resolution robustness for the other 212 laws from these 16.

### Global rescaling and common learning

For each direct-simulation panel below, repeat U and S with $S'=gS$ and
$\eta'=g^2\eta$ for $g\in\{0.1,10\}$. Couple initialization, observations,
noise, batch grouping, and stopping. Compare every original-scale iterate,
prediction, and saved moment with its unmodified counterpart. These controls are
duplicates of the same effective update, not extra tuning candidates. Use
absolute tolerance $2\times10^{-11}$ and relative tolerance $2\times10^{-10}$;
record maximum discrepancies, not just a pass flag.

At $\ell=0$, the common mean error must equal $-(1-h)^k\beta_C^*$ for both rules
at every shared $h,k$, regardless of $B$. The rare mean errors are
$-(1-4hb)^k\beta_R^*$ and $-(1-h)^k\beta_R^*$, respectively. These supply the
common-learning control without letting one method learn the common signal
faster by rate calibration.

At $\ell\ne0$, the same $h$ matches only common-coordinate diagonal drift.
Compute the actual mean errors as $e_k=-(I-DC)^k\beta^*$ and save the common
contrast $e_{C,k}^S-e_{C,k}^U$. Do not describe the dependent paths as matched
common learning. Show both coefficient mean paths alongside the risk contrast,
so a change caused by coupled common learning is visible. For zero common
signal, report absolute errors rather than dividing by $\beta_C^*=0$. The
squared-bias risk also provides a deterministic population-GD diagnostic at the
same step; it is not a competing algorithm with the same sample budget.

### Stability boundaries and failure probes

For each of the 36 $(q,\ell)$ laws, both scalings, and all three batches,
compute a bracket for the positive mean-square stability limit $\eta_{\rm MS}$
using the homogeneous symmetric second-moment operator. Record the bracket,
solver tolerance, and spectral radius $\rho$ at every evaluated rate. Check that
$0.99\eta_{\rm MS}$ is below and $1.01\eta_{\rm MS}$ above the boundary. The
numerically located boundary is not a new certified theorem.

As separate diagnostics, evaluate rates $\{0.5,0.99,1,1.01\}\eta_{\rm MS}$ and
the population-mean boundary $2/\lambda_{\max}(S^{-1}CS^{-1})$. Use
$\beta^*=(1,1)$, $\sigma^2=3$, and $k\in\{0,1,2,100,1000,10000\}$. These
law-specific rates are excluded from the common tuning grids. The scalar
rare-coordinate threshold from the existing stability result can be shown as a
reference, with the full operator determining multivariate stability.

Classify positive steps as stable when $\rho<1-10^{-10}$, numerically at the
boundary when $|\rho-1|\leq10^{-10}$, and unstable when $\rho>1+10^{-10}$. Keep
$h=0$ separately. A finite endpoint can be valid despite asymptotic instability.
Under the specified finite-support design and Gaussian noise, finite-time
moments exist even for unstable steps; floating-point overflow is a numerical
failure, not evidence of infinite finite-time risk.

## Stopping grids and resource accounting

The coarse update grid is

$$
  K_c=\{0,1,2,5,10,20,50,100,200,500,1000,2000,5000,10000\}.
$$

The coarse common-observation grid is

$$
  \mathcal M_c=\{0,100,200,500,1000,2000,5000,10000,20000,50000,100000\}.
$$

On the 16 refinement laws, also use

$$
  K_f=\{0\}\cup\{1,\ldots,200\}
  \cup\{250,300,\ldots,2000\}
  \cup\{2250,2500,\ldots,10000\},
$$

$$
  \mathcal M_f=\{0\}\cup\{100,200,\ldots,2000\}
  \cup\{2500,3000,\ldots,20000\}
  \cup\{22500,25000,\ldots,100000\}.
$$

These have 269 update counts and 89 observation counts, include the coarse
grids, and preserve their maximum budgets. For each batch, store moments at
$K\cup\{M/B:M\in\mathcal M\}$. Every declared $M$ is divisible by every batch.
Do not round update counts or interpolate risks to manufacture matched
observation budgets. Retain the originating budget-grid labels when endpoints
coincide.

At fixed $k$, report the different $M=kB$ values; the largest fixed-update
comparison uses $10^6$ observations for $B=100$. At fixed $M$, use exactly
$k=M/B$. The largest observation-grid budget is $10^5$. Fresh sampling gives
$n=M$ distinct observations in each run. Neither comparison is wall-clock
matching. Do not compare these fresh-sample budgets with repeated passes over
the fixed pilot as if they provided the same access to data.

The main archive has **51,048 distinct training configurations and 2,571,800
endpoints**, counting the labeled zero-step baselines and excluding boundary
probes and global-rescaling duplicates. Coarse stored counts for $B=1,10,100$
are 17, 14, and 14; refined counts are 321, 269, and 285. All 228 laws receive
$H_c$ and coarse stopping. The 16 selected laws receive $H_f$ and fine stopping,
subsuming their coarse entries. These counts make an incomplete grid detectable.

## Comparisons after rate and stopping adjustments

Report fixed-pair paths first, including the anchors, both risks, and all three
risk components. At shared fixed $k$ and $h$, also report the within-rule batch
contrast. Check the existing larger-batch moment ordering there. At shared $M$,
compare the actual different update counts without assuming that ordering.

Then compute two finite-grid oracle envelopes separately for each normalization,
batch, data law, and objective $W\in\{C,C_R\}$:

- **Rate adjustment:** minimize $R_W(h,k)$ over the declared eligible $h$ at
  each exact update or observation budget. The stopping count remains fixed.
- **Rate and stopping adjustment:** minimize over eligible $h$ and declared
  stops within a common cap $k\leq K_{\max}$ or $kB\leq M_{\max}$. For an update
  cap, use the corresponding $K$ grid; for an observation cap, use the
  corresponding $\mathcal M/B$ grid. Report the observations actually consumed
  by each selected fit as well as its cap.

Use every point in the relevant update or observation grid as a cap, including
the zero baseline. For resolution comparisons, use the shared coarse caps.

Primary envelopes admit stable positive steps and the zero-update predictor
($h=0$ or $k=0$). Evaluate the whole declared grid for both rules and report the
number of eligible candidates, which can differ because of stability. Alongside
them, report unrestricted finite-time envelopes including valid unstable and
boundary endpoints. Never remove an unstable fixed anchor from the report. An
envelope with unresolved invalid candidates is incomplete: the minimum among its
valid entries is only an observed upper bound on that grid's minimum. Do not
infer an ordering against another method's upper bound. Resolve such candidates
with a checked higher-precision calculation or retain the incomplete label.
Boundary uncertainty also limits the stable-only comparison.

Primary U/S envelope comparisons hold $B$ fixed. A secondary search over $B$
uses only common observation caps and the same candidate sets for U and S.
Report it separately from the within-batch result. Common update counts do not
give equal observation cost when selecting batch size.

Use all four coarse/fine combinations of rate and stopping resolution on the 16
refinement laws. Compare them at shared budgets or caps, reporting selected
$h,k$, objective value, cross-objective risk, and any classification changes.
Record optima at zero, the smallest or largest positive rate, and the earliest
or latest eligible stop. These are limits of the search, not grounds for an
unreported grid expansion. Preserve all tied minimizers within the numerical
tolerance below; for one display row, prefer fewer observations, then smaller
$h$, then smaller $B$.

Call a contrast positive or negative only beyond
$\tau=10^{-8}\max(1,|R_W^S|,|R_W^U|)$; otherwise label it numerically
unresolved. This tolerance classifies floating-point signs, not statistical
significance or scientific importance. Save unrounded values, absolute gaps, and
gaps relative to U and to initialization where those denominators are positive.
Use absolute gaps alone for zero denominators.

Report C1's four original signs separately from signs after adjustment. For C2,
distinguish the same fixed-pair disagreement from the two objective-specific
envelope contrasts. The latter may use different trained pairs. Cross-evaluate
both risks for the aggregate-selected U/S pair and the rare-selected U/S pair;
do not present separately optimized objectives as risks of one common pair.
Retain coefficient MSEs and cross moments when interpreting any disagreement.
Neither oracle envelope estimates validation-selection performance or a global
optimum over rates, stopping, and normalization.

## Paired direct simulations and uncertainty

Use **8,192 independent replications** for each of these six prespecified
panels, with U and S and $B\in\{1,10\}$ in each panel:

  | Panel ID                          | $(q,\ell,\beta^*,\sigma^2,h)$ | Stops for each batch     |
  | --------------------------------- | ----------------------------- | ------------------------ |
  | 0: C1                             | $(0.02,0,(1,1),3,0.002)$      | $k\in\{100,1000,10000\}$ |
  | 1: C2                             | $(0.02,1,(2,1),4,0.01)$       | $k\in\{10,100,1000\}$    |
  | 2: Greater rarity                 | $(0.002,0,(1,1),3,0.002)$     | $k\in\{100,1000,10000\}$ |
  | 3: Negative dependence and signal | $(0.02,-1,(2,-1),4,0.01)$     | $k\in\{10,100,1000\}$    |
  | 4: Common-only signal             | $(0.02,0,(1,0),1,0.002)$      | $k\in\{100,1000,10000\}$ |
  | 5: Pure noise                     | $(0.02,1,(0,0),4,0.01)$       | $k\in\{10,100,1000\}$    |

Use 32 fixed blocks of 256 replications. For block $r$ in panel $p$, initialize
NumPy PCG64 with `SeedSequence([20260916, p, r, s])`, using stream $s=0$ for
features and $s=1$ for noise. Declare generation order as observation first,
replication second within each block, and record NumPy's version. All compared
configurations reuse the same ordered feature and noise stream. Batch ten groups
consecutive observations that batch one processes singly. At a fixed update
count the streams share a prefix but consume different lengths; at a fixed
observation count they consume identical observations. No uncertainty
calculation treats coupled configurations as independent replications.

Generate observations in blocks without storing the complete training stream.
Stop updating a configuration after its last requested endpoint, while keeping
the longer stream for other configurations. For example, C1's longest batch-ten
path consumes 100,000 observations per replication; its batch-one path needs
only 10,000. These costs are part of the declared simulation workload.

For replicate error $e^{(r)}$, evaluate test risk exactly over the four cells,
$L_W^{(r)}=e^{(r)\top}We^{(r)}/2$. This removes test-set sampling error. For any
contrast, form the within-replicate difference $d_r$ and report

$$
  \widehat\Delta=\frac1N\sum_{r=1}^N d_r,\qquad
  \operatorname{MCSE}(\widehat\Delta)
  =\frac{\operatorname{sd}(d_1,\ldots,d_N)}{\sqrt N},\qquad N=8192,
$$

with sample standard deviation. Report means and MCSEs for coefficient errors,
second moments, both risks, and paired U/S and batch contrasts at all matched
endpoints in these panels. Save per-replication endpoint quantities so pairing
can be independently rechecked. Descriptive intervals
$\widehat\Delta\pm1.96\operatorname{MCSE}$ are pointwise normal approximations,
not simultaneous tests across the grid. A crossing whose interval includes zero
is a limited-precision simulation result, not evidence of equality.

Run noiseless companions on the same feature stream. Their centered covariance
and the second moment of noisy-minus-noiseless coefficients independently check
the two covariance contributions; retain the empirical cross term as well. Use
unbiased sample covariance for the noiseless component and a delete-one-block
jackknife over the 32 replication blocks for its MCSE. The exact moments have
floating-point error, **no Monte Carlo standard error**. Simulation agreement
within six MCSE plus $10^{-10}$ is a diagnostic gate, not a scientific
significance threshold. Investigate violations and report them; do not increase
replications until a desired sign appears. This simulation subset validates
direct updates and uncertainty, not retuned selection or the entire grid.

If any replicate fails, retain its panel, configuration, replicate ID, update,
reason, and last finite state. Mark the affected paired summary incomplete;
averaging only surviving replications changes its target. Report failure counts
alongside exact moments, even if the latter remain valid.

## Validation, artifacts, and execution gate

Before expanding the calculation:

1. Check every cell law, centering, $C$, and $C_R$ by direct support sums. Check
   all budgets, set nesting, deduplication, and the configuration/endpoint
   counts above. Compute both risks using the conditional second moment, not
   conditional covariance.
2. Enumerate short direct scaled-coordinate gradient paths for $B=1,2$ and
   $k=0,1,2$, covering independent, negative, and nested laws, mixed-sign and
   non-unit signals, both scalings, and zero/nonzero two-point noise. Compare
   original-scale means, moments, and all decomposition terms with the moment
   implementation. Use absolute tolerance $2\times10^{-11}$ and relative
   tolerance $2\times10^{-10}$.
3. Check long anchor endpoints against a separate one-update-at-a-time moment
   implementation. Re-run the existing C1/C2 certificates. Check global
   rescaling, common-learning identities, within-budget risk evaluation, and
   fixed-update batch ordering before interpreting the broader grid.
4. Exercise zero steps, zero signal, zero noise, boundary rates, overflow,
   incomplete paired summaries, and a grid minimum on a search boundary. Check
   symmetry and positive semidefiniteness of $V_k,A_k,\sigma^2N_k$ within the
   stated numerical tolerance. Record raw residuals and validity reasons; do not
   silently clip eigenvalues, risks, or plotted curves.

Use the existing finite-update operators, with an independently checked new
driver accepting each law's signal and noise explicitly. Reusing general helpers
must not import the first study's fixed signal into coefficient means or
summaries. Implement and run the focused checks before generating results. The
new runner, checker, and reproduction target are deliverables of the execution
task; no existing command currently runs this protocol.

Reserve `results/normalization-robustness/` for these generated artifacts:

- `specification.json`: protocol version and note hash, expanded law and
  training grids, slice labels, controls, seeds, tolerances, source/lockfile
  hashes, software versions, actual commands, and checksums of both preserved
  studies.
- `paths.npz`: every declared original-scale moment endpoint with configuration
  IDs, $k$, $M$, validity, and decomposition arrays. Record attempted endpoints
  even if their values are unavailable. Use explicit failure codes in the JSON,
  without nonstandard JSON NaN or infinity values.
- `summary.json`: fixed anchors, all contrasts and oracle selections,
  eligibility counts, resolution comparisons, boundary probes, simulation
  summaries, checks, and all failures. Include counts by law, scaling, rate,
  batch, and stopping.
- `paired-simulation.npz`: replicate IDs, paired endpoint quantities, noiseless
  companions, and failure masks. Hash it and the moment archive in the summary.
- `figures/`: SVG and PDF paths for fixed-pair risks and decompositions, rate
  and stopping adjustments, coarse/fine sensitivity, and C2's cross-moment
  effect. Use common axes within comparisons; label missing, unstable, and
  clipped plot regions and retain their raw values in the archives.

Write findings separately in `notes/normalization-robustness-results.md`,
linking to the expanded specification and artifacts. It must show both anchors
before adjustment, where each comparison survives or disappears, null or
unfavorable cases, actual budgets, boundary selections, and unresolved failures.
Plotting or screening must not delete these outcomes. Keep the pilot's risk
convention distinct: divide its excess squared prediction error by two only in
an explicitly labeled comparison. Do not pool its fixed-data uncertainty with
fresh-sample simulation uncertainty.

Completion of the execution task requires reproduction of the new artifacts,
independent numerical checks, paired uncertainty, a complete failure ledger, and
verified checksums for the preserved studies. Tail averaging is deferred unless
a subsequent stated literature question requires it; such an extension must
specify its window and compute cross-iterate moments, not average marginal
risks. Estimated preprocessing, absent rare observations, validation selection,
and a real sparse task remain the subsequent practical study.

## Specification audit

A design-only check inside `devenv shell` enumerated the sets above: 228 laws,
16 refinement laws, 35/68 rates, 51,048 configurations, and 2,571,800 endpoints.
Direct support sums verified feasibility, population centering, positive
definiteness of $C$, and the conditional test matrix for all 36 feature laws.
The existing full moment operator verified the below/above-boundary brackets for
all 216 feature-law, scaling, and batch combinations. This checks that the
declared experiment is internally consistent; it is not a robustness finding.
