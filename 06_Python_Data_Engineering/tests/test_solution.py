from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "task1"))
sys.path.insert(0, str(ROOT / "task2"))

from coco_to_yolo import clipped_yolo_bbox  # noqa: E402
from coco_utils import canonical_class, folder_for_image  # noqa: E402
from modify_annotations import modify, normalized_name  # noqa: E402
from validate_dataset import validate  # noqa: E402


class XmlTests(unittest.TestCase):
    def test_normalized_name(self):
        self.assertEqual(normalized_name("ftp/folder/photo.jpg"), "photo.png")
        self.assertEqual(normalized_name(r"C:\folder\photo.jpeg"), "photo.png")

    def test_modify_reverses_existing_ids_without_overwriting_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "sample.xml"
            source.write_text(
                '<annotations><image id="7" name="a/a.jpg"/>'
                '<image id="2" name="b\\b.jpeg"/></annotations>',
                encoding="utf-8",
            )
            destination = modify(source, root / "out")
            images = ET.parse(destination).getroot().findall("image")
            self.assertEqual([item.get("id") for item in images], ["2", "7"])
            self.assertEqual([item.get("name") for item in images], ["a.png", "b.png"])
            self.assertIn('id="7"', source.read_text(encoding="utf-8"))


class CocoTests(unittest.TestCase):
    def test_class_variant_and_multilabel_folder(self):
        grouped = {1: [{"category_id": 7}, {"category_id": 2}]}
        names = {7: "playhood_5", 2: "dog_1"}
        self.assertEqual(canonical_class("playhood_5"), "playhood")
        self.assertEqual(folder_for_image(1, grouped, names), "dog_playhood")
        self.assertEqual(folder_for_image(99, grouped, names), "no_annotations")

    def test_bbox_normalization_and_clipping(self):
        values, clipped = clipped_yolo_bbox([10, 20, 30, 40], 100, 100)
        self.assertFalse(clipped)
        self.assertEqual(values, [0.25, 0.4, 0.3, 0.4])
        values, clipped = clipped_yolo_bbox([-10, 0, 20, 20], 100, 100)
        self.assertTrue(clipped)
        self.assertEqual(values, [0.05, 0.1, 0.1, 0.2])

    def test_validator_reports_missing_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            annotations = root / "data.json"
            annotations.write_text(json.dumps({
                "images": [{"id": 1, "file_name": "missing.png", "width": 10, "height": 10}],
                "categories": [{"id": 1, "name": "item"}],
                "annotations": [{"id": 1, "image_id": 2, "category_id": 9, "bbox": [0, 0, 1, 1]}],
            }), encoding="utf-8")
            report = validate(annotations, root)
            self.assertFalse(report["valid"])
            self.assertEqual(report["counts"]["errors"], 3)


if __name__ == "__main__":
    unittest.main()

