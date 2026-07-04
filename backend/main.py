import sys
import traceback

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from setup import create_tables
    from routers import auth, media, admin
    from utils.security import hash_password
    from database import get_db, Database
    import os
    from dotenv import load_dotenv

    load_dotenv()

    app = FastAPI(title="Novichok API")

    # CORS – allow your GitHub Pages frontend (or * for now)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include route modules
    app.include_router(auth.router)
    app.include_router(media.router)
    app.include_router(admin.router)

    @app.get("/")
    def root():
        return {"status": "ok", "service": "Novichok API"}

    @app.on_event("startup")
    def startup():
        try:
            Database.test_connection()
            create_tables()

            db = get_db()
            admin_email = os.getenv("ADMIN_EMAIL")
            admin_password = os.getenv("ADMIN_PASSWORD", "changeme")

            if admin_email:
                existing = db.execute(
                    "SELECT id FROM admins WHERE email = ?", (admin_email,)
                ).fetchone()
                print(f"DEBUG: Existing admin check = {existing}")

                if not existing:
                    hashed = hash_password(admin_password)
                    print(f"DEBUG: Hashed password = {hashed}")
                    db.execute(
                        "INSERT INTO admins (email, password_hash) VALUES (?, ?)",
                        (admin_email, hashed),
                    )
                    # Immediately verify the insert persisted
                    check = db.execute(
                        "SELECT * FROM admins WHERE email = ?", (admin_email,)
                    ).fetchone()
                    print(f"DEBUG: After INSERT, admin row = {check}")
                    if check:
                        print("Admin user created.")
                    else:
                        print("ERROR: Admin INSERT did not persist!")
                else:
                    hashed = hash_password(admin_password)
                    db.execute(
                        "UPDATE admins SET password_hash = ? WHERE email = ?",
                        (hashed, admin_email),
                    )
                    print("Admin password updated.")

            print("Startup complete.")

        except Exception as e:
            print("STARTUP ERROR:")
            traceback.print_exc()
            raise

except Exception as e:
    print("FATAL ERROR during app creation:")
    traceback.print_exc()
    sys.exit(1)
