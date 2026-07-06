from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from database import get_db

router = APIRouter()

@router.get("/debug/{id}")
def debug_share(id: int):
    db = get_db()
    rows = db.execute("SELECT * FROM media WHERE id = ?", (id,)).fetchall()
    if not rows:
        raise HTTPException(404, "Media not found")
    row = rows[0]
    return {
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "media_type": row[5] if len(row) > 5 else "unknown",
        "cloudinary_url": row[7] if len(row) > 7 else "unknown",
    }

@router.get("/share/{id}", response_class=HTMLResponse)
def share_page(id: int):
    db = get_db()
    rows = db.execute("SELECT * FROM media WHERE id = ?", (id,)).fetchall()
    
    if not rows:
        raise HTTPException(404, "Media not found")
    
    row = rows[0]
    
    title = row[1] if row[1] else "Novichok Media"
    description = row[2] if row[2] else ""
    media_type = row[5] if len(row) > 5 else "image"
    image_url = row[7] if len(row) > 7 else ""
    page_url = f"https://u-novichok.github.io/image.html?id={id}"
    
    if not image_url:
        image_url = "https://via.placeholder.com/1200x630.png?text=No+Image"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{image_url}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:url" content="{page_url}">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="Novichok">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{image_url}">"""
    
    # Video support
    if media_type == "video":
        html += f"""
    <meta property="og:video" content="{image_url}">
    <meta property="og:video:type" content="video/mp4">
    <meta property="og:video:width" content="1280">
    <meta property="og:video:height" content="720">
    <meta name="twitter:card" content="player">
    <meta name="twitter:player" content="{image_url}">
    <meta name="twitter:player:width" content="1280">
    <meta name="twitter:player:height" content="720">"""
    
    html += f"""
    <meta http-equiv="refresh" content="0;url={page_url}">
</head>
<body>
    <p>Redirecting to <a href="{page_url}">{title}</a>…</p>
</body>
</html>"""
    
    return HTMLResponse(content=html)
