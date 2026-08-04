"""
ocrmypdf_adapter.py
OCRmyPDF integration adapter.
"""

from typing import Any
from src.domain.ocr_provider.iocr_provider import IOCRProvider


class OCRmyPDFAdapter(IOCRProvider):
    """
    Adapter executing text completions via OCRmyPDF processing backend.
    """

    def __init__(self, should_fail: bool = False, response_text: str = "OCRmyPDF Content", confidence: float = 0.85):
        self.should_fail = should_fail
        self.response_text = response_text
        self.confidence = confidence

    def extract_text(
        self,
        document_bytes: bytes,
        languages: list[str],
        deskew: bool = False,
        binarize: bool = False,
        rotate: bool = False,
        contrast_enhance: bool = False,
        table_extraction: bool = False,
        handwriting_support: bool = False,
        barcode_support: bool = False,
        qr_support: bool = False
    ) -> dict[str, Any]:
        if self.should_fail:
            raise RuntimeError("OCRmyPDF subprocess exit status 1")
        return {
            "text": self.response_text,
            "confidence": self.confidence,
            "metadata": {"provider": "OCRmyPDF", "languages": languages}
        }
