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
            print("Startup complete.")
        except Exception as e:
            print("STARTUP ERROR:")
            traceback.print_exc()
            raise

except Exception as e:
    print("FATAL ERROR during app creation:")
    traceback.print_exc()
    sys.exit(1)
