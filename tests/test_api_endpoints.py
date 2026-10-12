from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_products_endpoint_schema_and_error_codes():
    resp = client.get("/products", params={"page": 1, "page_size": 5})
    assert resp.status_code == 200
    payload = resp.json()
    assert "items" in payload
    assert len(payload["items"]) <= 5

    missing = client.get("/products/MISSING-ID")
    assert missing.status_code == 404


def test_cart_confirmation_is_enforced_server_side():
    resp = client.post("/cart/confirm", json={"cart_id": "cart-123", "items": [{"product_id": "LAP-002", "quantity": 1}], "confirmed": False})
    assert resp.status_code == 400
    assert "confirmation" in resp.json()["detail"].lower()
