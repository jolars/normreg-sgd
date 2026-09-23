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
  certificates prove positive gaps for $q\leq0.05$ in the rare-signal family
  and $q\leq0.04$ in the common-signal family, throughout
  $1\leq Mq(1-q)\leq4$. At $q=0.02$ and $M=102$, the certified gaps exceed
  $0.0092472\sigma^2$ and $0.0641380\sigma^2$, respectively. The proof
  covers all nonnegative constant rates, all admissible stops, and both full
  signal families. The small-$q$ corollary improves the former constants to
  $0.011\sigma^2$ and $0.055\sigma^2$. Run `task check:predictive-fixed-q`;
  independent mathematical review remains open.

- [ ] Simplify the experimental narrative, preserve unresolved-result
  qualifications, add the suggested Zou comparison, and correct the
  Proposition 4.2 label.
