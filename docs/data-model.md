# Data Model — Coupon & Promotions Engine

```sql
CREATE TABLE IF NOT EXISTS coupons (id TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE, discount_type TEXT NOT NULL, discount_value REAL NOT NULL, min_purchase REAL DEFAULT 0, max_uses INTEGER DEFAULT 1, current_uses INTEGER DEFAULT 0, expires_at TEXT, is_active INTEGER DEFAULT 1, created_at TEXT DEFAULT (datetime('now')));
```
