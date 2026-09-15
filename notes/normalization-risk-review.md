# Independent review of the normalization-risk theorem

September 15, 2026.

## Verdict

**Passed.** Propositions 1 and 2, Theorems C1 and C2, the stability arguments,
and the stated signal-reflection and risk-decomposition claims are
mathematically valid under the declared assumptions. The certificate correctly
encloses the continuous parameter boxes and supports all reported rational
bounds. No substantive mathematical correction remains in the reviewed files.

This is an independent Codex agent review. External academic peer review and
assessment of priority, publication-level novelty, robustness to retuning, and
practical usefulness are outside its scope.

## Reviewed versions

The following SHA256 hashes identify the reviewed files:

```text
7fcba813623c5726120ebfedd7b7975601611c61bf5cc85effa493d19f4ddf64  notes/normalization-risk-theorem.md
de2723078e1529905ffcb1e56e61f98764c342f3c0159f3c319f472abc43cf26  experiments/check_normalization_risk_theorem.py
```

Sources: [the theorem note](normalization-risk-theorem.md) and [the
certificate](../experiments/check_normalization_risk_theorem.py).

Two minor presentation findings were resolved during review. The model now
states $0<q<1/2$, which makes the standardized step and conditioning on $J=1$
well-defined. The reproduction paragraph now correctly describes the
certificate's update-enumeration signal as a mixed-sign signal. Neither
correction changes C1 or C2.

## Mathematical assessment

### Exact moments and variance separation

I independently formed the update matrix from the four binary cells and expanded
its action on each of the three symmetric-matrix basis elements. This gives
exactly the displayed $L_D$. In particular,

$$
  E\widehat c^2=c^2+(ab-c^2)/B,
  \qquad
  E(\widehat c\widehat b)=cb+c(1-4b)/B.
$$

The second expression uses $E(x_Cx_R^3)=c\{(1-q)^3+q^3\}=c(1-3b)$. The remaining
fourth-moment identity and the constant common-coordinate square give the stated
last diagonal entry. Conditional mean-zero response noise removes the mixed
update terms, and its covariance contributes $\sigma^2DCD/B$.

The noiseless feature-driven path has covariance $A_k$. Conditional on the
feature stream, the noise-driven path has mean zero, so its cross moment with
the noiseless path vanishes. This proves the stated decomposition and the
positive semidefiniteness of both variance terms. The assumptions of new
independent observations and fresh noise are sufficient for these steps.

### Scalar proxy and C1

For independence, the two diagonal moments form the stated nonnegative matrix
$K_D$. The telescoping identity for $K_D^k-K_0^k$ is correct without assuming
that $K_D$ and $K_0$ commute. Submultiplicativity gives $k\rho^{k-1}E_0$, and
summing over the noise terms gives the stated $(1-\rho)^{-2}$ bound. The
one-sided remainders justify the asymmetric U/S contrast bounds. The threshold
inequality follows because both denominator bounds are positive.

The common scalar terms cancel under the specified independent-design
calibration. The certificate uses valid upper bounds for the row sums, coupling
norm, signal magnitude, and weights. Its separate check of the cross moment's
multiplier completes the mean-square stability argument. The stated stopping
reversal, batch reversal, and comparison at $M=10{,}000$ follow from the four
certified signs. The wider noise interval $(1.405,5.69)$ follows from the
threshold bounds as stated.

### C2, subgroup weights, and signs

Direct conditioning on the rare cells gives the stated $C_R$, including the
conditional mean contribution. The risk weights on the three moments are
$(a/2,c,b/2)$ and $(a/2,\ell(1-q)/2,(1-q)^2/2)$, respectively. Their difference
proves equation (4), with the displayed factor and cross-moment coefficient.

The C2 stability proof is valid. For U, the feature-norm bound is $1.2104$ and
the stated lower eigenvalue bound is $0.0096$. For S, the standardized rare
coordinate equals $7$ when present, giving $L=50$, while the standardized
second-moment matrix has off-diagonal entry $\ell/7$. Both steps meet the strict
sufficient contraction inequality throughout the stated dependence range. The
invertible coordinate transformation transfers stability to the original
coefficient scale.

The augmented matrix correctly propagates both the homogeneous second moments
and the finite noise sum. The certified diagonal contrasts are positive and the
cross-moment contrast is negative throughout C2. Thus the subgroup advantage
really can coexist with larger mean squared errors for both coefficients. The
cross moment includes the product of biases, as the note explicitly states.

Writing $J_3=\operatorname{diag}(1,-1,1)$, reflection gives
$L_D(-\ell)=J_3L_D(\ell)J_3$ and $g_D(-\ell)=J_3g_D(\ell)$. The risk weights
transform by the same $J_3$. These identities prove the claimed even/odd
coefficient structure and invariance under
$(\ell,\beta_R^*)\mapsto(-\ell,-\beta_R^*)$ with the common coefficient fixed.
The opposite-sign nested example has the threshold ordering needed for the
asserted reverse orientation.

## Certificate audit

The integer interval implementation uses the correct floor and ceiling
operations, including negative products and negative denominator intervals. The
reciprocal scale is $10^{120}$ because stored endpoints are integers in units of
$10^{-60}$. Repeated squaring, matrix products, geometric sums, and hulls
preserve enclosure. Signed C2 matrix entries are handled by all four endpoint
products.

The upper-point intervals used for norm bounds are conservative. All proof
inputs are rational strings or integers, and the acceptance comparisons use
integer endpoints. Floating-point conversion is confined to display and the
separate operator checks. The 64 closed C1 rectangles and 128 closed C2
intervals cover their entire declared domains, including shared boundaries.
Noise and signal intervals are propagated as intervals rather than sampled.

The supplied script completed successfully under ordinary Python:

```sh
devenv shell -- python experiments/check_normalization_risk_theorem.py
```

## Independent calculations

Separate review code was written in
`/tmp/normalization_risk_independent_review.py` and run with:

```sh
devenv shell -- python -u /tmp/normalization_risk_independent_review.py
```

The independent model calculations use the binary cells and actual update
matrices. They do not call the project's existing moment or path routines. The
reviewed module is imported only to compare its transition and interval
primitives with independently calculated answers.

The following checks passed:

- **120 exact rational operator checks**, covering two prevalences, five
  dependence values, two steps, $B=1,2,3$, and both configurations. Each
  averages actual batch updates over every feature-cell sequence and checks all
  symmetric-matrix basis elements and the noise column. Conditional test weights
  were checked directly from the same cell law.
- **24 exact noisy two-update path enumerations**, covering positive and
  negative dependence, an interior law, $B=1,2$, both configurations, and both
  relative signal signs. These confirm the mean, second moments, vanishing
  noiseless/noise cross moment, variance decomposition, and positive
  semidefiniteness of both variance components.
- **13,992 exact rational checks of interval operations**, including signed
  addition, subtraction, multiplication, division, powers, and finite sums.
  Exact partition boundaries and overlaps were checked separately. These checks
  supplement the enclosure argument above.
- **A separate continuous-box calculation** using 55-digit decimal arithmetic
  with directed rounding. It reproduces all four C1 enclosures and verifies
  containment in every reported risk and threshold bound. For C2, its transition
  matrix is obtained from exact cell-update operators at $\ell=0,1$ and their
  affine dependence on $\ell$ when $B=1$. It uses the same 128-interval covering
  and independently verifies both risk signs and all three coefficient-moment
  signs.
- **Exact rational endpoint calculations** at all four dependence/signal
  settings in the threshold table. All eight displayed thresholds round
  correctly. The endpoint risk values and comparison signs agree. Eight exact
  operator/weight reflection checks additionally support the algebraic
  reflection argument.
- **Independent long-path bias and variance calculations** at both C1 stopping
  counts. Every displayed decomposition entry rounds correctly. At the late S
  stop, squared bias is approximately $2.47\times10^{-18}$ and update variance
  is approximately $1.40\times10^{-17}$, both below $10^{-16}$ as reported.

The independent C2 calculation gives the following outward-broadened decimal
enclosures. Its slightly tighter values arise from the affine cell-based
construction of the transition matrix.

  | S-minus-U quantity     | Independent enclosure       |
  | ---------------------- | --------------------------- |
  | Aggregate risk         | $[0.00077676,0.00193630]$   |
  | Rare-presence risk     | $[-0.09818463,-0.02347951]$ |
  | Common coefficient MSE | $[0.01966069,0.02277549]$   |
  | Cross moment           | $[-0.61591746,-0.59398004]$ |
  | Rare coefficient MSE   | $[0.41302615,0.49650209]$   |

The risk enclosures lie within C2's reported rational bounds. The findings
support computer-assisted mathematical validity for the stated comparisons; they
do not extend the claims beyond the fixed calibrations and parameter ranges in
the theorem note.
