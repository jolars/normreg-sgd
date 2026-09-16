# Practical preprocessing and validation: results and limits

September 16, 2026. Execution of [protocol version 1](practical-selection.md).
This completes the practical experiment in [TODO.md](../TODO.md), not a theory
of estimated preprocessing or an optimizer recommendation.

## Assessment

Relative scaling still changes rare-feature learning with estimated centering,
scales, and an intercept. Its direction depends on signal, budget, and the
validation objective. In the sampled C1 law, the fixed-configuration SD
advantage at short budgets becomes a small, uncertain disadvantage at the
longest budget with practical preprocessing. The sparse categorical benchmark
retains a rare-subgroup advantage for SD scaling after equal-effort validation
selection, but aggregate performance can move in the opposite direction. Damped
scaling is also competitive. These findings concern the declared finite grid and
task.

The strongest practical limitation is **missing subgroup information**. Empty
training groups cannot acquire a fitted effect under the declared preprocessing
policy. Empty validation groups can hide an explosive rare-feature coefficient
even when validation loss is finite and competitive. An aggregate fallback makes
selection defined; it does not certify rare-subgroup performance. A noisy
validation subgroup can also favor a poorer aggregate predictor. We retain these
outcomes and do not retune the grid after seeing them.

## Execution and evidence

There are 1,024 synthetic replications across eight laws and 64 Mushroom
partitions across two sample sizes. The archives retain **637,440 endpoints**:
614,400 synthetic and 23,040 categorical, including initialization, duplicates
arising from shared initial predictors, and failed candidates. There are 318,720
recorded selection decisions, including fixed configurations, separate
objectives, budget caps, and the larger joint-scaling search. They are not
independent observations.

- [Synthetic manifest](../results/practical-selection/synthetic.json) and
  [archive](../results/practical-selection/synthetic.npz).
- [Mushroom manifest](../results/practical-selection/mushroom.json) and
  [archive](../results/practical-selection/mushroom.npz).
- [Complete summaries](../results/practical-selection/summary.json): all
  candidate curves, selected losses, paired contrasts, absence strata,
  distributions, coefficient contributions, and selection counts.
- [Figure](../results/practical-selection/practical-selection.svg) and
  [PDF](../results/practical-selection/practical-selection.pdf).
- [Precision
  investigation](../results/practical-selection/precision-audit.json).

All reported losses include the factor one half. Synthetic test loss is excess
prediction loss, integrated over the four population cells. Mushroom test loss
is observed-label prediction loss. Validation always uses observed labels,
without access to the synthetic truth or held-out test outcomes. Every estimated
mean, variance, vocabulary, curvature, and initialization uses training data
only. Checkpoints share a trajectory; neither validation nor test data are used
for a final refit.

Each scaling and preprocessing arm receives five rates and two batch sizes: ten
trajectories and nominal tuning work $10M$ at budget cap $M$, whether selection
chooses only rate/batch or also stopping. The joint-scaling procedure receives
30 trajectories and is reported separately. Fixed configuration work is $M$.
Preprocessing scans $n$ training records and calibrates 15 synthetic or nine
categorical Gram matrices per replication across all arms/scalings. Each
scaling/arm has ten endpoints to score at a positive checkpoint, plus the
duplicated initialization; scoring reads the declared validation set. Archives
record $M$, $k=M/B$, $n$, and selected absolute learning rates. This is equal
search effort, not identical effective learning or continuous optimization.

## Controlled samples: preprocessing and stopping

For the next two tables, the fixed configuration is $a=0.05$, $B=16$ under the
protocol's empirical curvature calibration. Entries are SD minus no scaling in
rare excess half squared loss, with paired MCSE in parentheses. Negative values
favor SD. These use sampled, reused datasets and a different calibration from
the fresh-sample C1/C2 theorems; the law names identify their signals and
feature distributions, not a replication of the theorem's exact configurations.

  | Law | Preprocessing              | $M=128$          | $M=512$          | $M=2048$        |
  | --- | -------------------------- | ---------------: | ---------------: | --------------: |
  | C1  | Known                      | -0.1144 (0.0182) | -0.0730 (0.0341) | 0.1653 (0.0497) |
  | C1  | Centered, fitted intercept | -0.1653 (0.0295) | -0.1485 (0.0485) | 0.0901 (0.0697) |
  | C2  | Known                      | -0.4594 (0.0365) | -0.1937 (0.0448) | 0.2896 (0.0634) |
  | C2  | Centered, fitted intercept | -1.0050 (0.0458) | -0.9398 (0.0573) | 0.0571 (0.0773) |

Thus the early rare-learning advantage remains observable, but the positive
long-budget contrasts under fitted intercepts are within two MCSE of zero. They
do not establish a reliable practical reversal. At $M=128$, the known C2 arm has
aggregate contrast $+0.02566$ (0.00295) and rare contrast $-0.45937$ (0.03651).
Under estimated centering and a fitted intercept, the aggregate contrast becomes
$-0.18439$ (0.00238): that particular objective disagreement disappears.
Intercept handling materially changes the comparison.

The complete set of fixed-configuration rare contrasts at $M=2048$ is:

  | Law                | Known            | Estimated scales | Centered, fixed intercept | Centered, fitted intercept | Uncentered, fitted intercept |
  | ------------------ | ---------------: | ---------------: | ------------------------: | -------------------------: | ---------------------------: |
  | C1                 |  0.1653 (0.0497) |  0.1931 (0.0556) |           0.2192 (0.0650) |            0.0901 (0.0697) |              0.0242 (0.0594) |
  | Rarer C1           |  0.3794 (0.0996) |  0.3214 (0.0928) |           0.3180 (0.0964) |            0.2904 (0.0932) |              0.2119 (0.0795) |
  | C2                 |  0.2896 (0.0634) |  0.3526 (0.0743) |           0.3549 (0.0763) |            0.0571 (0.0773) |             -0.2484 (0.0568) |
  | Rarer C2           |  0.7664 (0.1545) |  0.5368 (0.1503) |           0.5290 (0.1527) |            0.2971 (0.1493) |              0.1283 (0.1246) |
  | Opposite, nested   |  0.2480 (0.0794) |  0.2726 (0.0818) |           0.2856 (0.0855) |            0.3280 (0.0905) |              0.2453 (0.0725) |
  | Opposite, disjoint |  0.3459 (0.0588) |  0.4343 (0.0769) |           0.4258 (0.0745) |            0.1513 (0.0813) |             -0.3748 (0.0561) |
  | Rare only          | -0.0566 (0.0229) | -0.0473 (0.0243) |          -0.0527 (0.0243) |           -0.2320 (0.0233) |             -0.2855 (0.0203) |
  | Common only        |  0.1130 (0.0135) |  0.1184 (0.0140) |           0.1188 (0.0149) |            0.1272 (0.0159) |              0.1059 (0.0143) |

The rare-only versus common-only contrast supports the allocation-of-learning
interpretation under every preprocessing arm. Original-scale paths, rather than
only selected endpoints, are retained. Changing centering also changes the
feature/intercept geometry, curvature calibration, and starting predictor. The
estimated-scale arm holds the population centering and intercept fixed, whereas
the practical arms include the uncertainty of the training response mean. These
are explicit ablations, not an additive attribution of risk differences to four
independent causes.

## Absence, validation, and failures

  | Law/task           | Replications | No rare training data | No rare validation data | Failed candidate endpoints |
  | ------------------ | -----------: | --------------------: | ----------------------: | -------------------------: |
  | C1                 |          128 |                     3 |                      13 |                         30 |
  | Rarer C1           |          128 |                    75 |                     106 |                          0 |
  | C2                 |          128 |                     2 |                      11 |                          6 |
  | Rarer C2           |          128 |                    70 |                     105 |                          0 |
  | Opposite, nested   |          128 |                     1 |                      11 |                         30 |
  | Opposite, disjoint |          128 |                     0 |                       9 |                         37 |
  | Rare only          |          128 |                     1 |                       6 |                         42 |
  | Common only        |          128 |                     1 |                      10 |                          6 |
  | Mushroom, $n=256$  |           32 |                     5 |                      13 |                          0 |
  | Mushroom, $n=2048$ |           32 |                     0 |                       0 |                          0 |

All estimated arms freeze constant columns at coefficient zero; a divisor of one
avoids division by zero. Unknown test categories have zero one-hot blocks. The
known arm can update an absent, population-centered feature, which is a
different information assumption. No subgroup test loss is missing in this run.
For empirical preprocessing with no rare training data, prediction can still use
other covariates and an intercept, but it cannot estimate the absent dummy's
effect. On Mushroom's five absent-training splits, aggregate-selected rare loss
is 0.49555 (0.02255) without scaling and 0.42954 (0.00630) with SD scaling.
Those losses are far above the all-split averages below.

At $q=0.002$, 106/128 and 105/128 validation sets have no rare observations. The
protocol falls back to aggregate validation in precisely those replications.
This does not protect against an unstable coefficient on a feature present in
training but absent in validation. For example, in rarer C2 replication 52,
training contains one rare observation and validation contains none. Joint
aggregate selection in the centered/fitted SD arm chooses $B=1$, $a=0.2$,
$M=2048$. Its rare coefficient is about $-6.719\times10^{16}$, yet validation
half squared loss is about 2.086. Exact-cell rare loss is about
$2.257\times10^{33}$. This candidate is finite under the declared failure
threshold and must not be discarded after observing its test error.

Consequently, means and MCSEs in several unrestricted synthetic selection panels
are dominated by individual explosive paths. The complete summary also reports
medians, 95th percentiles, maxima, and validation-absence strata. These tails
are evidence of a failure mode, not precise estimates of population expected
risk. For comparison, the centered/fitted C1 SD arm with aggregate joint
selection has rare loss 0.44927 (0.07909) among the 115 replications with rare
validation observations, versus roughly 32,155 (32,153) among the 13 without
them. The corresponding no-scaling values are 0.32141 (0.02278) and 0.52499
(0.15009). Presence of a few rare validation observations also does not
guarantee a useful selection rule: their labels are noisy, and the subgroup
objective may spend common-prediction accuracy to fit that noise.

The 151 failed synthetic endpoints remain in the archives, with a failure flag
and missing coefficients/losses. Failed candidates cannot win validation
selection. The archive distinguishes an initialization fallback after every
eligible endpoint fails from a fallback because validation has no rare cases. No
selection in this run needed the all-failed initialization fallback. Finite-only
candidate summaries explicitly record their missing counts and aggregation
convention; they are not complete unconditional path averages.

### Numerical investigation

The explicit transformed-design checker compares complete coefficient vectors on
the scale of their norm. Divergent vectors can contain small coordinates formed
by cancellation, so a coordinatewise relative test alone is not a useful
accuracy criterion there. Selected extreme paths require a further check because
small raw intercept errors can affect validation loss on the common group.

The separate precision investigation is **post hoc** and changes no primary
result. For each of the eight laws and three scaling rules, take the worst rare
test loss among the centered/fitted, aggregate-joint-selected replications.
Replay all ten competing trajectories at 160-digit decimal precision on the same
stored float64 input constants, including every eligible stopping checkpoint.
The artifact records selection changes, refined validation margins, coefficient
and prediction discrepancies, and rare risks. This bounded diagnostic does not
certify every unstable trajectory or cure validation's lack of rare
observations.

All **24 selections are unchanged** in this replay. The largest validation
prediction discrepancy is 0.000746, in rarer C2 replication 52 above. Its
refined validation loss is 2.086114 and its winning margin is 0.040412, while
its rare loss remains $2.257\times10^{33}$. Thus this catastrophic selection is
not explained by the detected cancellation. The full-path normwise comparison
over replication zero of all laws and sizes has maximum discrepancy
$9.08\times10^{-14}$ under the checker normalization $1+\|\beta\|_\infty$,
including the raw intercept in the vector.

## Sparse categorical evaluation

The task is squared-loss prediction of the recorded poisonous label in [UCI
Mushroom](https://archive.ics.uci.edu/dataset/73/mushroom), with green spore
prints defining the rare subgroup. There are 72 such records among 8,124
(0.886%). There are no duplicate predictor rows. Encoding uses only training
categories, includes missingness as a category, and stores the design as CSR.
The training vocabularies contain 98--117 dummy columns across the 64 splits.
Neither a label nor a test category is used to fit preprocessing. The source
files, attribution, checksum, and all partition indices are retained.

The following table includes all three scaling rules and both validation
objectives for the primary centered/fitted arm, joint rate/batch/stopping
selection, and cap $M=8192$. Entries are test half squared loss (MCSE).

  | Training / validation size | Selection objective | Scaling | Aggregate           | Green-spore subgroup |
  | -------------------------- | ------------------- | ------- | ------------------: | -------------------: |
  | 256 / 128                  | Aggregate           | None    |   0.00515 (0.00035) |    0.10272 (0.03092) |
  | 256 / 128                  | Aggregate           | SD      |   0.00475 (0.00081) |    0.07493 (0.02762) |
  | 256 / 128                  | Aggregate           | Damped  |   0.00401 (0.00032) |    0.07927 (0.02777) |
  | 256 / 128                  | Rare                | None    |   0.02007 (0.00713) |    0.06832 (0.02001) |
  | 256 / 128                  | Rare                | SD      |   0.01622 (0.00634) |    0.04778 (0.01933) |
  | 256 / 128                  | Rare                | Damped  |   0.01943 (0.00678) |    0.05001 (0.01916) |
  | 2048 / 1024                | Aggregate           | None    | 0.001754 (0.000060) |  0.012482 (0.001386) |
  | 2048 / 1024                | Aggregate           | SD      | 0.004617 (0.002125) |  0.005912 (0.001054) |
  | 2048 / 1024                | Aggregate           | Damped  | 0.001175 (0.000034) |  0.004151 (0.000465) |
  | 2048 / 1024                | Rare                | None    | 0.001878 (0.000130) |  0.012465 (0.001382) |
  | 2048 / 1024                | Rare                | SD      |   0.123905 (0.0755) |  0.003158 (0.000451) |
  | 2048 / 1024                | Rare                | Damped  |  0.014966 (0.00915) |  0.003984 (0.000495) |

Pairing matters. Under aggregate selection, SD minus no scaling in rare loss is
$-0.02779$ (paired MCSE 0.00648) at $n=256$ and $-0.00657$ (0.00153) at
$n=2048$. For the larger sample, the aggregate contrast is $+0.002863$
(0.00213), a noisy disadvantage. Switching the SD validation objective from
aggregate to rare reduces rare loss by 0.002754 (0.000967) but increases
aggregate loss by 0.11929 (0.0756). The direction of that tradeoff is visible,
but the aggregate penalty is highly variable. Damped scaling with aggregate
selection has smaller observed mean loss than SD under both objectives at the
larger sample size; this is not a universal ranking.

For SD with rare-objective selection at the larger size, the aggregate-loss
median is 0.00222 and the maximum is 2.36513, compared with the mean 0.12390.
Thus the large mean penalty includes an extreme partition outcome; it does not
describe a typical split. All partitions remain in the reported mean and MCSE.

Fixed stopping differs substantially from selection. At $n=2048$, the fixed
$a=0.05$, $B=16$, $M=8192$ rare losses are 0.19071 without scaling, 0.01370 with
SD, and 0.02725 with damping. Joint aggregate selection reduces these to
0.01248, 0.00591, and 0.00415. Thus selection greatly reduces the raw fixed-step
advantage, while an SD-versus-none rare difference remains within this grid. All
shorter caps, rate/batch-only selection, fixed intercepts, uncentered fits, and
the larger joint-scaling search remain in the complete summary.

The coefficients give a feature-level explanation without asserting unique or
causal effects in a rank-deficient one-hot design. At $n=2048$ under aggregate
selection, the average original-scale green coefficient is 0.48216 without
scaling, 0.74618 with SD, and 0.76784 with damping. Their mean centered green
contributions on the subgroup are 0.47788, 0.73962, and 0.76106. The remaining
feature contributions average -0.08611, -0.28014, and -0.29242, respectively;
the centered intercept is about 0.484. These components sum to the subgroup's
mean prediction. Faster learning of the rare dummy is partly offset by the other
categorical features. Coefficient paths, shifts, divisors, and intercepts are
saved on the original feature scale for every endpoint.

The finite grid is a material limit. All 32 no-scaling aggregate selections at
the larger size use the maximum rate factor 0.8, as do 31/32 at the smaller
size. This is equal effort without evidence of equally resolved optima. No
post-result rate expansion is included. For the smaller sample, 13/32 subgroup
validation rules fall back to aggregate loss. Missing green training categories
and other unknown test levels remain flagged, not silently removed.

## Interpretation and reproduction

The study answers the practical milestone in a bounded sense: normalization
still affects rare-feature learning under estimated preprocessing, and separate
aggregate/subgroup validation objectives lead to consequential differences on
one sparse linear-model task. The original controlled orderings do not all
survive, and an unguarded validation search can fail badly when the rare group
is missing. The evidence supports checking subgroup coverage, retained paths,
and both objectives in this setting. It does not support choosing SD, damping,
or no scaling universally.

Synthetic MCSE includes training-design, label, validation, and optimization
randomness; test integration is exact. Mushroom MCSE describes random partition
and optimization variation conditional on this fixed dataset, not a confidence
interval for a new population or a new species. These hypothetical field-guide
records are a reproducible categorical benchmark, not independent field data.
There are no multiple-comparison guarantees, nested tuning of preprocessing
choices, continuous-rate guarantees, or adaptive-optimizer/neural claims.

Reproduce offline inside `devenv shell`:

```sh
make reproduce-practical-selection
make check
```

GNU make reads `GNUmakefile`, which includes the original `Makefile` and adds
the new targets and integrated check. This preserves the original file's hash in
the preceding robustness study.

`make check-practical-selection` independently checks transformed-coordinate
paths, dense/sparse agreement, intercepts, training-only preprocessing, absent
and unknown categories, tie/failure rules, all archived validation and test
losses, every selection, and all selected-loss means, absence strata, paired
contrasts, and MCSEs. Full paths are replayed for replication zero of every law
and sample size. Source, input, archive, summary, figure, and preserved-study
hashes are checked. Earlier studies, including the robustness covariance gate
violation and its conditional-absence investigation, remain unchanged against
commit `a774192`.

Validation completed with `make reproduce-practical-selection` and the full
`make check` inside `devenv shell`. The latter also verified the preceding
studies, formatting, configuration, numerical baselines, and manuscript build.
