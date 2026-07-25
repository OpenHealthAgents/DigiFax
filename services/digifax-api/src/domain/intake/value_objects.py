import enum

from src.domain.common.exceptions import DomainException
from src.domain.common.value_object import ValueObject


class IntakeSource(enum.StrEnum):
    FAX_UPLOAD = "FAX_UPLOAD"
    EMAIL_ATTACHMENT = "EMAIL_ATTACHMENT"
    API_UPLOAD = "API_UPLOAD"


class FileMetadata(ValueObject):
    """Encapsulates validated details of the uploaded file payload."""

    ALLOWED_EXTENSIONS: set[str] = {
        "pdf", "tiff", "tif", "png", "jpeg", "jpg"
    }

    ALLOWED_MIME_TYPES: set[str] = {
        "application/pdf", "image/tiff", "image/png", "image/jpeg"
    }

    def __init__(
        self,
        filename: str,
        content_type: str,
        size_bytes: int,
        hash_sha256: str
    ):
        ext = self._extract_extension(filename)
        if ext not in self.ALLOWED_EXTENSIONS:
            raise DomainException(
                message=f"Unsupported file extension: .{ext}. Supported formats are PDF, TIFF, PNG, JPEG.",
                code="UNSUPPORTED_FILE_TYPE"
            )

        # Normalize mime type for variations (e.g. image/jpg -> image/jpeg)
        normalized_mime = content_type.lower().strip()
        if normalized_mime == "image/jpg":
            normalized_mime = "image/jpeg"

        if normalized_mime not in self.ALLOWED_MIME_TYPES:
            raise DomainException(
                message=f"Unsupported mime type: {content_type}. Supported types are PDF, TIFF, PNG, JPEG.",
                code="UNSUPPORTED_MIME_TYPE"
            )

        if size_bytes <= 0:
            raise DomainException(
                message="File size must be positive and greater than zero.",
                code="INVALID_FILE_SIZE"
            )

        if not hash_sha256:
            raise DomainException(
                message="SHA-256 hash value must be provided.",
                code="INVALID_HASH"
            )

        self.filename = filename
        self.content_type = normalized_mime
        self.size_bytes = size_bytes
        self.hash_sha256 = hash_sha256
        self.extension = ext

    def _extract_extension(self, filename: str) -> str:
        parts = filename.split(".")
        if len(parts) < 2 or not parts[-1]:
            raise DomainException(
                message="Filename must contain a valid extension.",
                code="MISSING_FILE_EXTENSION"
            )
        return parts[-1].lower().strip()
