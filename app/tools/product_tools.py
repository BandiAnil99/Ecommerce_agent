from __future__ import annotations

from typing import Iterable

from sqlalchemy.orm import Session

from app.models.database import ProductORM


def normalize_text(value: str | None) -> str:
    return (value or "").strip().lower()


def search_products(
    db: Session,
    *,
    category: str | None = None,
    max_budget: float | None = None,
    min_ram: int | None = None,
    product_id: str | None = None,
    limit: int | None = None,
) -> list[ProductORM]:
    query = db.query(ProductORM)

    if category:
        category_norm = normalize_text(category)
        query = query.filter(ProductORM.category.ilike(f"%{category_norm}%"))
    if product_id:
        query = query.filter(ProductORM.product_id == product_id)
    if max_budget is not None:
        query = query.filter(ProductORM.price <= max_budget)
    if min_ram is not None:
        query = query.filter(ProductORM.ram_gb >= min_ram)

    products = query.order_by(ProductORM.price.asc()).all()
    if limit is not None:
        return products[:limit]
    return products


def get_product(db: Session, product_id: str) -> ProductORM | None:
    return db.query(ProductORM).filter(ProductORM.product_id == product_id).one_or_none()


def compare_products(db: Session, product_ids: Iterable[str]) -> list[dict]:
    ids = [str(pid).strip() for pid in product_ids if str(pid).strip()]
    products = db.query(ProductORM).filter(ProductORM.product_id.in_(ids)).all()
    records = []
    for product in products:
        records.append({
            "product_id": product.product_id,
            "name": product.name,
            "price": product.price,
            "ram_gb": product.ram_gb,
            "battery_hours": product.battery_hours,
            "stock_quantity": product.stock_quantity,
            "processor": product.processor,
            "storage_gb": product.storage_gb,
        })
    return records
