from fastapi import APIRouter, HTTPException, Depends
from database import SessionLocal
from models import Admin
from schemas import LoginRequest, TokenResponse
from utils.security import verify_password, create_access_token
from utils.security import get_current_admin   # re-export for admin routes

router = APIRouter(prefix="/admin", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    db = SessionLocal()
    admin = db.query(Admin).filter(Admin.email == req.email).first()
    db.close()
    if not admin or not verify_password(req.password, admin.password_hash):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token(data={"sub": admin.email, "role": admin.role})
    return TokenResponse(access_token=token)
