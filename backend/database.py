import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
CF_DATABASE_ID = os.getenv("CF_DATABASE_ID")
CF_API_TOKEN = os.getenv("CF_API_TOKEN")

if not all([CF_ACCOUNT_ID, CF_DATABASE_ID, CF_API_TOKEN]):
    raise Exception("Missing Cloudflare D1 environment variables.")

API_URL = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/d1/database/{CF_DATABASE_ID}/query"
HEADERS = {
    "Authorization": f"Bearer {CF_API_TOKEN}",
    "Content-Type": "application/json"
}

class Database:
    def __init__(self):
        self._last_result = {}

    def execute(self, sql, params=None):
        body = {"sql": sql}
        if params:
            body["params"] = params
        try:
            resp = requests.post(API_URL, json=body, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("success"):
                raise Exception(f"D1 query failed: {data.get('errors')}")
            self._last_result = data
        except requests.exceptions.RequestException as e:
            raise Exception(f"D1 HTTP request failed: {e}")
        return self

    def fetchone(self):
        result = self._last_result.get("result", [])
        rows = result[0].get("results", []) if result else []
        if rows:
            # Return tuple of values in column order
            return tuple(rows[0].get(col) for col in rows[0])
        return None

    def fetchall(self):
        result = self._last_result.get("result", [])
        rows = result[0].get("results", []) if result else []
        if not rows:
            return []
        cols = list(rows[0].keys())
        return [tuple(row.get(c) for c in cols) for row in rows]

    @property
    def last_row_id(self):
        meta = self._last_result.get("result", [{}])[0].get("meta", {})
        return meta.get("last_row_id")

    @staticmethod
    def test_connection():
        db = Database()
        db.execute("SELECT 1 AS one")
        row = db.fetchone()
        print(f"D1 test row: {row}")
        if row and row[0] == 1:
            print("Cloudflare D1 connection successful.")
        else:
            raise Exception("D1 connection test failed.")

def get_db():
    return Database()
