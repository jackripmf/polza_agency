"""Validate COCO links, categories, image files and bounding boxes."""

from __future__ import annotations

import argparse
from pathlib import Path

from coco_utils import annotations_by_image, load_json, save_json


def validate(annotation_file: Path, dataset_root: Path) -> dict:
    data = load_json(annotation_file)
    images = data.get("images", [])
    annotations = data.get("annotations", [])
    categories = data.get("categories", [])
    image_ids = {item.get("id") for item in images}
    category_ids = {item.get("id") for item in categories}
    grouped = annotations_by_image(data)
    errors: list[dict] = []
    warnings: list[dict] = []

    for image in images:
        path = dataset_root / Path(str(image.get("file_name", "")))
        if not path.is_file():
            errors.append({"type": "missing_file", "image_id": image.get("id"), "path": str(path)})

    dimensions = {item.get("id"): (item.get("width"), item.get("height")) for item in images}
    for annotation in annotations:
        aid = annotation.get("id")
        image_id = annotation.get("image_id")
        category_id = annotation.get("category_id")
        if image_id not in image_ids:
            errors.append({"type": "unknown_image_id", "annotation_id": aid, "image_id": image_id})
        if category_id not in category_ids:
            errors.append({"type": "unknown_category_id", "annotation_id": aid, "category_id": category_id})
        bbox = annotation.get("bbox")
        if image_id in dimensions and isinstance(bbox, list) and len(bbox) == 4:
            x, y, width, height = bbox
            image_width, image_height = dimensions[image_id]
            if width <= 0 or height <= 0:
                errors.append({"type": "non_positive_bbox", "annotation_id": aid, "bbox": bbox})
            elif x < 0 or y < 0 or x + width > image_width or y + height > image_height:
                warnings.append({
                    "type": "bbox_outside_image",
                    "annotation_id": aid,
                    "image_id": image_id,
                    "bbox": bbox,
                    "image_size": [image_width, image_height],
                })

    report = {
        "valid": not errors,
        "counts": {
            "images": len(images),
            "annotations": len(annotations),
            "categories": len(categories),
            "empty_images": sum(not grouped.get(item.get("id")) for item in images),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "errors": errors,
        "warnings": warnings,
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("annotation_file", type=Path)
    parser.add_argument("dataset_root", type=Path)
    parser.add_argument("--output", type=Path, default=Path("dataset_report.json"))
    args = parser.parse_args()
    report = validate(args.annotation_file, args.dataset_root)
    save_json(report, args.output)
    print(args.output)
    raise SystemExit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()

