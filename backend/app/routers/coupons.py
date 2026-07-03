import json
import secrets
from datetime import datetime, timezone
from typing import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.database import get_db
from app.services.validator import CouponValidator
from app.services.calculator import DiscountCalculator
from app.services.redemption import RedemptionService

router = APIRouter(prefix="/api/coupons", tags=["coupons"])
_validator = CouponValidator()
_calculator = DiscountCalculator()
_redemption = RedemptionService()


class CouponCreate(BaseModel):
    type: Literal["PERCENTAGE", "FIXED_AMOUNT", "FREE_SHIPPING", "BUY_X_GET_Y"]
    value: float = Field(0, ge=0)
    valid_from: str
    valid_until: str
    code: str | None = None
    min_order_value: float = Field(0, ge=0)
    max_uses: int | None = Field(None, ge=1)
    per_customer_limit: int = Field(1, ge=1)
    applicable_categories: list[str] | None = None
    buy_quantity: int | None = Field(None, ge=1)
    get_quantity: int | None = Field(None, ge=1)


class CartItem(BaseModel):
    price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=1)
    category: str = ""


class ValidateRequest(BaseModel):
    code: str
    customer_id: str
    cart_items: list[CartItem] = Field(..., min_length=1)
    shipping: float = Field(0, ge=0)


class RedeemRequest(ValidateRequest):
    order_id: str


def _get_coupon(db, code: str):
    return db.execute("SELECT * FROM coupons WHERE code=?", (code,)).fetchone()


def _usage_counts(db, coupon_id: int, customer_id: str) -> tuple[int, int]:
    customer_uses = db.execute(
        "SELECT COUNT(*) FROM redemptions WHERE coupon_id=? AND customer_id=?",
        (coupon_id, customer_id),
    ).fetchone()[0]
    total_uses = db.execute(
        "SELECT COUNT(*) FROM redemptions WHERE coupon_id=?", (coupon_id,)
    ).fetchone()[0]
    return customer_uses, total_uses


@router.post("", status_code=201)
def create_coupon(payload: CouponCreate):
    db = get_db()
    code = payload.code or f"{payload.type[:4]}-{secrets.token_hex(4).upper()}"
    now = datetime.now(timezone.utc).isoformat()
    cats = json.dumps(payload.applicable_categories) if payload.applicable_categories else None
    try:
        cur = db.execute(
            "INSERT INTO coupons (code, type, value, min_order_value, max_uses, per_customer_limit, "
            "applicable_categories, buy_quantity, get_quantity, active, valid_from, valid_until, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,1,?,?,?)",
            (code, payload.type, payload.value, payload.min_order_value, payload.max_uses,
             payload.per_customer_limit, cats, payload.buy_quantity, payload.get_quantity,
             payload.valid_from, payload.valid_until, now),
        )
    except Exception:
        raise HTTPException(409, f"Coupon code '{code}' already exists")
    db.commit()
    return dict(db.execute("SELECT * FROM coupons WHERE id=?", (cur.lastrowid,)).fetchone())


@router.get("")
def list_coupons():
    db = get_db()
    return [dict(r) for r in db.execute("SELECT * FROM coupons ORDER BY id DESC").fetchall()]


@router.post("/validate")
def validate_coupon(payload: ValidateRequest):
    db = get_db()
    row = _get_coupon(db, payload.code)
    if not row:
        return {"valid": False, "reason_if_invalid": "Coupon code not found",
                "discount_amount": 0.0, "final_total": None}
    coupon = dict(row)
    cart = [i.model_dump() for i in payload.cart_items]
    customer_uses, total_uses = _usage_counts(db, coupon["id"], payload.customer_id)
    check = _validator.validate(coupon, cart, payload.customer_id, customer_uses, total_uses)
    if not check.valid:
        return {"valid": False, "reason_if_invalid": check.reason,
                "discount_amount": 0.0, "final_total": None}
    result = _calculator.calculate(coupon, cart, payload.shipping)
    return {
        "valid": True,
        "reason_if_invalid": "",
        "discount_amount": result.discount_amount,
        "shipping_discount": result.shipping_discount,
        "final_total": result.final_total,
        "breakdown": result.breakdown,
    }


@router.post("/redeem", status_code=201)
def redeem_coupon(payload: RedeemRequest):
    db = get_db()
    row = _get_coupon(db, payload.code)
    if not row:
        raise HTTPException(404, "Coupon code not found")
    coupon = dict(row)
    cart = [i.model_dump() for i in payload.cart_items]
    customer_uses, total_uses = _usage_counts(db, coupon["id"], payload.customer_id)
    check = _validator.validate(coupon, cart, payload.customer_id, customer_uses, total_uses)
    if not check.valid:
        raise HTTPException(422, check.reason)
    result = _calculator.calculate(coupon, cart, payload.shipping)
    outcome = _redemption.redeem(db, coupon["id"], payload.customer_id,
                                 payload.order_id, result.discount_amount)
    if not outcome.success:
        raise HTTPException(409, outcome.reason)
    return {
        "success": True,
        "redemption_id": outcome.redemption_id,
        "discount_amount": result.discount_amount,
        "final_total": result.final_total,
    }
