"""Calculate general statistics for one or more CVAT XML files."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable

from xml_utils import dimensions, emit, image_name, load_images, shapes


def extreme(images, value: Callable, mode: str) -> dict:
    target = (max if mode == "max" else min)(value(image) for image in images)
    matches = [image_name(image) for image in images if value(image) == target]
    return {"value": target, "count": len(matches), "example": matches[0]}


def statistics(path: Path) -> dict:
    images = load_images(path)
    annotated = sum(any(True for _ in shapes(image)) for image in images)
    result = {
        "file": path.name,
        "images_total": len(images),
        "images_annotated": annotated,
        "images_unannotated": len(images) - annotated,
        "figures_total": sum(sum(1 for _ in shapes(image)) for image in images),
    }
    if images:
        result["extremes"] = {
            "largest_area": extreme(images, lambda x: dimensions(x)[0] * dimensions(x)[1], "max"),
            "smallest_area": extreme(images, lambda x: dimensions(x)[0] * dimensions(x)[1], "min"),
            "largest_width": extreme(images, lambda x: dimensions(x)[0], "max"),
            "smallest_width": extreme(images, lambda x: dimensions(x)[0], "min"),
            "largest_height": extreme(images, lambda x: dimensions(x)[1], "max"),
            "smallest_height": extreme(images, lambda x: dimensions(x)[1], "min"),
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xml", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    args = parser.parse_args()
    emit([statistics(path) for path in args.xml], args.output)


if __name__ == "__main__":
    main()

