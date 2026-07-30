"""Reverse image IDs and normalize image names in CVAT XML files."""

from __future__ import annotations

import argparse
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET


def normalized_name(value: str) -> str:
    basename = PurePosixPath(value.replace("\\", "/")).name
    return str(Path(basename).with_suffix(".png"))


def modify(source: Path, output_dir: Path) -> Path:
    tree = ET.parse(source)
    images = list(tree.getroot().iterfind("image"))
    original_ids = [image.get("id", "") for image in images]
    for image, new_id in zip(images, reversed(original_ids)):
        image.set("id", new_id)
        image.set("name", normalized_name(image.get("name", "image")))

    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{source.stem}_modified{source.suffix}"
    try:
        ET.indent(tree, space="  ")
    except AttributeError:  # pragma: no cover - Python < 3.9
        pass
    tree.write(destination, encoding="utf-8", xml_declaration=True)
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xml", nargs="+", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    args = parser.parse_args()
    for source in args.xml:
        print(modify(source, args.output_dir))


if __name__ == "__main__":
    main()

