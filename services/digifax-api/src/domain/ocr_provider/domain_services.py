"""
domain_services.py
Domain Routing Service orchestrating OCR fallbacks based on priorities and confidence thresholds.
"""

import logging
from typing import Any
from src.domain.ocr_provider.entities import TenantOCRConfiguration
from src.domain.ocr_provider.iocr_provider import IOCRProvider

logger = logging.getLogger(__name__)


class TenantOCRRoutingService:
    """
    Domain Service routing OCR calls over fallback priorities, gating confidence thresholds.
    """

    @staticmethod
    def execute_ocr(
        tenant_config: TenantOCRConfiguration,
        document_bytes: bytes,
        provider_instances: dict[str, IOCRProvider]
    ) -> dict[str, Any]:
        """
        Runs OCR extraction by checking prioritized engines.
        
        Applies:
            - Priority order failovers on endpoint failures.
            - Low-confidence loops: if extracted confidence is below confidence_threshold,
              failover to next priority provider to find a cleaner scan output.
        """
        if not provider_instances:
            raise ValueError("Provider instances mapping is required")

        # 1. Sort configured providers by priority index ascending
        sorted_providers = sorted(tenant_config.providers, key=lambda p: p.priority)

        last_error = None
        best_result = None

        # 2. Iterate through fallback list
        for config in sorted_providers:
            provider_name = config.provider_name
            if provider_name not in provider_instances:
                logger.warning(f"OCR provider {provider_name} has no registered instance. Skipping.")
                continue

            instance = provider_instances[provider_name]
            
            try:
                # 3. Execute extraction with preprocessing options
                res = instance.extract_text(
                    document_bytes=document_bytes,
                    languages=config.language_packs,
                    deskew=tenant_config.preprocessing.deskew,
                    binarize=tenant_config.preprocessing.binarize,
                    rotate=tenant_config.preprocessing.rotate,
                    contrast_enhance=tenant_config.preprocessing.contrast_enhance,
                    table_extraction=tenant_config.features.table_extraction,
                    handwriting_support=tenant_config.features.handwriting_support,
                    barcode_support=tenant_config.features.barcode_support,
                    qr_support=tenant_config.features.qr_support
                )
                
                # Check confidence threshold gate
                conf = res.get("confidence", 0.0)
                if conf >= tenant_config.thresholds.confidence_threshold:
                    # Clear success, return immediately
                    return res
                else:
                    logger.warning(
                        f"Provider {provider_name} returned low confidence ({conf:.2f} < "
                        f"{tenant_config.thresholds.confidence_threshold:.2f}). Trying failover."
                    )
                    # Cache the best low-confidence result in case all fail
                    if not best_result or conf > best_result.get("confidence", 0.0):
                        best_result = res
                        
            except Exception as e:
                last_error = e
                logger.error(f"OCR execution failed on provider {provider_name}: {str(e)}")

        # 4. If all configurations failed or yielded low confidence, return best low-confidence result
        if best_result:
            logger.warning("Returning best available low-confidence result from failover loop.")
            return best_result

        raise RuntimeError(f"OCR Extraction failed across all fallback engines. Last Error: {str(last_error)}")
