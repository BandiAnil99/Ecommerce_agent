from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.models.database import SessionLocal
from app.tools.inventory_tools import get_inventory_status

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/{product_id}")
def inventory_for_product(product_id: str):
    db = SessionLocal()
    try:
        try:
            return get_inventory_status(db, product_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    finally:
        db.close()
