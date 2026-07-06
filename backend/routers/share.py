from fastapi import APIRouter, Depends, Request
from database import get_db
from utils.security import get_current_admin
from datetime import datetime, timedelta

router = APIRouter(prefix="/api", tags=["stats"])

# ────────────── PUBLIC TRACKING ENDPOINTS (no auth) ──────────────

@router.post("/track/view")
async def track_view(request: Request):
    """Record a page view. Body: { "page": "detail", "media_id": 123 } (optional)"""
    body = await request.json() if request.headers.get("content-type") == "application/json" else {}
    page = body.get("page", "unknown")
    media_id = body.get("media_id")
    db = get_db()
    db.execute("INSERT INTO page_views (page, media_id) VALUES (?, ?)", (page, media_id))
    return {"status": "ok"}

@router.post("/track/share")
async def track_share(request: Request):
    """Record a share event. Body: { "media_id": 123 }"""
    body = await request.json()
    media_id = body.get("media_id")
    if not media_id:
        return {"status": "error", "detail": "media_id required"}
    db = get_db()
    db.execute("INSERT INTO shares (media_id) VALUES (?)", (media_id,))
    return {"status": "ok"}

@router.post("/track/media-view")
async def track_media_view(request: Request):
    """Record a media detail view. Body: { "media_id": 123 }"""
    body = await request.json()
    media_id = body.get("media_id")
    if not media_id:
        return {"status": "error", "detail": "media_id required"}
    db = get_db()
    db.execute("INSERT INTO media_views (media_id) VALUES (?)", (media_id,))
    return {"status": "ok"}


# ────────────── ADMIN STATS (protected) ──────────────

@router.get("/admin/stats")
def get_admin_stats(admin = Depends(get_current_admin)):
    db = get_db()

    # --- Visitor counts ---
    today = datetime.utcnow().strftime("%Y-%m-%d")
    month_start = datetime.utcnow().strftime("%Y-%m-01")
    year_start = datetime.utcnow().strftime("%Y-01-01")

    visitors_today = db.execute(
        "SELECT COUNT(*) FROM page_views WHERE date(viewed_at) = ?", (today,)
    ).fetchone()[0]
    visitors_month = db.execute(
        "SELECT COUNT(*) FROM page_views WHERE date(viewed_at) >= ?", (month_start,)
    ).fetchone()[0]
    visitors_year = db.execute(
        "SELECT COUNT(*) FROM page_views WHERE date(viewed_at) >= ?", (year_start,)
    ).fetchone()[0]

    # --- Total shares ---
    total_shares = db.execute("SELECT COUNT(*) FROM shares").fetchone()[0]

    # --- Media counts ---
    total_images = db.execute("SELECT COUNT(*) FROM media WHERE media_type='image'").fetchone()[0]
    total_videos = db.execute("SELECT COUNT(*) FROM media WHERE media_type='video'").fetchone()[0]
    total_media = total_images + total_videos

    # --- Storage used (from file_size column) ---
    size_row = db.execute("SELECT SUM(file_size) FROM media").fetchone()
    storage_used_bytes = size_row[0] if size_row and size_row[0] else 0

    # --- Top 5 media by views ---
    top_media_rows = db.execute("""
        SELECT m.id, m.title, m.cloudinary_url, m.media_type, COUNT(v.id) as view_count
        FROM media m
        LEFT JOIN media_views v ON v.media_id = m.id
        GROUP BY m.id
        ORDER BY view_count DESC
        LIMIT 5
    """).fetchall()
    top_media = [{
        "id": r[0],
        "title": r[1],
        "url": r[2],
        "media_type": r[3],
        "views": r[4]
    } for r in top_media_rows]

    # --- Top 5 shared media ---
    top_shared_rows = db.execute("""
        SELECT m.id, m.title, m.cloudinary_url, m.media_type, COUNT(s.id) as share_count
        FROM media m
        LEFT JOIN shares s ON s.media_id = m.id
        GROUP BY m.id
        ORDER BY share_count DESC
        LIMIT 5
    """).fetchall()
    top_shared = [{
        "id": r[0],
        "title": r[1],
        "url": r[2],
        "media_type": r[3],
        "shares": r[4]
    } for r in top_shared_rows]

    return {
        "visitors_today": visitors_today,
        "visitors_month": visitors_month,
        "visitors_year": visitors_year,
        "total_shares": total_shares,
        "total_images": total_images,
        "total_videos": total_videos,
        "total_media": total_media,
        "storage_used_mb": round(storage_used_bytes / (1024*1024), 2),
        "top_media": top_media,
        "top_shared": top_shared,
        "render_status": "online",
        "d1_storage_mb": 2.1,           # still placeholder unless you integrate Cloudflare API
        "d1_requests_monthly": 98500    # placeholder
    }
