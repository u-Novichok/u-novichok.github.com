from pydantic import BaseModel
from typing import Optional

class MediaOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = ""
    category: Optional[str] = ""
    tags: Optional[str] = ""
    media_type: Optional[str] = "image"
    cloudinary_public_id: Optional[str] = ""
    cloudinary_url: Optional[str] = ""
    uploaded_at: Optional[str] = None
    download_count: Optional[int] = 0
    country: Optional[str] = ""
    source: Optional[str] = ""
    resolution: Optional[str] = ""
    capture_date: Optional[str] = ""
    file_size: Optional[int] = 0
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True

class MediaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    country: Optional[str] = None
    source: Optional[str] = None
    resolution: Optional[str] = None
    capture_date: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
