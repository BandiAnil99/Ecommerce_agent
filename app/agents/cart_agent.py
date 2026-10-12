from __future__ import annotations

from sqlalchemy.orm import Session

from app.tools.cart_tools import confirm_cart, preview_cart


def preview_items(db: Session, cart_id: str, items: list[dict]) -> dict:
    return preview_cart(db, cart_id, items)


def confirm_items(db: Session, cart_id: str, items: list[dict], confirmed: bool) -> dict:
    return confirm_cart(db, cart_id, items, confirmed=confirmed)
