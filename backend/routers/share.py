from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from database import get_db

router = APIRouter()

@router.get("/share/{id}", response_class=HTMLResponse)
def share_page(id: int):
    db = get_db()
    image = db.execute("SELECT * FROM media WHERE id = ?", (id,)).fetchone()
    if not image:
        raise HTTPException(404, "Image not found")

    # Build meta values from the image record (adjust indices if your column order differs)
    # Assuming order: id, title, description, category, tags, media_type, cloudinary_public_id, cloudinary_url, uploaded_at, download_count
    title = image[1] or "Novichok Image"
    description = image[2] or ""
    image_url = image[7]  # cloudinary_url
    page_url = f"https://u-novichok.github.io/image.html?id={id}"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{image_url}">
    <meta property="og:url" content="{page_url}">
    <meta property="og:type" content="article">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{image_url}">
    <meta http-equiv="refresh" content="2;url={page_url}">
</head>
<body>
    <p>Redirecting to <a href="{page_url}">{title}</a>…</p>
</body>
</html>"""
    return html
