# Feature normalization under finite training budgets

This repository contains the [manuscript](paper/main.tex), experiment code,
source data, saved results, and numerical checks for the study. The repository
and release archive use the same layout and commands.

The manuscript uses the anonymous ALT 2027 template supplied in
`alt2027-template.zip`. Its unmodified class files and sample are vendored in
[`paper/vendor/alt2027/`](paper/vendor/alt2027/README.md). ALT has no page
limit, but reviewers may stop after the first 12 pages, excluding references.
The paper build reports the main-text page count and flags drafts beyond that
threshold.

To build the complete paper from the saved results, install
[Nix](https://nixos.org/download/) and
[devenv](https://devenv.sh/getting-started/), then run this command from the
repository or extracted archive:

```sh
devenv shell task paper
```

The output is `build/main.pdf`, including the appendices. This command generates
the manuscript figures and runs LaTeX without retraining models. The Nix and
Python dependencies are pinned in `devenv.lock` and `uv.lock`. Initial setup
requires network access. A container with the dependencies already installed is
also available through the build instructions below.

For other tasks, enter `devenv shell` and run:

```sh
task experiment:mushroom     # Run and summarize Mushroom comparisons.
task experiment:synthetic    # Run and summarize synthetic-data comparisons.
task experiment:exact-risk   # Compute exact risks and paired simulations.
task figures                # Plot saved results.
task paper                  # Generate figures and compile build/main.pdf.
task check                  # Check code, numerics, illustrations, and the paper.
```

## Packaging and containers

`task package` (also named `task package-code`) creates
`build/normreg-multi-<version>.tar.gz`, using the version in `pyproject.toml`.
The archive contains the paper source and styles, experiment and plotting code,
source data, saved results, numerical checks, Lean source, instructions, and
environment files. It can be extracted and used without Git history. The image
and archive take their contents from the same definition in
[nix/release.nix](nix/release.nix).

`task review:package` creates the smaller
`build/normreg-multi-review-<version>.tar.gz` supplement used by private paper
reviews. It includes the computational and formal-support source plus
human-readable results needed to inspect the paper's claims. It excludes the
repository README, task and environment files, paper source, local reviews, TODO
files, build products, and raw numerical arrays. The full package remains
available when exact numerical artifacts are needed for reproduction.

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
archive with devenv or the published image. See the [devenv container
documentation](https://devenv.sh/containers/) for other registry destinations.

## Running experiments

Each experiment has a directory in `experiments/` and a task named
`experiment:<name>`. Shared data loading, random streams, SGD updates, and
statistics live in `experiments/common/`. The Mushroom and synthetic experiments
run independently.

  | Experiment          | Purpose                                                     | Results                      |
  | ------------------- | ----------------------------------------------------------- | ---------------------------- |
  | `mushroom`          | Categorical scaling, rate searches, and damping sensitivity | `results/mushroom/`          |
  | `synthetic`         | Sampled training, estimated preprocessing, and selection    | `results/synthetic/`         |
  | `exact-risk`        | Exact moments, rate comparisons, and paired simulations     | `results/exact-risk/`        |
  | `predictive-intro`  | Finite-grid oracle illustration                             | `results/predictive-intro/`  |
  | `coefficient-paths` | Constructed full-gradient paths to a shared OLS solution    | `results/coefficient-paths/` |
  | `signal-allocation` | Intermediate signal-allocation illustration                 | `results/signal-allocation/` |
  | `theory-bridge`     | Controlled departures from the oracle model                 | `results/theory-bridge/`     |
  | `diagnostics`       | Numerical discrepancies and prediction clipping             | `results/diagnostics/`       |
  | `precision`         | Decimal replay of selected synthetic paths                  | `results/synthetic/rates5/`  |

Mushroom supports `rates5`, `rates17`, `rates25`, and `damping`. Synthetic data
supports `rates5` and `rates25`. The default runs every configuration for that
experiment. Select one configuration with:

```sh
task experiment:mushroom -- --config rates17
```

Run or summarize separately when changing the analysis:

```sh
task experiment:mushroom:run -- --config rates17
task experiment:mushroom:summarize -- --config rates17
```

These tasks also work for synthetic data. Exact-risk calculations have separate
`:run` and `:summarize` tasks. The two illustrations compute their summaries in
one step. `task experiment:diagnostics` reconstructs discrepancies from saved
paths and updates the diagnostic tables in the manuscript. Run `task --list` to
see all tasks.

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
task experiment:theory-bridge             # Run calibration and evaluation.
task experiment:theory-bridge:summarize   # Reconstruct the saved summaries.
task figure:theory-bridge                 # Plot without training.
task check:theory-bridge                  # Check independent implementations.
```

The manuscript build includes both bridge figures. Raw samples, calibration risk
sums, selected predictors, and selection indices remain in the result shards.
The runner accepts `--workers`, `--output`, `--calibration-reps`, and
`--evaluation-reps` for explicitly separate runs, through
`task experiment:theory-bridge:run -- ...`.

Experiments can take substantial time and replace the saved outputs for the
selected configuration. Use a separate extracted copy to retain the supplied
results when rerunning experiments. Summarizing reads those outputs without
retraining. Building figures or the paper never launches experiments. Saved
summaries are included so the manuscript can be built immediately. The two large
exact-risk files, `paths.npz` and `summary.json`, are ignored; regenerate them
explicitly with `task experiment:exact-risk` when needed.

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
`run.py`, add a `summarize.py` when useful, and register its task in
`Taskfile.yml`. Use `python -m experiments.<name>.run` from the repository root.
Save numerical outputs and settings under `results/<name>/`. New experiments can
reuse functions in `experiments/common/` without depending on another
experiment's command-line entry point.

Git records changes to code, settings, and reported results. There are no
checksum checks, locked declarations, or dependencies on old Git revisions.
Commit the code, settings, and reported results together when recording a paper
version. Seeds, candidate settings, selections, and numerical failures remain in
the saved results.

## Checks and figures

`checks/` contains executable numerical checks, including independent SGD
updates, moment identities, selection rules, and theorem certificates.
`task check` runs these checks and builds the paper without running full
experiments.

```sh
task check:predictive-theorem # Check the oracle-tuning certificates.
task check:predictive-fixed-q # Certify the finite-prevalence gap bounds.
task check:predictive-review  # Run the independent certificate implementation.
task check:oracle-limits      # Check limiting risks and oracle-infimum control.
task check:normalization-risk # Check the supporting comparison certificates.
task check:workflow           # Exercise the workflow with small configurations.
task check:results            # Reconstruct saved losses and selections.
task check:exact-risk-results # Check the large exact-risk outputs, if generated.
```

The finite-prevalence checker certifies the continuous parameter regions in
Theorem 3.1 and Appendix A with exact rational exponential enclosures. Its rate
intervals bound every nonnegative constant rate, with analytic bounds above one,
and every admissible stop. It also checks the fixed example at $q=0.02$ and
$M=102$ and compares the bounds with observation-level moment calculations. The
earlier small-prevalence certificates remain in the theorem and review checkers;
they do not independently certify the new extension.

The source archive includes the certificate checkers and their recorded standard
output:

  | Claim                      | Checker                                                           | Recorded output                                                         |
  | -------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------- |
  | Theorem 3.1 and Appendix A | [Finite-prevalence checker](checks/predictive_fixed_q.py)         | [Finite-prevalence output](results/certificates/predictive-fixed-q.txt) |
  | Appendix B comparisons     | [Fixed-calibration checker](checks/normalization_risk_theorem.py) | [Fixed-calibration output](results/certificates/normalization-risk.txt) |

From the extracted archive, enter `devenv shell` and run
`task check:predictive-fixed-q` and `task check:normalization-risk`. These
commands recompute the certificates without training models. The first reports
all six certified regions, accepted box counts, exact coverage volumes, and the
smallest certified margins. Its exponential enclosures and volume checks use
exact rational arithmetic; displayed decimal margins are rounded. The second
reports the supporting interval bounds and separate numerical diagnostics. The
saved output summarizes completed checks and does not replace rerunning them.

The [oracle-limit notes](notes/oracle-limits.md) prove convergence of the
unrestricted rate-and-stop infima for fixed finite signals and noise and finite
positive rescaled budgets. `task check:oracle-limits` runs both the limit
diagnostics and the uniform-control checks. Their recorded outputs are [limit
checks](results/oracle-limits/checks.json) and [infimum
checks](results/oracle-limits/infimum-checks.json). These numerical diagnostics
are separate from the finite-prevalence certificates; the new proof has not
received independent mathematical review.

Use `task experiment:diagnostics` to regenerate the diagnostic records and
tables, then `task check:results` to verify them. Use
`task experiment:signal-allocation` to regenerate the signal-allocation
illustration, `task experiment:coefficient-paths` to regenerate the constructed
paths to OLS, and `task check:illustrations` to verify the illustration
summaries. The introductory signal-crossing figure uses a slice of the existing
signal-allocation results.

Checks retain and report the known numerical discrepancies in extreme synthetic
paths. They do not certify those paths merely because structural checks pass.
Successful numerical checks also do not replace the mathematical verification
that the manuscript identifies as unfinished.

Edit manuscript plots in [scripts/figures/](scripts/figures/README.md).
Generated PDF, SVG, and PNG files go in `figures/`; LaTeX output goes in
`build/`. The generated diagnostic table is
`paper/generated/review-diagnostics.tex`. Formal proofs live in `lean/` and are
checked separately with `task prepare-lean` and `task check-lean`.
