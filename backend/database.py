import os
from turso import Client
from dotenv import load_dotenv

load_dotenv()

TURSO_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

if not TURSO_URL or not TURSO_TOKEN:
    raise Exception("Turso environment variables not set.")

# Extract host from URL (strip libsql://)
host = TURSO_URL.replace("libsql://", "")

client = Client(host=host, auth_token=TURSO_TOKEN)

def get_db():
    """Return a database connection (the client)."""
    return client
