# Removing orthogonality: a two-feature investigation

Initial investigation, September 14, 2026. Adapted from the preceding `normreg`
project. References to the earlier manuscript below concern that project,
especially `paper/tex/theory.tex`, `paper/tex/additional-theory.tex`, and
`paper/tex/orthogonality-assumption.tex`. The propositions below are derivations
for this investigation, not claims of literature novelty.

The two-feature distribution theory can be developed without orthogonality.
Ridge has an immediate matrix solution; lasso and elastic net have nine affine
pieces, with exact Gaussian probabilities and moments. However, some of the
orthogonal normalization conclusions change. In particular, vanishing Pearson
correlation does not ensure that shrinkage of a common feature stops affecting
the coefficient of a rare feature.

## 1. Work on the original coefficient scale

Profile out the unpenalized intercept. Write

$$
  X_c = (I - \mathbf1\mathbf1^\top/n)X,
  \qquad
  y_c = (I - \mathbf1\mathbf1^\top/n)y,
$$

$$
  C = X_c^\top X_c/n
    = \begin{pmatrix}
        a & c \\
        c & b
      \end{pmatrix},\qquad z
    = X_c^\top y_c/n.
$$

Assume $a,b > 0$, $ab - c^2 > 0$, a fixed design, and independent Gaussian
errors with variance $\sigma_\varepsilon^2 > 0$. Then

$$
  z \sim N(\mu,\Omega),\qquad \mu = C\beta^*,
  \quad \Omega = \tau^2 C,\quad \tau^2 = \sigma_\varepsilon^2/n.
$$

Use the averaged loss, with $t = \lambda_1/n$ and $r = \lambda_2/n$, where the
lambdas refer to the manuscript's unaveraged loss. The original-scale weighted
elastic net minimizes

$$
  \tfrac12\beta^\top C\beta - z^\top\beta
  + t\sum_j u_j|\beta_j| + \tfrac r2\sum_j v_j\beta_j^2. \tag{1}
$$

Feature scaling by $s_j$ is exactly equivalent to $u_j = s_j, v_j = s_j^2$,
without any orthogonality assumption. Separate penalty weights allow other
choices, including the paper's $u_j = v_j$. Keep weights and tuning parameters
fixed with respect to the response for all distribution formulas below.
Cross-validation or a response-dependent $\lambda_{\max}$ needs separate
treatment.

Set

$$
  M = C + r\operatorname{diag}(v_1,v_2)
    = \begin{pmatrix}
        d_1 & c   \\
        c   & d_2
      \end{pmatrix},\qquad \ell_j
    = t u_j,\qquad \Delta
    = d_1d_2 - c^2
    > 0.
$$

The KKT conditions are

$$
  M\hat\beta + \ell \odot g = z,
  \qquad
  g_j = \operatorname{sign}(\hat\beta_j)\text{ if }\hat\beta_j
      \ne 0, \quad |g_j| \le 1\text{ otherwise}. \tag{2}
$$

These equations show precisely what orthogonality removed: the terms
$c\hat\beta_2$ and $c\hat\beta_1$, and correlation between the two scores.

## 2. Exact estimator and distribution for two features

For $t > 0$ and positive weights there are nine support/sign regions:

  | Support                        | Candidate estimator         | Conditions                                                  |
  | ------------------------------ | --------------------------- | ----------------------------------------------------------- |
  | Empty                          | $(0,0)$                     | $\vertz_1\vert \le \ell_1,\ \vertz_2\vert \le \ell_2$       |
  | Only 1, sign $h_1$             | $((z_1 - \ell_1h_1)/d_1,0)$ | $h_1z_1 > \ell_1,\ \vertz_2 - c\hat\beta_1\vert \le \ell_2$ |
  | Only 2, sign $h_2$             | $(0,(z_2 - \ell_2h_2)/d_2)$ | $h_2z_2 > \ell_2,\ \vertz_1 - c\hat\beta_2\vert \le \ell_1$ |
  | Both, signs $h \in \{-1,1\}^2$ | $M^{-1}(z - \ell \odot h)$  | $h_j\hat\beta_j > 0$ for both $j$                           |

In the last row,

$$
  \hat\beta_1 = \frac{d_2(z_1 - \ell_1h_1) - c(z_2 - \ell_2h_2)}{\Delta},
  \quad \hat\beta_2
  = \frac{d_1(z_2 - \ell_2h_2) - c(z_1 - \ell_1h_1)}{\Delta}. \tag{3}
$$

Each region is an intersection of linear half-planes in score space. The
conditions are necessary and sufficient by (2) and strict convexity. Apart from
boundaries of Gaussian probability zero, they partition the plane. Setting
$c = 0$ recovers the paper's independent soft-thresholding estimators.

There is an especially simple exact selection formula. Fit feature 1 alone,
$B_1(z_1) = S_{\ell_1}(z_1)/d_1$. Then

$$
  \hat\beta_2 = 0\quad \Longleftrightarrow \quad |z_2 - c B_1(z_1)|
              \le \ell_2. \tag{4}
$$

Indeed, the restricted minimizer is the full minimizer exactly when the inactive
KKT inequality for feature 2 holds. Conditional on $z_1 = x$, put

$$
  m(x) = \mu_2 + (c/a)(x - \mu_1),
  \qquad
  q(x) = c S_{\ell_1}(x)/d_1,\qquad \omega = \tau\sqrt{b - c^2/a}.
$$

Writing $f_1$ for the $N(\mu_1,\tau^2a)$ density gives

$$
  P(\hat\beta_2\ne0)=\int\_{-\infty}^{\infty} \left\[
  \Phi\!\left(\frac{m(x)-q(x)-\ell_2}{\omega}\right)
  +\Phi\!\left(\frac{q(x)-m(x)-\ell_2}{\omega}\right) \right\] f_1(x)\,dx. \tag{5}
$$

This is a one-dimensional integral, naturally split at $x = -\ell_1,\ell_1$.
Interchanging the indices gives feature 1's probability. Unlike the orthogonal
result, selection generally depends on the other feature's ridge penalty through
$d_1$. Holding all other parameters fixed, feature 2's own ridge weight does not
enter its zero/nonzero event.

Exact bias and covariance follow from the same nine regions. If the estimator on
region $R_k$ is $A_kz + b_k$, define the unnormalized moments

$$
  p_k = \int_{R_k}f(z)\,dz,\quad m_k = \int_{R_k}z f(z)\,dz,
  \quad Q_k = \int_{R_k}zz^\top f(z)\,dz.
$$

Then

$$
  E\hat\beta = \sum_k(A_km_k + b_kp_k),
$$

$$
  E\hat\beta\hat\beta^\top
  = \sum_k\{A_kQ_kA_k^\top + A_km_kb_k^\top + b_km_k^\top A_k^\top + p_kb_kb_k^\top\}. \tag{6}
$$

Subtract $\beta^*$ for bias, and subtract the outer product of the overall mean
for covariance. Gaussian integration over polygons, or one-dimensional
conditional integration of truncated Gaussian moments, evaluates these
quantities. This is an exact integral representation, rather than an assertion
that the answer reduces to a single univariate CDF.

One must retain the truncation when computing moments. Substituting
$E z = C\beta^*$ into a formula for a selected region does not give the
unconditional mean or the mean conditional on that region.

## 3. Ridge requires no orthogonality in any dimension

With $t = 0$ and $V = \operatorname{diag}(v)$,

$$
  E\hat\beta = (C + rV)^{-1}C\beta^*,
  \qquad
  \operatorname{Bias}(\hat\beta) = -r(C + rV)^{-1}V\beta^*,
$$

$$
  \operatorname{Cov}(\hat\beta) = \tau^2(C + rV)^{-1}C(C + rV)^{-1}. \tag{7}
$$

These expressions hold for arbitrary positive-definite $C$, and the mean and
covariance require only zero-mean noise with covariance $\sigma_\varepsilon^2I$.
For standard-deviation scaling, $V = \operatorname{diag}(a,b)$, write
$\rho^2 = c^2/(ab)$. Then

$$
  E\hat\beta_2
  = \frac{r(c/b)\beta_1^* + (1 + r - \rho^2)\beta_2^*} {(1 + r)^2 - \rho^2}. \tag{8}
$$

Thus standardization does not preserve the orthogonal, coordinatewise ridge
shrinkage factor on the original coefficient scale. More generally, for $r > 0$,
requiring $(C + rV)^{-1}C = kI$ with $0 < k < 1$ forces $V = (1 - k)C/(kr)$. A
diagonal $V$ can achieve this only if $C$ is diagonal. A full quadratic penalty
proportional to $C$ would achieve it, but would define a different penalty and
may be singular in high dimensions.

## 4. What survives for binary features

For two binary columns let

$$
  a = q_1(1 - q_1),\quad b = q_2(1 - q_2),\quad c = p_{11} - q_1q_2,
$$

where empirical proportions or population probabilities can be used, as
appropriate. Feasibility requires

$$
  \max(0,q_1 + q_2 - 1) \le p_{11} \le \min(q_1,q_2). \tag{9}
$$

The identities

$$
  \frac ca = E(X_2 \mid X_1 = 1) - E(X_2 \mid X_1 = 0),
  \qquad
  \frac cb = E(X_1 \mid X_2 = 1) - E(X_1 \mid X_2 = 0) \tag{10}
$$

imply $\vertc\vert \le \min(a,b)$, with strict inequality under the full-rank
assumption. Equality would force the columns to be identical or complements.

**Proposition: exact extension for a single signal.** In the noiseless
two-binary-feature lasso, take variance weights $u = (a,b)$. If
$\beta^* = (B,0)$, then for any $t \ge 0$,

$$
  \hat\beta = (S_t(B),0). \tag{11}
$$

To prove this, the active coordinate satisfies the scalar KKT condition, and the
inactive residual obeys $\vertc(B - S_t(B))\vert \le \vertc\vertt \le bt$.
Strict convexity gives uniqueness. The corresponding statement holds with the
coordinates exchanged. Thus a useful part of the variance-scaling result
survives arbitrary feasible binary correlation when only one coefficient is
nonzero. This statement is noiseless; noise can still produce false selections.

When both coefficients are active with signs $h$, the noiseless lasso gives

$$
  \hat\beta = \beta^* - t C^{-1}\operatorname{diag}(a,b)h,
$$

$$
  \hat\beta_1 = \beta_1^* - \frac{t\{h_1 - (c/a)h_2\}}{1 - \rho^2},
  \qquad
  \hat\beta_2 = \beta_2^* - \frac{t\{h_2 - (c/b)h_1\}}{1 - \rho^2}. \tag{12}
$$

These formulas require that the resulting coefficients have the stipulated
signs. They describe noiseless shrinkage, not noisy unconditional bias.

For example, choose $q_1 = 1/2,q_2 = 1/10,p_{11} = 1/10$, so that
$a = .25,b = .09,c = .05$. This is a feasible nested binary design, realizable
with integer cell counts whenever $n$ is a multiple of ten. At $t = .1$:

  | True coefficients | Orthogonal, variance-scaled lasso | Correlated, variance-scaled lasso |
  | ----------------- | --------------------------------- | --------------------------------- |
  | $(1,1)$           | $(.9,.9)$                         | $(.91,.95)$                       |
  | $(1,-1)$          | $(.9,-.9)$                        | $(.865,-.825)$                    |
  | $(1,0)$           | $(.9,0)$                          | $(.9,0)$                          |

Correlation can reduce or increase shrinkage depending on the signs. Therefore,
the stronger statement that correlation always exacerbates imbalance effects
does not hold in general.

**Proposition: no universal diagonal correction.** For $c \ne 0$, no positive
weights depending only on the design make the noiseless lasso equal
$(S_t(\beta_1^*),S_t(\beta_2^*))$ for every $\beta^*$, with fixed $t > 0$. Large
single-coordinate signals force $u = (a,b)$ by their active KKT conditions. A
sufficiently large signal $(B,B)$ would then require $C(1,1)^\top = (a,b)^\top$,
which forces $c = 0$.

If the two active signs were known, the positive weights

$$
  u_1 = a + c h_1h_2,\qquad u_2 = b + c h_1h_2 \tag{13}
$$

would instead give $\hat\beta = \beta^* - t h$ whenever
$\min_j\vert\beta_j^*\vert > t$. This is an oracle construction on a fixed
active sign region. It illustrates why a correction depends on unknown signs,
and does not supply a universally valid preprocessing rule.

A useful quantitative replacement for orthogonality is

$$
  \eta = \max(|c|/a,|c|/b).
$$

For $\eta < 1$, on a valid both-active sign region,

$$
  \|C^{-1}\operatorname{diag}(a,b)h
  - h\|_\infty \le \frac{\eta}{1 - \eta}. \tag{14}
$$

This follows by writing $C = D(I + D^{-1}(C - D))$ and applying the Neumann
series bound. Multiplying (14) by $t$ bounds the deviation from orthogonal
shrinkage. Uniformly small conditional mean differences control this error;
small Pearson correlation alone does not when the feature variances differ.

There is another simple extension if feature 1 is left unpenalized. Profiling
out its coefficient replaces the variance of feature 2 by $d = b - c^2/a$ and
its score by $z_2 - cz_1/a$, giving

$$
  \hat\beta_2 = \frac{S_{t u_2}(z_2 - cz_1/a)}{d + r v_2}.
$$

Taking $u_2 = v_2 = d$ recovers $S_t(\beta_2^*)/(1 + r)$ in the noiseless case.
This is an exact residualization result for an unpenalized nuisance feature.
When both features are penalized, residual-variance weights alone do not remove
the nuisance coefficient's shrinkage effect.

## 5. Vanishing correlation can leave a nonvanishing effect

Keep $q_1$ fixed in $(0,1)$, let $q_2 \downarrow 0$, and suppose
$c/b \to \kappa$. Binary feasibility gives $c = O(b)$, hence
$\rho = c/\sqrt{ab} \to 0$, but $\kappa$ need not be zero.

For a nested design $X_2 = 1 \Rightarrow X_1 = 1$,

$$
  c = q_2(1 - q_1),\qquad \frac cb = \frac{1 - q_1}{1 - q_2}
                                   \to 1 - q_1. \tag{15}
$$

With both coefficients positive and large enough to remain active, (12)
therefore gives the noiseless variance-scaled lasso limits

$$
  \hat\beta_1 \to \beta_1^* - t,
  \qquad
  \hat\beta_2 \to \beta_2^* - t(1 - \kappa). \tag{16}
$$

For $q_1 = 1/2$, the rare coefficient loses only $t/2$, despite $\rho \to 0$.
The result differs from the orthogonal loss of $t$. This can be realized as a
sequence of actual binary designs with $n \to \infty$ and fixed
$t = \lambda_1/n$. It also holds in probability with fixed Gaussian error
variance if $nq_2 \to \infty$, $\beta_1^*,\beta_2^* > t$, and variance-scaled
lasso: the coefficient noise vanishes at rate $(nq_2)^{-1/2}$, and the limiting
positive coefficients ensure the active-sign conditions hold with probability
tending to one.

The ridge example is equally direct. From (8), with fixed $r > 0$,

$$
  E\hat\beta_2 \to \frac{\beta_2^*}{1 + r}
                   + \frac{r\kappa\beta_1^*}{(1 + r)^2}. \tag{17}
$$

Taking $q_1 = 1/2,r = 1,\beta_1^* = \beta_2^* = 1$ gives $5/8$, compared with
the orthogonal value $1/2$. This result also holds along actual binary design
sequences with fixed $r = \lambda_2/n$, because the ridge mean does not depend
on the noise level.

There is a noisy analogue of (16), addressing the manuscript's formal
fixed-noise imbalance limits. In the continuous Gram-matrix experiment, hold
$a,t,\tau > 0$, $r \ge 0$, and $\beta^*$ fixed, let $b \downarrow 0$, and assume
$c/b \to \kappa$. Use feature scales $s_1 = a^\delta,s_2 = b^\delta$, with
$\delta \ge 1/2$. Define

$$
  B_1 = \frac{S_{t a^\delta}(a\beta_1^* + \xi_1)} {a + r a^{2\delta}},
  \qquad
  \xi_1 \sim N(0,\tau^2a), \quad L = \beta_2^* + \kappa(\beta_1^* - E B_1).
$$

Then

$$

\lim E\hat\beta_2= \begin{cases}
\displaystyle\frac{2\Phi(-t/\tau)}{1+r}L,&\delta=1/2,\\\[4pt\] L,&\delta>1/2.
\end{cases} \tag{18} $$

Thus the orthogonal asymptotic unbiasedness assertion for $\delta > 1/2$
generally becomes a limit containing the other coefficient's shrinkage bias.
Meanwhile,

$$
  P(\hat\beta_2 \ne 0) \to \begin{cases}
                             2\Phi(-t/\tau), & \delta = 1/2, \\
                             1,              & \delta > 1/2,
                           \end{cases}
$$

and

$$
  b\operatorname{Var}(\hat\beta_2) \to \begin{cases}
                                         \operatorname{Var}(S_t(\tau Z))/(1 + r)^2, & \delta = 1/2, \\
                                         \tau^2,                                    & \delta > 1/2,
                                       \end{cases} \qquad Z
                                   \sim N(0,1). \tag{19}
$$

The selection and variance conclusions in this regime therefore survive, while
the mean can change.

**Proof of (18)--(19).** Couple the Gaussian score errors by

$$
  \xi_2 = (c/a)\xi_1 + \tau\sqrt{b - c^2/a}\,Z, \qquad Z \perp \xi_1.
$$

The coordinate KKT equations and the 1-Lipschitz property of soft-thresholding
give $\Vert\hat\beta_2\Vert_2 = O(b^{-1/2})$ and
$\Vert\hat\beta_1 - B_1\Vert_2 = O(\sqrt b)$. For the first bound, substitute
the coordinate bound for $\hat\beta_1$ into that for $\hat\beta_2$, and use
$d_2 - c^2/d_1 \asymp b$. Replacing $\hat\beta_1$ by $B_1$ in coordinate 2
consequently changes its estimate by $O_{L^2}(\sqrt b)$. The resulting numerator
is soft-thresholding applied to

$$
  \tau\sqrt{b - c^2/a}\,Z + bU_b,
  \qquad
  U_b = \beta_2^* + (c/b)(\beta_1^* - B_1 + \xi_1/a).
$$

The family $U_b$ is bounded in $L^2$, with $E U_b \to L$. For a Gaussian
variable, the derivative of its soft-thresholded mean with respect to its
location is its probability of exceeding the threshold in absolute value. The
threshold-to-noise ratio here tends to $t/\tau$ when $\delta = 1/2$, and to zero
when $\delta > 1/2$. Integrating this derivative from location zero to $bU_b$,
then using dominated convergence, gives (18), after dividing by
$b + r b^{2\delta}$.

Likewise, $\sqrt b\hat\beta_2$ converges in $L^2$ to $S_t(\tau Z)/(1 + r)$ or
$\tau Z$, respectively. These limiting variables have mean zero, giving (19).
For selection use the exact restricted-fit identity (4), whose standardized
residual has the same limiting Gaussian distribution; the limiting threshold
boundaries have probability zero.

For empirical binary features, a fixed $n$ only allows proportions on the grid
$\{0,1/n,\ldots,1\}$. Consequently, (18)--(19), like a continuous fixed-$n$
imbalance limit, should be labeled a Gram-matrix limit. A statistical asymptotic
theorem for actual data must specify $n \to \infty$, the rare count $nq_2$, and
the rates of both penalties. The finite-design examples and the ridge/noiseless
sequences above do not rely on this formal interpretation. Limits for
$q_2 \uparrow 1$ follow by complementing the binary column and changing its
coefficient's sign.

## 6. A focused follow-up

A useful first paper could establish the exact two-feature probabilities and
moments, then distinguish three questions: preservation of single-signal
shrinkage, interaction between signs and shrinkage when both signals are
present, and the conditions under which rare-feature limits agree with their
orthogonal counterparts. Equations (11), (14), and (18) supply positive results,
an approximation bound, and a corrected limiting statement.

The original appendix's correlation arguments should not be treated as a proof
of estimator equivalence. Correlation going to zero must be combined with
control of covariance divided by the shrinking feature variance. Also, if both
binary features become rare together, their correlation need not vanish. For
binary/continuous pairs, the point-biserial correlation identity alone does not
impose a uniform bound on changing conditional means; additional distributional
assumptions are needed for such a limit.

For simulations, vary $(q_1,q_2,p_{11})$ within (9), and include same-sign,
opposite-sign, and single-signal configurations. Fixed cell counts isolate the
conditional-on-design theory. Hold noise and $t,r$ fixed for direct comparisons,
then study tuning rules separately. The existing orthogonality experiment uses a
response-dependent $\lambda_{\max}/2$ and changes noise to keep SNR fixed, so it
addresses a different comparison from fixed-parameter formulas (5)--(6).

General finite-sample lasso distribution theory already exists for correlated
designs and coordinate-specific penalty weights: see [Ewald and Schneider
(2020)](https://arxiv.org/html/1708.09608v3). Polyhedral selection events also
underpin [Lee, Sun, Sun, and Taylor (2016)](https://arxiv.org/html/1311.6238v8).
The potential contribution here is therefore the binary normalization theory and
its corrected conclusions, rather than the existence of a correlated lasso
distribution. This was a targeted literature check, not a novelty review of
every result in this note.

The companion numerical check is
[`check_two_features.py`](../experiments/check_two_features.py), with results in
[`two-feature-check.json`](../results/two-feature-check.json). Across six
configurations and 1.2 million Gaussian draws, the nine-region solver agreed
with independent coordinate descent to within $8.61 \times 10^{-13}$. Selection
probabilities from (5) and from the region integrals agreed to within
$3.34 \times 10^{-16}$. Integrated probabilities, means, and covariances agreed
with Monte Carlo within six standard errors. These checks cover the
finite-design formulas; the limit statements above are supported by their
derivations.

## 7. A boundary correction in the existing weighted-elastic-net theorem

Before extending the manuscript's weighted-elastic-net variance theorem, its
$\omega = 1/2$ boundary should be corrected. This is already an issue in the
orthogonal case and is separate from the correlation analysis above. With
feature variance $b$, weights $u = v = \sqrt b$, and $t,r,\tau > 0$, the
orthogonal estimator is exactly

$$
  \hat\beta=
  \frac{S_{t\sqrt b}(b\beta^*+\tau\sqrt b Z)}{b+r\sqrt b}
  =\frac{S_t(\sqrt b\beta^*+\tau Z)}{\sqrt b+r}
  \xrightarrow{L^2}\frac{S_t(\tau Z)}r.
$$

Its variance therefore tends to a finite positive constant,

$$
  \frac{\operatorname{Var}(S_t(\tau Z))}{r^2}
  = \frac{2\tau^2}{r^2} \left[ \{1 + (t/\tau)^2\}\Phi(-t/\tau) - (t/\tau)\phi(t/\tau) \right],
$$

not infinity as currently stated in `thm:weighted-elasticnet-bias-variance`. The
other two regimes remain zero for $\omega < 1/2$ and infinity for
$\omega > 1/2$, under that theorem's positive-penalty and positive-noise
assumptions. No manuscript changes have been made as part of this investigation.
