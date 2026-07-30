"""Convert restructured COCO bounding boxes to YOLO text labels."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil

from coco_utils import annotations_by_image, load_json, save_json


def clipped_yolo_bbox(bbox: list[float], image_width: float, image_height: float) -> tuple[list[float], bool]:
    x, y, width, height = map(float, bbox)
    was_clipped = x < 0 or y < 0 or x + width > image_width or y + height > image_height
    x1, y1 = max(0.0, x), max(0.0, y)
    x2, y2 = min(float(image_width), x + width), min(float(image_height), y + height)
    if x2 <= x1 or y2 <= y1:
        raise ValueError(f"Bounding box has no area inside image: {bbox}")
    clipped = [x1, y1, x2 - x1, y2 - y1]
    values = [
        (x1 + x2) / 2 / image_width,
        (y1 + y2) / 2 / image_height,
        (x2 - x1) / image_width,
        (y2 - y1) / image_height,
    ]
    return values, was_clipped


def convert(annotation_file: Path, dataset_root: Path, output_dir: Path) -> dict:
    data = load_json(annotation_file)
    categories = sorted(data.get("categories", []), key=lambda item: item["id"])
    class_ids = {item["id"]: index for index, item in enumerate(categories)}
    grouped = annotations_by_image(data)
    clipped_annotations: list[int] = []
    output_dir.mkdir(parents=True, exist_ok=True)

    for image in data.get("images", []):
        source = dataset_root / Path(image["file_name"])
        if not source.is_file():
            raise FileNotFoundError(source)
        folder = source.parent.name
        target_image = output_dir / folder / source.name
        target_image.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target_image)
        rows = []
        for annotation in grouped.get(image["id"], []):
            values, clipped = clipped_yolo_bbox(
                annotation["bbox"], image["width"], image["height"]
            )
            if clipped:
                clipped_annotations.append(annotation["id"])
            rows.append(
                f"{class_ids[annotation['category_id']]} "
                + " ".join(f"{value:.8f}" for value in values)
            )
        target_image.with_suffix(".txt").write_text(
            "\n".join(rows) + ("\n" if rows else ""), encoding="utf-8"
        )

    mapping = {
        "classes": [
            {"yolo_id": class_ids[item["id"]], "coco_id": item["id"], "name": item["name"]}
            for item in categories
        ],
        "clipped_annotation_ids": clipped_annotations,
    }
    save_json(mapping, output_dir / "classes.json")
    (output_dir / "classes.txt").write_text(
        "\n".join(item["name"] for item in categories) + "\n", encoding="utf-8"
    )
    return mapping


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("annotation_file", type=Path)
    parser.add_argument("dataset_root", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    result = convert(args.annotation_file, args.dataset_root, args.output_dir)
    print(f"Done. Classes: {len(result['classes'])}; clipped boxes: {len(result['clipped_annotation_ids'])}")


if __name__ == "__main__":
    main()
