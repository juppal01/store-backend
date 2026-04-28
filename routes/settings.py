"""settings.py — SEO settings CRUD"""
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db, SeoSettings
from routes.auth import verify_token

router = APIRouter()
bearer = HTTPBearer(auto_error=False)

class SEOIn(BaseModel):
    store_title: Optional[str] = ""
    meta_desc:   Optional[str] = ""
    keywords:    Optional[str] = ""
    canonical:   Optional[str] = ""
    ga_id:       Optional[str] = ""
    pixel_id:    Optional[str] = ""
    og_image:    Optional[str] = ""

@router.get("/seo")
def get_seo(db: Session = Depends(get_db)):
    s = db.query(SeoSettings).first()
    return s or {}

@router.put("/seo")
def update_seo(
    data: SEOIn,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
):
    verify_token(credentials)
    s = db.query(SeoSettings).first()
    if not s:
        s = SeoSettings(); db.add(s)
    for k, v in data.dict(exclude_unset=True).items():
        setattr(s, k, v)
    db.commit(); db.refresh(s)
    return s
