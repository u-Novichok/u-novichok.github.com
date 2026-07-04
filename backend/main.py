import sys
import traceback

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from setup import create_tables
    from routers import auth, media, admin
    from database import get_db, Database
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

    app.include_router(auth.router)
    app.include_router(media.router)
    app.include_router(admin.router)

    @app.get("/")
    def root():
        return {"status": "ok", "service": "Novichok API"}

    # --- TEMPORARY DEBUG ENDPOINTS (remove after use) ---
    @app.get("/debug/list-admins")
    def list_admins():
        db = get_db()
        rows = db.execute("SELECT * FROM admins").fetchall()
        return {"admins": rows}

    @app.post("/debug/check-password")
    def check_password(password: str = Form(...)):
        db = get_db()
        admin = db.execute(
            "SELECT * FROM admins WHERE email = ?", ("adeepag13@gmail.com",)
        ).fetchone()
        if not admin:
            return {"error": "Admin not found"}
        stored_hash = admin[2]
        from utils.security import verify_password
        ok = verify_password(password, stored_hash)
        return {"stored_hash": stored_hash, "match": ok}
    # ------------------------------------------------------

    @app.on_event("startup")
    def startup():
        try:
            Database.test_connection()
            create_tables()
            print("Startup complete.")
        except Exception as e:
            print("STARTUP ERROR:")
            traceback.print_exc()
            raise

except Exception as e:
    print("FATAL ERROR during app creation:")
    traceback.print_exc()
    sys.exit(1)
