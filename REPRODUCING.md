# Source supplement

This archive accompanies *Feature Normalization under Finite Training Budgets*.
It contains the manuscript source, experiment and plotting code, saved feature
draws, saved numerical arrays and summaries, certificate checkers, Lean proofs,
and pinned environment definitions described in the source-supplement appendix.

The [normreg package](normreg/README.md) contains the shared numerical routines.
It is importable from the repository root using the Python environment below.
Commands below run from the extracted archive's root and do not require a Git
checkout.

The anonymous review archive uses this document as its root `README.md` and
omits repository CI configuration. It contains the same reproduction inputs as
the complete source release. Local environments, Python caches, and Lean's
downloaded dependencies are excluded from both archives.

The manuscript presents the oracle results, their numerical illustrations, the
common-feature extension, and the controlled training study.

The paper, figures, documentation, and saved experimental data and results are
licensed under [CC BY 4.0](LICENSE-PAPER). The original Python and Lean code,
scripts, and build configuration are licensed under [MIT](LICENSE-CODE). During
anonymous review, attribute the research material to the anonymous authors of
*Feature Normalization under Finite Training Budgets*. Third-party materials,
including the unmodified ALT/JMLR template files in `paper/vendor/alt2027/` and
downloaded dependencies, retain their own licenses and copyright notices.

## Python environment

Run commands from the repository or extracted archive root. Experiments and
numerical checks need Python 3.12 or later, NumPy, SciPy, and Matplotlib. They
run on the CPU and do not need Nix, devenv, Task, or LaTeX.

To install the versions recorded in `uv.lock`, install
[uv](https://docs.astral.sh/uv/getting-started/installation/) and run:

```sh
uv sync --locked --no-dev --python 3.13
. .venv/bin/activate
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
```

These version ranges match `pyproject.toml`, but pip does not read `uv.lock`.
Use the uv setup to reproduce the recorded Python dependency versions. Task and
`python -m experiments` set `OPENBLAS_NUM_THREADS=1` for their subprocesses to
limit CPU contention when experiment workers run in parallel. These commands
handle the setting automatically.

## Certificates and saved results

With the Python environment active, run:

```sh
python -m checks.predictive_fixed_q
python -m checks.oracle_limits
python -m checks.oracle_infima
python -m checks.oracle_variational
python -m checks.oracle_finite
python -m checks.common_block
python -m checks.theory_bridge
python -m checks.theory_bridge --saved
python -m experiments.theory_bridge.summarize --check
python -m checks.exact_calibration
python -m checks.selection_gains
python -m checks.risk_decomposition
```

The first command recomputes the finite-prevalence certificates without training
models. Its recorded output is in
[`results/certificates/`](results/certificates/). The checker covers all six
continuous parameter regions using exact rational enclosures and coverage
checks. The other commands check the limiting characterization,
finite-prevalence selections, common-feature extension, and saved empirical
losses and selections. `python -m checks.workflow` exercises small test
experiments in temporary directories. Other executable checks are in `checks/`.

The analytic limiting proof and its variational consequences are in
[`paper/main.tex`](paper/main.tex). The controlled study's candidate families,
calibration, evaluation, and selection rules are specified in
[`experiments/theory_bridge/PROTOCOL.md`](experiments/theory_bridge/PROTOCOL.md).
Run `python -m experiments calibration-sensitivity` to reconstruct the
diagnostic that recalibrates on disjoint halves of the saved calibration shards
without retraining. Its partitions, selected candidates, held-out risks, and
summaries are saved as `results/theory-bridge/calibration-sensitivity.npz` and
`calibration-sensitivity.json`. `python -m checks.calibration_sensitivity`
checks the selection logic and saved diagnostic. The overlapping splits describe
sensitivity at half the original calibration size, not independent repetitions
or confidence intervals.

For the formal proof pilot, install Lean and run `lake exe cache get`, then
`lake build` from `lean/`. The preparation downloads Mathlib caches and needs
network access. The [`lean/README.md`](lean/README.md) identifies the statements
formalized and the assumptions left outside the formalization.

## Manuscript analyses and file locations

Saved `.npz` archives contain named numerical arrays, including candidate grids,
raw draws, selected predictors, and per-run diagnostics. JSON files contain
settings, axis labels, and derived summaries. The smaller deterministic
coefficient-path and predictive-introduction illustrations store their arrays
and settings together in `summary.json`. Figures and tables read these saved
artifacts without training models.

JSON records use finite numbers and explicit `null` values for undefined
statistics. Sampled summaries report finite and missing replicate counts. The
JSON summary checks require matching fields, types, selections, and ordering,
while allowing numerical roundoff with relative tolerance `1e-12` and absolute
tolerance `1e-14`. Derived-array checks use the same tolerances for finite
floating-point values and require exact shapes, data types, and integer
selections. The controlled-study summaries and recalibration diagnostic use the
settings and grids recorded with the saved results.

Retraining can select a different predictor when validation losses differ only
at floating-point precision, even with the same seeds and dependency versions.
The saved draws, selected predictors, and settings support reconstruction of the
reported summaries without repeating these near-tied selections. The
controlled-study protocol describes the selection and tie rules.

The finite-prevalence certificates use `checks/predictive_fixed_q.py`; the
recorded output is `results/certificates/predictive-fixed-q.txt`.
`checks/predictive_theorem.py` and `checks/predictive_review.py` provide the
small-prevalence checks. The limiting proofs and numerical comparisons are in
`paper/main.tex`. `normreg/limiting_oracle.py` implements the scalar solver, and
`checks/oracle_limits.py`, `checks/oracle_infima.py`, and
`checks/oracle_variational.py` check the limiting characterization. Recorded
limiting diagnostics are in `results/oracle-limits/`.

For the finite-prevalence oracle comparisons, `results/oracle-finite/` retains
settings, grids, all four searches, selected risks, rates, stops, and summaries.
`checks/oracle_finite.py` independently constructs observation-level tensor
updates and replays saved selections. Run:

```sh
python -m experiments oracle-finite
python -m checks.oracle_finite --rerun
python scripts/figures/plot_oracle_finite.py
```

Without `--rerun`, the checker replays saved selections without repeating the
full searches. The introductory allocation figure uses the nominal limiting
risks in `results/oracle-finite/summary.json`. Run
`python -m checks.oracle_limits` and `python -m checks.oracle_finite` to check
the scalar solver and saved comparisons, and
`python -m scripts.figures.plot_signal_crossing` to plot them without new
optimization or training.

The common-feature study retains each rate's lowest risk and earliest attaining
stop at every cap in `results/common-block/search.npz`, with settings and
summaries in the same directory. `checks/common_block.py` checks the reduction
and selected results. Run:

```sh
python -m experiments common-block
python -m checks.common_block --saved
python -m experiments.common_block.summarize --check
```

The controlled-study implementation is in `experiments/theory_bridge/`, and its
checks are in `checks/theory_bridge.py`. `results/theory-bridge/` retains
settings, raw feature cells and noise, replacement indices, calibration
summaries, selected predictors and their indices, numerical failure records, and
the machine-readable summary. Summarizing and plotting use saved results without
training.

The exact expected-risk calibration benchmark uses the saved rate factors,
stopping checkpoints, and frozen calibration choices for both fresh arms. It
propagates full second moments, including intercept cross moments, without
simulating training paths. `results/theory-bridge/exact-calibration.npz` retains
every candidate's expected risk, and `exact-calibration.json` records the grids,
minimizing choices, and calibration excesses. The benchmark optimizes the saved
finite family; its expectations are distinct from the evaluation means in Table 1.
Reconstruct it and check it against exhaustive short paths and the baseline's
existing moments:

```sh
python -m experiments exact-calibration
python -m checks.exact_calibration
```

The selection-gain and risk-decomposition analyses retain per-run arrays and
summaries in `results/theory-bridge/selection-gains.npz`,
`selection-gains.json`, `risk-decomposition.npz`, and `risk-decomposition.json`.
Reconstruct the analyses and tables from saved predictors without training, then
check them against independent cell predictions:

```sh
python -m experiments selection-gains
python -m checks.selection_gains
python -m experiments risk-decomposition
python -m checks.risk_decomposition
```

## Rerunning experiments

`python -m experiments --help` lists the named experiment commands. For example:

```sh
python -m experiments oracle-finite
python -m experiments common-block
python -m experiments theory-bridge
```

These commands replace the corresponding saved outputs and can take substantial
time. Run them in a separate extracted copy to retain the supplied results. Use
`--stage run` or `--stage summarize` to separate training from summarization
when an experiment has a separate summary module:

```sh
python -m experiments theory-bridge --stage run
python -m experiments theory-bridge --stage summarize
```

Individual modules remain available as `python -m experiments.<name>.run` and
`python -m experiments.<name>.summarize`. Use these for additional runner
options, such as `python -m experiments.theory_bridge.run --help`. Plotting
reads saved results without retraining.

The archive includes the supplied numerical arrays, including the searches in
`results/common-block/` and `results/oracle-finite/` and the controlled study's
calibration and evaluation shards, for saved-result checks.

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
task experiment:oracle-finite
task experiment:common-block
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

## Container alternative

On Linux with Nix, devenv, and Docker, build and load the local image:

```sh
devenv shell task container:load
```

The image includes the source supplement under `/env`, the pinned Python
dependencies, Task, and LaTeX. Replace `<version>` below with the version in
`pyproject.toml`:

```sh
docker run --rm --network none normreg-multi:<version> task check:workflow
docker run --name normreg-paper --network none normreg-multi:<version> task paper
docker cp normreg-paper:/env/build/main.pdf ./main.pdf
docker rm normreg-paper
```

The loaded image runs these commands without Nix or network access. It also runs
`task check:results` and the experiment tasks. Keep a container until its new
results have been copied from `/env/results`, or mount a writable copy of the
extracted archive at `/env`. Lean's separate `task prepare-lean` step needs
network access to download Mathlib caches.
