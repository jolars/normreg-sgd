# Checking the oracle limits at finite prevalence

The exact-moment comparisons recover the principal predictions of the [limiting
characterization](oracle-variational.md) as prevalence decreases: opposite
orderings for the theorem's two signal families, a signal-allocation crossing,
two noise reversals in the specified example, and a budget reversal. Convergence
can be slow enough to change the preferred scaling. In particular, the
high-noise example favors SD at prevalences where its limiting prediction favors U.

These are numerical comparisons over finite candidate families. The manuscript's
existing Theorem 3.1 and its finite-prevalence certificates remain the
quantitative guarantee over all nonnegative constant rates and deterministic
stops. Neither that theorem nor its proof has been changed. The checked limiting
proofs and these comparisons are now integrated into the manuscript.

## Model and search

The study uses independent binary features, population centering and scaling,
fresh observations, zero coefficients, a fixed zero intercept, and final
iterates. Write $s=(\beta_C^*)^2$, $r=(\beta_R^*)^2$, $\nu=\sigma^2$, and
$b=q(1-q)$. The risk is half the prediction error conditional on rare presence,
excluding irreducible test noise. The affine recurrence for $(G,H,\nu)$ in the
[limit notes](oracle-limits.md#exact-recurrence) is evaluated by matrix powers;
there is no Monte Carlo noise.

The [settings](../results/oracle-finite/settings.json) specify 43 signal, noise,
and target-budget combinations, each at six prevalences from $0.04$ through
$2\times10^{-6}$. They include both theorem anchors at $\tau=1,2,4$;
common-signal strengths at 90%, 100%, and 110% of the predicted crossing at
those budgets; eight allocations at fixed $s/4+r=1$ and $\tau=2$; four noise
levels; three points around U's rare-learning threshold; six budgets from $0.01$
through $1000$; three common-signal strengths with fixed rare signal; and
zero-signal and zero-noise endpoints. These are selected slices, not a full
factorial design or a uniform verification over their enclosing ranges.

Each scaling independently minimizes expected risk over its rates and stops. The
fine rate grid contains 2,049 fractions of its mean-square stability limit: the
union of 1,025 linear and 1,025 logarithmic points, with zero included and
positive fractions from $10^{-10}$ through $1-10^{-6}$. Limiting optimal rates
are not inserted into the grid. Rates outside this stable interval are not
searched. The stop grid includes initialization, every integer through 64, every
cap, and rounded geometric checkpoints up to the largest cap. It contains 663 to
883 distinct stops, depending on prevalence. The largest cap is 500,001,001
observations.

Caps round $\tau/b$ upward, except at target $\tau=4$, where they round downward
to remain in the theorem's range. Primary comparisons evaluate the limit at the
actual $Mb$. The nominal-target predictions are also saved, so integer-cap
effects are visible. At $q=0.04$, target $\tau=0.01$ permits just one
observation and actually gives $Mb=0.0384$. No small-prevalence accuracy should
be inferred from that coarse-budget setting.

The [saved arrays](../results/oracle-finite/search.npz) retain the exact
candidate grids and the selected risk, rate, and stop for four searches: coarse
rates and stops, fine rates only, fine stops only, and both fine. Coarse grids
take every second point of the generating linear and geometric grids, retaining
the early integer stops and all caps. The largest decrease on joint refinement
is $1.362\times10^{-5}$. Stop refinement alone changes no selected risk: every
positive-stop selection uses the cap, and the remaining selections use
initialization. No positive-stop selection lies at either edge of the rate grid.
These observations assess resolution but do not bound the error relative to the
unrestricted oracle or prove that the full cap is always optimal.

## Convergence and transition predictions

The [summary](../results/oracle-finite/summary.json) records both absolute
risks, rates, stops, gaps, ratios, refinement changes, and discrepancies from
the limit for all 258 comparisons. The largest absolute errors across the 43
settings are:

  | Prevalence $q$ | U error     | SD error      |
  | -------------: | ----------: | ------------: |
  |         $0.04$ |   0.0551020 |     0.0391366 |
  |         $0.02$ |   0.0777799 |     0.0197905 |
  |        $0.002$ |   0.0470811 |    0.00199772 |
  |       $0.0002$ |   0.0103992 |   0.000199959 |
  |      $0.00002$ |  0.00153332 |  0.0000199975 |
  |     $0.000002$ | 0.000201631 | 0.00000227583 |

The largest U error occurs at target $\tau=0.01$. Its increase between the first
two rows shows that finite-prevalence errors need not decrease monotonically
along rounded caps. For the theorem anchors alone, the largest errors at the
smallest prevalence are $2.987\times10^{-6}$ for U and $1.536\times10^{-6}$ for
SD. Finite search resolution contributes to these discrepancies, especially when
the prevalence effect becomes small.

Both theorem orderings hold in every sampled anchor comparison. At the smallest
prevalence, the common-signal crossing is bracketed by 90% and 110% of its
limiting value for all three budgets. The fixed-total allocation comparison
likewise recovers the predicted ordering on both sides of its crossing
$\theta_*\approx0.83770278$. Every sampled setting with a nonzero nominal
limiting gap has the predicted sign at the smallest prevalence. Cases placed
exactly at a limiting crossing remain sensitive to cap rounding and grid
resolution. Their tiny signed discrepancies are saved, but do not locate a
finite-prevalence boundary or establish uniqueness of such a boundary.

The U endpoint prediction requires particular care. At $\tau=2$, $s=1$, and
$r=0.01$, its limiting risk is $r/2=0.005$, with limiting rate zero. Finite
searches instead use positive rates to learn the common signal: the selected
rate falls from 0.07003 at $q=0.02$ to $2.866\times10^{-5}$ at
$q=2\times10^{-6}$, and the risk falls from 0.01570 to 0.00500127. Literal
zero-rate training would retain common-signal error. The threshold and
common-dependence slices exercise the same distinction; independence from the
common signal is a limiting conclusion, not a finite-prevalence identity.

## A finite-prevalence disagreement at high noise

For $s=0.1$, $r=1$, and target $\tau=2$, the four noise levels $\nu=0,0.1,1,100$
have limiting preferred scalings U, SD, SD, and U. The finite-grid searches
recover all four signs at $q=2\times10^{-5}$ and $q=2\times10^{-6}$. The
high-noise comparison disagrees at larger prevalences:

  | $q$               | U risk at $\nu=100$ | SD risk at $\nu=100$ | SD minus U   |
  | ----------------: | ------------------: | -------------------: | -----------: |
  |            $0.02$ |            0.488673 |             0.482985 |  -0.00568756 |
  |           $0.002$ |            0.505989 |             0.500357 |  -0.00563282 |
  |          $0.0002$ |            0.502721 |             0.502112 | -0.000608220 |
  |         $0.00002$ |            0.500486 |             0.502288 |   0.00180198 |
  |        $0.000002$ |            0.500068 |             0.502305 |   0.00223702 |
  | Limit at $\tau=2$ |            0.500000 |             0.502306 |   0.00230649 |

The discrepancies are much larger than the observed search-refinement changes.
They show why the limiting decision rule should not be used as a quantitative
finite-prevalence guarantee. They do not certify a reversal of the unrestricted
finite-prevalence oracles.

## Budget and the ordered large-budget limit

At $s=r=\nu=1$ and the smallest prevalence, U wins at target $\tau=1$, while SD
wins at $\tau=10,100,1000$. At $\tau=1000$, the finite risk ratio is 0.839843
and the limiting ratio is 0.839507. Both remain above the further large-budget
limit $4/5$. The saved comparisons support the direction of the budget
prediction without replacing the ordered-limit statement by a claim about a
simultaneous $q\to0$, $\tau\to\infty$ limit.

The plot below uses only the saved summary. Lines connect sampled settings; they
do not certify intervening transition locations. The budget panel uses target
budgets, so its coarsest small-budget points also reflect cap rounding.

![Finite-prevalence errors and allocation, noise, and budget
comparisons](../figures/oracle-finite/limit-comparison.png)

## Reproduction and independent checks

From the repository root inside `devenv shell`, run:

```sh
task experiment:oracle-finite
task check:oracle-finite -- --rerun
task figure:oracle-finite
task check:predictive-fixed-q
```

The run and summary tasks are also available separately as
`experiment:oracle-finite:run` and `experiment:oracle-finite:summarize`.
Summarization and plotting never rerun a search. The ordinary
`check:oracle-finite` checks the saved results without regenerating them;
`--rerun` additionally reconstructs every candidate selection.

The checker independently enumerates individual-observation tensor updates for a
small search and verifies all four nested grid combinations. It replays all
2,064 saved selections using the full observation tensor and long-double matrix
powers, with maximum risk discrepancy $7.38\times10^{-11}$. It also checks the
saved summary, feasible rates and stops, convergence, the predicted signs away
from limiting ties, the retained high-noise mismatch, and degenerate cases. The
[check output](../results/oracle-finite/checks.txt) records a complete rerun.
`task check:oracle-limits` includes this checker alongside the earlier limit,
uniform-control, and variational checks.
