from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import jwt, os, datetime

router = APIRouter()

ADMIN_EMAIL    = os.getenv("ADMIN_EMAIL",    "admin@yourstore.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change_me_in_env")
JWT_SECRET     = os.getenv("JWT_SECRET",     "super_secret_key_change_me")

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(req: LoginRequest):
    if req.email != ADMIN_EMAIL or req.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode(
        {"sub": "admin", "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)},
        JWT_SECRET, algorithm="HS256"
    )
    return {"token": token}

# ── Token verification (used by other routes) ──
def verify_token(credentials):
    try:
        jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
