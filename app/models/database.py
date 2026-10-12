from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Iterable

from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings

Base = declarative_base()


class ProductORM(Base):
    __tablename__ = "products"

    product_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    discount_percent = Column(Float, default=0.0)
    ram_gb = Column(Integer, nullable=False)
    processor = Column(String, nullable=False)
    storage_gb = Column(Integer, nullable=False)
    storage_type = Column(String, nullable=False)
    battery_hours = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    delivery_days = Column(Integer, nullable=False, default=0)
    description = Column(String, nullable=False)
    warranty = Column(String, nullable=False)
    faq_document = Column(String, nullable=False)


class CartORM(Base):
    __tablename__ = "carts"

    cart_id = Column(String, primary_key=True)
    status = Column(String, default="draft")
    total_amount = Column(Float, default=0.0)
    confirmed = Column(Integer, default=0)
    created_at = Column(String, default="")


class CartItemORM(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(String, nullable=False)
    product_id = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)


engine = create_engine(get_settings().DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def _normalize_product_row(row: dict) -> dict:
    return {
        "product_id": str(row.get("product_id", "")).strip(),
        "name": str(row.get("name", "")).strip(),
        "brand": str(row.get("brand", "")).strip(),
        "category": str(row.get("category", "laptop")).strip(),
        "price": float(row.get("price", 0) or 0),
        "discount_percent": float(row.get("discount_percent", 0) or 0),
        "ram_gb": int(row.get("ram_gb", 0) or 0),
        "processor": str(row.get("processor", "")).strip(),
        "storage_gb": int(row.get("storage_gb", 0) or 0),
        "storage_type": str(row.get("storage_type", "SSD")).strip(),
        "battery_hours": float(row.get("battery_hours", 0) or 0),
        "weight_kg": float(row.get("weight_kg", 0) or 0),
        "stock_quantity": int(row.get("stock_quantity", 0) or 0),
        "delivery_days": int(row.get("delivery_days", 0) or 0),
        "description": str(row.get("description", "")).strip(),
        "warranty": str(row.get("warranty", "")).strip(),
        "faq_document": str(row.get("faq_document", "")).strip(),
    }


def seed_products_from_csv(csv_path: str | Path) -> None:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Catalog file not found: {path}")

    with path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = [_normalize_product_row(row) for row in reader]

    db = SessionLocal()
    try:
        for row in rows:
            existing = db.get(ProductORM, row["product_id"])
            if existing:
                for key, value in row.items():
                    setattr(existing, key, value)
            else:
                db.add(ProductORM(**row))
        db.commit()
    finally:
        db.close()


def get_product_catalog_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "products.csv"


def seed_default_catalog() -> None:
    init_db()
    csv_path = get_product_catalog_path()
    if csv_path.exists():
        seed_products_from_csv(csv_path)


__all__ = [
    "Base",
    "ProductORM",
    "CartORM",
    "CartItemORM",
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    "seed_products_from_csv",
    "seed_default_catalog",
]
