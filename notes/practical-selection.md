# Practical preprocessing and validation selection

September 16, 2026. Protocol version 1, declared before inspecting this study's
prediction results. This extends the controlled C1/C2 comparisons in [the
robustness study](normalization-robustness-results.md). All earlier studies,
including their failures, are preserved against commit `a774192`. Results belong
in `practical-selection-results.md`.

## Questions and scope

Does relative scaling still change finite-budget rare-feature learning when
centering and scales are estimated, an intercept is fitted, and validation
replaces oracle selection? Does optimizing aggregate validation loss choose a
different predictor from optimizing rare-presence validation loss? Evaluate
these questions first in sampled versions of the controlled binary models, then
in one sparse categorical linear-model task. Null results, reversed orderings,
missing groups, boundary selections, and failed paths are outcomes.

This is a finite-grid experiment, not a theorem about estimated preprocessing, a
continuous tuning optimum, or a universal normalization recommendation. No
neural model or adaptive optimizer is included: neither is needed to test the
stated hypothesis that feature scaling changes finite-budget allocation of
learning and interacts with the validation objective.

## Controlled samples

For binary $(I,J)$ use $P(I=1)=1/2$, $P(J=1)=q$, and $P(I=1,J=1)=q(1+\ell)/2$.
Responses are $y=(I-1/2)\beta_C^*+(J-q)\beta_R^*+\varepsilon$, with independent
$\varepsilon\sim N(0,\sigma^2)$. Use these eight laws:

  | Labels             | $q$         | $\ell$ | $\beta^*$ | $\sigma^2$ |
  | ------------------ | ----------- | ------ | --------- | ---------- |
  | C1, rarer C1       | 0.02, 0.002 | 0      | (1,1)     | 3          |
  | C2, rarer C2       | 0.02, 0.002 | 1      | (2,1)     | 4          |
  | Opposite, nested   | 0.02        | 1      | (2,-1)    | 4          |
  | Opposite, disjoint | 0.02        | -1     | (2,-1)    | 4          |
  | Rare only          | 0.02        | 0      | (0,1)     | 1          |
  | Common only        | 0.02        | 0      | (1,0)     | 1          |

Each law has 128 independent replications, with 256 training and 128 independent
validation observations. They are random designs; rare counts are not forced.
Test excess loss is integrated exactly over the four population cells. Test
labels are never supplied to selection. Validation uses observed noisy labels.
All arms and candidates share a replication's samples, noise, and index stream.
The training dataset is fixed and revisited with replacement, reusing each
observation's noise. This differs from the fresh-sample C1/C2 theorems.

Use five preprocessing/intercept arms:

1. `known`: population means and variances, true intercept zero in population
   centered coordinates, fixed throughout training.
2. `estimated_scale`: population means and true fixed intercept, with variances
   estimated from the training sample. This isolates scale estimation and the
   constant-column policy.
3. `centered_fixed`: training means and variances, intercept initialized and
   fixed at the training response mean.
4. `centered_fitted`: the same preprocessing and initialization, with a jointly
   updated intercept.
5. `uncentered_fitted`: zero feature shift, training variances, and a jointly
   updated intercept initialized at the training response mean.

All feature coefficients start at zero. The known and estimated-scale arms start
with the true zero predictor; the other arms start with the sample response
mean. This initialization difference is part of practical intercept estimation
and is retained at budget zero. Variances use denominator $n$. In every
estimated arm, constant training columns have divisor one and coefficient fixed
at zero. Thus an unobserved rare feature cannot acquire an estimated effect. In
the known arm an absent but population-centered feature can still update,
illustrating the distinction between known preprocessing and empirical
identifiability.

## Sparse categorical task

Use [UCI Mushroom](https://archive.ics.uci.edu/dataset/73/mushroom), DOI
[10.24432/C5959T](https://doi.org/10.24432/C5959T), with the original
`agaricus-lepiota.data`. Predict the recorded poisonous label (one versus zero)
using a linear model trained by squared loss. Predictions are not clipped or
interpreted as calibrated probabilities. The subgroup is **green spore-print
color**, raw column 20 equal to `r` (column numbers include the label at zero).
This physical category is declared before evaluation, not chosen for an observed
method advantage. All 22 predictors are used. Treat `?` as a missing-value
category, not a number or an imputed value.

The dataset contains hypothetical descriptions derived from a field guide, not
independent field measurements. Random-record evaluation cannot establish
performance on new species or real-world utility. Audit duplicate predictor
rows; abort and revise the split protocol if duplicates exist, rather than
silently splitting identical predictors between partitions.

Use 32 independent random permutations for each of two training/validation
sizes, $(256,128)$ and $(2048,1024)$; the remaining records are held-out test
data. Reuse each permutation across sizes so the small training set is nested
within the large one, but analyze each size separately. No label or subgroup
stratification: retain natural missing rare groups. Fit the full one-hot
vocabulary on training predictors only. Unknown categories map to all-zero
blocks. Save the vocabulary, unknown counts, and partition row indices. Use CSR
storage for the one-hot design, and algebraic centering during updates to avoid
densifying the entire design. Centered minibatches need not remain sparse.

Compare `centered_fixed`, `centered_fitted`, and `uncentered_fitted`. No
population-preprocessing oracle is available. Report both held-out half squared
prediction losses, original-scale coefficient paths, the green-indicator
coefficient and its centered contribution, and intercept paths. Full one-hot
encoding is rank deficient; its coefficient paths describe this initialization
and optimizer, not unique or causal feature effects. If green is unseen in
training, its reported coefficient is zero and its vocabulary absence is
flagged.

## Configurations, budgets, and selection

For each arm compare divisors $1$ (`none`), $\sqrt{v_j}$ (`sd`), and
$\sqrt{v_j+0.01}$ (`damped`). Use the constant-column policy above. Fit the
averaged half squared loss. The intercept divisor is one. There is no penalty,
clipping, momentum, adaptive state, schedule, or averaging. Define curvature $L$
as the largest eigenvalue of the empirical scaled-design Gram matrix, including
the constant intercept coordinate only when it is updated. Inactive columns are
zeroed for this calculation. Set $\eta=a/\max(L,10^{-12})$, with

$$
  a\in\{0.001,0.01,0.05,0.2,0.8\}.
$$

Save $L$, the factors, absolute steps, means, divisors, and inactive columns.
This affords equal candidate counts, not equal approximation error to a
continuous optimum or equal mean learning rates. Empirical curvature calibration
does not guarantee stochastic stability.

For synthetic samples use batches $B\in\{1,16\}$ and processed-observation
checkpoints $M\in\{0,128,512,2048\}$. For Mushroom use $B\in\{16,128\}$ and
$M\in\{0,512,2048,8192\}$. Save $k=M/B$ and $n$ separately. Group the same
replacement index stream into different batches. Within each stage comparisons
match $M$; differing $B$ entails differing $k$. Save every coefficient and both
losses at every checkpoint, including all failed candidates. Stop a numerical
path only after nonfinite arithmetic or coefficient magnitude exceeding
$10^{100}$; record that status and all later endpoints as failed, not as omitted
runs.

At each positive budget cap and for each arm, scaling, and validation objective:

- `fixed`: factor 0.05, $B=16$, final checkpoint at the cap.
- `rate_batch`: validation selection of rate and batch at the cap.
- `joint`: validation selection of rate, batch, and stopping at or below the
  cap, including the initialization.

Also select `joint_scaling` over all three scalings, rates, batches, and stops
within each arm. This has three times the candidate search effort and is
reported separately, not credited as a fair single-scaling competitor. Aggregate
and rare selection share all fits and differ only in their validation scores. If
the validation subgroup is empty, explicitly fall back to aggregate selection
and mark that replication. Empty test subgroups produce a missing subgroup loss
and a reported denominator, never zero loss. Do not refit on validation data.

Tie ordering is lower $M$, lower $B$, lower rate, then `none`, `sd`, `damped`.
Failed candidates receive infinite selection loss. A finite selected candidate
must have finite loss on the selection group. Record the initialization fallback
if no eligible finite endpoint exists. Test values are only used after selection
to report outcomes and descriptive hindsight regret against the same finite
candidate set; that oracle is not a training procedure.

Each scaling/arm uses ten training trajectories per replication: two batches
times five rates. At cap $M$, nominal tuning work is $10M$ processed
observations for `rate_batch` and `joint` because checkpoints share
trajectories. Fixed configuration work is $M$. Joint scaling costs $30M$. These
counts exclude validation scoring, Gram-matrix calibration, and preprocessing,
which are reported separately. Distinct data access is always the stated
training and validation sample size; test observations never count as training
work.

## Randomness, reporting, and verification

Use NumPy `SeedSequence([20260916, stage, law_or_size, replication, stream])`.
Stage 0 is synthetic; stage 1 is Mushroom. Synthetic streams 0 and 1 generate
training and validation data, and stream 2 generates replacement indices.
Mushroom stream 0 with size index zero generates the shared permutation; stream
2 with the actual size index generates replacement indices. Replication indices
start at zero. No stochastic optimizer reruns are selected using test results.

Retain paired replicate losses and report means, paired differences, and Monte
Carlo standard errors (sample SD divided by the square root of the number of
complete pairs). For synthetic data this integrates training, validation, and
optimization randomness, while exact test integration adds no test sampling
noise. For Mushroom it describes random partition and optimization variation
conditional on this fixed dataset; overlapping test sets do not yield population
confidence intervals or independent task replications. Report natural train and
validation absence strata, fallback counts, selected boundaries, invalid paths,
and results for both objectives even when they disagree or are noisy. Use all
declared laws and sizes. Do not pool them into a selectively weighted headline.

Check short paths against a separate explicit transformed-design implementation;
check sparse versus dense updates, original-scale predictions, intercept
gradients, training-only preprocessing, constant/unknown columns, empty-group
selection, ties, failures, and selection's independence from test labels.
Recompute archived losses and selections independently, including paired
uncertainty and at least one full replication per law/size. Verify source,
protocol, input, archive, summary, and preserved-study hashes. Build the
manuscript and run the integrated repository checks. Artifacts belong under
`results/practical-selection/`; source data and its attribution belong under
`data/mushroom/`.
