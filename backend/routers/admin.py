from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from database import get_db
from utils.cloudinary_upload import upload_media, delete_media
from utils.security import get_current_admin
from schemas import MediaUpdate
import traceback

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/upload")
async def upload_media_route(
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form(""),
    country: str = Form(""),
    source: str = Form(""),
    capture_date: str = Form(""),
    resolution: str = Form(""),
    tags: str = Form(""),
    parent_id: int = Form(None),
    file: UploadFile = File(...),
    admin = Depends(get_current_admin)
):
    contents = await file.read()
    if not (file.content_type.startswith("image/") or file.content_type.startswith("video/")):
        raise HTTPException(400, "Only image and video files are allowed")
    try:
        public_id, secure_url = upload_media(contents, file.content_type, folder="novichok")
    except Exception as e:
        raise HTTPException(500, f"Cloudinary upload failed: {str(e)}")

    detected_type = "video" if file.content_type.startswith("video/") else "image"

    db_id = None
    try:
        db = get_db()
        db.execute(
            "INSERT INTO media (title, description, category, tags, media_type, country, source, resolution, capture_date, cloudinary_public_id, cloudinary_url, file_size, parent_id) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                title,
                description,
                category,
                tags,
                detected_type,
                country,
                source,
                resolution,
                capture_date,
                public_id,
                secure_url,
                len(contents),
                parent_id
            )
        )
        db_id = db.last_row_id
        print(f"Inserted media with id: {db_id}")
    except Exception as e:
        print("WARNING: Could not insert into D1 (writes disabled).")
        traceback.print_exc()

    return {
        "id": db_id,
        "url": secure_url,
        "public_id": public_id,
        "db_saved": db_id is not None
    }

@router.put("/media/{id}")
def update_media(id: int, update: MediaUpdate, admin = Depends(get_current_admin)):
    db = get_db()
    existing = db.execute("SELECT * FROM media WHERE id = ?", (id,)).fetchone()
    if not existing:
        raise HTTPException(404, "Media not found")
    update_data = update.dict(exclude_unset=True)
    set_clause = ", ".join(f"{k} = ?" for k in update_data.keys())
    values = list(update_data.values()) + [id]
    db.execute(f"UPDATE media SET {set_clause} WHERE id = ?", values)
    return {"message": "Updated", "id": id}

@router.delete("/media/{id}")
def delete_media_route(id: int, admin = Depends(get_current_admin)):
    db = get_db()
    media = db.execute("SELECT * FROM media WHERE id = ?", (id,)).fetchone()
    if not media:
        raise HTTPException(404, "Media not found")
    try:
        detected_type = media[5] if len(media) > 5 else "image"
        resource_type = "video" if detected_type == "video" else "image"
        delete_media(media[6], resource_type)
    except Exception:
        pass
    db.execute("DELETE FROM media WHERE id = ?", (id,))
    return {"message": "Deleted", "id": id}

@router.post("/download/{id}")
def increment_download(id: int):
    db = get_db()
    media = db.execute("SELECT * FROM media WHERE id = ?", (id,)).fetchone()
    if not media:
        raise HTTPException(404, "Media not found")
    db.execute("UPDATE media SET download_count = download_count + 1 WHERE id = ?", (id,))
    return {"url": media[7], "download_count": media[9] + 1}
