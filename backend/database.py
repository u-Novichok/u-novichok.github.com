import os
import requests
from dotenv import load_dotenv

load_dotenv()

TURSO_URL = os.getenv("TURSO_DATABASE_URL", "")
TURSO_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")

if not TURSO_URL or not TURSO_TOKEN:
    raise Exception("Missing TURSO_DATABASE_URL or TURSO_AUTH_TOKEN environment variable.")

base = TURSO_URL.replace("libsql://", "https://")
API_URL = f"{base}/v2/pipeline"
HEADERS = {
    "Authorization": f"Bearer {TURSO_TOKEN}",
    "Content-Type": "application/json"
}

class Database:
    def __init__(self):
        self._last_result = {}

    def execute(self, sql, params=None):
        payload = {
            "requests": [
                {"type": "execute", "stmt": {"sql": sql}, "params": params or []}
            ]
        }
        try:
            resp = requests.post(API_URL, json=payload, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            self._last_result = data.get("results", [{}])[0]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Turso HTTP request failed: {e}")
        return self

    def fetchone(self):
        rows = self._last_result.get("response", {}).get("result", {}).get("rows", [])
        if rows:
            return tuple(col.get("value") for col in rows[0])
        return None

    def fetchall(self):
        rows = self._last_result.get("response", {}).get("result", {}).get("rows", [])
        return [tuple(col.get("value") for col in row) for row in rows]

    @property
    def last_row_id(self):
        return self._last_result.get("response", {}).get("result", {}).get("lastInsertRowid")

    @staticmethod
    def test_connection():
        """Quick test to verify the Turso API works."""
        db = Database()
        db.execute("SELECT 1")
        row = db.fetchone()
        if row and row[0] == 1:
            print("Turso connection successful.")
        else:
            raise Exception("Turso connection test returned unexpected result.")

def get_db():
    return Database()
