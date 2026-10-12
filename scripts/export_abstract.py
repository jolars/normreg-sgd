"""Export the manuscript abstract as plain text for submission forms."""

import argparse
import re
from pathlib import Path


def export_abstract(source, output):
    abstracts = re.findall(
        r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
        source.read_text(encoding="utf-8"),
        flags=re.DOTALL,
    )
    if len(abstracts) != 1:
        raise ValueError("Expected exactly one abstract environment.")
    abstract = abstracts[0].replace("~", " ")
    abstract = " ".join(abstract.split())
    if not abstract:
        raise ValueError("The abstract is empty.")
    # Dropping unknown markup could silently change scientific notation.
    if re.search(r"[\\{}$%&_\^]", abstract):
        raise ValueError(
            "Abstract contains unsupported LaTeX; add an explicit plain-text "
            "conversion before exporting."
        )
    abstract = abstract.replace("---", "—").replace("--", "–")
    abstract = abstract.replace("``", '"').replace("''", '"')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(abstract + "\n", encoding="utf-8")
    print(f"Created {output}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    export_abstract(args.source, args.output)
