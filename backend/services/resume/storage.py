"""
File storage abstraction.

Saves uploaded files to local disk today. Kept behind this thin
interface so it can be swapped for S3/GCS/etc. later without
touching the router or the rest of the resume service.
"""
import uuid
from pathlib import Path

from config import get_settings

settings = get_settings()


class UnsupportedFileTypeError(Exception):
    """Raised when an uploaded file's extension isn't supported."""


class FileTooLargeError(Exception):
    """Raised when an uploaded file exceeds the configured size limit."""


SUPPORTED_EXTENSIONS = {"pdf", "docx"}


def _get_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def validate_upload(filename: str, size_bytes: int) -> str:
    """Validate an upload's extension and size. Returns the normalized extension."""
    extension = _get_extension(filename)
    if extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{extension}'. Allowed types: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise FileTooLargeError(
            f"File exceeds the {settings.max_upload_size_mb}MB upload limit"
        )

    return extension


def save_file(content: bytes, extension: str, user_id: int) -> str:
    """Persist file content to disk and return its storage path."""
    upload_dir = Path(settings.upload_dir) / str(user_id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}.{extension}"
    file_path = upload_dir / unique_name
    file_path.write_bytes(content)

    return str(file_path)