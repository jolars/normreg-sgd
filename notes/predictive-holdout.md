# Prospective evaluation of the oracle prediction

September 20, 2026. **Protocol draft; not yet frozen or executed.** This is the
next scientific milestone after the [contribution
decision](predictive-contribution.md). The prediction and proposed evaluation
choices are recorded before evaluating these configurations. Implementation, an
overlap audit against development calculations, data ingestion checks, and a
frozen declaration are still needed. The earlier experiments remain development
evidence and must not be relabeled as held-out confirmation.

## Prediction and interpretation

The [theorem](predictive-theorem.md), with its [unrestricted-rate
addendum](predictive-proof-review.md#addendum-the-predictive-rate-cap-can-be-removed),
predicts opposite orderings of the lowest attainable rare-presence risk under a
common observation cap: SD wins on the stated dominant rare-signal family, and
unscaled training wins on the dominant common-signal family. Every nonnegative
constant rate and deterministic stop is eligible in the theorem.

The prospective hypothesis is that this direction remains informative under
moderate changes in signal strength and prevalence, and with estimated
preprocessing. Tests outside the assumptions are extrapolations. Failure of an
extrapolation limits the explanation's reach; it does not refute the theorem.
Validation selection is a separate procedure and can fail even if an oracle
ordering persists.

Use three stages, with results reported separately:

1. Fresh-sample population moments on new binary laws, separating points inside
   the theorem from extrapolations.
2. New sampled binary datasets with estimated preprocessing and validation
   selection, retaining a known-preprocessing control.
3. A new sparse categorical design with controlled response signals, followed by
   its recorded prediction target as a practical comparison.

## New binary laws

Set $\ell=0$ and $\sigma^2=1$. Cross

$$
  q\in\{0.00007,0.0007,0.007,0.035\},\qquad
  d\in\{0.64,1,1.44\}
$$

with the two signals

$$
  \beta^*=(0.07,\sqrt d)^\top
  \quad\text{and}\quad
  \beta^*=(\sqrt d,0.07)^\top.
$$

The predicted SD-minus-U rare-risk gap is negative for the first family and
positive for the second. These give 24 laws. Only $q=0.00007,d=1$ lies in the
theorem's signal and prevalence domain. The other laws test larger prevalence or
a 20 percent change in dominant coefficient magnitude. The predictions use the
same signs throughout; no configuration is selected for its realized gap.

For $t\in\{1.25,2.5,3.75\}$, use observation cap $M=\lceil t/[q(1-q)]\rceil$.
Record the actual $Mq(1-q)$ and $Mq$ as well as the requested $t$. At the
in-domain prevalence all three rounded caps stay inside the theorem's budget
interval. The primary exposure is $t=2.5$; the other two are declared budget
checks. Do not pool prevalences or signal families into one average advantage.

Before execution, compare the full law tuples and budgets against the retained
development specifications and notes. Record exact overlaps as development
controls and any unknown provenance as such. New random seeds alone do not make
a previously inspected configuration held out from claim development. If an
overlap requires changing the proposed set, issue a new dated protocol before
computing any losses and retain this version.

## Population evaluation

Use fresh observations, $B=1$, known population centering and variances, zero
feature coefficients, and a fixed zero intercept. Calculate exact expected
moments from the finite recurrence. For each scaling, use the rate coordinate
$\alpha$ from the theorem:

$$
  D_U=\alpha I_2,\qquad D_S=\operatorname{diag}(4b\alpha,\alpha).
$$

The primary positive rate grid is $\{2^{j/8}:j=-128,\ldots,16\}$, with 145 rates
from $2^{-16}$ to $4$ for each rule. Include the zero predictor. At each cap use
all integers from zero through $\min(16,M)$ and the distinct counts
$\lceil M^{j/64}\rceil$, $j=0,\ldots,64$. A declared refinement uses
$\{2^{j/16}:j=-256,\ldots,32\}$ and adds stops through 32 and
$\lceil M^{j/128}\rceil$. Preserve both grids and every endpoint, including
failed or unstable paths. The refined sets contain the primary sets.

Report separately the finite-grid minima over all successfully evaluated
candidates and over mean-square-stable candidates, including initialization. An
unrestricted comparison with unresolved numerical candidates is incomplete.
Report both aggregate and rare risk, squared bias, feature-sampling variance,
observation-noise variance, and the selected original-scale coefficient means.
Record the selected rate, stop, rate boundaries, immediate rate neighbors, and
the effect of the declared refinement.

These finite searches do not certify continuous optima. At in-domain points,
also check the theorem's explicit winning candidate and quantitative lower bound
on every competitor; disagreement between a grid minimum and a candidate bound
must be investigated as a numerical or search issue. Elsewhere, a grid ordering
is evidence only for that search. No Monte Carlo uncertainty applies to
exact-moment values. Independently enumerate the four observation-cell operators
and check selected values at higher precision before interpretation.

## Estimated preprocessing and validation

Use the 18 laws with $q\in\{0.0007,0.007,0.035\}$, all three values of $d$, and
both signal families. Generate 128 independent replications at each
training/validation size $(256,128)$ and $(2048,1024)$. Draw independent
Gaussian observation noise of variance one. Test excess risks are integrated
over the four population cells, using the known noiseless response. Test
quantities never enter validation selection.

Use the `known`, `estimated_scale`, and `centered_fitted` conventions from the
[practical protocol](practical-selection.md). The first has population
preprocessing and a fixed true intercept. The second changes only scale
estimation and the constant-column policy. The third estimates means and
variances from training data, initializes the intercept at the training response
mean, and fits it. Estimated constant columns have divisor one and coefficient
fixed at zero; unknown rare effects remain zero. All feature coefficients start
at zero. Retain the distinct initialization conventions at budget zero.

Compare U and S using replacement sampling from each fixed noisy training set,
$B=1$, and the three observation caps above. This is a transport test from the
fresh-sample theorem to fixed-data training. Processed count $M$ and distinct
sample size $n$ have different meanings; $Mq$ is not a count of independently
observed rare training cases in this stage.

Each arm and scaling receives the same 25 rate factors from the frozen
[four-rule
protocol](variance-scaling-followup.md#four-rules-and-equal-searches), with
$\eta=a/\max(L,10^{-12})$ and empirical scaled curvature $L$, including the
intercept when fitted. Use the primary stopping set from the population stage.
Nominal work at cap $M$ is $25M$ processed rows per arm and scaling; checkpoint
scoring and preprocessing are reported separately. Pair datasets, noise, and
replacement index streams across methods.

Within each scaling, select rate and stop by aggregate validation loss and,
separately, rare validation loss. Initialization is eligible. Break ties by
smaller processed count, then smaller rate factor, then candidate index. Empty
rare validation groups trigger the declared aggregate-loss fallback and an
explicit flag. Retain extreme finite candidates. A path fails on nonfinite
arithmetic or an original coefficient or intercept exceeding $10^{100}$ in
absolute value; preserve the first failed update and mark subsequent endpoints.
Failure scores are infinite. Do not refit selected models.

The primary transport comparison is rare validation selection in the
`centered_fitted` arm at $t=2.5$. Report its unconditional outcomes and the
strata with and without rare observations in training and validation. The
population theorem does not justify discarding absence cases. Aggregate
selection, other arms, and other caps are secondary. Report hindsight oracle
choices within the same finite set separately from validation-selected choices.

## Additional sparse categorical task

Use [UCI Adult](https://www.archive.ics.uci.edu/dataset/2/adult), by Barry
Becker and Ronny Kohavi, DOI [10.24432/C5XW20](https://doi.org/10.24432/C5XW20),
under CC BY 4.0. The source provides categorical and integer predictors and an
income-threshold label. Use only its eight categorical predictors: workclass,
education, marital status, occupation, relationship, race, sex, and native
country. The declared rare indicator is `occupation=Protective-serv`; the common
indicator is `workclass=Private`. Category names come from the source schema,
not a comparison of normalization results. Record their observed frequencies
when ingesting the data.

Use the official `adult.data` pool for training and validation, and reserve
`adult.test` for testing. Trim field whitespace, preserve `?` as a category,
skip the test-file header, and remove the trailing period from test labels.
Audit duplicates by the full 14 raw predictor fields before discarding numeric
columns. Remove development-pool groups whose predictor tuple occurs in the
official test pool. Group remaining identical full predictor tuples together
when splitting training and validation. Identical categorical projections of
otherwise distinct raw records are retained. Report all removed and grouped
counts without choosing a rule based on prediction results.

For each of 32 permutations of the development groups and each target size
$(256,128)$ or $(2048,1024)$, assign whole groups to training until the training
count reaches its target, then whole groups to validation until its target is
reached. Record actual counts. Fit the full one-hot vocabulary, means, and
variances on training data only. Unknown levels map to zero blocks. Use sparse
storage, algebraic centering, a fitted unscaled intercept, and the same
constant-column policy as above. Retain subgroup absence and unknown-category
counts. The redundant one-hot coefficients are optimizer-dependent quantities.

First generate controlled responses on this categorical design, with independent
unit Gaussian training and validation noise and noiseless test targets:

$$
  f_R(x)=0.07\,1\{\text{workclass=Private}\}
              +1\{\text{occupation=Protective-serv}\},
$$

$$
  f_C(x)=1\{\text{workclass=Private}\}
              +0.07\,1\{\text{occupation=Protective-serv}\}.
$$

Predict lower SD rare risk for $f_R$ and lower U rare risk for $f_C$. These are
explicit extrapolations to dependent, redundant categorical predictors. The
known response functions make the signal assignment testable without inferring
it from observed method advantages. Report this stage as semisynthetic.

Separately predict the recorded income label, one for income above the source
threshold. Do not claim a theorem-predicted direction for this natural target:
its signal allocation is unknown. This comparison tests practical behavior and
selection failures on an additional dataset. Use unclipped half squared loss for
all targets, with aggregate and declared rare-subgroup evaluation.

Use the same 25 factors, $B=1$, and checkpoints
$\{0,1,2,4,8,16,32,64,128,256,512,1024\}$, with caps 64, 256, and 1024. The
primary categorical comparison is the controlled-response pair at cap 64 with
rare validation selection, reported separately by sample size. Later caps,
aggregate selection, hindsight choices, and the natural target are secondary.
All targets and methods share partitions and replacement streams; the two
controlled targets also share the Gaussian noise. Selection, failure handling,
and nominal work counts follow the binary sampled-data stage.

The source is a historical observational dataset. Treat these as prediction
comparisons within its fixed record pool. Coefficients do not identify causal
effects, and partition MCSEs do not establish population representativeness.

## Declaration, reporting, and acceptance criteria

Use a new seed namespace based on
`SeedSequence([20260920, stage, law, size, replication, stream])`, with the
integer indexing recorded in the specification. No replications are added or
removed in response to results. Report paired mean gaps and MCSEs, medians, 95th
percentiles, maxima, absence strata, initialization selections, rate/stop
boundaries, failures, and denominators. An empty test subgroup gives a missing
loss, never zero. Two-MCSE intervals are descriptive; report every declared
panel and do not interpret a collection of such intervals as a simultaneous
confidence statement. Tail-dominated means remain unresolved when the available
replications do not estimate them precisely.

Before evaluating new outcomes:

1. Complete the overlap and data-schema audits and record their results.
2. Finalize the specification, runner, summarizer, and independent checker.
   Verify updates on small development fixtures outside the evaluation set.
3. Freeze this protocol, specification, sources, dependencies, input data, seed
   mapping, and preserved-study hashes in a declaration under
   `results/predictive-holdout/`. Record the repository revision and source
   hashes rather than relying on an uncommitted working tree description.
4. Run the declared stages, retain all candidates and failures, and write the
   results to `notes/predictive-holdout-results.md`. Keep any subsequent
   diagnostics or revised protocol separate from the primary evaluation.

The milestone is complete when all declared panels and limitations have been
reported and independently checked, regardless of which normalization wins.
Distinguish in-domain numerical consistency, successful or failed extrapolation,
and validation-selection behavior. Neither a favorable subset nor another
evaluation of the original Mushroom study completes this milestone.
