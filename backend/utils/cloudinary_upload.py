import cloudinary
import cloudinary.uploader
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

def upload_image(file_bytes, folder="novichok"):
    result = cloudinary.uploader.upload(file_bytes, folder=folder)
    return result["public_id"], result["secure_url"]

def delete_image(public_id):
    cloudinary.uploader.destroy(public_id)
