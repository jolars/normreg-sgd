# Current paper tasks

Keep the finite-prevalence oracle theorem as the central result. Start with the
averaging comparison to assess the scope of the mechanism, then pursue a
limiting oracle characterization before rewriting the main narrative.

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

  The [working derivation](notes/oracle-limits.md) gives both limiting risks,
  proves the unrestricted oracle limits, and derives a unique signal-allocation
  crossing at positive noise and rare signal. Numerical checks pass with
  `task check:oracle-limits`. The oracle-infimum proof and signal-allocation
  consequences still need independent mathematical review.

- [x] Account for rates and stops that depend on prevalence, including
  initialization, vanishing rates, and large rates. For U, examine
  $q \ll \alpha(q) \ll 1$, which can learn the common signal while leaving
  the rare effect largely unchanged.

  The working derivation now gives the full U transient through
  $k_q\alpha_q\to\ell$, uniform bounds over allowed stops, and large-rate
  exclusions for both scalings. Checks cover 32 joint rate-and-stop sequences,
  zero signal and noise, and exact geometric lower bounds. The uniform control
  below completes the passage to oracle infima.

- [x] Establish the control needed to pass from fixed-rate limits to limits of
  the oracle infima. Identify any restrictions on signals, noise, and
  budgets.

  The [proof](notes/oracle-limits.md#completing-the-oracle-argument) gives
  uniform lower bounds over all rates and stops and explicit recovery choices,
  with errors $O(b)$ for S and $O(b\log(1/b))$ for U. It permits all fixed
  finite nonnegative signals and noise, including zeros, and requires
  $Mb\to\tau\in(0,\infty)$. A zero-budget counterexample explains that
  restriction. `task check:oracle-limits` also runs the [uniform-control
  diagnostics](checks/oracle_infima.py). Independent mathematical review remains
  outstanding.

- [x] Obtain a usable variational characterization and explain how signal
  allocation, noise, and budget determine the preferred scaling. Treat a
  complete closed-form transition boundary as optional additional work.

  The [variational comparison](notes/oracle-variational.md) gives unique scalar
  equations for optimal rates, allocation boundaries, and noise and budget
  regimes. A [root solver](experiments/common/limiting_oracle.py) implements the
  characterization. `task check:oracle-variational` checks it independently
  against objective searches and records examples with two noise reversals. The
  large-budget risk ratio tends to $4/5$ for positive rare signal and noise.
  These limiting claims still await independent mathematical review.

- [ ] Check the limiting predictions against finite-prevalence exact risks, and
  retain the existing theorem as the quantitative finite-prevalence
  guarantee.

## 3. Explain the adaptive-selection reversal

The saved study preserves both orderings under exact-risk selection in all 12
fresh, fixed-intercept baseline settings. Adding only a fitted intercept already
produces a reversal. For the rare-dominant signal at $q = .02$ and $M = 204$,
the SD-minus-U gap changes from $-.01915$ to $-.00589$ in the baseline and from
$-.10456$ to $+.01643$ with a fitted intercept.

- [ ] Use the fresh, fitted-intercept arm as the primary example and report the
  baseline comparison alongside it.
- [ ] Analyze the saved predictors' gains from selection, including their
  distributions across runs. Retain absolute risks and paired uncertainty,
  and distinguish gains relative to calibrated choices from theoretical
  adaptation gains.
- [ ] Decompose rare-subgroup error into common-coefficient error, intercept
  error, rare-coefficient error, and the intercept–rare cross term. Test
  whether cancellation explains the reversal; the ordering alone does not
  establish it.
- [ ] Keep exact-risk selection distinct from feasible validation selection and
  from the theorem's choices made before training.

## 4. Focus the manuscript and empirical narrative

- [ ] Organize the introduction around total rare-subgroup risk after separate
  rate and stopping optimization under a finite observation cap. State the
  distinction from prior optimal-stopping bias and tail-averaged SGD
  results.
- [ ] Promote the controlled-persistence figure into the main paper, and
  emphasize the controlled missing-validation example.
- [ ] Move most extreme synthetic-path diagnostics and Mushroom discussion to
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
  pilot.
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
