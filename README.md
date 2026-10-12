# Feature Normalization under Finite Training Budgets

Code, data, and saved results for [*Feature Normalization under Finite Training
Budgets*](paper/main.tex).

Standardizing a rare feature can help stochastic gradient descent learn its
effect before the training budget runs out, but it also changes the noise cost
of learning. The paper asks which scaling achieves lower prediction risk in the
rare subgroup when standardized and unscaled training each optimize their
constant learning rate and stopping time under the same observation cap.

For two independent binary features, we characterize both optimized risks as
rare prevalence vanishes while the expected number of rare observations remains
finite. With positive noise, the preferred scaling changes exactly once as
signal moves from the common feature to the rare feature at fixed initial
subgroup risk. Separate finite-prevalence bounds establish an advantage for
standardization when the rare signal dominates and for unscaled training when
the common signal dominates.

The theory concerns final iterates with population preprocessing and fresh
observations. Exact-moment searches assess the limiting approximation at finite
prevalence. A controlled study examines observation reuse, estimated
preprocessing, and intercept fitting: both orderings persist when tuning choices
are fixed before evaluation, but selecting a predictor after observing training
can reverse an ordering, even with exact population risk.

## Paper and supporting material

- [Manuscript source](paper/main.tex), including the proofs and appendices.
- [Reproduction guide](REPRODUCING.md), with commands for the certificates,
  experiments, saved analyses, figures, and paper build.
- [Controlled-study protocol](experiments/theory_bridge/PROTOCOL.md), specifying
  the candidate families, calibration, evaluation, and selection rules.
- [Lean verification](lean/README.md), describing the formalized bounds and
  their scope.

The main experiment outputs are:

  | Experiment          | Purpose                                               | Saved results                                            |
  | ------------------- | ----------------------------------------------------- | -------------------------------------------------------- |
  | `coefficient-paths` | Learning paths to a shared least-squares solution     | [results/coefficient-paths/](results/coefficient-paths/) |
  | `predictive-intro`  | Finite-grid illustration of the two risk orderings    | [results/predictive-intro/](results/predictive-intro/)   |
  | `oracle-finite`     | Finite-prevalence comparisons with the limiting risks | [results/oracle-finite/](results/oracle-finite/)         |
  | `common-block`      | Extension to several common features                  | [results/common-block/](results/common-block/)           |
  | `theory-bridge`     | Controlled departures from the theoretical setup      | [results/theory-bridge/](results/theory-bridge/)         |

## Reproducing the results

Run commands from the repository or extracted source archive root. Experiments
and numerical checks run on the CPU and require Python 3.12 or later, NumPy,
SciPy, and Matplotlib. To install the recorded dependency versions with
[uv](https://docs.astral.sh/uv/getting-started/installation/):

```sh
uv sync --locked --no-dev --python 3.13
. .venv/bin/activate
export OPENBLAS_NUM_THREADS=1
```

Python 3.13 and the thread setting match the development environment and saved
experiments. The [reproduction guide](REPRODUCING.md#python-environment) also
provides a pip setup.

To check the finite-prevalence certificates, limiting formulas, and saved
controlled-study results without retraining:

```sh
python -m checks.predictive_fixed_q
python -m checks.oracle_limits
python -m checks.theory_bridge --saved
```

To summarize saved results or rerun an experiment:

```sh
python -m experiments theory-bridge --stage summarize
python -m experiments theory-bridge
```

Use `python -m experiments --help` to list available experiments and analyses.
Rerunning an experiment can take substantial time and replaces its saved
outputs. Use a separate copy to retain the supplied results. Summarizing and
plotting read saved outputs without retraining. The [reproduction
guide](REPRODUCING.md) gives the full workflow and maps each analysis to its
files and checks.

## Building the paper

With [Nix](https://nixos.org/download/) and
[devenv](https://devenv.sh/getting-started/) installed, the pinned environment
supplies Python dependencies, LaTeX, and Task:

```sh
devenv shell
task paper
```

The output is `build/main.pdf`. The build regenerates manuscript figures from
saved results without launching experiments.

For a build without Nix, use the Python environment above and install a TeX
distribution with `latex`, `dvipng`, Times fonts, `latexmk`, and `pdflatex`;
`devenv.nix` lists the required TeX packages. Follow the [figure and paper build
commands](REPRODUCING.md#figures-and-paper-build). The [figure
guide](scripts/figures/README.md) describes individual plots and their outputs.

Development, validation, and release instructions are in
[CONTRIBUTING.md](CONTRIBUTING.md).
