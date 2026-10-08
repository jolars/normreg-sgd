# Current paper tasks

The manuscript now pairs the finite-prevalence oracle theorem with the limiting
characterization and a unique signal-allocation crossing. The proof has been
checked and integrated. Tail averaging and the adaptive-selection mechanism
remain the next substantive questions.

## 1. Test robustness to tail averaging

- [ ] Compare final iterates with averages over the latter half of training in
  the theorem's binary model: fresh observations, population preprocessing,
  zero initialization, and a fixed zero intercept.
- [ ] Match observation caps and separately tune rates and deterministic stops
  for each scaling and estimator. Include both representative signal pairs
  and a few intermediate allocations across prevalence and budget settings.
- [ ] Extend exact moments to accumulated iterates where practical, and check
  the implementation independently. Assess search resolution and distinguish
  finite-grid comparisons from unrestricted oracle claims.
- [ ] Measure how averaging changes common-coordinate noise and the two risk
  gaps. Use persistence to support broader relevance, or disappearing gaps
  to explain the scope of the final-iterate result.

## 2. Characterize the limiting oracle risks

- [x] Derive limiting risks for both scalings as $q \to 0$ with
  $Mq(1 - q) \to \tau$, starting from the exact moment recurrence and the
  proposed scalar SD risk equation.

  The [derivation](notes/oracle-limits.md) gives both limiting risks, proves the
  unrestricted oracle limits, and derives a unique signal-allocation crossing at
  positive noise and rare signal. Numerical checks pass with
  `task check:oracle-limits`. The checked oracle-infimum proof and
  signal-allocation consequences are integrated into the manuscript.

- [x] Account for rates and stops that depend on prevalence, including
  initialization, vanishing rates, and large rates. For U, examine
  $q \ll \alpha(q) \ll 1$, which can learn the common signal while leaving
  the rare effect largely unchanged.

  The derivation gives the full U transient through $k_q\alpha_q \to \ell$,
  uniform bounds over allowed stops, and large-rate exclusions for both
  scalings. Checks cover 32 joint rate-and-stop sequences, zero signal and
  noise, and exact geometric lower bounds. The uniform control below completes
  the passage to oracle infima.

- [x] Establish the control needed to pass from fixed-rate limits to limits of
  the oracle infima. Identify any restrictions on signals, noise, and
  budgets.

  The [proof](notes/oracle-limits.md#completing-the-oracle-argument) gives
  uniform lower bounds over all rates and stops and explicit recovery choices,
  with errors $O(b)$ for S and $O(b\log(1/b))$ for U. It permits all fixed
  finite nonnegative signals and noise, including zeros, and requires
  $Mb \to \tau \in (0,\infty)$. A zero-budget counterexample explains that
  restriction. `task check:oracle-limits` also runs the [uniform-control
  diagnostics](checks/oracle_infima.py). The manuscript includes the uniform
  argument and recovery choices in full.

- [x] Obtain a usable variational characterization and explain how signal
  allocation, noise, and budget determine the preferred scaling. Treat a
  complete closed-form transition boundary as optional additional work.

  The [variational comparison](notes/oracle-variational.md) gives unique scalar
  equations for optimal rates, allocation boundaries, and noise and budget
  regimes. A [root solver](experiments/common/limiting_oracle.py) implements the
  characterization. `task check:oracle-variational` checks it independently
  against objective searches and records examples with two noise reversals. The
  large-budget risk ratio tends to $4/5$ for positive rare signal and noise. The
  manuscript includes these consequences and their proofs.

- [x] Check the limiting predictions against finite-prevalence exact risks, and
  retain the existing theorem as the quantitative finite-prevalence
  guarantee.

  The [finite-prevalence comparison](notes/oracle-finite.md) checks 43 settings
  at six prevalences with independent tensor replays and nested rate and stop
  grids. It recovers the limiting signs away from ties at small prevalence and
  records a high-noise disagreement at larger prevalence. Saved risks, rates,
  stops, refinement diagnostics, and a figure are reproducible with
  `task experiment:oracle-finite`, `task check:oracle-finite -- --rerun`, and
  `task figure:oracle-finite`. The finite-prevalence theorem and certificates
  remain unchanged; these numerical searches do not certify continuous optima.

- [x] Integrate the limiting theorem, allocation corollary, variational
  consequences, and finite-prevalence checks into the paper. Redraw the
  introductory crossing at fixed $s/4 + r$ and retain the earlier $s + r$
  map in the supplement.

## 3. Explain the adaptive-selection reversal

The saved study preserves both orderings under exact-risk selection in all 12
fresh, fixed-intercept baseline settings. Adding only a fitted intercept already
produces a reversal. For the rare-dominant signal at $q = .02$ and $M = 204$,
the SD-minus-U gap changes from $-.01915$ to $-.00589$ in the baseline and from
$-.10456$ to $+.01643$ with a fitted intercept.

- [x] Use the fresh, fitted-intercept arm as the primary example and report the
  baseline comparison alongside it.

  The main paper compares both arms under calibration, validation, and
  exact-risk selection, reporting absolute risks, mean gains, and paired gap
  MCSEs. The fitted-intercept arm reverses the ordering, while the baseline
  retains SD's advantage in the rare-dominant example.

- [x] Analyze the distributions of selection gains for the fresh,
  fitted-intercept arm and its baseline. Saved summaries already include
  absolute risks, paired MCSEs, and distribution summaries of risk changes
  relative to calibration; the paper reports mean gains for both arms. Use
  the saved summaries and predictors to explain how gains differ across runs
  and between scalings, retaining the distinction from theoretical
  adaptation gains.

  The appendix reports gain quantiles, paired gain differences, tail shares, and
  validation losses relative to calibration, with a generated table and
  cumulative-distribution figure for the primary example. Saved predictor errors
  explain where the selected rare risks differ. The analysis retains all 96
  setting–selector combinations for the two fresh arms and separates theoretical
  finite-family adaptation gains from calibration suboptimality.
  `task check:selection-gains` verifies the results against rare-cell
  predictions and existing risk-change summaries without retraining.

- [ ] Decompose rare-subgroup error into common-coefficient error, intercept
  error, rare-coefficient error, and the intercept–rare cross term. Test
  whether cancellation explains the reversal; the ordering alone does not
  establish it.

- [x] Keep exact-risk selection distinct from feasible validation selection and
  from the theorem's choices made before training.

  The appendix distinguishes per-run exact-risk selection from minimizing mean
  risk over a fixed finite candidate family and from feasible validation
  selection. It also states that calibration choices are fixed before evaluation
  and that neither finite search is the theorem's unrestricted oracle.

## 4. Focus the manuscript and empirical narrative

- [x] Organize the introduction around total rare-subgroup risk after separate
  rate and stopping optimization under a finite observation cap. State the
  distinction from prior optimal-stopping bias and tail-averaged SGD
  results.
- [x] Promote the controlled-persistence figure into the main paper, and
  emphasize the controlled missing-validation example.
- [x] Move most extreme synthetic-path diagnostics and Mushroom discussion to
  the supplement, preserving reported failures and qualifications.
- [ ] Give adaptive selection a central role if the analysis explains its
  mechanism; otherwise present it as a focused qualification of the oracle
  comparison.
- [ ] Keep Mushroom extensions secondary. If Mushroom remains central, add an
  identifiable representation or suitable converged prediction references,
  and evaluate clipping consistently during validation and testing.
- [ ] Distinguish observation caps in the theorem from update caps with
  additional preprocessing and selection data in the controlled study.

## 5. Complete verification and submission preparation

The current draft already reports absolute selection risks and gains. The README
already documents certificate commands and recorded outputs; build on these
changes when preparing the supplied artifact.

- [ ] Arrange independent verification of the finite-prevalence bounds,
  exponential enclosures, and complete certificate domain coverage.
  Distinguish this work from the existing small-prevalence checks and Lean
  proofs of the large-rate bounds.
- [ ] Verify that the supplied source archive includes the certificate checkers,
  dependencies, minimal commands, and expected outputs. Run the certificate
  commands from an extracted archive without launching experiments.
- [ ] Reconcile verification status across the manuscript and README with the
  checks and mathematical review actually completed.
- [ ] Update the Su et al. citation to acknowledge the 2026 journal version and
  its author list, retaining version-specific references where needed.
- [ ] Check proposition/theorem naming and cross-references after restructuring.
- [ ] Check the main-paper length after revision and flag material beyond the
  first 12 pages, excluding references, that ALT reviewers may not read. ALT
  2027 has no page limit; do not make substantive cuts just to fit this
  threshold.

## 6. Extend Lean verification

The current proofs check the large-rate steps in both oracle arguments and
common-feature dimension monotonicity, conditional on the moment recurrences.
The final two items are larger optional projects.

- [x] Extend the finite-prevalence large-rate bounds to $0 < q \leq 1/16$ and
  expose the manuscript's exact U risk floor. Retain the $49/100$ bound as a
  small-prevalence corollary.

  [LargeRates.lean](lean/NormReg/LargeRates.lean) proves both floors at every
  finite stop, including initialization and unstable rates. The documentation
  and axiom audits cover the extended statements.

- [x] Formalize the limiting proof's general geometric bounds and rate cutoffs
  for arbitrary nonnegative signals and noise variance.

  [OracleLargeRates.lean](lean/NormReg/OracleLargeRates.lean) verifies the
  recurrence and risk rescaling, both geometric bounds, and both risk floors
  above the cutoffs. It includes equality at the cutoffs, initialization, zero
  signal, and zero noise. It also proves $2 \leq c_S(b) \leq c_U(b) < 3$ for
  $q \leq 1/16$. All main statements pass the axiom audit and `task check-lean`.

- [x] Formalize the common-feature dimension proposition: compare the two moment
  recurrences by induction at fixed rate and stop, then prove that taking
  infima over the same controls preserves the comparison. Keep the
  distinction between monotonicity of each method's risk and behavior of
  their risk gap.

  [CommonBlock.lean](lean/NormReg/CommonBlock.lean) proves coordinatewise moment
  comparison, fixed-rate risk comparison for U and S, and oracle comparison over
  all nonnegative rates and stops up to a shared budget. It includes
  initialization, zero signals and noise, and unstable finite rates. The
  dimension-one recurrence matches the existing two-feature formalization. All
  main statements pass the axiom audit and `task check-lean`; neither the proofs
  nor the documentation claim monotonicity of the risk gap.

- [ ] Formalize the remaining analytic finite-prevalence bounds: lower bounds
  for rates in $[0,1]$, the S candidate upper bound, and the U candidate's
  $H_{\max}$ feedback bound. Include positivity of denominators, stability
  of the candidate rates, and rescaling by $\sigma^2$.

- [ ] Prove the rational exponential enclosures used by [the certificate
  checker](checks/predictive_fixed_q.py), including the Taylor remainder
  bound, reciprocal bounds, and range reduction.

- [ ] Have the certificate search emit a subdivision tree, and build a Lean
  checker that verifies each leaf's rational margin and the tree's complete
  domain coverage. Prove that accepted certificates imply the reported
  oracle gap bounds, and include the checker results in the axiom audit.

- [ ] As a larger optional project, derive the moment recurrences and
  rare-subgroup risk formula from the probabilistic SGD model. Start with
  the one-step calculation over the four feature outcomes and conditional
  noise moments, then account for independence from the training history.

- [ ] As a larger optional project, formalize the rest of the limiting-oracle
  theorem: uniform moment approximations, the vanishing-rate U transient,
  trajectory reduction, and the lower bounds and recovery choices needed to
  pass to oracle infima. Cover zero signals and noise, and prove the uniform
  $O(b)$ and $O(b\log(1/b))$ errors on positive compact budget intervals.
