"""
iocr_provider.py
Domain interface (port) defining OCR provider abstraction.
"""

from abc import ABC, abstractmethod
from typing import Any


class IOCRProvider(ABC):
    """
    Abstractions for OCR engines (PaddleOCR, Surya, DocTR, OCRmyPDF, Tesseract, EasyOCR).
    
    Business Context:
        Decouples document classification and patient matching from concrete OCR implementations.
    """

    @abstractmethod
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
        """
        Executes text parsing and extraction over raw document file payloads.
        
        Returns:
            dict: Containing keys: "text" (str), "confidence" (float), "metadata" (dict)
        """
        pass
