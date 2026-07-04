from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from models import Admin
from utils.security import hash_password
from routers import auth, media, admin
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Novichok API")

# CORS – allow your GitHub Pages domain (or * for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # In production, restrict to your frontend URL
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
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Seed admin user
    db = SessionLocal()
    admin_email = os.getenv("ADMIN_EMAIL")
    if admin_email:
        existing = db.query(Admin).filter(Admin.email == admin_email).first()
        if not existing:
            admin_password = os.getenv("ADMIN_PASSWORD", "changeme")
            hashed = hash_password(admin_password)
            db.add(Admin(email=admin_email, password_hash=hashed, role="admin"))
            db.commit()
    db.close()

@app.get("/")
def root():
    return {"status": "ok", "service": "Novichok API"}
