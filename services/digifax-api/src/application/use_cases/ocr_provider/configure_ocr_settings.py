"""
configure_ocr_settings.py
Use Case configuring and saving TenantOCRConfiguration parameters.
"""

from src.application.ports.itenant_ocr_repository import ITenantOCRRepository
from src.domain.common.event_bus import IEventBus
from src.domain.ocr_provider.entities import TenantOCRConfiguration
from src.domain.ocr_provider.value_objects import (
    ImagePreprocessing,
    ExtractionFeatures,
    OCRThresholds,
    OCRProviderConfig
)


class ConfigureOCRSettingsUseCase:
    """
    Inbound Use Case configuring OCR processing settings for a Tenant.
    """

    def __init__(self, repo: ITenantOCRRepository, event_bus: IEventBus):
        self.repo = repo
        self.event_bus = event_bus

    def execute(
        self,
        tenant_id: str,
        preferred_provider: str,
        deskew: bool,
        binarize: bool,
        rotate: bool,
        contrast_enhance: bool,
        table_extraction: bool,
        handwriting_support: bool,
        barcode_support: bool,
        qr_support: bool,
        confidence_threshold: float,
        providers: list[dict]
    ) -> TenantOCRConfiguration:
        """
        Validates, modifies, and saves target OCR configurations.
        """
        preprocess = ImagePreprocessing(
            deskew=deskew,
            binarize=binarize,
            rotate=rotate,
            contrast_enhance=contrast_enhance
        )
        features = ExtractionFeatures(
            table_extraction=table_extraction,
            handwriting_support=handwriting_support,
            barcode_support=barcode_support,
            qr_support=qr_support
        )
        thresholds = OCRThresholds(
            confidence_threshold=confidence_threshold
        )
        
        provider_configs = [
            OCRProviderConfig(
                provider_name=p["provider_name"],
                priority=p.get("priority", 1),
                language_packs=p.get("language_packs", ["en"])
            ) for p in providers
        ]

        config = self.repo.get_by_tenant_id(tenant_id)
        if not config:
            config = TenantOCRConfiguration(
                tenant_id=tenant_id,
                preferred_provider=preferred_provider,
                preprocessing=preprocess,
                features=features,
                thresholds=thresholds,
                providers=provider_configs
            )
        else:
            config.update_configuration(
                preferred_provider=preferred_provider,
                preprocessing=preprocess,
                features=features,
                thresholds=thresholds,
                providers=provider_configs
            )

        self.repo.save(config)

        # Dispatch events
        for event in config._domain_events:
            self.event_bus.publish(event)
        config._domain_events.clear()

        return config
