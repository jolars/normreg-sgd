"""Expose recorded output paths temporarily without changing frozen sources."""

import fcntl
import os
from contextlib import contextmanager

import frozen_inputs


@contextmanager
def legacy_output_paths():
    """Let frozen readers and writers use their recorded paths during execution."""
    root = frozen_inputs.ROOT
    (root / "build").mkdir(exist_ok=True)
    # Frozen commands share historical paths, so their aliases must not overlap.
    with (root / "build/frozen-outputs.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        links = []
        try:
            for original, relocated in frozen_inputs.RELOCATED_PATHS.items():
                source, destination = root / original, root / relocated
                if source.exists() or source.is_symlink():
                    raise FileExistsError(
                        f"Cannot expose frozen output {original}: the path exists."
                    )
                source.parent.mkdir(parents=True, exist_ok=True)
                destination.parent.mkdir(parents=True, exist_ok=True)
                source.symlink_to(os.path.relpath(destination, source.parent))
                links.append(source)
            yield
        finally:
            for source in reversed(links):
                source.unlink()
