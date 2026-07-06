from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from database import get_db
from utils.cloudinary_upload import upload_image, delete_image
from utils.security import get_current_admin
from schemas import MediaUpdate
import traceback

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/upload")
async def upload_media(
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form(""),
    tags: str = Form(""),
    file: UploadFile = File(...),
    admin = Depends(get_current_admin)
):
    contents = await file.read()
    if not (file.content_type.startswith("image/") or file.content_type.startswith("video/")):
        raise HTTPException(400, "Only image and video files are allowed")
    try:
        public_id, secure_url = upload_image(contents, folder="novichok")
    except Exception as e:
        raise HTTPException(500, f"Cloudinary upload failed: {str(e)}")

    # Try to insert into Turso; if it fails, still return success
    db_id = None
    try:
        db = get_db()
        detected_type = "video" if file.content_type.startswith("video/") else "image"

        db.execute(
             "INSERT INTO media (title, description, category, tags, media_type, cloudinary_public_id, cloudinary_url) VALUES (?,?,?,?,?,?,?)",
              (title, description, category, tags, detected_type, public_id, secure_url)
        )
        db_id = db.last_row_id
        print(f"Inserted media with id: {db_id}")
    except Exception as e:
        print("WARNING: Could not insert into Turso (writes disabled).")
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
def delete_media(id: int, admin = Depends(get_current_admin)):
    db = get_db()
    media = db.execute("SELECT * FROM media WHERE id = ?", (id,)).fetchone()
    if not media:
        raise HTTPException(404, "Media not found")
    try:
        delete_image(media[6])  # cloudinary_public_id
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
