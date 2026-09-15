# Focused overlap audit for the normalization-risk comparisons

September 15, 2026. This addendum initially compared [Conjecture
C1](normalization-risk-comparison.md) with three primary sources. It now covers
the [C1 and C2 proofs](normalization-risk-theorem.md) and five further sources.
It supplements the historical [eight-source audit](novelty-audit.md), whose
inspected revision and conclusions remain intact. Primary HTML statements or the
specified PDF passages were inspected. This is not a review of those papers'
proofs or an exhaustive priority search.

## Assessment

**The general mechanism has close prior art; C2 is the stronger concrete
contribution candidate.** C1 now has a scalar approximation with a controlled
remainder and a continuous-box certificate. C2 shows an objective disagreement
over a feasible dependence-and-noise rectangle, including larger MSE for each
coefficient under the configuration with smaller rare-presence prediction risk.
Independent mathematical review is separate from this novelty assessment.

None of the inspected statements directly gives the stated C1 or C2
inequalities. Their moment framework is established, and target-risk geometry
also has explicit antecedents in covariate-shift analysis. A specific example
absent from the inspected statements is not automatically a substantive new
theorem. My assessment is that C1 alone is an incremental worked comparison; C2
provides a more informative mechanism to test for robustness. Publication-level
novelty and priority remain unresolved.

## S9. Su, Zou, and Wu: preconditioned least-squares SGD

Version: [arXiv:2403.08585v3](https://arxiv.org/html/2403.08585v3), May 26, 2024.
Inspected Assumptions 3.1–3.3, equations (3.1)–(3.2), Theorem 4.2, and Appendix
A.1.

Their algorithm uses fresh single observations, constant steps, and tail
averaging. The theorem bounds aggregate excess risk using the transformed
covariance and signal, under positive covariance, fourth-moment, and noise
assumptions. Map their preconditioner $G$ to our $P$, covariance $H$ to our $C$,
and transformed signal to $S\beta^*$. The update and operator framework overlap
directly; the output averaging and risk weight differ.

For our Bernoulli model with $b=q(1-q)$, testing their fourth-moment assumption
on the rare coordinate gives the necessary bound

$$
  \alpha\geq\frac{E x_R^4-b^2}{b^2}=\frac1b-4.
$$

Thus its constant grows as $q^{-1}$. Their displayed curvature-only step
restriction must not be imported as a uniform rare-limit stability guarantee
without resolving this dependence.

**Classification:** established framework; additional comparison needed. A
one-sided aggregate bound for averaged iterates does not order our two
final-iterate subgroup risks. Appendix A.1 nevertheless supplies relevant moment
machinery, so changing the output criterion alone proves no novelty.

## S10. Meterez et al.: Seesaw

Version: [arXiv:2510.14717v2](https://arxiv.org/html/2510.14717v2), July 27, 2026.
Inspected Section 5, Theorem 1, and Appendix A.1. This updates the v1 used in
the initial planning check.

The setup has Gaussian features, Gaussian response noise, and a common
covariance. Theorem 1 compares geometric step-decay/batch-ramp schedules with
matched decay/ramp products and equal observations per phase. It assumes
$\eta\leq0.01/\operatorname{tr}(H)$ and bounded risk after scheduling begins.
Its conclusion compares phase-end population risks up to constants depending on
that bound, allowing a 1.01 multiplier on one entire step schedule. The
displayed risk includes irreducible noise. It is not exact equality of paths,
means, or excess risks.

**Classification:** relevant resource and schedule baseline; C1 is neither a
direct consequence nor a counterexample. C1 uses binary features, different
relative preconditioners, constant steps, and a conditional excess-risk
criterion. Agreement up to constants would also permit strict ranking reversals.
Appendix A.1 includes multiplicative SGD fluctuations; it must not be described
as a purely additive-noise approximation. The normalized-SGD corollary concerns
gradient normalization, not input-feature scaling.

## S11. Défossez and Bach: AdaBatch

Version: [arXiv:1711.01761v1](https://arxiv.org/html/1711.01761v1), November 6, 2017.
Inspected equations (2.3)–(2.4), Assumption 1, Table 1, and Appendix C.2,
equations (7.21)–(7.23).

AdaBatch averages each coordinate over its active observations. Its expected
rescaling has entries $[1-(1-p_j)^B]/p_j$, where $p_j$ is support probability.
The paper also analyzes deterministic preconditioning, including inverse
frequency. Table 1 explicitly connects faster learning, increased noise, and a
batch-dependent step restriction. Its noise parameter is gradient variance at
the optimum, not our response variance.

The bounds use Hessian comparisons, bounded individual curvature, and a compact
domain/projection argument. Appendix C.2 gives an iterate-distance bound and an
aggregate-risk bound for geometrically weighted averages.

**Classification:** substantial conceptual and analytical overlap. In our
centered model both coordinates have support probability one, so literal
AdaBatch aggregation becomes ordinary batching. Its general deterministic
preconditioning analysis still applies as a comparison framework. Its upper
bounds do not establish C1's strict ordering of exact final-iterate risks.
Centering distinguishes the sampling mechanism; it does not remove this prior
art.

## S12. Ali, Dobriban, and Tibshirani: stochastic gradient flow

Version: [arXiv:2003.07802v2](https://arxiv.org/html/2003.07802v2), June 19,
2020; published at [ICML 2020](https://proceedings.mlr.press/v119/ali20a.html).
Inspected Lemma 1, Remark 2, Section 3.1, and Theorem 2, equations (12)–(14).

They fix the training design and noisy response, then study batch sampling
through stochastic gradient flow. Lemma 1 matches discrete SGD's first two
moments to an Euler discretization of that flow. It does not identify discrete
SGD with the continuous process; Remark 2 leaves discretization error open.
Theorem 2 bounds coefficient risk relative to gradient flow and ridge across the
path, with an additional stochastic-variance term. In-sample variants are also
given.

**Classification:** close antecedent for decomposition and risk along the
training path. Applying their setup to a scaled design is immediate, but it
retains fixed-data noise and changes the coefficient norm. Their continuous-flow
upper bound does not give our exact fresh-sample, final-iterate U/S contrasts. A
separate discretization and sampling argument would be needed to derive them
from that bound. Variance caused by stochastic gradients is already part of
their model.

## S13. Zou et al.: SGD versus ridge

Version: [arXiv:2108.04552v2](https://arxiv.org/abs/2108.04552v2), July 11,
2022, NeurIPS 2021 paper, “The Benefits of Implicit Regularization from SGD in
Least Squares Problems.” Inspected Sections 3–5, Assumption 3.1, and Theorems
4.1–4.2 and 5.1–5.3 in the [full
HTML](https://ar5iv.labs.arxiv.org/html/2108.04552).

Their estimator uses a fresh observation per update, zero initialization, a
tunable constant step, and tail averaging. They compare aggregate population
risk with ridge, allowing specified sample inflation. The one-hot model is
uncentered and supported on basis vectors; their second model is Gaussian.
Neither is our centered dependent binary law. Their one-hot analysis already
makes coordinate frequency part of a statistical SGD comparison.

**Classification:** strong baseline for tuned and budget-aware comparisons, not
a direct C1/C2 implication. Their theorems compare different estimators and
allow learning-rate choice; our fixed U/S pair cannot establish superiority
after optimal tuning. Use the existing Jain et al. audit for final-iterate and
mini-batch baselines rather than attributing those results to this paper.

## S14. Bordes et al.: rare-feature scaling predates this project

Version: [JMLR 11(77), 2229–2240,
2010](https://www.jmlr.org/papers/v11/bordes10a.html), “Erratum: SGDQN is Less
Careful than Expected,” by Bordes, Bottou, Gallinari, Chang, and Smith.
Inspected Section 5.4 on printed p.2238 in the [published
PDF](https://jmlr.org/papers/volume11/bordes10a/bordes10a.pdf#page=10),
including a visual check. The author-hosted draft found initially was replaced
by the published version for this comparison.

They discuss the loss of sparsity from centering and warn that normalizing very
rare features can create large feature values and hurt test performance. This is
discussion in an optimizer evaluation, not a quantitative theorem for our
regression model.

**Classification:** explicit conceptual antecedent. A claim that this project
first identifies harmful rare-feature standardization would be untenable. The
passage does not supply a stopping threshold, risk decomposition, or
aggregate/subgroup comparison.

## S15. Liu et al.: preconditioning and covariate-shift risk

Version: [arXiv:2502.09047v1](https://arxiv.org/html/2502.09047v1), February 13,
2025, “Optimal Algorithms in Linear Regression under Covariate Shift: On the
Importance of Precondition,” by Liu, Zhang, Chen, and Fang. Inspected Sections
3.1, 4, 5.1, and 5.3.1, Assumptions 1–4, and Theorems 2–4 and 6.

Their source and target second moments can differ. Theorems 2–3 characterize
minimax linear preconditioning with known moment matrices. Theorem 4 bounds
target error for fresh-sample accelerated SGD with a prescribed decreasing-step
schedule. Theorem 6 explicitly considers rank-one target matrices.

**Mapping and classification:** set their source matrix to $C$ and target matrix
to $C_R$. Conditioning on $J=1$ defines a target law preserving the response
model. Thus subgroup prediction is within the covariate-shift viewpoint,
including the nested rank-one case. General target geometry and off-diagonal
target moments are not new here. Their Assumption 3 requires
$\psi\geq E x_R^4/b^2=1/b-3$ in our model. Their minimax results and
scheduled-optimizer upper bound do not directly order our two fixed
constant-step configurations. A candidate-specific comparison still needs the
exact contrasts; the different target alone establishes no gap in existing
theory.

## S16. Milligan et al.: normalization of binary-frequency features

Version: OPT 2024 workshop, “Normalization Matters for Optimization Performance
on Graph Neural Networks,” by Milligan, Kunstner, Shirzad, Schmidt, and
Sutherland. Inspected Sections 2, 4, and 5 in the [proceedings
PDF](https://opt-ml.org/papers/2024/paper107.pdf), with a visual check of p.5.
OpenReview access failed; the workshop's own copy was accessible.

They compare column standardization with row normalization, tune steps for
training loss, and link binary feature frequencies to poor conditioning. Their
discussion explicitly identifies increased stochastic variance from
standardizing rare features as a concern. The study focuses on deterministic
training dynamics and leaves generalization and stochastic optimization for
future work.

**Classification:** particularly close motivation. C1 quantitatively studies a
concern this paper already states. C2 adds a specific prediction-objective
comparison, beyond their training-loss comparisons. Their empirical GNN
improvements are neither established nor contradicted by our two-feature
fresh-sample calculation.

## Additional deductions and implications for the candidate

For the independent model with $0<q<1/2$, the two test matrices directly imply

$$
  R\leq R_R\leq\frac{1-q}{q}R.
$$

An aggregate-risk bound can therefore yield a subgroup upper bound, with a
prevalence-dependent loss. The issue is its usefulness and whether it separates
two configurations. Comparing two upper bounds does not establish the ordering
of the actual risks.

The [existing audit](novelty-audit.md) already maps the finite-update moments to
Défossez–Bach and Jain et al. C1's two-dimensional reduction and affine noise
threshold are additional calculations within that framework. Their computational
validity is distinct from the value of the proposed comparison.

The new [proof note](normalization-risk-theorem.md) supplies the missing uniform
C1 bounds and the C2 prediction comparison. Its general sufficient condition
controls the error from dropping cross-coordinate update coupling. For C2, the
cross moment of the coefficient errors receives weight $0.01$ in aggregate risk
and $0.49$ in rare risk at the nested endpoint. This explains why an improvement
in subgroup prediction can coexist with deterioration in both individual
coefficient errors. The underlying quadratic-form identity is elementary; the
explicitly realized stable SGD comparison is the additional calculation.

## Defensible working claim and decision

A concrete statement supported by the calculations is:

> For a declared finite observation budget, conventional feature scaling can
> worsen aggregate prediction and both individual coefficient errors while
> improving prediction conditional on a rare feature. Feasible dependence and
> signal signs determine how the coefficient errors combine. Exact fresh-SGD
> moments yield explicit risk gaps and noise-threshold bounds.

This is a claim about particular configurations and parameter ranges. It does
not say that scaling improves optimally tuned procedures, that learning-rate
adjustment cannot remove the reversal, or that the construction is the first of
its kind. I would develop C2 as the main candidate and retain C1 as the
controlled learning-versus-noise explanation. Before treating C2 as the main
paper contribution, determine whether its effect persists over a declared tuning
range and whether the same limitation has already been formalized in target-risk
or subgroup-risk work. A broad novelty claim is not justified yet.

## Remaining literature work

- Trace the closest target-risk antecedents cited by Liu et al., checking for
  existing strict preconditioner comparisons and coefficient-error/subgroup
  disagreements. The earlier Jain et al. comparison remains an input, not a new
  proof review.
- Check whether final-iterate preconditioning results give tighter comparisons
  for this fixed-dimensional binary setting, with explicit dependence on the
  fourth-moment constant.
- Extend the dependence and subgroup-risk comparison around C2. Check whether
  useful uniform prevalence bounds add anything beyond fixed-distribution
  examples; changing risk weights alone does not establish novelty.
- Resolve additional citations from the deep research report only as needed for
  retained claims; this addendum does not verify its entire bibliography.

The eight source comparisons in this addendum are complete at their stated
scope. The broader novelty assessment remains open. Mathematical review is
tracked with the proof note and separately from literature priority.
