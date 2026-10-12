from app.agents.requirement_agent import extract_requirements
from app.models.database import SessionLocal
from app.services.product_service import list_products, search_catalog


def test_product_search_and_filters():
    db = SessionLocal()
    try:
        products = search_catalog(db, max_budget=60000, min_ram=16)
        assert products
        assert all(item["price"] <= 60000 for item in products)
        assert all(item["ram_gb"] >= 16 for item in products)
    finally:
        db.close()


def test_budget_constraints():
    db = SessionLocal()
    try:
        items, total = list_products(db, page=1, page_size=20, budget=60000)
        assert total >= 1
        assert all(item["price"] <= 60000 for item in items)
    finally:
        db.close()


def test_ram_requirements():
    req = extract_requirements("I want 16 GB RAM and Python programming laptop under 60k")
    assert req.min_ram_gb == 16
    assert req.budget == 60000
