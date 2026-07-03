import os
import sqlite3

DB_PATH = os.getenv("DB_PATH", ":memory:")

_conn: sqlite3.Connection | None = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS coupons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL CHECK(type IN ('PERCENTAGE','FIXED_AMOUNT','FREE_SHIPPING','BUY_X_GET_Y')),
    value REAL NOT NULL DEFAULT 0,
    min_order_value REAL NOT NULL DEFAULT 0,
    max_uses INTEGER,
    per_customer_limit INTEGER NOT NULL DEFAULT 1,
    applicable_categories TEXT,
    buy_quantity INTEGER,
    get_quantity INTEGER,
    active INTEGER NOT NULL DEFAULT 1,
    valid_from TEXT NOT NULL,
    valid_until TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS redemptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coupon_id INTEGER NOT NULL REFERENCES coupons(id),
    customer_id TEXT NOT NULL,
    order_id TEXT NOT NULL,
    discount_amt REAL NOT NULL,
    redeemed_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_redemptions_coupon ON redemptions(coupon_id, customer_id);
"""


def get_db() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        if DB_PATH != ":memory:":
            os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.executescript(SCHEMA)
        _conn.commit()
    return _conn
