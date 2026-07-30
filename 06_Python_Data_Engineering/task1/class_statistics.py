"""Count annotation labels in one or more CVAT XML files."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from xml_utils import emit, load_images, shapes


def statistics(path: Path) -> dict:
    counts = Counter(
        shape.get("label", "<без метки>")
        for image in load_images(path)
        for shape in shapes(image)
    )
    return {
        "file": path.name,
        "unique_labels": len(counts),
        "labels": dict(sorted(counts.items())),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xml", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    emit([statistics(path) for path in args.xml], args.output)


if __name__ == "__main__":
    main()

