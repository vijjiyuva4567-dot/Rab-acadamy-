import csv
import json
import tempfile
import unittest

from pathlib import Path

from inventory_engine.manager import InventoryManager

from inventory_engine.models import (
    PhysicalProduct,
    DigitalProduct,
)

from inventory_engine.storage import InventoryStorage

from inventory_engine.exceptions import (
    StorageError,
)


class TestInventoryStorage(unittest.TestCase):

    def setUp(self):
        self.manager = InventoryManager()

        self.manager.add_product(
            PhysicalProduct(
                product_id="P001",
                name="Laptop",
                price=50000,
                quantity=5,
                weight=1.5,
                shipping_cost=500,
            )
        )

        self.manager.add_product(
            DigitalProduct(
                product_id="D001",
                name="Python Course",
                price=2000,
                quantity=10,
                file_size=500,
                download_url="https://example.com/python",
            )
        )

        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_load_json(self):
        file_path = (
            Path(self.temp_dir.name)
            / "inventory.json"
        )

        InventoryStorage.save_json(
            self.manager,
            file_path,
        )

        loaded = InventoryStorage.load_json(
            file_path
        )

        self.assertEqual(
            loaded.count(),
            2,
        )

        laptop = loaded.get_product(
            "P001"
        )

        self.assertEqual(
            laptop.name,
            "Laptop",
        )

        self.assertEqual(
            laptop.quantity,
            5,
        )

    def test_save_and_load_csv(self):
        file_path = (
            Path(self.temp_dir.name)
            / "inventory.csv"
        )

        InventoryStorage.save_csv(
            self.manager,
            file_path,
        )

        loaded = InventoryStorage.load_csv(
            file_path
        )

        self.assertEqual(
            loaded.count(),
            2,
        )

        course = loaded.get_product(
            "D001"
        )

        self.assertEqual(
            course.name,
            "Python Course",
        )

    def test_json_file_content(self):
        file_path = (
            Path(self.temp_dir.name)
            / "inventory.json"
        )

        InventoryStorage.save_json(
            self.manager,
            file_path,
        )

        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        self.assertEqual(
            len(data),
            2,
        )

        self.assertEqual(
            data[0]["product_id"],
            "P001",
        )

    def test_csv_file_content(self):
        file_path = (
            Path(self.temp_dir.name)
            / "inventory.csv"
        )

        InventoryStorage.save_csv(
            self.manager,
            file_path,
        )

        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            rows = list(
                csv.DictReader(file)
            )

        self.assertEqual(
            len(rows),
            2,
        )

    def test_invalid_json(self):
        file_path = (
            Path(self.temp_dir.name)
            / "invalid.json"
        )

        file_path.write_text(
            "{ invalid json",
            encoding="utf-8",
        )

        with self.assertRaises(
            StorageError
        ):
            InventoryStorage.load_json(
                file_path
            )

    def test_json_wrong_format(self):
        file_path = (
            Path(self.temp_dir.name)
            / "wrong.json"
        )

        file_path.write_text(
            '{"name": "wrong"}',
            encoding="utf-8",
        )

        with self.assertRaises(
            StorageError
        ):
            InventoryStorage.load_json(
                file_path
            )

    def test_missing_json_file(self):
        file_path = (
            Path(self.temp_dir.name)
            / "missing.json"
        )

        with self.assertRaises(
            StorageError
        ):
            InventoryStorage.load_json(
                file_path
            )

    def test_unknown_product_type(self):
        file_path = (
            Path(self.temp_dir.name)
            / "unknown.json"
        )

        data = [
            {
                "product_id": "X001",
                "name": "Unknown",
                "price": 100,
                "quantity": 1,
                "product_type": "unknown",
            }
        ]

        file_path.write_text(
            json.dumps(data),
            encoding="utf-8",
        )

        with self.assertRaises(
            StorageError
        ):
            InventoryStorage.load_json(
                file_path
            )


if __name__ == "__main__":
    unittest.main()