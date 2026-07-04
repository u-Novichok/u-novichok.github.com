from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from database import Base

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    category = Column(String, default="")
    tags = Column(String, default="")         # comma-separated
    media_type = Column(String, default="image")
    cloudinary_public_id = Column(String)
    cloudinary_url = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    download_count = Column(Integer, default=0)

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="admin")
    created_at = Column(DateTime, default=datetime.utcnow)
