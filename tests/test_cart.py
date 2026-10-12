from app.models.database import SessionLocal
from app.tools.cart_tools import preview_cart


def test_cart_quantity_validation():
    db = SessionLocal()
    try:
        try:
            preview_cart(db, "cart-1", [{"product_id": "LAP-002", "quantity": 0}])
            assert False, "Should reject quantity 0"
        except ValueError:
            pass
    finally:
        db.close()


def test_cart_confirmation_requirements():
    db = SessionLocal()
    try:
        try:
            from app.tools.cart_tools import confirm_cart
            confirm_cart(db, "cart-2", [{"product_id": "LAP-002", "quantity": 1}], confirmed=False)
            assert False, "Cart confirmation should be required"
        except PermissionError:
            pass
    finally:
        db.close()
