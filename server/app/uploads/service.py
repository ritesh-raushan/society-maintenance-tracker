import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from app.core.config import settings
from app.core.errors import AppError

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_PHOTO_SIZE_BYTES = 5 * 1024 * 1024
PHOTO_FOLDER = "society-maintenance-tracker/complaints"


def ensure_storage_configured() -> None:
    if not (
        settings.cloudinary_cloud_name
        and settings.cloudinary_api_key
        and settings.cloudinary_api_secret
    ):
        raise AppError(
            code="STORAGE_NOT_CONFIGURED",
            message="Image storage is not configured on the server.",
            status_code=503,
        )


def _configure_cloudinary() -> None:
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
    )


def validate_photo(photo: UploadFile) -> None:
    if photo.content_type not in ALLOWED_IMAGE_TYPES:
        raise AppError(
            code="INVALID_FILE_TYPE",
            message="Only JPEG, PNG and WebP images are allowed.",
            status_code=400,
        )

    size = 0

    while chunk := photo.file.read(1024 * 1024):
        size += len(chunk)

        if size > MAX_PHOTO_SIZE_BYTES:
            raise AppError(
                code="FILE_TOO_LARGE",
                message="Photo must not exceed 5 MB.",
                status_code=400,
            )

    photo.file.seek(0)


def upload_photo(photo: UploadFile) -> str:
    ensure_storage_configured()
    _configure_cloudinary()

    result = cloudinary.uploader.upload(
        photo.file,
        folder=PHOTO_FOLDER,
        resource_type="image",
    )

    return result["secure_url"]
