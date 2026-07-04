from fastapi import APIRouter, HTTPException, Query
from database import get_db
from typing import Dict, Any, List
from schemas import MediaOut
import json

router = APIRouter()

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
    items = []
    for row in rows:
        items.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "category": row[3],
            "tags": row[4],
            "media_type": row[5],
            "cloudinary_public_id": row[6],
            "cloudinary_url": row[7],
            "uploaded_at": row[8],
            "download_count": row[9]
        })

    # Count total
    count_sql = "SELECT COUNT(*) FROM media"
    if conditions:
        count_sql += " WHERE " + " AND ".join(conditions)
    total = db.execute(count_sql, params[:-2] if conditions else []).fetchone()[0]

    return {"total": total, "items": items}

@router.get("/media/{id}", response_model=MediaOut)
def get_media(id: int):
    db = get_db()
    row = db.execute("SELECT * FROM media WHERE id = ?", (id,)).fetchone()
    if not row:
        raise HTTPException(404, "Media not found")
    return MediaOut(
        id=row[0],
        title=row[1],
        description=row[2],
        category=row[3],
        tags=row[4],
        media_type=row[5],
        cloudinary_public_id=row[6],
        cloudinary_url=row[7],
        uploaded_at=row[8],
        download_count=row[9]
    )
