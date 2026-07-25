from src.application.ports.iocr_engine import IOcrEngine
from src.domain.common.exceptions import DomainException
from src.infrastructure.ocr.doctr_adapter import DocTrAdapter
from src.infrastructure.ocr.ocrmypdf_adapter import OcrMyPdfAdapter
from src.infrastructure.ocr.paddleocr_adapter import PaddleOcrAdapter
from src.infrastructure.ocr.surya_adapter import SuryaOcrAdapter
from src.infrastructure.ocr.tesseract_adapter import TesseractAdapter


class OcrEngineFactory:
    """Factory creating IOcrEngine adapters based on configuration strings."""

    _PROVIDERS = {
        "tesseract": TesseractAdapter,
        "paddleocr": PaddleOcrAdapter,
        "ocrmypdf": OcrMyPdfAdapter,
        "surya": SuryaOcrAdapter,
        "doctr": DocTrAdapter
    }

    @classmethod
    def create(cls, provider_name: str) -> IOcrEngine:
        """Instantiates the requested OCR engine adapter.

        Args:
            provider_name: The case-insensitive name of the engine (e.g., 'tesseract').

        Returns:
            The resolved IOcrEngine adapter instance.

        Raises:
            DomainException if the provider name is unknown.
        """
        name = provider_name.strip().lower()
        adapter_cls = cls._PROVIDERS.get(name)
        if not adapter_cls:
            allowed = ", ".join(cls._PROVIDERS.keys())
            raise DomainException(
                message=f"Unsupported OCR provider: {provider_name}. Supported providers are: {allowed}.",
                code="UNSUPPORTED_OCR_PROVIDER"
            )
        return adapter_cls()  # type: ignore[abstract]
