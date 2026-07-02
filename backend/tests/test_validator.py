import pytest
from datetime import date, timedelta
from services.validator import CouponValidator

def make_coupon(**kwargs):
    defaults = {
        "id": 1, "code": "SAVE20", "type": "PERCENTAGE", "value": 20,
        "min_order_value": 0, "max_uses": None, "per_customer_limit": 1,
        "applicable_categories": None, "active": 1,
        "valid_from": (date.today() - timedelta(days=1)).isoformat(),
        "valid_until": (date.today() + timedelta(days=30)).isoformat(),
    }
    defaults.update(kwargs)
    return defaults

def make_cart(total=100.0, categories=("electronics",)):
    return [{"price": total, "quantity": 1, "category": categories[0]}]

def test_valid_coupon_passes():
    v = CouponValidator()
    result = v.validate(make_coupon(), make_cart(), customer_id="c1", customer_uses=0, total_uses=0)
    assert result.valid is True

def test_expired_coupon_fails():
    c = make_coupon(valid_until=(date.today() - timedelta(days=1)).isoformat())
    v = CouponValidator()
    result = v.validate(c, make_cart(), "c1", 0, 0)
    assert result.valid is False
    assert "expired" in result.reason.lower()

def test_min_order_not_met():
    c = make_coupon(min_order_value=200)
    v = CouponValidator()
    result = v.validate(c, make_cart(50), "c1", 0, 0)
    assert result.valid is False
    assert "minimum" in result.reason.lower()

def test_max_uses_exceeded():
    c = make_coupon(max_uses=10)
    v = CouponValidator()
    result = v.validate(c, make_cart(), "c1", 0, total_uses=10)
    assert result.valid is False
    assert "usage limit" in result.reason.lower()

def test_per_customer_limit_exceeded():
    v = CouponValidator()
    result = v.validate(make_coupon(), make_cart(), "c1", customer_uses=1, total_uses=1)
    assert result.valid is False
    assert "already used" in result.reason.lower()

def test_category_restriction_blocks_wrong_category():
    import json
    c = make_coupon(applicable_categories=json.dumps(["clothing"]))
    cart = [{"price": 100, "quantity": 1, "category": "electronics"}]
    v = CouponValidator()
    result = v.validate(c, cart, "c1", 0, 0)
    assert result.valid is False
    assert "category" in result.reason.lower()