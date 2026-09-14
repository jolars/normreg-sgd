# Research plan

The consolidated task checklist is in [TODO.md](../TODO.md). This note records
the research question, mathematical setup, and scope of the existing results.

The central question is when marginal feature normalization controls shrinkage
in the presence of correlated predictors. The motivating example is a rare
binary feature whose Pearson correlation with another feature vanishes, while
the other coefficient's shrinkage continues to affect its estimate.

Covariance divided by the rare feature's variance, together with the nuisance
estimator's bias, describes this effect more usefully than correlation alone.
The general bias-transfer mechanism has precedents in regularization-induced
confounding. The candidate contribution is its interaction with binary rarity,
normalization, and thresholding; its generality and novelty remain to be
established through the comparisons in [TODO.md](../TODO.md).

## Current foundation

  | Result                                                       | Status and scope                                                                                                                                                    |
  | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | Nine KKT regions and exact selection integral                | Derived for two features with a positive-definite centered Gram matrix and fixed weights.                                                                           |
  | Gaussian bias and covariance by region integration           | Derived and implemented; independent coordinate descent and Monte Carlo checks are available.                                                                       |
  | Ridge mean and covariance                                    | Standard matrix formulas, valid beyond orthogonality.                                                                                                               |
  | Exact variance-scaled lasso shrinkage with one true signal   | Proved for two binary features without noise.                                                                                                                       |
  | Sign-dependent shrinkage with two signals                    | Derived within a valid active-sign region; includes feasible binary counterexamples.                                                                                |
  | No universal design-only diagonal correction                 | Proved for reproducing coordinatewise soft thresholding for every signal vector. This is a specific impossibility statement, not a claim that weighting is useless. |
  | Rare-feature bias transfer                                   | Derived for two features in a formal fixed-noise Gram limit; a genuine binary sequence is available in a specific lasso regime.                                     |
  | Several nuisance predictors and statistical sampling regimes | Research objective.                                                                                                                                                 |
  | Novelty relative to weighted-lasso theory                    | Targeted initial references only; unresolved.                                                                                                                       |

The initial investigation also identifies a boundary correction at
$\omega = 1/2$ in the earlier weighted-elastic-net variance theorem. It is
tracked in [TODO.md](../TODO.md) as a separate task in the earlier project.

## First milestone: general theorem and novelty assessment

Use a block design covariance

$$
  C_n = \begin{pmatrix}
          A_n      & c_n \\
          c_n^\top & b_n
        \end{pmatrix}, \qquad b_n
      \downarrow 0,
$$

where the last coordinate is binary and rare, $A_n$ describes a fixed number of
nuisance predictors, and $c_n/b_n$ may have a nonzero vector limit $\kappa$.
Start with $A_n \to A \succ 0$. Let $B$ denote the appropriate limiting
penalized estimator fitted to the nuisance block alone.

For feature scales $s_{\mathrm{rare}}=b_n^\delta$ with $\delta>1/2$ and fixed
score-noise level $\tau>0$, the candidate mean relation suggested by the
two-feature formal limit is

$$
  E\hat\beta_{\mathrm{rare}}
  \longrightarrow \beta_{\mathrm{rare}}^*
                  + \kappa^\top(\beta_{\mathrm{nuisance}}^* - EB).
$$

This formula is a target to derive under stated assumptions. It must not be
applied indiscriminately to changing sample sizes, penalty rates, or active
sets. In particular, the fixed-noise Gram calculation does not itself prove a
sampling theorem.

The milestone is complete when there is a checked theorem with a coherent binary
sampling interpretation, an experiment showing a consequential difference, and a
written comparison to the closest prior results. The theory tasks, literature
comparisons, and experiment design are consolidated in [TODO.md](../TODO.md). A
substantial general result would make the bivariate analysis a useful
introduction to the main contribution.

## Possible contribution after the first milestone

A focused paper could combine a theorem about rare-feature bias transfer,
conditions that preserve normalization effects, and a practical demonstration.
The scope decision follows the first milestone. Further questions about bounded
rare counts, multiple rare features, and nuisance residualization are tracked in
[TODO.md](../TODO.md).
