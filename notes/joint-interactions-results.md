# First joint-interaction results

## Main finding

**Matching common-feature learning does not match the fitted model.** In the
independent two-feature example, no scaling and standard-deviation scaling use
learning rates 0.008 and 0.002, respectively. These choices give exactly the
same common-coordinate mean trajectory. After 1,000 updates, both common
coefficient means are 0.86494, but the rare coefficient means are 0.14514 and
0.86494. Both true coefficients equal one.

The prediction consequences depend on batch size and stopping. The following are
rare-presence excess risks from the exact moment calculation, with the factor of
one half used in the manuscript:

  | Batch size | Updates | No scaling | Standard-deviation scaling |
  | ---------- | ------- | ---------- | -------------------------- |
  | 1          | 1,000   | 0.354659   | 0.039039                   |
  | 1          | 10,000  | 0.023453   | 0.026263                   |
  | 10         | 1,000   | 0.353352   | 0.013720                   |
  | 10         | 10,000  | 0.021121   | 0.002514                   |

At batch size one, the comparison reverses between 1,000 and 10,000 updates. At
batch size ten, standard-deviation scaling still has lower risk at both reported
endpoints. Each row holds update count fixed, so batch ten consumes ten times as
many observations as batch one. These are comparisons at stated rates, not
comparisons after optimizing each method's learning rate or stopping.

The decomposition explains the late batch-one reversal. At 10,000 updates, the
no-scaling risk is approximately 0.020863 squared bias, 0.000245 variance from
feature sampling, and 0.002346 observation-noise variance. The
standard-deviation-scaled risk is almost entirely observation-noise variance,
0.026263. Its rare signal has been learned more fully, but the larger rare
updates also sustain more noise. Increasing the batch to ten reduces that noise
contribution to 0.002514. The snapshot reversal was identified by inspecting the
declared grid; it is numerical evidence for this model, not a general boundary
theorem.

This comparison connects all four choices: normalization determines relative
coordinate update sizes, the learning-rate calibration matches common-feature
learning, batch size changes update variance, and stopping determines the
remaining bias. The specification contains a draft proof that relative scaling
cannot generally be absorbed into a constant learning rate and stopping count.
That proof still needs independent review.

## Batch comparisons under two budgets

The predeclared comparison uses standard-deviation scaling and step 0.002:

  | Held fixed         | Batch 1: updates / observations | Batch 10: updates / observations | Batch 1 risk | Batch 10 risk |
  | ------------------ | ------------------------------- | -------------------------------- | ------------ | ------------- |
  | 100 updates        | 100 / 100                       | 100 / 1,000                      | 0.421644     | 0.407115      |
  | 1,000 observations | 1,000 / 1,000                   | 100 / 1,000                      | 0.039039     | 0.407115      |

At a fixed update count, the means agree and the larger batch reduces variance.
At a fixed observation budget, the smaller batch performs more updates. Here its
reduction in squared bias outweighs its additional variance. No scaling has the
same batch-order reversal in this comparison, but much slower rare learning and
substantially larger remaining rare-subgroup risk.

Paired direct SGD simulations with 32,768 repetitions give the following
batch-one minus batch-ten rare-risk differences:

- Fixed updates: 0.014601, Monte Carlo standard error 0.000709; exact difference
  0.014529.
- Fixed observations: -0.368174, Monte Carlo standard error 0.000258; exact
  difference -0.368076.

The same underlying ordered observations and response noise are used for each
paired configuration. Simulation uncertainty is reported for the simulation
estimates; the exact moment values have no Monte Carlo sampling error.

## Figures and retained output

- [Mean coefficient paths](../results/figures/joint-mean-paths.svg): relative
  feature learning under four normalization exponents. The nested design also
  shows transient rare-coefficient overshoot, so its paths do not follow the
  independent-coordinate formula.
- [Batch sizes and training
  budgets](../results/figures/joint-batch-budgets.svg): rare risk and its
  squared-bias contribution under both budget conventions.
- Full risk maps for
  [independent](../results/figures/joint-risk-independent.svg) and
  [nested](../results/figures/joint-risk-nested.svg) features show learning rate
  and stopping jointly, with panels for normalization and batch size. Actual
  learning rates and computed moment-stability boundaries are shown.

Each figure also has a PDF with the same basename. The [JSON
summary](../results/joint-interactions.json) and [compressed moment
archive](../results/joint-interactions.npz) retain all 1,056 configurations at
60 stopping counts: 63,360 endpoints. The archive contains original-scale bias,
error second moments, both covariance contributions, and validity flags. The
risk maps label saturation and invalid numerical endpoints; 2,610 endpoints are
flagged nonfinite or invalid. Unstable configurations are retained, including
finite values before numerical overflow.

The full rate grid includes near-zero steps and rates above the moment-stability
threshold. A separately labeled local sensitivity check was added after the
first run: standard-deviation scaling at rate factors 0.001, 0.002, and 0.004,
and observation budgets 500, 1,000, and 2,000. It checks the primary batch
comparison in a neighborhood of its declared setting. It does not establish
robustness of the later normalization-ranking reversal or replace broader
prevalence, signal, and grid-resolution checks.

Both batch-order directions persist in this local check. At 100 updates, the
batch-one minus batch-ten risk difference ranges from 0.00417 to 0.04526 across
the three rate factors. At matched observations, it ranges from -0.39911 to
-0.07238 across the nine rate/budget combinations.

## Validation and interpretation limits

- Exhaustive short gradient paths agree with the new moment calculation in 32
  cases, covering both dependence laws, all four normalization exponents,
  batches one and two, and zero or positive noise variance.
- A separate implementation of the existing manuscript operator checks the
  10,000-update endpoints by iterating one update at a time.
- Additional checks cover global rescaling, batch ordering, stability
  thresholds, covariance decomposition, conditional test risks, and overflow.
- Every directly simulated mean, second moment, and risk falls within the
  predeclared tolerance of six Monte Carlo standard errors. Source hashes,
  dependency versions, seeds, and the archive checksum are recorded.

See the [comparison specification and derivations](joint-interactions.md) for
assumptions and reproduction commands. This is a controlled fresh-sample study
with known preprocessing, one prevalence, one signal, and constant learning
rates. It establishes numerical examples under those assumptions. Independent
proof review is pending because Coterie was unavailable. Practical
preprocessing, schedules, validation-based selection, fixed-data reuse, and
novelty remain separate work.
