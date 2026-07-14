from fastapi import APIRouter, HTTPException
from database import get_db
from typing import Dict, Any

router = APIRouter()


def row_to_dict(row: dict) -> dict:
    return {
        "id": row.get("id"),
        "title": row.get("title", ""),
        "description": row.get("description", ""),
        "category": row.get("category", ""),
        "tags": row.get("tags", ""),
        "media_type": row.get("media_type", "image"),
        "cloudinary_public_id": row.get("cloudinary_public_id", ""),
        "cloudinary_url": row.get("cloudinary_url", ""),
        "uploaded_at": row.get("uploaded_at"),
        "download_count": row.get("download_count", 0),
        "country": row.get("country", ""),
        "source": row.get("source", ""),
        "resolution": row.get("resolution", ""),
        "capture_date": row.get("capture_date", ""),
        "file_size": row.get("file_size", 0),
        "parent_id": row.get("parent_id"),
    }


@router.get("/media", response_model=Dict[str, Any])
def list_media(
    category: str = None,
    search: str = None,
    skip: int = 0,
    limit: int = 24
):
    db = get_db()
    sql = "SELECT * FROM media"
    params = []
    conditions = []

    if category:
        conditions.append("category = ?")
        params.append(category)
    if search:
        conditions.append("(title LIKE ? OR tags LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY uploaded_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])

    rows = db.execute(sql, params).fetchall()
    items = [row_to_dict(r) for r in rows]

    count_sql = "SELECT COUNT(*) AS cnt FROM media"
    if conditions:
        count_sql += " WHERE " + " AND ".join(conditions)
    count_row = db.execute(count_sql, params[:-2] if conditions else []).fetchone()
    total = count_row["cnt"] if count_row else 0

    return {"total": total, "items": items}


@router.get("/media/{id}", response_model=Dict[str, Any])
def get_media(id: int):
    db = get_db()
    row = db.execute("SELECT * FROM media WHERE id = ?", (id,)).fetchone()
    if not row:
        raise HTTPException(404, "Media not found")
    return row_to_dict(row)
