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

    # Column indexes: 0=id, 1=title, 2=description, 3=category, 4=tags, 5=media_type, 6=public_id, 7=cloudinary_url, 8=uploaded_at, 9=download_count
    title = row[1] if row[1] else "Novichok Media"
    description = row[2] if row[2] else ""
    media_type = row[5] if len(row) > 5 else "image"
    original_url = row[7] if len(row) > 7 else ""
    page_url = f"https://u-novichok.github.io/image.html?id={id}"

    # Truncate description for social previews (200 chars)
    og_description = (description[:197] + "...") if len(description) > 200 else description

    # Build a proper image thumbnail URL
    if media_type == "video":
        # Use the first frame of the video as a JPG thumbnail
        thumbnail_url = original_url.replace("/upload/", "/upload/so_1/")
        if thumbnail_url.endswith(".mp4"):
            thumbnail_url = thumbnail_url.rsplit(".", 1)[0] + ".jpg"
        elif not thumbnail_url.endswith(".jpg"):
            thumbnail_url += ".jpg"
    else:
        # For images, use a properly sized version
        thumbnail_url = original_url.replace("/upload/", "/upload/q_auto,f_auto,w_1200/")

    # Fallback if URL is empty
    if not thumbnail_url:
        thumbnail_url = "https://via.placeholder.com/1200x630.png?text=No+Preview"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <meta name="description" content="{og_description}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{og_description}">
    <meta property="og:image" content="{thumbnail_url}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:url" content="{page_url}">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="Novichok">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{og_description}">
    <meta name="twitter:image" content="{thumbnail_url}">"""

    # Video-specific tags (still useful for platforms that support them)
    if media_type == "video":
        html += f"""
    <meta property="og:video" content="{original_url}">
    <meta property="og:video:type" content="video/mp4">
    <meta property="og:video:width" content="1280">
    <meta property="og:video:height" content="720">
    <meta name="twitter:player" content="{original_url}">
    <meta name="twitter:player:width" content="1280">
    <meta name="twitter:player:height" content="720">"""

    # Short delay before redirect
    html += f"""
    <meta http-equiv="refresh" content="3;url={page_url}">
</head>
<body>
    <p>Redirecting to <a href="{page_url}">{title}</a>…</p>
</body>
</html>"""

    return HTMLResponse(content=html)
