from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from database import SessionLocal
from models import Media
from schemas import MediaUpdate
from utils.cloudinary_upload import upload_image, delete_image
from utils.security import get_current_admin
from sqlalchemy.orm import Session

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
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Only image files are allowed")
    try:
        public_id, secure_url = upload_image(contents, folder="novichok")
    except Exception as e:
        raise HTTPException(500, f"Cloudinary upload failed: {str(e)}")

    db = SessionLocal()
    media = Media(
        title=title,
        description=description,
        category=category,
        tags=tags,
        media_type="image",
        cloudinary_public_id=public_id,
        cloudinary_url=secure_url,
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    db.close()
    return {"id": media.id, "url": secure_url}

@router.put("/media/{id}")
def update_media(id: int, update: MediaUpdate, admin = Depends(get_current_admin)):
    db = SessionLocal()
    media = db.query(Media).filter(Media.id == id).first()
    if not media:
        db.close()
        raise HTTPException(404, "Media not found")
    update_data = update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(media, key, value)
    db.commit()
    db.refresh(media)
    db.close()
    return {"message": "Updated", "id": id}

@router.delete("/media/{id}")
def delete_media(id: int, admin = Depends(get_current_admin)):
    db = SessionLocal()
    media = db.query(Media).filter(Media.id == id).first()
    if not media:
        db.close()
        raise HTTPException(404, "Media not found")
    # Delete from Cloudinary
    try:
        delete_image(media.cloudinary_public_id)
    except Exception:
        # Log this, but continue to delete DB record
        pass
    db.delete(media)
    db.commit()
    db.close()
    return {"message": "Deleted", "id": id}

@router.post("/download/{id}")
def increment_download(id: int):
    db = SessionLocal()
    media = db.query(Media).filter(Media.id == id).first()
    if not media:
        db.close()
        raise HTTPException(404, "Media not found")
    media.download_count = (media.download_count or 0) + 1
    db.commit()
    db.close()
    return {"url": media.cloudinary_url, "download_count": media.download_count}
