
from src.application.ports.idocument_storage import IDocumentStorage
from src.domain.common.exceptions import DomainException


class InMemoryStorage(IDocumentStorage):
    """Simple in-memory storage adapter mimicking S3/local file writes."""

    def __init__(self) -> None:
        self._storage: dict[str, bytes] = {}

    def save(self, filepath: str, data: bytes) -> str:
        self._storage[filepath] = data
        return filepath

    def get(self, storage_path: str) -> bytes:
        if storage_path not in self._storage:
            raise DomainException(
                message=f"File not found in storage: {storage_path}",
                code="FILE_NOT_FOUND"
            )
        return self._storage[storage_path]
