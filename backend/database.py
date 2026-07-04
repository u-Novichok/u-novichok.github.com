import os
import requests
from dotenv import load_dotenv

load_dotenv()

TURSO_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

if not TURSO_URL or not TURSO_TOKEN:
    raise Exception("Turso environment variables not set.")

# Build the base URL for the HTTP API
# TURSO_URL format: libsql://novichok-xxxx.turso.io
# We need https://novichok-xxxx.turso.io
base = TURSO_URL.replace("libsql://", "https://")
API_URL = f"{base}/v2/pipeline"
HEADERS = {
    "Authorization": f"Bearer {TURSO_TOKEN}",
    "Content-Type": "application/json"
}

class Database:
    """Simple wrapper around Turso's HTTP API."""
    def execute(self, sql, params=None):
        """Execute a SQL statement and return self for chaining."""
        payload = {"requests": [{"type": "execute", "stmt": {"sql": sql}, "params": params or []}]}
        resp = requests.post(API_URL, json=payload, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        if results:
            self._last_result = results[0]
        else:
            self._last_result = {}
        return self

    def fetchone(self):
        """Return first row of last result as tuple."""
        rows = self._last_result.get("response", {}).get("result", {}).get("rows", [])
        if rows:
            # Each row is a list of objects: [{"type":"text","value":"..."}, ...]
            return tuple(col.get("value") for col in rows[0])
        return None

    def fetchall(self):
        """Return all rows as list of tuples."""
        rows = self._last_result.get("response", {}).get("result", {}).get("rows", [])
        return [tuple(col.get("value") for col in row) for row in rows]

    @property
    def last_row_id(self):
        """Return last inserted row id."""
        return self._last_result.get("response", {}).get("result", {}).get("lastInsertRowid", None)

# Create a global instance (Turso API is stateless, so it's fine)
def get_db():
    return Database()
