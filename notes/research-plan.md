# Research plan

Working direction: **Normalization and Implicit Regularization in Stochastic
Learning**. Revised September 15, 2026. The task checklist is in
[TODO.md](../TODO.md). The immediate focus is **feature scaling, finite-time
SGD, and rare-subgroup prediction**.

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

The comparative milestone asks a narrower question: **Under a declared training
budget, when does relative feature scaling change the ordering of prediction
risks, and how do rarity, stopping, stochastic variance, and dependence explain
that ordering?** The [C1 and C2 proofs](normalization-risk-theorem.md) now
provide two bounded answers. The next milestone tests their robustness to
declared learning-rate and stopping adjustments before expanding the joint
configuration grid. A complete characterization of every training regime remains
a longer-term research objective.

## Implications of the literature report

The [September 15 research report](../deep-research-report.md) supports this
focus. It identifies substantial prior work on the individual mechanisms and a
possible gap in their consequences for common and rare features. Its novelty
ratings are provisional judgments. The exported citation markers do not provide
usable source links, and absence from its search does not establish priority.
Use the report to prioritize theorem-level comparisons alongside the existing
[bounded audit](novelty-audit.md).

The first three source checks sharpened the immediate comparison:

- [Su, Zou, and Wu](https://arxiv.org/html/2403.08585v3) analyze preconditioned
  least-squares SGD and compare its aggregate excess risk with ridge. Their
  equation (3.2) uses tail averaging, and Theorem 4.2 gives a risk bound under
  fourth-moment assumptions. Compare these statements with our final-iterate,
  original-scale, rare-subgroup objective, including how moment constants depend
  on prevalence. A conventional normalization is a special preconditioner;
  different terminology alone creates no research gap.
- [Meterez et al., Seesaw](https://arxiv.org/html/2510.14717v2) study
  learning-rate and batch-size scheduling equivalence. Compare the schedules,
  assumptions, risk criterion, and resource accounting in their Theorem 1 with
  any proposed failure of scalar compensation here.
- [Défossez and Bach, AdaBatch](https://arxiv.org/abs/1711.01761) connect sparse
  mini-batch aggregation to coordinate rescaling. Compare that mechanism with
  fixed prevalence-based preprocessing. Our centered binary coordinates are
  nonzero even when the indicator is absent, so occurrence counts alone do not
  describe which coordinates receive updates.

The [focused audit](normalization-risk-audit.md) now also compares
Ali–Dobriban–Tibshirani, Zou et al., the SGD-QN erratum, covariate-shift
preconditioning, and feature normalization in GNNs. Harmful rare-feature scaling
and target-risk geometry have explicit antecedents. The broader novelty
assessment remains open. The central contribution candidate is a quantitative
risk comparison with a statistical interpretation. Global rescaling,
independent-coordinate flow rates, moment recursions, and generic fourth-moment
dependence remain supporting tools. The existing covariance-matched construction
already illustrates why $Bq$ and covariance do not determine SGD behavior. A
further result in that direction should identify a consequential risk difference
or a useful approximation with explicit limits.

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

The [first comparison specification](joint-interactions.md) and [numerical
results](joint-interactions-results.md) now implement an initial constant-step,
fresh-sample study: 1,056 configurations, retained training paths, risk
decompositions, four figures, and paired simulation checks. Draft analytical
deductions have local proofs and independent computational checks; independent
proof review is pending because Coterie was unavailable. The first specification
and grid are complete. The next steps use their findings to select and establish
one substantive comparison.

[C1](normalization-risk-comparison.md) now has a [proof with controlled
threshold bounds](normalization-risk-theorem.md) throughout its original
parameter box. A second theorem, C2, gives opposite aggregate and rare-presence
orderings for the same configurations at 100 observations, uniformly over
declared dependence and noise intervals. SD scaling worsens both coefficient
MSEs in C2; its smaller cross moment of the coefficient errors explains the
rare-prediction advantage. Independent proof review is tracked with the theorem
note. The associated [expanded audit](normalization-risk-audit.md) finds no
direct statement of these comparisons in its inspected sources, while
identifying substantial overlap in their mechanisms.

The next scientific decision is whether C2's objective disagreement survives a
declared range of learning-rate and stopping adjustments. Retain C1 as the
controlled bias-versus-noise comparison and preserve both fixed configurations
and failures. The steps below retain the milestone criteria that led to these
results; mathematical completion does not settle novelty or empirical value.

### 1. Formulate a candidate result and check its closest prior work

Use the [focused comparison note](normalization-risk-comparison.md), starting
from the observed no-scaling versus standard-deviation-scaling rare-risk
reversal. In the independent model at the stated common-learning calibration,
the ordering changes between 1,000 and 10,000 updates for $B=1$. The $B=10$
endpoints have a different ordering pattern. These observations identify a
candidate mechanism involving bias and observation-noise variance; they do not
establish a threshold or a comparison of tuned procedures.

State the exact risk inequalities to prove, the two normalization rules, rate
calibration, stopping counts, budget, feasible feature law, signal, and noise.
Start with constant-step, fresh-sample SGD under the existing
known-preprocessing assumptions. Compare both methods at the same budget within
each inequality. If batch size changes, report fixed-update and
fixed-observation comparisons separately.

Alongside this formulation, extend the bounded audit with the three closest
sources above and their relevant antecedents. Map each candidate claim to exact
theorems, assumptions, output iterates, risk weights, and prevalence-dependent
constants. Record whether it follows directly, requires a further calculation,
or remains unresolved. Verify the report's additional recent references before
using them to support a claim.

**Completion criterion:** one explicit conjecture and a source-backed account of
what must be established beyond existing results. If a direct specialization
already gives the proposed result, credit it and refine the research target.

### 2. Prove an interpretable normalization-risk comparison

The [comparison proofs](normalization-risk-theorem.md) now implement this step,
with independent review tracked separately. Use the exact finite-update moments
to derive sufficient conditions for the candidate ordering and its reversal.
Separate squared bias, multiplicative update variance, and propagated
observation-noise variance. Give a quantitative parameter range or a threshold
bound with controlled approximation error. An isolated grid crossing, or
continuity around one crossing without useful bounds, does not yet explain when
the mechanism matters.

The stronger comparison, now realized by C2, is disagreement between aggregate
and rare-presence risk for the same two training configurations:

$$
  R^{(a)} < R^{(b)},\qquad R_R^{(a)} > R_R^{(b)}.
$$

Hold the test law and training budget fixed in this comparison. First test
whether the existing paths support it, then determine how feasible dependence
and signal signs change the sufficient conditions. Report a risk gap or its
prevalence order. A comparison of two configurations does not establish
different global optima over all normalization and training choices.

Pursue one principal theorem first. Dependence, the three $Bq$ limits, and a
uniform comparison across normalization exponents are extensions when they
resolve a specific limitation of that theorem. Reuse the existing three-feature
construction for matched-covariance questions: two binary marginals and their
covariance already determine their joint law.

**Completion criterion:** a full proof, independent proof review, and
independent numerical checks of a comparative statistical statement. A checked
equivalence or counterexample that rules out the candidate mechanism is also a
useful outcome. The existing algebraic controls alone do not complete this
milestone.

### 3. Test the comparison's robustness and limits

Declare a focused extension to the retained grid around the proposed result.
Vary prevalence, feasible dependence, signal signs and magnitudes, noise, rate
resolution, and stopping resolution. Include near-zero steps, stable regimes,
theoretical boundaries, and unfavorable or null outcomes. Preserve the frozen
pilot and first fresh-sample study as separate records.

Use global rescaling as a pathwise control and matching common-feature mean
learning as a mechanistic calibration. Then check sensitivity to a declared
range of learning-rate and stopping adjustments at comparable budgets. A fixed
configuration reversal need not survive retuning; determine whether it does and
limit the conclusion accordingly. Tail averaging is a focused comparator if
needed to understand overlap with the preconditioned-SGD literature.

Retain coefficient paths, both risks, and variance decompositions. Use paired
data and noise for direct simulations and report Monte Carlo uncertainty;
deterministic moment values do not have Monte Carlo error. Check small direct
update paths before expanding a calculation, and retain failed runs.

**Completion criterion:** reproducible evidence showing where the proposed
comparison holds, where it fails, and whether budget calibration or retuning
explains its limits. Broader grids should answer these questions.

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

### 5. Decide the manuscript's contribution and scope

Use the theorem-level comparison and robustness results to choose the main
claim. A promising account is how prevalence-based feature scaling allocates
finite-time bias and stochastic variance, with consequences for rare-subgroup
prediction. Use the controls and existing moment machinery to explain that
result. The single-regime $4\sigma^2/(3nq_n)$ limit remains a foundation unless
a new comparison gives it a distinct role.

**Completion criterion:** align the title, abstract, contribution statements,
and literature discussion with the accepted result and its limits. If no
substantive comparison survives the audit and checks, reassess the claim and
publication scope before undertaking a broad empirical expansion.

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

Johan's [research report](../deep-research-report.md) now supplies the broader
literature assessment. The existing [audit](novelty-audit.md) remains a record
of the earlier theorem-level comparison. Complete the focused source checks
above as candidate claims take shape. Mathematical correctness, originality, and
empirical usefulness require separate evidence; the report alone settles none of
them.
