from app.agents.requirement_agent import extract_requirements
from app.models.database import SessionLocal
from app.services.product_service import search_catalog


def test_missing_product_specs_are_handled():
    db = SessionLocal()
    try:
        items = search_catalog(db, category="laptop")
        assert any(item["faq_document"] for item in items)
    finally:
        db.close()


def test_assistant_requirement_extraction():
    req = extract_requirements("Need a laptop under ₹60,000 for Python programming and online classes with 16 GB RAM")
    assert req.budget == 60000
    assert req.min_ram_gb == 16
    assert "python" in " ".join(req.use_cases).lower()
