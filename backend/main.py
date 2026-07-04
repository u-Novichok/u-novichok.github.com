import sys
import traceback

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from setup import create_tables
    from routers import auth, media, admin
    from database import get_db, Database
    from utils.security import verify_password, hash_password
    import os
    from dotenv import load_dotenv

    load_dotenv()

    app = FastAPI(title="Novichok API")

    # CORS – allow frontend access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Public and admin routers
    app.include_router(auth.router)
    app.include_router(media.router)
    app.include_router(admin.router)

    @app.get("/")
    def root():
        return {"status": "ok", "service": "Novichok API"}

    # ======================
    # TEMPORARY DEBUG ROUTES – REMOVE AFTER LOGIN SUCCESS
    # ======================

    @app.get("/debug/list-admins")
    def list_admins():
        """Return all admin rows so you can see the exact stored data."""
        db = get_db()
        rows = db.execute("SELECT * FROM admins").fetchall()
        return {"admins": rows}

    @app.get("/debug/check-password")
    def check_password(password: str):
        """Check if the given password matches the stored hash."""
        db = get_db()
        rows = db.execute("SELECT * FROM admins").fetchall()
        for row in rows:
            # row[1] is email
            if row[1] == "adeepag13@gmail.com":
                stored_hash = row[2]
                ok = verify_password(password, stored_hash)
                return {
                    "found": True,
                    "stored_hash": stored_hash,
                    "password_match": ok
                }
        return {"found": False, "error": "Admin not found in database"}

    @app.post("/debug/update-admin-password")
    def update_admin_password(new_password: str):
        """Re-hash the password using the server's bcrypt and update the stored hash."""
        db = get_db()
        hashed = hash_password(new_password)
        db.execute(
            "UPDATE admins SET password_hash = ? WHERE email = ?",
            (hashed, "adeepag13@gmail.com")
        )
        return {
            "message": "Password hash updated. Use this password to login.",
            "new_hash": hashed
        }

    # ======================
    # END DEBUG
    # ======================

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
