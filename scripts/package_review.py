"""Create an anonymous review supplement from the complete release archive."""

import argparse
import copy
import io
import tarfile
import tempfile
from pathlib import Path, PurePosixPath


def package_review(source, output):
    root = output.name.removesuffix(".tar.gz")
    readme_written = False
    with (
        tempfile.TemporaryDirectory(
            prefix=".review-package-", dir=output.parent
        ) as tmp,
        tarfile.open(source, "r|gz") as incoming,
    ):
        temporary = Path(tmp) / output.name
        with tarfile.open(temporary, "w|gz") as outgoing:
            for member in incoming:
                relative = PurePosixPath(*PurePosixPath(member.name).parts[1:])
                if (
                    relative == PurePosixPath("README.md")
                    or ".github" in relative.parts
                ):
                    continue
                target = copy.copy(member)
                target.name = (PurePosixPath(root) / relative).as_posix()
                stream = incoming.extractfile(member) if member.isfile() else None
                if relative == PurePosixPath("REPRODUCING.md"):
                    content = stream.read()
                    outgoing.addfile(target, io.BytesIO(content))
                    target.name = f"{root}/README.md"
                    outgoing.addfile(target, io.BytesIO(content))
                    readme_written = True
                else:
                    outgoing.addfile(target, stream)
        if not readme_written:
            raise ValueError("Release archive is missing REPRODUCING.md.")
        # A failed conversion must not replace an existing review packet.
        temporary.replace(output)
    print(f"Created {output} from {source} with anonymous reproduction instructions.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    package_review(args.source, args.output)
