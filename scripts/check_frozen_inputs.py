"""Check that historical provenance never hides missing or changed paper inputs."""

import hashlib
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

import frozen_inputs
from relocated_outputs import legacy_output_paths


def main():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)

        def git(*args):
            return subprocess.check_output(["git", *args], cwd=root, text=True).strip()

        git("init", "--quiet")
        archived = root / "old.txt"
        retained = root / "paper.txt"
        archived.write_text("historical input\n")
        retained.write_text("paper input\n")
        git("add", ".")
        git(
            "-c",
            "user.name=Provenance test",
            "-c",
            "user.email=test@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--quiet",
            "-m",
            "Fixture",
        )
        revision = git("rev-parse", "HEAD")
        expected = hashlib.sha256(archived.read_bytes()).hexdigest()
        with (
            patch.object(frozen_inputs, "ROOT", root),
            patch.object(frozen_inputs, "REVISION", revision),
            patch.object(frozen_inputs, "ARCHIVED_PATHS", {"old.txt"}),
        ):
            assert frozen_inputs.sha256(archived) == expected
            archived.write_text("changed input\n")
            assert frozen_inputs.sha256(archived) != expected
            archived.unlink()
            assert frozen_inputs.sha256(archived) == expected
            retained.unlink()
            try:
                frozen_inputs.sha256(retained)
            except FileNotFoundError:
                pass
            else:
                raise AssertionError("A missing paper input was hidden by history.")
            with patch.object(frozen_inputs, "REVISION", "0" * 40):
                try:
                    frozen_inputs.sha256(archived)
                except RuntimeError as error:
                    assert "Git history" in str(error)
                else:
                    raise AssertionError("An unavailable archive was accepted.")
            figure = root / "figures/frozen/study/plot.svg"
            figure.parent.mkdir(parents=True)
            figure.write_text("frozen figure\n")
            legacy = root / "results/study/plot.svg"
            with patch.object(
                frozen_inputs,
                "RELOCATED_PATHS",
                {"results/study/plot.svg": "figures/frozen/study/plot.svg"},
            ):
                digest = hashlib.sha256(figure.read_bytes()).hexdigest()
                assert frozen_inputs.sha256(legacy) == digest
                with legacy_output_paths():
                    assert legacy.read_bytes() == figure.read_bytes()
                    assert list(legacy.parent.glob("*.svg")) == [legacy]
                    legacy.write_text("regenerated figure\n")
                    assert figure.read_text() == "regenerated figure\n"
                assert not legacy.is_symlink()
                assert not legacy.exists()
                try:
                    with legacy_output_paths():
                        raise RuntimeError("Interrupted reproduction")
                except RuntimeError:
                    pass
                assert not legacy.is_symlink()
                legacy.write_text("unexpected output\n")
                try:
                    with legacy_output_paths():
                        raise AssertionError("An existing output was overwritten.")
                except FileExistsError:
                    pass
                assert legacy.read_text() == "unexpected output\n"
                legacy.unlink()
                figure.write_text("changed figure\n")
                assert frozen_inputs.sha256(legacy) != digest
                figure.unlink()
                with legacy_output_paths():
                    assert not legacy.exists()
                    legacy.write_text("new figure\n")
                    assert figure.read_text() == "new figure\n"
                figure.unlink()
                try:
                    frozen_inputs.sha256(legacy)
                except FileNotFoundError:
                    pass
                else:
                    raise AssertionError("A missing relocated figure was hidden.")
    print("Historical provenance and missing/changed paper-input checks passed.")


if __name__ == "__main__":
    main()
