import sys
import traceback

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from setup import create_tables
    from routers import auth, media, admin
    from database import get_db, Database
    from utils.security import verify_password, hash_password, create_access_token
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

    # ========== TEMPORARY BYPASS (remove after fixing Turso writes) ==========
    @app.post("/admin/login-bypass")
    def login_bypass(secret_key: str):
        """Return a valid admin JWT if the provided secret matches ADMIN_BYPASS_KEY env variable."""
        expected = os.getenv("ADMIN_BYPASS_KEY", "novichok-bypass-2026")
        if secret_key != expected:
            return {"detail": "Invalid secret key"}, 401
        token = create_access_token(data={"sub": "bypass-admin", "role": "admin"})
        return {"access_token": token, "token_type": "bearer"}
    # =========================================================================

    # ---- Optional debug endpoints (keep them for now) ----
    @app.get("/debug/list-admins")
    def list_admins():
        db = get_db()
        rows = db.execute("SELECT * FROM admins").fetchall()
        return {"admins": rows}

    @app.get("/debug/check-password")
    def check_password(password: str):
        db = get_db()
        rows = db.execute("SELECT * FROM admins").fetchall()
        for row in rows:
            if row[1] == "adeepag13@gmail.com":
                stored_hash = row[2]
                ok = verify_password(password, stored_hash)
                return {"found": True, "stored_hash": stored_hash, "password_match": ok}
        return {"found": False, "error": "Admin not found in database"}
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
