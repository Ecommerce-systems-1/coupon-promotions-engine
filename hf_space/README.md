---
title: Coupon & Promotions Engine
emoji: 🏷️
colorFrom: yellow
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# Coupon & Promotions Engine

PERCENTAGE, FIXED_AMOUNT, FREE_SHIPPING, and BUY_X_GET_Y coupons with validation rules and redemption limits.

The landing page is an interactive API console — click any endpoint to call the live API.

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/coupons` | Create a coupon |
| GET | `/api/coupons` | List coupons |
| POST | `/api/coupons/validate` | Validate against a cart |
| POST | `/api/coupons/redeem` | Redeem (atomic, usage-capped) |

## Stack

Python 3.11 · FastAPI · SQLite · Pydantic v2 · Next.js 14 (static export) · Tailwind CSS · Docker
