# Controlled rare-subgroup prediction pilot

## Assessment

Fixed scaling changes rare-subgroup prediction substantially in some of these
small, controlled problems. The direction reverses with signal, dependence,
batch size, and budget. The pilot supports a concrete illustration of a familiar
early-stopping and preconditioning tradeoff. It does not establish a generally
better scaling rule, robustness beyond the specified grid, or novelty.

For example, at prevalence 0.01, independent features, and 400 processed
observations, standard-deviation scaling reduces rare-only GD risk by 0.58017
(paired Monte Carlo standard error 0.01517). On the same design with a
common-only signal, it increases risk by 0.14895 (0.01301). These differences
are substantial relative to the fixed observation-noise variance of one. The
first comparison uses just one GD update. The complete tables below include
reversals and small differences, and the JSON retains all 864 evaluated settings
and 7,776 tuning-candidate endpoints.

On the equal-weight average over all 24 design/signal cases, the GD advantage of
standard-deviation scaling at 400 observations reverses by 8,000 observations.
For replacement SGD with batch size one, the corresponding average advantage
already reverses at 2,000 observations. Those averages assign an arbitrary equal
weight to the declared cases; they are descriptive summaries of this grid.

## Frozen protocol

The design, damping, seeds, objective, and nine learning-rate factors were fixed
and communicated before inspecting evaluation outcomes. The implementation is
[run_rare_subgroup_pilot.py](../experiments/run_rare_subgroup_pilot.py); the
generated artifact is
[rare-subgroup-pilot.json](../results/rare-subgroup-pilot.json).

Let the binary features be $(W,J)$, with common prevalence $p = 1/2$ and rare
prevalence $q \in \{1/20,1/100\}$. Each training dataset has $n = 400$
observations. The population law has the following exact joint-cell counts
divided by 400. The fixed training design contains precisely those counts,
ordered by cell.

  | $q$  | Dependence  | $(0,0)$ | $(0,1)$ | $(1,0)$ | $(1,1)$ |
  | ---- | ----------- | ------: | ------: | ------: | ------: |
  | 0.05 | Independent |     190 |      10 |     190 |      10 |
  | 0.05 | Nested      |     200 |       0 |     180 |      20 |
  | 0.05 | Negative    |     180 |      20 |     200 |       0 |
  | 0.01 | Independent |     198 |       2 |     198 |       2 |
  | 0.01 | Nested      |     200 |       0 |     196 |       4 |
  | 0.01 | Negative    |     196 |       4 |     200 |       0 |

Nested means $J = 1$ implies $W = 1$. Negative association is the feasible
disjoint boundary $\Pr(W = 1,J = 1) = 0$. All six centered Gram matrices are
positive definite. Thus these are actual feasible binary designs, including
boundary cells with zero probability, rather than formal covariance choices.

Use known population centering $x = (W - p,J - q)^\top$, response
$y = x^\top\beta^* + \varepsilon$, and signals $(1,0)$, $(0,1)$, $(1,1)$, and
$(1,-1)$. The intercept is fixed at zero in these centered coordinates.
Original-scale coefficients start at zero. Observation noise is iid Gaussian
with variance one. Each comparison reuses exactly the same fixed noisy
observations. Neither features nor responses are centered again using realized
noise.

For coordinate variance $v_j$, the feature presented to the optimizer is
$z_j = x_j/s_j$. The four **divisors** are:

- No scaling: $s_j = 1$.
- Standard-deviation scaling: $s_j = \sqrt{v_j}$.
- Variance scaling: $s_j = v_j$.
- Damped scaling: $s_j = \sqrt{v_j + 0.01}$, with damping fixed at 0.01 in
  variance units before evaluation.

Scales remain fixed. Predictions use the same population centering and scales as
training; there is no prevalence shift. The original-scale estimate is
$\beta = S^{-1}\theta$. Loss is half the averaged training squared error, so a
full GD update is $\beta \leftarrow \beta - \eta S^{-2}X^\top(X\beta - y)/n$.
There is no momentum, clipping, weight decay, adaptive state, or iterate
averaging. SGD samples indices independently and uniformly **with replacement**
within and across batches, conditional on the entire noisy dataset. A repeated
index retains its response noise.

  | Processed observations | GD updates ($n$ per update) | SGD updates ($B = 1$) | SGD updates ($B = 20$) |
  | ---------------------: | --------------------------: | --------------------: | ---------------------: |
  |                    400 |                           1 |                   400 |                     20 |
  |                  2,000 |                           5 |                 2,000 |                    100 |
  |                  8,000 |                          20 |                 8,000 |                    400 |

All budgets divide the per-update cost exactly; no partial batches or rounding
are needed. Counts describe the optimization paths whose moments are computed,
not the runtime of the exact moment algorithm.

### Oracle learning-rate tuning

For every design, signal, optimizer, scaling, and budget separately, select one
constant step from $\eta = a/\lambda_{\max}(S^{-1}CS^{-1})$, where
$C = X^\top X/n = E[xx^\top]$ and

$$
  a \in \{0.001,0.003,0.01,0.03,0.1,0.3,0.7,1.5,2.5\}.
$$

The objective is mean rare-presence excess squared prediction risk over 32
independent tuning datasets. This is **oracle risk tuning**: the true signal and
test cell law are known, and sampled-index moments are integrated exactly. It is
not a deployable validation rule or a test of validation-based stopping. Every
comparison receives the same nine candidates and 32 tuning datasets. Its nominal
tuning cost at a budget $M$ is $9 \times 32 \times M$ processed observations.
The exact implementation can compute those endpoints without simulating those
paths. The tuning datasets contain $32n$ distinct noisy observations per design
and are shared across candidates and signals.

Ties select the first minimum in the increasing rate grid. An endpoint with
nonfinite moments, or conditional covariance with an eigenvalue below
$-10^{-8}\max(1,\max_{ij}|E[e_i e_j]|)$, receives infinite tuning objective and
is retained with its failure count. No finite replicate is silently removed from
a candidate's objective. Asymptotic homogeneous second-moment instability is
separately recorded and does not disqualify a finite-horizon endpoint.

The 256 evaluation datasets use disjoint seeds. NumPy generates each noise
vector with `default_rng(SeedSequence([seed, design_id]))`, in the cell order
above. Design IDs 0--5 follow table order. Tuning seeds are 10000--10031;
evaluation seeds are 20000--20255. The same noise vector is shared across all
methods, scalings, and signals within a design and stage. No index-sampling or
test-sampling seeds are needed because those expectations are exact.

## Risks, moments, and uncertainty

Let $e = \beta - \beta^*$ and $V_D = E_D[ee^\top]$, conditional on the fixed
noisy dataset $D$. Risks in this note omit the factor of one half:

$$
  R_D = \operatorname{tr}(CV_D),
  \qquad
  R_{D,R} = \operatorname{tr}(C_R V_D),\qquad C_R = E[xx^\top \mid J = 1].
$$

They measure excess squared prediction error and exclude irreducible test noise.
They are expectations under a new test point from the same population, with
fixed population preprocessing. Crucially, $C_R$ is the conditional **second
moment**, including the nonzero conditional feature mean, not the conditional
covariance. For an isolated rare-coefficient error of one, aggregate risk is
$q(1 - q)$ and rare-presence risk is $(1 - q)^2$. At $q = 0.01$, the subgroup
weights that error 99 times as heavily as the aggregate objective.

All coefficient means, second moments, covariance matrices, per-coordinate MSE,
and summed coefficient MSE in the JSON are on the original feature scale. For
the 256-dataset mixture, coefficient bias is the average conditional mean. The
reported covariance is the average conditional sampling covariance plus the
covariance of conditional means across training-noise datasets. The latter uses
denominator 256 to preserve the finite-mixture decomposition exactly; it is a
plug-in estimate, not an unbiased population covariance estimator. Every record
also retains exact moments conditional on evaluation seed 20000.

For a conditional risk $r_D$, reported Monte Carlo standard error (MCSE) is the
sample standard deviation of its 256 values divided by $\sqrt{256}$. Paired
contrasts use the corresponding differences within each noisy dataset. There is
no Monte Carlo error from replacement-index sampling or test integration. MCSE
quantifies uncertainty across training noise, conditional on the fixed design
and the rates selected by the realized tuning sample. It excludes tuning-sample
variation, random-design variation, and uncertainty in estimated preprocessing.
Approximate normal intervals could use mean plus or minus 1.96 MCSE; they would
be pointwise, not simultaneous across the grid.

### Conditional calculation

In scaled coordinates let $u = S(\beta - \beta^*)$ and augment it by a constant
one. For observation $i$, define

$$
  A_i = \begin{pmatrix}
          I - \eta z_i z_i^\top & \eta z_i\varepsilon_i \\
          0                     & 1
        \end{pmatrix},\qquad w
      = (u^\top,1)^\top.
$$

An SGD batch applies the average of its $A_i$ matrices. Independent replacement
gives the exact second-moment operator

$$
  \mathcal L_B(U)
  = \bar A U\bar A^\top
    + \frac1B\left( \frac1n\sum_i A_i U A_i^\top - \bar A U\bar A^\top \right).
$$

Taking its $k$th matrix power in nine-dimensional vectorized coordinates gives
the moments at each budget. The off-diagonal augmented blocks preserve the
empirical score and curvature-noise cross terms required by [the conditional
replacement identities](sampling-schemes.md). Grouping observations into four
cells uses both within-cell noise means and second moments, so it preserves
individual observation-noise variation. GD uses $\bar A^k$ directly. This is
fixed-data reuse, not fresh-sample SGD.

## Complete grid summaries

Each cell below is mean risk (MCSE), averaged equally over all six designs and
four signals. To retain correlations induced by shared noise across signals, the
implementation averages the 24 conditional risks within each noise replication
before calculating MCSE. Casewise outcomes and paired contrasts are in the JSON;
these tables do not select favorable cases.

### Rare-presence excess squared prediction risk

  | Method    | Observations | None              | Std. dev.         | Variance          | Damped            |
  | --------- | -----------: | ----------------: | ----------------: | ----------------: | ----------------: |
  | GD        |          400 | 0.29536 (0.00133) | 0.15654 (0.00257) | 0.19481 (0.00240) | 0.17042 (0.00261) |
  | GD        |         2000 | 0.20276 (0.00231) | 0.11397 (0.00309) | 0.14154 (0.00368) | 0.11613 (0.00354) |
  | GD        |         8000 | 0.10218 (0.00225) | 0.11522 (0.00343) | 0.13078 (0.00460) | 0.11902 (0.00330) |
  | SGD, B=1  |          400 | 0.22752 (0.00237) | 0.21194 (0.00270) | 0.25535 (0.00284) | 0.22283 (0.00184) |
  | SGD, B=1  |         2000 | 0.13839 (0.00353) | 0.15651 (0.00448) | 0.19143 (0.00451) | 0.15059 (0.00327) |
  | SGD, B=1  |         8000 | 0.12569 (0.00356) | 0.17948 (0.00595) | 0.19953 (0.00595) | 0.16618 (0.00576) |
  | SGD, B=20 |          400 | 0.21447 (0.00166) | 0.22132 (0.00231) | 0.25940 (0.00219) | 0.19160 (0.00239) |
  | SGD, B=20 |         2000 | 0.12655 (0.00224) | 0.15134 (0.00350) | 0.17981 (0.00302) | 0.12816 (0.00294) |
  | SGD, B=20 |         8000 | 0.10583 (0.00301) | 0.12897 (0.00288) | 0.15220 (0.00334) | 0.11796 (0.00373) |

### Aggregate excess squared prediction risk

  | Method    | Observations | None              | Std. dev.         | Variance          | Damped            |
  | --------- | -----------: | ----------------: | ----------------: | ----------------: | ----------------: |
  | GD        |          400 | 0.12843 (0.00074) | 0.06122 (0.00018) | 0.16123 (0.00009) | 0.06674 (0.00027) |
  | GD        |         2000 | 0.03517 (0.00073) | 0.02939 (0.00015) | 0.10721 (0.00014) | 0.02345 (0.00011) |
  | GD        |         8000 | 0.01481 (0.00010) | 0.02905 (0.00014) | 0.08252 (0.00015) | 0.02761 (0.00013) |
  | SGD, B=1  |          400 | 0.03603 (0.00012) | 0.04057 (0.00017) | 0.12984 (0.00015) | 0.03808 (0.00016) |
  | SGD, B=1  |         2000 | 0.01303 (0.00010) | 0.00935 (0.00014) | 0.11101 (0.00016) | 0.00806 (0.00012) |
  | SGD, B=1  |         8000 | 0.00679 (0.00011) | 0.00587 (0.00012) | 0.05830 (0.00019) | 0.00574 (0.00012) |
  | SGD, B=20 |          400 | 0.04316 (0.00010) | 0.05173 (0.00017) | 0.14108 (0.00013) | 0.04541 (0.00015) |
  | SGD, B=20 |         2000 | 0.01759 (0.00010) | 0.03703 (0.00015) | 0.11647 (0.00013) | 0.02272 (0.00013) |
  | SGD, B=20 |         8000 | 0.00672 (0.00010) | 0.03181 (0.00016) | 0.10022 (0.00015) | 0.01439 (0.00012) |

### Signal and dependence reversals at the smaller prevalence

The following table includes **all** dependence/signal cases at $q = 0.01$ and
the first budget of 400 observations. Entries are standard-deviation scaling
minus no scaling in rare-presence risk (paired MCSE). Negative values favor
standard-deviation scaling. This table shows interactions that the averages
hide; neither a sign nor a small MCSE is a novelty assessment.

  | Dependence  | Signal        | GD                 | SGD, B=1           | SGD, B=20          |
  | ----------- | ------------- | -----------------: | -----------------: | -----------------: |
  | Independent | common-only   | +0.14895 (0.01301) | +0.15770 (0.00300) | +0.18580 (0.00663) |
  | Independent | rare-only     | -0.58017 (0.01517) | -0.11667 (0.00574) | -0.04318 (0.00076) |
  | Independent | equal-sign    | -0.67977 (0.01690) | -0.08685 (0.00634) | +0.03652 (0.00158) |
  | Independent | opposite-sign | -0.67022 (0.01722) | -0.05849 (0.01134) | +0.03658 (0.00158) |
  | Nested      | common-only   | +0.05161 (0.00360) | +0.07938 (0.00405) | +0.09435 (0.00440) |
  | Nested      | rare-only     | -0.54764 (0.01475) | -0.09672 (0.00538) | -0.02113 (0.01405) |
  | Nested      | equal-sign    | +0.12201 (0.01014) | -0.08449 (0.00489) | -0.01876 (0.01617) |
  | Nested      | opposite-sign | -0.00095 (0.00266) | -0.15602 (0.00721) | -0.00971 (0.00149) |
  | Negative    | common-only   | +0.05568 (0.00405) | +0.08015 (0.00422) | +0.10509 (0.00509) |
  | Negative    | rare-only     | -0.54107 (0.01693) | -0.10636 (0.00751) | -0.02499 (0.00112) |
  | Negative    | equal-sign    | -0.00049 (0.00003) | -0.15066 (0.00823) | -0.00957 (0.00055) |
  | Negative    | opposite-sign | +0.14293 (0.01187) | -0.08518 (0.00773) | +0.01027 (0.01793) |

The GD rare-only improvements occur across all three dependencies at this
budget, but the common-only effects go the other way. Dependence also reverses
the equal-sign and opposite-sign comparisons. At $q = 0.01$ with $B = 20$, the
nested opposite-sign and negative equal-sign improvements are precisely measured
but only about 0.01 in absolute risk. Small changes need not be consequential
even when precisely measured. The nested rare-only, nested equal-sign, and
negative opposite-sign differences are within two MCSE of zero. These are
informative limited-precision outcomes, not evidence of equality.

Across all 24 cases at budget 8,000, standard-deviation scaling has higher rare
risk than no scaling by more than two paired MCSE in 23 cases for $B = 1$; the
remaining case is within two MCSE. This is descriptive, without a
multiple-comparison correction. It is also sensitive to the available constant
steps, discussed next.

## Instability and limits of the comparison

All 864 selected evaluation endpoints have finite valid moments. Of 7,776
tuning-candidate endpoints, 2,160 have homogeneous second-moment spectral radius
at least one; 1,028 have nonfinite or invalid moments. The JSON retains the
spectral radius, finite/invalid status, and replicate failure counts for every
candidate. The instability count includes endpoints at different budgets for the
same rate; it does not represent 2,160 independent datasets.

Nine selected endpoints have asymptotic homogeneous instability. All nine are GD
with no scaling and the largest rate factor 2.5, evaluated after one or five
updates. A short-horizon oracle can select such a step, so reporting only
asymptotically stable selections would alter the declared objective. These
choices provide no long-run convergence guarantee.

The smallest grid factor is selected in 195 of 864 settings, and the largest in
nine. Thus the finite grid is a material limitation: some optima may be outside
it, especially at long budgets or when near-zero steps avoid fitting rare noise.
No candidate grid or damping was changed after evaluation. The observed
reversals do not establish the ordering of continuously optimized learning
rates. The grid is relative to largest curvature; it affords equal candidate
effort, not equal approximation error to each continuous optimum.

Further limits are the two prevalences, fixed rare counts of four or twenty,
known preprocessing and intercept, two-dimensional fixed features, constant
steps, final iterates, a single fixed noise variance, and oracle tuning. Signal
variance changes with the signal and prevalence, so these are not SNR-matched
comparisons. Noise replications condition on exact cell counts; there is no
training-design sampling uncertainty. These outcomes do not test joint
fresh-observation budget theorems, adaptive optimizers, reshuffling, fitted
intercepts, empirical scales, validation rules, or real data.

The pilot therefore clears a narrow numerical milestone: fixed scaling can
matter for a stated rare-subgroup objective at equal processed counts, with
controlled examples of benefit, harm, and small differences. Its reversals and
prior theoretical overlap favor a focused illustrative role unless a stronger
result survives separate theory, literature, and empirical review. Numerical
agreement is neither proof nor evidence of originality.

## Reproduction and validation

Run ordinary Python, without `-O`:

```sh
devenv shell -- python experiments/check_rare_subgroup_pilot.py
devenv shell -- make check-python check-optimization
devenv shell -- python experiments/run_rare_subgroup_pilot.py
devenv shell -- python experiments/run_rare_subgroup_pilot.py --output /tmp/rare-subgroup-pilot.json
cmp results/rare-subgroup-pilot.json /tmp/rare-subgroup-pilot.json
devenv shell -- panache format --check notes/rare-subgroup-pilot.md
devenv shell -- panache lint notes/rare-subgroup-pilot.md
```

The focused check first failed because the new implementation was absent. It now
independently enumerates every ordered batch and every path through two updates
on a tiny eight-observation noisy dataset, for GD and replacement batches of one
and two under all four scalings. Direct loss gradients give the reference
coefficients, and direct support integration gives both risks. It also checks
cell feasibility, centering, standardization, prediction-scale conversion, the
isolated rare-error weights, and convergence of reused noisy GD to the dataset's
OLS coefficient. Finally, it compares the new matrix-power implementation at the
8,000-observation budget with the existing empirical score/cross-term recurrence
applied one update at a time.

Maximum absolute discrepancy was $2.65 \times 10^{-14}$, using relative
tolerance $2 \times 10^{-10}$ and absolute tolerance $2 \times 10^{-11}$. The
established optimization checks and Ruff pass inside `devenv shell`. A further
failing check exposed overflow when computing MCSE for extreme but finite
unstable endpoints; rescaling before computing means and standard deviations
corrected the summary without changing the candidate grid or any selected
learning rate. A second run reproduced the artifact byte for byte. The artifact
records Python, NumPy, and SciPy versions; SHA-256 hashes of both scripts and
`uv.lock`; all designs and scaled Gram matrices; noise-vector hashes; seeds;
settings; and reproduction commands. Regenerate numerical values and provenance
with the script; do not edit the JSON by hand.
