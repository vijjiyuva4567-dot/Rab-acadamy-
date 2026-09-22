import unittest

from inventory_engine.manager import InventoryManager

from inventory_engine.models import (
    PhysicalProduct,
    DigitalProduct,
)

from inventory_engine.exceptions import (
    DuplicateProductError,
    ProductNotFoundError,
    InvalidQuantityError,
    InsufficientStockError,
)


class TestInventoryManager(unittest.TestCase):

    def setUp(self):
        self.manager = InventoryManager()

        self.phone = PhysicalProduct(
            product_id="P001",
            name="Smartphone",
            price=20000,
            quantity=5,
            weight=0.2,
            shipping_cost=100,
        )

        self.course = DigitalProduct(
            product_id="D001",
            name="Python Course",
            price=1500,
            quantity=10,
            file_size=300,
            download_url="https://example.com/python",
        )

    def test_add_product(self):
        self.manager.add_product(self.phone)

        self.assertEqual(
            self.manager.count(),
            1,
        )

    def test_duplicate_product(self):
        self.manager.add_product(self.phone)

        with self.assertRaises(
            DuplicateProductError
        ):
            self.manager.add_product(self.phone)

    def test_get_product(self):
        self.manager.add_product(self.phone)

        result = self.manager.get_product(
            "P001"
        )

        self.assertEqual(
            result.name,
            "Smartphone",
        )

    def test_product_not_found(self):
        with self.assertRaises(
            ProductNotFoundError
        ):
            self.manager.get_product(
                "UNKNOWN"
            )

    def test_remove_product(self):
        self.manager.add_product(self.phone)

        removed = self.manager.remove_product(
            "P001"
        )

        self.assertEqual(
            removed.product_id,
            "P001",
        )

        self.assertEqual(
            self.manager.count(),
            0,
        )

    def test_remove_missing_product(self):
        with self.assertRaises(
            ProductNotFoundError
        ):
            self.manager.remove_product(
                "UNKNOWN"
            )

    def test_add_stock(self):
        self.manager.add_product(self.phone)

        self.manager.add_stock(
            "P001",
            5,
        )

        self.assertEqual(
            self.phone.quantity,
            10,
        )

    def test_remove_stock(self):
        self.manager.add_product(self.phone)

        self.manager.remove_stock(
            "P001",
            2,
        )

        self.assertEqual(
            self.phone.quantity,
            3,
        )

    def test_invalid_add_stock(self):
        self.manager.add_product(self.phone)

        with self.assertRaises(
            InvalidQuantityError
        ):
            self.manager.add_stock(
                "P001",
                -5,
            )

    def test_invalid_remove_stock(self):
        self.manager.add_product(self.phone)

        with self.assertRaises(
            InvalidQuantityError
        ):
            self.manager.remove_stock(
                "P001",
                0,
            )

    def test_insufficient_stock(self):
        self.manager.add_product(self.phone)

        with self.assertRaises(
            InsufficientStockError
        ):
            self.manager.remove_stock(
                "P001",
                100,
            )

    def test_search_products(self):
        self.manager.add_product(self.phone)
        self.manager.add_product(self.course)

        results = self.manager.search_products(
            "python"
        )

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0].product_id,
            "D001",
        )

    def test_search_by_id(self):
        self.manager.add_product(self.phone)

        results = self.manager.search_products(
            "P001"
        )

        self.assertEqual(
            len(results),
            1,
        )

    def test_search_no_match(self):
        self.manager.add_product(self.phone)

        results = self.manager.search_products(
            "xyz"
        )

        self.assertEqual(
            results,
            [],
        )

    def test_total_inventory_value(self):
        self.manager.add_product(self.phone)
        self.manager.add_product(self.course)

        expected = (
            (20000 * 5 + 100 * 5)
            + (1500 * 10)
        )

        self.assertEqual(
            self.manager.total_inventory_value(),
            expected,
        )

    def test_products_returns_copy(self):
        self.manager.add_product(self.phone)

        products = self.manager.products

        products.clear()

        self.assertEqual(
            self.manager.count(),
            1,
        )

    def test_clear(self):
        self.manager.add_product(self.phone)
        self.manager.add_product(self.course)

        self.manager.clear()

        self.assertEqual(
            self.manager.count(),
            0,
        )


if __name__ == "__main__":
    unittest.main()