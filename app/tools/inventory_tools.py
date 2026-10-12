from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.database import ProductORM


def get_inventory_status(db: Session, product_id: str) -> dict:
    product = db.query(ProductORM).filter(ProductORM.product_id == product_id).one_or_none()
    if product is None:
        raise ValueError(f"Product not found: {product_id}")
    in_stock = product.stock_quantity > 0
    status = "in_stock" if in_stock else "out_of_stock"
    if product.stock_quantity > 0 and product.stock_quantity <= 3:
        status = "low_stock"
    return {
        "product_id": product.product_id,
        "in_stock": in_stock,
        "stock_quantity": product.stock_quantity,
        "delivery_days": product.delivery_days,
        "status": status,
    }
