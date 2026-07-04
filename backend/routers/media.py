from fastapi import APIRouter, HTTPException, Query
from database import SessionLocal
from models import Media
from schemas import MediaOut
from sqlalchemy.orm import joinedload
import typing

router = APIRouter()

@router.get("/media", response_model=typing.Dict[str, typing.Any])
def list_media(
    category: str = None,
    search: str = None,
    skip: int = 0,
    limit: int = 24
):
    db = SessionLocal()
    query = db.query(Media)
    if category:
        query = query.filter(Media.category == category)
    if search:
        like_pattern = f"%{search}%"
        query = query.filter(
            (Media.title.ilike(like_pattern)) |
            (Media.tags.ilike(like_pattern))
        )
    total = query.count()
    items = query.order_by(Media.uploaded_at.desc()).offset(skip).limit(limit).all()
    db.close()
    return {"total": total, "items": [MediaOut.from_orm(item).dict() for item in items]}

@router.get("/media/{id}", response_model=MediaOut)
def get_media(id: int):
    db = SessionLocal()
    media = db.query(Media).filter(Media.id == id).first()
    db.close()
    if not media:
        raise HTTPException(404, "Media not found")
    return MediaOut.from_orm(media)
