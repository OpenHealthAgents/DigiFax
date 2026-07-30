"""
value_objects.py
Domain Value Objects representing OCR configurations and pre-processing options.
"""

from dataclasses import dataclass, field
from typing import Any
from src.domain.common.value_object import ValueObject


@dataclass(frozen=True)
class ImagePreprocessing(ValueObject):
    """Immutable image pre-processing configurations prior to raw OCR runs."""
    deskew: bool = False
    binarize: bool = False
    rotate: bool = False
    contrast_enhance: bool = False


@dataclass(frozen=True)
class ExtractionFeatures(ValueObject):
    """Immutable functional features flags supported during OCR runs."""
    table_extraction: bool = False
    handwriting_support: bool = False
    barcode_support: bool = False
    qr_support: bool = False


@dataclass(frozen=True)
class OCRThresholds(ValueObject):
    """Immutable confidence gating limits."""
    confidence_threshold: float = 0.80

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("OCR Confidence threshold must be between 0.0 and 1.0")


@dataclass(frozen=True)
class OCRProviderConfig(ValueObject):
    """Immutable provider priority details."""
    provider_name: str  # PaddleOCR, Surya OCR, DocTR, OCRmyPDF, Tesseract, EasyOCR
    priority: int = 1
    language_packs: list[str] = field(default_factory=lambda: ["en"])

    def __post_init__(self) -> None:
        if not self.provider_name.strip():
            raise ValueError("Provider name cannot be empty")
        if self.priority < 1:
            raise ValueError("Priority index must be at least 1")
        if not self.language_packs:
            raise ValueError("Must specify at least 1 language pack code")
