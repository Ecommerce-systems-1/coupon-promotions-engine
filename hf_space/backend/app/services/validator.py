import json
from dataclasses import dataclass
from datetime import date

@dataclass
class ValidationResult:
    valid: bool
    reason: str = ""

class CouponValidator:
    def validate(self, coupon: dict, cart_items: list, customer_id: str,
                 customer_uses: int, total_uses: int) -> ValidationResult:
        today = date.today().isoformat()
        if coupon["valid_from"] > today or coupon["valid_until"] < today:
            return ValidationResult(False, "Coupon has expired or not yet active")
        if not coupon["active"]:
            return ValidationResult(False, "Coupon is inactive")
        order_total = sum(i["price"] * i["quantity"] for i in cart_items)
        if order_total < coupon["min_order_value"]:
            return ValidationResult(False, f"Minimum order value ${coupon['min_order_value']:.2f} not met")
        if coupon["max_uses"] is not None and total_uses >= coupon["max_uses"]:
            return ValidationResult(False, "Coupon usage limit reached")
        if customer_uses >= coupon["per_customer_limit"]:
            return ValidationResult(False, f"You have already used this coupon {customer_uses} time(s)")
        if coupon["applicable_categories"]:
            allowed = set(json.loads(coupon["applicable_categories"]))
            cart_cats = {i["category"] for i in cart_items}
            if not allowed & cart_cats:
                return ValidationResult(False, f"Coupon only valid for category: {', '.join(allowed)}")
        return ValidationResult(True)