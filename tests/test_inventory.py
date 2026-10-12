from app.models.database import SessionLocal
from app.services.product_service import get_product_details
from app.tools.inventory_tools import get_inventory_status


def test_out_of_stock_products():
    db = SessionLocal()
    try:
        info = get_inventory_status(db, "LAP-003")
        assert info["status"] == "out_of_stock"
        info2 = get_inventory_status(db, "LAP-002")
        assert info2["stock_quantity"] > 0
    finally:
        db.close()


def test_empty_search_results():
    db = SessionLocal()
    try:
        products = db.query(__import__("app.models.database", fromlist=["ProductORM"]).ProductORM).filter(__import__("app.models.database", fromlist=["ProductORM"]).ProductORM.price < 100).all()
        assert products == []
    finally:
        db.close()
