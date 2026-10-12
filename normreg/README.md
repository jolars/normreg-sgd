# Numerical routines

`normreg` is the repository's shared Python package for the mathematics used in
the experiments. Run Python from the repository root with the dependencies in
`pyproject.toml` installed. The package needs NumPy and SciPy; it uses no
experiment settings or repository paths. It is maintained here for research use
and will not be published to PyPI.

## Modules

- `moments` builds centered two-feature binary models and propagates exact
  fresh-sample SGD moments, including separate design and response-noise
  covariance. It supports independent and nested features, feature scaling, and
  independent samples within each minibatch.
- `risk` evaluates population and rare-subgroup excess half squared loss for
  independent features with common prevalence `0.5` and rare prevalence `q`.
  These risks exclude irreducible test response noise.
- `limiting_oracle` solves the scalar oracle problems as rare prevalence tends
  to zero. Its floating-point roots are not finite-prevalence certificates.
- `common_block` evaluates exact aggregate moments for independent, balanced
  common features and one rare feature, along with stability bounds and limits
  at a fixed positive rate. Endpoint risks and limits assume unit noise
  variance.

The two `stability_limit` functions use their respective modules' rate
conventions. In `moments`, `step` is the learning rate for features divided by
`scales`. In `common_block`, `alpha` is the manuscript's rescaled rate: the
learning rate is `q * (1 - q) * alpha` for standardized training and `alpha` for
unscaled training.

## Example

Compute original-scale coefficient error moments under population
standardization:

```python
import numpy as np

from normreg.moments import make_model, moment_path, stability_limit
from normreg.risk import risks

q = 0.01
model = make_model(q, "independent")
scales = np.sqrt(np.diag(model["gram"]))
step = 0.1 * stability_limit(model, scales, batch=1)
path = moment_path(
    model,
    scales,
    step,
    batch=1,
    counts=[0, 10, 100],
    signal=np.array([0.1, 1.0]),
    noise_variance=1.0,
)
assert path["valid"].all()
expected_rare_risk = 0.5 * np.einsum("ij,kij->k", model["rare_second"], path["second"])

# Evaluate one realized predictor's centered errors instead of expected moments.
population_risk, rare_risk = risks((0.0, -0.1, -1.0), q)
```

`moment_path` starts at zero coefficients and returns the mean coefficient error
as `bias` and its uncentered second moment as `second`, both in the original
feature coordinates. `counts` contains SGD update counts; each update uses
`batch` fresh observations. `valid` reports finite endpoints with numerically
positive semidefinite second moments and covariance components.
`spectral_radius` separately describes moment stability.

`risks((offset, common, rare), q)` accepts broadcastable centered predictor
errors and returns an array with population and rare-subgroup risk on its final
axis. `predictor_risks(coefficients, q, signals)` accepts raw predictors whose
last axis is `(intercept, common coefficient, rare coefficient)`. Its final
three input axes are `(signal, candidate, coefficient)`; `signals` has shape
`(number of signals, 2)` and gives the true coefficients of centered features.

`oracle_minimum(standardized, tau, s, r, noise)` returns limiting risk and the
rare-coordinate rate. `tau` is the rescaled observation budget, `s` and `r` are
the squared common and rare signal coefficients, and `noise` is response noise
variance. Under unscaled training, a returned rate of zero represents a
vanishing-rate sequence that learns the common coordinate.

Keep seeds, grids, calibration rules, saved-result handling, and plotting in
`experiments/` and `scripts/`. The numerical checks in `checks/` validate these
routines against independent calculations and saved manuscript results.
