# Source supplement

This archive accompanies *Feature Normalization under Finite Training Budgets*.
It contains the manuscript source, experiment and plotting code, source data,
saved numerical arrays and summaries, certificate checkers, Lean proofs, and
pinned environment definitions described in Appendix L. Commands below run from
the extracted archive's root and do not require a Git checkout.

The anonymous review archive uses this document as its root `README.md` and
omits repository CI and publishing documentation. It contains the same
reproduction inputs as the complete source release. Private notes, mock reviews,
instruction files, local environments, Python caches, and Lean's downloaded
dependencies are excluded from both archives.

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
python -m checks.normalization_risk_theorem
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
task check:normalization-risk
task check:oracle-limits
task check:common-block
task check:results
```

The first two commands recompute the certificates without training models. Their
recorded output is in [`results/certificates/`](results/certificates/). The
finite-prevalence checker covers all six continuous parameter regions using
exact rational enclosures and coverage checks. The other commands check the
limiting characterization, finite-prevalence selections, common-feature
extension, and saved empirical losses and selections. `task check-experiments`
runs the broader numerical checks, including small test experiments in temporary
directories.

The analytic limiting proof and its variational consequences are in
[`paper/oracle-proofs.tex`](paper/oracle-proofs.tex). The controlled study's
candidate families, calibration, evaluation, and selection rules are specified
in
[`experiments/theory_bridge/PROTOCOL.md`](experiments/theory_bridge/PROTOCOL.md).
Recorded numerical discrepancies and their interpretation remain in the
manuscript and saved diagnostics; passing the checks does not erase them.

For the formal proof pilot, run `task prepare-lean`, then `task check-lean`. The
preparation downloads Mathlib caches and needs network access. The
[`lean/README.md`](lean/README.md) identifies the statements formalized and the
assumptions left outside the formalization.

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
