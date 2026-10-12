"""Package and compile the manuscript sources for an arXiv upload."""

import argparse
import os
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path


def package_arxiv(output):
    paper = Path("paper").resolve()
    build = Path("build").resolve()
    figures = paper.parent / "figures"
    vendor = paper / "vendor" / "alt2027"
    files = {
        Path("main.tex"): paper / "main.tex",
        Path("main.bbl"): build / "main.bbl",
        Path("references.bib"): paper / "references.bib",
    }
    # The recorder lists the files actually used, excluding obsolete figures.
    for line in (build / "main.fls").read_text().splitlines():
        if not line.startswith("INPUT "):
            continue
        source = (paper / line.removeprefix("INPUT ")).resolve()
        if source.is_relative_to(paper) and source.suffix in {
            ".tex",
            ".cls",
            ".sty",
            ".bst",
        }:
            target = (
                Path(source.name)
                if source.is_relative_to(vendor)
                else source.relative_to(paper)
            )
        elif source.is_relative_to(figures):
            target = Path("figures") / source.relative_to(figures)
        else:
            continue
        files[target] = source

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".arxiv-package-", dir=output.parent
    ) as tmp:
        staging = Path(tmp).resolve() / "sources"
        for target, source in files.items():
            destination = staging / target
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source.suffix == ".tex":
                # arXiv compiles from the submission root, outside paper/.
                content = source.read_text().replace("../figures/", "figures/")
                if target == Path("main.tex"):
                    # Omit proceedings branding only in the staged preprint.
                    if content.count(r"\maketitle") != 1:
                        raise ValueError(
                            r"Expected exactly one \maketitle in main.tex."
                        )
                    content = content.replace(
                        r"\maketitle",
                        "\\maketitle\n\\thispagestyle{plain}",
                        1,
                    )
                destination.write_text(content)
            else:
                shutil.copy2(source, destination)

        environment = os.environ.copy()
        for variable in ("TEXINPUTS", "BIBINPUTS", "BSTINPUTS"):
            environment.pop(variable, None)
        # Python's shared libraries can conflict with standalone TeX binaries.
        environment.pop("LD_LIBRARY_PATH", None)
        subprocess.run(
            [
                "latexmk",
                "-norc",
                "-pdf",
                "-bibtex-",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-file-line-error",
                "main.tex",
            ],
            cwd=staging,
            env=environment,
            check=True,
        )
        temporary = Path(tmp) / output.name
        with tarfile.open(temporary, "w:gz") as archive:
            for target in sorted(files):
                archive.add(staging / target, arcname=target.as_posix())
        shutil.copy2(staging / "main.pdf", output.with_suffix("").with_suffix(".pdf"))
        # Publish the archive only after its sources compile successfully.
        temporary.replace(output)
    print(f"Created {output} with {len(files)} source and figure files.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    package_arxiv(args.output)
