# Research plan

Working direction: **Normalization and Implicit Regularization in Stochastic
Learning**. Revised September 15, 2026. The task checklist is in
[TODO.md](../TODO.md).

## Central question

**How do normalization, learning rate, batch size, and stopping time jointly
determine the fitted model and its statistical properties?**

The project studies the interaction among all four choices: which features are
learned, how their coefficients evolve, how training noise enters the model, and
what predictions result. The goal is to explain this joint behavior across data
distributions and training regimes. Choosing hyperparameters is one application
of that understanding. The analysis must retain the trajectories and tradeoffs
that disappear when only the best tuned endpoint is reported.

Common and rare features provide an interpretable starting point. Their
different frequencies expose how normalization allocates learning across
coordinates, how batch composition affects stochastic updates, and how stopping
changes the balance between incomplete learning and noise. Dependence between
features is central because it can couple their learning and change the effects
of each training choice.

## Connection to the original paper and the ML objective

The foundation is Johan Larsson and Jonas Wallin's *The Choice of Normalization
Influences Shrinkage in Regularized Regression*, in the neighboring `normreg`
repository. That paper studies how normalization changes the fitted model
through explicit regularization, including binary-feature prevalence,
penalty-specific bias, variance, mixed feature types, and interactions. It
already proposes treating normalization as a hyperparameter and evaluates tuning
a normalization exponent.

This follow-up carries that statistical viewpoint into SGD and implicit
regularization. Feature scaling changes the geometry of the updates; learning
rate, batch size, and stopping determine how that geometry affects the trained
predictor. The intended ML contribution is an explanation of their joint
effects, supported by controlled theory and experiments that connect to finite
training budgets and practical learning procedures.

Here, implicit regularization concerns the statistical effects of the training
procedure, including finite-time bias and stochastic updates. Whether these
effects improve generalization is an outcome to investigate. Keep full-rank
convergence to OLS, finite-time regularization, and selection among
overparameterized interpolating solutions distinct. Begin with the first two;
interpolation is a possible later extension.

The original paper remains the conceptual foundation. Its explicit-penalty
calculations also provide comparisons for interpreting the effects of training.
A general extension of every shrinkage theorem is a separate project branch.

## Joint configuration and statistical outcomes

For a stated data-generating model, initialization, preprocessing convention,
and sampling scheme, study the relationship

$$
  \left( S,\{\eta_j\}_{j=0}^{k-1},B,k \right)
  \longmapsto \mathcal L(\hat\beta_k)
  \longmapsto \text{coefficient and prediction properties}.
$$

Here $S$ is the diagonal matrix of feature divisors, $\eta_j$ the learning rate
at update $j$, $B$ the batch size, and $k$ the stopping update. The law
$\mathcal L$ must identify which randomness is included: sampled training
designs, observation noise, or sampled optimization indices. Fixed-data
conditional results and averages over training datasets answer different
questions.

### Initial model

Start with squared-loss linear regression and feasible common and rare binary
features. Use known population centering and scales, a fixed known intercept,
and zero initialization for the first analytical comparisons. For centered
features $x$ and the response after subtracting the known intercept, write

$$
  y = x^\top\beta^* + \varepsilon,
  \qquad
  E(\varepsilon \mid x) = 0,\qquad C = E(xx^\top).
$$

First use fixed conditional noise variance
$E(\varepsilon^2 \mid x) = \sigma^2 > 0$ and hold the original-scale signal
fixed across paired training configurations. Study changes in noise level and
signal-to-noise matching separately.

For fixed empirical designs use $C = X_c^\top X_c/n$. Identify whether the
centering in $X_c$ is known population centering or estimated training
centering. The averaged training loss includes the factor $1/2$.

Dividing features by positive $s_j$ gives $S = \operatorname{diag}(s)$,
$\theta = S\beta$, and $P = S^{-2}$. A batch update on the original coefficient
scale is

$$
  \beta_{j+1}
  = \beta_j
    + \frac{\eta_j}{B}P\sum_{i \in \mathcal B_j} x_i(y_i - x_i^\top\beta_j),
$$

where repeated indices retain multiplicity. State whether observations are
fresh, sampled with replacement from a fixed noisy dataset, or shuffled across
epochs. A repeated training observation retains its response noise. Population
gradient flow supplies the comparison

$$
  \dot\beta(T) = PC\{\beta^* - \beta(T)\}.
$$

For binary coordinate variance $v_j = q_j(1 - q_j) > 0$, start with the family
$s_j = v_j^\delta$. It includes no scaling at $\delta = 0$, standard-deviation
scaling at $\delta = 1/2$, and variance scaling at $\delta = 1$. Include damped
scaling with an explicit damping convention. Record actual divisors and
centering order for named software normalizations. For example, max-abs scaling
on uncentered binary data containing ones uses divisor one; applying it after
centering is a different convention.

Start with one common and one rare feature under independent, nested, and
negatively associated feasible joint laws. Vary common-only, rare-only,
equal-sign, and opposite-sign signals. Extend to a fixed common block after the
two-feature mechanisms are understood. Changing covariance or prevalence must
respect actual joint-cell probability bounds.

### Outcomes

Measure original-scale coefficient means, bias, covariance, and mean squared
error. Separate incomplete learning, dependence-induced contributions,
multiplicative update variance, and observation noise where the model permits
that decomposition. Describe the learning of common and rare signals with a
stated coefficient-error criterion. Nonzero GD coefficients alone do not define
feature selection; any thresholded selection metric needs an explicit rule.

For $V = E[(\hat\beta_k - \beta^*)(\hat\beta_k - \beta^*)^\top]$, report
aggregate and rare-presence excess prediction risks under a stated test law:

$$
  R = \tfrac12\operatorname{tr}(CV),
  \qquad
  R_R = \tfrac12\operatorname{tr}(C_RV),\qquad C_R = E[xx^\top \mid J = 1].
$$

The test point is independent of training. The conditional second moment $C_R$
includes the nonzero conditional mean. Risk excludes irreducible test noise. The
existing pilot omits the factor $1/2$; convert or label that convention when
comparing its values with manuscript risks. Aggregate and subgroup objectives
can give different assessments of the same trained model.

## Scientific questions

1. **Normalization and learning rate.** How does their combination determine
   relative learning across common and rare features? Identify exact
   reparameterizations, approximate equivalences, and effects that remain when
   relative coordinate scales change. Use global rescaling as a basic control.
2. **Normalization, learning rate, and batch size.** How do feature frequency,
   dependence, and batch composition affect gradient fluctuations, stability,
   and coefficient error? Determine what the batch-rarity product $Bq$ explains
   and what additionally depends on the feature distribution.
3. **Stopping and the fitted model.** How do these interactions evolve along the
   training path? Identify when incomplete common or rare learning dominates,
   when noise dominates, and when comparisons between normalization rules change
   direction. Constant steps come first; specified decreasing schedules follow.
4. **Dependence and prediction.** How does incomplete learning of one feature
   affect another feature's coefficient and the resulting predictions? Relate
   coefficient effects to aggregate and rare-subgroup risk under the same stated
   test law.
5. **Selection of a training configuration.** Once the joint behavior is
   understood, what do fixed defaults, separate tuning, and joint tuning achieve
   for a specified objective and budget? Preserve fixed-configuration results
   alongside tuned summaries so that tuning does not hide the mechanisms being
   studied.

These are research questions. Improvements from normalization, simple rules for
choosing settings, and persistent risk reversals are possible findings to test,
not assumed conclusions.

## Comparisons and resource accounting

Different comparisons isolate different interactions. Specify what is held fixed
before interpreting a change in performance.

  | Comparison                                | What it addresses                                                                                                             |
  | ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
  | Same update count $k$                     | How update size, scaling, and gradient noise change the path; larger batches process more observations.                       |
  | Same processed observations $M = kB$      | How batch size trades fewer updates against averaging within an update. Full empirical GD costs $n$ observations per update.  |
  | Same cumulative step size $\sum_j\eta_j$  | Whether a flow-time comparison explains the mean trajectory; discrete dynamics and stochastic moments still require checking. |
  | Same dataset and paired observation noise | How training choices act on a fixed learning problem, including repeated passes.                                              |
  | Same tuning effort                        | How fixed defaults and configuration-selection procedures compare under a declared search budget.                             |

Use $n$ for the number of distinct training observations, $M$ for processed
observations, $k$ for update count, and $T$ for flow time. For constant steps,
$T = k\eta$ is a flow-time calibration. Fresh-sample runs consume new
observations, whereas fixed-data runs may have $M > n$. Matching $M$ alone does
not match access to distinct data across these sampling schemes. Report both.
Wall-clock time is a separate measure with hardware and implementation details.

Show absolute learning rates together with any curvature-normalized or
stability-normalized rate. A change in normalization can alter both reference
quantities. State the calibration used in each comparison and retain unstable
and nonfinite outcomes.

## Existing results and their role

The completed work supplies analytical tools and a pilot for the joint study.
Its mathematical and numerical status is separate from its role in the eventual
contribution.

  | Existing work                                                                       | Established scope                                                                                                                                        | Use in the joint study                                                                                                                     |
  | ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
  | [Population flow](../paper/sections/gradient-flow.tex)                              | Bivariate and fixed common-block rare limits under known population preprocessing, on bounded flow-time intervals.                                       | Explain relative learning and transient contributions from dependent features.                                                             |
  | [Discrete moments](../paper/sections/discrete-dynamics.tex)                         | Exact finite-update GD and fresh-SGD mean and covariance formulas.                                                                                       | Calculate how normalization, steps, batches, and stopping jointly determine error.                                                         |
  | [Stochastic stability](../paper/sections/stochastic-gradient.tex)                   | Scalar threshold and bounded-common-block batch-rarity limits under stated population assumptions.                                                       | Delimit stable configurations and study their statistical consequences along training paths.                                               |
  | [Sampling schemes](sampling-schemes.md)                                             | Matched-covariance binary examples, conditional replacement identities, and reshuffling epoch identities.                                                | Identify distributional and sampling effects that a population mean path cannot capture.                                                   |
  | [Joint-budget theorem](joint-budget-limits.md) and [review](joint-budget-review.md) | Independently reviewed result for two binary features, standard-deviation scaling, $q_n = n^{-1/2}$, and a specified decreasing-step fresh-SGD schedule. | Provide a checked joint limit and error decomposition. Comparisons across normalization, batch size, and schedules remain to be developed. |
  | [Controlled pilot](rare-subgroup-pilot.md)                                          | Reproduced comparison of four scalings, three GD/SGD methods, three budgets, six fixed binary designs, and four signals.                                 | Locate candidate interactions and reversals for analytical explanation and sensitivity checks.                                             |
  | [Initial dependence investigation](two-feature-investigation.md)                    | Explicit-penalty calculations beyond orthogonality, with Gaussian region integration and binary examples.                                                | Connect the original paper's modeling perspective to dependence and explicit-regularization comparisons.                                   |

The budget theorem gives rare-coefficient MSE asymptotic to $4\sigma^2/(3nq_n)$
under its specified regime, with smaller bias and multiplicative variance. That
establishes one attainable error limit. It does not compare the four training
choices over their joint range.

The pilot uses known preprocessing, fixed rare counts of 4 or 20, and separate
oracle constant-step tuning. Of 864 evaluated settings, 195 select the smallest
grid factor. Its reported reversals motivate further analysis; their robustness
to a wider rate range and practical tuning remains unresolved. Preserve the
frozen pilot and its provenance when designing the next experiment.

## Next research steps

### 1. Specify the joint comparisons

Write `notes/joint-interactions.md` defining the initial normalization family,
step schedules, batches, stopping counts, sampling laws, and risk objectives.
Use the existing two-feature setup and include both fixed-update and
fixed-observation comparisons. Derive and independently check the global-scale
and learning-rate equivalence as a control, then separate it from changes in
relative feature scales.

**Completion criterion:** every proposed comparison identifies its assumptions,
fixed quantities, varied quantities, and measured outcomes. Its connection to
the original paper and the five scientific questions is explicit.

### 2. Explain joint behavior in a controlled model

Apply the existing finite-update moments to constant-step SGD with two feasible
binary features. Begin with an independent design, then add dependence. Analyze
several normalization exponents, batch-rarity regimes, and stopping counts.
Locate conditions for changes in coefficient learning and risk comparisons;
distinguish derived boundaries from numerical patterns. Extend to decreasing
steps or a common block only when the added complexity answers a specific
interaction question.

**Completion criterion:** at least one precise comparison across normalization
and optimization settings, with a full proof and independent numerical check, or
a checked equivalence or counterexample that rules out a proposed mechanism. A
result about one fixed configuration must state what it contributes to the
comparison.

### 3. Map and test the predicted interactions

Build on the pilot with a separately declared experiment. Retain results over
the joint configuration grid before selecting any optimum. Include near-zero
steps and enough stopping points to resolve incomplete learning and noise
effects. Plot coefficient trajectories and risk over learning rate and stopping
count, faceted by normalization and batch size. Annotate theoretical stability
boundaries and compare fixed updates with fixed processed observations.

Use paired data and noise, report Monte Carlo uncertainty, and preserve failed
runs. Separate fixed cell counts from sampled designs and fresh observations
from fixed-data reuse. Check conditional moments against direct update paths on
small cases before expanding the grid.

**Completion criterion:** reproducible evidence for or against the proposed
interactions, including unfavorable and null outcomes, uncertainty, and
sensitivity to the grid. Changes in rankings alone require a mechanism or a
clearly stated unresolved explanation.

### 4. Test practical consequences

After the controlled comparisons, study training-estimated centering and scales,
intercept handling, and samples with no rare observations. Compare fixed
stopping with a stated validation rule. Evaluate joint normalization and
optimization tuning with separate validation and test data and comparable search
effort.

Choose a sparse text or categorical task with an interpretable rare-feature
definition, first using linear models. Report aggregate and subgroup prediction
alongside the feature-level mechanism. Add a small neural model or adaptive
optimizers only with an explicit hypothesis connecting them to the controlled
study. Record momentum, clipping, schedules, stabilizing constants, and weight
decay when applicable; fixed diagonal preconditioning does not describe their
complete dynamics.

**Completion criterion:** determine whether the controlled mechanism remains
observable with practical preprocessing and training choices, and delimit any
recommendation by the task, objective, data, and budget.

## Validation, boundaries, and literature review

Follow [AGENTS.md](../AGENTS.md). Mathematical claims require explicit
assumptions, full proofs, independent proof review, and numerical checks where
applicable. Numerical agreement validates calculations under the tested
conditions. Keep proved statements, empirical evidence, conjectures, and novelty
assessments distinct.

Inside `devenv shell`, use `make check-optimization` for the existing flow,
moment, stability, sampling, joint-budget, and pilot checks. Use
`make check-python` for experiment formatting and lint, and `make check` for
integrated validation. Ordinary Python assertions must remain enabled. Keep the
explicit penalty convention $t = \lambda_1/n$, $r = \lambda_2/n$ separate from
training time. Regenerate numerical artifacts with their scripts and record
provenance.

The initial scope is fixed-feature learning. Multiple rare features, growing
common dimension, prevalence shift, interpolation, and neural feature learning
are later extensions. The separate boundary correction in the original `normreg`
project remains separate work.

Johan will conduct the literature review separately. The existing
[audit](novelty-audit.md) remains a record of the earlier comparison of selected
mathematical tools. This plan specifies the scientific program without deciding
novelty or publication format. Incorporate the separate review before finalizing
contribution claims and manuscript positioning.
