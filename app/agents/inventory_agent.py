from __future__ import annotations

from sqlalchemy.orm import Session

from app.tools.inventory_tools import get_inventory_status


def check_inventory_for_products(db: Session, product_ids: list[str]) -> list[dict]:
    inventory = []
    for product_id in product_ids:
        inventory.append(get_inventory_status(db, product_id))
    return inventory
