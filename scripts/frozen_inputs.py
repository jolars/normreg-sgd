"""Hash retired provenance inputs from Git while checking paper inputs on disk."""

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = json.loads((ROOT / "scripts/archived_inputs.json").read_text())
REVISION = ARCHIVE["revision"]
ARCHIVED_PATHS = frozenset(ARCHIVE["paths"])
VERIFIED = set()


def sha256(path):
    path = Path(path).resolve()
    try:
        with path.open("rb") as stream:
            return hashlib.file_digest(stream, "sha256").hexdigest()
    except FileNotFoundError:
        relative = str(path.relative_to(ROOT))
        if relative not in ARCHIVED_PATHS:
            raise
    result = subprocess.run(
        ["git", "show", f"{REVISION}:{relative}"], cwd=ROOT, capture_output=True
    )
    if result.returncode:
        raise RuntimeError(
            f"Cannot verify archived input {relative}. Full Git history is required "
            f"through {REVISION}; use git fetch --unshallow for a shallow clone."
        )
    if not VERIFIED:
        print(
            f"Verifying retired provenance inputs from Git revision {REVISION}.",
            flush=True,
        )
    VERIFIED.add(relative)
    return hashlib.sha256(result.stdout).hexdigest()
