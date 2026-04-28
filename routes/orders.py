"""orders.py"""
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db, Order
from routes.auth import verify_token

router = APIRouter()
bearer = HTTPBearer(auto_error=False)

@router.get("")
def list_orders(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
):
    verify_token(credentials)
    return db.query(Order).order_by(Order.created_at.desc()).limit(100).all()
