# Matched covariance and sampling schemes

This note supplies finite-support comparisons and exact sampling identities for
the framework in [discrete dynamics](../paper/sections/discrete-dynamics.tex)
and [stochastic stability](../paper/sections/stochastic-gradient.tex). All
propositions below concern fixed dimension and finite update counts unless a
limit is explicitly stated. They are supporting calculations, with no claim of
novelty. Comparisons with the closest least-squares SGD and random reshuffling
results remain necessary before positioning a manuscript claim.

## Experiment and notation

Use half the averaged squared error, known population centering, fixed positive
diagonal scales $S$, and a fixed intercept. The response is
$y = x^\top\beta^* + \varepsilon$, and $z = S^{-1}x$. Write

$$
  u_k = S(\beta_k - \beta^*),\quad H = E[zz^\top],
  \quad R = I - \eta H,\quad \mathcal M(V) = E[zz^\top Vzz^\top],
$$

$$
  \mathcal T_B(V) = RVR + \frac{\eta^2}{B}\{\mathcal M(V) - HVH\}.
$$

Here $k$ counts updates, $B \ge 1$ is an integer batch size, and $\eta > 0$ is
fixed. Original-scale means and second moments are $S^{-1}E u_k$ and
$S^{-1}E[u_ku_k^\top]S^{-1}$. Initialization is deterministic unless stated
otherwise. Fresh sampling means independent observation pairs within and across
batches. Conditional fixed-data sampling means that both features and observed
responses are held fixed and only the sampled indices vary. A sampled
observation retains its original noise on every reuse.

The population fresh-sample identities require $H \succ 0$, $E\|z\|^4 < \infty$,
$E(\varepsilon \mid z) = 0$, and $E[\varepsilon^2\|z\|^2] < \infty$, together
with independent initialization of finite second moment. These imply finite
moments at each fixed $k$ for fresh sampling. Conditional fixed-data results
below require only finite data values and finite conditional second moments of
initialization. They do not assert unconditional integrability under just the
fresh-sample assumptions.

## A binary matched-covariance family

**Proposition 1 (feasibility and differing update moments).** For every
$q \in (0,1/2]$ and $a \in[-1,1]$, let $U,V \in \{-1,1\}$ and $J \in \{0,1\}$
have cell probabilities

$$
  \Pr(U = u,V = v,J = 1) = \frac q4(1 + a uv),\qquad \Pr(U = u,V = v,J = 0)
  = \frac{1 - q}{4} \left( 1 - \frac{qa}{1 - q}uv \right).
$$

Set $W_1 = (U + 1)/2$, $W_2 = (V + 1)/2$, $b = q(1 - q)$, and

$$
  x = (W_1 - 1/2,W_2 - 1/2,J - q)^\top,
  \quad S = \operatorname{diag}(1/2,1/2,\sqrt b),
  \quad z = (U,V,Z)^\top,\quad Z = (J - q)/\sqrt b.
$$

All these distributions have the same mean $(1/2,1/2,q)$ for the binary
variables and the same centered covariance $C = \operatorname{diag}(1/4,1/4,b)$,
so $H = I_3$. In particular, each pair of binary coordinates is independent.
Nevertheless, writing

$$
  \mu = E Z^4 = \frac{(1 - q)^3 + q^3}{q(1 - q)},
  \qquad
  \delta = E[UVZ^2] = \frac{a(1 - 2q)}{1 - q},
$$

the fourth-moment operator on a symmetric matrix $V_0 = (v_{ij})$ is

$$
  \mathcal M_a(V_0) = \begin{pmatrix}
                        v_{11} + v_{22} + v_{33} & 2v_{12} + \delta v_{33}
                                                 & 2v_{13} + 2\delta v_{23}                      \\
                        2v_{12} + \delta v_{33}  & v_{11} + v_{22} + v_{33}
                                                 & 2v_{23} + 2\delta v_{13}                      \\
                        2v_{13} + 2\delta v_{23} & 2v_{23} + 2\delta v_{13}
                                                 & v_{11} + v_{22} + \mu v_{33} + 2\delta v_{12}
                      \end{pmatrix}.
$$

Thus $q < 1/2$ and $a \ne 0$ give an operator different from the $a = 0$
operator at identical covariance and identical marginal fourth moments.

*Proof.* The two conditional correlation parameters have absolute value at most
one because $q/(1 - q) \le 1$. Thus all eight displayed probabilities are
nonnegative. Summing over $u,v$ gives probabilities $q$ and $1 - q$ for $J$.
Both signs are balanced conditional on either value of $J$, and

$$
  E[UV \mid J = 1] = a,\qquad E[UV \mid J = 0] = -qa/(1 - q).
$$

It follows that $E U = E V = E UV = E UZ = E VZ = 0$. The variances of $U,V,Z$
are one. Conditioning on $J$ gives

$$
  E[UVZ^2] = q a\frac{1 - q}{q} + (1 - q)\frac{-qa}{1 - q}\frac q{1 - q}
           = \frac{a(1 - 2q)}{1 - q}.
$$

Moreover, $U^2 = V^2 = 1$, $E[UZ^3] = E[VZ^3] = 0$, and $E[UZ] = E[VZ] = 0$.
Expanding each entry of $E[zz^\top V_0zz^\top]$ using these identities proves
the matrix formula. This also verifies every fourth moment needed below. No
formal covariance feasibility assumption replaces the explicit probability
calculation. $\square$

Two binary coordinates with their means and covariance specified have all four
cell probabilities specified. A two-coordinate binary example of this kind is
therefore impossible. The extra common coordinate supplies the unspecified
higher-order dependence.

**Proposition 2 (finite-update and stability consequences).** In the noiseless
fresh-batch experiment of Proposition 1, fix $q \in (0,1/2)$ and compare
parameter $a$ against $a = 0$, using the same $B,\eta,\beta^*$ and
original-scale initial error $\beta_0 - \beta^* = (0,0,1)^\top$. Both have mean
error $(1 - \eta)^k(\beta_0 - \beta^*)$ for every $k$. After exactly two
updates, their original-scale rare-coefficient second moments differ by

$$
  E_a[(\beta_{2,R} - \beta_R^*)^2]
  - E_0[(\beta_{2,R} - \beta_R^*)^2] = \frac{2\eta^4\delta^2}{B^2}.
$$

The difference is also the difference of centered rare-coefficient variances,
since the means agree. The comparison uses $2B$ processed observations in both
experiments.

For all-initializations mean-square stability, define

$$
  \lambda_+=\frac{\mu+2+\sqrt{(\mu-2)^2+8(1+\delta^2)}}2,
  \qquad L_a=\max\{\lambda_+,2+2|\delta|\}.
$$

The exact fresh-batch stability interval is

$$
  0 < \eta < \eta_{\mathrm{crit},a},
  \qquad
  \eta_{\mathrm{crit},a} = \frac{2}{1 + (L_a - 1)/B}.
$$

For the explicit pair $q = 1/4$, $B = 1$, $a \in \{0,1\}$, the thresholds are

$$
  \eta_{\mathrm{crit},0} = \frac{12}{13 + \sqrt{73}},
  \qquad
  \eta_{\mathrm{crit},1} = \frac{12}{13 + \sqrt{105}}.
$$

The shared choice $\eta = 8/15$ is strictly inside the first interval and
strictly outside the second. Both means converge, but the second distribution
fails mean-square convergence for at least one deterministic initialization.

*Proof.* Put $U_k = E[u_ku_k^\top]$ and $r = 1 - \eta$. Fresh independence gives
$U_{k+1} = \mathcal T_{B,a}(U_k)$ and $E u_k = r^ku_0$. Since
$U_0 = b e_3e_3^\top$, the two $U_1$ matrices differ only in entries $(1,2)$ and
$(2,1)$, each by $b\eta^2\delta/B$. The $(3,3)$ formula for $\mathcal M_a$ then
gives a difference $2b\eta^4\delta^2/B^2$ in $U_2$. Dividing by $b$ proves the
original-scale assertion.

Use the Frobenius-orthonormal basis consisting of the three diagonal units and
$(E_{ij} + E_{ji})/\sqrt2$. The diagonal common contrast has eigenvalue zero for
$\mathcal M_a$. On the span of $(E_{11} + E_{22})/\sqrt2$, $E_{33}$, and
$(E_{12} + E_{21})/\sqrt2$, its matrix is

$$
  \begin{pmatrix}
    2      & \sqrt2       & 0            \\
    \sqrt2 & \mu          & \sqrt2\delta \\
    0      & \sqrt2\delta & 2
  \end{pmatrix}.
$$

This matrix has eigenvalue two and the two roots
$\{\mu + 2 \pm \sqrt{(\mu - 2)^2 + 8(1 + \delta^2)}\}/2$. The remaining two
modes have eigenvalues $2 \pm 2\delta$. Hence its largest eigenvalue is $L_a$.
Since $H = I$, the second-moment operator is

$$
  \mathcal T_{B,a} = (1 - 2\eta + \eta^2(1 - 1/B))\mathcal I
                     + \eta^2\mathcal M_a/B,
$$

where $\mathcal I$ is the identity operator.

For completeness, the spectral radius of this self-adjoint covariance map equals
its largest eigenvalue: for any symmetric $V_0$, diagonalize $V_0$ and use
$|\langle V_0,FV_0F\rangle| \le \langle |V_0|,F|V_0|F\rangle$ for each symmetric
update $F$. Averaging and maximizing Rayleigh quotients gives the assertion.
Rank-one positive semidefinite matrices span symmetric matrices, so decay from
every deterministic error is equivalent to spectral radius less than one. Its
largest eigenvalue is $1 - 2\eta + \eta^2\{1 + (L_a - 1)/B\}$, proving the
interval. At its upper endpoint it is one, so all-initializations convergence
fails there too.

At $q = 1/4$, $\mu = 7/3$ and $\delta = 2a/3$. Substitution gives the displayed
thresholds, with $L_a = \lambda_+$ in both cases. The inequalities for $8/15$
follow from $\sqrt{73} < 19/2 < \sqrt{105}$. $\square$

At $a = \pm1$ some cells have zero probability; these are valid distributions.
The two signs of $a$ change some covariance entries of the iterates but have the
same stability spectrum. At $q = 1/2$, $\delta = 0$, so this family no longer
distinguishes fourth update moments. The rare limit $q \downarrow 0$ has
$\mu \sim q^{-1}$ and bounded $\delta$, hence $L_a \sim q^{-1}$. For fixed $B$,
both thresholds are asymptotic to $2Bq$: the finite-$q$ difference is consistent
with the manuscript's leading rare-limit result. No positive fixed step is
uniformly stable as $q \downarrow 0$ at fixed $B$. The construction excludes
$q = 0$, where population standardization is undefined.

## Fixed-data sampling with replacement

Condition on a realized dataset $D = ((z_i,\varepsilon_i))_{i=1}^n$, $n \ge 1$,
centered and scaled using the prescribed population quantities, without
reestimating either from $D$. The empirical feature mean need not be zero. Set

$$
  A_i = z_i z_i^\top,\quad g_i = z_i\varepsilon_i,
  \quad H_D = \frac1n\sum_i A_i,\quad h_D = \frac1n\sum_i g_i,
  \quad Q_D = \frac1n\sum_i g_i g_i^\top,\quad R_D = I - \eta H_D,
$$

$$
  \mathcal M_D(V) = \frac1n\sum_i A_i V A_i,
  \quad \mathcal V_D(V) = \mathcal M_D(V) - H_DVH_D,
  \quad \mathcal T_{D,B}(V) = R_DVR_D + \frac{\eta^2}{B}\mathcal V_D(V),
$$

$$
  L_D(m) = \frac1n\sum_i (A_i - H_D)m(g_i - h_D)^\top.
$$

At each update draw $B$ independent uniform indices from $\{1,\ldots,n\}$,
independently across updates and from initialization conditional on $D$. Let
$\widehat H_k$ and $\xi_k$ be the corresponding averages of $A_i$ and $g_i$.
Then $u_{k+1} = (I - \eta\widehat H_k)u_k + \eta\xi_k$.

**Proposition 3 (exact conditional affine moments).** For every such finite
dataset, every integer $k \ge 0$, and every $B \ge 1$, put
$m_k = E[u_k \mid D]$, $U_k = E[u_ku_k^\top \mid D]$, and
$\Sigma_k = U_k - m_km_k^\top$. Then

$$
  m_{k+1} = R_Dm_k + \eta h_D,
  \qquad
  m_k = R_D^km_0 + \eta\sum_{j=0}^{k-1}R_D^j h_D,
$$

$$
  \begin{aligned}
    U_{k+1} = {} & \mathcal T_{D,B}(U_k)
    +\eta\{R_Dm_kh_D^\top + h_Dm_k^\top R_D\} \\
                 & -\frac{\eta^2}{B}\{L_D(m_k) + L_D(m_k)^\top\}
    +\eta^2\left\{ h_Dh_D^\top + \frac{Q_D - h_Dh_D^\top}{B} \right\}.
  \end{aligned}
$$

Equivalently, define $d_i(m) = (A_i - H_D)m - (g_i - h_D)$ and
$W_D(m) = n^{-1}\sum_i d_i(m)d_i(m)^\top$. The centered covariance satisfies

$$
  \Sigma_{k+1} = \mathcal T_{D,B}(\Sigma_k) + \frac{\eta^2}{B}W_D(m_k),
$$

$$
  \Sigma_k
  = \mathcal T_{D,B}^k(\Sigma_0)
    + \frac{\eta^2}{B}\sum_{j=0}^{k-1} \mathcal T_{D,B}^{k-1-j}\{W_D(m_j)\}.
$$

Empty sums are zero. No invertibility or stability assumption is needed for
these finite identities.

*Proof.* Conditional on $D$, the current indices are independent of $u_k$.
Independent draws inside the batch give

$$
  E[\xi_k \mid D] = h_D,
  \quad E[\xi_k\xi_k^\top \mid D] = h_Dh_D^\top + (Q_D - h_Dh_D^\top)/B,
$$

$$
  E[(I - \eta\widehat H_k)m\xi_k^\top \mid D] = R_Dmh_D^\top
                                                - \frac{\eta}{B}L_D(m).
$$

Expanding the outer product of the update proves the uncentered recurrence.
Alternatively, write $u_k = m_k + v_k$ with conditional mean-zero $v_k$. The
centered update is

$$
  u_{k+1} - m_{k+1} = (I - \eta\widehat H_k)v_k
                      - \eta\{(\widehat H_k - H_D)m_k - (\xi_k - h_D)\}.
$$

The two terms have zero cross expectation because $v_k$ is independent of the
current indices and has mean zero. The second term is an average of independent
centered $d_i(m_k)$, proving the covariance formula. Iteration proves its finite
sum and the mean formula. $\square$

In the noiseless case $g_i = 0$, Proposition 3 is exactly the fresh-sample
moment theorem applied to the empirical feature distribution. Its mean is
empirical GD. If $H_D \succ 0$, the manuscript's homogeneous mean-square
stability criterion also applies with empirical operators. If $H_D$ is singular,
a nonzero vector in its nullspace is orthogonal to every $z_i$, so its noiseless
error cannot contract. All-initializations contraction in the full coefficient
space is then impossible.

With noise, even conditionally mean-zero population errors usually produce
$h_D \ne 0$. The mean tends to $H_D^{-1}h_D$ relative to truth if $H_D \succ 0$
and $0 < \eta < 2/\lambda_{\max}(H_D)$. Recentring at this empirical
least-squares solution replaces $g_i$ by $g_i - A_iH_D^{-1}h_D$ and makes its
empirical average zero, but does not in general eliminate $L_D$. For example,
scalar $z_1 = 1,z_2 = 2$ and $\varepsilon_1 = 2,\varepsilon_2 = -1$ give
$h_D = 0$ and $L_D(m) = -3m$. These feature values may occur in a population
with known mean zero; the realized sample is not required to have empirical mean
zero. Thus a normal-equation identity alone does not justify dropping cross
terms.

## Why averaging over the training sample does not recover fresh SGD

**Counterexample 1 (persistent observation noise).** Let $n = B = 1$, let $z$ be
an equiprobable sign, and let $\varepsilon$ be independent with mean zero and
variance $\sigma^2 > 0$. Start at truth, $u_0 = 0$, and reuse the one observed
pair. For every $k \ge 0$,

$$
  u_k = \{1 - (1 - \eta)^k\}z\varepsilon,
  \qquad
  E u_k^2 = \sigma^2\{1 - (1 - \eta)^k\}^2.
$$

This follows by solving the scalar affine recursion with $A_1 = 1$. In contrast,
independent fresh observations give

$$
  E u_k^2 = \eta^2\sigma^2\sum_{j=0}^{k-1}(1 - \eta)^{2j}.
$$

At $k = 2$ the reuse value minus the fresh value is $2\eta^2(1 - \eta)\sigma^2$,
nonzero for $0 < \eta < 1$. For $0 < \eta < 2$, the respective limits as
$k \to \infty$ are $\sigma^2$ and $\eta\sigma^2/(2 - \eta)$. The reused dataset
also gives the same update for every batch size, so increasing $B$ cannot reduce
this data uncertainty. All features and noise may have finite support in this
example, for instance $\varepsilon = \pm\sigma$ equiprobably. At $\eta = 1$ the
displayed second moments coincide, which is a special case rather than an
extension theorem.

**Counterexample 2 (even the unconditional mean changes).** In a noiseless
scalar experiment with $n = 1$, $H = E z^2$, deterministic $u_0 \ne 0$, and
finite fourth moment,

$$
  E u_2 = E[(1 - \eta z^2)^2]u_0
        = \{(1 - \eta H)^2 + \eta^2\operatorname{Var}(z^2)\}u_0.
$$

Fresh sampling gives only $(1 - \eta H)^2u_0$. A standardized Bernoulli feature
of prevalence $q \ne 1/2$ has nonconstant $z^2$, so supplies a centered
finite-support example. The expectation of an empirical matrix power cannot be
replaced by the power of the population matrix.

Unconditional moments also need stronger integrability when observations are
reused. In the same noiseless $n = 1$ experiment,
$u_k^2 = (1 - \eta z^2)^{2k}u_0^2$. At $k = 2$, finite $E z^4$ with infinite
$E z^8$ gives infinite reused-data second moment, whereas the fresh-data second
moment is finite. A symmetric distribution with polynomial tail exponent
strictly between four and eight, rescaled to variance one, suffices.
Consequently, conditional finite identities cannot be averaged without checking
the relevant integrability. When it holds, the correct identities are
$E u_k = E_D m_k$ and
$\operatorname{Cov}(u_k) = E_D\Sigma_k + \operatorname{Cov}_D(m_k)$.

## Random reshuffling: exact epochs, dependent updates

**First-pass exception (unconditional law).** Suppose the original dataset
consists of $n$ independent identically distributed observation pairs, the
permutation is independent of that dataset, initialization is independent of
both, and centering and scales are fixed population quantities. Then the ordered
observations in the first reshuffled pass have exactly the joint law of $n$
fresh independent pairs, before conditioning on the dataset. Thus every
finite-update fresh-sampling identity applies unconditionally within that first
pass, including disjoint minibatches of a specified size, provided their total
observation count is at most $n$.

To prove this, condition on any particular permutation. Permuting the factors of
the product law of the original independent sample leaves the same product law.
Averaging over the independent permutation leaves it unchanged, jointly with the
independent initialization. Applying the deterministic update map to these
observations proves equality of the iterate laws. Conditioning on the realized
dataset removes this argument, and a second pass reuses observations, so the
product-law identity does not extend to repeated passes. Estimated centering,
estimated scales, or initialization fitted using the dataset also fall outside
this statement.

Keep the same finite dataset and take $B = 1$. At the start of each epoch, draw
a uniform permutation $\pi$ independently of all past permutations and
initialization, conditional on $D$. Use every observation once in that order.
Write $F_i = I - \eta A_i$ and, with the rightmost factor applied first,

$$
  P_\pi = F_{\pi(n)}\cdots F_{\pi(1)},
  \qquad
  b_\pi = \eta\sum_{j=1}^n F_{\pi(n)}\cdots F_{\pi(j+1)}g_{\pi(j)}.
$$

The product in the summand is the identity when $j = n$. An epoch processes $n$
observations and makes $n$ updates. Let $v_e = u_{en}$ denote the error at its
boundary, and let $\bar m_e,\bar U_e,\bar\Sigma_e$ be its conditional mean,
second moment, and covariance given $D$.

**Proposition 4 (epoch recurrence).** For every finite dataset and every integer
$e \ge 0$,

$$
  v_{e+1} = P_{\pi_e}v_e + b_{\pi_e},
  \qquad
  \bar m_{e+1} = E_\pi[P_\pi]\bar m_e + E_\pi[b_\pi],
$$

$$
  \begin{aligned}
    \bar U_{e+1} = {}     & E_\pi[P_\pi\bar U_eP_\pi^\top]
    +E_\pi[P_\pi\bar m_e b_\pi^\top
        +b_\pi\bar m_e^\top P_\pi^\top]
    +E_\pi[b_\pi b_\pi^\top], \\
    \bar\Sigma_{e+1} = {} & E_\pi[P_\pi\bar\Sigma_eP_\pi^\top]
    +\operatorname{Cov}_\pi(P_\pi\bar m_e + b_\pi).
  \end{aligned}
$$

All expectations over $\pi$ are finite uniform sums over the $n!$ permutations.
In the noiseless case, put $\mathcal K_D(V) = E_\pi[P_\pi V P_\pi^\top]$. Then
$\bar U_e = \mathcal K_D^e(\bar U_0)$, and decay for every deterministic initial
error at epoch boundaries is equivalent to $\rho(\mathcal K_D) < 1$ on symmetric
matrices. This criterion also gives decay at every update for this fixed
dataset.

*Proof.* Successively substitute the $n$ affine updates to obtain the displayed
$P_\pi,b_\pi$. The new permutation is independent of the error at the epoch
boundary, so expansion of its first two moments gives the formulas. Rank-one
positive semidefinite matrices span symmetric matrices; thus all-initializations
decay is equivalent to decay of powers of $\mathcal K_D$, which in finite
dimension is equivalent to spectral radius less than one. For the last
statement, the finitely many prefix products inside an epoch have a finite
maximum squared norm for fixed $D,n,\eta$. This bounds any intermediate
noiseless second moment by a constant times the preceding boundary second
moment. Conversely, full-sequence decay implies boundary decay. $\square$

Generally, $P_\pi$ is not symmetric, so the self-adjoint single-update
generalized-eigenvalue formula is not automatically an epoch formula. Nor can
the distribution of the next index inside an epoch be treated as independent of
the current iterate: both depend on the indices already used. For equal-sized
reshuffled batches with $B \mid n$, the same epoch proof applies after replacing
each $F_i,g_i$ by the averages over its ordered batch and using $n/B$ factors.
Unequal last batches require their specified averaging weights in those factors.

**Counterexample 3 (reshuffling changes mean and stability).** Use a known
population-standardized Bernoulli feature with prevalence $1/3$. Its two values
are $z = \sqrt2$ and $z = -1/\sqrt2$. Condition on a noiseless dataset of size
two containing one of each value, an event of positive probability under
independent sampling. Its empirical mean is not zero, and no sample recentering
is performed. The two scalar curvatures are $2$ and $1/2$. For any nonzero
initial error,

$$
  u_2^{\mathrm{shuffle}} = (1 - 2\eta)(1 - \eta/2)u_0,
  \qquad
  E[u_2^{\mathrm{replace}} \mid D] = (1 - 5\eta/4)^2u_0.
$$

Scalar multiplication commutes, so the first identity holds for both
permutations. Subtracting gives $-9\eta^2u_0/16$, proving failure of the
replacement mean identity after two updates. Replacement mean-square contraction
per update requires

$$
  \frac{(1 - 2\eta)^2 + (1 - \eta/2)^2}{2} < 1 \quad \Longleftrightarrow \quad 0
                                           < \eta < 20/17.
$$

Reshuffling contracts per epoch precisely when $|1 - 5\eta/2 + \eta^2| < 1$, or
$0 < \eta < 5/2$. To check the latter equivalence, the quadratic has minimum
$-9/16 > -1$ and is less than one exactly on that interval. At $\eta = 2$,
reshuffling reaches zero error in one epoch because one factor vanishes;
replacement has second-moment factor $9/2$ per update and diverges. Over the
same two-observation budget the replacement factor is $(9/2)^2$. This is a
conditional fixed-data counterexample, not a population claim that reshuffling
always improves stability or prediction. When all $A_i$ agree, the noiseless
products do agree, another boundary case.

## Limit operations and remaining checks

The finite-sum and finite-product identities require no exchange of limits. For
a fixed dataset, any asserted convergence of matrix or operator powers above
uses a strict spectral-radius bound. Extending a stationary covariance formula
to a sequence of datasets requires an appropriate uniform contraction bound and
control of its forcing terms; neither follows from finite fourth population
moments. Conditional stability need not provide a dominating integrable bound
for averaging over random datasets.

The persistent-noise example explicitly shows noncommutation even without
rarity: for reused data and $\sigma^2 > 0$,

$$
  \lim_{\eta \downarrow 0}\lim_{k \to \infty}E u_k^2 = \sigma^2,
  \qquad
  \lim_{k \to \infty}\lim_{\eta \downarrow 0}E u_k^2 = 0.
$$

The first inner limit restricts $0 < \eta < 2$. A joint limit such as
$k\eta \to T$ is a different experiment. Likewise, the fixed-$q$ stability
intervals cannot justify interchanging $q \downarrow 0$ and $k \to \infty$ at a
fixed positive step. No joint sample-size/rarity theorem, estimated scale
result, adaptive-optimizer conclusion, or optimal-stopping claim is proved here.

The numerics role should independently enumerate the eight binary cells, verify
all means and covariance entries, construct the six-dimensional Frobenius
operator, and compare its spectrum and two-update moments with Propositions 1
and 2. For Proposition 3, enumerate replacement batches and short trajectories
with nonzero $h_D$ and $L_D$, including a random initial error; check both
uncentered and centered recurrences. For Proposition 4, enumerate permutations
of a small multivariate noisy dataset so that the ordered matrix products and
affine terms are both exercised. The three scalar counterexamples provide exact
regression cases.

The referee should check the conditional versus unconditional quantifiers, the
independence used at update and epoch boundaries, the integrability
qualification for data reuse, the two-update original-scale conversion, and the
all-initializations qualification on stability. Literature comparison should
include exact least-squares moment recursions, constant-step mean-square
stability, and finite-sum random reshuffling; this note does not claim that the
formulas or constructions are absent from that literature.
