# Current research plan

Updated September 23, 2026. The current paper is **Feature Normalization under
Finite Training Budgets**, targeting AISTATS 2027. The [September 20
decision](predictive-contribution.md) makes the comparison after oracle tuning
the main theoretical contribution. The previous broad research program and its
completed and deferred milestones are preserved in the [archive](archive.md).

## Claim and scope

Under a common observation cap, standard-deviation scaling can improve or worsen
the best attainable rare-subgroup prediction risk even after each method chooses
any nonnegative constant learning rate and deterministic stop. The theorem
treats independent common and rare binary features, known population centering
and scales, zero initialization, a fixed zero intercept, and fresh observations
with batch size one. It gives explicit positive gaps on two signal families when
$0<q\leq10^{-4}$ and $1\leq Mq(1-q)\leq4$.

This comparison concerns total rare-presence risk, including stochastic training
variance. It does not cover learning-rate schedules, estimated preprocessing, or
validation-selected procedures. The two sufficient signal families do not
identify a general transition or recommend one normalization rule universally.

The statement and proof are inline in [the manuscript](../paper/main.tex). The
[direct theorem](predictive-theorem.md) proves the bounded-rate comparison, and
the [review addendum](predictive-proof-review.md) removes the rate cap. The
[Lean pilot](../lean/README.md) proves two large-rate bounds conditional on the
recurrence; it does not formalize the full model or theorem.

## Evidence and remaining work

The bounded proof has a separate Codex review and independent numerical
certificates. Independent review of the unrestricted-rate addendum, human
mathematical review remain open. The [bounded source
comparison](predictive-source-comparison.md) distinguishes the theorem from
Amari et al.'s optimally stopped bias result and the inspected preconditioning
and target-risk literature. This comparison does not settle exhaustive priority
or publication significance.

The calibrated C1/C2 results explain specific risk contrasts. The robustness
study shows that retuning removes both original anchors. Practical selection,
expanded categorical rates, damping sensitivity, and the four-rule extension
delimit empirical usefulness. Preserve their failed paths, missing groups,
tuning boundaries, and numerical audit limitations. They informed the theorem
and are not prospective confirmation of its prediction.

The September 23 revision adds a [finite-grid signal-allocation
illustration](signal-allocation.md) under the theorem's model and separate
[review diagnostics](review-diagnostics.md) for the frozen practical studies.
The latter identify claims affected by numerical discrepancies and evaluate
clipping of saved Mushroom selections. Both additions are post hoc. The main
empirical figure now shows the final matched search, with the earlier comparison
preserved in the supplement.

Prioritize author verification and the self-contained anonymous reproduction
package. The [prospective protocol](predictive-holdout.md) remains a deferred
extension if a stronger practical contribution is needed. Before executing it,
audit development overlap, implement and check the evaluation, and freeze the
prediction and implementation. Begin with the theorem's model and change
observation reuse, preprocessing, intercept fitting, and selection separately.
Report unfavorable and unresolved results alongside successes.

The [current task list](../TODO.md) tracks those reviews, evaluation, and
submission preparation. The [conference plan](aistats-2027.md) records the
submission requirements. Align the final claim with the completed evidence;
neither the framing decision nor a successful build establishes readiness.

## Working boundary

The active manuscript is consolidated in `paper/main.tex`, with only the
checklist in a separate section file. Historical manuscripts, unused section
copies, and the former broad backlog live in `../../normreg-multi-archive`.
Consult [the inventory](archive.md) before restoring old directions.

Some older calculations, proof sources, notes, and results remain here because
the current empirical studies import them or verify their frozen hashes. Their
presence does not make every earlier research objective part of this paper.
Preserve those dependencies and use the declared reproduction targets described
in [AGENTS.md](../AGENTS.md).
