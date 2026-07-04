from fastapi import APIRouter, HTTPException
from database import get_db
from schemas import LoginRequest, TokenResponse
from utils.security import verify_password, create_access_token
import traceback

router = APIRouter(prefix="/admin", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    try:
        db = get_db()
        admin = db.execute(
            "SELECT * FROM admins WHERE email = ?", (req.email,)
        ).fetchone()
        if not admin:
            print("LOGIN DEBUG: No admin found with that email")
            raise HTTPException(401, "Invalid credentials")
        stored_hash = admin[2]
        print(f"LOGIN DEBUG: Stored hash = {stored_hash}")
        password_ok = verify_password(req.password, stored_hash)
        print(f"LOGIN DEBUG: Password match = {password_ok}")
        if not password_ok:
            raise HTTPException(401, "Invalid credentials")
        token = create_access_token(data={"sub": admin[1], "role": admin[3]})
        return TokenResponse(access_token=token)
    except Exception as e:
        print("LOGIN ERROR:")
        traceback.print_exc()
        raise
