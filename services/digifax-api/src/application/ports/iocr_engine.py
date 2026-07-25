import abc

from src.domain.ocr.value_objects import OcrResult


class IOcrEngine(abc.ABC):
    """Outbound port interface defining standard OCR document processing services."""

    @abc.abstractmethod
    def perform_ocr(
        self,
        document_id: str,
        document_bytes: bytes,
        file_extension: str
    ) -> OcrResult:
        """Executes layout extraction and character recognition on file payload.

        Args:
            document_id: Unique string identifying the ingestion session.
            document_bytes: Raw binary file payload to process.
            file_extension: Extension format (e.g. "pdf", "tiff").

        Returns:
            The normalized OcrResult model mapping text layouts and grids.
        """
        pass
