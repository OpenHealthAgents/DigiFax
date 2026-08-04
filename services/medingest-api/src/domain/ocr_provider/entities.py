"""
entities.py
Domain Entities and Aggregate Root for OCR configurations.
"""

from src.domain.common.entity import Entity
from src.domain.ocr_provider.value_objects import (
    ImagePreprocessing,
    ExtractionFeatures,
    OCRThresholds,
    OCRProviderConfig
)


class TenantOCRConfiguration(Entity):
    """
    Aggregate Root managing a Tenant's OCR provider settings and processing options.
    """

    def __init__(
        self,
        tenant_id: str,
        preferred_provider: str,
        preprocessing: ImagePreprocessing,
        features: ExtractionFeatures,
        thresholds: OCRThresholds,
        providers: list[OCRProviderConfig],
        version: int = 1
    ):
        super().__init__(id=tenant_id)
        self.tenant_id = tenant_id
        self.preferred_provider = preferred_provider
        self.preprocessing = preprocessing
        self.features = features
        self.thresholds = thresholds
        self.providers = providers
        self.version = version
        self._domain_events = []

    def update_configuration(
        self,
        preferred_provider: str,
        preprocessing: ImagePreprocessing,
        features: ExtractionFeatures,
        thresholds: OCRThresholds,
        providers: list[OCRProviderConfig]
    ) -> None:
        """Updates formatting details and provider settings configurations."""
        self.preferred_provider = preferred_provider
        self.preprocessing = preprocessing
        self.features = features
        self.thresholds = thresholds
        self.providers = providers

        from src.domain.common.domain_event import DomainEvent
        from dataclasses import dataclass, field
        from datetime import datetime

        @dataclass(frozen=True)
        class OCRConfigUpdatedEvent(DomainEvent):
            tenant_id: str
            preferred_provider: str
            occurred_at: datetime = field(default_factory=datetime.utcnow)

        self._domain_events.append(
            OCRConfigUpdatedEvent(
                tenant_id=self.tenant_id,
                preferred_provider=preferred_provider
            )
        )
