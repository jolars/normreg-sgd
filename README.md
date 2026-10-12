# Feature normalization under finite training budgets

This repository contains the [manuscript](paper/main.tex), experiment code,
source data, saved results, and numerical checks for the study. The repository
and release archive use the same layout and commands.

The manuscript focuses on the oracle results, their numerical illustrations, the
common-feature extension, and the controlled training study. Earlier
fixed-calibration, signal-allocation, synthetic, and Mushroom investigations
remain reproducible from the code and saved results, but are outside the
manuscript.

## Python environment

Run commands from the repository or extracted archive root. Experiments and
numerical checks need Python 3.12 or later, NumPy, SciPy, and Matplotlib. They
run on the CPU and do not need Nix, devenv, Task, or LaTeX.

To install the versions recorded in `uv.lock`, install
[uv](https://docs.astral.sh/uv/getting-started/installation/) and run:

```sh
uv sync --locked --no-dev --python 3.13
. .venv/bin/activate
export OPENBLAS_NUM_THREADS=1
```

This uses Python 3.13, matching the development environment. Initial setup needs
network access. The [`--locked`
option](https://docs.astral.sh/uv/concepts/projects/sync/) checks that the
lockfile matches `pyproject.toml` and installs its recorded versions without
updating it. After activation, use the `python` commands below. You can also run
them without activation by replacing `python` with
`uv run --locked --no-dev python`.

If you prefer standard Python tools, create a virtual environment and install
compatible dependencies with pip:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install 'numpy>=2.0' 'scipy>=1.14' 'matplotlib>=3.10'
export OPENBLAS_NUM_THREADS=1
```

These version ranges match `pyproject.toml`, but pip does not read `uv.lock`.
Use the uv setup to reproduce the recorded Python dependency versions. The
thread setting matches the saved experiments; the named experiment command also
sets it for every subprocess.

## Running experiments

Run and summarize a named experiment with `python -m experiments NAME`. Run
`python -m experiments --help` to list names and options. Each experiment has a
directory in `experiments/`. Shared data loading, random streams, SGD updates,
and statistics live in `experiments/common/`. The Mushroom and synthetic
experiments run independently.

  | Experiment          | Purpose                                                     | Results                      |
  | ------------------- | ----------------------------------------------------------- | ---------------------------- |
  | `mushroom`          | Categorical scaling, rate searches, and damping sensitivity | `results/mushroom/`          |
  | `synthetic`         | Sampled training, estimated preprocessing, and selection    | `results/synthetic/`         |
  | `exact-risk`        | Exact moments, rate comparisons, and paired simulations     | `results/exact-risk/`        |
  | `predictive-intro`  | Finite-grid oracle illustration                             | `results/predictive-intro/`  |
  | `coefficient-paths` | Constructed full-gradient paths to a shared OLS solution    | `results/coefficient-paths/` |
  | `signal-allocation` | Intermediate signal-allocation illustration                 | `results/signal-allocation/` |
  | `oracle-finite`     | Limiting predictions against finite-prevalence exact risks  | `results/oracle-finite/`     |
  | `common-block`      | Exact-moment searches with a growing common-feature block   | `results/common-block/`      |
  | `theory-bridge`     | Controlled departures from the oracle model                 | `results/theory-bridge/`     |
  | `diagnostics`       | Numerical discrepancies and prediction clipping             | `results/diagnostics/`       |
  | `precision`         | Decimal replay of selected synthetic paths                  | `results/synthetic/rates5/`  |

Mushroom supports `rates5`, `rates17`, `rates25`, and `damping`. Synthetic data
supports `rates5` and `rates25`. The default runs every configuration for that
experiment. Select one configuration with:

```sh
python -m experiments mushroom --config rates17
```

Run or summarize separately when changing the analysis:

```sh
python -m experiments mushroom --config rates17 --stage run
python -m experiments mushroom --config rates17 --stage summarize
```

The same stage options work for synthetic data, exact-risk, oracle-finite,
common-block, and theory-bridge. Illustrations and saved-path analyses compute
summaries in their run step. `python -m experiments diagnostics` reconstructs
discrepancies from saved paths and updates the separate diagnostic tables.

You can also invoke individual modules directly, including their additional
options:

```sh
python -m experiments.mushroom.run --config rates17
python -m experiments.mushroom.summarize --config rates17
python -m experiments.theory_bridge.run --help
```

For example, `python -m experiments exact-risk` runs the moment calculation,
paired simulations, and summary in sequence. The diagnostics command first
reconstructs the variance-scaling audit. Each command stops if a step fails.

The controlled bridge study compares representatives of the theorem's two signal
families while separately introducing observation reuse, estimated scales,
fitted intercepts, estimated centering, and initialization at the training mean.
Rates and stops are calibrated on independent replications, then compared with
finite-validation selection on the same candidate paths. Its
[protocol](experiments/theory_bridge/PROTOCOL.md) specifies the candidate
family, sampling, budgets, and interpretation. The [manuscript](paper/main.tex)
presents the findings; the [saved summary](results/theory-bridge/summary.json)
contains paired risk differences and numerical diagnostics.

```sh
python -m experiments theory-bridge
python -m experiments theory-bridge --stage summarize
python scripts/figures/plot_theory_bridge.py
python -m checks.theory_bridge
```

The manuscript build includes both bridge figures. Raw samples, calibration risk
sums, selected predictors, and selection indices remain in the result shards.
The runner accepts `--workers`, `--output`, `--calibration-reps`, and
`--evaluation-reps` for explicitly separate runs, through
`python -m experiments.theory_bridge.run`. Pass the same `--output` directory to
`python -m experiments.theory_bridge.summarize` afterward.

`python -m experiments calibration-sensitivity` reconstructs a diagnostic that
selects tuning choices on one half of the saved calibration shards and evaluates
them on the disjoint other half. It uses 100 partitions in both orientations
without retraining. The [saved
results](results/theory-bridge/calibration-sensitivity.json) report ordering and
selection sensitivity; overlapping splits are not independent replications.
`python -m checks.calibration_sensitivity` checks the selection logic and
reconstructs the saved diagnostic.

`python -m experiments exact-calibration` computes exact expected risks over the
saved candidate family for both fresh arms, including the fitted intercept's
cross moments. The [saved
benchmark](results/theory-bridge/exact-calibration.json) compares the frozen
calibration choices with the best fixed choices at every cap, prevalence, and
signal pair. This deterministic calculation identifies calibration suboptimality
without retraining or changing the original choices.
`python -m checks.exact_calibration` checks exhaustive short SGD paths, the
baseline's existing moments, and reproduction of all saved candidate risks and
summaries.

`python -m experiments risk-decomposition` decomposes saved rare risks in both
fresh arms into common-coefficient, centered-intercept, rare-coefficient, and
cross terms without retraining. The [saved
results](results/theory-bridge/risk-decomposition.json) show that opposing
intercept and rare-coefficient errors account for the fitted-intercept
exact-selection reversal. The analysis retains all caps, prevalences, signals,
and selectors, including validation reversals without this mechanism.
`python -m checks.risk_decomposition` verifies the per-run terms, paired
contributions, cancellation summaries, and generated table against independent
cell predictions and the existing risks and gains. Omitting the cross term is an
accounting diagnostic; resetting the selected intercept does not retrain or
reselect.

Experiments can take substantial time and replace the saved outputs for the
selected configuration. Use a separate extracted copy to retain the supplied
results when rerunning experiments. Summarizing reads those outputs without
retraining. Building figures or the paper never launches experiments. Saved
summaries are included so the manuscript can be built immediately. The two large
exact-risk files, `paths.npz` and `summary.json`, are ignored; regenerate them
explicitly with `python -m experiments exact-risk` when needed.

## Editing experiments

Configurations are ordinary Python values. Mushroom's 17-factor grid is in
[experiments/mushroom/rates17.py](experiments/mushroom/rates17.py), and its
damping offsets are in
[experiments/mushroom/damping.py](experiments/mushroom/damping.py). The shared
25-factor comparison is in
[experiments/common/rates25.py](experiments/common/rates25.py). Data generation,
the five-factor grid, sample sizes, and seeds are in
[experiments/common/data.py](experiments/common/data.py).

To add an experiment, create `experiments/<name>/` with `__init__.py` and
`run.py`, add a `summarize.py` when useful, and register its modules in
`experiments/__main__.py` and add a convenience task in `Taskfile.yml`. Use
`python -m experiments.<name>.run` from the repository root. Save numerical
outputs and settings under `results/<name>/`. New experiments can reuse
functions in `experiments/common/` without depending on another experiment's
command-line entry point.

Git records changes to code, settings, and reported results. There are no
checksum checks, locked declarations, or dependencies on old Git revisions.
Commit the code, settings, and reported results together when recording a paper
version. Seeds, candidate settings, selections, and numerical failures remain in
the saved results.

## Checks and figures

`checks/` contains executable numerical checks, including independent SGD
updates, moment identities, selection rules, and theorem certificates. Run
individual checks with `python -m checks.<name>`. The workflow check exercises
small configurations in temporary directories without replacing saved experiment
results.

```sh
python -m checks.predictive_theorem
python -m checks.predictive_fixed_q
python -m checks.predictive_review
python -m checks.oracle_limits
python -m checks.oracle_infima
python -m checks.oracle_variational
python -m checks.oracle_finite
python -m checks.normalization_risk_theorem
python -m checks.workflow
python -m checks.practical_selection
python -m checks.mushroom_rate_search
python -m checks.mushroom_sensitivity
python -m checks.variance_scaling
python -m checks.theory_bridge --saved
python -m experiments.theory_bridge.summarize --check
python -m experiments.diagnostics.run --check
python -m checks.exact_calibration
python -m checks.selection_gains
python -m checks.risk_decomposition
```

After explicitly generating the optional large exact-risk outputs, check them
with `python -m checks.normalization_robustness`.

The finite-prevalence checker certifies the continuous parameter regions in
Theorem 3.1 and Appendix A with exact rational exponential enclosures. Its rate
intervals bound every nonnegative constant rate, with analytic bounds above one,
and every admissible stop. It also checks the fixed example at $q = 0.02$ and
$M = 102$ and compares the bounds with observation-level moment calculations.
The earlier small-prevalence certificates remain in the theorem and review
checkers; they do not independently certify the new extension.

The source archive includes the certificate checkers and their recorded standard
output:

  | Claim                         | Checker                                                           | Recorded output                                                         |
  | ----------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------- |
  | Theorem 3.1 and Appendix A    | [Finite-prevalence checker](checks/predictive_fixed_q.py)         | [Finite-prevalence output](results/certificates/predictive-fixed-q.txt) |
  | Fixed-calibration comparisons | [Fixed-calibration checker](checks/normalization_risk_theorem.py) | [Fixed-calibration output](results/certificates/normalization-risk.txt) |

From the extracted archive, run `python -m checks.predictive_fixed_q` and
`python -m checks.normalization_risk_theorem`. These commands recompute the
certificates without training models. The first reports all six certified
regions, accepted box counts, exact coverage volumes, and the smallest certified
margins. Its exponential enclosures and volume checks use exact rational
arithmetic; displayed decimal margins are rounded. The second reports the
earlier fixed-calibration bounds and separate numerical diagnostics. The saved
output summarizes completed checks and does not replace rerunning them.

The [manuscript proof](paper/oracle-proofs.tex) establishes convergence of the
unrestricted rate-and-stop infima for fixed finite signals and noise and finite
positive rescaled budgets. The same manuscript source gives unique scalar rate
equations and explains the signal, noise, and budget regimes.
`python -m checks.oracle_limits` runs the limit diagnostics. Run
`python -m checks.oracle_infima`, `python -m checks.oracle_variational`, and
`python -m checks.oracle_finite` for uniform-control checks, variational checks,
and finite-prevalence comparisons. The earlier recorded outputs are [limit
checks](results/oracle-limits/checks.json) and [infimum
checks](results/oracle-limits/infimum-checks.json), plus [variational
checks](results/oracle-limits/variational-checks.json). These numerical
diagnostics supplement the analytic proofs and are separate from the
finite-prevalence certificates. The proof includes the boundary-sequence
arguments needed for unrestricted rate and stopping optimization.

The [finite-prevalence comparison](paper/oracle-numerics.tex) tests 43 settings
at six prevalences, retaining the theorem as the quantitative guarantee. It
recovers the limiting signal, noise, and budget predictions at small prevalence
and records a high-noise disagreement at larger prevalence. The [saved
summary](results/oracle-finite/summary.json) retains absolute risks, rates,
stops, and separate rate and stop refinement diagnostics. Run
`python -m experiments oracle-finite` to regenerate the exact-moment searches
and summary, `python -m checks.oracle_finite --rerun` to replay every search,
and `python scripts/figures/plot_oracle_finite.py` to plot the saved
comparisons. These finite-grid searches do not certify continuous optima.

Use `python -m experiments diagnostics` to regenerate the diagnostic records and
tables, then run the saved-result checks listed above to verify them. Use
`python -m experiments signal-allocation` to regenerate the signal-allocation
illustration, `python -m experiments coefficient-paths` to regenerate the
constructed paths to OLS, and the illustration modules with `--check` to verify
the illustration summaries. The introductory signal-crossing figure holds
$s/4 + r$ fixed and plots the saved nominal limiting risks from `oracle-finite`
at rescaled budget two. The earlier allocation map at fixed $s + r$ remains
available through its experiment and plotting script.

Checks retain and report the known numerical discrepancies in extreme synthetic
paths. They do not certify those paths merely because structural checks pass.
These archived investigations are outside the current manuscript. Numerical
checks supplement the retained mathematical proofs.

Edit manuscript plots in [scripts/figures/](scripts/figures/README.md).
Generated PDF, SVG, and PNG files go in `figures/`; LaTeX output goes in
`build/`. The generated diagnostic table is
`paper/generated/review-diagnostics.tex`. Formal proofs of the large-rate bounds
and common-feature dimension proposition live in [lean/](lean/README.md) and are
checked separately with `lake exe cache get` and `lake build` from `lean/`.

## Figures and paper build

Plotting uses Matplotlib's LaTeX renderer. Install a TeX distribution with
`latex`, `dvipng`, the Times fonts, and the packages listed in `devenv.nix`.
Compiling the paper also requires `latexmk` and `pdflatex`. These tools can be
installed separately from Python; the optional devenv environment below supplies
them together.

Generate the manuscript figures from saved results:

```sh
python scripts/figures/plot_coefficient_paths.py
python -m scripts.figures.plot_signal_crossing
python scripts/figures/plot_predictive_intro.py
python scripts/figures/plot_tuned_decomposition.py
python scripts/figures/plot_common_block.py
python scripts/figures/plot_oracle_finite.py
python scripts/figures/plot_theory_bridge.py
```

Then compile the complete paper, including the appendices:

```sh
(cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir=../build main.tex)
```

The output is `build/main.pdf`. Plotting and compiling the paper read saved
results without running experiments. See the [figure
guide](scripts/figures/README.md) for individual outputs and styling.

## Optional devenv environment

For stronger reproducibility of system tools as well as Python dependencies,
install [Nix](https://nixos.org/download/) and
[devenv](https://devenv.sh/getting-started/), then enter:

```sh
devenv shell
```

This supplies Python 3.13, the dependencies in `uv.lock`, LaTeX, Lean, Task, and
validation tools. `devenv.lock` pins the Nix inputs. Initial setup needs network
access. The same Python commands work inside this environment. Use it when you
want to reproduce the system packages used for development and the paper build.

## Task convenience wrappers

[Task](https://taskfile.dev/) provides convenience wrappers around the Python,
plotting, and build commands. It is optional and can be installed independently
or supplied by devenv. Run `task --list` to see the available wrappers. Task
uses the active Python environment; it does not install Python dependencies
itself.

```sh
task experiment:mushroom -- --config rates17
task experiment:synthetic -- --config rates5
task experiment:theory-bridge
task figures
task paper
task check:workflow
```

The experiment tasks run the same modules as `python -m experiments NAME`. Where
an experiment has separate summaries, its `:run` and `:summarize` tasks separate
those steps. `task check:results` groups the saved-result checks, and
`task check-experiments` runs the broader numerical checks. `task check` also
runs formatting and configuration checks and builds the paper, using the
additional development tools supplied by devenv. `task prepare-lean` downloads
Mathlib caches, and `task check-lean` builds the formal proofs; they run
separately from `task check`.

## Packaging and containers

`task package` (also named `task package-code`) creates
`build/normreg-multi-<version>.tar.gz`, using the version in `pyproject.toml`.
The archive contains the paper source and styles, experiment and plotting code,
source data, saved results, numerical checks, Lean source, instructions, and
environment files. It can be extracted and used without Git history. The image
and archive take their contents from the same definition in
[nix/release.nix](nix/release.nix).

`task review:package` derives the anonymous
`build/normreg-multi-review-<version>.tar.gz` supplement used by private paper
reviews from the complete release archive. It retains the manuscript source,
task and environment files, source data, saved arrays, and numerical and formal
checks described in the source-supplement appendix. It replaces the repository
README with the anonymous [reproduction guide](REPRODUCING.md) and omits
repository CI metadata. Both archives exclude private notes, local reviews,
instruction files, build products, and downloaded caches. `task check:packages`
builds both archives and checks their reproduction contents and README links.

For the current ALT rehearsal, run `task review-alt`. It builds the manuscript,
creates the curated supplement, and passes both to `codex-alt-review`; it never
passes the repository checkout itself.

Local environments, build products, private mock reviews, and Lean's downloaded
caches are excluded. As in the repository, the two large exact-risk outputs must
be generated with `task experiment:exact-risk`; they are not needed to build the
paper. Packaging and container builds do not run experiments.

Build and load the image on a Linux machine with Nix, devenv, and Docker:

```sh
devenv shell task container:load
```

The local image is `normreg-multi:<version>`. `task container:build` builds the
image specification without loading Docker. The image includes the archive
contents under `/env`, Python 3.13 with the dependencies from `uv.lock`, Task,
and the manuscript's LaTeX tools. It uses the same pinned Nix packages as the
development environment. No Nix installation or package downloads are needed to
run the loaded image.

For example, replace `<version>` with the version being reproduced:

```sh
docker run --rm --network none normreg-multi:<version> task --list
docker run --rm --network none normreg-multi:<version> task check:workflow
docker run --name normreg-paper --network none normreg-multi:<version> task paper
docker cp normreg-paper:/env/build/main.pdf ./main.pdf
docker rm normreg-paper
```

The same image runs `task experiment:<name>` and `task check:results`. To retain
new results, keep the container until `docker cp` has copied `/env/results`, or
mount a writable copy of the extracted archive at `/env`. The separate
`task prepare-lean` step downloads Mathlib caches and needs network access.

Publish the versioned image to a registry explicitly:

```sh
devenv shell task container:publish REGISTRY=docker://ghcr.io/jolars/
```

Authenticate with that registry before publishing. This command publishes
`ghcr.io/jolars/normreg-multi:<version>`; the archive in `build/` can be
attached to the corresponding repository release. Reviewers can use either the
archive with Python, the optional devenv environment, or the published image.
See the [devenv container documentation](https://devenv.sh/containers/) for
other registry destinations.
