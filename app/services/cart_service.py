from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.database import CartItemORM, CartORM, ProductORM


def get_cart(db: Session, cart_id: str) -> dict:
    cart = db.query(CartORM).filter(CartORM.cart_id == cart_id).one_or_none()
    if cart is None:
        raise ValueError(f"Cart not found: {cart_id}")
    items = db.query(CartItemORM).filter(CartItemORM.cart_id == cart_id).all()
    return {
        "cart_id": cart.cart_id,
        "status": cart.status,
        "confirmed": bool(cart.confirmed),
        "total": cart.total_amount,
        "items": [{
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
        } for item in items],
    }


def delete_cart_item(db: Session, cart_id: str, product_id: str) -> dict:
    cart = db.query(CartORM).filter(CartORM.cart_id == cart_id).one_or_none()
    if cart is None:
        raise ValueError(f"Cart not found: {cart_id}")
    deleted = db.query(CartItemORM).filter(CartItemORM.cart_id == cart_id, CartItemORM.product_id == product_id).delete()
    if deleted == 0:
        raise ValueError(f"Item not found in cart: {product_id}")
    db.commit()
    return get_cart(db, cart_id)
