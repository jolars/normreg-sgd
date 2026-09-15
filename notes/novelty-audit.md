# Bounded novelty audit: rare-feature least squares

Date: September 15, 2026. Assignment ct-01M2HVG2T0P9YD8R02VXFMTBZH. Repository
inspected at 224c7cfab2252c74f6bee7f18326102d6a068f5e. Repository files were not
changed.

Lead follow-up, September 15: the [joint-budget theorem](joint-budget-limits.md)
has now passed [independent proof review](joint-budget-review.md), and the
[controlled pilot](rare-subgroup-pilot.md) has been reproduced. The audit below
preserves the comparisons at the inspected revision. Mathematical acceptance and
the pilot's risk reversals do not settle the unresolved priority assessment.

## Assessment

The general gradient-flow solution, fresh-SGD moment operators, fourth-moment
dependence, and stability mechanism have substantial established overlap. The
manuscript's rare-feature limits and feasible covariance-matched construction
are explicit specializations of those tools. This audit does not establish their
originality. Further development is best directed at a uniform
observation-budget result and a consequential, precisely defined rare-subgroup
prediction comparison.

The table distinguishes a direct specialization from an additional calculation
and from a comparison that remains unresolved.

  | Manuscript claim                                               | Classification                                                                                       | Closest inspected evidence                                                                           |
  | -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
  | Fixed scaling, matrix-exponential path, full-rank OLS endpoint | Established background                                                                               | S4 Lemma 1; S5 Appendix D.1; S7 for the distinct interpolation question                              |
  | Finite-update fresh-SGD second moments and noise sum           | Established operator framework; conditional-noise specialization and centered-covariance bookkeeping | S1 §2.1; S2 Appendix A.4                                                                             |
  | Scalar Bernoulli stability and dependence on Bq                | Scalar specialization plus substitution of Bernoulli moments                                         | S1, S2, S3                                                                                           |
  | Exact multivariate critical step                               | Same generalized-eigenvalue criterion, with sampling conventions mapped below                        | S3 Theorems 5 and 14; S1 sufficient criterion; S2 divergence characterization                        |
  | Three batch-rarity threshold limits                            | Additional asymptotic evaluation of the established criterion                                        | Manuscript operator-norm limit; S1–S3 supply the framework                                           |
  | Matched covariance but different SGD behavior                  | Established general mechanism; explicit feasible binary construction and two-update calculation      | S1–S3                                                                                                |
  | Fixed-time common-block rare coefficient                       | Additional singular-limit calculation from the established flow solution                             | S4; no joint stopping-time conclusion                                                                |
  | Replacement and reshuffling identities                         | Supporting conditional moment/product identities                                                     | General affine-update algebra; specialized reshuffling literature remains outside this bounded audit |
  | Proposed decreasing-step joint theorem                         | Close classical framework; exact uniform specialization unresolved until proof review                | S8                                                                                                   |

## Primary-source comparisons

### S1. Défossez and Bach: least-mean-squares operators

Version: AISTATS 2015, PMLR 38, pp.205–213, “Averaged Least-Mean-Squares:
Bias-Variance Trade-offs and Optimal Sampling Distributions.” Inspect §2.1,
equations (2.1)–(2.4), Lemma 1, printed p.207, and the tightness discussion on
p.208. [Published PDF](https://proceedings.mlr.press/v38/defossez15.pdf#page=3).
Also inspected arXiv:1412.0156v1 (November 29, 2014), §2 and §3.1, where
numbering differs. [Full HTML](https://arxiv.org/html/1412.0156).

Assumptions: fixed-distribution iid observations, finite fourth moments,
positive definite H; their main risk results concern averaged constant-step
iterates. The operator is T(U)=HU+UH−γM(U). Set their X=z and γ=η: our
one-observation propagation operator is I−ηT. Their sufficient contractivity
criterion is exactly positivity of our A−ηM; its scalar specialization gives
η<2E\[Z²\]/E\[Z⁴\].

Version caution: the published p.208 explicitly presents tightness as a
conjecture. The earlier arXiv Lemma 1 includes an operator noncontractivity
statement above the threshold. Do not cite the published Lemma 1 as an
already-proved necessary-and-sufficient all-initializations convergence theorem.
The general second/fourth-moment distinction is nevertheless established here.

### S2. Jain, Kakade, Kidambi, Netrapalli, and Sidford: minibatches and risk

Version: JMLR 18(223), 2018, pp.1–42; also inspected the HTML rendering of
arXiv:1610.03774v4 (July 31, 2018). [Published
PDF](https://jmlr.org/papers/volume18/16-595/16-595.pdf), [full
HTML](https://ar5iv.labs.arxiv.org/html/1610.03774).

Assumptions: fresh iid minibatches, H positive definite, finite fourth tensor
and noise covariance; misspecification is allowed. Appendix A.4, equations
(26)–(27), pp.26–27, gives the noise-driven second-moment recurrence and finite
sum. Their I−γT_b equals our T_B after x=z, γ=η, b=B, and their noise covariance
Σ=our Q. Their variance process starts at truth. Our E(ε\|z)=0 additionally
removes bias/noise cross terms for arbitrary initial mean; subtracting mmᵀ gives
our centered covariance.

Appendix A.5.1, p.33, has the corresponding variational divergence threshold.
Lemma 4, equation (8), p.13, bounds final-iterate risk at floor(n/B) updates;
Theorem 1, equation (4), p.10, bounds tail-averaged risk. These are mandatory
budget baselines. Under our bounded standardized block, their R²=Θ(q⁻¹), so
their safe step already has order min{1,Bq}. Neither averaging nor aggregate
risk can silently be replaced by our final-iterate rare-coordinate objective.

### S3. Mulayoff and Michaeli: exact mean-square stability

Version: COLT 2024, PMLR 247, pp.3915–3969; PDF uses internal page labels 1–55.
Theorem 5, equations (12)–(13), internal p.5; Proposition 6, p.6; Theorem 14,
§3.3. [Published
PDF](https://proceedings.mlr.press/v247/mulayoff24a/mulayoff24a.pdf#page=5),
[arXiv:2306.07850v3 full HTML](https://arxiv.org/html/2306.07850v3).

Assumptions: a fixed finite dataset, independent batches across updates,
distinct examples within a batch, PSD per-example Hessians at an interpolating
minimum. Linearization is exact for noiseless least squares with H_i=z_i z_iᵀ.
Their batch correction is p=(n−B)/\[B(n−1)\], while ours is 1/B for independent
draws.

After that sampling substitution, their C corresponds to our A/2 and their D to
our B_B. Their 2/λmax(C†D) therefore equals our critical step. This is the same
algebraic criterion, not a literal fresh-population theorem as written. Theorem
14 supplies the dominant PSD eigenmode underlying our spectral-radius argument.
Their endpoint permits bounded moments; our strict interval concerns decay for
every initialization. General exact stability should be credited; the rare
asymptotic evaluation is the remaining calculation.

### S4. Ali, Kolter, and Tibshirani: early stopping and ridge

Version: AISTATS 2019, PMLR 89, pp.1370–1378; arXiv:1810.10082v4 (February 23,
2019). Lemma 1, equation (6), PDF p.3; Lemmas 5–6, pp.5; Theorems 1–2, p.6.
[Published PDF](https://proceedings.mlr.press/v89/ali19a/ali19a.pdf#page=3),
[full HTML](https://arxiv.org/html/1810.10082).

Lemma 1 fixes arbitrary X,y and zero initialization. Apply it to XS⁻¹, then map
θ back by S⁻¹: the manuscript's fixed-scale flow is a direct coordinate
specialization. The rare block limit requires the additional
triangular-generator limit and continuity calculation.

Theorem 1 assumes E(y)=Xβ\*, Cov(y)=σ²I and gives risk_GF(T)≤1.6862
risk_ridge(1/T), including in-sample prediction. In scaled coordinates its
estimation norm is the θ norm, not automatically original-scale coefficient
error. Theorem 2's out-of-sample bound uses a spherical signal prior. It does
not directly cover fixed-signal rare-subgroup risk; spherical θ means a
different prior on β. Section 3.1, equations (7)–(8), establishes different
spectral filters, not identical paths. The PMLR landing-page abstract reverses
the inequality in prose; use the actual theorem.

### S5. Amari et al.: preconditioning and generalization

Version inspected: arXiv:2006.10732v4, December 8, 2020. Appendix D.1 gives the
preconditioned flow; §4.2 Propositions 6–7 treats early stopping. [Full
HTML](https://arxiv.org/html/2006.10732v4). The work was subsequently presented
at ICLR 2021; its [OpenReview
record](https://openreview.net/forum?id=S724o4_WB3) was behind a browser
challenge in this session.

Assumptions for their main asymptotics: fixed training data during optimization,
proportional overparameterization d/n→γ>1, a random-design model and spectral
regularity, and a fixed positive definite preconditioner. Proposition 6 gives
monotonic prediction variance along flow. Proposition 7 compares optimally
stopped bias under specific signal covariance models.

This establishes that preconditioning/generalization/early-stopping tradeoffs
themselves are prior work. The manuscript has fixed dimension, a fixed signal,
and a vanishing-prevalence distribution instead of that proportional
random-effects regime. Their statements do not directly imply its common-to-rare
coefficient limit or SGD fourth-moment threshold. Conversely, our diagonal
scaling is not the inverse full population Fisher under dependence, and proves
no adaptive-optimizer result.

### S6. Duchi, Hazan, and Singer: rare predictive features and adaptive geometry

Version: JMLR 12(61), 2011, pp.2121–2159. Introduction and §1.3, p.2125;
Corollary 1, p.2125; Theorem 5 and Corollary 6, p.2132. [Published
PDF](https://jmlr.org/papers/volume12/duchi11a/duchi11a.pdf#page=5).

Their online convex setup permits changing losses; the adaptive diagonal
geometry depends on accumulated squared coordinate gradients. Under the stated
bounded distance to a comparator, their regret bound depends on the sum of
coordinate gradient-history norms and competes with an optimally chosen diagonal
geometry. The sparse-input motivation explicitly includes infrequently
encountered predictive features.

Thus “adaptive geometry helps rare features” is not a new motivation. Our fixed
S⁻² contains neither its history-dependent updates nor its online comparator
guarantee. Their theorem does not directly give our original-scale coefficient
MSE, subgroup prediction error, or Bq stability threshold. Converting regret to
statistical risk would require a specified sampling/averaging argument; an
additional curvature-to-coordinate conversion is needed for rare coefficient
error. This source was inspected as primary PDF text; page-image verification
was unavailable.

### S7. Gunasekar et al.: interpolation and geometry

Version: ICML 2018, PMLR 80, pp.1832–1841; also arXiv:1802.08246v3 (June 22,
2020). §2.2, Theorem 1, equation (6), PDF p.3; Remark 1 includes stochastic
gradients. [Published
PDF](https://proceedings.mlr.press/v80/gunasekar18a/gunasekar18a.pdf#page=3),
[full HTML](https://arxiv.org/html/1802.08246).

Assumptions: a realizable finite dataset, a loss with a unique finite root, a
strongly convex mirror potential, and convergence to zero empirical loss. The
limit minimizes Bregman distance to initialization among interpolants. Choosing
ψ(β)=βᵀP⁻¹β/2 gives the fixed-preconditioner minimum-distance interpolant; from
zero this is the minimum P⁻¹ norm interpolant.

This directly covers the corresponding interpolation-bias statement. It neither
proves convergence for arbitrary steps nor treats the manuscript's noisy
full-rank OLS setting or finite-budget rare-subgroup risk. Keep those three
questions separate. The later arXiv version records corrections concerning
matrix factorization; the comparison here uses only the linear mirror-descent
theorem.

### S8. Moulines and Bach: decreasing-step SGD

Version: NIPS 2011 proceedings, Theorem 1 and equation (6), internal p.3;
assumptions H1–H4 on pp.2–3; discussion on p.4. [Published
PDF](https://proceedings.neurips.cc/paper_files/paper/2011/file/40008b9a5380fcacce3976bf7c08af5b-Paper.pdf#page=3).

Assumptions: unbiased adapted gradients, gradient differences Lipschitz in
quadratic mean, strong convexity of the population objective, and bounded
gradient-noise second moment at the optimum. Theorem 1 treats steps Cj⁻α and
supplies explicit mean-square bounds; equation (6) is its deterministic energy
recurrence.

Our standardized bounded binary setting meets these conditions separately at
each q, with a uniformly positive population curvature, L²=O(q⁻¹), and an O(1)
gradient-noise bound. The proposed 2/\[ceil(16/q_n)+j\] schedule is shifted,
while the printed theorem's inverse-time constants can grow exponentially in L².
Consequently the desired uniform q_n=n⁻¹/² conclusion is not a direct
substitution into that theorem. A rarity-aware solution of the energy recurrence
is a specialization requiring proof, not evidence of a new SGD rate. Exact
separate original-scale bias, multiplicative variance, and noise comparisons
remain to be reviewed. Only primary PDF text was accessible here.

## Supported differences and priority recommendations

1. **Credit the framework and narrow the contribution.** Introduce discrete
   moments as a specialization of stochastic least-squares operator analysis.
   Present the scalar stability result as a Bernoulli example. Attribute the
   exact general criterion before analyzing its rare limits. The centered
   covariance formula and random-initialization terms are useful bookkeeping,
   not sufficient grounds for novelty.

2. **Keep the feasible construction as a controlled example.** It fixes all
   marginal laws, means, and covariance while changing a mixed fourth moment.
   The two-update original-scale gap and the finite-q stable/unstable pair are
   explicit consequences. I independently enumerated all eight cells and all
   two-update paths using exact rational arithmetic at q=1/4, a∈{0,1}, B=1,
   η=8/15. The gap is 32768/455625; thresholds are approximately 0.556999532 and
   0.516196731, bracketing η=0.533333333. No numerical files were written.

3. **Do not overstate its rare-limit size.** From the manuscript's own gap
   2η⁴d_a²e₀²/B² and stability bound η=O(min{1,Bq}), with bounded original
   initial error, the two-update gap is O(q⁴) for fixed B and at most O(q²)
   uniformly across B. Both populations share the leading 2Bq threshold when
   Bq→0. A fixed-q instability example alone does not establish a persistent
   rare-limit performance advantage.

4. **Specify the prediction objective.** With population-centered x and
   coefficient-error second moment V, rare-presence excess squared loss is
   tr(E\[xxᵀ\|J=1\]V)/2. Use the conditional second moment, not merely
   conditional covariance: the conditional mean is generally nonzero. An
   isolated rare error r has aggregate weight q(1−q)r²/2 but rare-presence
   weight (1−q)²r²/2. The construction also changes the conditional test-feature
   law. To isolate a training effect, use one stated common test law or account
   for both changing factors in the quadratic risk. A rare-coordinate variance
   gap alone does not order subgroup prediction risk.

5. **Make the budget theorem the next review target.** For the proposed B=1,
   k=n, q_n=n⁻¹/² and shifted inverse-time steps, establish constants uniform in
   n, separated errors, and the original-scale conversion. An O(1/n) bound for
   scaled squared error already implies an O(1/\[nq_n\]) rare-coordinate bound
   by division by q_n(1−q_n). Merely restating that conversion is not a new
   statistical rate. Any additional result should explain dependence, tuning
   costs, lower bounds, or a useful subgroup comparison.

## Unresolved comparisons and access limits

- This was an eight-source audit, not an exhaustive priority search. Whether the
  exact binary family or the exact three-regime asymptotic statement appeared
  previously remains unresolved. No unsuccessful search supports an originality
  claim.
- Dedicated random-reshuffling/finite-sum literature was not audited. The
  conditional affine recurrences, independent-epoch product operator, and
  unconditional first-pass iid identity should stay labeled supporting
  identities. Distinct examples within independently drawn minibatches in S3 is
  not random reshuffling across an epoch.
- The class-imbalance, gradient-starvation, and recent optimizer-tuning TODO
  references were outside this bounded comparison. No conclusion about feature
  learning, language models, Adam, or overall optimizer superiority follows.
- Known preprocessing is material. None of the manuscript's fixed-scale
  identities by itself addresses data-dependent centering, estimated scales,
  fitted initialization, an updated intercept, or a dataset with no rare
  examples.
- Actual full-paper PDF text was inspected for the proceedings sources; full
  HTML was additionally inspected where linked. Web screenshot calls returned
  citation text without image payload through the bridge, so no visual PDF
  equation/page verification is claimed. A normal sandboxed attempt at an
  in-memory PDF download failed DNS resolution; no sandbox or permission change
  was attempted. OpenReview's browser challenge prevented inspecting the
  ICLR-hosted version of S5. These limitations do not affect the availability of
  its specified arXiv version.
- Validation comprised source-statement/assumption mapping, repository formula
  inspection, and the independent rational support calculation. This is not a
  full mathematical referee review or repository test-suite run. Git status was
  clean.

## Suggested bibliography changes for the lead

Add these entries using the linked publisher metadata:

- defossez2015averaged: Alexandre Défossez and Francis Bach. “Averaged
  Least-Mean-Squares: Bias-Variance Trade-offs and Optimal Sampling
  Distributions.” AISTATS, PMLR 38:205–213, 2015.
  [Metadata](https://proceedings.mlr.press/v38/defossez15.html).
- jain2018parallelizing: Prateek Jain, Sham M. Kakade, Rahul Kidambi, Praneeth
  Netrapalli, and Aaron Sidford. “Parallelizing Stochastic Gradient Descent for
  Least Squares Regression: Mini-batching, Averaging, and Model
  Misspecification.” JMLR 18(223):1–42, 2018.
  [Metadata](https://jmlr.org/papers/v18/16-595.html).
- mulayoff2024exact: Rotem Mulayoff and Tomer Michaeli. “Exact Mean Square
  Linear Stability Analysis for SGD.” COLT, PMLR 247:3915–3969, 2024.
  [Metadata](https://proceedings.mlr.press/v247/mulayoff24a.html).
- moulines2011nonasymptotic: Eric Moulines and Francis R. Bach,
  publisher-metadata author order. “Non-Asymptotic Analysis of Stochastic
  Approximation Algorithms for Machine Learning.” Advances in Neural Information
  Processing Systems 24, 2011.
  [Metadata](https://papers.nips.cc/paper/2011/hash/40008b9a5380fcacce3976bf7c08af5b-Abstract.html).
- Upgrade amari2020preconditioning to an ICLR 2021 conference entry if citing
  that publication, retaining arXiv:2006.10732v4 as the version actually checked
  here. The ICLR venue is confirmed on [coauthor Denny Wu's publication
  page](https://dennywu1.github.io/research.html). Do not imply that the
  challenged OpenReview PDF was inspected.

Existing Ali, Duchi, and Gunasekar publisher metadata are substantially correct.
Pin theorem numbering to the stated version. In particular, the Défossez–Bach
preprint and conference sections differ, and the Ali landing-page abstract
should not be copied as theorem evidence.

## Tentative manuscript wording

“We specialize established least-squares flow and stochastic-moment tools to
feasible rare-binary populations with common predictors. The analysis makes
explicit how dependence affects transient original-scale coefficients, how rare
observations constrain stable shared step sizes, and how covariance-matched
populations can have different finite-update errors. These examples motivate a
separate observation-budget analysis and evaluation of rare-subgroup prediction
under known preprocessing.”

This wording describes the present mathematical content without asserting
priority. Add a joint-budget sentence only after independent proof review and
numerical validation; no such theorem was accepted as part of this literature
assignment.

The lead preserves this report as the source audit. Repository validation and
integration are recorded separately; this report does not accept the candidate
joint-budget theorem.
