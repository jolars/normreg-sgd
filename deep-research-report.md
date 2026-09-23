# Novelty assessment of “Normalization and Implicit Regularization in Stochastic Learning”

This is the September 15, 2026 planning assessment, with citations repaired on
September 23. Its proposed directions and novelty ratings are historical
judgments, not the current paper's claims. The [contribution
decision](notes/predictive-contribution.md) and [bounded source
comparison](notes/predictive-source-comparison.md) supersede its positioning
advice. The [citation resolution record](notes/research-report-citations.md)
identifies the sources, corrections, and material excluded from the manuscript.
The original browsing log is unavailable; the links below supply checked support
for the surrounding statements rather than recover the opaque search
identifiers.

## Overall assessment

**Yes, the research plan plausibly contains a novel research contribution, but
the novelty is not in the broad idea that normalization, learning rate, batch
size, and early stopping affect SGD.** Each of those components, and several
pairwise interactions among them, already have substantial literatures. Early
stopping in least squares has explicit regularization interpretations;
stochastic-gradient dynamics and risk trajectories in least squares are well
studied; mini-batch size and learning rate have known equivalences and
trade-offs; feature frequency has long motivated coordinate-adaptive
optimization; and, most importantly, **preconditioned SGD for least squares has
now been studied explicitly as a source of implicit regularization** ([Ali,
Kolter, and Tibshirani][ali2019]; [Zou et al.][zou2021]; [Jain et
al.][jain2018]; [Meterez et al.][meterez2026]; [Su, Zou, and Wu][su2024]).

What does appear much less occupied—and, in the literature I found, is not
treated as a unified problem—is the following combination:

> **Treat a conventional feature-normalization rule as a fixed diagonal
> preconditioner whose entries depend on feature prevalence, and characterize
> how that preconditioner interacts with learning rate, batch composition,
> stopping time, and dependence between common and rare features to determine
> finite-time coefficient bias, stochastic variance, and aggregate versus
> rare-subgroup prediction risk.**

That is substantially more specific than “normalization affects SGD.” I did
**not** find a paper that combines all of the following in the way your plan
proposes:

$$
  \text{prevalence-dependent feature scaling} \times \text{learning rate}
  \times \text{batch size} \times \text{stopping} \times \text{feature
  dependence},
$$

while retaining **original-scale coefficient trajectories and stochastic
moments** and explicitly comparing **overall and rare-subgroup statistical
risk** under several matched resource notions.

My assessment as of **September 15, 2026** is therefore:

  | Level of claim                                                                                                                                   | Novelty assessment                                                                              |
  | ------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
  | “Feature scaling changes SGD dynamics.”                                                                                                          | **Not novel**                                                                                   |
  | “Early stopping implicitly regularizes least squares.”                                                                                           | **Not novel**                                                                                   |
  | “Learning rate and batch size jointly determine stochastic SGD behavior.”                                                                        | **Not novel**                                                                                   |
  | “Rare/sparse features interact with optimization frequency.”                                                                                     | **Not novel**                                                                                   |
  | “Preconditioning can change SGD's implicit regularization in least squares.”                                                                     | **Not novel; particularly close prior work exists**                                             |
  | “For common/rare binary predictors, normalization changes finite-time learning rates differently according to prevalence.”                       | **Likely elementary/derivable rather than sufficient novelty by itself**                        |
  | “Normalization, batch rarity, stopping, and feature dependence jointly induce quantitatively characterizable coefficient/risk trade-offs.”       | **Plausibly novel**                                                                             |
  | “Their interaction can produce provable normalization-ranking reversals or aggregate-versus-rare-subgroup risk reversals under matched budgets.” | **Potentially strong novelty if proved**                                                        |
  | “A complete theory over the whole four-dimensional configuration space.”                                                                         | **Novel-sounding, but too broad to be a credible contribution claim without a sharper theorem** |

I would therefore describe the project as **high-potential but not yet
novelty-secure**. The plan identifies an apparently underexplored intersection.
What will determine publishable novelty is not the intersection itself but the
**comparative theorem or phenomenon you establish inside it**.

## What the existing literature already covers

The important issue is that several sentences that could easily become headline
claims for this project would already be too broad. The surrounding literature
has advanced considerably, including quite recently.

### Normalization and explicit regularization are already your established starting point

Larsson and Wallin's *The Choice of Normalization Influences Shrinkage in
Regularized Regression* directly studies how feature normalization changes
lasso, ridge, and elastic-net fitting. In particular, it treats binary-feature
prevalence, shows normalization-specific effects on coefficient shrinkage,
considers mixed feature types and interactions, and explicitly proposes
normalization as something that can be tuned ([Larsson and
Wallin][larsson2025]).

That makes the conceptual continuity in your proposed paper attractive, but it
also means that the follow-up cannot reasonably claim as new:

- that normalization affects statistical shrinkage;
- that binary prevalence makes normalization consequential;
- that different normalization exponents can be compared statistically; or
- that normalization itself might be tuned.

The new object has to be **training-induced finite-time/stochastic
regularization rather than explicit-penalty regularization**.

There is a particularly clean reason that this transition is natural. From your
own update,

$$
  \beta_{t+1}
  =
  \beta_t+ \frac{\eta_t}{B}S^{-2} \sum_{i\in\mathcal B_t}
  x_i(y_i-x_i^\top\beta_t),
$$

normalization is literally a choice of **fixed diagonal preconditioner**
$P=S^{-2}$ when expressed on the original coefficient scale. That gives you a
useful bridge to the optimization literature—but it also puts you directly next
to the preconditioned-SGD literature.

### Preconditioned SGD is the most important novelty threat

Su, Zou, and Wu's *Improving Implicit Regularization of SGD with Preconditioning
for Least Square Problems* is probably the paper that should most strongly
affect your positioning. It studies least-squares SGD with an arbitrary
preconditioning matrix, derives excess-risk bounds, compares preconditioned SGD
with standard and preconditioned ridge regression, and constructs
preconditioners that improve SGD's statistical behavior ([Su, Zou, and
Wu][su2024]).

This means that a claim such as

> “We show that feature normalization changes the implicit regularization of SGD
> because normalization changes the optimization geometry”

would now be much too weak. In mathematical terms, feature normalization is a
special diagonal preconditioner, and the broad proposition that preconditioning
can change the generalization/regularization properties of least-squares SGD is
already explicit in that work ([Su, Zou, and Wu][su2024]).

There is also newer work analyzing preconditioned SGD through the simultaneous
effects of geometry on conditioning and stochastic noise floors, including
diagonal preconditioners. That reinforces the point that “preconditioning
changes the rate/noise trade-off” is not itself an open conceptual claim ([Scott
et al.][scott2026]).

Your differentiation from this literature is potentially strong, however. Your
$P$ is not designed abstractly to optimize a bound or condition number. It is
generated by **actual preprocessing conventions**, with entries tied to **binary
prevalence**, and you want to know how those conventions act jointly with
batches and finite stopping on **specific coordinates and subpopulations**. That
is a statistical question that is considerably more structured than “find a
better preconditioner.”

### Early stopping in least squares is already a mature regularization topic

Ali, Kolter, and Tibshirani studied the complete gradient-flow trajectory for
least squares and its relationship with ridge regularization, including risk
comparisons along the early-stopping path ([Ali, Kolter, and
Tibshirani][ali2019]). Ali, Dobriban, and Tibshirani subsequently studied the
implicit regularization of **stochastic gradient flow** for least squares,
making learning rate, mini-batching, number of iterations, and excess risk part
of the analysis ([Ali, Dobriban, and Tibshirani][ali2020]).

The discrete problem has also moved forward. The July 2026 revision of
Sonthalia, Lok, and Rebrova studies discrete full-batch gradient descent in
linear least squares. Its abstract describes parameter trajectories and expected
excess risk for learning-rate schedules, and a connection with generalized ridge
solutions ([Sonthalia, Lok, and Rebrova][sonthalia2026]).

Jahn, Pillaud-Vivien, and Schertzer's paper, posted on **September 10, 2026**,
studies discrepancy-based stopping for a continuous-time SGD model in linear
inverse problems. Its abstract reports a high-probability minimax rate up to a
logarithmic factor under source and spectral conditions, despite persistent
stochastic fluctuations ([Jahn, Pillaud-Vivien, and Schertzer][jahn2026]).

Consequently, neither of these would be strong novelty claims:

> “Stopping time acts as an implicit regularizer in linear regression.”

or

> “One should study the entire trajectory rather than only convergence.”

Those are established viewpoints. Your possible novelty is instead that
**changing normalization changes which coordinates are early and late along that
trajectory, in a prevalence- and dependence-dependent way, and simultaneously
changes the stochastic variance accumulated before stopping**.

That distinction is important.

### Learning rate and batch size already have a large joint literature

For least squares specifically, Jain et al. gave sharp results for
mini-batching, averaging, and statistical error, including how the usefulness of
larger mini-batches depends on the problem ([Jain et al.][jain2018]). More
generally, the observation that learning rate and batch size can compensate for
one another is longstanding: Smith et al. showed empirically that increasing
batch size can replace learning-rate decay in several training settings and
proposed proportional learning-rate/batch-size scaling ([Smith et al.,
2018][smith2018]).

Meterez et al.'s *Seesaw* paper, first posted in 2025, compares geometric
learning-rate and batch-size schedules for noisy Gaussian linear regression. The
inspected 2026 revision gives phase-end risk comparisons up to constants under
matched observation budgets and a bounded-risk assumption. This is not an
identity of trajectories or a result about feature normalization ([Meterez et
al.][meterez2026]).

There is also a distinct line of work interpreting the SGD regularizer induced
by finite learning rates in terms of the learning-rate-to-batch-size ratio;
Smith et al. derive such a modified-loss effect for random-shuffling SGD under
their regime ([Smith et al., 2021][smith2021]).

Thus your Questions 1–3 should not be positioned as discovering that $\eta$,
$B$, and $k$ interact. The potentially new part is:

$$
  \boxed{ \text{How does a prevalence-structured }P=S^{-2} \text{ alter those
  known }(\eta,B,k)\text{ interactions?} }
$$

and, especially, whether no scalar adjustment of $\eta$ or $B$ can reproduce
what changing **relative coordinate scaling** does.

### SGD implicit regularization in least squares is also established

Zou et al. explicitly study the “implicit regularization” of unregularized SGD
in linear least squares, in both under- and overparameterized regimes, and
compare optimally tuned SGD statistically with ridge regression ([Zou et
al.][zou2021]). This is one reason your plan is right to keep full-rank
convergence to OLS, finite-time regularization, and minimum-norm/interpolating
implicit bias conceptually separate.

That separation should remain prominent. In the full-rank setting your
normalization-dependent fitted model at finite time is primarily a statement
about **transient optimization bias plus stochastic variation**. Calling every
such difference “implicit regularization” without qualification risks making the
work look less precise than it actually is.

Exact second-moment operators for least-squares SGD already appear in [Défossez
and Bach][defossez2015] and [Jain et al.][jain2018]. Deriving a closed recursion
is therefore useful machinery, but its existence alone does not establish
novelty. These checked sources replace the original report's unidentified
citations to high-dimensional trajectory analyses.

### Rare features and feature-frequency-dependent optimization are not new either

The general optimization difficulty caused by sparse or infrequently occurring
coordinates is longstanding. Frequency-adaptive online methods were developed
specifically to alter learning rates according to feature occurrence; adaptive
methods such as AdaGrad became attractive in sparse settings for closely related
reasons. AdaBatch is particularly relevant because it modifies mini-batch
aggregation for sparse problems and interprets the result as implicit coordinate
rescaling ([Défossez and Bach][adabatch2017]).

Zou et al. also analyze an uncentered one-hot design in their SGD-versus-ridge
comparison. [Zou et al.][zou2021] The original report's separate attribution to
stochastic reweighting could not be verified and is withdrawn. And a 2026 study
of stochastic momentum with sparse updates explicitly analyzes what happens to
optimization dynamics when feature updates arrive rarely ([Everett and
Paquette][everett2026]).

So neither

> “Rare features receive gradients infrequently”

nor

> “Rare features can benefit from different effective learning rates”

is a novel thesis.

What I did **not** find in this literature is your more specific question: what
happens when the effective coordinate learning rate comes not from an adaptive
optimizer but from a **standard preprocessing choice such as no scaling, SD
scaling, variance scaling, or damped scaling**, and when one then follows the
statistical cost of that choice all the way through observation noise, batch
composition, stopping, dependence, and subgroup prediction.

That is a considerably narrower and more defensible gap.

## Where the plan looks genuinely distinctive

The strongest aspect of the plan is not any one of its four training choices. It
is the **structured statistical experiment created by putting them together
without optimizing them away**.

### Prevalence converts normalization into an analytically transparent learning-rate allocation

Your binary model gives a particularly clean mechanism. Suppose first that the
centered coordinates are independent and

$$
  v_j=q_j(1-q_j), \qquad s_j=v_j^\delta.
$$

Then

$$
  P_{jj}=v_j^{-2\delta}, \qquad (PC)_{jj}=v_j^{1-2\delta}.
$$

Hence population gradient flow satisfies coordinatewise

$$
  \dot e_j(T)
  =
  -v_j^{1-2\delta} e_j(T),
$$

where $e_j=\beta_j-\beta_j^*$. Thus the deterministic learning time scale is
proportional to

$$
  v_j^{\,2\delta-1}.
$$

For a rare binary coordinate, $v_R\simeq q$, so the three headline
normalizations yield

$$
  \begin{array}{c|c} \delta & \text{rare-coordinate flow rate}\\ \hline 0 &
  q\\ 1/2 & 1\\ 1 & 1/q. \end{array}
$$

That is a striking mechanism: no scaling makes the rare signal intrinsically
slow in flow time, SD scaling equalizes this diagonal population rate, and
variance scaling makes the rare coordinate intrinsically fast.

But **this calculation itself is probably too elementary to be the main
theorem**. Its real value is that it creates a transparent baseline against
which the stochastic cost can be studied. Variance scaling may accelerate the
rare mean trajectory while simultaneously magnifying its individual stochastic
updates. That potential rate-versus-noise conflict is where the more interesting
statistics begin.

Your plan is unusually well structured for isolating exactly that transition.

### The global-scale control sharply distinguishes trivial from substantive normalization effects

One of the best pieces of the plan is the proposed global scaling control. It
should probably appear very early in the eventual paper.

If every divisor is multiplied by $c>0$,

$$
  S' = cS,
$$

then

$$
  P'=(S')^{-2}=c^{-2}P.
$$

Therefore choosing

$$
  \eta'_t=c^2\eta_t
$$

gives

$$
  \eta'_tP'=\eta_tP.
$$

With the same initialization and same sampled batches, the **entire
original-scale discrete trajectory is identical pathwise**.

This equivalence is algebraic, not a novel result. But that is precisely why it
is a good control: it allows you to state cleanly that the scientific object is
**relative feature normalization**, not “normalization” in the sense of a
meaningless overall change of units.

For two coordinates,

$$
  \frac{P_{RR}}{P_{CC}}
  =
  \left(\frac{v_R}{v_C}\right)^{-2\delta},
$$

and a single global learning rate cannot remove a change in that ratio. This
makes the distinction between

$$
  \text{global rescaling} \quad\text{and}\quad \text{relative preconditioning}
$$

mathematically exact.

That is more compelling than simply reporting that different standardized
datasets need different learning rates.

### The $Bq$ question can become novel if you establish what it does *not* explain

The quantity $Bq$ is a natural first-order measure of how many rare occurrences
appear in a mini-batch. Its basic significance is not novel: sparse-data
optimization already recognizes that batching behaves differently for
infrequently active coordinates, and methods such as AdaBatch were motivated in
part by this structure ([Défossez and Bach][adabatch2017]).

A stronger result would be something like:

$$
  Bq \text{ controls one component of rare-gradient fluctuation,}
$$

**but two distributions with identical $Bq$, identical covariance, or even
identical marginal prevalences can nevertheless exhibit different finite-time
coefficient covariance because of joint feature occurrence or data reuse.**

That would move beyond a familiar sparsity heuristic and give a genuine
statistical characterization.

Your independent/nested/negatively-associated binary constructions are therefore
more important for novelty than they might initially appear. They allow you to
separate:

$$
  \text{marginal rarity} \quad\text{from}\quad \text{joint batch composition}.
$$

A theorem or counterexample proving that $Bq$ is insufficient—while
characterizing the additional joint-law quantity that is needed—could be a clean
contribution.

### Dependence may be the most underexploited part of the proposal

The independent case makes the normalization mechanism transparent, but it is
probably not where the strongest paper lies.

When $C$ has off-diagonal entries,

$$
  \dot e=-PCe,
$$

and scaling changes both the coordinate-specific rates and the way errors in one
coordinate feed into the evolution of another. Although this is still linear
algebra, it gives you a mechanism that much of the preconditioned-SGD literature
does not formulate in terms of **statistically meaningful common/rare binary
variables and their feasible joint distributions**. Existing preconditioning
work generally seeks global risk guarantees or improved optimization/statistical
conditioning rather than asking how incomplete learning of one interpretable
feature contaminates another feature's coefficient ([Su, Zou, and Wu][su2024];
[Scott et al.][scott2026]).

This could generate a genuinely interesting result of the form:

> A normalization that is optimal for a rare coordinate under independence
> ceases to be optimal when that coordinate is associated with a common
> coordinate, because early stopping transmits residual common-feature error
> into the rare coefficient.

Even better would be an explicit sign or threshold condition in terms of
$q_R,q_C,\operatorname{Cov}(X_R,X_C),\delta,\eta,B,k$.

That would be much harder to dismiss as a restatement of generic preconditioning
theory.

### Aggregate versus rare-subgroup risk is particularly promising

The proposed pair

$$
  R=\frac12\operatorname{tr}(CV), \qquad R_R=\frac12\operatorname{tr}(C_RV)
$$

adds something important.

Most of the nearby least-squares SGD literature evaluates global excess
prediction risk. For example, both the SGD-versus-ridge work and
preconditioned-SGD work are framed around aggregate generalization/excess risk
rather than the consequences for a test subpopulation defined by the presence of
a rare predictor ([Zou et al.][zou2021]; [Su, Zou, and Wu][su2024]).

Your conditional risk is not merely the same risk on fewer observations, because

$$
  C_R=E[xx^\top\mid J=1]
$$

contains both altered second moments and a generally nonzero conditional mean.
Feature dependence can therefore make a coefficient error that contributes
little to aggregate risk particularly important among rare-feature observations.

A result such as

$$
  R(\delta_1)<R(\delta_2) \qquad\text{while}\qquad R_R(\delta_1)>R_R(\delta_2)
$$

over a nondegenerate parameter region would be scientifically meaningful. If you
could characterize **when** such reversals occur and link them to the
optimization trajectory, that would be considerably stronger than merely
observing subgroup-performance differences in a simulation.

I regard this as one of the highest-novelty directions in the plan.

### Your resource accounting is unusually careful, although not itself novel

Separating

- equal update count $k$,
- equal processed observations $M=kB$,
- equal cumulative step $\sum_t\eta_t$,
- identical datasets/noise,
- fresh versus reused observations,

is excellent design.

The need for this distinction is reinforced by existing work on mini-batching
and by more recent linear-regression work examining one-pass versus
repeated-data training ([Jain et al.][jain2018]; [Chen, Zhou, and
Zhou][chen2026]; [Lin, Wu, and Bartlett][lin2025]). Recent
learning-rate/batch-size equivalence results also show why an apparent
improvement can disappear after the appropriate computational calibration
([Meterez et al.][meterez2026]).

So the accounting framework is not, by itself, a novelty claim. Its value is
defensive: it makes a normalization-ranking reversal much more convincing if the
reversal survives the relevant budget comparison—or scientifically informative
if it does not.

## Novelty risk by proposed contribution

A useful way to assess the project is to ask what a skeptical reviewer could
cite against each possible headline result.

  | Candidate contribution from the plan                                                                               | Prior-art pressure                                                                 | My assessment                                                                                       |
  | ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
  | Normalization changes GD/SGD convergence rates                                                                     | Classical optimization/preconditioning; feature scaling is standard                | **Very low novelty**                                                                                |
  | Global feature scaling is equivalent to adjusting $\eta$                                                           | Direct algebra                                                                     | **Control result only**                                                                             |
  | Relative normalization gives different learning rates to common and rare binary coordinates                        | Follows directly from $PC$; frequency-sensitive learning is long known             | **Low alone; useful mechanism**                                                                     |
  | Early stopping regularizes least squares                                                                           | Extensive gradient-flow/GD literature                                              | **Not novel** [Ali, Kolter, and Tibshirani][ali2019]; [Sonthalia, Lok, and Rebrova][sonthalia2026]. |
  | SGD provides implicit regularization in least squares                                                              | Extensive literature                                                               | **Not novel** [Zou et al.][zou2021].                                                                |
  | Preconditioning changes SGD's implicit regularization                                                              | Direct recent prior work                                                           | **Not novel** [Su, Zou, and Wu][su2024].                                                            |
  | Batch size and learning rate trade off                                                                             | Extensive literature, including recent finite-sample linear-regression equivalence | **Not novel** [Meterez et al.][meterez2026]; [Smith et al., 2018][smith2018].                       |
  | Rare features require frequency-aware optimization                                                                 | Sparse/adaptive optimization literature                                            | **Not novel** [Défossez and Bach][adabatch2017]; [Duchi, Hazan, and Singer][duchi2011].             |
  | $Bq$ determines rare-feature SGD variability                                                                       | Related intuitions already exist                                                   | **Moderate at best unless made exact and delimited**                                                |
  | $Bq$ is insufficient under dependence; identify the missing quantity                                               | I found no close treatment in your normalization setting                           | **Potentially strong**                                                                              |
  | Exact finite-time moments under a diagonal preconditioner                                                          | Quadratic-SGD dynamics are heavily studied                                         | **Moderate as machinery; weak as headline**                                                         |
  | Normalize-by-prevalence $\times B\times\eta\times k$ risk phase diagram                                            | No close match found                                                               | **Moderate-to-high if analytically characterized**                                                  |
  | Provable reversal between normalization rules as stopping/batch regime changes                                     | No close match found                                                               | **High potential**                                                                                  |
  | Dependence causes incomplete learning of one feature to distort another differently under different normalizations | No close match found in this statistical formulation                               | **High potential**                                                                                  |
  | Aggregate-optimal normalization differs from rare-subgroup-optimal normalization for a characterized regime        | No close match found                                                               | **High potential**                                                                                  |
  | Joint hyperparameter tuning of normalization, LR, batch, and stopping improves test performance                    | Hyperparameter tuning is generic; normalization tuning already in foundation paper | **Low without mechanism**                                                                           |
  | Extension to adaptive optimizers/neural nets                                                                       | Very crowded area                                                                  | **Not inherently novel; should remain secondary**                                                   |
  | Extension to overparameterized interpolation                                                                       | Huge implicit-bias literature                                                      | **Would require a fresh novelty review**                                                            |

The main implication is that **the project becomes more novel as it becomes more
statistical and less generic-optimization-oriented**.

The phrase “joint effects of four hyperparameters” sounds broad but does not by
itself establish novelty. Conversely, a narrow theorem about common/rare
dependent binary coordinates can be substantially more original if it exposes a
mechanism absent from general risk bounds.

## What would make the contribution clearly novel

I would not make the eventual paper's main contribution “a comprehensive study
of normalization, learning rate, batch size, and stopping.” That invites the
obvious response that all four have already been studied extensively.

Instead, I would aim for one or two theorem-shaped discoveries.

### A normalization-ranking reversal theorem

A particularly strong result would establish conditions under which, for
example,

$$
  R_k(\delta=1/2)<R_k(\delta=0)
$$

at one stopping regime but

$$
  R_{k'}(\delta=1/2)>R_{k'}(\delta=0)
$$

later, or under a different $B$, with a mechanism decomposed into finite-time
bias and stochastic variance.

Even stronger would be a critical boundary

$$
  k^*=k^*(q,B,\eta,\sigma^2,\beta^*,\rho,\delta_1,\delta_2)
$$

or its asymptotic approximation, at which the ordering changes.

Why this would matter: early-stopping theory already says risk evolves with
training time, and preconditioned-SGD theory already says preconditioning
changes risk ([Ali, Kolter, and Tibshirani][ali2019]; [Su, Zou, and
Wu][su2024]). What would be new is a **statistically interpretable explanation
of how a standard normalization choice causes one rule to dominate another in
one finite-budget regime and lose in another because rare-feature bias and
stochastic variance evolve at different rates**.

That directly answers your central question rather than merely assembling
existing ingredients.

### A batch-rarity/preconditioning law

Another strong target would be an asymptotic regime such as

$$
  q\to0,\qquad B=B_q,\qquad \eta=\eta_q,\qquad k=k_q,\qquad s_R\asymp q^\delta
$$

in which you derive the rare-coordinate error and identify separate terms such
as

$$
  \operatorname{MSE}_R
  =
  \underbrace{\text{finite-time bias}}_{\text{normalization/stopping}} +
  \underbrace{\text{observation-noise variance}}_{\text{effective rare sample
  size}} + \underbrace{\text{multiplicative SGD
  variance}}_{\text{batch/preconditioner}} + o(\cdot).
$$

Then characterize which terms dominate in regimes such as

$$
  Bq\to0,\qquad Bq\to c,\qquad Bq\to\infty.
$$

The novelty would become much stronger if different $\delta$'s have genuinely
different optimal $B,\eta,k$ scalings, rather than merely different constants.

For example, a theorem showing that stronger rare-feature scaling removes a
$q$-dependent deterministic learning bottleneck **but creates a stochastic
stability/noise bottleneck** would provide a memorable “no free normalization”
principle.

This is much more distinctive than the statement that rare features are
infrequently sampled.

### A dependence theorem

Suppose $C$ has common/rare covariance $c$. A useful result could characterize
the rare-coordinate error as something schematically like

$$
  e_R(t)
  =
  a_R(t)e_R(0) + a_{RC}(t)e_C(0) + \text{stochastic terms},
$$

and then show exactly how $a_{RC}(t)$ changes with $\delta$.

The scientifically interesting statement is not that a matrix exponential has an
off-diagonal element. It would be something like:

> For fixed marginal prevalences, increasing positive association changes the
> preferred normalization because the rare coordinate initially learns partly
> through the common feature; the sign reverses for opposite-sign signals or
> negative association.

Your planned equal-sign/opposite-sign and nested/negative-dependence experiments
are unusually well suited to producing such a result.

That would also connect naturally to the original Larsson–Wallin paper's concern
with dependence while producing something genuinely new on the training side
([Larsson and Wallin][larsson2025]).

### An aggregate-versus-subgroup reversal theorem

I think this may be the cleanest bridge between statistics and modern ML
relevance.

Characterize a region where

$$
  \arg\min_\delta R(\delta) \neq \arg\min_\delta R_R(\delta),
$$

and explain the difference through the finite-time coefficient covariance.

Even a two-normalization theorem,

$$
  R_{\delta_1}<R_{\delta_2}, \qquad R_{R,\delta_1}>R_{R,\delta_2},
$$

would be strong if it holds over an open parameter region rather than one
constructed numerical example.

This is less directly crowded by the neighboring SGD literature, whose principal
comparisons generally use aggregate excess risk ([Zou et al.][zou2021]; [Su,
Zou, and Wu][su2024]). It also turns the “rare feature” device from an
optimization curiosity into a statistical prediction problem.

### A counterexample can be a real contribution

Your completion criterion wisely permits a checked counterexample. One
particularly valuable result would be to overturn an apparently plausible
heuristic, for example:

$$
  Bq\text{ matched} \quad\not\Rightarrow\quad \text{matched rare-coordinate SGD
  behavior},
$$

or

$$
  \eta P C\text{ matched at the mean level} \quad\not\Rightarrow\quad
  \text{matched prediction risk},
$$

because the second-moment operator differs.

Similarly, you could show that matching flow time

$$
  T=k\eta
$$

correctly aligns deterministic mean trajectories over a range but fails to align
stochastic covariance.

Such a result would define precisely where commonly used optimization
approximations stop being statistically adequate. That is a good contribution
even if no normalization rule emerges as universally superior.

## Recommended scientific positioning

I would narrow the conceptual claim. **“Normalization and implicit
regularization” is accurate but puts the work in an extremely broad and crowded
literature.** In ML, “normalization” also readily evokes batch normalization,
layer normalization, RMS normalization, and parameter normalization, none of
which is your primary object.

A more defensible intellectual description is:

> **Feature scaling as prevalence-dependent preconditioning of finite-time
> SGD.**

or, more fully,

> **How feature scaling allocates finite-time bias and stochastic variance
> across common and rare features.**

The storyline could then be:

1. **Feature scaling is diagonal preconditioning.** Global scaling is exactly
   absorbable into the learning rate, so only relative scaling can have a
   substantive effect.
2. **For unequal feature prevalences, conventional normalization rules imply
   radically different coordinate learning rates.** This is the simple
   deterministic mechanism.
3. **SGD makes aggressive rare-feature scaling costly.** Batch rarity,
   observation noise, and multiplicative gradient noise determine that cost.
4. **Early stopping selects a point on this bias–variance trajectory.**
5. **Dependence moves error between features**, so coordinatewise reasoning
   ceases to suffice.
6. **Aggregate and rare-subgroup prediction can therefore favor different
   training configurations.**

That is a coherent statistical contribution. It is more specific than the
general preconditioning literature and more mechanistic than simply tuning
normalization.

I would also be explicit in the paper about the closest literature rather than
trying to place it at a distance:

- Larsson–Wallin: normalization changes **explicit regularization** for
  prevalent versus rare binary features ([Larsson and Wallin][larsson2025]).
- Ali–Kolter–Tibshirani and related work: stopping induces **finite-time
  regularization** in least squares ([Ali, Kolter, and Tibshirani][ali2019]).
- Ali–Dobriban–Tibshirani and Zou et al.: SGD itself has analyzable
  **statistical regularization behavior** in least squares ([Ali, Dobriban, and
  Tibshirani][ali2020]; [Zou et al.][zou2021]).
- Su–Zou–Wu: **preconditioning changes that behavior** ([Su, Zou, and
  Wu][su2024]).
- Jain et al. and Meterez et al.: mini-batch size and learning rate have
  nontrivial and sometimes equivalent effects in least-squares SGD ([Jain et
  al.][jain2018]; [Meterez et al.][meterez2026]).
- Sparse/frequency-adaptive optimization: rare feature occurrence has long been
  recognized as an optimization issue ([Défossez and Bach][adabatch2017];
  [Duchi, Hazan, and Singer][duchi2011]).
- **Your gap:** none of these works, as far as I could find, asks how *ordinary
  preprocessing normalization based on feature prevalence* jointly redistributes
  deterministic learning and stochastic error across **dependent common/rare
  features over the finite training path**, and then evaluates both overall and
  rare-presence prediction risk.

That final sentence is, in my judgment, the novelty claim worth trying to
substantiate.

## Final verdict

**I would proceed with this project, but I would not yet describe the research
plan itself as demonstrating a novel idea. It identifies a plausibly novel gap;
the novelty still has to crystallize into a result.**

The broad umbrella is crowded. In particular, three developments rule out broad
claims:

1. early stopping and whole-path regularization for least squares are already
   established; [Ali, Kolter, and Tibshirani][ali2019]; [Sonthalia, Lok, and
   Rebrova][sonthalia2026].
2. preconditioned SGD for least squares has already been studied explicitly as
   implicit regularization; [Su, Zou, and Wu][su2024].
3. learning-rate/batch-size equivalence now has a finite-sample
   noisy-linear-regression treatment ([Meterez et al.][meterez2026]).

But those papers do **not**, from the literature I located, collapse your
project. Rather, they sharpen what is actually new about it.

The part I would rate most highly is the combination

$$
  \boxed{ \text{feature prevalence} \;\longrightarrow\;
  \text{normalization/preconditioning} \;\longrightarrow\; \text{coordinate
  learning rates and stochastic fluctuations} \;\longrightarrow\; \text{finite
  stopping} \;\longrightarrow\; \text{coefficient and subgroup risk} }
$$

with **feature dependence** determining how errors propagate between
coordinates.

That chain appears substantially less explored than any of its individual links.

My qualitative novelty ratings would be:

  | Aspect                                               | Rating                                                                              |
  | ---------------------------------------------------- | ----------------------------------------------------------------------------------: |
  | Broad central question                               |                                                                             **2/5** |
  | Normalization as preconditioning                     |                                                                             **1/5** |
  | Common/rare deterministic learning-rate mechanism    |                                                                           **2.5/5** |
  | Normalization × stochastic batch rarity              |                                                                           **3.5/5** |
  | Normalization × stopping-time bias–variance reversal |                                                                             **4/5** |
  | Dependence-induced common/rare coefficient coupling  |                                                                             **4/5** |
  | Aggregate versus rare-subgroup risk interaction      |                                                                         **4–4.5/5** |
  | Full integrated statistical program                  | **4/5**, provided it yields an analytical result rather than only a grid experiment |

The **strongest paper would not try to claim all four hyperparameters as
individually novel**. It would establish a small number of sharp comparative
statements—for example, a normalization-ranking reversal, a $Bq$-regime theorem
with a limitation under dependence, and/or an aggregate-versus-rare-subgroup
risk reversal—and use the broader experimental program to show where those
mechanisms persist.

One specific part of the current plan deserves caution: the internally described
result

$$
  \operatorname{MSE}_R\sim\frac{4\sigma^2}{3nq_n}
$$

under one normalization and one schedule may be a useful theorem and technical
foundation, but **on the information given I would not make it the novelty
centerpiece**. An error rate of order $1/(nq)$ is qualitatively what one expects
when a coefficient is informed by an effective sample size of order $nq$; the
distinctive contribution would be showing how that limit **changes across
normalization, batch, and stopping regimes**, or proving that some apparently
natural alternative cannot attain it.

So the answer to “Does this research plan represent a novel idea?” is:

> **Yes at the level of the specific statistical synthesis and several proposed
> comparison questions; no at the level of its individual ingredients. The
> strongest currently defensible novelty claim is the joint,
> prevalence-structured finite-time behavior of ordinary SGD under feature
> normalization—especially when batch rarity, feature dependence, and subgroup
> risk are included. A sharp comparative theorem in that space would, based on
> the literature reviewed here through September 15, 2026, give the project a
> credible and potentially strong original contribution.**

[ali2019]: https://proceedings.mlr.press/v89/ali19a.html
[ali2020]: https://proceedings.mlr.press/v119/ali20a.html
[zou2021]: https://arxiv.org/abs/2108.04552v2
[jain2018]: https://jmlr.org/papers/v18/16-595.html
[meterez2026]: https://arxiv.org/html/2510.14717v2
[su2024]: https://arxiv.org/html/2403.08585v3
[larsson2025]: https://arxiv.org/html/2501.03821v3
[scott2026]: https://arxiv.org/abs/2511.19716v3
[sonthalia2026]: https://arxiv.org/abs/2406.04425v2
[jahn2026]: https://arxiv.org/abs/2609.11273v1
[smith2018]: https://arxiv.org/abs/1711.00489v2
[smith2021]: https://arxiv.org/abs/2101.12176v1
[adabatch2017]: https://arxiv.org/html/1711.01761v1
[duchi2011]: https://jmlr.org/papers/v12/duchi11a.html
[everett2026]: https://arxiv.org/abs/2605.28961v1
[chen2026]: https://arxiv.org/abs/2605.24316v3
[lin2025]: https://arxiv.org/abs/2506.08415v2
[defossez2015]: https://proceedings.mlr.press/v38/defossez15.html
