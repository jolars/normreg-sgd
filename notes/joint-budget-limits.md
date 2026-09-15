# A joint observation-budget limit for the rare coefficient

## Result and scope

This note proves a joint-limit result for the last iterate of fresh-sample SGD.
With known population centering and standard-deviation scales, one common binary
feature, and rare prevalence $q_n = n^{-1/2}$, a specified decreasing learning
rate attains original-scale rare-coefficient mean squared error asymptotic to
$4\sigma^2/(3nq_n)$. Optimization bias and multiplicative update variance are
smaller. The factor $4/3$ describes this particular last-iterate schedule. It is
not an efficiency or optimality claim.

The finite-budget inequalities and proof appear below. The argument does not
substitute a growing update count into the manuscript's fixed-update limit. It
uses uniform bounds on the actual binary populations and the time-dependent
second-moment operators. Estimated preprocessing, repeated sampling from a fixed
dataset, and a central limit theorem remain outside the result. A literature
comparison is still required before interpreting this as a contribution beyond
established least-squares SGD theory.

## Experiment, assumptions, and quantifiers

For every sufficiently large integer $n$, exactly $n$ fresh observations are
available from a population indexed by $n$. Within that population, the pairs
$(W,J)$ take values in $\{0,1\}^2$, with

$$
  p_n = E W,\qquad q_n = E J = n^{-1/2},\qquad a_n = p_n(1 - p_n),
  \quad b_n = q_n(1 - q_n),\quad c_n = \operatorname{Cov}(W,J).
$$

Assume $p_n \to p \in (0,1)$ and $c_n/b_n \to \kappa$. The joint probabilities
are genuine nonnegative binary cell probabilities, not merely a proposed
covariance matrix. In particular,

$$
  \kappa_n := c_n/b_n = E(W \mid J = 1) - E(W \mid J = 0) \in[-1,1] .
$$

Fix $a_0 > 0$ and an integer $n_0$ such that, for every $n \ge n_0$,

$$
  a_n \ge a_0,\qquad 0 < q_n \le a_0/64. \tag{1}
$$

Such choices exist under the assumptions. The proof needs no rate for
$p_n \to p$ or $\kappa_n \to \kappa$. Indeed, the bounds use only (1) and
$|\kappa_n| \le 1$. A concrete feasible family fixes $r_0 \in (0,1)$ and
$r_1 \in[0,1]$, sets $P(W = 1 \mid J = j) = r_j$, and varies $q_n$. Then
$p_n = (1 - q_n)r_0 + q_n r_1$ and $\kappa_n = r_1 - r_0$ exactly. This includes
independent, positively dependent, and negatively dependent features, as well as
zero-probability joint cells at $r_1 = 0$ or $1$.

Write $x = (W - p_n,J - q_n)^\top$ and observe the centered response model

$$
  Y = \alpha + x^\top\beta^* + \varepsilon, \qquad E(\varepsilon \mid W,J) = 0,
  \qquad
  E(\varepsilon^2 \mid W,J) = \sigma^2 \in (0,\infty). \tag{2}
$$

The intercept $\alpha$ is fixed, known, and held fixed during training. The
signal $\beta^* = (\beta_C^*,\beta_R^*)^\top$ is fixed across $n$. For each
finite $M$, the inequalities below hold uniformly over $\|\beta^*\| \le M$, and
over populations and conditional noise laws satisfying the stated assumptions
with the same $a_0$ and $\sigma^2$. The observations $(W_i,J_i,\varepsilon_i)$
are iid within each experiment. No coupling between different experiments is
required. Gaussian noise or a fourth noise moment is unnecessary.

Center using the known $p_n,q_n$, use the fixed scales
$S_n = \operatorname{diag}(\sqrt{a_n},\sqrt{b_n})$, and put $z = S_n^{-1}x$.
Minimize the averaged squared loss, with the factor $1/2$. Initialize
$\theta_0 = 0$ and use the last iterate, without averaging:

$$
  \begin{aligned}
    B_n                                            & = 1,                           & k_n & = n,       & k_nB_n & = n, \\
    \tau_n                                         & = \lceil16/q_n\rceil,          &
    \eta_{n,j}                                     & = \frac{2}{\tau_n + j},        & 0   & \le j < n, \\
    \theta_{j+1}
                                                   & = \theta_j - \eta_{n,j}z_{j+1}
    \{z_{j+1}^\top\theta_j - (Y_{j+1} - \alpha)\}, &
    \beta_{n,j}                                    & = S_n^{-1}\theta_j.
  \end{aligned} \tag{3}
$$

The integer $\tau_n$ is a learning-rate offset, not a training time or penalty.
Every update consumes a different observation. All steps and the stopping count
are deterministic. Thus $n$ is both the population index and the actual
available observation budget, and all $n$ observations are used.

## Joint-budget theorem

Suppress $n$ temporarily, and let $u_j = S_n(\beta_{n,j} - \beta^*)$ and
$m_j = E u_j$. Define the standardized design and noise covariance contributions
$D_j,N_j$ by the recurrences in the proof. They are positive semidefinite and
satisfy

$$
  \operatorname{Cov}(u_j) = D_j + N_j. \tag{4}
$$

$D_j$ is the covariance remaining when the response noise is set to zero. $N_j$
contains observation noise, including its subsequent amplification by random
updates. Set $C_* = \|S_n\beta^*\|^2 \le M^2/4$. For every $n \ge n_0$ and every
integer $0 \le k \le n$,

$$
  \begin{aligned}
    |E\beta_{n,R,k} - \beta_R^*|^2
     & \le \frac{C_*}{b_n}
    \left( \frac{\tau_n}{\tau_n + k} \right)^{7/2}, \\
    0 \le \frac{(D_k)_{RR}}{b_n}
     & \le \frac{C_*}{b_n}
    \left( \frac{\tau_n}{\tau_n + k} \right)^3, \\
    0 \le \frac{(N_k)_{RR}}{b_n}
     & \le \frac{4\sigma^2}{b_n(\tau_n + k)}.
  \end{aligned} \tag{5}
$$

The second bound is deliberately conservative at $k = 0$, where $D_0 = 0$. For
the joint limit in (3),

$$
  nN_n
  \longrightarrow \frac{4\sigma^2}{3}I_2 \quad\text{in operator norm}. \tag{6}
$$

Consequently, with all coefficients reported on the original scale,

$$
  \begin{aligned}
    |E\beta_{n,R,n} - \beta_R^*|^2        & = O(n^{-5/4}),                       \\
    (D_n)_{RR}/b_n                        & = O(n^{-1}),                         \\
    (N_n)_{RR}/b_n                        & \sim \frac{4\sigma^2}{3nq_n},        \\
    nq_n\operatorname{Var}(\beta_{n,R,n}) & \longrightarrow \frac{4\sigma^2}{3}, \\
    nq_n E(\beta_{n,R,n} - \beta_R^*)^2   & \longrightarrow \frac{4\sigma^2}{3}.
  \end{aligned} \tag{7}
$$

Thus the bias is $o((nq_n)^{-1/2})$, the standard deviation due to
multiplicative updates is $o((nq_n)^{-1/2})$, and the observation-noise standard
deviation is asymptotic to $2\sigma/\sqrt{3nq_n}$. This establishes a
second-moment uncertainty scale, not a distributional limit or a confidence
interval. Markov's inequality also gives
$\beta_{n,R,n} - \beta_R^* = O_P((nq_n)^{-1/2})$.

## Proof

### 1. Uniform curvature and fourth-update bounds

For a fixed experiment, put

$$
  H = Ezz^\top
    = \begin{pmatrix}
        1    & \rho \\
        \rho & 1
      \end{pmatrix},\qquad \rho
    = \frac{c_n}{\sqrt{a_nb_n}},\qquad K
    = E[\|z\|^2zz^\top].
$$

Binary feasibility and (1) give
$|\rho| \le \sqrt{b_n/a_n} \le \sqrt{q_n/a_0} \le 1/8$. Therefore

$$
  \frac78 I \preceq H \preceq \frac98 I. \tag{8}
$$

In particular, the covariance is full rank for these experiments. Since
$a_n \le 1/4$, condition (1) implies $q_n < 1/2$. Pointwise,

$$
  z_C^2 \le 1/a_0,\qquad z_R^2 \le 1/q_n,\qquad \|z\|^2 \le \frac{65}{64q_n}.
$$

Multiplication of $zz^\top \succeq 0$ by this scalar bound and expectation show
that

$$
  K \preceq \frac{65}{64q_n}H \preceq \frac{585}{512q_n}I
    \preceq \frac2{q_n}I. \tag{9}
$$

This controls mixed fourth moments as well as the rare marginal fourth moment.
Vanishing Pearson correlation alone would not give (9).

### 2. Exact separation of the error sources

For each update, let $s_j = \tau_n + j$, $\eta_j = 2/s_j$, and define

$$
  \begin{aligned}
    R_j           & = I - \eta_jH,                               \\
    \mathcal V(U) & = E[(zz^\top - H)U(zz^\top - H)],            \\
    \mathcal T_j(U)
                  & = E[(I - \eta_jzz^\top)U(I - \eta_jzz^\top)] \\
                  & = R_jUR_j + \eta_j^2\mathcal V(U).
  \end{aligned} \tag{10}
$$

Both operators in (10) preserve positive semidefiniteness where applicable.
Independence of the next observation from the past, and conditional mean-zero
noise, imply

$$
  \begin{aligned}
    m_{j+1}                           & = R_jm_j,                                & m_0  & = -S_n\beta^*, \\
    D_{j+1}                           & = \mathcal T_j(D_j)
    +\eta_j^2\mathcal V(m_jm_j^\top), & D_0                                      & = 0, \\
    N_{j+1}                           & = \mathcal T_j(N_j) + \eta_j^2\sigma^2H, & N_0  & = 0.
  \end{aligned} \tag{11}
$$

To check the noise cross terms explicitly, conditional on all features, each
innovation $z_i\varepsilon_i$ has conditional mean zero, and distinct
innovations have zero conditional cross moments. The deterministic-in-noise
trajectory is a function of those features. It is therefore uncorrelated with
the sum of propagated noise innovations. Further,
$E[z\varepsilon^2z^\top] = \sigma^2H$ by (2). Expanding one update and
subtracting $m_{j+1}m_{j+1}^\top$ gives (11) and (4). Equivalently,
$U_j^{(0)} = m_jm_j^\top + D_j$ is the noiseless second moment and satisfies
$U_{j+1}^{(0)} = \mathcal T_j(U_j^{(0)})$.

### 3. Contraction at every update

For any positive semidefinite $U$, (8)--(10) imply

$$
  \begin{aligned}
    \operatorname{tr}\mathcal T_j(U)
     & = \operatorname{tr}\{(I - 2\eta_jH + \eta_j^2K)U\}                           \\
     & \le \left( 1 - \frac{7}{2s_j} + \frac{8}{q_ns_j^2} \right)\operatorname{tr}U \\
     & \le \left( 1 - \frac3{s_j} \right)\operatorname{tr}U,
  \end{aligned} \tag{12}
$$

because $q_ns_j \ge q_n\tau_n \ge 16$. The scalar contraction factor is positive
since $\tau_n > 3$. For integers $0 \le l \le k$, write

$$
  G_{l,k} = \prod_{j=l}^{k-1}\left( 1 - \frac3{s_j} \right).
$$

Empty products equal one. The inequality $1 - v \le e^{-v}$ and the integral
bound for a decreasing function give

$$
  G_{l,k} \le \exp\left( -3\sum_{j=l}^{k-1}\frac1{s_j} \right)
          \le \left( \frac{\tau_n + l}{\tau_n + k} \right)^3. \tag{13}
$$

Applying (12)--(13) to $U_j^{(0)}$ bounds its trace by
$C_*(\tau_n/(\tau_n + k))^3$. Since $0 \preceq D_k \preceq U_k^{(0)}$, this
proves the design-variance bound.

All eigenvalues of $R_j$ are positive, and $\|R_j\| \le 1 - 7/(4s_j)$ by (8).
The same product argument gives

$$
  \|m_k\|^2 \le C_* \left( \frac{\tau_n}{\tau_n + k} \right)^{7/2}. \tag{14}
$$

Original-scale rare squared bias is $|(m_k)_R|^2/b_n$, proving the first bound
of (5).

For $v_j = \operatorname{tr}N_j$, equations (11)--(12) and
$\operatorname{tr}H = 2$ give

$$
  v_{j+1} \le \left( 1 - \frac3{s_j} \right)v_j + \frac{8\sigma^2}{s_j^2}.
$$

The bound $v_j \le 4\sigma^2/s_j$ holds by induction, starting at $v_0 = 0$:

$$
  \left( 1 - \frac3s \right)\frac{4\sigma^2}{s}
  + \frac{8\sigma^2}{s^2} = 4\sigma^2\frac{s - 1}{s^2}
                          \le \frac{4\sigma^2}{s + 1}. \tag{15}
$$

This proves the third bound in (5).

### 4. Random updates have a smaller effect on propagated noise

Define the covariance obtained by propagating noise through the mean update
matrices:

$$
  \bar N_0 = 0,
  \qquad
  \bar N_{j+1} = R_j\bar N_jR_j + \eta_j^2\sigma^2H. \tag{16}
$$

Put $F_j = N_j - \bar N_j$. Subtracting (16) from (11) yields

$$
  F_{j+1} = R_jF_jR_j + \eta_j^2\mathcal V(N_j),\qquad F_0 = 0. \tag{17}
$$

Hence $F_j \succeq 0$. For $U \succeq 0$,

$$
  0 \le \operatorname{tr}\mathcal V(U)
    = \operatorname{tr}(KU) - \operatorname{tr}(HUH)
    \le \frac2{q_n}\operatorname{tr}U.
$$

Also $\operatorname{tr}(R_jUR_j) \le \operatorname{tr}\mathcal T_j(U)$.
Equations (12), (15), and (17) therefore give

$$
  \operatorname{tr}F_k
  \le \frac{32\sigma^2}{q_n} \sum_{j=0}^{k-1}s_j^{-3}G_{j+1,k}.
$$

Since $s_j$ are consecutive integers, the product telescopes exactly:

$$
  G_{j+1,k}
  = \frac{(s_j - 2)(s_j - 1)s_j} {(\tau_n + k - 3)(\tau_n + k - 2)(\tau_n + k - 1)}
  \le \frac{s_j^3}{(\tau_n + k - 3)^3}.
$$

This includes $j = k - 1$, when the product is empty. It follows that

$$
  0 \le \operatorname{tr}F_k
    \le \frac{32\sigma^2 k}{q_n(\tau_n + k - 3)^3}. \tag{18}
$$

At $k = n$, $nq_n \to \infty$ and $\tau_n/n \to 0$, so
$n\|F_n\| \le n\operatorname{tr}F_n \to 0$. This is a uniform error bound for
replacing random propagation of observation noise by mean propagation.

### 5. The limiting noise constant

The two eigenvalues of $H$ are $h = 1 \pm \rho$, each tending to one. All $R_j$
commute with $H$. In the corresponding orthonormal eigenbasis, $\bar N_n$ is
diagonal, with entries

$$
  v_{h,n}
  = 4\sigma^2h\sum_{j=0}^{n-1}\frac1{s_j^2} \prod_{l=j+1}^{n-1}\left( 1 - \frac{2h}{s_l} \right)^2. \tag{19}
$$

Here $h$ depends on $n$ but stays in $[7/8,9/8]$. Fix $\delta \in (0,1)$ and let
$m = \lceil\delta n\rceil$. The terms with $j < m$ are the propagation of
$\bar N_m$ through $R_m,\ldots,R_{n-1}$. By (12)--(13), (15), and
$0 \preceq \bar N_m \preceq N_m$, their total trace is at most

$$
  \frac{4\sigma^2}{\tau_n + m}G_{m,n}
  \le \frac{4\sigma^2(\tau_n + m)^2}{(\tau_n + n)^3}. \tag{20}
$$

After multiplication by $n$, the limsup is at most $4\sigma^2\delta^2$.

For the remaining terms, uniformly over $m \le j < n$ and the two values of $h$,
Taylor's formula for $\log(1 - v)$ gives

$$
  \begin{aligned}
    \log\prod_{l=j+1}^{n-1}\left( 1 - \frac{2h}{s_l} \right)^2
     & = -4h\sum_{l=j+1}^{n-1}\frac1{s_l}
    +O\left( \sum_{l=j+1}^{n-1}s_l^{-2} \right) \\
     & = 4h\log\frac{\tau_n + j + 1}{\tau_n + n}
    +O((\tau_n + j + 1)^{-1}).
  \end{aligned} \tag{21}
$$

The Taylor remainder is uniform since $2h/s_l \le 1/2$ for these experiments.
The second line follows by bounding the harmonic sum between its adjacent
integrals, whose difference is at most $1/(\tau_n + j + 1)$. Since
$\tau_n/n \to 0$ and $h \to 1$, the product in (21) converges uniformly to
$(j/n)^4$ on this interval. Therefore the late terms of $n v_{h,n}$ converge, by
an ordinary Riemann sum, to

$$
  4\sigma^2\int_\delta^1 x^2\,dx = \frac{4\sigma^2}{3}(1 - \delta^3).
$$

All early terms are nonnegative and obey (20). Taking $n \to \infty$ first at
fixed $\delta$, then $\delta \downarrow 0$, proves $n v_{h,n} \to 4\sigma^2/3$
for both eigenvalues. The common limit makes the choice of eigenvectors
irrelevant, including when $\rho = 0$. Thus $n\bar N_n \to (4\sigma^2/3)I_2$.
Equation (18) proves (6).

### 6. Original-scale comparison with the budget benchmark

For $q_n = n^{-1/2}$, $b_n \sim n^{-1/2}$ and $\tau_n \sim 16n^{1/2}$.
Substitution in (5) gives the first two rates in (7). Equation (6) gives the
third rate. The squared bias and design variance vanish after multiplication by
$nq_n = n^{1/2}$, proving the last two limits in (7). This completes the proof.

## Boundaries and order of limits

- **A broader sufficient rarity condition.** The finite-budget proof and the
  noise limit require only $q_n \to 0$, (1), and $nq_n \to \infty$. To make the
  displayed design bound negligible compared with $1/(nq_n)$, it suffices
  additionally that $n^2q_n^3 \to \infty$. Indeed, its ratio is
  $O((n^2q_n^3)^{-1})$. The squared-bias ratio is $O((n^{5/2}q_n^{7/2})^{-1})$
  and vanishes under the same condition, because
  $n^{5/2}q_n^{7/2} = (n^2q_n^3)\sqrt{nq_n}$. Thus (7), with the explicit
  polynomial bounds replaced by their $q_n$-dependent versions in (5), also
  holds for $q_n = n^{-\gamma}$ with any fixed $0 < \gamma < 2/3$. These are
  sufficient conditions from this proof. At $\gamma = 2/3$ the design bound is
  only of benchmark order, and it does not decide whether design variance is
  negligible. Failure of the bound for faster decay is not a counterexample to
  the rate.
- **Fixed stopping count versus growing budget.** Even for schedule (3), at any
  fixed prevalence, extend the same step schedule to every $j \ge 0$ using an
  infinite fresh-observation stream for this iterated-limit comparison. At any
  fixed $k$, taking $q \downarrow 0$ first makes each of the first $k$ steps
  $O(q)$ and leaves $E\beta_{R,k} \to 0$. To see this on the original scale, put
  $P = S_n^{-2}$ and $C = E xx^\top$. Then $P C$ has diagonal entries one and
  off-diagonal entries $c/a$ and $c/b$, both bounded under the assumptions. A
  fixed product of $I - \eta_j P C$ tends to the identity. Conversely, at each
  fixed feasible $q > 0$ with full rank, $k \to \infty$ makes the mean error
  tend to zero: diagonalize $H$, use $\sum_j\eta_j = \infty$, and note that
  $0 < \eta_j\lambda_{\max}(H) < 1$. For $\beta_R^* \ne 0$, these two iterated
  mean limits are different. The theorem specifies a joint path along which
  enough learning occurs.
- **Fixed nonzero steps do not survive vanishing rarity at batch size one.** In
  the scalar standardized Bernoulli model the noiseless second moment factor is
  $1 - 2\eta + \eta^2\mu_4$, where $\mu_4 \sim q^{-1}$. It exceeds one for every
  fixed $\eta > 0$ when $q$ is small enough. With noise, even the one-update
  original-scale observation-noise variance equals $\eta^2\sigma^2/b$. A
  fixed-update mean limit cannot control these second moments or justify a
  growing stopping count.
- **Degenerate parameters.** Zero rare signal, zero common signal, and
  $\kappa = 0$ are all covered. If both signals are zero, $m_j = D_j = 0$
  exactly. Negative dependence and zero-probability joint cells are permitted.
  If $\sigma^2 = 0$, (5) still holds with $N_j = 0$, but the positive-noise
  equivalence in (7) is no longer a conclusion. A common variance approaching
  zero is excluded because (8)--(9) would need different bounds. At $q = 0$, the
  specified scaling is undefined.
- **No rare observations and known preprocessing.** The event has probability
  $(1 - q_n)^n \le e^{-nq_n}$, which tends to zero here. The update is
  nevertheless defined on this event because the population scale is known and
  positive; the centered rare covariate is then $-q_n$ on every observation.
  This does not establish anything about dividing by an empirical standard
  deviation, which would be zero. The proof neither conditions away this event
  nor replaces the actual observations by expected rare counts. The case $nq_n$
  bounded is outside both the consistency conclusion and the noise-limit proof.
- **Exchanges actually justified.** The noise argument first restricts to a
  fixed positive fraction of late observations, uses a uniform Taylor bound
  there, and then removes the restriction using (20). Equation (18) justifies
  the other approximation at the growing stopping count. There is no interchange
  of an infinite update sum with a rare-population limit, no passage from a
  fixed-$k$ theorem to $k = n$, and no stationary constant-step noise-floor
  calculation.

## Remaining gaps and literature comparison

An established proof framework is [Moulines and Bach (2011), Theorem 1 and proof
recurrence
(6)](https://proceedings.neurips.cc/paper_files/paper/2011/file/40008b9a5380fcacce3976bf7c08af5b-Paper.pdf).
For the stochastic gradients here, (8)--(9) give strong convexity at least
$7/8$, a squared mean-square Lipschitz constant at most $2/q_n$, and
gradient-noise second moment $2\sigma^2$ at the optimum. A comparison of their
decreasing-step bounds with this joint regime must track the constants as
$q_n \to 0$ and account for the offset $\tau_n$ in (3). A difference between the
printed power schedule and this shifted schedule does not itself establish
novelty. The broader literature audit and exact implication check remain for the
lead's integration.

The [independent referee report](joint-budget-review.md) found no material
mathematical defect in the submitted proof. Its nonblocking infinite-stream
clarification is included above. The reproducible [joint-budget
checks](../experiments/check_joint_budget.py) independently enumerate short
original-scale trajectories and evaluate increasing budgets. This validity
evidence does not establish novelty. The following are separate open tasks:

1. Compare the exact assumptions and rates with nonasymptotic least-squares
   stochastic approximation and decreasing-step last-iterate results, including
   how their constants depend on a fourth moment growing as $1/q_n$. Compare
   averaged SGD results separately: this note does not average iterates. The
   $4/3$ noise constant is the scalar $\eta_j \approx 2/j$ propagation constant
   and is not asserted to be new.
2. Check which existing results already imply the sufficient joint rarity
   condition, or improve it to $nq_n \to \infty$ alone. The conservative bound
   on design covariance loses the coordinate-specific smallness of the initial
   rare error. No sharp necessity claim is made for $n^2q_n^3 \to \infty$.
3. Estimate centering, scales, and the intercept from data, and then handle
   random preprocessing and absent-rare samples explicitly. The present response
   uses the known centered-model intercept; this is not a joint
   intercept-fitting result.
4. Establish a distributional limit under suitable noise-tail assumptions before
   using the second-moment scale for confidence intervals. Fixed conditional
   variance alone is the only noise-tail requirement here.
5. Compare batch sizes, normalization choices, averaging, and step schedules
   using the same processed-observation budget and separate tuning. This
   one-schedule existence result does not rank those alternatives, describe
   adaptive optimizers, or analyze stopping chosen by validation data.

The existing manuscript's [finite-update
identities](../paper/sections/discrete-dynamics.tex) and [stability
bounds](../paper/sections/stochastic-gradient.tex) are the local starting
points. The continuous-time and adaptive-optimization references already in the
bibliography address related questions, but an exact theorem-level literature
comparison for this joint regime remains to be done. An absence of a checked
reference is not evidence of novelty.

## Independent checks for numerics and referee roles

Use ordinary Python, with assertions enabled, in `devenv shell` when the
environment permits it. Do not rewrite stored reference results.

For the numerics role:

1. Build the four actual binary cells from $r_0,r_1,q$, center by the population
   means, and enumerate their probabilities. Suggested cases are $r_0 = 1/2$
   with $r_1 \in \{0,1/2,1\}$. Use $\beta^* = (0.8,-0.4)$ and independent
   symmetric noise of variance $\sigma^2 = 0.09$, along with the all-zero signal
   as a diagnostic.
2. Derive the moment update directly from the four sampled gradient maps, rather
   than assuming a limiting covariance. For short paths, enumerate the feature
   and noise trajectories and compare their mean and covariance with (11). Check
   both coordinate scales and positive semidefiniteness of $D,N,N - \bar N$.
3. At budgets such as $n = 2^{18},2^{20},2^{22}$, take $q = n^{-1/2}$,
   $\tau = \lceil16/q\rceil$, and exactly $n$ updates. Verify (1) for a declared
   $a_0$, then check (5), (12), (15), and (18). Track separately $nq$ times
   squared rare bias, design variance, and observation-noise variance. The first
   two should tend to zero and the last to $4\sigma^2/3 = 0.12$. These finite
   budgets need not be in the final asymptotic range for each conservative
   bound.
4. Compare the matrix recurrence with (19) and an independently computed
   mean-propagation covariance. Confirm that the trace difference obeys (18).
   Include $\kappa = 0$ and both signs of dependence, and verify that $nN$ tends
   to a scalar matrix while $q$ changes with $n$.
5. Probe a faster rarity sequence near $q = n^{-2/3}$ as a boundary diagnostic.
   Treat finite-budget observations there as numerical evidence, not as either a
   proof or a disproof of a stronger theorem. Do not infer accuracy from mean
   error alone.

For the referee role, independently check the bound on $K$, the distinction
between covariance and second moment in (11), the product endpoints in
(18)--(21), uniformity of the late-observation approximation, and the
original-scale division by $b_n$. Also check that the claimed broader sufficient
condition follows from (5), and that the known-intercept and known-preprocessing
assumptions match the intended experiment.
