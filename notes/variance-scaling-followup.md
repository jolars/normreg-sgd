# Variance scaling across practical preprocessing arms

September 16, 2026. Protocol version 1, declared before executing these new
candidates. This follow-up completes the fourth scaling comparator across the
synthetic and Mushroom practical settings and extends the unresolved variance
rate search. It is informed by the earlier studies on these same laws and data;
it is not a held-out confirmation of a new prediction.

## Samples and preprocessing

Reuse all eight laws, 128 replications per law, training size 256, validation
size 128, exact four-cell excess test risks, and all five arms in the frozen
[practical protocol](practical-selection.md). Reuse both Mushroom sizes, 32
partitions per size, all three empirical preprocessing arms, the green
spore-print subgroup, training-only vocabulary, and held-out records. Retain the
original samples, label noise, and replacement index streams. These are
fixed-data replacement-SGD experiments, not fresh-sample dynamics.

Use population variances only in the synthetic `known` arm, training variances
with denominator $n$ otherwise. Preserve population or training means, the
initializations, fixed or fitted unscaled intercepts, unknown-category policy,
and constant-column policy of the practical study. Estimated constant columns
have divisor one and coefficient fixed at zero. Known population-centered
columns remain active even when absent from training.

## Four rules and equal searches

Compare divisors $s_j=1$, $\sqrt{v_j}$, $\sqrt{v_j+0.01}$, and $v_j$, named
`none`, `sd`, `damped`, and `variance`. The last corresponds to $\delta=1$ in
$s_j=v_j^\delta$. The damping offset remains a fixed heuristic. Use averaged
half squared loss, zero feature coefficients, and original-scale reporting. Do
not add penalties, clipping, momentum, averaging, or refitting.

For every rule and arm set $\eta=a/\max(L,10^{-12})$, with the empirical
scaled-design curvature including the intercept coordinate only when fitted. Use
the same 25 factors:

$$
  a\in\{0.00001,0.0001,0.001,0.01,0.05,0.2,0.4,0.6,0.8,1,
  1.2,1.4,1.6,1.8,2,2.4,3.2,4.8,6.4,12.8,25.6,51.2,102.4,204.8,409.6\}.
$$

The two smaller factors probe lower boundaries; six successive doublings above
6.4 address the variance upper boundary. Fix the grid before execution and
report any remaining edges without adapting it to test outcomes. This grid does
not establish a continuous tuning optimum or guarantee stochastic stability.

Synthetic batches are $\{1,16\}$, with stored checkpoints
$\{0,128,256,512,1024,2048\}$ and caps $\{128,512,2048\}$. Mushroom batches are
$\{16,128\}$, with stored checkpoints $\{0,128,256,512,1024,2048,4096,8192\}$
and caps $\{512,2048,8192\}$. Compare at matched processed count $M$ and retain
update count $k=M/B$.

Within each arm and scaling, jointly select rate, batch, and stopping for each
cap using aggregate or rare validation. Primary selection uses the original
stage-specific checkpoints; secondary selection uses all stored checkpoints.
Also evaluate the nested five-factor practical search and, for Mushroom, the
nested 17-factor search, both with original stops. These nested comparisons use
the same four methods, so the new variance candidate is never compared only
against less-tuned baselines. No selection across scalings is added.

Initialization is eligible. Break ties by lower processed count, batch, factor,
then candidate index. If rare validation is empty, fall back to aggregate loss
and flag that decision. Test outcomes never enter selection. Each fixed rule
uses 50 paths, costing nominally $50M$ processed observations per arm and split;
the four-rule total is $200M$. Nested five- and 17-factor searches cost $10M$
and $34M$ per rule. Extra stops reuse trajectories but increase scoring. Record
nominal and executed live-path observations and scored endpoints. Preprocessing,
curvature calibration, and validation scoring are outside the training budget.

## Interpretation and reporting

Variance scaling's original lasso motivation concerns the original-coordinate
penalty weights. Here there is no explicit penalty: its SGD coordinate update
multiplier is $\eta/s_j^2=\eta/v_j^2$ on active columns. Curvature calibration
also changes the scalar learning rate. Faster relative rare-coordinate updates
therefore bring different noise and stability tradeoffs; a shrinkage argument
does not establish a prediction ordering for tuned SGD.

Keep every path, checkpoint, and split. A path fails on nonfinite arithmetic or
an original coefficient or centered intercept exceeding $10^{100}$ in absolute
value. Record its first failed update and mark later checkpoints as failed.
Failed validation endpoints have infinite selection score. Extreme finite
endpoints remain eligible. Empty test subgroups have missing losses and explicit
denominators, never zero losses.

Archive all original-scale coefficient and intercept paths, preprocessing,
partitions, streams, losses, and choices. For each law or size, arm, cap,
objective, and search, report both test risks, means, MCSEs, medians, 95th
percentiles, maxima, absence strata, paired differences from each other rule,
initializations, rate/batch/stop histograms, failures, and work counts. Record
immediate-neighbor validation scores for expanded selections, separately from
initialization. Summarize original-scale rare coefficients and selected-path
risks, including continuation beyond a selected stop with missing denominators.

The primary categorical comparison remains centered/fitted, $n=2048$, $M=8192$,
aggregate selection, and original stops. Present all synthetic laws at the
largest cap in that arm, without pooling them into one headline. All other arms,
caps, objectives, and stopping resolutions are secondary and remain available.
Two-MCSE paired contrasts are descriptive. Synthetic MCSE covers sampling and
optimization variation; Mushroom MCSE is conditional on this previously studied
dataset and overlapping partitions. Tail-dominated means need their medians and
maxima. No universal ordering, equivalence claim, or practical safety
recommendation follows.

## Declaration, preservation, and checks

New outputs belong under `results/variance-scaling-followup/`; the result note
is `notes/variance-scaling-followup-results.md`. Freeze this protocol and
`experiments/variance_scaling_spec.py` by SHA-256 before executing candidates.
Preserve the earlier experiments, results, data, protocols, result notes,
`Makefile`, and `uv.lock` by their current file hashes, including the ignored
robustness artifacts recorded by the earlier studies. Record sources, locked
dependencies, versions, archive hashes, declaration time, and execution time.
The earlier studies and their failures remain unchanged.

Before execution, independently check all four divisors and every arm's
curvature against explicit transformed designs, dense/sparse short paths,
fixed/fitted intercepts, inactive and unknown columns, first failures, selection
eligibility, ties, and absent-group fallbacks. After execution, reconstruct all
losses and selections, compare overlapping original paths with the frozen
practical and centered Mushroom sensitivity archives, and replay all selected
trajectories plus every trajectory in replication zero of each case in
transformed coordinates. Independently audit paired summaries, boundaries,
counts, and hashes. A normwise trajectory discrepancy above $2\times10^{-9}$ or
a selected validation prediction discrepancy above $10^{-8}$ is a reported
numerical gate violation, not a reason to discard a path or change selection.
Retain details of such violations and limit numerical agreement claims to the
checks that pass. Build both manuscripts and run integrated checks.
