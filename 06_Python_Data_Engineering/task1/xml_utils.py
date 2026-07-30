"""Shared helpers for CVAT XML annotation files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable
import xml.etree.ElementTree as ET

SHAPE_TAGS = ("box", "polygon", "points")


def load_images(path: Path) -> list[ET.Element]:
    """Parse a CVAT XML file and return all image elements."""
    return list(ET.parse(path).getroot().iterfind("image"))


def image_name(image: ET.Element) -> str:
    return image.get("name", "<без имени>")


def dimensions(image: ET.Element) -> tuple[int, int]:
    return int(image.get("width", 0)), int(image.get("height", 0))


def shapes(image: ET.Element) -> Iterable[ET.Element]:
    for tag in SHAPE_TAGS:
        yield from image.findall(tag)


def emit(data: Any, output: Path | None = None) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    print(text)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")

