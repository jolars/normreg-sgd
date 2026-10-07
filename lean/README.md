# Lean proof pilot

This project formalizes large-rate lower bounds used in the
[manuscript](../paper/main.tex)'s finite-prevalence and limiting-oracle proofs.
It treats the exact moment recurrences as explicit hypotheses and uses the
manuscript's rare-subgroup risk. The finite-prevalence bounds normalize noise
variance to one; the limiting-oracle bounds allow arbitrary nonnegative noise
variance.

## Finite-prevalence bounds

The definitions and proofs are in [LargeRates.lean](NormReg/LargeRates.lean),
under the `NormReg` namespace. Write $b = q(1 - q)$, and let $\theta$ denote the
manuscript's rare-coordinate step $\alpha$. Both main theorems assume
$0 < q \leq 1/16$ and $\theta \geq 1$, and hold for every $k \in \mathbb N$:

  | Lean theorem                      | Recurrence and initialization              | Conclusion                           |
  | --------------------------------- | ------------------------------------------ | ------------------------------------ |
  | `unscaled_large_rate_lower_bound` | U: $u = \theta/4$, $C_0 \geq 0$, $H_0 = 1$ | $(1 - q)^2/[2(1 + 3b)] \leq R_{R,k}$ |
  | `scaled_large_rate_lower_bound`   | S: $u = b\theta$, $C_0 = 1$, $H_0 \geq 0$  | $1/8 \leq R_{R,k}$                   |

These are the analytic floors used to cover all rates above one in the
finite-prevalence oracle comparison. The U theorem exposes the manuscript's
prevalence-dependent floor directly. The corollary
`unscaled_small_prevalence_lower_bound` retains the original strict bound
$49/100 < R_{R,k}$ when $0 < q \leq 10^{-4}$.

The formal statements use the original coefficient scale and
$R_{R,k} = C_k/8 + (1 - q)^2H_k/2$. They include $k = 0$, $\theta = 1$, and
arbitrarily large finite rates, without a stability assumption or an
observation-budget restriction. The other signal coordinate only needs a
nonnegative initial second moment; its upper signal bound in the full theorem is
unnecessary here.

`MomentRecurrence` records both moment equations. The theorem
`momentRecurrence_exists` constructs sequences satisfying it for arbitrary real
parameters and initial values, establishing that the hypotheses are satisfiable.
The lemma `MomentRecurrence.nonneg` derives nonnegativity of both moment
sequences from their initial values and $0 \leq b \leq 1/4$. The proof uses

$$
  D_b = (1 - b\theta)^2 + b\theta^2(1 - 4b) \geq 0,
$$

so it also covers rates above the stability threshold.

For U, `rare_moment_floor` proves $H_k \geq 1/(1 + 3b)$ by induction. The main
theorem weights this floor by $(1 - q)^2/2$ and uses $C_k \geq 0$ to obtain the
displayed risk bound.

For S, `scaled_weighted_floor` uses a weighted moment bound. For any $w \geq 2$,
put $W_k = C_k + wH_k$ and $A = (1 - b\theta)^2$. Nonnegative coupling and
$D_b \geq A$ imply

$$
  W_{k+1} \geq A W_k + wb\theta^2, \qquad A + wb\theta^2 - 1
          = b\theta\{\theta(b + w) - 2\} \geq 0.
$$

Thus $W_0 \geq 1$ implies $W_k \geq 1$ by induction. Taking
$w = 4(1 - q)^2 \geq 2$ gives $W_k = 8R_{R,k}$ and proves the claimed bound.
This argument also covers $b\theta = 2$ without dividing by $1 - A$.

## Bounds for the limiting oracle proof

[OracleLargeRates.lean](NormReg/OracleLargeRates.lean) formalizes the general
bounds in the opening subsection of [the limiting oracle
proof](../paper/oracle-proofs.tex). Its `GeneralMomentRecurrence` uses
$G_k = C_k/4$, initial values $G_0 = s/4$ and $H_0 = r$, and arbitrary noise
variance $\nu \geq 0$. Thus $v = G_0 + H_0 = s/4 + r$, and
$R_{R,k} = \{G_k + (1 - q)^2H_k\}/2$. The proofs require only nonnegative
initial moments. `MomentRecurrence.toGeneral` checks the change of common-moment
scale at noise variance one, and `rescaledRareRisk_eq` checks the risk formula
against `rareRisk`. `generalMomentRecurrence_exists` constructs sequences for
arbitrary real parameters and initial values.

Write $w = (1 - q)^2$, $D_b = 1 - b\theta(2 - \theta + 3b\theta)$, and
$\lambda_b = 1 - 2b\theta + b\theta^2(1 - 3b + b^2)$. For $0 < q \leq 1/2$, the
theorems `oracle_unscaled_geometric_lower_bound` and
`oracle_scaled_geometric_lower_bound` prove, respectively,

$$
  R_{R,k}^U
  \geq \frac w2\left[ D_b^kr + b\theta^2\nu \sum_{j=0}^{k-1}D_b^j \right],\qquad R_{R,k}^S
            \geq \frac w2\left[ \lambda_b^kv + b\theta^2\nu \sum_{j=0}^{k-1}\lambda_b^j \right].
$$

These hold at every finite stop and every real rate, including all nonnegative
rates in the oracle domain. For S, the proof bounds $G_k + H_k$ by a scalar
recurrence with multiplier $\lambda_b$ and forcing $b\theta^2\nu$. It checks
that the omitted common-moment term and extra noise term are nonnegative.

The definitions `unscaledRateCutoff` and `scaledRateCutoff` give

$$
  c_U(b) = \frac{2}{1 - 3b},\qquad c_S(b) = \frac{2}{1 - 3b + b^2}.
$$

The theorems `oracle_unscaled_large_rate_lower_bound` and
`oracle_scaled_large_rate_lower_bound` prove $R_{R,k}^U \geq wr/2$ for
$\theta \geq c_U(b)$ and $R_{R,k}^S \geq wv/2$ for $\theta \geq c_S(b)$. They
include equality at the cutoffs, initialization, zero signal, and zero noise,
with no stability assumption. Finite geometric sums avoid division by zero when
a drift factor equals one.

Finally, `oracle_rate_cutoff_bounds` gives the explicit small-prevalence range
$0 \leq q \leq 1/16$ on which $2 \leq c_S(b) \leq c_U(b) < 3$ and
$1 - w \leq 4b$. These are the cutoff and risk-weight bounds used to restrict
the rate domain in the limiting proof.

## Scope

The recurrence and risk formula correspond to independent centered Bernoulli
features, fresh observations with $B = 1$, known population preprocessing, a
fixed zero intercept, zero coefficient initialization, and conditional mean-zero
noise with constant nonnegative variance. These probabilistic assumptions and
the derivation of the risk and moment recurrences are described in the
manuscript; they have not been formalized here. The Lean theorems quantify over
real sequences satisfying the displayed recurrences. They do not assume the
lower bounds they prove.

The finite-prevalence pilot does not formalize bounds for rates below one,
winning candidate bounds, interval certificates for the oracle gaps, the infimum
argument, or rescaling by $\sigma^2$. It therefore does not certify the full
finite-prevalence theorem. For the limiting-oracle theorem, only the general
large-rate bounds and cutoff properties are checked. Its uniform approximations,
recovery argument, and convergence rates remain outside the formalization. Human
review of the correspondence between these statements and the statistical model
remains necessary.

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
of the main risk bounds, the small-prevalence corollary, the cutoff bounds, both
existence constructions, and the recurrence and risk correspondences against the
standard Lean axioms `propext`, `Classical.choice`, and `Quot.sound`. These
checks fail if an unfinished proof, custom axiom, or native-evaluation axiom
enters their dependencies. See the official [proof validation
guide](https://lean-lang.org/doc/reference/latest/ValidatingProofs/) for the
meaning and limits of this audit.
