# Normalization robustness: findings and limits

September 16, 2026. Execution of [protocol version
1](normalization-robustness.md), with known population preprocessing, zero
initialization, a fixed zero intercept, and constant-step fresh-sample SGD.
These are numerical comparisons on declared finite grids. The [C1 and C2
theorems](normalization-risk-theorem.md) retain their original
fixed-configuration scope.

**Both original anchor comparisons disappear after rate adjustment.** C1's
independent anchor favors standard-deviation scaling at all four endpoints after
adjustment. C2's nested anchor favors no scaling on both objectives at 100
observations. Allowing earlier stopping and refining the grids preserves these
anchor conclusions. Other laws retain or produce reversals and objective
disagreements, so this does not establish a universal normalization ordering.

## Scope and artifacts

The run contains all **228 laws, 51,048 configurations, and 2,571,800 moment
endpoints** declared in advance. The 16 refinement laws receive all four
coarse/fine rate and stopping combinations. The two earlier studies are
unchanged against the protocol's `a47cbfb` preservation baseline.

- [Expanded
  specification](../results/normalization-robustness/specification.json): laws,
  signal variances, slice labels, rates, divisors, actual learning rates,
  effective coordinate steps, curvature, stability, seeds, versions, hashes,
  commands, and preserved-study checksums.
- [Moment archive](../results/normalization-robustness/paths.npz):
  original-scale means, biases, full second moments, design covariance,
  observation-noise covariance and its unit-noise counterpart, both risks and
  their decompositions, raw symmetry and PSD residuals, failure codes, and exact
  update/observation budgets. Grid-label bits identify coarse updates, coarse
  observations, fine updates, and fine observations, respectively.
- [Summary](../results/normalization-robustness/summary.json): 37,470 fixed-pair
  contrasts, fixed-rate batch contrasts, 465,600 oracle comparisons, all tied
  minimizers, cross-objective evaluations, resolution comparisons, boundary
  probes, simulation uncertainty, controls, and failures. Tables pair a `fields`
  list with `rows`; selected endpoint IDs join directly to the moment archive.
  Tie groups use inclusive endpoint-ID ranges.
- [Paired simulation
  archive](../results/normalization-robustness/paired-simulation.npz): noisy and
  noiseless errors, replicate and block IDs, and failure masks for all six
  panels, with 8,192 replications each.
- [Figures](../results/normalization-robustness/figures.json): checksums for six
  figures in SVG and PDF. Figure generation also writes local PNG previews to
  the ignored `build/robustness/` directory.

Every contrast below is **SD scaling S minus no scaling U**. Risk includes the
factor one half and excludes irreducible test noise. The primary oracle admits
stable steps and the zero predictor. Its common parameter is $h$, with
$\eta_U=4h$ and $\eta_S=h$; the rates are not matched in absolute $\eta$. The
positive coarse range is $[1.953125\times10^{-6},0.64]$, with 34 positive rates
and zero. Refinement adds 33 geometric midpoints without extending the range. A
sign requires a gap exceeding $10^{-8}\max(1,|R^U|,|R^S|)$.

## C1: the original stopping reversal disappears at the anchor

C1 fixes $q=0.02$, $\ell=0$, $\beta^*=(1,1)$, $\sigma^2=3$, and $h=0.002$. The
fixed rare-risk contrasts reproduce the theorem. The adjusted columns minimize
rare risk separately for U and S at each exact endpoint.

  | Batch $B$ | Updates $k$ | Observations $M$ | Fixed gap   | Coarse rate-adjusted gap | Fine rate-adjusted gap |
  | --------- | ----------- | ---------------- | ----------- | ------------------------ | ---------------------- |
  | 1         | 1,000       | 1,000            | -0.26627047 | -0.00569467              | -0.00815852            |
  | 1         | 10,000      | 10,000           | +0.05064340 | -0.00256190              | -0.00210466            |
  | 10        | 1,000       | 10,000           | -0.33489858 | -0.00138055              | -0.00184405            |
  | 10        | 10,000      | 100,000          | -0.01404551 | -0.00010275              | -0.00030022            |

Rate-and-stopping adjustment gives the same values at these update caps and at
the corresponding observation caps. The selected fits use the complete listed
budget. All four coarse/fine combinations retain negative adjusted signs. The
two $k=10,000$ rows compare equal update counts but different observation costs.
The middle two rows compare equal observation costs and different update counts.

At $B=1$, $k=10,000$, the coarse rare-risk choices are $h_U=0.004$ and
$h_S=0.0003125$. They attain risks 0.01556805 and 0.01300616. Reducing S's step
removes the late observation-noise cost responsible for the fixed-pair reversal.
At $k=1,000$, U instead needs $h_U=0.02$ to compete with $h_S=0.002$.
Consequently, common-feature mean learning is matched for the fixed pair, but
not for these separately adjusted pairs. The [mean
paths](../results/normalization-robustness/figures/coefficient-means.svg) and
[decomposition](../results/normalization-robustness/figures/fixed-decomposition.svg)
retain that distinction.

Across the 36 prevalence/dependence laws with $(\beta^*,\sigma^2)=((1,1),3)$, 30
have the original $B=1$ early-negative/late-positive pattern at fixed $h=0.002$;
18 reproduce all four original signs. After either coarse rate adjustment or
coarse rate-and-stopping adjustment, four of those 30 retain the $B=1$ stopping
reversal:

  | $(q,\ell)$   | Adjusted gap at $k=1,000$ | Adjusted gap at $k=10,000$ |
  | ------------ | ------------------------- | -------------------------- |
  | $(0.02,-1)$  | -0.00326171               | +0.00028737                |
  | $(0.05,-1)$  | -0.00050474               | +0.00048705                |
  | $(0.1,-1)$   | -0.00064106               | +0.00001533                |
  | $(0.1,-0.5)$ | -0.00199901               | +0.00021310                |

These four laws are outside the declared 16-law refinement subset. Their
resolution robustness is untested. Negative dependence with two positive signals
also changes the coupled common-feature trajectory, so the independent
common-learning explanation cannot be transferred unchanged.

## C2: retuning removes the anchor's objective disagreement

C2 fixes $q=0.02$, $\ell=1$, $\beta^*=(2,1)$, $\sigma^2=4$, $B=1$, and
$k=M=100$. Before adjustment, $h_U=h_S=0.01$ gives aggregate risks 0.08545538
and 0.08675606, a **+0.00130069** gap. Rare-presence risks are 0.75545570 and
0.68273163, a **-0.07272408** gap. Both coefficient MSEs increase under S; the
negative change in their cross moment explains the rare-risk improvement. The
[cross-moment
figure](../results/normalization-robustness/figures/c2-cross-moment.svg) shows
the signed contributions before and after adjustment.

The following rows report actual trained pairs, each evaluated on both risks.
All selected fits use 100 updates and 100 observations. Rate-and-stopping
adjustment gives these same selections and risks at the corresponding cap.

  | Grid and selection objective | $h_U$      | $h_S$      | Aggregate gap for selected pair | Rare gap for selected pair |
  | ---------------------------- | ---------- | ---------- | ------------------------------- | -------------------------- |
  | Coarse, aggregate            | 0.02       | 0.016      | +0.02404628                     | +0.77903917                |
  | Coarse, rare                 | 0.04       | 0.008      | +0.06748607                     | +0.23982114                |
  | Fine, aggregate              | 0.02529822 | 0.016      | +0.02461220                     | +0.83622614                |
  | Fine, rare                   | 0.04       | 0.00632456 | +0.10440546                     | +0.22947600                |

Thus neither objective-selected pair retains the original disagreement. The fine
aggregate envelope gap is +0.02461220, whereas its rare envelope gap is
+0.22947600; these two envelope gaps concern different pairs. The table makes
the cross-evaluations explicit. The interior $\ell=0.9$ endpoint also loses its
disagreement after coarse adjustment.

Across the 36 prevalence/dependence laws with $(\beta^*,\sigma^2)=((2,1),4)$,
only the two fixed pairs at $q=0.02$, $\ell\in\{0.9,1\}$ have C2's
positive-aggregate/negative-rare ordering at 100 observations. None of the 36
has this ordering after coarse adjustment, either for the objective-specific
envelopes or for either common selected pair.

## What remains beyond the anchors

The signal/noise slice gives a different picture. At $q=0.02$, $B=1$, $k=M=100$,
seven of its 162 laws have C2's fixed-pair ordering at $h=0.01$. None of those
seven retains it for either coarse objective-selected pair. However, other laws
produce disagreement after adjustment:

- The two objective-specific envelopes have positive-aggregate/negative-rare
  gaps in 13 laws, and the opposite ordering in two laws. These are comparisons
  of separately optimized objectives.
- Evaluating both risks for the aggregate-selected pair gives C2's ordering in
  15 laws. Evaluating both risks for the rare-selected pair gives it in five
  laws. These counts concern common trained pairs and need not coincide with the
  envelope counts.

For example, at $\ell=-1$, $\beta^*=(1,-1)$, and $\sigma^2=1$, the
aggregate-selected coarse pair uses $h_U=0.02$, $h_S=0.016$, and 100 updates for
both fits. Its aggregate gap is +0.00154122 and its rare gap is -0.02762504.
This law was not selected for refinement, so it supplies a bounded numerical
example, not a resolution claim or a new theorem. Conversely, at $\ell=0$,
$\beta^*=(1,0)$, and $\sigma^2=4$, both envelopes favor U, with gaps +0.01531242
and +0.08072420. The rare-only signal $(0,1)$ instead favors S at that law and
budget, with gaps -0.00174979 and -0.03531392. Pure-noise laws select the zero
predictor and give zero gaps. Null and unfavorable outcomes remain in the
tables.

Budget dependence also survives adjustment at both anchors, with a different
pattern from C1's original late-noise reversal. At $B=1$, coarse
rate-and-stopping adjustment favors U on both objectives at 100 observations and
S on both objectives at 1,000, 10,000, and 100,000 observations. For C1, the
rare gaps at these four caps are +0.01972103, -0.00569467, -0.00256190, and
-0.00029498. For C2, they are +0.23982114, -0.02330197, -0.00852715, and
-0.00160562. This is a statement about those declared caps, not every
intermediate budget.

The separate search over $B\in\{1,10,100\}$ uses common observation caps only.
At C1's cap $M=10,000$, both coarse and fine pooled envelopes favor S on both
objectives. At C2's cap $M=100$, both favor U on both objectives. Selected
batches can differ by method and objective: the coarse C1 rare-risk search
selects $B_U=10$ and $B_S=1$, while the coarse C2 rare-risk search selects
$B_U=1$ and $B_S=10$. The summary retains their actual observations, updates,
and caps. This pooled search is not a fixed-update comparison.

## Resolution and search boundaries

At shared coarse caps on the 16 declared refinement laws, each row below
compares 2,752 stable-envelope contrasts against the coarse/coarse result.
Counts include both objectives, both budget conventions, and the separately
labeled pooled-batch observation search. The sign tolerance is numerical, not a
significance test.

  | Rate/stopping refinement | Rate-adjustment classification changes | Rate-and-stopping classification changes |
  | ------------------------ | -------------------------------------- | ---------------------------------------- |
  | Fine/coarse              | 78                                     | 79                                       |
  | Coarse/fine              | 0                                      | 7                                        |
  | Fine/fine                | 78                                     | 79                                       |

The zero in the middle row follows because rate adjustment at an exact shared
stop does not use extra stopping candidates. The other counts show that grid
resolution matters outside the anchors; they do not justify extrapolating
resolution robustness to the other 212 laws. See the [resolution
figure](../results/normalization-robustness/figures/resolution-sensitivity.svg).

Search-boundary selections are retained, including tied fits chosen by fewer
observations, then smaller $h$, then smaller batch. Across the coarse/coarse
stable comparisons and both displayed fits, 26,751 selections are zero
predictors, 646 use the smallest positive rate, and 12,652 use the largest rate.
These are repeated comparison rows, not counts of distinct fitted models. The
summary also flags earliest/latest stops and retains every tied minimizer. No
grid was expanded after inspecting an optimum.

## Numerical checks, uncertainty, and failures

The independent checks enumerate 48 short gradient-path cases, including
negative dependence, mixed signs, non-unit signals, two batch sizes, and zero or
two-point noise. The largest discrepancy across the short and long moment checks
is $2.65\times10^{-13}$. The C1/C2 continuous-box certificates were rerun
separately; the larger grid does not extend their proven boxes.

All 216 stability brackets pass their below/above-boundary probes. Among the
51,048 main configurations, 47,526 have stable positive steps, 2,154 have
unstable steps, and 1,368 are labeled zero-step baselines. No positive
common-grid step falls in the numerical boundary band. The main archive has
**30,944 nonfinite floating-point endpoints**, all at unstable configurations.
No finite endpoint failed the PSD or symmetry checks. The separate 6,480
boundary-probe endpoints include 264 nonfinite results. Raw values and failure
codes are kept; finite-time moments under these laws exist even when
floating-point evaluation overflows.

Every primary stable envelope is complete. Of all 465,600 comparisons, **73,500
unrestricted comparisons are incomplete** because an invalid candidate remains
unresolved. Their reported minima over valid entries are upper bounds on the
full grid minima, and their signs are labeled incomplete. We make no ordering
claim from comparing these upper bounds. No higher-precision resolution of these
unrestricted candidates is claimed.

A separate stop-by-stop reduction independently checks all 465,600 oracle
minima, candidate and invalid counts, budgets, and classifications. It also
checks cross-objective risk evaluation and 936 deterministic exhaustive tie
cases. Independent common-mean and rare-mean controls have maximum absolute
residuals $4.42\times10^{-12}$ and $3.11\times10^{-12}$. Across 1,570,104 valid
fixed-update batch comparisons, the minimum eigenvalue of the second-moment
difference, relative to the moment scale, is $-1.91\times10^{-15}$, consistent
with the stated larger-batch ordering within numerical tolerance. That ordering
is not imposed on equal-observation comparisons.

All six paired simulation panels completed with **zero failed replicates**.
Original-scale iterates and predictions under global rescaling differ by at most
$6.58\times10^{-14}$; moment discrepancies are at most $1.34\times10^{-15}$. The
archive preserves all paired endpoints and noiseless companions. Means,
coefficient moments, risks, and U/S and batch contrasts use within-replicate
differences and sample-standard-deviation MCSEs. Noiseless covariance uses an
unbiased estimator and a delete-one-block jackknife over the 32 replication
blocks.

**One of the covariance diagnostics fails the six-MCSE gate and remains a
reported limitation.** In the greater-rarity panel, S with $B=1$, $k=10,000$,
$q=0.002$, and $h=0.002$ has exact noiseless rare-coefficient variance
$2.33494\times10^{-9}$. The simulated estimate is $1.57410\times10^{-14}$, with
jackknife MCSE $1.32329\times10^{-14}$. The other moment, risk, paired contrast,
and covariance gates pass.

Conditioning the independent updates on no rare observation explains most of
this miss. That event has probability $(1-q)^k=2.02029\times10^{-9}$ and
contributes $1.86513\times10^{-9}$, or 79.88%, of the exact variance. Only
$1.65502\times10^{-5}$ such replications are expected in the declared sample;
replaying its feature streams finds none. A separate one-update-at-a-time
calculation checks the conditional moment. The simulation cannot resolve this
small tail-dominated covariance, and the jackknife cannot recover events absent
from its sample. We retain the gate violation and its investigation without
increasing replications or relaxing tolerances. Exact moments have no Monte
Carlo standard error. The simulation subset does not validate retuned selection.

## Reproduction and interpretation

Inside `devenv shell`, run:

```sh
make reproduce-normalization-robustness
make check-normalization-robustness
make check
```

The reproduction target runs focused numerical checks and the existing theorem
certificates before regenerating moments, simulations, summaries, and figures.
The focused checker verifies source and artifact hashes, the full grid,
numerical and selection identities, paired uncertainty, the retained covariance
diagnostic, and preservation checksums. `make check` includes these checks and
the rest of the repository validation. Reproduction is computationally larger
than the preceding studies, and the complete moment archive is about 441 MiB.

The evidence supports interactions among normalization, rate, stopping, batch,
dependence, signal, and risk objective. It does **not** support robustness of
the original fixed anchors to the declared retuning. It also does not rule out
objective disagreement after retuning on other laws. The surviving comparisons
are candidates for further analysis, with their search bounds and refinement
coverage stated above.

Tail averaging remains deferred under the declared protocol. This task tests
constant-step final iterates and makes no comparison with a tail-averaged
estimator or claim of superiority over that literature. An averaging comparison
would require a stated window and cross-iterate moments. Estimated centering and
scales, fitted intercepts, absent observations in practical training samples,
validation-based selection, and a sparse-data task remain the next study. The
diagnostic conditioning on absence above does not implement estimated
preprocessing or practical selection. Novelty and empirical usefulness remain
separate research questions.
