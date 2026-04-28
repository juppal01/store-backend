"""
ArtisanCo. Store — FastAPI Backend
Run locally:  uvicorn main:app --reload --port 8000
Deploy:       Railway, Render, or any Python host
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt, os
from dotenv import load_dotenv

from routes import products, categories, orders, settings, auth
from database import init_db

load_dotenv()
init_db()   # auto-create tables on first boot

app = FastAPI(title="ArtisanCo. Store API", version="1.0.0")

# ── CORS — allow your frontend domain ───────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",          # local dev
        os.getenv("FRONTEND_URL", "*"),   # production (set in .env)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────
app.include_router(auth.router,       prefix="/api/admin",      tags=["Auth"])
app.include_router(products.router,   prefix="/api/products",   tags=["Products"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
app.include_router(orders.router,     prefix="/api/orders",     tags=["Orders"])
app.include_router(settings.router,   prefix="/api/settings",   tags=["Settings"])

@app.get("/")
def root():
    return {"status": "ArtisanCo. API is running ✓"}

@app.get("/health")
def health():
    return {"status": "ok"}
