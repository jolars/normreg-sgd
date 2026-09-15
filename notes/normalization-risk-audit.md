# Focused overlap audit for the normalization-risk candidate

September 15, 2026. This addendum compares [Conjecture
C1](normalization-risk-comparison.md) with three primary sources. It supplements
the historical [eight-source audit](novelty-audit.md), whose inspected revision
and conclusions remain intact. Primary HTML equations and statements were
inspected; this is not an independent review of their proofs.

## Assessment

**The general mechanism has close prior art.** C1 should be developed as an
explicit, quantitatively bounded statistical comparison. Merely showing that
frequency-based scaling trades faster learning for greater stochastic variance
would repeat an existing explanation.

None of the inspected statements directly gives C1's four strict final-iterate
rare-risk inequalities throughout its parameter box. The underlying moment
framework already exists, however. A new application of it must earn its role
through useful thresholds, risk gaps, or a consequential limitation. This audit
does not establish priority or publication-level novelty.

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

The immediate decision is to seek uniform threshold and risk-gap bounds for C1,
then assess whether they add enough statistical understanding. An isolated
certified box would settle an existence question, but the broader contribution
still needs an interpretable parameter dependence or a consequential prediction
comparison. The closely spaced aggregate/subgroup thresholds at the current
independent anchor reinforce this distinction.

## Remaining literature work

- Complete the candidate-specific comparison with Ali–Dobriban–Tibshirani and
  Zou et al., including the antecedents of the risk bounds used here. The
  earlier Jain et al. comparison remains an input, not a new proof review.
- Check whether final-iterate preconditioning results give tighter comparisons
  for this fixed-dimensional binary setting, with explicit dependence on the
  fourth-moment constant.
- Review dependence and subgroup-risk literature if the main target changes from
  C1 to a disagreement between prediction objectives.
- Resolve additional citations from the deep research report only as needed for
  retained claims; this addendum does not verify its entire bibliography.

The first three prioritized source comparisons are complete at the stated scope.
The broader novelty assessment and independent proof review remain open.
