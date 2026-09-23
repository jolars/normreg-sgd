# Feature normalization under finite training budgets

The experiments in this repository support [the manuscript](paper/main.tex),
including its appendices. Run commands from the repository root in
`devenv shell`.

```sh
make paper       # Build the five manuscript figures and build/main.pdf.
make figures     # Build just the manuscript figures from saved summaries.
make check       # Check formatting, provenance, calculations, and the paper.
make verify      # Run the paper's numerical and artifact checks.
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

The corresponding `reproduce-*` targets regenerate studies or illustrations
intentionally. Certificate and shared-moment checks compute their results
directly. Reproduction can be expensive and can rewrite results; building the
paper reads saved summaries. `make prepare-results` reconstructs the two ignored
robustness artifacts when missing and checks their frozen hashes.

Some older module names remain because the paper's calculations import them:
`run_joint_interactions.py` supplies exact moments,
`check_joint_interactions.py` supplies exhaustive path enumeration,
`check_discrete_dynamics.py` supplies an independent moment operator, and
`plot_joint_interactions.py` supplies the frozen figure export helper. Their
standalone historical study is no longer part of the build. Archived plots
within retained studies remain inputs to their artifact audits; editable
manuscript plots live in [scripts/figures](scripts/figures/README.md).

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
shallow clone, run `git fetch --unshallow`. The `make` targets apply the
provenance adapter in
[scripts/frozen_experiment.py](scripts/frozen_experiment.py); invoke those
targets instead of running frozen study drivers directly. Numerical gate
failures recorded in the original studies remain visible in their audits.
