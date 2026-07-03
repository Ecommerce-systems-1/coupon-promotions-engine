import pytest
from app.services.calculator import DiscountCalculator

def test_percentage_discount():
    c = {"type": "PERCENTAGE", "value": 20, "buy_quantity": None, "get_quantity": None}
    cart = [{"price": 100, "quantity": 1, "category": "x"}]
    calc = DiscountCalculator()
    r = calc.calculate(c, cart, shipping=10)
    assert r.discount_amount == pytest.approx(20.0)
    assert r.final_total == pytest.approx(90.0)

def test_fixed_amount_capped_at_total():
    c = {"type": "FIXED_AMOUNT", "value": 150, "buy_quantity": None, "get_quantity": None}
    cart = [{"price": 100, "quantity": 1, "category": "x"}]
    calc = DiscountCalculator()
    r = calc.calculate(c, cart, shipping=0)
    assert r.discount_amount == pytest.approx(100.0)
    assert r.final_total == pytest.approx(0.0)

def test_free_shipping():
    c = {"type": "FREE_SHIPPING", "value": 0, "buy_quantity": None, "get_quantity": None}
    cart = [{"price": 100, "quantity": 1, "category": "x"}]
    calc = DiscountCalculator()
    r = calc.calculate(c, cart, shipping=15)
    assert r.discount_amount == pytest.approx(15.0)
    assert r.shipping_discount == pytest.approx(15.0)

def test_buy_2_get_1():
    c = {"type": "BUY_X_GET_Y", "value": 0, "buy_quantity": 2, "get_quantity": 1}
    cart = [
        {"price": 50, "quantity": 1, "category": "x"},
        {"price": 30, "quantity": 1, "category": "x"},
        {"price": 20, "quantity": 1, "category": "x"},  # cheapest = free
    ]
    calc = DiscountCalculator()
    r = calc.calculate(c, cart, shipping=0)
    assert r.discount_amount == pytest.approx(20.0)