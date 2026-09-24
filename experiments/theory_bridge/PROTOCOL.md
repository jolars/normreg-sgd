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
