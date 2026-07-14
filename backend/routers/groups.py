from fastapi import APIRouter, HTTPException
from database import get_db

router = APIRouter()


@router.get("/groups/{parent_id}")
def get_media_group(parent_id: int):
    db = get_db()

    parent = db.execute(
        "SELECT * FROM media WHERE id = ?", (parent_id,)
    ).fetchone()

    if not parent:
        raise HTTPException(404, "Post not found")

    children = db.execute(
        "SELECT * FROM media WHERE parent_id = ? OR id = ? ORDER BY sort_order ASC",
        (parent_id, parent_id)
    ).fetchall()

    items = []
    for row in children:
        items.append({
            "id": row.get("id"),
            "title": row.get("title", ""),
            "description": row.get("description", ""),
            "media_type": row.get("media_type", "image"),
            "cloudinary_public_id": row.get("cloudinary_public_id", ""),
            "cloudinary_url": row.get("cloudinary_url", ""),
            "country": row.get("country", ""),
            "source": row.get("source", ""),
            "capture_date": row.get("capture_date", ""),
            "resolution": row.get("resolution", ""),
            "sort_order": row.get("sort_order", 0),
        })

    return {"parent_id": parent_id, "items": items, "count": len(items)}
