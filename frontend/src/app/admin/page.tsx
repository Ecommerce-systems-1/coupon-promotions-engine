1.  mkdir coupon-promotions-engine && cd coupon-promotions-engine
2.  git init && git checkout -b main
3.  Create requirements.txt: fastapi uvicorn[standard] pytest httpx python-multipart
4.  Write backend/database.py: init_db() creates coupons + redemptions tables + view
5.  Write backend/schemas.py: CouponCreate, CouponOut, CartItem, ValidateRequest,
    ValidateResponse, RedeemRequest, RedeemResponse
6.  Run: python -m pytest backend/tests/test_validator.py — expect FAIL
7.  Write backend/services/validator.py — tests must pass
8.  Run: python -m pytest backend/tests/test_calculator.py — expect FAIL
9.  Write backend/services/calculator.py — tests must pass
10. Run: python -m pytest backend/tests/test_redemption.py — expect FAIL
11. Write backend/services/redemption.py using BEGIN IMMEDIATE — tests must pass
12. Run: python -m pytest backend/tests/test_coupons_router.py — expect FAIL
13. Write backend/routers/coupons.py: POST /coupons, GET /coupons,
    POST /coupons/validate (no DB write), POST /coupons/redeem (atomic write)
14. Write backend/main.py: lifespan→init_db+seed; mount routers under /api
15. Write backend/seed.py: 20 coupons (5 of each type) + 500 redemption records
16. Run: python -m pytest backend/tests/ — ALL must pass
17. cd frontend && npx create-next-app@14 . --typescript --tailwind --app
18. Write frontend/src/lib/api.ts
19. Write CartSimulator.tsx, CouponInput.tsx, DiscountBreakdown.tsx, CouponAdminForm.tsx
20. Write page.tsx (cart simulator) and admin/page.tsx (coupon management)
21. Set next.config.js: output: 'export', distDir: '../backend/static'
22. Run: npm run build
23. Write Dockerfile: FROM python:3.11-slim; copy backend; pip install; copy static; CMD uvicorn
24. Write .github/workflows/ci.yml
25. docker build -t coupon-engine . && docker run -p 7860:7860 coupon-engine
26. Verify PERCENTAGE: add $100 cart, apply 20% coupon → discount $20
27. Verify FIXED_AMOUNT: add $50 cart, apply $100 coupon → discount capped at $50
28. Verify FREE_SHIPPING: add items with $15 shipping → shipping waived
29. Verify BUY_X_GET_Y (buy 2 get 1): 3 items $50/$30/$20 → cheapest $20 free
30. Verify max_uses: create coupon max_uses=1, redeem once, second redeem → 409
31. git add -A && git commit -m "feat: coupon and promotions engine"
32. gh repo create coupon-promotions-engine --public && git push -u origin main