from fastapi import APIRouter, HTTPException
from database import get_db

router = APIRouter()

@router.get("/groups/{parent_id}")
def get_media_group(parent_id: int):
    db = get_db()
    # Fetch parent + all children ordered by sort_order
    parent = db.execute(
        "SELECT * FROM media WHERE id = ?", (parent_id,)
    ).fetchone()
    
    if not parent:
        raise HTTPException(404, "Post not found")
    
    children = db.execute(
        "SELECT * FROM media WHERE parent_id = ? OR id = ? ORDER BY sort_order ASC",
        (parent_id, parent_id)
    ).fetchall()
    
    # Format results
    items = []
    for row in children:
        items.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "media_type": row[5] if len(row) > 5 else "image",
            "cloudinary_public_id": row[6] if len(row) > 6 else None,
            "cloudinary_url": row[7] if len(row) > 7 else None,
            "sort_order": row[10] if len(row) > 10 else 0,
        })
    
    return {"parent_id": parent_id, "items": items, "count": len(items)}
