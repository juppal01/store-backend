from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from database import get_db, Product
from routes.auth import verify_token

router  = APIRouter()
bearer  = HTTPBearer(auto_error=False)

# ── Schemas ───────────────────────────────────────────────────────
class ProductIn(BaseModel):
    name:         str
    description:  Optional[str]  = ""
    category:     Optional[str]  = ""
    price:        float
    mrp:          Optional[float] = None
    cost_price:   Optional[float] = None
    stock:        Optional[int]  = 0
    sku:          Optional[str]  = None
    image_url:    Optional[str]  = ""
    emoji:        Optional[str]  = "📦"
    tags:         Optional[str]  = ""
    badge:        Optional[str]  = ""
    status:       Optional[str]  = "active"
    featured:     Optional[bool] = False
    gst:          Optional[str]  = "0%"
    seo_title:    Optional[str]  = ""
    seo_desc:     Optional[str]  = ""
    weight:       Optional[float] = None
    dimensions:   Optional[str]  = None
    low_stock_alert: Optional[int] = 10

class BulkAction(BaseModel):
    ids:    List[int]
    action: str   # "active" | "draft" | "delete"

# ── GET all products (public — supports ?status=active filter) ──
@router.get("")
def list_products(
    status:   Optional[str] = None,
    category: Optional[str] = None,
    search:   Optional[str] = None,
    db:       Session       = Depends(get_db)
):
    q = db.query(Product)
    if status:   q = q.filter(Product.status == status)
    if category: q = q.filter(Product.category == category)
    if search:   q = q.filter(Product.name.ilike(f"%{search}%"))
    return q.order_by(Product.created_at.desc()).all()

# ── GET single product ────────────────────────────────────────────
@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "Product not found")
    return p

# ── CREATE product (admin only) ───────────────────────────────────
@router.post("", status_code=201)
def create_product(
    data: ProductIn,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db:   Session = Depends(get_db)
):
    verify_token(credentials)
    # Auto-set mrp if not provided
    payload       = data.dict()
    payload["mrp"] = payload["mrp"] or payload["price"]

    # Ensure SKU uniqueness
    if payload.get("sku"):
        exists = db.query(Product).filter(Product.sku == payload["sku"]).first()
        if exists:
            payload["sku"] = None  # clear duplicate SKU silently

    p = Product(**payload)
    db.add(p); db.commit(); db.refresh(p)
    return p

# ── UPDATE product (admin only) ───────────────────────────────────
@router.put("/{product_id}")
def update_product(
    product_id: int,
    data: ProductIn,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db:   Session = Depends(get_db)
):
    verify_token(credentials)
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "Product not found")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit(); db.refresh(p)
    return p

# ── DELETE product (admin only) ───────────────────────────────────
@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db:   Session = Depends(get_db)
):
    verify_token(credentials)
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "Product not found")
    db.delete(p); db.commit()

# ── BULK action (admin only) ──────────────────────────────────────
@router.post("/bulk")
def bulk_action(
    data: BulkAction,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db:   Session = Depends(get_db)
):
    verify_token(credentials)
    products = db.query(Product).filter(Product.id.in_(data.ids)).all()

    if data.action == "delete":
        for p in products:
            db.delete(p)
    elif data.action in ("active", "draft"):
        for p in products:
            p.status = data.action
    else:
        raise HTTPException(400, "Unknown action")

    db.commit()
    return {"updated": len(products)}
