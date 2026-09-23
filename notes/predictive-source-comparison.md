# Closest-source review of the oracle normalization comparison

September 23, 2026. This review addresses the first claims task in
[TODO.md](../TODO.md), against the manuscript at
`522dedf4bd4aa23fd4cde4338ca7abd7c18a85ac`. It assesses Theorem 3.1, including
the unrestricted-rate extension, rather than the earlier calibrated C1/C2
comparisons. The historical [source audit](normalization-risk-audit.md),
[target-risk comparison](target-risk-comparison.md), and reviewed proof records
remain unchanged.

## Assessment

**The inspected statements do not imply Theorem 3.1 by direct specialization.**
They already establish signal-dependent effects of preconditioning after
stopping optimization, tuned comparisons with ridge, target-aware shrinkage, and
target-risk bounds for final SGD iterates. None supplies the two stated positive
gaps between optimally tuned U and S in this binary model. The reasons are
specific differences in assumptions, estimators, risks, and quantifiers, not
merely the absence of a rare-feature example.

Retain the narrow contribution: explicit opposite orderings of total
rare-presence risk after separate constant-rate and deterministic-stop oracle
tuning under a common observation cap. Do not claim priority for harmful
normalization, signal alignment, subgroup evaluation, tuning-resistant effects
of preconditioning in general, or the moment recurrence. This bounded review
supports that distinction; it does not establish exhaustive priority or replace
human mathematical verification.

## Claim being compared

With $b=q(1-q)$, the theorem fixes two independent binary features, population
centering and scales, a zero intercept, zero initialization, and one fresh
observation per update. Its oracle is

$$
  R_A^*(M)=\inf_{\alpha\geq0,\;k\in\{0,\ldots,M\}}
  \frac12\operatorname{tr}(C_RV_k^A(\alpha)),\qquad A\in\{U,S\},
$$

where $D_U(\alpha)=\alpha I_2$,
$D_S(\alpha)=\operatorname{diag}(4b\alpha,\alpha)$, and
$C_R=\operatorname{diag}(1/4,(1-q)^2)$. The infimum is taken separately for each
rule and each signal. It includes stopping at the prescribed initialization and
finite stops at rates that need not be mean-square stable. It does not select a
rate or stop from the realized data stream.

For $0<q\leq10^{-4}$ and $1\leq Mb\leq4$, the family with
$(\beta_R^*)^2=\sigma^2$ and $(\beta_C^*)^2\leq\sigma^2/100$ has
$R_U^*-R_S^*\geq0.007\sigma^2$. The family with $(\beta_C^*)^2=\sigma^2$ and
$(\beta_R^*)^2\leq\sigma^2/100$ has $R_S^*-R_U^*\geq0.005\sigma^2$. Either
coefficient may have either sign, and $\sigma^2>0$. These are pointwise
guarantees throughout the stated signal families, not worst-case risks over a
coefficient ball or averages over a signal prior.

## Versions and inspected passages

The arXiv landing pages were checked on the review date. Their latest listed
versions were Amari v4, Su v3, Liu v1, and Sagawa v2. Page numbers below refer
to the downloaded PDF pages. Searchable text was extracted first; the listed
equation-bearing pages were then inspected visually.

  | Source           | Version used                                                                                                                             | Passages inspected visually                                                           |
  | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
  | Amari et al.     | [arXiv:2006.10732v4](https://arxiv.org/abs/2006.10732v4), December 8, 2020                                                               | pp. 4–6, 8: gradient flow, bias–variance definition, A1, A3, Proposition 7            |
  | Su, Zou, and Wu  | [arXiv:2403.08585v3](https://arxiv.org/abs/2403.08585v3), May 26, 2024                                                                   | pp. 4, 6–7, 13: Assumptions 3.1–3.3, Eqs. (3.1)–(3.2), Theorems 4.2–4.4, Appendix A.1 |
  | Liu et al.       | [arXiv:2502.09047v1](https://arxiv.org/abs/2502.09047v1), February 13, 2025                                                              | pp. 5, 7–9: Assumption 3, Theorems 2–4, Algorithm 1                                   |
  | Lei, Hu, and Lee | [ICML 2021, PMLR 139:6164–6174](https://proceedings.mlr.press/v139/lei21a.html)                                                          | pp. 3–4: Theorems 3.2 and 3.4, Remark 3.1, Proposition 3.5                            |
  | Wu et al.        | [NeurIPS 2022 proceedings](https://papers.nips.cc/paper_files/paper/2022/hash/d5c04aa72b92c53bda5b525b60958295-Abstract-Conference.html) | pp. 4–6: update, Assumptions 1–2′, Theorems 3.1–3.2, Corollary 3.3                    |
  | Hashimoto et al. | [ICML 2018, PMLR 80:1929–1938](https://proceedings.mlr.press/v80/hashimoto18a.html)                                                      | p. 5: Eq. (4), Proposition 2                                                          |
  | Sagawa et al.    | [arXiv:1911.08731v2](https://arxiv.org/abs/1911.08731v2), April 2, 2020, ICLR 2020                                                       | p. 8: Table 3, Proposition 1                                                          |

Amari et al. also appeared at ICLR 2021, as confirmed by the [author's
publication list](https://www.cs.toronto.edu/~rgrosse/publications/). The
OpenReview PDF returned a browser challenge. The precise statement checked here
is the accessible arXiv v4, and the manuscript bibliography now pins that
version rather than silently attributing its numbering to an unread proceedings
copy. Su's [author CV](https://i.cs.hku.hk/~cwu/CV/cv.pdf) lists a 2024 ICLR
workshop presentation; the comparison uses the later May 26 arXiv text. No
priority conclusion depends on the workshop version. Liu's landing page listed
only v1; this review makes no claim about a later venue publication.

## Comparison of objectives and tuning

  | Result                          | Data and signal assumptions                                                                            | Risk and output                                                           | Optimization or tuning domain                                                                                   |
  | ------------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
  | This manuscript, Theorem 3.1    | Fresh binary observations, dimension two, fixed signal families                                        | Total rare-presence excess risk of a final iterate                        | Separate infima over all nonnegative constant rates and all deterministic stops up to $M$                       |
  | Amari, Proposition 7            | Fixed training sample, overparameterized proportional limit, signal priors, A1/A3                      | Aggregate prediction bias along gradient flow                             | Infimum over all continuous times $t\geq0$ for each preconditioner                                              |
  | Su, Theorems 4.2–4.4            | Fresh observations, covariance and moment assumptions                                                  | Aggregate excess risk of a tail average                                   | Restricted constant steps for the bound; rate and preconditioner choice against ridge at a given sample size    |
  | Liu, Theorems 2–4               | Random source samples, known source/target moments for the minimax estimator, ellipsoidal signal class | Worst-case target risk; linear estimator or final accelerated-SGD iterate | Matrix optimization for the minimax estimator; prescribed geometric schedule and hyperparameter choices for SGD |
  | Lei, Theorem 3.2 and Remark 3.1 | Fixed design, Gaussian response noise, coefficient ball                                                | Worst-case target risk of linear estimators                               | Matrix shrinkage versus the best scalar ridge penalty                                                           |
  | Wu, Corollary 3.3               | Fresh source samples, no target training samples, fourth-moment and noise assumptions                  | Target excess risk of the final iterate                                   | Geometric step decay with a restricted initial rate                                                             |

### Amari: optimized bias is a real antecedent

Proposition 7 defines $B^{\mathrm{opt}}=\inf_{t\geq0}B(\theta(t))$. With signal
second moment proportional to $\Sigma_X^{-1}$, inverse-population-Fisher
preconditioning minimizes this bias among the admitted preconditioners. With an
isotropic signal prior, ordinary gradient flow has no larger optimal bias than
the inverse-Fisher flow. A1 imposes $d/n\to\gamma>1$; A3 imposes joint spectral
conditions. These are non-strict comparisons. The paper also studies variance
and total risk elsewhere; describing the whole paper as bias-only would be
incorrect. Its bias–variance split is with respect to label noise (p. 5), while
our decomposition also separates variation from feature sampling. The two bias
terms should not be identified. [Proposition 7, p.
8](https://arxiv.org/pdf/2006.10732v4#page=8).

For our independent model, U and S are exactly the identity and inverse
population covariance preconditioners. That overlap must be acknowledged. But
setting $\Sigma_X=C$ does not turn their fixed-sample gradient flow into fresh
SGD or satisfy the proportional limit with dimension two. Nor does optimizing
one component of risk order the minima of the sums of bias and variance.
Rescaling continuous time absorbs a scalar flow rate; it does not reproduce
SGD's separate dependence on update size and observation count. Proposition 7
therefore does not yield either finite-budget gap.

### Su: the update and moment machinery already overlap

Equation (3.1) is our update with $G=P$ and $H=C$. Equation (3.2) returns
$2N^{-1}\sum_{t=N/2}^{N-1}w_t$. Theorem 4.2 bounds its aggregate risk for
$\eta\leq1/\operatorname{tr}(G^{1/2}HG^{1/2})$. Theorems 4.3–4.4 choose a rate
and preconditioner to match eligible ridge solutions up to constants, for
sufficiently large common sample size. Appendix A.1 already supplies the
preconditioned error-moment recurrence. [Sections 3–4 and Appendix
A.1](https://arxiv.org/html/2403.08585v3).

Their family $G_\tau=(\tau C+I)^{-1}$ includes U at $\tau=0$ and approaches S
after scalar compensation, since $\tau G_\tau\to C^{-1}$. For $\delta>0$,
$G_{1/\delta}=\delta(C+\delta I)^{-1}$ also represents our population damped
rule after a rate adjustment. The family itself is not a distinction.

The required new comparison concerns two final-iterate subgroup-risk infima. An
upper bound for an average cannot serve as a lower bound for every final iterate
of the losing rule. Even minimizing two upper bounds does not rank the actual
minima. The ridge comparator, freely chosen relative preconditioner, unspecified
comparison constants, and restricted rate bound also do not supply the theorem's
U/S gaps. The shared recurrence can be specialized to derive our exact moments,
but certifying the two infima requires an additional argument.

### Target risk: conditioning changes the test law

Let $P$ be the training law and $Q_R=P(\cdot\mid J=1)$. Then

$$
  \frac{dQ_R}{dP}=\frac{\mathbf{1}\{J=1\}}q,\qquad
  Q_R(y\mid x)=P(y\mid x)
$$

on the target support. Source centering remains fixed, so the target matrix is
the second moment $C_R$, not the covariance after target recentering. This is
ordinary well-specified covariate shift. With an invertible scale matrix $S$,
the source and target moments become $S^{-1}CS^{-1}$ and $S^{-1}C_RS^{-1}$. A
coordinate transformation therefore preserves their distinction. Replacing the
training law by $Q_R$ would change the experiment.

Lei et al.'s Remark 3.1 gives an example where minimax linear target risk is an
$O(d^{-1/4})$ fraction of the worst-case risk of optimally tuned ridge.
Proposition 3.5 instead identifies a common Bayes-optimal ridge estimator across
targets under an isotropic Gaussian prior. Thus a strict target-risk separation
after scalar tuning is already established, and a new target need not imply a
new optimum. [Remark 3.1 and Proposition 3.5, PDF p.
4](https://proceedings.mlr.press/v139/lei21a/lei21a.pdf#page=4). Conditional on
a feature stream, our SGD iterates are linear in responses, but a minimax
comparison over a ball does not rank U and S pointwise throughout our two signal
families. Its fixed-design Gram also cannot be replaced by $C$ without
accounting for random-design error.

Liu et al.'s Theorems 2–3 optimize a linear transformation using the source and
target moments and an ellipsoidal coefficient class. Theorem 4 bounds the target
risk of Algorithm 1's final iterate with geometric step decay and acceleration.
The prescribed schedule reduces to geometrically decaying ordinary SGD when its
two step parameters coincide. [Sections 4–5.1, pp.
7–9](https://arxiv.org/pdf/2502.09047v1#page=7). Mapping their source and target
matrices to $C$ and $C_R$ is legitimate. However, neither their minimax
optimization nor their scheduled-iterate upper bound supplies a lower bound for
all constant-rate U or S candidates at each fixed signal. Their use of the word
preconditioning includes a transformation of the estimator, which is not
automatically a fixed preconditioner at every SGD update.

Wu et al.'s Corollary 3.3 explicitly covers source-only online training and
target evaluation of the final iterate. Its upper and lower bounds are for
geometric step decay and use different moment assumptions; the lower bound also
requires independent Gaussian response noise. [Corollary 3.3, p.
6](https://papers.nips.cc/paper_files/paper/2022/file/d5c04aa72b92c53bda5b525b60958295-Paper-Conference.pdf#page=6).
Thus neither fresh sampling nor final-iterate target risk distinguishes our work
on its own. Besides the different schedule and constant-factor bounds, the
lower-bound moment condition fails in our model, as checked below.

Hashimoto et al.'s Proposition 2 bounds group risks by a distributionally robust
objective. Sagawa et al.'s Table 3 compares group objectives after validation
search over regularization and training duration; Proposition 1 relates convex
robust optimization to reweighting. These are antecedents for subgroup
evaluation and regularization, but neither ranks the oracle U/S paths. Our
algorithm minimizes the source loss and evaluates one designated subgroup; it
does not optimize the worst group or a divergence ball. [Hashimoto, PDF p.
5](https://proceedings.mlr.press/v80/hashimoto18a/hashimoto18a.pdf#page=5),
[Sagawa, p. 8](https://arxiv.org/pdf/1911.08731v2#page=8).

## Direct applicability checks

The following are calculations for our model, not additional claims attributed
to the source papers. For $x_R=J-q$ and $b=q(1-q)$,

$$
  E[x_R^4]=q(1-q)^4+(1-q)q^4=b(1-3b).
$$

Substituting $A=e_Re_R^\top$ in Su's Assumption 3.2 forces

$$
  \alpha_{\mathrm{Su}}\geq
  \frac{E[x_R^4]-b^2}{b^2}=\frac1b-4.
$$

Liu's Assumption 3 and Wu's Assumption 1A omit the subtracted covariance
product, forcing their source fourth-moment constants to be at least $1/b-3$.
These necessary bounds survive diagonal rescaling. They do not say that the
upper-moment assumptions fail at a fixed $q>0$. They say that any invocation
uniform in $q$ must track diverging constants; a curvature-only rate expression
must not be treated as a uniform rare-limit guarantee. Liu also discusses a
weaker condition for finite coefficient norm on p. 5, so this calculation is not
a blanket exclusion of that framework.

Wu's lower-moment assumption 1B is different. Test its source inequality with
$A=e_Ce_C^\top$ and take the common-coordinate entry. Since
$x_C=I-1/2\in\{-1/2,1/2\}$,

$$
  E[x_C^4]-(E[x_C^2])^2=\frac1{16}-\frac1{16}=0,
$$

whereas the required lower bound is $\beta/16>0$. No positive $\beta$ works,
before or after diagonal scaling. Choosing Gaussian response noise would not
repair this feature-moment failure.

Finally, independence gives $C\preceq C_R\preceq((1-q)/q)C$, hence

$$
  R_k\leq R_{R,k}\leq\frac{1-q}{q}R_k.
$$

An aggregate upper bound can therefore control subgroup risk, with a factor that
diverges as prevalence vanishes. This conversion alone gives no strict ordering
between the two methods. Similarly, an existential hard signal in a minimax
lower bound is not a lower bound at every signal in either theorem family. These
are the missing logical steps in attempts to obtain the oracle comparison solely
from the inspected results.

## Manuscript action and verification scope

The related-work paragraph now identifies the optimized-bias antecedent, Su's
averaged-SGD/ridge comparison, Lei's optimally tuned target-risk separation, and
Wu's final-iterate target-risk analysis alongside Liu. It states the
quantitative oracle comparison without asserting a first result. The
bibliography adds the verified Lei and Wu proceedings entries and pins the three
inspected preprints. Supporting-method references moved to Appendix C to keep
the main text within eight pages. Other citation-marker work in TODO.md remains
open.

This was a source-statement and applicability review, not a full proof audit of
any cited paper. Searches checked the named papers' versions and publication
records; they were not an exhaustive search of all subsequent literature. The
reviewed mathematical notes, frozen experiments, and numerical artifacts were
not changed.

Validation completed in `devenv shell`: `make paper` produced the 23-page PDF
with eight main-text pages and no unresolved citations or references. The
revised related work, bibliography, and Appendix C introduction were visually
checked on PDF pp. 2, 9, and 14. The existing title-box overflow warning
remains; the new bibliography entries produce no overflow. Markdown formatting
and lint pass for TODO.md and this note, and `git diff --check` passes.

As an arithmetic check separate from the algebraic arguments, exact rational
enumeration of the four binary cells verified the fourth moments, the two
necessary upper-moment constants, the failed lower-moment condition, the
conditional target matrix, and the aggregate-to-subgroup risk weights at
$q=10^{-1},\ldots,10^{-6}$. These finite checks neither prove the oracle theorem
nor extend the literature search.
