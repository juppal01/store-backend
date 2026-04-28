"""
categories.py — CRUD for product categories
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db, Category
from routes.auth import verify_token

router = APIRouter()
bearer = HTTPBearer(auto_error=False)

class CategoryIn(BaseModel):
    name:    str
    visible: Optional[bool] = True

@router.get("")
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).filter(Category.visible == True).order_by(Category.name).all()

@router.get("/all")
def list_all_categories(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
):
    verify_token(credentials)
    return db.query(Category).order_by(Category.name).all()

@router.post("", status_code=201)
def create_category(
    data: CategoryIn,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
):
    verify_token(credentials)
    if db.query(Category).filter(Category.name == data.name).first():
        raise HTTPException(400, "Category already exists")
    c = Category(**data.dict()); db.add(c); db.commit(); db.refresh(c)
    return c

@router.put("/{cat_id}")
def update_category(
    cat_id: int, data: CategoryIn,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
):
    verify_token(credentials)
    c = db.query(Category).filter(Category.id == cat_id).first()
    if not c: raise HTTPException(404, "Category not found")
    c.name = data.name; c.visible = data.visible
    db.commit(); db.refresh(c); return c

@router.delete("/{cat_id}", status_code=204)
def delete_category(
    cat_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
):
    verify_token(credentials)
    c = db.query(Category).filter(Category.id == cat_id).first()
    if not c: raise HTTPException(404, "Category not found")
    db.delete(c); db.commit()
