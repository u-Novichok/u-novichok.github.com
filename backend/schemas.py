
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MediaOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = ""
    category: Optional[str] = ""
    tags: Optional[str] = ""
    media_type: Optional[str] = "image"
    cloudinary_public_id: str
    cloudinary_url: str
    uploaded_at: Optional[datetime]
    download_count: Optional[int] = 0

    class Config:
        from_attributes = True

class MediaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
