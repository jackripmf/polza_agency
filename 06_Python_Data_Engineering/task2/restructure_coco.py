"""Group COCO images into class folders and update file_name values."""

from __future__ import annotations

import argparse
from pathlib import Path, PurePosixPath
import shutil

from coco_utils import annotations_by_image, folder_for_image, load_json, save_json


def build_index(source_images: Path) -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = {}
    for path in source_images.rglob("*"):
        if path.is_file():
            index.setdefault(path.name, []).append(path)
    return index


def restructure(annotation_file: Path, source_images: Path, output_dir: Path, copy: bool) -> Path:
    data = load_json(annotation_file)
    grouped = annotations_by_image(data)
    categories = {item["id"]: item["name"] for item in data.get("categories", [])}
    index = build_index(source_images)
    seen_destinations: set[Path] = set()

    for image in data.get("images", []):
        basename = PurePosixPath(str(image["file_name"]).replace("\\", "/")).name
        candidates = index.get(basename, [])
        if len(candidates) != 1:
            raise FileNotFoundError(
                f"Expected exactly one source for {basename!r}, found {len(candidates)}"
            )
        folder = folder_for_image(image["id"], grouped, categories)
        relative = Path("images") / folder / basename
        destination = output_dir / relative
        if destination in seen_destinations or destination.exists():
            raise FileExistsError(f"Duplicate destination: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        (shutil.copy2 if copy else shutil.move)(candidates[0], destination)
        seen_destinations.add(destination)
        image["file_name"] = relative.as_posix()

    output_json = output_dir / "updated_annotations.json"
    save_json(data, output_json)
    return output_json


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("annotation_file", type=Path)
    parser.add_argument("source_images", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy instead of moving images (useful for repeatable experiments)",
    )
    args = parser.parse_args()
    print(restructure(args.annotation_file, args.source_images, args.output_dir, args.copy))


if __name__ == "__main__":
    main()

