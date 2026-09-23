# Feature normalization under finite training budgets

The experiments in this repository support [the manuscript](paper/main.tex),
including its appendices. Run commands from the repository root in
`devenv shell`.

```sh
task paper       # Build the five manuscript figures and build/main.pdf.
task figures     # Export manuscript figures to figures/ from saved summaries.
task check       # Check formatting, provenance, calculations, and the paper.
task verify      # Run the paper's numerical and artifact checks.
```

## Experiments used in the paper

  | Study or calculation                             | Paper location                                   | Check target                                          |
  | ------------------------------------------------ | ------------------------------------------------ | ----------------------------------------------------- |
  | Oracle separation certificates                   | Oracle theorem and its proofs                    | `check-predictive-theorem`, `check-predictive-review` |
  | Shared exact-moment implementation               | Moment recurrences and comparison proofs         | `check-moments`                                       |
  | Finite-grid oracle illustration                  | Introduction and illustration appendix           | `check-predictive-intro`                              |
  | Intermediate signal allocation                   | Signal-allocation figure and appendix            | `check-signal-allocation`                             |
  | Calibrated risk comparisons                      | Fixed-configuration results and proofs           | `check-normalization-risk`                            |
  | Retuning the calibrated anchors                  | Section 5.1 and comparison appendix              | `check-normalization-robustness`                      |
  | Estimated preprocessing and validation selection | Section 5 and practical-selection appendix       | `check-practical-selection`                           |
  | Expanded Mushroom rate search                    | Expanded-search appendix                         | `check-mushroom-rate-search`                          |
  | Damping and variance sensitivity                 | Sensitivity appendix                             | `check-mushroom-sensitivity`                          |
  | Matched four-scaling search                      | Final Mushroom comparison and follow-up appendix | `check-variance-scaling`                              |
  | Numerical discrepancies and clipping             | Final comparison and diagnostic appendix         | `check-review-diagnostics`                            |

Run `task --list` to list the available commands. The corresponding
`reproduce-*` tasks regenerate studies or illustrations intentionally.
Certificate and shared-moment checks compute their results directly.
Reproduction can be expensive and can rewrite results; building the paper reads
saved summaries. `task prepare-results` reconstructs the two ignored robustness
artifacts when missing and checks their frozen hashes.

Some older module names remain because the paper's calculations import them:
`run_joint_interactions.py` supplies exact moments,
`check_joint_interactions.py` supplies exhaustive path enumeration,
`check_discrete_dynamics.py` supplies an independent moment operator, and
`plot_joint_interactions.py` supplies the frozen figure export helper. Their
standalone historical study is no longer part of the build. `results/` contains
numerical arrays, summaries, and provenance records. Manuscript figures are
generated under `figures/`, and the unchanged historical exports used by
artifact audits live in `figures/frozen/`. Editable plotting code lives in
[scripts/figures](scripts/figures/README.md). The generated diagnostic table is
stored in `paper/generated/review-diagnostics.tex`.

## Frozen provenance after cleanup

Recorded numerical results, seeds, declarations, and hash manifests are
unchanged. Those records also hash earlier experiments and notes that are no
longer part of the paper.
[scripts/archived_inputs.json](scripts/archived_inputs.json) lists the retired
inputs and pins the Git revision containing their exact contents. Checks hash
those historical blobs without restoring the files to the working tree. All
retained inputs are checked on disk; deleting or changing one still fails
validation.

Use a clone with full Git history for artifact checks and reproduction. For a
shallow clone, run `git fetch --unshallow`. The Task commands apply the
provenance adapter in
[scripts/frozen_experiment.py](scripts/frozen_experiment.py); invoke those tasks
instead of running frozen study drivers directly. Numerical gate failures
recorded in the original studies remain visible in their audits.

[scripts/relocated_outputs.json](scripts/relocated_outputs.json) maps recorded
figure and table paths to their new locations. The adapter temporarily exposes
the old paths as symlinks while a frozen command runs, then removes them,
including on failure. Frozen commands share a lock so these aliases cannot
overlap. This preserves the hashed source files and manifests while writing
figures under `figures/frozen/`. Missing or changed frozen exports still fail
validation.
