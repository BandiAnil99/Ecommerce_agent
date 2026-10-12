from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.agents.cart_agent import confirm_items, preview_items
from app.models.database import SessionLocal
from app.models.schemas import CartConfirmRequest, CartPreviewRequest, CartResponse, CartPreviewResponse
from app.services.cart_service import delete_cart_item, get_cart

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("/preview")
def preview_cart(request: CartPreviewRequest) -> CartPreviewResponse:
    db = SessionLocal()
    try:
        try:
            result = preview_items(db, request.cart_id or "preview-cart", [{"product_id": item.product_id, "quantity": item.quantity} for item in request.items])
            return CartPreviewResponse(**result)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    finally:
        db.close()


@router.post("/confirm")
def confirm_cart(request: CartConfirmRequest) -> CartResponse:
    db = SessionLocal()
    try:
        try:
            result = confirm_items(db, request.cart_id, [{"product_id": item.product_id, "quantity": item.quantity} for item in request.items], confirmed=request.confirmed)
            return CartResponse(**result)
        except (PermissionError, ValueError) as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    finally:
        db.close()


@router.get("/{cart_id}")
def get_cart_details(cart_id: str) -> dict:
    db = SessionLocal()
    try:
        try:
            return get_cart(db, cart_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    finally:
        db.close()


@router.delete("/{cart_id}/items/{product_id}")
def delete_item(cart_id: str, product_id: str) -> dict:
    db = SessionLocal()
    try:
        try:
            return delete_cart_item(db, cart_id, product_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    finally:
        db.close()
