import abc


class IDocumentStorage(abc.ABC):
    """Outbound port interface for saving and retrieving raw document file bytes."""

    @abc.abstractmethod
    def save(self, filepath: str, data: bytes) -> str:
        """Saves the raw bytes to storage (e.g. S3 or local directory).

        Returns:
            The resolved unique storage path URI/key.
        """
        pass

    @abc.abstractmethod
    def get(self, storage_path: str) -> bytes:
        """Retrieves raw file bytes from storage by its key/URI."""
        pass
