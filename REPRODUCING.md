# Source supplement

This archive accompanies *Feature Normalization under Finite Training Budgets*.
It contains the manuscript source, experiment and plotting code, source data,
saved numerical arrays and summaries, certificate checkers, Lean proofs, and
pinned environment definitions described in the source-supplement appendix.
Commands below run from the extracted archive's root and do not require a Git
checkout.

The anonymous review archive uses this document as its root `README.md` and
omits repository CI and publishing documentation. It contains the same
reproduction inputs as the complete source release. Private notes, mock reviews,
instruction files, local environments, Python caches, and Lean's downloaded
dependencies are excluded from both archives.

The manuscript presents the oracle results, their numerical illustrations, the
common-feature extension, and the controlled training study. The archive also
retains earlier fixed-calibration, signal-allocation, synthetic, and Mushroom
investigations with their numerical diagnostics.

## Environment and paper build

Install [Nix](https://nixos.org/download/) and
[devenv](https://devenv.sh/getting-started/), then run:

```sh
devenv shell
task paper
```

The environment supplies Python 3.13, NumPy, SciPy, Matplotlib, Task, LaTeX, and
Lean. `devenv.lock` and `uv.lock` pin the dependencies. Initial setup needs
network access. `task paper` generates figures from saved results and compiles
`build/main.pdf`, including the appendices. It does not run experiments.
`task figures` regenerates the figures alone.

To inspect the numerical claims without Nix or LaTeX, use Python 3.12 or later
and install the Python dependencies:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install 'numpy>=2.0' 'scipy>=1.14' 'matplotlib>=3.10'
python -m checks.predictive_fixed_q
python -m checks.oracle_limits
```

This alternative uses compatible dependency versions; the devenv environment
provides the pinned versions. The Python checks run from the archive root.
Plotting and building the manuscript also require the LaTeX tools supplied by
devenv.

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

## Certificates and saved results

Inside `devenv shell`, run:

```sh
task check:predictive-fixed-q
task check:oracle-limits
task check:common-block
task check:theory-bridge
task check:results
```

The first command recomputes the finite-prevalence certificates without training
models. Its recorded output is in
[`results/certificates/`](results/certificates/). The checker covers all six
continuous parameter regions using exact rational enclosures and coverage
checks. The other commands check the limiting characterization,
finite-prevalence selections, common-feature extension, and saved empirical
losses and selections. `task check-experiments` runs the broader numerical
checks, including small test experiments in temporary directories.

The analytic limiting proof and its variational consequences are in
[`paper/oracle-proofs.tex`](paper/oracle-proofs.tex). The controlled study's
candidate families, calibration, evaluation, and selection rules are specified
in
[`experiments/theory_bridge/PROTOCOL.md`](experiments/theory_bridge/PROTOCOL.md).
Run `task experiment:calibration-sensitivity` to reconstruct the diagnostic that
recalibrates on disjoint halves of the saved calibration shards without
retraining. Its partitions, selected candidates, held-out risks, and summaries
are saved as `results/theory-bridge/calibration-sensitivity.npz` and
`calibration-sensitivity.json`. `task check:calibration-sensitivity` checks the
selection logic and saved diagnostic. The overlapping splits describe
sensitivity at half the original calibration size, not independent repetitions
or confidence intervals.

The earlier fixed-calibration certificates can be recomputed with
`task check:normalization-risk`. Recorded numerical discrepancies in the earlier
synthetic studies remain in the saved diagnostics; passing the checks does not
certify the affected paths.

For the formal proof pilot, run `task prepare-lean`, then `task check-lean`. The
preparation downloads Mathlib caches and needs network access. The
[`lean/README.md`](lean/README.md) identifies the statements formalized and the
assumptions left outside the formalization.

## Manuscript analyses and file locations

The finite-prevalence certificates use `checks/predictive_fixed_q.py`; the
recorded output is `results/certificates/predictive-fixed-q.txt`.
`checks/predictive_theorem.py` and `checks/predictive_review.py` provide the
small-prevalence checks. The limiting proofs and numerical comparisons are in
`paper/oracle-proofs.tex` and `paper/oracle-numerics.tex`.
`experiments/common/limiting_oracle.py` implements the scalar solver, and
`checks/oracle_limits.py`, `checks/oracle_infima.py`, and
`checks/oracle_variational.py` check the limiting characterization. Recorded
limiting diagnostics are in `results/oracle-limits/`.

For the finite-prevalence oracle comparisons, `results/oracle-finite/` retains
settings, grids, all four searches, selected risks, rates, stops, and summaries.
`checks/oracle_finite.py` independently constructs observation-level tensor
updates and replays saved selections. Run:

```sh
task experiment:oracle-finite
task check:oracle-finite -- --rerun
task figure:oracle-finite
```

Without `--rerun`, the checker replays saved selections without repeating the
full searches. The introductory allocation figure uses the nominal limiting
risks in `results/oracle-finite/summary.json`. Run `task check:oracle-limits` to
check the scalar solver and saved comparisons, and `task figure:intro` to plot
them without new optimization or training. The earlier allocation study at fixed
unweighted squared coefficient sum remains in `results/signal-allocation/`, but
is not used in that figure.

The common-feature study retains each rate's lowest risk and earliest attaining
stop at every cap in `results/common-block/search.npz`, with settings and
summaries in the same directory. `checks/common_block.py` checks the reduction
and selected results. Run:

```sh
task experiment:common-block
task check:common-block -- --saved
```

The controlled-study implementation is in `experiments/theory_bridge/`, and its
checks are in `checks/theory_bridge.py`. `results/theory-bridge/` retains
settings, raw feature cells and noise, replacement indices, calibration
summaries, selected predictors and their indices, numerical failure records, and
the machine-readable summary. Summarizing and plotting use saved results without
training.

The selection-gain and risk-decomposition analyses retain per-run arrays and
summaries in `results/theory-bridge/selection-gains.npz`,
`selection-gains.json`, `risk-decomposition.npz`, and `risk-decomposition.json`.
Reconstruct the analyses and tables from saved predictors without training, then
check them against independent cell predictions:

```sh
task experiment:selection-gains
task check:selection-gains
task experiment:risk-decomposition
task check:risk-decomposition
```

## Rerunning experiments

`task --list` lists the experiment commands. For example:

```sh
task experiment:mushroom -- --config rates17
task experiment:synthetic -- --config rates5
task experiment:theory-bridge
```

These commands replace the corresponding saved outputs and can take substantial
time. Run them in a separate extracted copy to retain the supplied results. The
`:run` and `:summarize` tasks separate training from summarization. Plotting
reads saved results without retraining.

Two optional large exact-risk outputs are omitted from both archives:
`results/exact-risk/paths.npz` and `results/exact-risk/summary.json`. They are
not needed for the paper build or the checks listed above. To generate and check
them explicitly, run:

```sh
task experiment:exact-risk
task check:exact-risk-results
```

All other supplied numerical arrays, including `results/common-block/search.npz`
and the Mushroom, synthetic, and controlled study shards, remain in the archive
for saved-result checks.
