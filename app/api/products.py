from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.models.schemas import ProductRecord
from app.services.product_service import compare_catalog, get_product_details, list_products, search_catalog

router = APIRouter(prefix="/products", tags=["products"])


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def list_product_catalog(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    category: str | None = None,
    budget: float | None = None,
    min_ram: int | None = None,
) -> dict:
    db = SessionLocal()
    try:
        items, total = list_products(db, page=page, page_size=page_size, category=category, budget=budget, min_ram=min_ram)
        return {"items": items, "page": page, "page_size": page_size, "total": total}
    finally:
        db.close()


@router.get("/search")
def search_products(
    category: str | None = None,
    budget: float | None = None,
    min_ram: int | None = None,
) -> dict:
    db = SessionLocal()
    try:
        items = search_catalog(db, category=category, max_budget=budget, min_ram=min_ram)
        if not items:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products matched the provided filters.")
        return {"items": items}
    finally:
        db.close()


@router.get("/{product_id}")
def product_detail(product_id: str) -> dict:
    db = SessionLocal()
    try:
        item = get_product_details(db, product_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {product_id} not found.")
        return item
    finally:
        db.close()


@router.get("/compare")
def compare_products_route(product_ids: str = Query(...)) -> dict:
    ids = [part.strip() for part in product_ids.split(",") if part.strip()]
    if not ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one product ID is required.")
    db = SessionLocal()
    try:
        rows = compare_catalog(db, ids)
        return {"comparison": rows}
    finally:
        db.close()
