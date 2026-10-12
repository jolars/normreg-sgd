"""Check that a source archive supports the advertised reproduction workflows."""

import argparse
import re
import tarfile
from pathlib import Path, PurePosixPath


def check_archive(path, review=False):
    required = {
        "README.md",
        "REPRODUCING.md",
        "Taskfile.yml",
        "devenv.nix",
        "devenv.yaml",
        "devenv.lock",
        "nix/release.nix",
        "pyproject.toml",
        "uv.lock",
        "normreg/__init__.py",
        "normreg/README.md",
        "normreg/moments.py",
        "normreg/risk.py",
        "normreg/limiting_oracle.py",
        "normreg/common_block.py",
        "experiments/__main__.py",
        "paper/main.tex",
        "paper/references.bib",
        "paper/.latexmkrc",
        "paper/vendor/alt2027/alt2027.cls",
        "paper/generated/selection-gains.tex",
        "paper/generated/risk-decomposition.tex",
        "checks/predictive_fixed_q.py",
        "results/certificates/predictive-fixed-q.txt",
        "results/coefficient-paths/summary.json",
        "results/predictive-intro/summary.json",
        "results/common-block/search.npz",
        "results/common-block/summary.json",
        "results/oracle-finite/search.npz",
        "results/oracle-finite/summary.json",
        "results/theory-bridge/settings.json",
        "results/theory-bridge/summary.json",
        "lean/lakefile.toml",
        "lean/lake-manifest.json",
    }
    excluded = {"__pycache__", ".lake", ".git", "notes", "reviews"}
    instructions = {"agents.md", "agents.override.md", "skill.md", "todo.md"}
    text = {}
    files = set()
    with tarfile.open(path, "r|gz") as archive:
        for member in archive:
            parts = PurePosixPath(member.name).parts
            assert parts and not member.name.startswith("/") and ".." not in parts
            assert member.isfile() or member.isdir(), member.name
            relative = PurePosixPath(*parts[1:])
            assert not excluded.intersection(relative.parts), member.name
            assert relative.name.lower() not in instructions, member.name
            assert relative.suffix not in {".pyc", ".pyo"}, member.name
            if member.isfile():
                name = relative.as_posix()
                assert name not in files, f"Duplicate archive file: {name}"
                files.add(name)
                if name in {"README.md", "REPRODUCING.md", "lean/README.md"}:
                    text[name] = archive.extractfile(member).read().decode()
    assert required <= files, f"Missing reproduction files: {sorted(required - files)}"
    for directory in ("common-block", "oracle-finite", "theory-bridge"):
        assert any(
            name.startswith(f"results/{directory}/") and name.endswith(".npz")
            for name in files
        ), f"Missing saved replay arrays for {directory}"
    for name, content in text.items():
        for link in re.findall(r"\]\(([^)]+)\)", content):
            if "://" in link or link.startswith("#"):
                continue
            target = Path(name).parent / link.split("#", 1)[0]
            # Resolve relative documentation links without using checkout files.
            resolved = []
            for part in target.parts:
                if part == "..":
                    resolved.pop()
                elif part != ".":
                    resolved.append(part)
            target = "/".join(resolved)
            assert target in files or any(
                item.startswith(target.rstrip("/") + "/") for item in files
            ), f"Broken archive link in {name}: {link}"
    if review:
        assert not any(name.startswith(".github/") for name in files)
        assert text["README.md"] == text["REPRODUCING.md"]
        assert "ghcr.io" not in text["README.md"]
    print(f"{path}: {len(files)} files; reproduction contents and links passed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--review", action="store_true")
    args = parser.parse_args()
    check_archive(args.archive, args.review)
