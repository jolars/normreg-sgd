# Contribution decision: normalization after oracle tuning

September 20, 2026. The predictive comparison will be a main theoretical
contribution of the AISTATS draft. This records a manuscript decision, separate
from mathematical review, a priority claim, or an assessment that the paper is
ready for submission. The earlier proof and review notes remain unchanged so
their recorded hashes continue to identify the reviewed statements.

## The claim to lead with

**Under a common observation budget, standard-deviation scaling can improve or
worsen the best attainable rare-subgroup prediction risk, even after each method
chooses any nonnegative constant learning rate and any deterministic stop within
the budget.**

The [direct theorem](predictive-theorem.md) proves the two orderings on its
bounded rate interval. The [review
addendum](predictive-proof-review.md#addendum-the-predictive-rate-cap-can-be-removed)
extends them to every nonnegative constant rate. In the stated independent
binary model, with known preprocessing, a fixed zero intercept, zero
initialization, and one fresh observation per update, let $b=q(1-q)$,
$0<q\leq10^{-4}$, and $1\leq Mb\leq4$. Then:

- If $(\beta_R^*)^2=\sigma^2$ and $(\beta_C^*)^2\leq\sigma^2/100$, the optimal U
  rare risk exceeds the optimal S rare risk by at least $0.007\sigma^2$.
- If $(\beta_C^*)^2=\sigma^2$ and $(\beta_R^*)^2\leq\sigma^2/100$, the reverse
  gap is at least $0.005\sigma^2$.

The bounds hold when either coefficient changes sign. Both methods have the same
observation cap and select their own rate and stop. The winning candidates are
stable, and the losing-method bounds cover unstable rates at finite stops too.
The result therefore also holds when each rule searches only stable constant
rates, together with initialization.

The useful addition is the comparison of complete tuning families. Scalar
retuning removes the earlier C1/C2 anchor comparisons, but it cannot always
remove the prediction effect of relative scaling. The positive gaps are uniform
as prevalence decreases while the expected rare training count remains roughly
one to four. This is a statement about persistent scarcity of rare observations,
not an asymptotic regime with increasingly many rare observations.

## Comparison with the closest statements

The [five-source
comparison](predictive-theorem.md#what-the-result-adds-and-what-remains-a-judgment)
remains the record for the bounded theorem. The following addition addresses the
closest signal-alignment and early-stopping antecedent. Its primary statement
was inspected on September 20, 2026.

[Amari et al., Section 4.2, Proposition
7](https://arxiv.org/html/2006.10732v4#S4.SS2) compare optimally stopped bias
for particular signal covariance models in an overparameterized fixed-data
setting. The preferred preconditioner depends on signal alignment; optimizing
the stopping time need not erase that dependence. Their Section 4.2 also
discusses how early stopping changes risk comparisons. Thus signal-dependent
preference after stopping optimization is an established conclusion. The broader
[novelty
audit](novelty-audit.md#s5-amari-et-al-preconditioning-and-generalization)
already records this source; it should also appear next to the main theorem.

Our theorem compares total conditional prediction risk, including both forms of
stochastic training variance, in a fixed-dimensional fresh-sample binary model.
It gives explicit positive gaps after optimizing every nonnegative constant rate
and every deterministic stop under an equal observation cap. Amari et al.'s
displayed bias inequalities do not directly give these particular total risk
separations. This is our interpretation of the statements, not an exhaustive
priority assessment or a new review of their proofs.

The other comparisons retain their existing limits:

- [Su, Zou, and Wu](https://arxiv.org/html/2403.08585v3) supply preconditioned
  SGD moment analysis and aggregate-risk bounds for tail-averaged iterates.
- [AdaBatch](https://arxiv.org/html/1711.01761v1) already connects
  frequency-dependent learning, noise, and batching.
- [Liu et al.](https://arxiv.org/html/2502.09047v1) analyze target-aware minimax
  preconditioning and scheduled SGD.
- [Lei, Hu, and Lee](https://proceedings.mlr.press/v139/lei21a.html) already
  establish target-aware separations from optimally tuned ridge.
- [Wu et
  al.](https://papers.nips.cc/paper_files/paper/2022/file/d5c04aa72b92c53bda5b525b60958295-Paper-Conference.pdf)
  analyze last-iterate target risk under a decreasing-step schedule.

Neither conventional normalization terminology, subgroup conditioning, familiar
moment tools, nor a different output iterate establishes novelty by itself. The
contribution claim is the specific quantitative comparison and its statistical
interpretation.

## Manuscript role and remaining work

The [main theorem](../paper/sections/conference-predictive.tex) now precedes C1
and C2, with a [proof appendix](../paper/sections/predictive-proofs.tex) that
includes the unrestricted-rate argument. The abstract, introduction, and
discussion distinguish that oracle result from the earlier calibrated
comparisons and finite-grid empirical studies. The former recommendation to
retain the result only as supporting theory is superseded by this decision.

The following limits remain material:

1. The theorem treats two independent features, a narrow prevalence range,
   specific signal-to-noise families, known preprocessing, and $B=1$.
2. The two families give sufficient conditions without identifying the
   transition at intermediate signal allocations.
3. Constant-rate oracle tuning gives no guarantee for schedules, estimated
   preprocessing, or validation-selected procedures.
4. Existing experiments informed claim development. They are not prospective
   confirmation of the prediction.

The next scientific milestone is the [held-out
evaluation](predictive-holdout.md): declare the prediction and protocol, freeze
their implementation before evaluation, then test new synthetic configurations
and an additional sparse categorical task. Preserve the missing-group failures
and all earlier studies. If further theory is needed, prioritize an
interpretable sufficient condition separating the two orderings over sharper
constants.

The bounded-rate proof has a separate Codex review. Independent review of the
unrestricted-rate addendum, human mathematical review, and review of the source
comparison remain open. Choosing this as a main contribution completes none of
those reviews or the held-out evaluation.
