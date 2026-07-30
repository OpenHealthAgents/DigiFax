"""
doctr_adapter.py
DocTR integration adapter.
"""

from typing import Any
from src.domain.ocr_provider.iocr_provider import IOCRProvider


class DocTRAdapter(IOCRProvider):
    """
    Adapter executing text completions via DocTR (Document Text Recognition) model.
    """

    def __init__(self, should_fail: bool = False, response_text: str = "DocTR Content", confidence: float = 0.89):
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
            raise RuntimeError("DocTR failed decoding layout elements")
        return {
            "text": self.response_text,
            "confidence": self.confidence,
            "metadata": {"provider": "DocTR"}
        }
