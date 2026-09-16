# Mushroom rate-search follow-up

September 16, 2026. Protocol version 1, declared before running this follow-up.
The motivation is the observed upper-rate boundary in the [frozen practical
study](practical-selection-results.md): all 32 large-sample unscaled aggregate
selections used factor 0.8. This is a follow-up on the same dataset and splits,
not an independent confirmation on new data. The original protocol, results,
sources, precision investigation, and artifacts remain unchanged. Results belong
in `mushroom-rate-search-results.md` and `results/mushroom-rate-search/`.

## Data, models, and pairing

Reuse all 64 Mushroom replications from [practical protocol version
1](practical-selection.md): 32 permutations at each training/validation size
$(256,128)$ and $(2048,1024)$, with the remaining records held out. Use the same
training-only one-hot vocabularies, unknown-category policy, population-variance
denominator $n$, constant-column freezing, and green-spore subgroup. Reuse the
exact replacement index streams and all preprocessing/intercept arms:
`centered_fixed`, `centered_fitted`, and `uncentered_fitted`. The primary arm is
`centered_fitted`; report the others as ablations, without pooling sizes or
arms. The three divisors remain 1, $\sqrt{v_j}$, and $\sqrt{v_j+0.01}$.

Use averaged half squared loss, zero initial feature coefficients, and the
training response mean as initial intercept. The raw original-scale predictor is
$b_0+x^\top\beta$; store both $b_0$ and every component of $\beta$. Fitted
intercepts have divisor one. Full one-hot coefficients are optimizer-dependent,
not uniquely identified or causal effects. No clipping, penalty, momentum,
averaging, or validation refit is introduced. This is fixed-data replacement
SGD, not fresh-sample SGD.

## A broader, equally allocated search

Continue to set $\eta=a/\max(L,10^{-12})$, where $L$ is the largest empirical
scaled-design curvature, including the intercept coordinate when fitted. Use the
following **17 factors for every scaling and arm**:

$$
  a\in\{0.001,0.01,0.05,0.2,0.4,0.6,0.8,1,1.2,1.4,1.6,1.8,
         2,2.4,3.2,4.8,6.4\}.
$$

The old five factors are a nested reference. The new grid gives denser coverage
near the previous upper edge and extends eightfold beyond it, including factors
above the full-batch quadratic stability threshold 2. This is not a stochastic
stability guarantee or a reason to remove a candidate. Use both original batches
$B\in\{16,128\}$ and budget caps $M\in\{512,2048,8192\}$. Record $k=M/B$, $n$,
$L$, and the absolute $\eta$ separately.

Save paths at $M\in\{0,128,256,512,1024,2048,4096,8192\}$. Compare these three
searches, all specified before examining the new outcomes:

1. `original`: the old five factors and old stopping checkpoints
   $\{0,512,2048,8192\}$. Reconstruct the frozen selections as a replication
   check.
2. `expanded`: all 17 factors, with those same old stopping checkpoints. This
   isolates rate expansion.
3. `expanded_stops`: all 17 factors and all eight stored checkpoints. This
   separately tests stopping resolution, using the same training paths.

For every search, size, arm, cap, and scaling, select rate and batch at the cap
(`rate_batch`), or rate, batch, and stopping at or below the cap (`joint`). Use
both aggregate and rare validation objectives. Retain the original fixed
configuration $a=0.05$, $B=16$ at every cap as a descriptive baseline. There is
no joint selection over scalings in this follow-up. Duplicate `rate_batch`
queries for `expanded_stops` are omitted because their candidate pools are
identical to `expanded`.

Each expanded scaling/arm receives 34 trajectories, costing at most $34M$
processed training observations at cap $M$, versus $10M$ in the nested old
search and $M$ for the fixed baseline. Equal effort compares scalings within a
search; expanded versus original has deliberately greater tuning effort.
Checkpoints share trajectories. The extra stopping search increases validation
scoring, not training work. Record nominal and actually executed training work,
including early numerical termination, and endpoint scoring counts.
Preprocessing uses $n$ records and nine Gram calculations per split; these costs
are outside the observation budget. Runtime and software versions are
descriptive.

## Failures, selection, and boundary assessment

Keep the original path failure rule: nonfinite arithmetic or a feature
coefficient/centered intercept exceeding $10^{100}$ in magnitude. Record the
first failing update, keep its failure flag and all subsequent failed endpoints,
and never replace an extreme finite test loss with a missing value. A failed
endpoint has infinite selection loss. Retain finite unstable candidates. If all
eligible endpoints fail, use initialization and flag that fallback. If rare
validation observations are absent, use aggregate validation and flag that
fallback. Empty test subgroups have missing loss with a reported denominator.
Tie ordering is lower $M$, lower $B$, lower $a$, then the original scaling
order. Test labels cannot enter selection, rate calibration, or any boundary
decision. Do not extend this grid based on its test results.

Report selected rate/batch/stop histograms and lower/upper-boundary counts for
all queries. For every expanded joint selection, also compare its validation
score with the same path's immediate lower and higher rate neighbors at the same
batch and stopping point, and retain the higher-rate endpoint's failure flag.
Initialization has no meaningful rate and is counted separately. The original
upper-edge problem is resolved **within the declared grid** if no large-sample
unscaled aggregate joint selection in the primary arm at $M=8192$ uses 6.4 and
each positive-budget selection has a higher tested neighbor with a worse or
equal validation score (or a failed endpoint). Report any other unresolved
boundaries. Interior selection does not prove a continuous optimum, stochastic
stability, or comparable approximation error across scalings.

## Reporting and interpretation

Retain every candidate's training, validation, and test aggregate and subgroup
loss, original-scale coefficients, raw and centered intercepts, preprocessing,
and selection status. Report selected endpoints and paths together. Show the
green-indicator coefficient, its centered contribution, other features'
conditional contribution, and their sum with the centered intercept. Show
aggregate and rare test risks along the trajectories selected at the largest cap
for both objectives, including the selected stopping point. Continuation after a
selected stop is descriptive only. Save summaries of all candidate curves, with
explicit failure/missing counts rather than survivor-only comparisons presented
as complete means.

Use paired differences and Monte Carlo standard errors (sample SD divided by the
square root of the number of complete pairs), plus medians, 95th percentiles,
and maxima. Compare scaling versus none, expanded versus original, extra
stopping versus expanded, and rare-objective versus aggregate-objective
selection. Include train-absence and validation-absence strata and denominators.
These MCSEs describe partition and optimizer variation conditional on this fixed
dataset; they are not population confidence intervals. All splits remain in
reported means, including catastrophic finite selections.

Classify the original normalization comparisons using the paired contrasts: an
advantage persists if its direction survives expansion and its magnitude exceeds
two MCSE; it disappears if the expanded contrast is within two MCSE of zero, or
reverses with magnitude exceeding two MCSE. Report unresolved numerical or
search-boundary cases separately. This two-MCSE convention is descriptive, not a
multiple-comparison test or proof of equivalence. Provide numerical gaps
alongside these labels. Treat all ablations and shorter caps as secondary.
Missing green training or validation observations remain limitations.

## Declaration, preservation, and verification

Write a declaration containing the protocol/specification hashes and the current
baseline commit before execution. Verify those hashes on every run. Preserve all
existing tracked experiment sources, results, Mushroom input files, and the two
practical-study notes against that baseline. The new artifacts also record their
source, dependency-lock, archive, summary, and figure hashes. No earlier study
is regenerated or edited.

Before running the experiment, check explicit transformed-design updates against
the new runner, including dense/sparse inputs, intercepts, constant columns,
failure updates, empty groups, ties, and the three candidate pools.
Independently reconstruct every archived loss and selection. Replay all paths
for replication zero of both sizes, and all selected paths for the other splits,
in transformed coordinates. Compare vectors normwise and check selected
validation predictions; investigate discrepancies larger than
$10^{-8}(1+|\widehat y|)$ separately without silently changing primary
selection. Reproduce the old checkpoints and selections against the frozen
archive. Independently check paired summaries, boundary diagnostics, failure
counts, and preservation hashes. Build the manuscript, inspect the new figures,
and run the full repository validation.
