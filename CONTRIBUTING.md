# Contributing

This guide covers changes to the code, analyses, figures, and manuscript for
*Feature Normalization under Finite Training Budgets*. For reproducing the paper
from the supplied results, start with [README.md](README.md) and the
[reproduction guide](REPRODUCING.md).

## Development environment

The optional [devenv](https://devenv.sh/getting-started/) environment supplies
Python 3.13, the dependencies in `uv.lock`, LaTeX, Lean, Task, and validation
tools. Install [Nix](https://nixos.org/download/) and devenv, then run from the
repository root:

```sh
devenv shell
```

`devenv.lock` pins the Nix inputs. Initial setup needs network access. Without
devenv, use the Python setup in the README and install the additional tools
needed for your changes. [Task](https://taskfile.dev/) is optional and uses the
active Python environment. Run `task --list` to see its convenience commands.

## Editing experiments

Configurations are ordinary Python values. The controlled study's rate grid,
sample sizes, and seed are in
[experiments/theory_bridge/config.py](experiments/theory_bridge/config.py). The
finite-prevalence searches and common-feature extension use
[experiments/oracle_finite/config.py](experiments/oracle_finite/config.py) and
[experiments/common_block/config.py](experiments/common_block/config.py). Shared
moment routines and numerical utilities live in `experiments/common/`.

To add an experiment, create `experiments/<name>/` with `__init__.py` and
`run.py`, and add a `summarize.py` when useful. Register its modules in
`experiments/__main__.py` and add a convenience task in `Taskfile.yml`. Use
`python -m experiments.<name>.run` from the repository root. Save numerical
outputs and settings under `results/<name>/`. New experiments can reuse
functions in `experiments/common/` without depending on another experiment's
command-line entry point.

Use named arrays in compressed `.npz` archives for detailed numerical results,
and JSON for settings, axis labels, and derived summaries. Small deterministic
illustrations may keep their arrays in JSON. Use
`experiments.common.data.write_json` for JSON files; it rejects nonfinite
numbers. Encode intended missing values as `None` in the analysis and report
missing replicate counts when summarizing sampled results. Summaries should read
settings from the saved records rather than the current configuration. Provide a
read-only `--check` mode that uses
`experiments.common.reproduction.assert_reproduced` to verify the summary with
the shared numerical tolerances, and include it in the saved-result checks. Use
`assert_arrays_reproduced` from the same module for derived archives; it checks
floating-point arrays with those tolerances and discrete arrays exactly.

Commit the code, settings, and reported results together when recording a paper
version. Keep the seeds, candidate settings, selections, and numerical
diagnostics needed to reproduce and assess the current manuscript in the saved
results. Obsolete experiments and their artifacts may be removed. Use Git
history to record changes.

## Validation

Checks are executable Python modules in `checks/`. Run the checks relevant to
your changes with `python -m checks.<name>`. For example:

```sh
python -m checks.oracle_limits
python -m checks.theory_bridge
python -m checks.workflow
```

The workflow check exercises small configurations in temporary directories
without replacing saved experiment results. The [reproduction
guide](REPRODUCING.md) maps the paper's claims and saved analyses to their
checks. Numerical checks supplement the mathematical proofs; retain and report
known discrepancies when changing analyses.

With the development tools installed, use:

```sh
task check-python
task check:results
task check
```

`task check-python` checks Python formatting and lint with Ruff.
`task check:results` reconstructs saved losses, selections, and summaries.
`task check` runs formatting, configuration, and numerical checks and builds the
paper, matching CI.

Lean checks run separately:

```sh
task prepare-lean
task check-lean
```

The preparation step downloads Mathlib caches. See the [Lean
guide](lean/README.md) for the formalized statements and their scope.

## Figures and manuscript

Edit plots in [scripts/figures/](scripts/figures/README.md), using `style.py`
and `palette.toml` for shared styling. Regenerate figures and build the paper
with:

```sh
task figures
task paper
```

These commands read saved results without running experiments. If an analysis
changes, regenerate its summary before plotting. Figure exports go in
`figures/`, and the compiled manuscript is `build/main.pdf`. The generated
selection-gain and risk-decomposition tables live in `paper/generated/`.

## Style and change descriptions

Use four-space Python indentation, an 88-character line limit, `snake_case`
functions and modules, and `UPPER_CASE` constants. Use `run.py` and
`summarize.py` for experiment entry points and `plot_*.py` for figures. Preserve
manuscript notation. Comments should explain why the code works as it does,
using complete sentences.

`task format` formats Markdown with Panache at 80 columns, Nix with nixfmt, and
Python with Ruff. When editing prose, follow the surrounding author's voice, use
American English and the Oxford comma, and prefer concrete subjects and active
verbs.

Use Conventional Commits with ASCII messages and short titles, ideally under 60
characters. Link issues with `Fixes #N`, `Closes #N`, or `Refs #N` as
appropriate. Pull requests should explain the change, identify affected
scientific claims or artifacts, and report validation commands. Include figure
previews when changing plots.

## Packaging and containers

`task package` (also named `task package-code`) creates
`build/normreg-multi-<version>.tar.gz`, using the version in `pyproject.toml`.
The archive contains the paper source and styles, experiment and plotting code,
saved feature draws, results, numerical checks, Lean source, instructions, and
environment files. It can be extracted and used without Git history. The image
and archive take their contents from the same definition in
[nix/release.nix](nix/release.nix).

`task review:package` derives the anonymous
`build/normreg-multi-review-<version>.tar.gz` supplement used by private paper
reviews from the complete release archive. It retains the manuscript source,
task and environment files, saved feature draws and arrays, and numerical and
formal checks described in the source-supplement appendix. It replaces the
repository README with the anonymous [reproduction guide](REPRODUCING.md) and
omits contributor documentation and repository CI metadata. Both archives
exclude private notes, local reviews, instruction files, build products, and
downloaded caches. `task check:packages` builds both archives and checks their
reproduction contents and README links.

For the current ALT rehearsal, run `task review-alt`. It builds the manuscript,
creates the curated supplement, and passes both to `codex-alt-review`; it never
passes the repository checkout itself.

Local environments, build products, private mock reviews, and Lean's downloaded
caches are excluded. Packaging and container builds do not run experiments.

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
