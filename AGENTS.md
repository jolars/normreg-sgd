# Project guidance

This is a research manuscript with supporting Python calculations. It studies
normalization and shrinkage for correlated binary features. The bivariate
results are the starting point; the general rare-feature sampling theorem and
novelty assessment are research objectives.

## Sources and mathematical conventions

- `paper/main.tex` and `paper/sections/` are the working manuscript.
  `paper/references.bib` contains the bibliography.
- `notes/research-plan.md` records the research program and the scope of
  candidate claims. `notes/two-feature-investigation.md` preserves the initial
  derivations; its references to the original paper concern the earlier
  `normreg` project.
- `experiments/check_two_features.py` contains exact region integration and
  independent numerical checks. This is a script project, not an installable
  Python library.
- The paper uses the averaged loss and $C = X_c^\top X_c/n$, while the numerical
  script uses $G = nC$. Keep $\lambda_1 = nt$ and $\lambda_2 = nr$ consistent.
  Report coefficients on the original feature scale.
- Distinguish noiseless active-sign formulas, unconditional Gaussian moments,
  formal Gram-matrix limits, and asymptotics of actual binary samples. A
  selected region uses truncated Gaussian moments. Binary simulations must
  satisfy the joint-cell probability bounds.

## Development and validation

Enter `devenv shell` before running these commands:

```sh
make paper
make check-python
make check-quick
make check
```

`make check-python` checks experiment formatting and lint. `make check-quick`
also checks repository configuration and Markdown, builds the paper, and runs
the smaller numerical validation. `make check` runs the full validation. The
mathematical checks use assertions, so run ordinary Python without `-O`.

Use `make format` for Markdown, Nix, and Python formatting. The devenv shell
uses Nix's Ruff executable and installs runtime Python dependencies from
`uv.lock`. The optional uv development group supports environments outside
NixOS.

## Generated files and releases

`build/` contains generated LaTeX output and is ignored. Regenerate
`results/two-feature-check.json` with `make reproduce`; do not hand-edit the
numerical values or provenance. `make verify` validates without rewriting it.
Refresh `uv.lock` with uv and `devenv.lock` with devenv when changing inputs.
Keep the Panache version in the Markdown CI job aligned with the devenv package
when updating the Nix inputs.

Versionary manages the version in `pyproject.toml`, its lockfile update, and
`CHANGELOG.md` once releases are enabled. Do not hand-edit that changelog. The
release job requires `ENABLE_RELEASES=true` and `RELEASE_TOKEN`; package
publication and a license have not been configured.
