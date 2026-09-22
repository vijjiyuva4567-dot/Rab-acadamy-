import unittest

from inventory_engine.models import (
    Product,
    PhysicalProduct,
    DigitalProduct,
)

from inventory_engine.exceptions import (
    InvalidProductError,
    InvalidQuantityError,
    InsufficientStockError,
)


class TestPhysicalProduct(unittest.TestCase):

    def setUp(self):
        self.product = PhysicalProduct(
            product_id="P001",
            name="Laptop",
            price=50000,
            quantity=10,
            weight=1.5,
            shipping_cost=500,
        )

    def test_product_properties(self):
        self.assertEqual(
            self.product.product_id,
            "P001",
        )

        self.assertEqual(
            self.product.name,
            "Laptop",
        )

        self.assertEqual(
            self.product.price,
            50000,
        )

        self.assertEqual(
            self.product.quantity,
            10,
        )

    def test_add_stock(self):
        self.product.add_stock(5)

        self.assertEqual(
            self.product.quantity,
            15,
        )

    def test_remove_stock(self):
        self.product.remove_stock(3)

        self.assertEqual(
            self.product.quantity,
            7,
        )

    def test_insufficient_stock(self):
        with self.assertRaises(
            InsufficientStockError
        ):
            self.product.remove_stock(100)

    def test_invalid_quantity(self):
        with self.assertRaises(
            InvalidQuantityError
        ):
            self.product.add_stock(-1)

    def test_invalid_name(self):
        with self.assertRaises(
            InvalidProductError
        ):
            PhysicalProduct(
                product_id="P002",
                name="",
                price=100,
                quantity=1,
                weight=1,
            )

    def test_invalid_price(self):
        with self.assertRaises(
            InvalidProductError
        ):
            PhysicalProduct(
                product_id="P002",
                name="Phone",
                price=-100,
                quantity=1,
                weight=1,
            )

    def test_invalid_weight(self):
        with self.assertRaises(
            InvalidProductError
        ):
            PhysicalProduct(
                product_id="P002",
                name="Phone",
                price=100,
                quantity=1,
                weight=0,
            )

    def test_shipping_cost(self):
        self.assertEqual(
            self.product.shipping_cost,
            500,
        )

    def test_calculate_value(self):
        expected = (
            50000 * 10
            + 500 * 10
        )

        self.assertEqual(
            self.product.calculate_value(),
            expected,
        )

    def test_product_type(self):
        self.assertEqual(
            self.product.product_type(),
            "physical",
        )


class TestDigitalProduct(unittest.TestCase):

    def setUp(self):
        self.product = DigitalProduct(
            product_id="D001",
            name="Python Course",
            price=2000,
            quantity=5,
            file_size=500,
            download_url="https://example.com/course",
        )

    def test_product_type(self):
        self.assertEqual(
            self.product.product_type(),
            "digital",
        )

    def test_calculate_value(self):
        self.assertEqual(
            self.product.calculate_value(),
            10000,
        )

    def test_file_size(self):
        self.assertEqual(
            self.product.file_size,
            500,
        )

    def test_download_url(self):
        self.assertEqual(
            self.product.download_url,
            "https://example.com/course",
        )

    def test_invalid_file_size(self):
        with self.assertRaises(
            InvalidProductError
        ):
            DigitalProduct(
                product_id="D002",
                name="Course",
                price=100,
                quantity=1,
                file_size=0,
                download_url="url",
            )

    def test_invalid_url(self):
        with self.assertRaises(
            InvalidProductError
        ):
            DigitalProduct(
                product_id="D002",
                name="Course",
                price=100,
                quantity=1,
                file_size=100,
                download_url="",
            )


class TestPolymorphism(unittest.TestCase):

    def test_polymorphic_calculate_value(self):
        physical = PhysicalProduct(
            product_id="P001",
            name="Phone",
            price=10000,
            quantity=2,
            weight=0.5,
            shipping_cost=100,
        )

        digital = DigitalProduct(
            product_id="D001",
            name="Ebook",
            price=500,
            quantity=2,
            file_size=10,
            download_url="url",
        )

        products = [
            physical,
            digital,
        ]

        values = [
            product.calculate_value()
            for product in products
        ]

        self.assertEqual(
            values[0],
            20200,
        )

        self.assertEqual(
            values[1],
            1000,
        )


if __name__ == "__main__":
    unittest.main()