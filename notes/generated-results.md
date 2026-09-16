# Generated result storage

On September 16, 2026, two generated robustness artifacts were removed from the
unpublished Git history because they exceeded GitHub's file-size limit:

- `results/normalization-robustness/paths.npz`: 461,922,788 bytes.
- `results/normalization-robustness/summary.json`: 213,219,462 bytes.

Both files remain available locally and are ignored by Git. The repository does
not use Git LFS. Published history through `a47cbfb` is unchanged. The removal
changes the IDs of six subsequent unpublished commits, including the baselines
recorded in the practical-selection, Mushroom rate-search, and scaling
sensitivity studies.

## Recreate local artifacts

Inside `devenv shell`, run:

```sh
make prepare-results
```

The relevant check and reproduction targets run this prerequisite automatically.
It regenerates missing moment paths with the frozen runner and reconstructs the
summary from the saved specification, boundary probes, paired simulation, and
simulation summary. It does not rerun the Monte Carlo experiment or change any
tracked result. The covariance gate failure and its conditional-absence
investigation are preserved.

Each recreated file must match its original SHA-256 hash before installation.
Existing files are checked and never replaced automatically if their hashes
differ. Temporary outputs live under the ignored `build/` directory. Use the
pinned development environment to reproduce the original bytes.

## Preserve the frozen studies

The source files, numerical results, protocols, declarations, timestamps, and
recorded hashes are unchanged. Some frozen scripts originally used `git ls-tree`
and `git diff` against unpublished baseline commits. Those references cannot be
resolved from a fresh clone after removing the large files from history.

The Make targets now invoke those scripts through
`scripts/frozen_experiment.py`. This launcher replaces only their
`preserved_hashes` functions: it computes every preserved file's SHA-256 hash
and compares it with the original recorded value. It uses the practical study's
`synthetic.json` preservation map and the two later studies' `declaration.json`
maps. Missing files and changed bytes fail verification. The original source and
declaration checks still run, and no numerical or selection functions are
replaced. The recorded commit IDs remain historical provenance, not references
required by the launcher.

The robustness study's earlier published baseline remains available. CI uses a
full checkout for its original Git-based checks. A pre-commit size check rejects
new ordinary Git files larger than 100 MiB.
