# Independent referee report: joint observation-budget theorem

Date: September 15, 2026. Referee assignment: ct-01M2HWA2ST21FGWH602SWNTQNW.
Reviewed theorist task: ct-01M2HVEVWMDAZZ6QKYB2CKPDJ4, assignment
ca-01M2HVF3DYZM4STC686R59RP19.

## Exact material and verdict

I independently reviewed notes/joint-budget-limits.md at commit
c82e75270cca9b92d45716b7a018867b88691035 in
/home/jola/.local/state/coterie/runs/cr-01M2HV7JE2YF36E4VSWD86THG9/workspaces/cp-01M2HV7JE2YFNPEJ0V6A6F70HM/ca-01M2HVF3DYZM4STC686R59RP19.
HEAD and the note's SHA256
f9641f1eec69b2ec99ed808e4f44f13657b0d5a772fca2a85398d0d659cf8736 matched the
assignment. Git status was clean before and after review. I read that worktree's
AGENTS.md and used paper/sections/discrete-dynamics.tex and
paper/sections/stochastic-gradient.tex at the same commit for context. I made no
repository source edits.

Verdict: no material mathematical defect found. The finite-budget inequalities
(5), matrix noise limit (6), and original-scale consequences (7) follow under
the stated assumptions. I recommend mathematical acceptance of this exact
candidate note, with the nonblocking scope clarification below. This is a
validity verdict, not a novelty or publication verdict.

## Findings, ordered by consequence

1. No blocking finding in the candidate theorem or its proof. I found no missing
   convergence rate for the common marginal or dependence, no missing fourth
   noise moment, and no unsupported exchange of growing-budget and rarity
   limits.
2. Minor clarification, notes/joint-budget-limits.md:412-422, compared with the
   finite schedule at lines 75-90. The fixed-q limit k -> infinity uses the
   natural extension eta_j = 2/(ceil(16/q)+j), j >= 0, and an infinite iid
   stream. Equation (3) formally defines only j < n from a finite budget. State
   explicitly that the iterated-limit comparison uses this auxiliary
   infinite-stream extension. The extension immediately validates the argument;
   no change to the finite-budget theorem, constants, or rates is needed.
   Suggested sentence: "For this iterated-limit comparison, extend the same step
   schedule to every j >= 0 using an infinite fresh-observation stream." This is
   a scope clarification, not a counterexample.

## Verdicts on the principal conclusions

  | Claim and location                                                                                             | Verdict                                                   | Reason                                                                                                                                            |
  | -------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
  | Exact centered-covariance separation, (4), (10)-(11), lines 94-104 and 189-224                                 | Valid                                                     | Conditional mean-zero noise and iid triples remove all cross terms, even when the conditional noise distribution depends on the features.         |
  | Uniform finite-budget bounds, (5), lines 105-118                                                               | Valid for every n >= n0 and integer 0 <= k <= n           | The stated binary bounds imply the uniform one-step trace contraction; the mean and noise bounds use distinct, valid recurrences.                 |
  | n N_n -> (4 sigma^2/3) I_2, (6), lines 124-127                                                                 | Valid in operator norm                                    | The PSD propagation difference is o(1/n); a uniform late-observation approximation and a separate early-observation bound establish the constant. |
  | Original rare squared bias O(n^(-5/4)), design variance O(n^(-1)), and variance/MSE limits, (7), lines 131-146 | Valid for q_n = n^(-1/2)                                  | Original-scale conversion divides each rare second moment by b_n, followed by direct comparison with 1/(n q_n).                                   |
  | Broader sufficient condition, lines 399-411                                                                    | Valid, retaining the other model assumptions and schedule | n^2 q_n^3 -> infinity controls the conservative design bound and also the squared-bias bound. It is sufficient, not established as necessary.     |
  | Noncommuting rare/stopping mean limits, lines 412-422                                                          | Valid under the explicit extension described above        | Fixed k gives a product tending to the identity on the original scale; fixed full-rank q gives mean convergence to the signal.                    |

## Independent proof audit

### 1. Binary feasibility, uniformity, and fourth moments

At lines 32-52 and 164-183, c/b = E(W\|J=1)-E(W\|J=0) really belongs to
\[-1,1\]. Thus \|rho\| <= sqrt(b/a) <= sqrt(q/a0) <= 1/8. This proves (8),
including full rank; it does not require a rate for p_n -> p or kappa_n ->
kappa.

The pointwise rare bound is valid at both J values: z_R^2 is either (1-q)/q or
q/(1-q), both at most 1/q when q < 1/2. The common bound is z_C^2 <= 1/a0. Since
q <= a0/64, their sum is at most 65/(64q). Multiplication by zz^T, then
expectation, gives K <= (65/(64q))H <= (585/(512q))I <= (2/q)I exactly as in
(9). Mixed fourth moments are therefore controlled, including cells of
probability zero and either sign of dependence.

The constants in these inequalities are uniform over the stated class with fixed
a0. The convergence assumptions on p and kappa are stronger than this proof
needs. C\_\* <= M^2/4 follows because both Bernoulli variances are at most 1/4.
No boundedness or higher moment of response noise is used here.

### 2. Covariance versus second moment and noise requirements

The actual scaled update is u\_(j+1) = (I-eta_j zz^T)u_j + eta_j z epsilon.
Independence of successive triples makes the next random map independent of the
current error. Conditional on all features, different innovations have zero
cross moments, and their cross moments with the noiseless trajectory are zero.
The conditional variance assumption gives E\[epsilon^2 zz^T\] = sigma^2 H.

Consequently U_j^(0) = E\[u_j^(0)u_j^(0)T\] propagates by T_j, while its
centered covariance is D_j = U_j^(0)-m_j m_j^T. Subtracting the next mean outer
product produces the eta_j^2 V(m_j m_j^T) source in (11). This source must not
be omitted; the note includes it. N_j is the covariance of propagated noise,
including its later interaction with random update matrices. Equation (4)
therefore describes centered covariance, not the full second moment.

All finite-update second moments exist by induction: the design is bounded for
each n, and the innovations have finite second moment. The bounds are uniform
despite the design bound growing with rarity. Conditional noise laws may vary
with n and with (W,J). Fixed conditional variance suffices; neither Gaussian
noise, independence of epsilon from the same observation's features, a fourth
noise moment, nor a triangular-array Lindeberg assumption is needed for these
second-moment conclusions.

### 3. Finite-k contractions and endpoints

In (12), the coefficients are correct: 2 eta_j (7/8) = 7/(2s_j) and eta_j^2
(2/q) = 8/(q s_j^2). The condition q s_j >= 16 leaves contraction at most
1-3/s_j, a positive number. For (13), the decreasing-function integral
inequality is in the correct direction: sum\_(j=l)^(k-1) 1/(tau+j) >=
log((tau+k)/(tau+l)). This includes the empty product l=k.

D_k <= U_k^(0) in PSD order proves the design bound. Separately, the positive
mean update matrices satisfy norm(R_j) <= 1-7/(4s_j), which yields exponent 7/2
after squaring. The noise trace source is eta_j^2 sigma^2 tr(H) = 8
sigma^2/s_j^2. The induction in (15) holds because (s-1)/s^2 <= 1/(s+1). None of
these bounds assumes a stationary step or a constant moment operator.

At k=0 the bias bound follows from C\_\* >= b beta_R\*^2; D_0=N_0=0 satisfy
their conservative bounds. All denominators are positive because tau > 3.

### 4. Random propagation versus mean propagation

Subtracting (16) from (11) gives (17) with V(N_j), not V(Nbar_j). Since V
preserves PSD matrices, F_j=N_j-Nbar_j is PSD by induction. Also tr V(U) =
tr(KU)-tr(HUH) lies between zero and (2/q)tr(U) for PSD U. Combining this with
tr N_j <= 4 sigma^2/s_j gives the source 32 sigma^2/(q s_j^3).

The source injected at update j is propagated through updates j+1,...,k-1. The
product at lines 318-326 is therefore G\_(j+1,k) =
\[(s_j-2)(s_j-1)s_j\]/\[(tau+k-3)(tau+k-2)(tau+k-1)\]. Its value is one for
j=k-1, as required. Bounding each summand yields exactly (18), including k=0
through its empty sum. At k=n, n \|\|F_n\|\| <= 32 sigma^2 n^2/\[q(tau+n-3)^3\] =
O(1/(nq)) -> 0 when nq -> infinity. No diagonalization or commutation of the
random update matrices is assumed.

### 5. Uniform noise limit and limit exchanges

Equation (19) follows from diagonalizing H and the deterministic R_j matrices;
its propagation begins at l=j+1 and ends at n-1, correctly excluding the update
that injects the noise.

For m=ceil(delta n), the early terms are exactly Nbar_m propagated through
R_m,...,R\_(n-1). Their trace is bounded by 4 sigma^2 (tau+m)^2/(tau+n)^3, so
the limsup after multiplying by n is at most 4 sigma^2 delta^2. This bound
applies simultaneously to both eigenmodes.

On the late interval, h remains in \[7/8,9/8\], the logarithmic Taylor remainder
is uniformly bounded by a constant times sum s_l^(-2), and the harmonic-sum
integral error is O(1/(tau+j+1)). At j=n-1 the product and harmonic sum are
empty and the endpoint formula remains valid. Since tau/n -> 0, the product
converges uniformly to (j/n)^4 on j/n >= delta. Together with n^2/s_j^2 ->
(j/n)^(-2), the late part of n v\_(h,n) is a Riemann sum for 4 sigma^2
integral_delta^1 x^2 dx.

The positive early part, with its O(delta^2) envelope, can then be removed after
taking n -> infinity. This proves the constant 4 sigma^2/3. A common limit for
both eigenvalues gives operator-norm convergence independent of eigenvector
choices, including rho=0.

In particular, the proof does not need an extra condition such as \|rho_n\| log
n -> 0. The late fraction keeps the relevant logarithms bounded, while the early
fraction is controlled separately. The approximation of random propagation is
justified independently by (18). The note does not extrapolate the existing
manuscript's fixed-k result.

### 6. Original scale, broader rarity, and boundary interpretation

For q=n^(-1/2), tau is asymptotic to 16 sqrt(n), so the two conservative
original rare bounds are q^(-1) O((tau/n)^(7/2)) = O(n^(-5/4)) and q^(-1)
O((tau/n)^3) = O(n^(-1)). Equation (6), b=q(1-q), and sigma^2>0 give N_RR/b \~ 4
sigma^2/(3nq). Squared bias and design variance disappear after multiplication
by nq=sqrt(n), proving both final limits in (7). Markov's inequality gives the
stated O_P rate; it does not imply a normal limit.

For general q -> 0 and nq -> infinity, the displayed design bound divided by the
benchmark 1/(nq) is O(1/(n^2 q^3)); the squared-bias ratio is O(1/(n^(5/2)
q^(7/2))). The identity n^(5/2) q^(7/2) = (n^2 q^3)sqrt(nq) proves the asserted
sufficient extension. At gamma=2/3 this conservative design bound does not
resolve negligibility. The note correctly avoids treating that failure as a
counterexample.

For the auxiliary iterated-limit experiment, PC has bounded entries on the
original scale, so fixed-k products tend to I as q -> 0. At any fixed feasible,
full-rank q, the extended schedule has positive mean factors and divergent total
step size, yielding convergence to beta\*. The two rare-coordinate limits differ
when beta_R\* != 0. The scalar fixed-step instability discussion is also
correct: its second-moment factor exceeds one for sufficiently small q at any
fixed positive eta.

Zero signals and either sign of dependence are covered; sigma^2=0 removes the
positive-noise equivalence rather than producing the same asymptotic statement.
The known positive population scale defines updates even on an absent-rare
sample. The theorem includes that event in its expectations. It gives no
empirical-preprocessing or fixed-data resampling conclusion.

## Independent validation and environment

The proof audit above is the basis for the verdict. I did not treat the lead's
or theorist's numerical agreement as proof evidence.

As a supplemental check, I ran file-free Python Fraction arithmetic, with
assertions enabled. It enumerated all feature/noise paths through three updates
for nine feasible binary laws: q=1/1024, r0 in {1/4,1/2,3/4}, r1 in {0,1/2,1},
a0=1/8, beta\*=(4/5,-2/5), sigma^2=1. The calculation used original-coordinate
sampled gradient maps, not an assumed standardized limiting covariance.
Conditional noise was symmetric +/-1 when W=0, and {-2,1/2} with probabilities
{1/5,4/5} when W=1. Both conditional variances are one, while their laws depend
on the feature.

All 36 population/update checks passed: exact means, noiseless centered
covariance, total centered covariance, zero noiseless/noise cross moment, PSD D,
N, and N-Nbar, curvature and K inequalities, and the displayed mean, design,
noise-trace, and propagation-difference bounds. A separate 188 exact rational
checks verified the telescoping product identity for offsets {4,17,4096,16384},
several stopping counts, and every source index, including empty products. These
finite checks supplement the analytic uniform proof; they do not establish its
asymptotic conclusions by themselves.

The initial devenv runtime probe succeeded. A subsequent devenv-shell invocation
failed on .devenv/imports.txt with "Read-only file system (os error 30)". I did
not change permissions or bypass that write restriction. I ran the file-free
rational calculation with the inherited Python runtime and bytecode writing
disabled instead. I did not rerun the project's build or full check suite for
this read-only proof review. git diff --check for the reviewed commit passed,
and the reviewed worktree and note hash remained unchanged. No source commit is
needed from this referee.

## What this proves relative to the framework, and what remains unchecked

Relative to the standard least-squares moment recurrences used as a starting
point, this note supplies an explicit bound uniform over k <= n and the feasible
rare binary populations while the fourth-update bound grows as 1/q. It
separately bounds optimization bias and centered noiseless design variance,
proves that replacing random noise propagation by mean propagation incurs
O(1/(nq)) error after multiplying by n, evaluates the resulting triangular-array
last-iterate noise constant, and carries those statements to the original rare
coefficient scale. Those are the additional uniform estimates and decompositions
verified here.

I have not independently audited the primary-source theorem statements or
determined whether existing SGD results already imply these uniform estimates,
their sufficient rarity range, or the 4/3 constant. The local mapping of
curvature, mean-square gradient Lipschitz bound, and optimum noise moment at
lines 458-460 is algebraically correct; that mapping is not a priority
comparison. The shifted schedule alone proves no novelty, and an absence of
referee findings establishes none.

Also unchecked or outside the candidate theorem: sharper necessary/sufficient
rarity ranges; a central limit theorem under triangular noise laws; estimated
centering, scales, or intercept; fixed-dataset reuse; higher-dimensional or
unbounded common blocks; minimax efficiency; tuning costs; and matched-budget
comparisons among normalization methods, step schedules, or adaptive optimizers.
A rare-coefficient MSE statement alone does not order rare-subgroup prediction
risk, which also depends on the common-coordinate error, cross moments, and the
conditional test-feature law.

The lead has preserved this report. The nonblocking infinite-stream
clarification is applied during integration; accepted task closure records the
integrated validation separately.
