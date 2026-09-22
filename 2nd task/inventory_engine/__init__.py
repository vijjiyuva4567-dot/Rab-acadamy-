"""
Inventory Management Engine

An object-oriented inventory management system demonstrating:
- Inheritance
- Encapsulation
- Polymorphism
- Custom exceptions
- JSON and CSV persistence
- Unit testing
"""

from .models import Product, PhysicalProduct, DigitalProduct
from .manager import InventoryManager

__all__ = [
    "Product",
    "PhysicalProduct",
    "DigitalProduct",
    "InventoryManager",
]