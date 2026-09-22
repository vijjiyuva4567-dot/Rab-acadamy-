from pathlib import Path

from inventory_engine import (
    InventoryManager,
    PhysicalProduct,
    DigitalProduct,
)

from inventory_engine.storage import InventoryStorage
from inventory_engine.exceptions import InventoryError


def display_inventory(manager):
    print("\n========== INVENTORY ==========")

    for product in manager.list_products():
        print(product)

    print(
        f"\nTotal products: {manager.count()}"
    )

    print(
        f"Total inventory value: "
        f"₹{manager.total_inventory_value():.2f}"
    )


def main():
    manager = InventoryManager()

    try:
        # ---------------------------------
        # Add physical product
        # ---------------------------------

        laptop = PhysicalProduct(
            product_id="P001",
            name="Laptop",
            price=55000,
            quantity=5,
            weight=1.5,
            shipping_cost=500,
        )

        manager.add_product(laptop)

        # ---------------------------------
        # Add digital product
        # ---------------------------------

        course = DigitalProduct(
            product_id="D001",
            name="Python Programming Course",
            price=1999,
            quantity=10,
            file_size=850,
            download_url="https://example.com/python-course",
        )

        manager.add_product(course)

        # ---------------------------------
        # Display inventory
        # ---------------------------------

        display_inventory(manager)

        # ---------------------------------
        # Stock operations
        # ---------------------------------

        manager.add_stock("P001", 3)
        manager.remove_stock("D001", 2)

        print("\nAfter stock update:")
        display_inventory(manager)

        # ---------------------------------
        # Search
        # ---------------------------------

        print("\n========== SEARCH ==========")

        results = manager.search_products("python")

        for product in results:
            print(product)

        # ---------------------------------
        # JSON persistence
        # ---------------------------------

        json_path = Path("data/inventory.json")

        InventoryStorage.save_json(
            manager,
            json_path,
        )

        print(
            f"\nJSON saved to: {json_path}"
        )

        # ---------------------------------
        # CSV persistence
        # ---------------------------------

        csv_path = Path("data/inventory.csv")

        InventoryStorage.save_csv(
            manager,
            csv_path,
        )

        print(
            f"CSV saved to: {csv_path}"
        )

        # ---------------------------------
        # Load JSON
        # ---------------------------------

        loaded_manager = InventoryStorage.load_json(
            json_path
        )

        print(
            "\nInventory loaded successfully from JSON."
        )

        display_inventory(loaded_manager)

    except InventoryError as exc:
        print(
            f"\nInventory error: {exc}"
        )


if __name__ == "__main__":
    main()