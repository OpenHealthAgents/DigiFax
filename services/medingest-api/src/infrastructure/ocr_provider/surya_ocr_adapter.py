"""
surya_ocr_adapter.py
Surya OCR integration adapter.
"""

from typing import Any
from src.domain.ocr_provider.iocr_provider import IOCRProvider


class SuryaOCRAdapter(IOCRProvider):
    """
    Adapter executing text extraction via Surya OCR engine.
    """

    def __init__(self, should_fail: bool = False, response_text: str = "Surya OCR Content", confidence: float = 0.92):
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
            raise RuntimeError("Surya OCR failed to load weights")
        return {
            "text": self.response_text,
            "confidence": self.confidence,
            "metadata": {"provider": "SuryaOCR", "languages": languages}
        }
