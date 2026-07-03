import sqlite3, pytest
from app.services.redemption import RedemptionService

@pytest.fixture
def db(tmp_path):
    conn = sqlite3.connect(str(tmp_path / "test.db"))
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE coupons (id INTEGER PRIMARY KEY, max_uses INTEGER, code TEXT, per_customer_limit INTEGER DEFAULT 1)""")
    conn.execute("""CREATE TABLE redemptions (id INTEGER PRIMARY KEY AUTOINCREMENT, coupon_id INTEGER, customer_id TEXT, order_id TEXT, discount_amt REAL, redeemed_at TEXT DEFAULT (datetime('now')))""")
    conn.execute("INSERT INTO coupons VALUES (1, 2, 'TEST10', 5)")
    conn.commit()
    yield conn
    conn.close()

def test_first_redemption_succeeds(db):
    svc = RedemptionService()
    result = svc.redeem(db, coupon_id=1, customer_id="c1", order_id="ord-1", discount_amt=10.0)
    assert result.success is True

def test_exceeds_max_uses(db):
    svc = RedemptionService()
    svc.redeem(db, coupon_id=1, customer_id="c1", order_id="ord-1", discount_amt=10.0)
    svc.redeem(db, coupon_id=1, customer_id="c2", order_id="ord-2", discount_amt=10.0)
    result = svc.redeem(db, coupon_id=1, customer_id="c3", order_id="ord-3", discount_amt=10.0)
    assert result.success is False
    assert "limit" in result.reason.lower()