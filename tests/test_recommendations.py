from app.agents.requirement_agent import extract_requirements
from app.models.database import SessionLocal
from app.services.recommendation_service import rank_products


def test_discount_calculations():
    from app.tools.budget_tools import calculate_discounted_price
    final_price, discount = calculate_discounted_price(60000, 10)
    assert final_price == 54000.0
    assert discount == 6000.0


def test_product_ranking_for_python_workload():
    db = SessionLocal()
    try:
        products = [
            {"product_id": "LAP-002", "price": 55990, "ram_gb": 16, "battery_hours": 10.8, "stock_quantity": 12, "processor": "AMD Ryzen 7 7730U", "storage_gb": 512},
            {"product_id": "LAP-005", "price": 44990, "ram_gb": 8, "battery_hours": 9.8, "stock_quantity": 21, "processor": "Intel Core i5-1240P", "storage_gb": 512},
        ]
        requirements = extract_requirements("I need a laptop under ₹60,000 for Python programming, machine learning basics, and online classes. I prefer 16 GB RAM and good battery life.")
        ranked = rank_products(requirements, products, [{"product_id": "LAP-002", "stock_quantity": 12, "status": "in_stock"}, {"product_id": "LAP-005", "stock_quantity": 21, "status": "in_stock"}])
        assert ranked[0]["product_id"] == "LAP-002"
    finally:
        db.close()


def test_rag_behavior_when_no_documents_match():
    from app.services.rag_service import RAGService
    rag = RAGService()
    result = rag.answer_question("totally irrelevant question to this laptop catalog")
    assert result["answer"]
    assert result["answer_confidence"] in {"low", "medium"}
