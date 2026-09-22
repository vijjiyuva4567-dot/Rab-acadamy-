class InventoryError(Exception):
    """Base exception for inventory-related errors."""

    pass


class InvalidProductError(InventoryError):
    """Raised when product data is invalid."""

    pass


class ProductNotFoundError(InventoryError):
    """Raised when a requested product does not exist."""

    pass


class DuplicateProductError(InventoryError):
    """Raised when a product with the same ID already exists."""

    pass


class InsufficientStockError(InventoryError):
    """Raised when there is not enough stock available."""

    pass


class InvalidQuantityError(InventoryError):
    """Raised when an invalid quantity is provided."""

    pass


class StorageError(InventoryError):
    """Raised when a storage operation fails."""

    pass