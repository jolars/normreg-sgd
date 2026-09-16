# Mushroom rate expansion: results and limits

September 16, 2026. Execution of the separately declared [rate-search
protocol](mushroom-rate-search.md). The [original practical
study](practical-selection-results.md), including its boundary selections and
precision investigation, remains unchanged.

## What the expanded comparison resolves

The large-sample unscaled aggregate search no longer selects its upper rate
boundary. At $n=2048$ and cap $M=8192$, all 32 primary-arm selections use
interior factors between 0.6 and 1.8. Every selection has a strictly worse
validation score at its immediate higher tested factor, with the same batch and
stop. This resolves the original boundary at 0.8 **within this declared grid**.
It does not identify a continuous optimum.

The previous SD advantage in rare-subgroup loss under aggregate selection is
mostly removed. Its paired contrast against no scaling changes from $-0.006570$
(MCSE $0.001526$) to $-0.001192$ ($0.001318$). The expanded contrast is within
two MCSE of zero, so the original advantage disappears under the protocol's
descriptive convention. This is not evidence of equivalence. With finer stopping
choices it is $-0.000597$ ($0.001204$).

Other effects persist. Damping improves both aggregate and rare loss under
aggregate selection at both sample sizes. SD retains a rare-loss advantage under
aggregate selection at $n=256$, at shorter large-sample budgets, and under
rare-objective selection at $n=2048$. Relative coefficient learning also remains
different after retuning. These are conditional findings on one dataset, not a
universal ranking of normalization methods.

The secondary uncentered, rare-objective search still has upper-edge selections
when additional early stopping checkpoints are allowed. Missing subgroup
coverage and highly variable aggregate losses under rare selection also remain
unresolved. The full report retains them.

## Search, effort, and evidence

The experiment reuses the frozen 32 partitions at each of two sample sizes, the
same training-only one-hot vocabularies, and the same replacement index streams.
The three scaling rules and three preprocessing/intercept arms are unchanged.
The primary arm centers predictors and fits an intercept initialized at the
training response mean. We compare 17 curvature-normalized rate factors from
0.001 through 6.4, including all five original factors, and batches 16 and 128.
The primary expansion keeps the old stopping checkpoints. A separate secondary
search adds 128, 256, 1024, and 4096 observations as stopping options.

Each scaling/arm receives 34 trajectories, versus ten in the original grid. At
cap 8192 this is nominally 278,528 processed observations per scaling/arm,
versus 81,920 before expansion. Comparison across scaling rules has equal
nominal effort within each search; comparison against the original search has
3.4 times the tuning work. Fixed-configuration work remains 8192. At the largest
cap, joint selection scores 136 endpoints per scaling/arm on the expanded grid,
or 272 with extra stops, including duplicated initialization. Rate/batch-only
selection scores 34 endpoints. Scoring both objectives shares all training fits.

There are **156,672 archived endpoints and 20,736 selection decisions** across
64 replications. These include all arms, scalings, batches, rates, checkpoints,
both validation objectives, and budget caps 512, 2048, and 8192. Endpoint and
selection counts include shared initializations and dependent comparisons.
Nominal total training work is 160,432,128 processed observations. First-failure
updates record the work spent on each live trajectory. For the large-sample
primary arm, average live work per expanded scaling/arm at cap 8192 is 264,354.5
for none, 263,728 for SD, and 264,237 for damping. The vectorized implementation
still carries zeroed inactive slots, so these counts are not a wall-clock
accounting of the arithmetic saved. Training preprocessing scans $n$ records and
calibrates nine Gram matrices per split, outside this budget.

- [Declaration](../results/mushroom-rate-search/declaration.json): protocol and
  specification hashes recorded before the new experiment, with preserved inputs
  anchored at commit `7c6d331`.
- [Manifest](../results/mushroom-rate-search/manifest.json): configurations,
  candidate and query indices, sample metadata, source hashes, and eight path
  archives. Each archive contains eight replications, including every
  original-scale coefficient, loss, partition, preprocessing parameter, and
  first-failure update.
- [Complete summary](../results/mushroom-rate-search/summary.json): all paired
  contrasts, absence strata, candidate curves, selected trajectories,
  coefficient contributions, rate neighbors, boundary counts, and tuning costs.
- [Selected endpoint figure](../results/mushroom-rate-search/selected-risks.svg)
  and [PDF](../results/mushroom-rate-search/selected-risks.pdf).
- [Artifact hashes](../results/mushroom-rate-search/artifacts.json).

All losses below are observed-label half squared prediction losses. No test
label enters selection, curvature calibration, or the boundary diagnostic. Test
observations are never counted as training work. MCSE describes random-partition
and optimizer variation conditional on this fixed dataset, not uncertainty about
new species or a population of tasks. This is a follow-up informed by the
original boundary, not an independent confirmation on fresh data.

## Selected endpoints and paired comparisons

The expanded search with the original stopping checkpoints gives the following
results at cap $M=8192$. Entries are test loss (MCSE) in the primary arm; all 32
partitions per size remain in each mean.

  | Training / validation | Selection | Scaling | Aggregate           | Green-spore subgroup |
  | --------------------- | --------- | ------- | ------------------: | -------------------: |
  | 256 / 128             | Aggregate | None    | 0.004752 (0.000356) |  0.098799 (0.032694) |
  | 256 / 128             | Aggregate | SD      | 0.004647 (0.000814) |  0.076035 (0.028437) |
  | 256 / 128             | Aggregate | Damped  | 0.003568 (0.000337) |  0.078161 (0.028979) |
  | 256 / 128             | Rare      | None    | 0.160600 (0.059375) |  0.065839 (0.024700) |
  | 256 / 128             | Rare      | SD      | 0.203718 (0.114109) |  0.041942 (0.019786) |
  | 256 / 128             | Rare      | Damped  | 0.125706 (0.087346) |  0.041806 (0.020859) |
  | 2048 / 1024           | Aggregate | None    | 0.001341 (0.000074) |  0.005955 (0.000888) |
  | 2048 / 1024           | Aggregate | SD      | 0.004476 (0.001498) |  0.004764 (0.001079) |
  | 2048 / 1024           | Aggregate | Damped  | 0.000810 (0.000039) |  0.000682 (0.000133) |
  | 2048 / 1024           | Rare      | None    | 0.039395 (0.017807) |  0.003678 (0.000334) |
  | 2048 / 1024           | Rare      | SD      | 0.141068 (0.079208) |  0.002257 (0.000419) |
  | 2048 / 1024           | Rare      | Damped  | 0.002611 (0.000958) |  0.000499 (0.000112) |

Rate expansion changes the unscaled large-sample aggregate-selected predictor
substantially: its aggregate loss falls by 0.000413 (paired MCSE 0.000042), and
its rare loss falls by 0.006527 (0.001017). SD's corresponding rare improvement
is 0.001149 (0.000336), while damping improves by 0.003469 (0.000369). Thus the
reduced SD-versus-none gap is not caused by discarding SD candidates. Every
original candidate remains eligible, and selection uses validation only. A
nested candidate family improves the winning validation score, not necessarily
the held-out score.

The next table isolates the rare-loss contrasts. Negative values favor the
listed scaling over none. The two-MCSE descriptions follow the declared
convention; they are not equivalence tests or simultaneous confidence claims.

  | $n$  | Selection | Scaling | Original gap (paired MCSE) | Expanded gap (paired MCSE) | Expanded with extra stops | Assessment                      |
  | ---: | --------- | ------- | -------------------------: | -------------------------: | ------------------------: | ------------------------------- |
  |  256 | Aggregate | SD      |       -0.027793 (0.006479) |       -0.022763 (0.007829) |      -0.020067 (0.005373) | Persists                        |
  |  256 | Aggregate | Damped  |       -0.023451 (0.006277) |       -0.020637 (0.007882) |      -0.018331 (0.005449) | Persists                        |
  |  256 | Rare      | SD      |       -0.020538 (0.005816) |       -0.023897 (0.014940) |      -0.002463 (0.006956) | Within two MCSE after expansion |
  |  256 | Rare      | Damped  |       -0.018312 (0.005436) |       -0.024033 (0.014674) |      -0.003186 (0.005178) | Within two MCSE after expansion |
  | 2048 | Aggregate | SD      |       -0.006570 (0.001526) |       -0.001192 (0.001318) |      -0.000597 (0.001204) | Original advantage disappears   |
  | 2048 | Aggregate | Damped  |       -0.008331 (0.001158) |       -0.005273 (0.000797) |      -0.004649 (0.000519) | Persists                        |
  | 2048 | Rare      | SD      |       -0.009307 (0.001315) |       -0.001421 (0.000470) |      -0.001309 (0.000342) | Persists, much smaller          |
  | 2048 | Rare      | Damped  |       -0.008481 (0.001122) |       -0.003179 (0.000312) |      -0.002730 (0.000298) | Persists                        |

Under aggregate selection at $n=2048$, SD's aggregate disadvantage is 0.003134
(0.001495), just over two MCSE. Its mean is sensitive to large partition
outcomes: median aggregate loss is 0.001776 and maximum loss is 0.041117,
compared with the mean 0.004476. Damping has aggregate contrast -0.000532
(0.000056). At $n=256$, SD's aggregate contrast is -0.000106 (0.000843), while
damping's is -0.001184 (0.000217). Thus removing the main SD rare-loss advantage
does not remove all normalization effects.

Switching validation objectives can still exchange aggregate accuracy for rare
accuracy. At the larger size, the rare-minus-aggregate selection contrasts are:

  | Scaling | Aggregate change (paired MCSE) | Rare change (paired MCSE) |
  | ------- | -----------------------------: | ------------------------: |
  | None    |           +0.038054 (0.017818) |      -0.002278 (0.000828) |
  | SD      |           +0.136592 (0.079298) |      -0.002507 (0.000951) |
  | Damped  |           +0.001802 (0.000953) |      -0.000183 (0.000074) |

The SD aggregate penalty remains highly variable, with rare-selected median
0.004357 and maximum 2.365130. For none, these are 0.002703 and 0.509963.
Neither mean describes a typical partition. Adding stopping checkpoints raises
the large-sample rare-selected aggregate means to 0.080405 for none and 0.244480
for SD, while lowering their rare means to 0.003148 and 0.001839. The
corresponding damped means are 0.002063 and 0.000418. More validation choices do
not guarantee better held-out aggregate performance.

## Paths, rates, and remaining boundaries

The original-scale trajectories explain how unscaled learning catches up without
making the three fitted predictors identical. Under large-sample aggregate
selection, the green coefficient for none increases from an original-grid mean
of 0.48216 to 0.59990; SD increases from 0.74618 to 0.77633, and damping from
0.76784 to 0.91262. The expanded means decompose as follows:

  | Scaling | Green coefficient | Centered green contribution | Other subgroup contribution | Centered intercept | Mean absolute $\eta$ |
  | ------- | ----------------: | --------------------------: | --------------------------: | -----------------: | -------------------: |
  | None    |           0.59990 |                     0.59460 |                    -0.14755 |            0.48469 |              0.74989 |
  | SD      |           0.77633 |                     0.76948 |                    -0.30233 |            0.48467 |              0.08029 |
  | Damped  |           0.91262 |                     0.90456 |                    -0.40205 |            0.48475 |              0.05185 |

The last three prediction components sum to the mean rare-group prediction.
Other categorical coefficients offset much of the larger green contribution.
These are optimizer-dependent coordinates in a rank-deficient design, not
uniquely identified effects. Raw intercepts and every original-scale coefficient
are archived, including failed-path masks and unseen-category flags.

The path figures pair aggregate and rare risks with the green coefficient,
centered intercept, and feature contributions:

- $n=256$: [aggregate
  selection](../results/mushroom-rate-search/paths-n256-aggregate.svg) and [rare
  selection](../results/mushroom-rate-search/paths-n256-rare.svg).
- $n=2048$: [aggregate
  selection](../results/mushroom-rate-search/paths-n2048-aggregate.svg) and
  [rare selection](../results/mushroom-rate-search/paths-n2048-rare.svg).

Dotted curves use original-grid selected rates and batches; solid curves use
expanded-grid choices. Crosses and circles at the separate right-hand position
show the corresponding selected endpoints. This position is not a later budget.
Curves follow the chosen trajectory beyond its selected stop for description
only. Risk axes are logarithmic; coefficient/contribution axes use a symmetric
logarithmic scale with a linear region within 0.1 of zero. Means on a candidate
curve with failures explicitly carry missing counts in the complete summary.

At the main large-sample comparison, all unscaled aggregate selections use
$B=16$ and $M=8192$. Their rate histogram is 0.6: 1, 0.8: 1, 1.0: 3, 1.2: 3,
1.4: 7, 1.6: 11, and 1.8: 6. The immediate higher-rate validation gap is
strictly positive for all 32, with minimum $9.57\times10^{-7}$. SD selects
$B=128$ in 27/32 partitions and $B=16$ in five, while damping selects $B=16$
throughout, split equally between factors 0.4 and 0.6. All three scalings stop
at 8192 in this comparison. Matching processed observations therefore compares
512 updates for $B=16$ with 64 for $B=128$.

The boundary claim has limits. Among the 10,368 expanded-search decisions, 49
choose the upper rate 6.4. All 49 belong to the secondary `uncentered_fitted`,
rare-objective, extra-stopping search; counts include the same partition under
several caps. Its early uncentered comparisons remain unresolved at the upper
edge. There are also 90 positive-budget lower-edge choices and 69 initialization
choices, counted separately. No selection needs the all-failed fallback. All
histograms and individual neighbor diagnostics are retained. Interior choices
resolve a finite-grid boundary, not rate-grid resolution, a continuous optimum,
or the need for additional training time.

## Secondary budgets, intercepts, and failures

The disappearing large-sample SD advantage is specific to the longest budget and
centered arms. With aggregate selection in the primary arm, SD-minus-none rare
gaps at caps 512 and 2048 are -0.072857 (MCSE 0.011815) and -0.012679
(0.004061). Damping's gaps are -0.107374 (0.010210) and -0.024331 (0.003553).
Relative scaling still accelerates early rare learning under the expanded
search.

At cap 8192 with a centered, fixed intercept, the large-sample SD rare gap is
-0.000925 (0.001250), again within two MCSE, while damping's is -0.004995
(0.000685). With an uncentered, fitted intercept and the original stopping
checkpoints, the SD gap is -0.038224 (0.004383), and damping's is -0.036247
(0.004106). Thus the primary result cannot be generalized to uncentered
training. Both objectives, both selection rules, all caps, and all absence
strata for every arm are in the complete summary.

Numerical failures are retained: 901 small-sample and 897 large-sample paths
cross the declared threshold, producing 1477 and 1473 failed saved endpoints.
The 2950 failed endpoints are stored with flags and missing coefficients/losses;
their candidates receive infinite validation loss. Extreme finite candidates
remain eligible and are not removed using held-out errors. Expanding the search
does not imply that all candidates are stable.

The five small-sample training partitions with no green category still cannot
learn that dummy's coefficient. Under expanded aggregate selection their rare
losses average 0.51233 for none, 0.43994 for SD, and 0.44841 for damping, far
above the all-partition averages. Thirteen of the 32 validation partitions have
no green observations, so every rare-objective procedure uses its flagged
aggregate fallback on those same partitions. No test subgroup is empty. The
larger size has neither training nor validation absence. All original missing
group failures and the synthetic decimal investigation remain preserved.

## Reproduction and audit

Run offline inside `devenv shell`:

```sh
make reproduce-mushroom-rate-search
make check
```

The first target verifies the pre-execution declaration, runs all fits,
summarizes every declared comparison, creates SVG/PDF figures, and audits the
artifacts. The focused audit is `make check-mushroom-rate-search`; it also runs
in integrated validation. The runner uses the locked Python environment and one
OpenBLAS thread. Its manifest records software versions, architecture, and
elapsed time. The final run used Python 3.13.15, NumPy 2.5.3, and SciPy 1.18.1.
The host is an x86-64 AMD Ryzen 9 7900 with 12 cores and 24 logical CPUs; this
run uses one OpenBLAS thread and no GPU. Runtime is implementation-specific, not
a matched wall-clock comparison between scaling rules.

During the audit, recovering centered intercepts from large raw coefficients
exposed cancellation on divergent, unselected paths. The runner now records the
centered intercept state directly. A regression check verifies that fixed
intercepts stay fixed even when reconstructing them from raw coordinates loses
precision. This changes the path diagnostics, not training updates, candidate
eligibility, or the selected predictors. The original practical study is not
modified. Raw-prediction and selected-prediction checks remain separate from the
normwise trajectory check.

The independent checker reconstructs all training, validation, and test losses,
all selections, paired means/MCSEs, coefficient contributions, selected paths,
failure counts, rate neighbors, and tuning-work summaries. It replays every
trajectory for replication zero of both sizes and every selected trajectory for
the remaining splits in explicitly transformed coordinates. It also compares
selected validation predictions and checks original-grid paths and choices
against the frozen archive. Protocol, source, input, archive, summary, figure,
and preservation hashes are checked. Numerical checking does not replace human
review of the experimental interpretation.

The focused reproduction and audit pass. The maximum normwise trajectory
discrepancy is $9.01\times10^{-13}$, and the maximum selected-validation
prediction discrepancy is $5.93\times10^{-14}$, below the declared
$10^{-8}(1+|\widehat y|)$ gate. The revised manuscript builds with six pages of
main text; the new table and figure layouts have been visually inspected. The
full `make check` also passes, including the frozen practical study, earlier
optimization and robustness checks, formatting, configuration, numerical
baselines, and manuscript build. All 73 baseline files in the declaration retain
their hashes.
