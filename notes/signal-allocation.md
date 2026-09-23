# Signal allocation under finite search grids

September 23, 2026. This is a post hoc numerical illustration added after
independent review. It explores intermediate signals under the oracle theorem's
data model. It is separate from the preserved introduction figure and the
unexecuted prospective protocol.

## Model and search

Keep independent binary features with common prevalence one half and rare
prevalence `q = 1e-4`, population centering and scales, zero initialization, a
fixed zero intercept, and one fresh observation per update. Set the squared
coefficient sum to 1.01 and allocate fraction `f` to the rare coefficient. This
sum is not aggregate signal variance, which also depends on prevalence.

The 43 allocations are 41 equally spaced fractions from zero to one, together
with `1/101` and `100/101`, which include the original figure's two signal
pairs. Noise variances are 0.25, 1, and 4. There are 21 rounded integer caps
from 10002 to 40004, all within the theorem's observation-budget interval.

Each rule independently selects from zero and 1025 geometric positive rate
parameters from `1e-6` to 2. Stopping candidates include zero, every cap, and
distinct rounded values of 1025 geometric points from one to the largest cap.
Only stops within a given cap are eligible. These are finite rate and stopping
searches; they are not the unrestricted oracle in the theorem.

## Calculation and checks

The calculation propagates the exact diagonal-moment recurrence by powers of its
affine matrix. Risk is linear in the initial squared coefficients and noise
variance, allowing the same propagated matrices to serve all signal allocations.
Initialization remains eligible, and the saved selections include actual rates
and stops. A nested coarse search retains every second positive rate and every
second geometric stopping point, plus zero and all caps.

Joint refinement changes any reported risk by less than `3e-5`. All selections
that take an update have interior rate parameters. The script also checks
finiteness, nonnegativity, budget eligibility, and monotonicity of selected risk
in the cap. A separately enumerated full tensor operator replays 112 selected
endpoints, including pure signals and the original theorem anchors; its maximum
absolute risk disagreement must be below `1e-9`.

The plotted transition shifts with budget and noise. More budget lowers the
rare-signal fraction needed for SD to have lower grid-selected risk at each
plotted noise level. The contours interpolate zero differences between finite
search minima. Neither interior selections nor grid refinement certifies their
location for unrestricted rates and stops, and the numerical accuracy check is
not an error bound relative to that oracle.

## Reproduction

Inside `devenv shell`, run:

```sh
make reproduce-signal-allocation
make check-signal-allocation
make paper
```

The [calculation](../scripts/illustrate_signal_allocation.py) writes
[`summary.json`](../results/signal-allocation/summary.json), including the
grids, both risk arrays, selections, numerical checks, and source hashes. The
separate [figure generator](../scripts/figures/plot_signal_allocation.py) reads
that artifact and exports the manuscript figure to
`build/figures/signal-allocation/`. The existing introduction-figure sources and
artifacts remain unchanged.
