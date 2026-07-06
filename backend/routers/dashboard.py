from fastapi import APIRouter, Depends
from database import get_db
from utils.security import get_current_admin

router = APIRouter(prefix="/admin", tags=["dashboard"])

@router.get("/dashboard")
def dashboard_stats(admin = Depends(get_current_admin)):
    db = get_db()
    total_images = 0
    total_videos = 0
    total_media = 0
    storage_used_bytes = 0

    # Get counts by media_type
    rows = db.execute("SELECT media_type, COUNT(*) as cnt FROM media GROUP BY media_type").fetchall()
    for row in rows:
        media_type = row[0]
        count = row[1]
        if media_type == "image":
            total_images = count
        elif media_type == "video":
            total_videos = count
        total_media += count

    # Storage: sum of file_size if column exists (optional, currently 0)
    # In future: ALTER TABLE media ADD COLUMN file_size INTEGER DEFAULT 0;
    try:
        size_rows = db.execute("SELECT SUM(file_size) FROM media").fetchone()
        if size_rows and size_rows[0]:
            storage_used_bytes = size_rows[0]
    except:
        pass  # column may not exist yet

    # Recent uploads (last 5)
    recent = db.execute(
        "SELECT id, title, cloudinary_url, media_type, uploaded_at FROM media ORDER BY uploaded_at DESC LIMIT 5"
    ).fetchall()
    recent_list = [{
        "id": r[0],
        "title": r[1],
        "url": r[2],
        "media_type": r[3],
        "uploaded_at": r[4]
    } for r in recent]

    return {
        "total_images": total_images,
        "total_videos": total_videos,
        "total_media": total_media,
        "storage_used_bytes": storage_used_bytes,
        "storage_used_mb": round(storage_used_bytes / (1024*1024), 2),
        "recent_uploads": recent_list,
        "render_status": "online",
        "d1_storage_mb": 2.1,          # placeholder, fetch from Cloudflare later
        "d1_requests_monthly": 98500,  # placeholder
        "visitors_today": 342,         # placeholder – add tracking later
        "visitors_month": 4589,
        "visitors_year": 32100,
        "shares_total": 8742
    }
