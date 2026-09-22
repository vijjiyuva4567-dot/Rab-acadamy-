from abc import ABC, abstractmethod

from .exceptions import (
    InvalidProductError,
    InvalidQuantityError,
    InsufficientStockError,
)


class Product(ABC):
    """
    Abstract base class representing a general product.

    Demonstrates encapsulation using private attributes
    and polymorphism through the abstract methods.
    """

    def __init__(self, product_id, name, price, quantity):
        self.__product_id = None
        self.__name = None
        self.__price = None
        self.__quantity = None

        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity

    # -----------------------------
    # Encapsulated properties
    # -----------------------------

    @property
    def product_id(self):
        return self.__product_id

    @product_id.setter
    def product_id(self, value):
        if not isinstance(value, str) or not value.strip():
            raise InvalidProductError(
                "Product ID must be a non-empty string."
            )

        self.__product_id = value.strip()

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        if not isinstance(value, str) or not value.strip():
            raise InvalidProductError(
                "Product name must be a non-empty string."
            )

        self.__name = value.strip()

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise InvalidProductError(
                "Price must be a valid number."
            )

        if value < 0:
            raise InvalidProductError(
                "Price cannot be negative."
            )

        self.__price = value

    @property
    def quantity(self):
        return self.__quantity

    @quantity.setter
    def quantity(self, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise InvalidQuantityError(
                "Quantity must be an integer."
            )

        if value < 0:
            raise InvalidQuantityError(
                "Quantity cannot be negative."
            )

        self.__quantity = value

    # -----------------------------
    # Stock operations
    # -----------------------------

    def add_stock(self, quantity):
        if not isinstance(quantity, int) or quantity <= 0:
            raise InvalidQuantityError(
                "Stock quantity must be a positive integer."
            )

        self.__quantity += quantity

    def remove_stock(self, quantity):
        if not isinstance(quantity, int) or quantity <= 0:
            raise InvalidQuantityError(
                "Stock quantity must be a positive integer."
            )

        if quantity > self.__quantity:
            raise InsufficientStockError(
                f"Insufficient stock for product '{self.__name}'. "
                f"Available: {self.__quantity}, requested: {quantity}."
            )

        self.__quantity -= quantity

    # -----------------------------
    # Polymorphic methods
    # -----------------------------

    @abstractmethod
    def product_type(self):
        """Return the type of product."""
        pass

    @abstractmethod
    def calculate_value(self):
        """Calculate total inventory value for this product."""
        pass

    # -----------------------------
    # Serialization
    # -----------------------------

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "product_type": self.product_type(),
        }

    def __str__(self):
        return (
            f"{self.product_type()} | "
            f"{self.product_id} | "
            f"{self.name} | "
            f"₹{self.price:.2f} | "
            f"Stock: {self.quantity}"
        )


class PhysicalProduct(Product):
    """
    Physical product.

    Adds weight information and shipping cost.
    """

    def __init__(
        self,
        product_id,
        name,
        price,
        quantity,
        weight,
        shipping_cost=0.0,
    ):
        super().__init__(
            product_id,
            name,
            price,
            quantity,
        )

        self.__weight = None
        self.__shipping_cost = None

        self.weight = weight
        self.shipping_cost = shipping_cost

    @property
    def weight(self):
        return self.__weight

    @weight.setter
    def weight(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise InvalidProductError(
                "Weight must be a valid number."
            )

        if value <= 0:
            raise InvalidProductError(
                "Weight must be greater than zero."
            )

        self.__weight = value

    @property
    def shipping_cost(self):
        return self.__shipping_cost

    @shipping_cost.setter
    def shipping_cost(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise InvalidProductError(
                "Shipping cost must be a valid number."
            )

        if value < 0:
            raise InvalidProductError(
                "Shipping cost cannot be negative."
            )

        self.__shipping_cost = value

    def product_type(self):
        return "physical"

    def calculate_value(self):
        return (
            self.price * self.quantity
            + self.shipping_cost * self.quantity
        )

    def to_dict(self):
        data = super().to_dict()

        data.update(
            {
                "weight": self.weight,
                "shipping_cost": self.shipping_cost,
            }
        )

        return data


class DigitalProduct(Product):
    """
    Digital product.

    Adds file size and download information.
    """

    def __init__(
        self,
        product_id,
        name,
        price,
        quantity,
        file_size,
        download_url,
    ):
        super().__init__(
            product_id,
            name,
            price,
            quantity,
        )

        self.__file_size = None
        self.__download_url = None

        self.file_size = file_size
        self.download_url = download_url

    @property
    def file_size(self):
        return self.__file_size

    @file_size.setter
    def file_size(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise InvalidProductError(
                "File size must be a valid number."
            )

        if value <= 0:
            raise InvalidProductError(
                "File size must be greater than zero."
            )

        self.__file_size = value

    @property
    def download_url(self):
        return self.__download_url

    @download_url.setter
    def download_url(self, value):
        if not isinstance(value, str) or not value.strip():
            raise InvalidProductError(
                "Download URL must be a non-empty string."
            )

        self.__download_url = value.strip()

    def product_type(self):
        return "digital"

    def calculate_value(self):
        return self.price * self.quantity

    def to_dict(self):
        data = super().to_dict()

        data.update(
            {
                "file_size": self.file_size,
                "download_url": self.download_url,
            }
        )

        return data