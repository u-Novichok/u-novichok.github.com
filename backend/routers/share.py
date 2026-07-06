from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from database import get_db

router = APIRouter()

@router.get("/share/{id}", response_class=HTMLResponse)
def share_page(id: int):
    db = get_db()
    rows = db.execute("SELECT * FROM media WHERE id = ?", (id,)).fetchall()
    if not rows:
        raise HTTPException(404, "Media not found")
    row = rows[0]

    title = row[1] or "Novichok Media"
    description = (row[2] or "")[:200]
    image_url = row[7] or ""
    page_url = f"https://u-novichok.github.io/image.html?id={id}"

    if not image_url:
        image_url = "https://via.placeholder.com/1200x630.png?text=No+Preview"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{image_url}">
    <meta property="og:url" content="{page_url}">
    <meta name="twitter:card" content="summary_large_image">
    <meta http-equiv="refresh" content="0;url={page_url}">
</head>
<body><p>Redirecting…</p></body>
</html>"""
    return HTMLResponse(content=html)
