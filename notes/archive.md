# Historical material

On September 22, 2026, historical manuscripts and the broad research backlog
were archived in the neighboring project
[`../../normreg-multi-archive`](../../normreg-multi-archive/README.md), backed
by the private
[jolars/normreg-multi-archive](https://github.com/jolars/normreg-multi-archive)
repository. The source snapshot is active-repository commit
`271c615c2445f57a45ca37d96218484bc0c3363c`.

The archive retains that complete tracked snapshot and its Git history. This
preserves the context needed to build older manuscripts and verify studies that
refer to historical commits. It also contains copies of the two ignored large
robustness outputs locally; fresh clones regenerate those files with
`make prepare-results`. Generated build files and environment caches are not
part of the archive. The archive is a historical record; current work continues
in this repository.

## What moved out of the active tree

- `paper/research-notes.tex`: the longer manuscript, including common-block
  flow, sampling distinctions, joint-budget limits, and shrinkage baselines.
- `paper/proposed-claim.tex`: the earlier one-page claim, superseded by the
  theorem and contribution decision.
- Twenty-six files under `paper/sections/`: the old conference section copies,
  duplicate proof and experiment appendices, and chapters used only by the
  longer manuscript. The current paper already contains its text and appendices
  inline in `paper/main.tex`.
- The former `TODO.md` and `notes/research-plan.md`: completed milestones,
  superseded priorities, and deferred research directions. These remain at their
  original paths in the archive; the active versions now describe this paper.
- Previous project guidance and navigation: preserved as `AGENTS.research.md`
  and `README.research.md` in the archive.

The [archive
manifest](https://github.com/jolars/normreg-multi-archive/blob/main/archive-manifest.json)
lists all 28 removed files and four replaced documents with their original
SHA-256 hashes. Paths are unchanged in the archive except for the two renamed
documents above. The archive's `make paper-notes` and `make paper-claim` targets
retain the historical builds.

## What remains and why

The current manuscript, bibliography, checklist, official template, theory and
review notes, Lean pilot, empirical studies, source data, and figure generators
remain active. The empirical studies still appear in the main paper and its
supplement, including their unfavorable and unresolved results.

Several older calculations also remain because current scripts import them or
frozen study records hash them. For example, later declarations preserve the
shrinkage checker, the block and sampling checks, the joint-budget notes, and
the earlier pilot. Removing or relocating these would break reproducibility even
though their broader research directions are deferred. Preserve their paths,
contents, and recorded hashes. The same restriction applies to the original
`Makefile`; active build changes belong in `GNUmakefile`.

`paper/sections/discrete-dynamics.tex` and `stochastic-gradient.tex` remain as
derivation sources cited by frozen proof notes. Neither is an input to the
current paper. `paper/sections/checklist.tex` is its only section input.

Historical links inside frozen notes identify the original source layout. In
particular, the reviewed `notes/predictive-claim.md` links to the archived
`paper/proposed-claim.tex`. Consult the same path in the archive; do not change
a reviewed file merely to update that link. Active navigation and contribution
notes point to the consolidated manuscript or this inventory.
