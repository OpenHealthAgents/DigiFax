"""
execute_ocr_extraction.py
Use Case managing tenant document OCR processing using resolved configurations.
"""

from typing import Any
from src.application.ports.itenant_ocr_repository import ITenantOCRRepository
from src.domain.ocr_provider.entities import TenantOCRConfiguration
from src.domain.ocr_provider.value_objects import (
    ImagePreprocessing,
    ExtractionFeatures,
    OCRThresholds,
    OCRProviderConfig
)
from src.domain.ocr_provider.domain_services import TenantOCRRoutingService
from src.domain.ocr_provider.iocr_provider import IOCRProvider


class ExecuteOCRExtractionUseCase:
    """
    Inbound Use Case executing OCR parsing. Resolves defaults if unconfigured.
    """

    def __init__(self, repo: ITenantOCRRepository):
        self.repo = repo

    def execute(
        self,
        tenant_id: str,
        document_bytes: bytes,
        provider_instances: dict[str, IOCRProvider]
    ) -> dict[str, Any]:
        """
        Loads tenant configuration settings, applying global defaults as fallback,
        then delegates OCR execution to the domain routing service.
        """
        config = self.repo.get_by_tenant_id(tenant_id)
        if not config:
            # Build Default Global OCR configurations
            default_preprocess = ImagePreprocessing(
                deskew=True,
                binarize=True,
                rotate=False,
                contrast_enhance=True
            )
            default_features = ExtractionFeatures(
                table_extraction=True,
                handwriting_support=False,
                barcode_support=True,
                qr_support=True
            )
            default_thresholds = OCRThresholds(
                confidence_threshold=0.75
            )
            default_providers = [
                OCRProviderConfig(provider_name="Tesseract", priority=1, language_packs=["en"]),
                OCRProviderConfig(provider_name="PaddleOCR", priority=2, language_packs=["en"]),
                OCRProviderConfig(provider_name="EasyOCR", priority=3, language_packs=["en"])
            ]
            config = TenantOCRConfiguration(
                tenant_id=tenant_id,
                preferred_provider="Tesseract",
                preprocessing=default_preprocess,
                features=default_features,
                thresholds=default_thresholds,
                providers=default_providers
            )

        # Delegate execution to domain routing service
        return TenantOCRRoutingService.execute_ocr(
            tenant_config=config,
            document_bytes=document_bytes,
            provider_instances=provider_instances
        )
