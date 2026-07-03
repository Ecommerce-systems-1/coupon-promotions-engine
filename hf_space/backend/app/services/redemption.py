from dataclasses import dataclass
from datetime import datetime

@dataclass
class RedemptionResult:
    success: bool
    reason: str = ""
    redemption_id: int | None = None

class RedemptionService:
    def redeem(self, db, coupon_id: int, customer_id: str, order_id: str, discount_amt: float) -> RedemptionResult:
        try:
            db.execute("BEGIN IMMEDIATE")
            coupon = db.execute("SELECT max_uses FROM coupons WHERE id=?", (coupon_id,)).fetchone()
            if not coupon:
                db.execute("ROLLBACK")
                return RedemptionResult(False, "Coupon not found")
            if coupon["max_uses"] is not None:
                count = db.execute("SELECT COUNT(*) FROM redemptions WHERE coupon_id=?", (coupon_id,)).fetchone()[0]
                if count >= coupon["max_uses"]:
                    db.execute("ROLLBACK")
                    return RedemptionResult(False, "Coupon usage limit reached")
            cur = db.execute(
                "INSERT INTO redemptions (coupon_id, customer_id, order_id, discount_amt, redeemed_at) VALUES (?,?,?,?,?)",
                (coupon_id, customer_id, order_id, discount_amt, datetime.utcnow().isoformat())
            )
            db.execute("COMMIT")
            return RedemptionResult(True, redemption_id=cur.lastrowid)
        except Exception as e:
            db.execute("ROLLBACK")
            return RedemptionResult(False, str(e))