"""Check that historical provenance never hides missing or changed paper inputs."""

import hashlib
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

import frozen_inputs


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
    print("Historical provenance and missing/changed paper-input checks passed.")


if __name__ == "__main__":
    main()
