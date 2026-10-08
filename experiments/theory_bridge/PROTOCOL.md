# Controlled departures from the oracle model

This study asks which parts of the two opposite oracle orderings remain visible
when individual assumptions are changed. These settings were written before
examining the study's outcomes. The experiment is an exploratory extension of
the existing theorem, not an independent confirmation of a new prediction.

## Model and budget

Independent binary features have prevalences 1/2 and either 0.02 or 0.005. The
coefficients are (0.1, 1) or (1, 0.1), in common/rare order. Responses use
population-centered features and independent standard Gaussian noise. Each
update processes one observation. Caps approximate one, two, and four expected
rare occurrences and satisfy the theorem's scaled-budget interval.

The fixed training pool contains 256 observations. Fresh training uses distinct
independent observations. Replacement training draws indices independently from
the fixed pool and reuses each row's original noise. The pool is the first 256
observations of the saved IID stream, pairing the two sampling procedures. The
entire pool is available for empirical preprocessing, even when the update cap
is below 256. Thus the cap counts SGD observations, not total data access or
preprocessing computation. No estimated-preprocessing arm claims the theorem's
observation budget interpretation.

## Matched interventions

Eight training arms use the same model, data, noise, and rate-search design:

1. Fresh observations, population preprocessing, and a fixed zero intercept.
2. The same fresh setup with a fitted intercept initialized at zero.
3. Replacement sampling, population preprocessing, and a fixed zero intercept.
4. Arm 3 with estimated scales only.
5. Arm 3 with a fitted intercept initialized at zero.
6. Arm 3 with estimated scales and a fitted intercept initialized at zero.
7. Arm 6 with estimated centering.
8. Arm 7 with the fitted intercept initialized at the training response mean.

The unscaled and SD procedures are evaluated separately in every arm. Estimated
variances use denominator 256. A zero empirical variance receives divisor one;
no additional feature-freezing rule is applied. Under empirical centering, a
constant training column has zero gradient automatically. Population centering
is retained in the scale-only intervention. The intercept is never scaled and
uses the same learning rate as transformed coefficients.

## Candidate family and stability

For each preprocessing configuration, let L be the largest squared norm of a
transformed feature vector over all four possible binary cells, including a unit
intercept coordinate when fitted. Rates are eta = t/L, where t is zero or one of
129 geometric values from 0.0001 to 1.9. Every individual homogeneous update is
nonexpansive because eta times its squared feature norm is below two. This is a
conservative candidate family, not a search over all stable rates. For estimated
preprocessing, L and therefore eta depend on the training pool. Each trajectory
nevertheless uses one constant rate throughout training.

Stops include zero, 65 rounded geometric points from one through the largest
cap, and all three caps. A nested coarse search retains every second positive
rate and every second stopping checkpoint, always retaining zero and the caps.
All scalings receive the same number of trajectories. At cap M, nominal search
cost is the number of rates times M per training arm and replication; candidates
share paths across caps, stopping checkpoints, and selection policies. Raw
training data and validation data are additional statistical resources.

## Calibration and selection

Use 2048 calibration replications and 4096 independent evaluation replications.
For each arm, scaling, signal, and cap, select one rate factor and stop by mean
exact population rare risk across the calibration replications. Freeze those
choices before evaluation. This estimates a finite-family optimum, conditional
on a realized calibration run; it is not the theorem's unrestricted oracle. For
the fresh fixed-intercept arm, choose using exact expected moments instead of
the simulated calibration means. Exact moments also quantify the effect of the
rate and stopping grids relative to a denser search over all integer stops.

On each evaluation replication, independently select from the same candidate
paths using rare validation loss with 128, 512, or 2048 independent validation
observations. The validation sets are nested prefixes. An empty rare validation
group falls back to aggregate validation loss. Validation never sees population
risk. Ties favor the earlier stop, then the smaller rate factor.

A separate diagnostic selects the best realized candidate using exact population
rare risk. This per-replication benchmark differs from minimizing risk averaged
over training randomness. It is used only to measure selection regret, not as an
estimate of the theorem's oracle.

## Evaluation and retention

Evaluate excess half squared loss analytically under the four-cell test law,
including the rare subgroup. There is no sampled test set and no clipping.
Report SD-minus-unscaled risk differences, paired Monte Carlo standard errors,
changes between matched arms, grid sensitivity, selected rates and stops,
boundary frequencies, missing-feature counts, and selection regret. Monte Carlo
standard errors condition on the frozen calibration choices. They do not include
uncertainty from estimating those choices or correct for the multiple
comparisons in this exploratory study.

Retain raw feature cells, Gaussian noise, replacement indices, calibration
moment summaries, all selected predictors, their indices, and failure records.
Summarization and plotting never retrain. Numerical checks compare transformed
SGD with independent original-coordinate updates, exact-risk evaluation with
four-cell enumeration, and the fresh simulation with exact expected moments. The
complete protocol includes unresolved comparisons and numerical failures.

## Calibration sensitivity added after review

The sensitivity diagnostic uses only the saved calibration risk sums. For each
prevalence, seed 20260928 generates 100 random partitions of the 32 shards into
two equal groups. Each group contains 1024 replications. Select rate factors and
stops on one half and evaluate the selected candidates on the disjoint other
half, then reverse their roles. Keep the fine candidate family and original tie
rule. The fresh fixed-intercept arm retains exact calibration and exact risk.

The 200 overlapping splits are a descriptive diagnostic at half the original
calibration size, not independent replications or confidence intervals. They
combine variation in selection and held-out evaluation. The original evaluation
and its conditional MCSEs remain unchanged. Retain all partitions, selected
indices, and held-out risks in `calibration-sensitivity.npz`, with settings and
row summaries in `calibration-sensitivity.json` under `results/theory-bridge/`.
Run `task experiment:calibration-sensitivity` to reconstruct this diagnostic
without training, and `task check:calibration-sensitivity` to verify it.

## Selection-gain analysis added after review

Use the saved evaluation predictors for both fresh arms, both prevalences, all
three caps, and both signals. Define gain as calibrated minus selected
population rare risk for the same scaling and run. Analyze exact-risk selection
and all three validation sizes. Retain gain quantiles, paired U-minus-SD gain
differences and MCSEs, counts of positive, zero, and negative gains, and the
share of positive gain contributed by the largest 10% of gains. These
descriptive finite-family gains condition on the frozen calibration choices.
Their means under exact selection combine theoretical adaptation gains (the
difference between the minimum expected risk and the expectation of minimum
risk) with calibration suboptimality. The latter is zero for the baseline's
exact moment calibration and is not identified for the fitted-intercept arm. The
theorem optimizes deterministic rates and stops and does not cover adaptive
selection.

Evaluate each saved predictor on the two rare cells. Record its signed mean
prediction error in the rare subgroup and common-coefficient error, including
their root mean squares. The rare mean error combines the intercept and
rare-coefficient effects; this analysis does not test cancellation between them.
Retain per-run risks, gains, and errors in `selection-gains.npz` and all setting
summaries in `selection-gains.json` under `results/theory-bridge/`. Generate the
manuscript table in `paper/generated/selection-gains.tex` from these summaries.
Run `task experiment:selection-gains` without retraining, then
`task check:selection-gains` to verify the results using independent rare-cell
predictions and the existing risk-change summaries.

## Rare-risk decomposition added after the gain analysis

Separate the centered intercept error from the rare-coefficient error for every
saved predictor in the same two fresh arms. For the predictor
`a + b_C (I - 1/2) + b_R (J - q)`, the true intercept is zero. Recover `a` from
the saved raw intercept as `raw_intercept + b_C/2 + q*b_R`, and define
`e_C = b_C - beta_C` and `d = (1-q)*(b_R-beta_R)`. Decompose rare excess half
loss into `e_C^2/8`, `a^2/2`, `d^2/2`, and `a*d`. Preserve the baseline's exact
zero centered intercept when converting from raw coordinates.

Retain per-run errors and terms, their means and MCSEs, paired SD-minus-U gap
contributions, and changes relative to calibration. Summarize opposing signs and
cancellation as `-a*d / ((a^2+d^2)/2)`, defining it as zero when both errors are
zero. Also report the pooled fraction, taking means before division. Check
whether the cross term accounts for the primary reversal and whether the same
explanation holds across prevalence, cap, signal, and selector. Omitting the
cross term is an accounting diagnostic, not a predictor risk. Setting the
centered intercept to zero in an already selected predictor is a separate
intervention without retraining or reselection; it does not recover the
fixed-intercept training arm. This descriptive analysis does not identify causal
training effects or resolve calibration suboptimality.

Run `task experiment:risk-decomposition` to write `risk-decomposition.npz` and
`risk-decomposition.json` under `results/theory-bridge/` and the generated
manuscript table in `paper/generated/risk-decomposition.tex`, without training.
Run `task check:risk-decomposition` to verify all 120 setting–policy
combinations using independent four-cell predictions, saved risks, and selection
gains.
