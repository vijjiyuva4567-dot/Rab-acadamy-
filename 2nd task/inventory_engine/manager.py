from .exceptions import (
    DuplicateProductError,
    ProductNotFoundError,
    InvalidQuantityError,
)


class InventoryManager:
    """
    Manages products in the inventory.

    Uses encapsulation by keeping the product collection private.
    """

    def __init__(self):
        self.__products = {}

    @property
    def products(self):
        """
        Return a copy of the products dictionary.

        This prevents direct modification of the internal dictionary.
        """
        return self.__products.copy()

    def add_product(self, product):
        product_id = product.product_id

        if product_id in self.__products:
            raise DuplicateProductError(
                f"Product '{product_id}' already exists."
            )

        self.__products[product_id] = product

    def remove_product(self, product_id):
        if product_id not in self.__products:
            raise ProductNotFoundError(
                f"Product '{product_id}' was not found."
            )

        return self.__products.pop(product_id)

    def get_product(self, product_id):
        if product_id not in self.__products:
            raise ProductNotFoundError(
                f"Product '{product_id}' was not found."
            )

        return self.__products[product_id]

    def add_stock(self, product_id, quantity):
        if not isinstance(quantity, int) or quantity <= 0:
            raise InvalidQuantityError(
                "Quantity must be a positive integer."
            )

        product = self.get_product(product_id)
        product.add_stock(quantity)

    def remove_stock(self, product_id, quantity):
        if not isinstance(quantity, int) or quantity <= 0:
            raise InvalidQuantityError(
                "Quantity must be a positive integer."
            )

        product = self.get_product(product_id)
        product.remove_stock(quantity)

    def list_products(self):
        return list(self.__products.values())

    def search_products(self, keyword):
        if not isinstance(keyword, str):
            return []

        keyword = keyword.lower().strip()

        return [
            product
            for product in self.__products.values()
            if keyword in product.name.lower()
            or keyword in product.product_id.lower()
        ]

    def total_inventory_value(self):
        """
        Demonstrates polymorphism.

        Each product calculates its value using its own
        calculate_value() implementation.
        """
        return sum(
            product.calculate_value()
            for product in self.__products.values()
        )

    def count(self):
        return len(self.__products)

    def clear(self):
        self.__products.clear()