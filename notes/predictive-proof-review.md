# Proof review of the predictive theorem and uniform remainder

September 17, 2026.

## Verdict and scope

**Passed under the stated assumptions.** The stability and uniform remainder
proposition in [the feasibility proof](predictive-claim-feasibility.md) and the
two oracle separations in [the direct theorem](predictive-theorem.md) are
mathematically valid. The continuous certificates support the advertised
inequalities. No mathematical correction to those results was needed.

This is a Codex review of the earlier development, with new calculations that
import none of the project's existing checkers. It is not human verification or
external academic peer review. The mathematical review covers the model and
recurrence definitions in (P1)–(P5), the complete stability/remainder argument,
the direct predictive proof, and the certificate implementations. The earlier
[expansion-based derivation](predictive-regime.md) was also checked for
consistency with these arguments. The cited literature comparison was not
independently re-audited, and publication-level novelty remains undecided.

The review also supplies a short argument removing the predictive theorem's
upper rate restriction. This is a new addendum developed during the review, with
separate arithmetic checks. It has not itself received an independent review or
human review. The original proof files and their statements are preserved. This
note updates the review status recorded in those dated files.

## Exact moments and the approximation

Write the original-scale error update as

$$
  e_{k+1}=(I-D\widehat C_{k+1})e_k+D\overline{x\varepsilon}_{k+1},
  \qquad D=\operatorname{diag}(4u,v/b).
$$

The four cell probabilities are nonnegative on the declared domain. Conditional
mean-zero response noise removes the mixed signal/noise terms. Independent
observations and conditional variance $\sigma^2$ give the noise covariance
$\sigma^2DCD/B$. No Gaussian assumption is needed.

The constant common square, $x_C^2=1/4$, and the binary identities give

$$
  E\widehat c^2=c^2+(b/4-c^2)/B,
  \qquad
  E(\widehat c\widehat b)=c\{b+(1-4b)/B\}.
$$

Expanding the three symmetric second moments gives precisely (P3). Setting the
upper-right entry of the random update matrix to zero gives $L_0$, including its
common-to-rare terms. Keeping the noise vector unchanged is legitimate for this
analytical surrogate. Direct integration of the rare-presence cells gives the
displayed $C_R$ and the risk weights, including the conditional mean
contribution and the factor $1/2$.

For $d_k=s_k-z_k-\xi_k$, direct subtraction gives $d_{k+1}=Ld_k+H\xi_k$. Thus
(P5) bounds the signed residual entrywise without assuming that the correction
is a positive semidefinite moment matrix. Its signal and noise decomposition
follows from linearity. The exact small-batch and finite-remainder checks below
reconstruct these facts from the cell law.

## Uniform stability and the quadratic remainder

The identity $|L|=Q+J$ is exact: the only overlapping nonzero entries of $L_0$
and $H$ are positive middle diagonal entries. The potentially negative
$\chi=1-v-\theta(1-4b)$ is correctly handled with absolute values.

The bounds $\kappa\leq8/15$, $-v\leq\chi\leq1-v$, and $\omega\leq289/900$ hold
throughout (P1). For (F6), the coefficient $3-15q+16q^2$ decreases to $17/8$ on
the prevalence interval. In the negative-$\chi$ case, $|\chi|\leq1/4$ and
$(1-q)+1/\{4(1-q)\}\leq5/4$ give the asserted bound.

The three entries of each vector inequality in (F8) and (F9) check out. In
particular, the weakest third-coordinate deficits are $41v/900$ and $371v/900$
for the two $\lambda$ comparison vectors, and $941v/900$ for the noise vector.
They remain strictly positive at the domain boundaries. The first two
coordinates, where feedback enters, have deficits proportional to $u$. This is
the step that avoids a spurious factor $u/v$.

Consequently $Qp\leq\lambda p$, the nonnegative resolvent
$\mathcal K=(\lambda I-Q)^{-1}J$ exists, and $\mathcal Kh\leq4qh$. Since
$4q\leq1/4$, its Neumann series converges. The displayed inequality

$$
  (\lambda I-|L|)h\geq(1-4q)(\lambda I-Q)h>0
$$

proves the claimed strict spectral-radius bound by the weighted maximum norm. It
is stronger than checking the eigenvalues at finitely many configurations.

The factors of $\lambda$ in the signal accumulation are correct:

$$
  \sum_{j<k}Q^{k-1-j}J\lambda^j
  \leq\lambda^k(\lambda I-Q)^{-1}J.
$$

One feedback insertion costs at most $2q$ for the signal and $4q$ for the noise.
The second insertion and its subsequent propagation give respectively
$8q^2/(1-4q)$ and $16q^2/(1-4q)$. For noise, replacing the resolvents at one by
those at $\lambda<1$ increases their nonnegative entries. This justifies (F12)
and (F13) for all finite $k$, with no lower bound on $q$ or the positive step.

Finally, $\mu_C\leq7/32$, $\mu_{C_R}\leq13/8$, and $1-4q\geq3/4$ give (F2).
Taking the larger noise coefficient gives the common constant $104/3$ in (P2).
Zero learning rate is treated separately, as stated. The proof does not extend
its stability claim to rates outside (P1).

## Direct predictive theorem

Under independence, the odd common moments vanish. The cross error moment
therefore affects neither diagonal recurrence nor rare-presence risk. This
justifies (T5), the absence of a signal-sign restriction, and the nonnegative
coupling used throughout the proof.

For the rare-signal family, $A\leq D_b$ on the original rate domain. Dropping
nonnegative terms gives (T6). Its affine dependence on $D_b^k$ reduces the lower
bound over all earlier stops to the two endpoints. This includes $k=0$ and
arbitrarily small rates, without interchanging an infimum and a limit.

One small detail is worth making explicit in the $11q$ transfer. The initial and
noise coefficient errors are bounded by $2q$ and $5q$, but their weights are $z$
and $1-z$. Their combined error is at most $5q$, not $7q$. The exponential error
contributes at most $16q$. Thus the factor $1/2$ gives $21q/2<11q$, as used by
the checker. The proof's stated constant is valid.

For S, the exact combination $Y_k=C_k/4+H_k$ obeys (T8). The discarded term has
coefficient $b^2\theta^2(4-b)\geq0$. The geometric sum and exponential transfer
give the stated $5q$ upper error. Hence the continuous limiting gap $1/100$
yields a finite gap at least $1/100-16q\geq0.0084$, stronger than the advertised
$0.007$.

For the common-signal family, (T13) follows from common squared bias and
$Mb\leq4$. In (T14), the minimum of $z^2/8+(3/50)(1-z)$ over $[0,1]$ is
$33/625$. The two rate cases therefore give a uniform lower bound exceeding
$1/60$. For the U candidate, summing the common equation and then bounding the
rare equation gives exactly the coefficients $68h^3$, $64h^2$, and $64h^5$ in
(T15). The final upper bound is less than $0.01072966$, and
$1/60-11/1000>1/200$.

For each ordering, the proof compares a bound for every competing rate and stop
with one admissible candidate for the winning method. It does not assume that
the candidate is optimal. The compact original domain also justifies the
statement about attained minima. All risks average over training randomness; the
rate and stop are deterministic oracle choices, not validation selectors.

## Continuous-certificate audit

Both original exponential enclosures are sound. For (T11), every omitted
positive-series term has successive ratio at most $x/20<1$, giving the stated
geometric tail bound before reciprocation. The older certificate's signed Taylor
remainder also encloses the exponential on $[0,4]$.

The rectangle bounds correctly use monotonicity in $N$ and change the
exponential endpoint when $1-N$ changes sign. The S candidate's plateau
decreases with $\tau$, while its exponent increases; its initial coefficient
exceeds the plateau. Its risk therefore decreases, as required for the upper
bound at the lower budget endpoint. The direct checker explicitly includes the
minimum with $1/2$; the older checker establishes that baseline separately.

The recursive subdivisions partition the original rectangle, with only shared
edges. Exact total area three and termination confirm complete coverage. All
acceptance comparisons use fractions; displayed decimal margins play no role in
acceptance. The reported 5,035 and 3,197 original leaf counts reproduce.

The new [review checker](../experiments/check_predictive_review.py) uses a third
construction: degree-13 and degree-12 Taylor bounds for $e^{-x/4}$, followed by
fourth powers, and ternary subdivision. The intermediate bounds are nonnegative.
It certifies **3,925 leaves**, maximum depth **11**, total area **3**, and a
minimum rational margin greater than **0.010000090**. This covers the continuous
comparison, not just sampled points.

## Addendum: the predictive rate cap can be removed

Keep every model, signal, noise, and budget assumption of the direct theorem,
but define

$$
  \widetilde R_A^*
  =\inf_{\theta\geq0,\ k\in\{0,\ldots,M\}}R_{R,k}^A(\theta),
  \qquad A\in\{U,S\},
$$

using the same $D_U(\theta)$ and $D_S(\theta)$. The two advertised gaps still
hold with these enlarged infima. In particular, they hold when each method
searches all its mean-square-stable nonnegative constant rates. The argument
actually bounds every finite nonnegative constant rate, including unstable ones
at finite stops. It does not assert stability of those additional rates.

Normalize $\sigma^2=1$ again. It suffices to exclude $\theta\geq1$ for the
losing method in each signal family. The original winning candidates remain
available and stable. Equation (T5) continues to hold outside the original rate
interval, and its entries remain nonnegative because they are squared update
coefficients and their expectations.

### Rare signal: large U rates cannot beat the S candidate

Here $H_0=1$. Put $m_b=1/(1+3b)$. For every $\theta\geq1$,

$$
  D_bm_b+b\theta^2-m_b
  =\frac{2b\theta(\theta-1)}{1+3b}\geq0.
$$

Dropping the nonnegative common-to-rare term and using induction proves
$H_k\geq m_b$ for every stop. Therefore

$$
  R_{R,k}^U(\theta)
  \geq\frac{(1-q)^2}{2(1+3b)}
  \geq\frac{(1-Q)^2}{2(1+3Q)}>\frac{49}{100}.
$$

The original S candidate, with $\theta_S=2/(\tau+4)$ and $k=M$, satisfies

$$
  R_{R,M}^S(\theta_S)
  \leq F_S(2/(\tau+4),\tau;1/100,1)+5q
  \leq F_S(2/5,1;1/100,1)+5Q<\frac13.
$$

The last inequality is certified rationally in the review checker. Thus every
new U competitor loses to this candidate by more than $49/100-1/3>7/1000$.
Original-domain competitors already have the required gap. Taking the enlarged
infima proves $\widetilde R_U^*-\widetilde R_S^*\geq7/1000$.

### Common signal: large S rates cannot beat the U candidate

Here $C_0=1$ and $H_0\geq0$. Set $A=(1-b\theta)^2$. The exact identity

$$
  D_b-A=b\theta^2(1-4b)\geq0
$$

and nonnegativity imply

$$
  C_k\geq A^k,\qquad
  H_k\geq b\theta^2\sum_{j=0}^{k-1}D_b^j
        \geq b\theta^2\sum_{j=0}^{k-1}A^j.
$$

If $A\geq1$, common error alone gives $R_{R,k}^S\geq1/8$. Otherwise
$0<b\theta<2$, and geometric summation yields

$$
  R_{R,k}^S\geq\frac{A^k}{8}
    +\frac{(1-q)^2\theta}{2(2-b\theta)}(1-A^k).
$$

For $\theta\geq1$, the second coefficient is at least $(1-q)^2/4>1/8$. Hence
$R_{R,k}^S\geq1/8$ in this case too, including $k=0$. The original U candidate
has risk below $11/1000$, so all added S competitors lose by more than
$1/8-11/1000>1/200$. Together with the original-domain comparison, this proves
$\widetilde R_S^*-\widetilde R_U^*\geq1/200$. Rescaling restores $\sigma^2$ in
both gaps.

This removes the rate-cap objection for these two particular families. It does
not remove the assumptions of independence, two features, $B=1$, known
preprocessing, the signal-to-noise equalities, or the prevalence/budget range.
It provides no selection guarantee or ordering over learning-rate schedules.

## Reproduction and remaining review

The following commands passed inside the devenv environment:

```sh
devenv shell -- make check-predictive-claim
devenv shell -- make check-predictive-review
```

The new checker performs:

- 36 exact enumerations of batches of size one, two, and three, checking the
  exact and surrogate operators and both risk weights.
- 432 exact vector-inequality checks, including 24 negative-$\chi$ cases,
  prevalence down to $10^{-12}$, and batch size up to $10^8$.
- 1,296 exact finite residual and envelope checks, including zero noise,
  opposite signal signs, dependence boundaries, and zero stops.
- The separate 3,925-leaf continuous certificate and exact checks of the
  finite-prevalence transfer constants.
- 21 exact checks of the unrestricted-rate identities, including the $b\theta=2$
  boundary and rates above it.
- 576 finite comparisons using 85-digit arithmetic, including $q=10^{-12}$,
  rates above one, and observation budgets of approximately $4\times10^{12}$.

The finite 85-digit calculations are diagnostics, not outward-rounded
certificates; their square-root candidate rate is also approximated at that
precision. The continuous proof uses the displayed inequalities and exact
rational enclosures. The additional algebra checks support the new addendum; its
universal rate statements rely on the induction and geometric-sum arguments
above.

Human mathematical review, independent review of the new addendum, and review of
the source comparison remain open. The central-contribution decision and
held-out prediction experiment are separate tasks. No frozen experimental
artifacts or original theorem statements were changed by this review.

## Reviewed versions

These SHA-256 hashes identify the unchanged principal review inputs:

```text
2adf18d51abfb8d551a2687739c5cd7e46bac6318bd710191b96f84694f8aa14  notes/predictive-claim.md
fbfc185df0802f2baaefa9bdc38569f4e562f1e7f78667289ae0b9453f6a84f0  notes/predictive-claim-feasibility.md
4649b030b26c37d3e25faf2abe5de31724291f25d9677f52acff6556d26a77fd  notes/predictive-theorem.md
2d24cd23667f12d4274200bed5ff12a8277accc9a5635139447e0236c375934e  experiments/check_predictive_claim.py
7f03db5d00773f6dda67e005445fde6d16bc0c2cb4c87263872b24bccaee7ccb  experiments/check_predictive_feasibility.py
f95b00a3176149f5c359a5afbd485283bbfbfe34555b12e2e93dae0753667936  experiments/check_predictive_regime.py
35139e4e57a188ab52136498f57c8b7717ddaa0b1cda756911d004d83a63f51e  experiments/check_predictive_theorem.py
```
