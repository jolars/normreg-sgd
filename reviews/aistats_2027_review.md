# Review: *Feature Normalization under Finite Training Budgets*

**Recommendation: Borderline, leaning weak reject.**\
**Confidence: Moderate.**

The paper has a credible theoretical core: its oracle comparison is more
substantive than demonstrating that two normalization rules behave differently
at arbitrarily chosen learning rates. I did not find a fatal error in the
central moment recurrence or the analytic bounding argument. My main
reservations concern the significance of the advance over existing
preconditioning results, the dependence on a narrowly specified training
procedure, and an empirical narrative that mixes several distinct statistical
questions.

I reviewed the main paper and appendices. The executable source supplement
described in Appendix H was not among the supplied materials, so I could
independently check formulas and numerical examples, but not reproduce the
reported rational-arithmetic certificates or archived experiments.

## Summary of the contribution

The paper studies squared-loss SGD with two independent binary features, one
common and one rare. Its principal comparison is between unscaled training and
population standard-deviation scaling, with each method independently optimizing
its nonnegative constant learning rate and deterministic stopping time under a
shared observation cap. Theorem 3.1 establishes opposite rare-subgroup
excess-risk orderings on two signal families: standardization wins when the rare
signal dominates, while unscaled training wins when the common signal dominates.
The guaranteed gaps are at least $\sigma^2/1000$ and $\sigma^2/50$,
respectively, for $q \leq 0.04$ and $1 \leq Mq(1 - q) \leq 4$. Importantly, the
comparisons include initialization and finite stops at rates that need not be
mean-square stable. ([Manuscript, §3 and Theorem 3.1, p. 4](main.pdf#page=4))

The main conceptual point is that a scalar learning rate and stopping time
cannot generally compensate for a change in relative coordinate scaling.
Learning the relevant signal can require accepting noise in another coordinate,
and a finite observation budget limits the possibility of trading a smaller rate
for a longer run. The nonvanishing gaps concern a regime in which the total
budget grows but the expected number of rare observations remains bounded.
([Manuscript, §3, p. 4](main.pdf#page=4))

The empirical component then distinguishes choosing tuning parameters to perform
well **on average before training** from choosing among **realized fitted
predictors after training**. Both calibrated orderings persist in the controlled
experiments, but adaptive selection can reverse an ordering, including when
selection uses exact population risk. This is a different statistical objective,
not a contradiction of the theorem. ([Manuscript, §4.1 and Table 1, p.
5](main.pdf#page=5))

## Strengths

**The theorem addresses the obvious tuning objection.**\
The strongest feature is the comparison over all nonnegative constant rates and
all eligible deterministic stops. A fixed-rate demonstration would be
substantially less interesting, and the paper explicitly shows that some of its
motivating fixed-calibration reversals disappear after tuning. The main theorem
therefore answers a stronger question than its preliminary examples. Its
conclusion also survives restricting both searches to stable rates, so the
theoretical separation is not an artifact of admitting explosive updates.
([Manuscript, Theorem 3.1, p. 4](main.pdf#page=4); [Table 3 and §C.4, p.
21](main.pdf#page=21))

**The risk decomposition gives a useful explanation.**\
Separating squared mean error, feature-sampling variation, and observation-noise
variation makes the result more informative than an optimization-path picture
alone. Figure 4, on page 6, is particularly effective: it shows that the
disadvantaged method can optimally retain substantial bias to avoid the noise
cost of further learning. The paper correctly avoids the simplistic claim that
whichever method loses must have variance as its largest risk component.
([Manuscript, §3, p. 5](main.pdf#page=5); [Figure 4, p. 6](main.pdf#page=6))

**The controlled extension is thoughtfully designed.**\
Separating calibration from evaluation, pairing the methods, and changing
observation reuse, preprocessing, and intercept treatment in matched arms are
meaningful strengths. The reported persistence of all 96 calibrated orderings is
considerably more relevant to the theorem than an uncontrolled comparison on a
larger benchmark. Figure 7, currently on page 23, deserves greater prominence.
The reported gaps exceed nine paired Monte Carlo standard errors, conditional on
the calibration choices, and retain their signs on the coarser search.
([Manuscript, §§D.1.2–D.1.3, p. 22](main.pdf#page=22); [Figure 7, p.
23](main.pdf#page=23))

**The manuscript is unusually explicit about limitations.**\
It distinguishes finite-grid searches from continuous optimization, update
budgets from tuning work, verified numerical behavior from unresolved
discrepancies, and post hoc clipping from clipping-aware selection. In
particular, it does not use the problematic 25-rate synthetic means to establish
a normalization ranking. Those qualifications are scientifically appropriate.
([Manuscript, §4.2, p. 6](main.pdf#page=6); [§G.4.1, p. 34](main.pdf#page=34))

## Technical correctness and verification

### The central recurrence checks out

I independently reconstructed the second-moment update by enumerating the four
binary feature outcomes. This agrees with Equation (8), including the terms
coupling the two coefficient errors. In spot checks over 672 configurations,
including mixed coefficient signs and rates above the stability range, the
relative numerical discrepancy was approximately $2 \times 10^{-15}$. This is a
check of the recurrence implementation, not a proof of the uniform theorem.

The coupling matters: independence of the features does **not** imply
independence of the fitted coefficient errors. The paper handles this correctly
by retaining the cross-coordinate contributions while exploiting closure of the
two diagonal second moments. Its argument that coefficient signs do not affect
the independent-model risk is also consistent with the vanishing odd
common-feature moments. ([Manuscript, §A.1 and Equation (8), p.
11](main.pdf#page=11))

The proof’s main structure is sound: lower-bound the losing method uniformly in
rate and stop, then upper-bound the other method using an explicit stable
candidate. The large-rate arguments are important and appear valid; they close
off the possibility that an unusual unstable rate with a short finite stop
defeats the comparison. ([Manuscript, §§A.3–A.4, pp. 13–14](main.pdf#page=13))

I also evaluated the explicit bounds independently at $q = 0.02$, $M = 102$,
obtaining

$$
  \Delta_R \approx 0.0092472916, \qquad \Delta_C \approx 0.0641380467,
$$

in agreement with the reported values. These are conservative family-level gap
bounds, not estimates of the actual oracle minima. ([Manuscript, §A.5, p.
14](main.pdf#page=14))

### The computational certification remains an important verification dependency

The final step establishing the uniform constants relies on rational-arithmetic
certificates over continuous parameter regions. Appendix A.5 explains the
enclosure and subdivision rules reasonably clearly. Nevertheless, reproducing a
few floating-point evaluations does not verify coverage of all boxes, the exact
exponential enclosures, or the reported acceptance margins. ([Manuscript, §A.5, p.
14](main.pdf#page=14))

Two aspects of the supplied PDF need attention. The checklist still contains a
`<tobeadded>` repository placeholder, and Appendix A states that independent
review and human verification of the complete theorem remain open in the working
draft; it also explains that the Lean pilot does not formalize the
finite-prevalence theorem. These are not evidence that the theorem is false, but
they make the status of its verification insufficiently settled for a
submission-ready presentation. ([Manuscript, checklist, p.
10](main.pdf#page=10); [Appendix A, p. 11](main.pdf#page=11))

For this paper, the certificate verifier is part of the mathematical evidence,
not merely optional experimental code. I would expect an accessible, versioned
artifact with a minimal verification command, expected outputs, and enough
information to reproduce the domain-coverage checks independently of the large
experimental pipeline. Removing the working-draft wording without completing the
corresponding verification would not address the issue.

## Major concerns

### 1. The exact novelty is real but narrower than the broad motivation

The general idea that preconditioning changes statistical behavior, and that the
preferred preconditioner depends on signal alignment even after early stopping,
is already established. In particular, Amari et al.’s Proposition 7 gives
opposite optimal-stopping **bias** comparisons under different signal priors. Su
et al. analyze excess risk for preconditioned fresh-sample SGD with tail
averaging and compare appropriately chosen preconditioners with ridge
regression. ([arxiv.org](https://arxiv.org/html/2006.10732v4))

The manuscript’s distinctions from those results are legitimate: it studies
total rare-subgroup risk, final iterates, fixed signal families, finite
observation caps, and explicit positive gaps after optimizing both rate and
stopping time. I did not find an exact duplicate of this result in the closest
papers checked. The detailed discussion in Appendix B.3 is substantially more
precise than the broad introductory message. ([Manuscript, §B.3, pp.
16–17](main.pdf#page=16))

My concern is therefore **significance rather than an unsupported allegation of
missing priority**. The main theorem currently establishes two sufficient signal
regimes in a highly tractable model, while the intermediate behavior is explored
numerically rather than characterized analytically. The paper itself correctly
notes that neither the signal conditions nor the budget interval identify
general transition boundaries. ([Manuscript, §3, pp. 4–5](main.pdf#page=4))

A two-feature model is not inherently a weakness: a minimal counterexample can
be the right contribution. But the paper would be substantially stronger with an
interpretable characterization that goes beyond “either ordering is possible.”
The most natural direction is the small-prevalence regime already central to the
paper: characterize limiting risks as $q \to 0$ with $Mq(1 - q) \to \tau$, and
explain how the preferred scaling depends jointly on signal allocation, noise,
and budget. That would make the contribution less dependent on particular
sufficient constants and numerical contours.

### 2. The main mechanism needs one targeted robustness test within the theoretical model

The theorem concerns constant-rate, single-observation, unaveraged SGD with
deterministic stopping and known population preprocessing. These restrictions
are stated clearly. The difficulty is that the noise cost of the final iterate
is central to the separation, while procedures that directly alter that noise
cost remain outside the comparison. ([Manuscript, §2, p. 3](main.pdf#page=3);
[§5, p. 8](main.pdf#page=8))

The most informative additional experiment would not be a broad optimizer
benchmark. It would be a controlled comparison of final-iterate and
tail-averaged SGD, or a simple deterministic decay schedule, **in exactly the
theorem’s binary model**, with matched observation caps and separate tuning for
each normalization rule. Tail averaging is especially relevant because it is
also the procedure analyzed in the closest fresh-sample preconditioning work.
([arxiv.org](https://arxiv.org/html/2403.08585v3))

The question is specific: does unscaled training’s common-coordinate noise
penalty remain substantial under averaging, and do both oracle orderings
persist? I am not asserting that averaging removes the separation. Rather, the
current paper does not establish which parts of the phenomenon are robust and
which depend on the last-iterate restriction.

There is also an important distinction between the theorem’s observation cap and
the empirical studies’ total information budget. In the controlled
estimated-preprocessing arms, all 256 pool rows are used even when the update
cap is smaller; some arms additionally initialize the intercept from the
response mean. This is disclosed, but it means those experiments cannot
establish persistence under the same **total data budget** as the theorem. Their
interpretation should remain persistence under a matched **update cap**, with
additional preprocessing and selection resources. ([Manuscript, §D.1.1 and Table
4, pp. 21–22](main.pdf#page=21))

### 3. The empirical section combines different phenomena without a sufficiently unified conclusion

The stable oracle tradeoff, missing-subgroup validation, numerical instability,
rank-deficient solution selection, and prediction clipping are all relevant
subjects. They are not, however, interchangeable evidence for the same
mechanism.

The extreme five-rate synthetic example illustrates a validation-coverage
failure in an admitted candidate family; the manuscript explicitly says it is
not evidence that the theorem’s stable mechanism causes catastrophic losses. The
25-rate synthetic results introduce a separate numerical-verification issue, and
some affected mean risks are dominated by unresolved selected paths. The careful
qualifications prevent overclaiming, but the amount of space devoted to these
cases still makes the paper’s central empirical message harder to identify.
([Manuscript, §4.2, p. 6](main.pdf#page=6); [§G.4, pp. 33–34](main.pdf#page=33))

The controlled study already contains a cleaner missing-validation example: for
the fresh baseline at $q = .005$, the reported gap changes from $-.0216$ under
calibration to $+1.133$ with 128 validation rows, and the adverse gap is
concentrated in runs without rare validation observations. This happens within
the conservative search, without needing the unresolved extreme-path analysis. I
would emphasize this result and move more of the broader numerical pathology
discussion out of the main narrative. ([Manuscript, §D.1.4, p.
25](main.pdf#page=25))

The Mushroom experiment has a different limitation. Its rank-deficient one-hot
representation means scaling can affect which solution is selected, not only the
speed of approaching a shared solution. The manuscript acknowledges that a
converged prediction reference and identifiable contrasts would be required to
attribute the differences to early stopping. That acknowledgment is correct, but
the missing control still limits the experiment’s evidential connection to the
theorem. ([Manuscript, §4.2, p. 7](main.pdf#page=7))

A useful revision would either introduce an identifiable representation with an
appropriate shared-solution reference, or compare each scaling’s finite-budget
predictions against its own converged prediction reference. The analysis should
focus on predictions rather than interpreting nonidentified coefficient
differences.

Finally, the clipping results materially affect practical interpretation. In
Table 12, under rare validation, SD’s aggregate mean loss changes from
approximately $0.1411$ to $0.00186$, whereas unscaled training changes from
$0.0394$ to $0.03145$, reversing their aggregate ordering. These are descriptive
results for postprocessed selected predictors, not a clipping-aware
training-and-selection procedure. A comparison that uses clipped predictions
consistently for validation and testing would be more relevant to bounded-label
deployment. ([Manuscript, §G.5 and Table 12, p. 35](main.pdf#page=35))

### 4. The adaptive-selection reversal is potentially important but underexplained

The distinction between

$$
  F_A = \min_a \mathbb E_D[r_A(D,a)] \quad\text{and}\quad O_A
      = \mathbb E_D[\min_a r_A(D,a)]
$$

is correctly presented in the supplement. Defining the adaptation gain
$G_A = F_A - O_A \geq 0$ gives

$$
  O_S - O_U = (F_S - F_U) - (G_S - G_U).
$$

Thus, an ordering reverses when one scaling benefits sufficiently more from
choosing among its realized predictors. The manuscript already supplies the
underlying inequality, but the main presentation mostly reports the resulting
sign change. ([Manuscript, §D.1.4, pp. 24–25](main.pdf#page=24))

Table 1 is striking: the SD-minus-U gap moves from $-.0855$ under separate
calibration to $+.0460$ under exact population selection. Relative to the
evaluated calibrated choices, that is a $0.1315$ larger selection benefit for U
than for SD. Because calibration estimates the finite-family optimum, this
should not be presented as an exact estimate of the theoretical $G_U - G_S$, but
it is nevertheless a large effect deserving explanation. ([Manuscript, Table 1
and §4.1, p. 5](main.pdf#page=5))

I would report the absolute risks of both methods under each selection policy,
their respective gains from selection, and the distribution of those gains
across runs. I would also ask whether exact-risk selection reverses an ordering
in the fresh, population-preprocessed, fixed-intercept baseline, rather than
only in the fully modified arm highlighted in Table 1.

Intercept fitting offers a particularly concrete mechanism to investigate. With
a fitted intercept, the rare-subgroup error involves

$$
  a + (1 - q)(b_R - \beta_R^*),
$$

so good rare prediction can result from cancellation between intercept and
rare-coefficient errors. The supplied table does not establish whether such
cancellation drives the selection reversal. Showing the joint error components
would explain more than another ordering plot. ([Manuscript, §D.1.4, p.
25](main.pdf#page=25))

## A concrete theoretical revision worth pursuing

There appears to be a tractable route to improving interpretability without
moving immediately to high dimension.

As a reviewer-derived calculation from Equation (8), let

$$
  s = (\beta_C^*)^2,\qquad r = (\beta_R^*)^2,
$$

fix a standardized rare-coordinate step $0 < \alpha \leq 1$, and take $q \to 0$
with $kq(1 - q) \to t$. The limiting diagonal-moment equations are

$$
  \dot C = -2\alpha C,
  \qquad
  \dot H = -\alpha(2 - \alpha)H + \alpha^2\left( \sigma^2 + \frac C4 \right).
$$

Consequently, $W = C/4 + H$, twice the limiting rare risk, obeys the scalar
equation

$$
  \dot W = -\alpha(2 - \alpha)W + \alpha^2\sigma^2.
$$

This yields the fixed-rate limiting expression

$$
  R_S^{\mathrm{lim}}(t,\alpha)
  = \frac12\left[ \left( r + \frac{s}{4} \right)e^{-\alpha(2-\alpha)t} + \frac{\alpha\sigma^2}{2 - \alpha} \left( 1 - e^{-\alpha(2-\alpha)t} \right) \right].
$$

This calculation follows from the manuscript’s recurrence; it is not a theorem
stated in the submission. ([Manuscript, §A.1 and Equation (8), p.
11](main.pdf#page=11))

An analogous characterization for unscaled training, together with careful
treatment of rates depending on $q$, could make the signal–noise–budget tradeoff
much more transparent. Crucially, a pointwise fixed-rate limit would **not** by
itself justify exchanging the limit with the oracle infimum. Establishing that
additional control would be a meaningful strengthening, rather than merely
another illustration of the existing theorem.

## Presentation and submission readiness

The main paper would benefit from being organized around three results: the
oracle separation, the controlled persistence experiment, and the change induced
by adaptive selection. I would promote Figure 7 into the main paper, potentially
replacing the introductory geometry figure. Figure 1 is clear, but Figure 7
provides more distinctive evidence for this submission.

The appendix also has a small naming inconsistency: B.2 is introduced as a
proposition but later referred to as a theorem, including in its proof heading.
([Manuscript, Proposition B.2, p. 16](main.pdf#page=16); [§B.3.5, p.
19](main.pdf#page=19))

The bibliography should acknowledge that a journal version of Su et al.’s
preconditioning paper appeared in 2026, with an updated author list. Keeping a
version-specific arXiv citation for theorem numbering may be appropriate, but
the relationship to the journal version should be explicit.
([epubs.siam.org](https://epubs.siam.org/doi/10.1137/24M1710425))

## Overall assessment

This is **not** a paper I would reject because a two-feature model is inherently
too simple, because adaptive selection contradicts the theorem, or because
unrelated empirical replay failures invalidate the analytic recurrence. Those
would be unfair criticisms.

My reservation is that the current submission combines a technically credible
but narrowly scoped separation theorem with a broad collection of empirical
qualifications, without yet extracting a sufficiently general or sharply
interpretable conclusion. The precise oracle result is the strongest
contribution; the controlled study is its strongest empirical support; the
adaptive-selection reversal is the most promising additional finding.

A fully reproducible certificate artifact, one deeper characterization or
targeted robustness result, and a more focused empirical narrative would
materially strengthen the case for acceptance.

--------------------------------------------------------------------------------

*Manuscript citations use 1-based PDF page numbers. To use the local manuscript
links, keep this Markdown document in the same folder as the submitted PDF,
named `main.pdf`.*
