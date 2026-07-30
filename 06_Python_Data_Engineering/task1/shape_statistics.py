"""Count box, polygon and points shapes in CVAT XML files."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from xml_utils import SHAPE_TAGS, emit, load_images


def statistics(path: Path) -> dict:
    counts = Counter(
        child.tag
        for image in load_images(path)
        for child in image
        if child.tag in SHAPE_TAGS
    )
    return {
        "file": path.name,
        "shape_types": {tag: counts[tag] for tag in SHAPE_TAGS},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xml", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    emit([statistics(path) for path in args.xml], args.output)


if __name__ == "__main__":
    main()

