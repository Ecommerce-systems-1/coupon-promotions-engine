from dataclasses import dataclass, field

@dataclass
class DiscountResult:
    discount_amount: float
    shipping_discount: float
    final_total: float
    breakdown: dict = field(default_factory=dict)

class DiscountCalculator:
    def calculate(self, coupon: dict, cart_items: list, shipping: float = 0) -> DiscountResult:
        subtotal = sum(i["price"] * i["quantity"] for i in cart_items)
        t = coupon["type"]
        if t == "PERCENTAGE":
            disc = round(subtotal * coupon["value"] / 100, 2)
            return DiscountResult(disc, 0, max(0, subtotal + shipping - disc),
                                  {"type": t, "pct": coupon["value"], "savings": disc})
        elif t == "FIXED_AMOUNT":
            disc = min(coupon["value"], subtotal)
            return DiscountResult(disc, 0, max(0, subtotal + shipping - disc),
                                  {"type": t, "fixed": coupon["value"], "savings": disc})
        elif t == "FREE_SHIPPING":
            return DiscountResult(shipping, shipping, subtotal,
                                  {"type": t, "shipping_waived": shipping})
        elif t == "BUY_X_GET_Y":
            prices = sorted([i["price"] for i in cart_items for _ in range(i["quantity"])])
            buy_q, get_q = coupon["buy_quantity"], coupon["get_quantity"]
            group = buy_q + get_q
            sets = len(prices) // group
            free_items = prices[:sets * get_q]  # cheapest items are free
            disc = round(sum(free_items), 2)
            return DiscountResult(disc, 0, max(0, subtotal + shipping - disc),
                                  {"type": t, "free_items": len(free_items), "savings": disc})
        return DiscountResult(0, 0, subtotal + shipping, {})