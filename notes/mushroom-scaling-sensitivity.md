# Mushroom damping and variance-scaling sensitivity

September 16, 2026. Protocol version 1, declared before running these new
candidates. The offset 0.01 was a prespecified heuristic in the controlled
pilot, then inherited by the practical studies. No derivation or sensitivity
assessment established that particular value. This follow-up tests sensitivity
to the offset and restores variance scaling as a comparator. It is informed by
the earlier results on these same data, not independent confirmation.

## Scope and preserved studies

Use both existing Mushroom training/validation sizes, $(256,128)$ and
$(2048,1024)$, with all 32 partitions per size, the same held-out records, and
the same replacement index streams. Restrict this bounded comparison to the
primary `centered_fitted` arm. This does not resolve other intercept/centering
arms or the synthetic practical experiments.

Preserve the protocols, sources, data, and numerical artifacts of all earlier
studies against commit `94ed9b4931c8b648ce6ec3aab3f32e4cb53041f0`. New artifacts
belong in `results/mushroom-scaling-sensitivity/`, and results in
`notes/mushroom-scaling-sensitivity-results.md`. Declare protocol and
specification hashes before execution; record all source, dependency, input, and
archive hashes. Reconstruct the three shared methods against the frozen
rate-search archive as a replication check.

## Methods and tuning

For each active training column, compare these eight fixed rules:

- No scaling: $s_j=1$.
- SD scaling: $s_j=\sqrt{v_j}$, equivalently damping $\tau=0$.
- Variance scaling: $s_j=v_j$.
- Five damped rules: $s_j=\sqrt{v_j+\tau}$ for
  $\tau\in\{0.001,0.003,0.01,0.03,0.1\}$.

Here $v_j$ is the training variance with denominator $n$. Retain training-only
vocabularies and centering, unknown categories as zero blocks, and constant
columns frozen at zero coefficient with divisor one. Fit an unscaled intercept
initialized at the training response mean, with zero initial coefficients and
averaged half squared loss. No clipping, penalty, averaging, momentum, or
validation refitting is added. Coefficients use the original feature scale and
are not uniquely identified effects in the full one-hot design.

For **each fixed rule**, use all 17 rate factors from the frozen expanded
search, $\eta=a/\max(L,10^{-12})$, with fitted-intercept empirical curvature
$L$, and $B\in\{16,128\}$:

$$
  a\in\{0.001,0.01,0.05,0.2,0.4,0.6,0.8,1,1.2,1.4,1.6,1.8,
         2,2.4,3.2,4.8,6.4\}.
$$

Store all checkpoints $M\in\{0,128,256,512,1024,2048,4096,8192\}$. At caps 512,
2048, and 8192, select rate, batch, and stopping by aggregate or rare-group
validation loss. Primary selection uses the original checkpoints
$\{0,512,2048,8192\}$; secondary selection uses all stored checkpoints. Report
initialization selections separately. Tie order is lower processed count, batch,
rate, then candidate index. Empty rare validation groups fall back to aggregate
validation, with the fallback flagged. Test outcomes never enter selection or
changes to the grid.

Each rule receives 34 training paths, costing nominally $34M$ processed
observations per split at cap $M$. The complete eight-rule study costs $272M$;
the five positive damping values alone cost $170M$. Extra stopping checkpoints
reuse paths but increase validation scoring. Record executed live-path work and
scoring counts as well as nominal work. Preprocessing and scoring are outside
the training budget. **Do not select a damping level using test results or
present the best of five levels as a competitor with equal tuning effort.** This
study evaluates sensitivity at fixed offsets, not a deployable rule for choosing
the offset.

## Failures and reporting

Use the frozen failure rule: nonfinite arithmetic or an original coefficient or
centered intercept exceeding $10^{100}$ in magnitude. Retain first-failure
updates and every failed endpoint. Finite extreme candidates remain eligible;
failed endpoints have infinite validation loss. Retain all splits and identify
missing-group denominators. Report lower/upper rate boundaries and finite
immediate-neighbor validation comparisons, without extending the grid after
seeing test results. Interior choices do not establish continuous optima.

Save all original-scale coefficient/intercept paths, preprocessing, candidate
losses, selections, partitions, and index streams. Summarize green coefficients,
their centered contributions, other-feature contributions, both risk paths, and
selected endpoints. Continuation after a selected stop is descriptive.

For each size, objective, cap, and stopping search separately, report means,
MCSEs, medians, 95th percentiles, and maxima. Use paired differences against no
scaling, SD, the original damping 0.01, and variance scaling; retain absence
strata. MCSE describes variation across these overlapping partitions and
optimizer streams on one fixed dataset. Two-MCSE contrasts are descriptive,
without equivalence or simultaneous-testing claims.

The primary assessment is the centered/fitted, aggregate-selected comparison at
$n=2048$, $M=8192$, using original stops. Classify its advantage over none as
insensitive to this grid only if both paired risk differences remain negative by
more than two MCSE at every positive damping value. Otherwise report the actual
interval of tested offsets retaining those differences, any reversals, and
unresolved contrasts. Separately assess variance scaling against the three
original rules. Retain smaller budgets, smaller samples, and rare validation as
secondary comparisons rather than pooling them.

## Independent checks

Before execution, check divisors and curvature against explicitly transformed
features, short trajectories against transformed-coordinate SGD, constant
columns, failures, and validation selection/ties/fallbacks. After execution,
independently reconstruct all losses and selections, replay all selected paths
and all paths in replication zero at each size, and audit paired summaries, work
counts, and preserved hashes. Require normwise trajectory discrepancies below
$2\times10^{-9}$ and selected validation prediction discrepancies below
$10^{-8}$. Numerical failures remain reported if a gate is exceeded.
