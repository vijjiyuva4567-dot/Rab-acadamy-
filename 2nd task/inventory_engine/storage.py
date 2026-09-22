import csv
import json
from pathlib import Path

from .exceptions import StorageError
from .models import PhysicalProduct, DigitalProduct


class InventoryStorage:
    """
    Handles persistence of inventory data in JSON and CSV formats.
    """

    @staticmethod
    def save_json(manager, file_path):
        path = Path(file_path)

        try:
            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            data = [
                product.to_dict()
                for product in manager.list_products()
            ]

            with path.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    data,
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

        except (OSError, TypeError, ValueError) as exc:
            raise StorageError(
                f"Failed to save JSON data: {exc}"
            ) from exc

    @staticmethod
    def load_json(file_path):
        path = Path(file_path)

        try:
            with path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(
                f"Failed to load JSON data: {exc}"
            ) from exc

        if not isinstance(data, list):
            raise StorageError(
                "JSON inventory data must be a list."
            )

        return InventoryStorage._create_manager(data)

    @staticmethod
    def save_csv(manager, file_path):
        path = Path(file_path)

        fieldnames = [
            "product_id",
            "name",
            "price",
            "quantity",
            "product_type",
            "weight",
            "shipping_cost",
            "file_size",
            "download_url",
        ]

        try:
            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with path.open(
                "w",
                newline="",
                encoding="utf-8",
            ) as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=fieldnames,
                )

                writer.writeheader()

                for product in manager.list_products():
                    data = product.to_dict()

                    row = {
                        field: data.get(field, "")
                        for field in fieldnames
                    }

                    writer.writerow(row)

        except (OSError, csv.Error) as exc:
            raise StorageError(
                f"Failed to save CSV data: {exc}"
            ) from exc

    @staticmethod
    def load_csv(file_path):
        path = Path(file_path)

        try:
            with path.open(
                "r",
                newline="",
                encoding="utf-8",
            ) as file:
                reader = csv.DictReader(file)
                data = list(reader)

        except (OSError, csv.Error) as exc:
            raise StorageError(
                f"Failed to load CSV data: {exc}"
            ) from exc

        return InventoryStorage._create_manager(data)

    @staticmethod
    def _create_manager(data):
        """
        Convert dictionaries into Product objects.
        """

        from .manager import InventoryManager

        manager = InventoryManager()

        try:
            for item in data:
                product_type = str(
                    item.get("product_type", "")
                ).lower()

                if product_type == "physical":
                    product = PhysicalProduct(
                        product_id=item["product_id"],
                        name=item["name"],
                        price=float(item["price"]),
                        quantity=int(item["quantity"]),
                        weight=float(item["weight"]),
                        shipping_cost=float(
                            item.get("shipping_cost", 0)
                            or 0
                        ),
                    )

                elif product_type == "digital":
                    product = DigitalProduct(
                        product_id=item["product_id"],
                        name=item["name"],
                        price=float(item["price"]),
                        quantity=int(item["quantity"]),
                        file_size=float(item["file_size"]),
                        download_url=item["download_url"],
                    )

                else:
                    raise StorageError(
                        f"Unknown product type: {product_type}"
                    )

                manager.add_product(product)

        except (KeyError, TypeError, ValueError) as exc:
            raise StorageError(
                f"Invalid stored product data: {exc}"
            ) from exc

        return manager