from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import get_db
from utils.security import hash_password, get_current_admin

router = APIRouter(prefix="/admin", tags=["admin_users"])

class CreateAdminRequest(BaseModel):
    email: str
    password: str

@router.get("/users")
def list_admins(admin = Depends(get_current_admin)):
    db = get_db()
    rows = db.execute("SELECT id, email, role, created_at FROM admins ORDER BY created_at DESC").fetchall()
    users = []
    for row in rows:
        users.append({
            "id": row.get("id"),
            "email": row.get("email"),
            "role": row.get("role", "admin"),
            "created_at": row.get("created_at"),
        })
    return users

@router.post("/users")
def create_admin(req: CreateAdminRequest, admin = Depends(get_current_admin)):
    db = get_db()
    existing = db.execute("SELECT id FROM admins WHERE email = ?", (req.email,)).fetchone()
    if existing:
        raise HTTPException(400, "An admin with this email already exists")
    hashed = hash_password(req.password)
    db.execute("INSERT INTO admins (email, password_hash) VALUES (?, ?)", (req.email, hashed))
    new_id = db.last_row_id
    return {"message": "Admin created", "id": new_id}
