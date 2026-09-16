# Variance scaling across practical arms: results

Variance scaling is now included alongside none, SD, and damping in every
synthetic and Mushroom preprocessing arm. The common expanded grid removes the
Mushroom rate-edge selections. Its primary selected predictors and risks are
unchanged from the nested 17-factor search: variance scaling retains larger
rare-group loss than each comparator, while its aggregate contrast is too noisy
to resolve by the descriptive two-MCSE criterion. The synthetic results retain
extreme finite selections and some unresolved rate boundaries. They do not
establish a universal ordering of tuned scaling rules.

## Declared comparison

The [protocol](variance-scaling-followup.md) and
[declaration](../results/variance-scaling-followup/declaration.json) fix the
four methods, 25 curvature-relative rate factors from $10^{-5}$ to 409.6, two
batches, and original and refined stopping searches before execution. The eight
synthetic laws retain all 128 replications and all five preprocessing arms.
Mushroom retains both sample sizes, all 32 partitions per size, and all three
empirical arms. Training, validation, test data, and index streams are paired
with the earlier studies. This is a follow-up on previously studied settings,
not independent confirmation.

Each rule receives 50 training paths per arm and split, nominally $50M$
processed observations at cap $M$. The four-rule total is $200M$. Nested
five-factor and 17-factor searches retain their smaller work counts. Checkpoints
reuse trajectories; preprocessing and scoring are outside the training budget.
No test result changes a grid, selects a method, or excludes a split. The
damping offset stays at its prespecified heuristic 0.01.

There are 6,451,200 saved endpoints and 387,072 selection decisions. Synthetic
data contribute 6,144,000 endpoints, including 1,009,300 failed endpoints on
321,338 failed paths. Mushroom contributes 307,200 endpoints, including 22,240
failed endpoints on 9,580 failed paths. Failures are retained with their first
update, and all finite candidates remain eligible for validation selection. The
expanded grid deliberately includes unstable rates; these failure counts
describe the candidate family rather than the selected procedures.

## Primary Mushroom comparison

These are held-out half squared losses at $n=2048$, validation size 1024, cap
$M=8192$, training centering, a fitted intercept, and original stopping
checkpoints. Parentheses contain MCSE across all 32 paired partitions.

  | Selection | Scaling  | Aggregate loss       | Rare-group loss     |
  | --------- | -------- | -------------------: | ------------------: |
  | Aggregate | None     |  0.001341 (0.000074) | 0.005955 (0.000888) |
  | Aggregate | SD       |  0.004476 (0.001498) | 0.004764 (0.001079) |
  | Aggregate | Damped   |  0.000810 (0.000039) | 0.000682 (0.000133) |
  | Aggregate | Variance |  0.311988 (0.201772) | 0.051586 (0.008319) |
  | Rare      | None     |  0.039395 (0.017807) | 0.003678 (0.000334) |
  | Rare      | SD       |  0.141068 (0.079208) | 0.002257 (0.000419) |
  | Rare      | Damped   |  0.002611 (0.000958) | 0.000499 (0.000112) |
  | Rare      | Variance | 25.572030 (8.045267) | 0.019374 (0.002403) |

Under aggregate selection, variance-minus-none rare loss is 0.045630 (paired
MCSE 0.008323). Its rare disadvantages against SD and damping are 0.046822
(0.008189) and 0.050904 (0.008322). All exceed two MCSE. The aggregate
differences, respectively 0.310647 (0.201754), 0.307512 (0.201403), and 0.311178
(0.201763), do not. Variance's aggregate median is 0.069802 and maximum
6.505207; its mean is not a typical outcome. Rare selection produces still more
variable aggregate loss: median 5.7430 and maximum 154.6572.

The earlier primary variance choices at factor 6.4 remain selected in
replications 7 and 22, both at $B=128$ and $M=512$. Their immediate higher
factor 12.8 now has finite, worse aggregate validation losses, respectively
0.078750 and 10.058543. Thus 6.4 is an interior tested choice, not an untested
upper edge. Across both Mushroom sizes, all arms, objectives, caps, and both
expanded stopping searches, no positive-budget selection uses $10^{-5}$ or
409.6. This resolves the finite grid boundary, not a continuous optimum.

At original stops, all Mushroom selected predictors match the nested 17-factor
search. Sixty candidate-index changes only relabel the identical initial
predictor with the newly available lower factor. Refined stopping does select
some added rates through 102.4, so the conclusion of unchanged predictors is
specific to the original stops. The full refined results and their continuation
paths remain in the summaries.

Mean original-scale green coefficients in the primary aggregate-selected
comparison are 0.5999, 0.7763, 0.9126, and 0.2954 for none, SD, damping, and
variance. The full one-hot design is rank deficient; these describe the
optimizer's path, not uniquely identified or causal category effects.

## Other Mushroom preprocessing arms and sample size

The table reports aggregate-selected means at cap 8192 and original stops. Each
cell is aggregate loss / rare-group loss. All four methods receive the same
search effort within an arm.

  | Training size | Arm                          | None                | SD                  | Damped              | Variance             |
  | ------------: | ---------------------------- | ------------------: | ------------------: | ------------------: | -------------------: |
  |           256 | Centered, fixed intercept    | 0.004740 / 0.101062 | 0.003846 / 0.075937 | 0.003533 / 0.077910 |  0.011805 / 0.079580 |
  |           256 | Centered, fitted intercept   | 0.004752 / 0.098799 | 0.004647 / 0.076035 | 0.003568 / 0.078161 |  0.011799 / 0.079579 |
  |           256 | Uncentered, fitted intercept | 0.006764 / 0.136151 | 0.004550 / 0.076391 | 0.004491 / 0.082727 |  0.179701 / 0.079542 |
  |          2048 | Centered, fixed intercept    | 0.001273 / 0.005647 | 0.004631 / 0.004722 | 0.000807 / 0.000652 |  0.311944 / 0.051601 |
  |          2048 | Centered, fitted intercept   | 0.001341 / 0.005955 | 0.004476 / 0.004764 | 0.000810 / 0.000682 |  0.311988 / 0.051586 |
  |          2048 | Uncentered, fitted intercept | 0.003924 / 0.043284 | 0.003126 / 0.005060 | 0.001620 / 0.007037 | 13.787223 / 0.049465 |

At $n=256$, centered/fitted variance has larger aggregate loss than none by
0.007047 (paired MCSE 0.000555). Its rare-loss difference is -0.019220
(0.012351), within two MCSE of zero. Its rare contrasts with SD and damping are
also unresolved. Thus the resolved primary large-sample rare disadvantage does
not extend to this smaller-sample contrast. Variance's uncentered aggregate
means are especially variable: MCSE 0.150890 at $n=256$ and 12.294085 at
$n=2048$.

Five small training partitions have no green observations and thirteen
validation partitions have none. All test groups are nonempty. Rare selection
falls back to aggregate validation on those thirteen partitions; none is
removed. The results describe overlapping random partitions of one fixed dataset
of hypothetical mushroom descriptions, not population confidence intervals or
generalization to new species.

![Four-method Mushroom comparison at the largest
budget.](../results/variance-scaling-followup/selected-risks.png)

The [PDF figure](../results/variance-scaling-followup/selected-risks.pdf) shows
means on logarithmic axes. The summaries retain MCSEs, medians, 95th
percentiles, maxima, paired contrasts, and absence denominators rather than
presenting these means as precise population estimates.

## Synthetic comparisons

These tables retain every law at cap $M=2048$ in the centered/fitted arm,
aggregate validation, and original stops. Test risks integrate the four-cell
population exactly and exclude observation noise. Values are means over all 128
replications, including extreme finite selections.

  | Law                | None aggregate | SD aggregate | Damped aggregate | Variance aggregate |
  | ------------------ | -------------: | -----------: | ---------------: | -----------------: |
  | C1                 |        0.02603 |      7.373e4 |            25.79 |             0.1596 |
  | Rarer C1           |        0.02503 |     3.932e13 |         1.466e27 |           6.647e11 |
  | C2                 |        0.04214 |      3.420e9 |          2.395e7 |           8.370e14 |
  | Rarer C2           |        0.03345 |     3.527e28 |         5.270e16 |           3.453e27 |
  | Opposite, nested   |        0.03674 |       0.1428 |          0.04860 |              110.7 |
  | Opposite, disjoint |        0.04252 |      7.564e4 |            904.7 |           4.077e16 |
  | Rare only          |        0.01261 |      0.01618 |          0.01223 |            0.01065 |
  | Common only        |       0.007597 |      2.836e7 |            233.0 |            0.07023 |

  | Law                | None rare | SD rare  | Damped rare | Variance rare |
  | ------------------ | --------: | -------: | ----------: | ------------: |
  | C1                 |    0.3458 |  3.686e6 |        1288 |         7.007 |
  | Rarer C1           |    0.5107 | 1.966e16 |    7.332e29 |      3.323e14 |
  | C2                 |    0.4358 | 1.710e11 |     1.198e9 |      4.185e16 |
  | Rarer C2           |    0.5215 | 1.763e31 |    2.635e19 |      1.727e30 |
  | Opposite, nested   |    0.3994 |    5.873 |       1.138 |          5534 |
  | Opposite, disjoint |    0.4092 |  3.782e6 |     4.523e4 |      2.038e18 |
  | Rare only          |    0.2326 |   0.5892 |      0.3530 |        0.4122 |
  | Common only        |   0.05054 |  1.418e9 |     1.165e4 |         3.077 |

The huge means are dominated by a few selected paths, often with no rare
validation observations. They are not precise estimates of expected risk. For
example, variance scaling in rarer C2 has rare median 0.6836, mean
$1.727\times10^{30}$, MCSE $1.552\times10^{30}$, and maximum
$1.974\times10^{32}$. In C1 its rare median is 0.3826, mean 7.007, MCSE 4.246,
and maximum 474.125. For rare-only signal, the variance aggregate mean is
0.01065 (MCSE 0.00311), but its rare mean is 0.4122 (0.1467), versus 0.2326
(0.0319) for none. These comparisons do not imply that faster rare-coordinate
updates uniformly help prediction.

All five preprocessing arms, both validation objectives, the smaller caps,
nested practical searches, refined stops, and absence strata are retained in the
case summaries. Across the two expanded stopping searches there are 106
lower-edge decisions and 52 upper-edge decisions, counting repeated queries on
the same replications. The upper choices occur only for variance scaling with
known preprocessing in the two rarer anchor laws. They remain unresolved; the
Mushroom boundary result is not a statement about every synthetic arm.

Variance scaling's earlier lasso motivation concerns original-coordinate penalty
weights. Here the penalty is absent, and the active-coordinate SGD multiplier is
$\eta/v_j^2$, with a separately recalibrated scalar rate. Its relative learning
and stochastic stability tradeoffs require this direct comparison rather than an
inference from lasso shrinkage.

## Independent audit and numerical limits

The [audit](../results/variance-scaling-followup/audit.json) reconstructs all
6,451,200 endpoint losses and 387,072 selections, verifies preprocessing,
partitions, paired summaries, absence strata, neighbors, and work counts, and
replays 100,271 trajectories in explicit transformed coordinates. Replays cover
every selected path plus every candidate in replication zero of each law or
size. All overlapping practical and centered Mushroom sensitivity coefficient
paths reproduce exactly. Reconstructed losses differ by at most
$1.36\times10^{-14}$ in the audit's normwise measure and leave every selection
unchanged.

The declared trajectory and selected-prediction gates do **not** all pass. There
are 63 retained discrepancy records in twelve synthetic replications, all with
empty rare validation groups:

- Sixty selected-prediction checks exceed $10^{-8}$: 32 variance, 14 SD, and 14
  damped decisions, all in the centered/fitted arm. These count repeated choices
  across objectives, caps, and stopping searches, not sixty independent
  trajectories. The largest relative prediction discrepancy is 0.004184, for
  rarer C2, replication 17.
- In rarer C2, replication zero, two centered/fitted SD paths with $B=1$ cross
  the failure threshold at different updates. Factor 4.8 fails at update 198 in
  original coordinates versus 206 in transformed coordinates; factor 6.4 fails
  at 177 versus 179. That replication has no rare training or validation
  observations.
- The same replication has the largest normwise trajectory discrepancy,
  0.003747, exceeding $2\times10^{-9}$. Both implementations agree on the
  failure statuses at stored checkpoints. No selected reference endpoint is
  failed.

The trajectory measure divides coefficient discrepancies by one plus the largest
absolute reference coefficient at that endpoint. The prediction measure uses the
maximum validation-prediction difference divided by one plus the largest
absolute reference prediction. Small coefficient errors can be amplified when
large intercept and feature contributions cancel. These checks do not certify
the affected extreme synthetic paths; neither their precise risks nor their
selections are presented as independently verified in transformed arithmetic.
The earlier practical study's separate decimal investigation is preserved and is
not extended to these new candidates by assumption.

No Mushroom comparison violates either gate. The initial full audit stopped at
the first failure-time disagreement. Its checker was extended to retain those
times and any checkpoint-status disagreements alongside the predeclared
numerical gates, then all new artifacts were regenerated with the updated source
hash. Final review also added a regression check ensuring that a missing
rare-group loss cannot mask an aggregate-loss discrepancy in the norm
calculation. The grid, simulator, loss, selection rule, protocol, and
declaration were unchanged. The focused checker verifies the complete retained
discrepancy record; its successful structural audit does not mean all numerical
gates pass.

## Artifacts and reproduction

The [synthetic manifest](../results/variance-scaling-followup/synthetic.json)
and [Mushroom manifest](../results/variance-scaling-followup/mushroom.json)
record sources, versions, timing, candidates, queries, and archive hashes. There
are 136 path shards, each below 100 MiB. Summaries are split across ten law/size
JSON files; immediate-neighbor candidate IDs, validation scores, and failure
flags are stored in ten compressed arrays. The [artifact
index](../results/variance-scaling-followup/artifacts.json) records their
hashes. All original-scale coefficient paths, centered and raw intercepts,
divisors, curvatures, steps, streams, and Mushroom partitions are retained.
Selected-path continuations report missing denominators when they fail after the
selected stop.

Inside `devenv shell`, run `make reproduce-variance-scaling` or
`make check-variance-scaling`. The declaration preserves 179 earlier files,
including the locally regenerated robustness artifacts. The earlier covariance
gate violation, practical missing-group failures and decimal investigation, rate
search, and fixed-offset sensitivity remain unchanged.
