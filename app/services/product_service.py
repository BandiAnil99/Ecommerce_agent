from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.database import ProductORM
from app.tools.product_tools import compare_products, search_products


def list_products(db: Session, page: int = 1, page_size: int = 10, **filters) -> tuple[list[dict[str, Any]], int]:
    query = db.query(ProductORM)
    if filters.get("category"):
        query = query.filter(ProductORM.category.ilike(f"%{filters['category']}%"))
    if filters.get("budget") is not None:
        query = query.filter(ProductORM.price <= float(filters["budget"]))
    if filters.get("min_ram") is not None:
        query = query.filter(ProductORM.ram_gb >= int(filters["min_ram"]))
    total = query.count()
    products = query.order_by(ProductORM.price.asc()).offset((page - 1) * page_size).limit(page_size).all()
    return [
        {
            "product_id": product.product_id,
            "name": product.name,
            "brand": product.brand,
            "category": product.category,
            "price": product.price,
            "discount_percent": product.discount_percent,
            "ram_gb": product.ram_gb,
            "processor": product.processor,
            "storage_gb": product.storage_gb,
            "storage_type": product.storage_type,
            "battery_hours": product.battery_hours,
            "weight_kg": product.weight_kg,
            "stock_quantity": product.stock_quantity,
            "delivery_days": product.delivery_days,
            "description": product.description,
            "warranty": product.warranty,
            "faq_document": product.faq_document,
        }
        for product in products
    ], total


def search_catalog(db: Session, **filters) -> list[dict[str, Any]]:
    products = search_products(db, **filters)
    return [
        {
            "product_id": product.product_id,
            "name": product.name,
            "brand": product.brand,
            "category": product.category,
            "price": product.price,
            "discount_percent": product.discount_percent,
            "ram_gb": product.ram_gb,
            "processor": product.processor,
            "storage_gb": product.storage_gb,
            "storage_type": product.storage_type,
            "battery_hours": product.battery_hours,
            "weight_kg": product.weight_kg,
            "stock_quantity": product.stock_quantity,
            "delivery_days": product.delivery_days,
            "description": product.description,
            "warranty": product.warranty,
            "faq_document": product.faq_document,
        }
        for product in products
    ]


def get_product_details(db: Session, product_id: str) -> dict[str, Any] | None:
    product = db.query(ProductORM).filter(ProductORM.product_id == product_id).one_or_none()
    if product is None:
        return None
    return {
        "product_id": product.product_id,
        "name": product.name,
        "brand": product.brand,
        "category": product.category,
        "price": product.price,
        "discount_percent": product.discount_percent,
        "ram_gb": product.ram_gb,
        "processor": product.processor,
        "storage_gb": product.storage_gb,
        "storage_type": product.storage_type,
        "battery_hours": product.battery_hours,
        "weight_kg": product.weight_kg,
        "stock_quantity": product.stock_quantity,
        "delivery_days": product.delivery_days,
        "description": product.description,
        "warranty": product.warranty,
        "faq_document": product.faq_document,
    }


def compare_catalog(db: Session, product_ids: list[str]) -> list[dict[str, Any]]:
    return compare_products(db, product_ids)
