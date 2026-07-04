from fastapi import APIRouter, HTTPException
from database import get_db
from schemas import LoginRequest, TokenResponse
from utils.security import verify_password, create_access_token

router = APIRouter(prefix="/admin", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    db = get_db()
    admin = db.execute("SELECT * FROM admins WHERE email = ?", (req.email,)).fetchone()
    if not admin or not verify_password(req.password, admin[2]):  # index 2 = password_hash
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token(data={"sub": admin[1], "role": admin[3]})  # email, role
    return TokenResponse(access_token=token)
