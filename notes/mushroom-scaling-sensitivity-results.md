# Mushroom damping and variance-scaling results

The main damping advantage is not specific to exactly 0.01, but it is not
uniform over the entire declared grid either. At the largest sample and budget,
aggregate validation gives resolved improvements over no scaling in both risks
at the tested offsets 0.003, 0.01, 0.03, and 0.1. At 0.001, only the rare-risk
improvement is resolved. The original offset remains a prespecified heuristic;
these results do not select an optimal damping level.

## Declared comparison and validation

The [protocol](mushroom-scaling-sensitivity.md) compares eight fixed rules in
the primary centered, fitted-intercept arm. Each receives 17 rate factors, two
batches, both validation objectives, and the original and refined stopping
searches. All 32 existing partitions at each training size are retained. No test
result selects a damping level or changes the grid. The five positive offsets
together receive five times the work of one fixed rule.

The [declaration](../results/mushroom-scaling-sensitivity/declaration.json)
freezes the protocol and specification before execution. The
[manifest](../results/mushroom-scaling-sensitivity/manifest.json) records
sources, archives, versions, and timing. All 102 preserved files retain their
baseline hashes. The three overlapping methods reproduce the frozen rate-search
paths and choices.

There are 139,264 saved endpoints and 6,144 selection decisions. All 1,501
failed paths and 2,403 failed saved endpoints remain archived. The independent
audit reconstructs losses, choices, paired summaries, coefficient contributions,
paths, and work counts. It replays every selected path and every path in
replication zero at each size in transformed coordinates. Maximum normwise
trajectory discrepancy is $1.61\times10^{-12}$, and maximum selected validation
prediction discrepancy is $1.47\times10^{-13}$, below the declared gates.

Reproduce with `make reproduce-mushroom-sensitivity` and audit with
`make check-mushroom-sensitivity` inside `devenv shell`.

## Primary large-sample comparison

These are held-out half squared losses at $n=2048$, with 1,024 validation
records, cap $M=8192$, aggregate validation, and the original stopping
checkpoints. Parentheses contain MCSE across the 32 paired splits.

  | Rule         | Aggregate loss      | Rare-group loss     |
  | ------------ | ------------------: | ------------------: |
  | None         | 0.001341 (0.000074) | 0.005955 (0.000888) |
  | SD, $\tau=0$ | 0.004476 (0.001498) | 0.004764 (0.001079) |
  | Variance     | 0.311988 (0.201772) | 0.051586 (0.008319) |
  | $\tau=0.001$ | 0.001282 (0.000054) | 0.001543 (0.000323) |
  | $\tau=0.003$ | 0.001075 (0.000031) | 0.001149 (0.000165) |
  | $\tau=0.01$  | 0.000810 (0.000039) | 0.000682 (0.000133) |
  | $\tau=0.03$  | 0.000727 (0.000044) | 0.000911 (0.000277) |
  | $\tau=0.1$   | 0.000812 (0.000053) | 0.001858 (0.000525) |

Paired damped-minus-none differences make the uncertainty in the comparison
explicit:

  | Offset | Aggregate difference | Rare-group difference |
  | ------ | -------------------: | --------------------: |
  | 0.001  | -0.000059 (0.000069) |  -0.004412 (0.000857) |
  | 0.003  | -0.000266 (0.000067) |  -0.004806 (0.000816) |
  | 0.01   | -0.000532 (0.000056) |  -0.005273 (0.000797) |
  | 0.03   | -0.000614 (0.000048) |  -0.005044 (0.000668) |
  | 0.1    | -0.000530 (0.000037) |  -0.004097 (0.000521) |

The strict predeclared criterion for both benefits at **every** positive offset
is therefore not met. Four tested offsets from 0.003 through 0.1 retain both
differences beyond two MCSE; that statement does not cover every intervening
offset. Adding intermediate stopping checkpoints preserves this conclusion. At
the shorter large-sample caps 512 and 2048, all five positive offsets retain
both improvements over none under aggregate validation.

Offset 0.03 has lower aggregate loss than 0.01 by 0.000083 (paired MCSE
0.000019). Its rare loss is higher by 0.000229 (0.000197), an unresolved
difference. Offset 0.1 has a resolved rare-loss disadvantage relative to 0.01,
0.001177 (0.000447). Reporting these contrasts does not authorize choosing an
offset from the test outcomes.

The mean original-scale green coefficients are 0.5999, 0.7763, and 0.2954 for
none, SD, and variance scaling. For increasing positive offsets they are 0.8496,
0.8686, 0.9126, 0.8991, and 0.8218. Other-feature contributions offset part of
the green contribution; these coefficients are not unique or causal effects.
Full selected paths and contribution summaries are retained in the
[summary](../results/mushroom-scaling-sensitivity/summary.json). Every selected
endpoint has a finite test loss. One small-sample, rare-selected variance path
fails when continued to 8,192 observations beyond its chosen stop; that
continuation mean explicitly reports 31 finite paths and one missing path. It
does not remove a selected endpoint or a split.

## Smaller samples and rare-objective selection

At $n=256$, aggregate validation retains both improvements over none for all
five positive offsets at $M=8192$. Rare-loss differences range from -0.023218
(0.007525) at 0.001 to -0.010856 (0.005159) at 0.1. Mean rare losses remain
0.07558--0.08794; five partitions have no green training examples and thirteen
have no green validation examples. All test groups are nonempty.

Rare validation can still select damaging finite paths. At $n=256$, offset 0.03
has aggregate mean loss 42.6229 (MCSE 42.3937), median 0.004108, and maximum
1356.8142. Its rare mean loss is 4.7479 (4.6944), median 0.002501, and maximum
150.2734. The dominant split is replication 26, with two green training examples
and one green validation example. It selects factor 1.4, $B=16$, and $M=2048$,
with rare validation loss 0.000893 despite aggregate validation loss 198.3387.
The selected path passes the independent replay gate. Extra stopping checkpoints
do not remove this failure. No trimming or test-based exclusion is applied.

At $n=2048$, rare validation gives damped rare mean losses between 0.000499 and
0.001009, versus 0.003678 for none and 0.002257 for SD. Its aggregate means
range from 0.002175 to 0.009711. The separate summaries retain paired
uncertainty, both objectives, all caps, and absence strata. These outcomes do
not imply that more damping always helps or that rare validation protects
aggregate prediction.

![Fixed-offset sensitivity at the largest
budget.](../results/mushroom-scaling-sensitivity/sensitivity.png)

The [PDF figure](../results/mushroom-scaling-sensitivity/sensitivity.pdf) shows
means over all 32 splits, on logarithmic risk axes, for the primary stopping
search. The horizontal axis lists fixed offsets, with SD at zero. Lines for none
and variance are reference means; the connecting lines do not establish behavior
at untested offsets. Uncertainty and tail summaries are in the tables and
artifact rather than represented as population confidence intervals.

## Variance scaling and remaining boundaries

Variance scaling has substantially larger mean losses in the main comparison.
Its aggregate median is 0.069802 and maximum is 6.505207, so the large mean is
not a typical outcome. Its rare-loss disadvantage versus none is 0.045630
(paired MCSE 0.008323). The aggregate difference has much larger uncertainty:
0.310647 (0.201754). Under large-sample rare validation, its aggregate mean is
25.5720 (8.0453), median 5.7430, and maximum 154.6572, while rare loss is
0.019374 (0.002403).

Two of the 32 primary variance-scaled selections use the upper rate factor 6.4.
Across all caps, objectives, and stopping searches, variance scaling has 31
upper-edge selection decisions, counting repeated splits across queries. None,
SD, and every positive damping level have no lower- or upper-edge selections in
this arm. Thus this finite search supplies evidence about variance scaling under
the declared grid, but leaves its rate search unresolved. It does not establish
inferiority after continuous optimization. Other preprocessing arms and
synthetic comparisons remain outside this follow-up.

The reported MCSEs concern partition and optimizer variation within the same
previously studied dataset. The two-MCSE convention is descriptive, without
equivalence or simultaneous-testing guarantees. A separate validation protocol
would be needed to choose the damping level as part of a practical training
procedure, accounting for its additional search effort.
