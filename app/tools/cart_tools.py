from __future__ import annotations

from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.database import CartItemORM, CartORM, ProductORM


def create_cart_record(db: Session, cart_id: str | None = None) -> CartORM:
    cart_id = cart_id or str(uuid4())
    cart = db.query(CartORM).filter(CartORM.cart_id == cart_id).one_or_none()
    if cart is None:
        cart = CartORM(cart_id=cart_id, status="draft", confirmed=0, total_amount=0.0, created_at="")
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def preview_cart(db: Session, cart_id: str, items: list[dict]) -> dict:
    subtotal = 0.0
    records = []
    for item in items:
        product = db.query(ProductORM).filter(ProductORM.product_id == item["product_id"]).one_or_none()
        if product is None:
            raise ValueError(f"Product not found: {item['product_id']}")
        qty = int(item.get("quantity", 1))
        if qty < 1:
            raise ValueError(f"Quantity must be at least 1 for {item['product_id']}")
        if product.stock_quantity < qty:
            raise ValueError(f"Insufficient stock for {item['product_id']}")
        unit_price = product.price * (1 - (product.discount_percent / 100.0))
        line_total = unit_price * qty
        subtotal += line_total
        records.append({
            "product_id": product.product_id,
            "quantity": qty,
            "unit_price": round(unit_price, 2),
            "line_total": round(line_total, 2),
        })
    return {
        "cart_id": cart_id,
        "valid": True,
        "subtotal": round(subtotal, 2),
        "total": round(subtotal, 2),
        "savings": round(0.0, 2),
        "message": "Cart preview is valid.",
        "items": records,
    }


def confirm_cart(db: Session, cart_id: str, items: list[dict], confirmed: bool = False) -> dict:
    if not confirmed:
        raise PermissionError("Cart creation requires explicit customer confirmation.")
    preview = preview_cart(db, cart_id, items)
    cart = db.query(CartORM).filter(CartORM.cart_id == cart_id).one_or_none()
    if cart is None:
        cart = create_cart_record(db, cart_id)
    cart.status = "confirmed"
    cart.confirmed = 1
    cart.total_amount = preview["total"]
    db.query(CartItemORM).filter(CartItemORM.cart_id == cart_id).delete()
    for item in preview["items"]:
        db.add(CartItemORM(
            cart_id=cart_id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            unit_price=item["unit_price"],
        ))
    db.commit()
    return {
        "cart_id": cart_id,
        "status": cart.status,
        "confirmed": True,
        "total": preview["total"],
        "items": preview["items"],
    }
