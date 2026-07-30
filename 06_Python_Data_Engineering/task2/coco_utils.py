"""Shared helpers for the COCO dataset scripts."""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import re
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def save_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def canonical_class(name: str) -> str:
    """Convert variant names such as playhood_5 to playhood."""
    return re.sub(r"_\d+$", "", name)


def safe_component(name: str) -> str:
    cleaned = re.sub(r"[^\w.-]+", "_", name, flags=re.UNICODE).strip("._")
    return cleaned or "unnamed"


def annotations_by_image(data: dict) -> dict[int, list[dict]]:
    result: dict[int, list[dict]] = defaultdict(list)
    for annotation in data.get("annotations", []):
        result[annotation["image_id"]].append(annotation)
    return result


def folder_for_image(image_id: int, grouped: dict, category_names: dict[int, str]) -> str:
    classes = sorted(
        {
            safe_component(canonical_class(category_names[a["category_id"]]))
            for a in grouped.get(image_id, [])
            if a.get("category_id") in category_names
        }
    )
    return "_".join(classes) if classes else "no_annotations"

