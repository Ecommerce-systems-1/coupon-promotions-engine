from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pathlib
from app.database import get_db
from app.routers import coupons

app = FastAPI(title="Coupon & Promotions Engine")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(coupons.router)

get_db()  # initialise schema at import; tests use TestClient without lifespan


@app.get("/health")
def health():
    db = get_db()
    coupons_count = db.execute("SELECT COUNT(*) FROM coupons").fetchone()[0]
    redemptions_count = db.execute("SELECT COUNT(*) FROM redemptions").fetchone()[0]
    return {"status": "ok", "coupons": coupons_count, "redemptions": redemptions_count}


static_dir = pathlib.Path("/app/frontend/out")
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
