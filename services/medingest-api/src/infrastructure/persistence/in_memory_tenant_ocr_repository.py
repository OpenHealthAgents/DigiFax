"""
in_memory_tenant_ocr_repository.py
In-memory persistence adapter for TenantOCRConfiguration aggregate.
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
from src.infrastructure.persistence.base_repository import BaseInMemoryRepository


class InMemoryTenantOCRRepository(BaseInMemoryRepository, ITenantOCRRepository):
    """
    Thread-safe in-memory adapter storing TenantOCRConfiguration records.
    """

    def __init__(self) -> None:
        super().__init__()

    def save(self, config: TenantOCRConfiguration) -> None:
        """Saves configuration with version validation (OCC)."""
        record_data = {
            "id": config.tenant_id,
            "tenant_id": config.tenant_id,
            "preferred_provider": config.preferred_provider,
            "preprocessing": {
                "deskew": config.preprocessing.deskew,
                "binarize": config.preprocessing.binarize,
                "rotate": config.preprocessing.rotate,
                "contrast_enhance": config.preprocessing.contrast_enhance
            },
            "features": {
                "table_extraction": config.features.table_extraction,
                "handwriting_support": config.features.handwriting_support,
                "barcode_support": config.features.barcode_support,
                "qr_support": config.features.qr_support
            },
            "thresholds": {
                "confidence_threshold": config.thresholds.confidence_threshold
            },
            "providers": [
                {
                    "provider_name": p.provider_name,
                    "priority": p.priority,
                    "language_packs": p.language_packs
                } for p in config.providers
            ],
            "version": getattr(config, "version", 1)
        }

        self._save_record(config.tenant_id, record_data)
        saved = self._records[config.tenant_id]
        config.version = saved["version"]

    def get_by_tenant_id(self, tenant_id: str) -> TenantOCRConfiguration | None:
        """Retrieves and reconstitutes TenantOCRConfiguration aggregate."""
        record = self._get_record_by_id(tenant_id, tenant_id)
        if not record:
            return None

        preprocessing = ImagePreprocessing(
            deskew=record["preprocessing"]["deskew"],
            binarize=record["preprocessing"]["binarize"],
            rotate=record["preprocessing"]["rotate"],
            contrast_enhance=record["preprocessing"]["contrast_enhance"]
        )
        features = ExtractionFeatures(
            table_extraction=record["features"]["table_extraction"],
            handwriting_support=record["features"]["handwriting_support"],
            barcode_support=record["features"]["barcode_support"],
            qr_support=record["features"]["qr_support"]
        )
        thresholds = OCRThresholds(
            confidence_threshold=record["thresholds"]["confidence_threshold"]
        )
        providers = [
            OCRProviderConfig(
                provider_name=p["provider_name"],
                priority=p["priority"],
                language_packs=p["language_packs"]
            ) for p in record["providers"]
        ]

        return TenantOCRConfiguration(
            tenant_id=record["tenant_id"],
            preferred_provider=record["preferred_provider"],
            preprocessing=preprocessing,
            features=features,
            thresholds=thresholds,
            providers=providers,
            version=record["version"]
        )
