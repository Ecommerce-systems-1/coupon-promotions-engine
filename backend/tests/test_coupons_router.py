from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_coupon():
    resp = client.post("/api/coupons", json={
        "type": "PERCENTAGE", "value": 15,
        "valid_from": "2026-01-01", "valid_until": "2026-12-31",
        "min_order_value": 50
    })
    assert resp.status_code == 201
    assert "code" in resp.json()

def test_validate_valid_coupon():
    code = client.post("/api/coupons", json={
        "type": "FIXED_AMOUNT", "value": 10,
        "valid_from": "2026-01-01", "valid_until": "2026-12-31"
    }).json()["code"]
    resp = client.post("/api/coupons/validate", json={
        "code": code, "customer_id": "cust-1",
        "cart_items": [{"price": 100, "quantity": 1, "category": "electronics"}],
        "shipping": 0
    })
    assert resp.status_code == 200
    assert resp.json()["valid"] is True
    assert resp.json()["discount_amount"] == 10.0

def test_validate_invalid_code_returns_reason():
    resp = client.post("/api/coupons/validate", json={
        "code": "DOESNOTEXIST", "customer_id": "c1",
        "cart_items": [{"price": 50, "quantity": 1, "category": "x"}], "shipping": 0
    })
    assert resp.status_code == 200
    assert resp.json()["valid"] is False
    assert resp.json()["reason_if_invalid"] != ""