from __future__ import annotations


def compare_products(products: list[dict]) -> list[dict]:
    rows = []
    for product in products:
        rows.append({
            "product_id": product["product_id"],
            "name": product["name"],
            "price": product["price"],
            "ram_gb": product["ram_gb"],
            "processor": product["processor"],
            "storage_gb": product["storage_gb"],
            "battery_hours": product["battery_hours"],
            "stock_quantity": product["stock_quantity"],
            "delivery_days": product["delivery_days"],
        })
    return rows
