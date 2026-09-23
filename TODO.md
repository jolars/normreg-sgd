# Current paper tasks

Keep the manuscript theory-led. Prioritize the revisions below, informed by the
[mock-review synthesis](reviews/2026-09-23-aistats/synthesis.md), before adding
another empirical study.

- [x] Package certificates and experimental artifacts

- [ ] complete Appendices A/C.

- [ ] Add one controlled experiment changing a single oracle assumption—Section 5.
  Include a converged prediction reference for Mushroom.

- [ ] Extend the oracle comparison to fixed positive $q$, with explicit risk-gap
  bounds depending on $q$ and $M$—Theorem 3.1 and Appendix A. Identify where
  each bound is positive for its signal family, and assess how conservative
  the current cutoff $q \leq 10^{-4}$ and constants are. Retain the
  small-$q$ result as a corollary if the broader proof supports it.
  Exploratory rate-grid searches for the Figure 1 signal vectors at
  $q = 0.02$, $M = 102$, and $\sigma^2 = 1$ give gaps of approximately
  $0.0257$ favoring SD for the rare-signal vector and $0.0747$ favoring no
  scaling for the common-signal vector. These are numerical evidence; the
  extension needs a proof covering all nonnegative constant rates, all
  admissible stops, and the full signal families.

- [ ] Simplify the experimental narrative, preserve unresolved-result
  qualifications, add the suggested Zou comparison, and correct the
  Proposition 4.2 label.
