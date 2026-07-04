import os
import requests
import json
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
        self._last_raw = {}

    def execute(self, sql, params=None):
        payload = {
            "requests": [
                {"type": "execute", "stmt": {"sql": sql}, "params": params or []}
            ]
        }
        try:
            resp = requests.post(API_URL, json=payload, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            self._last_raw = data
            results = data.get("results", [])
            self._last_result = results[0] if results else {}

            # Check for Turso-level error
            if self._last_result.get("type") == "error":
                error_msg = self._last_result.get("response", {}).get("error", "Unknown Turso error")
                raise Exception(f"Turso query error: {error_msg}")

            # Print raw response for write operations
            if not sql.strip().upper().startswith("SELECT"):
                print("RAW WRITE RESPONSE:")
                print(json.dumps(data, indent=2))
                affected = self._last_result.get("response", {}).get("result", {}).get("affected_row_count")
                last_id = self._last_result.get("response", {}).get("result", {}).get("last_insert_rowid")
                print(f"Rows affected: {affected}, Last insert ID: {last_id}")

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
        db = Database()
        db.execute("SELECT 1")
        print("RAW TURSO RESPONSE:")
        print(json.dumps(db._last_raw, indent=2))
        row = db.fetchone()
        print(f"PARSED ROW: {row}")
        if row and row[0] == "1":
            print("Turso connection successful.")
        else:
            raise Exception(f"Turso connection test failed. Parsed row: {row}")

def get_db():
    return Database()
