# Lean proof pilot

This project formalizes the two large-rate lower bounds in the [predictive proof
review](../notes/predictive-proof-review.md#addendum-the-predictive-rate-cap-can-be-removed).
It treats the exact moment recurrence (T5) as an explicit hypothesis and defines
the risk by (T4) from the [direct theorem](../notes/predictive-theorem.md).
Noise variance is normalized to one.

## Checked statements

The definitions and proofs are in [LargeRates.lean](NormReg/LargeRates.lean),
under the `NormReg` namespace. Write $b=q(1-q)$. Both main theorems assume
$0<q\leq10^{-4}$ and $\theta\geq1$, and hold for every $k\in\mathbb N$:

  | Lean theorem                      | Recurrence and initialization        | Conclusion        |
  | --------------------------------- | ------------------------------------ | ----------------- |
  | `unscaled_large_rate_lower_bound` | U: $u=\theta/4$, $C_0\geq0$, $H_0=1$ | $49/100<R_{R,k}$  |
  | `scaled_large_rate_lower_bound`   | S: $u=b\theta$, $C_0=1$, $H_0\geq0$  | $1/8\leq R_{R,k}$ |

The formal statements use the original coefficient scale and
$R_{R,k}=C_k/8+(1-q)^2H_k/2$. They include $k=0$, $\theta=1$, and arbitrarily
large finite rates, without a stability assumption or an observation-budget
restriction. The other signal coordinate only needs a nonnegative initial second
moment; its upper signal bound in the full theorem is unnecessary here.

`MomentRecurrence` records both equations in (T5). The theorem
`momentRecurrence_exists` constructs sequences satisfying it for arbitrary real
parameters and initial values, establishing that the hypotheses are satisfiable.
The lemma `MomentRecurrence.nonneg` derives nonnegativity of both moment
sequences from their initial values and $0\leq b\leq1/4$. The proof uses

$$
  D_b=(1-b\theta)^2+b\theta^2(1-4b)\geq0,
$$

so it also covers rates above the stability threshold.

For U, `rare_moment_floor` proves $H_k\geq1/(1+3b)$ by induction. The main
theorem then bounds the risk using the prevalence restriction.

For S, `scaled_weighted_floor` gives a shorter proof than the geometric-sum
argument in the note. For any $w\geq2$, put $W_k=C_k+wH_k$ and
$A=(1-b\theta)^2$. Nonnegative coupling and $D_b\geq A$ imply

$$
  W_{k+1}\geq A W_k+wb\theta^2,
  \qquad
  A+wb\theta^2-1=b\theta\{\theta(b+w)-2\}\geq0.
$$

Thus $W_0\geq1$ implies $W_k\geq1$ by induction. Taking $w=4(1-q)^2\geq2$ gives
$W_k=8R_{R,k}$ and proves the claimed bound. This argument also covers
$b\theta=2$ without dividing by $1-A$.

## Scope

The recurrence and risk formula correspond to independent centered Bernoulli
features, fresh observations with $B=1$, known population preprocessing, a fixed
zero intercept, zero coefficient initialization, and conditional mean-zero noise
with variance one. These probabilistic assumptions and the derivation of (T4)
and (T5) are described in the manuscript; they have not been formalized here.
The Lean theorems quantify over real sequences satisfying the displayed
recurrence. They do not assume the lower bounds they prove.

This pilot does not formalize the original rate-domain comparisons, winning
candidate bounds, continuous exponential certificate, infimum argument, or
rescaling by $\sigma^2$. It therefore does not certify the full predictive
theorem or the entire unrestricted-rate addendum. Human review of the
correspondence between these statements and the statistical model remains
necessary, as do the outstanding scientific and source-comparison reviews.

## Build and audit

Lean and Mathlib are pinned to v4.30.0; `lake-manifest.json` records the exact
dependency commits. The existing devenv environment supplies Lean and Lake. From
the repository root:

```sh
devenv shell
task prepare-lean
task check-lean
```

The preparation target downloads the required precompiled Mathlib modules. Its
first run needs network access. Dependencies and build products live in the
ignored `lean/.lake/` directory. Subsequent checks reuse those files. The Lean
targets are separate from the manuscript and numerical validation targets.

Lake may rebuild dependencies when the local toolchain's build identifier
differs from that used for the cache. The Nix Lean v4.30.0 package used for this
pilot reports its commit as `v4.30.0`, so its first build requires this
additional work.

The build treats warnings, including unfinished proofs, as errors.
[Audit.lean](NormReg/Audit.lean) also checks the transitive axiom dependencies
of the two main theorems and the existence construction against the standard
Lean axioms `propext`, `Classical.choice`, and `Quot.sound`. These checks fail
if an unfinished proof, custom axiom, or native-evaluation axiom enters their
dependencies. See the official [proof validation
guide](https://lean-lang.org/doc/reference/latest/ValidatingProofs/) for the
meaning and limits of this audit.
