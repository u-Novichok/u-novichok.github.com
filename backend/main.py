from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from setup import create_tables
from routers import auth, media, admin
from utils.security import hash_password
from database import get_db
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Novichok API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(media.router)
app.include_router(admin.router)

@app.on_event("startup")
def startup():
    create_tables()
    # Seed admin user
    db = get_db()
    admin_email = os.getenv("ADMIN_EMAIL")
    if admin_email:
        existing = db.execute("SELECT id FROM admins WHERE email = ?", (admin_email,)).fetchone()
        if not existing:
            admin_password = os.getenv("ADMIN_PASSWORD", "changeme")
            hashed = hash_password(admin_password)
            db.execute("INSERT INTO admins (email, password_hash) VALUES (?, ?)", (admin_email, hashed))
            print("Admin user created.")

@app.get("/")
def root():
    return {"status": "ok", "service": "Novichok API"}
