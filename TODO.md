# Current paper tasks

Keep the manuscript theory-led. Prioritize the revisions below, informed by the
[mock-review synthesis](reviews/2026-09-23-aistats/synthesis.md), before adding
another empirical study.

- [x] Package certificates and experimental artifacts

- [ ] complete Appendices A/C.

- [ ] Add one controlled experiment changing a single oracle assumption—Section 5.
  Include a converged prediction reference for Mushroom.

- [x] Extend the oracle comparison to fixed positive $q$, with explicit risk-gap
  bounds depending on $q$ and $M$—Theorem 3.1 and Appendix A. Rational
  certificates prove positive gaps for $q \leq 0.05$ in the rare-signal
  family and $q \leq 0.04$ in the common-signal family, throughout
  $1 \leq Mq(1 - q) \leq 4$. At $q = 0.02$ and $M = 102$, the certified gaps
  exceed $0.0092472\sigma^2$ and $0.0641380\sigma^2$, respectively. The
  proof covers all nonnegative constant rates, all admissible stops, and
  both full signal families. The small-$q$ corollary improves the former
  constants to $0.011\sigma^2$ and $0.055\sigma^2$. Run
  `task check:predictive-fixed-q`; independent mathematical review remains
  open.

- [ ] Simplify the experimental narrative, preserve unresolved-result
  qualifications, add the suggested Zou comparison, and correct the
  Proposition 4.2 label.

- [x] The connection between the theorem and the practical studies needs either
  an experiment or a smaller role in the paper.

  The transition at the start of Section 4 (paper/main.tex:392) naturally raises
  the question: Can a practical learner realize the advantages established
  above? But the experiments simultaneously introduce observation reuse,
  estimated preprocessing, fitted intercepts, batch selection, and
  validation-based selection. They then concentrate on missing validation
  groups, search sensitivity, and clipping.

  These are relevant problems, but the reader never learns which part of the
  theoretical mechanism survives those changes. The draft acknowledges this
  accurately; acknowledgment alone does not supply the missing connection.

  The controlled study proposed in the Discussion (paper/main.tex:580) is
  precisely the experiment I would prioritize. Start with the two theorem signal
  families and introduce the practical changes separately, keeping the remaining
  setup matched. Report the SD-minus-U rare-risk difference across budgets. This
  would show where the ordering persists, weakens, or changes.

  Without that study, I would shorten the practical section and present it
  explicitly as evidence about the difficulty of comparing normalization
  procedures. The central theorem supports its stated claim without a broad
  applied benchmark, but the current amount of empirical material makes the
  reader expect a stronger connection.

- [x] The explanation of the mechanism needs to connect two different
  comparisons.

  In Section 2 (paper/main.tex:262), you match progress on the common
  coefficient and explain faster rare-signal learning versus greater rare-
  coordinate noise. In Section 3 (paper/main.tex:288), the explanation changes:
  learning the important signal incurs noise in the other coefficient.

  Both explanations make sense, but the transition deserves more attention. A
  reader can understand the first and still wonder why tuning cannot remove its
  disadvantage—especially because the fixed-calibration reversal immediately
  disappears after tuning.

  I would make the central constraint explicit: a global learning rate moves
  both coordinate step sizes together, while normalization fixes their ratio.
  Learning the rare signal under U therefore has a common-coordinate cost;
  learning the common signal under SD has a rare-coordinate cost.

  The most valuable additional theoretical figure would show risk components at
  the separately tuned choices. Use the two signal families and a representative
  budget, separating common and rare contributions and distinguishing incomplete
  learning, feature-sampling variation, and observation noise. The current
  figures establish which method wins. This figure would explain why, using the
  same comparison as the theorem.

  The fixed-rate example could then be shorter. Its numerical details and
  additional batch/dependence results already have an appropriate home in the
  appendix.

- [ ] The technical setup introduces more machinery than the main result
  initially needs.

  Across Section 2 (paper/main.tex:188), the reader encounters transformed
  features and parameters, the scaling and preconditioning matrices, mini-
  batches, two risk objectives, conditional second moments, three error
  components, and a calibrated rate parameter. Section 3 then introduces a
  different rate parameterization.

  Each item is reasonable, but their accumulation slows the argument. I would
  consider three changes:
  - Begin with (B=1), which is the setting of the central theorem, and introduce
    the general batch formula when needed.

  - Explain rare risk first as a weighted sum of the two coefficient MSEs— the
    simple expression already given in Appendix A—before introducing the general
    trace formulation.

  - Motivate the oracle parameterization by saying that (\alpha) is the
    rare-coordinate step size. That gives the otherwise surprising
    (\operatorname{diag}(4b\alpha,\alpha)) an immediate purpose.

  The main theorem statement (paper/main.tex:325) could also foreground the
  positive gaps directly. Currently, readers first encounter unnamed functions
  defined much later, a prevalence range where their bounds need not be
  positive, and then two narrower cutoffs. A simpler main-text statement with
  the common range (q\leq 0.04) and explicit positive constants would
  communicate the result faster. The sharper ranges and prevalence-dependent
  bounds could remain in the appendix.

- [ ] The empirical figures should show the comparisons that carry the argument.

  Figure 5 and Table 1 (paper/main.tex:474) largely present the same final
  Mushroom losses. Yet the section’s main conclusions concern changes caused by
  expanding the search and clipping predictions. Those changes are not visible
  in the main empirical figure.

  I would replace one of the duplicated presentations with a compact comparison
  showing the SD-minus-U gap under the original and expanded searches, with
  paired uncertainty. A second panel could show the effect of clipping the
  selected predictors. These would directly support the section’s claims and
  mostly use results already available.

  The theoretical figures have clearer individual roles: Figure 1 explains
  geometry, Figure 2 gives the intuitive crossing, Figure 3 illustrates the
  theorem across budgets, and Figure 4 explores the transition. Still, the full
  heatmap is a lower priority than the mechanism decomposition suggested above.

  Placement also matters. In the compiled draft, Figure 4 appears amid the
  Mushroom discussion, and Figure 5 appears above the Discussion. Keeping each
  closer to its explanatory text would help the running thread.

- [ ] The validation-coverage example needs more context before the enormous
  loss appears.

  The missing-validation-observations subsection (paper/main.tex:426) moves
  quickly from the protocol to a rare loss of approximately (10^{33}), followed
  by high-precision replay and unresolved discrepancies in another search. The
  statistical point risks getting overshadowed by numerical pathology.

  Start with the simple observation \[
  \Pr(N\_{\mathrm{rare,val}}=0)=(1-q)^{n\_{\mathrm{val}}}. \] This makes the
  coverage problem predictable from the sampling design. Then explain what
  validation cannot distinguish when the group is absent, and use the extreme
  predictor as an illustration.

  If this remains a substantial empirical contribution, a distribution of
  selected rare losses stratified by rare-validation count would be more
  informative than the single worst case. A comparison under a restricted,
  stable candidate search would also help distinguish ordinary selection
  difficulty from explosive candidates.

  The draft correctly limits the claims supported by the numerical
  investigations. Keep those qualifications, but let the statistical explanation
  lead the subsection.

- [ ] Damping becomes an empirical protagonist without enough preparation.

  Damping enters in Section 4 (paper/main.tex:409), then delivers some of the
  strongest empirical results. Readers may reasonably finish that section
  thinking that damping is the practical answer—even though the theorem compares
  U and SD and supplies no rule for choosing the offset.

  Its motivation is intuitively compatible with the paper: limit amplification
  while retaining some benefit from scaling. I would connect that motivation
  explicitly to the preceding mechanism.

  If damping is intended as a substantive practical conclusion, a small
  exact-model comparison across damping offsets would help show how it behaves
  in the two signal families. If it is intended only as an additional baseline,
  reduce its prominence accordingly. Variance scaling likewise needs a clear
  role as a stronger-amplification comparison; otherwise it feels like another
  method introduced after the central question has already been answered.

- [ ] Several passages would benefit from conceptual orientation before
  technical distinctions.

  The related-work paragraphs (paper/main.tex:165) ask readers to distinguish
  gradient flow, overparameterization, signal priors, tail averaging, ridge
  comparisons, minimax target risk, and covariate shift before the paper has
  formally introduced its own problem. Organize the opening around the two
  relevant ideas—preconditioning changes statistical behavior, and subgroup risk
  weights errors differently—then explain the precise distinction of your
  theorem. Some of the detailed comparisons could move later.

  Around the signal-allocation discussion (paper/main.tex:367), bring forward
  the appendix’s explanation that the sweep holds squared coefficient magnitude
  fixed, rather than aggregate signal variance. “Signal allocation” can
  otherwise suggest equal predictive contributions, which is especially
  misleading with unequal prevalences.

  All the main oracle illustrations use (q=10^{-4}), although the theorem now
  covers substantially larger prevalences. An additional (q=0.02) illustration
  would make the finite-prevalence result more tangible. This could be a
  supplementary panel rather than another main figure.

- [x] The appendices contain too much development history.

  The proof material has a sensible overall organization. The empirical
  appendices increasingly read as successive stages of the project: original
  search, expanded search, damping sensitivity, variance-scaling follow-up, and
  post-review diagnostics.

  That history sometimes provides evidence—for example, demonstrating
  sensitivity to search range. Elsewhere it requires readers to reconstruct
  which protocol and conclusion are current. The discussion of “former” theorem
  bounds (paper/main.tex:919) has a similar problem: readers encountering this
  manuscript for the first time have little reason to care about an earlier
  unpublished cutoff.

  I would organize the supplement around the final questions and protocols:
  proof and certificates, numerical illustrations, empirical methods, search
  sensitivity, preprocessing and damping sensitivity, and numerical diagnostics.
  Preserve earlier searches where they support an explicit comparison, with the
  protocol table identifying their differences.
