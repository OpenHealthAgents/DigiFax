"""
test_ocr_provider.py
Unit tests verifying OCR Provider Management tactical objects, routing, and fallback behaviors.
"""

import pytest
from typing import Any

from src.domain.ocr_provider.entities import TenantOCRConfiguration
from src.domain.ocr_provider.value_objects import (
    ImagePreprocessing,
    ExtractionFeatures,
    OCRThresholds,
    OCRProviderConfig
)
from src.domain.ocr_provider.domain_services import TenantOCRRoutingService
from src.application.use_cases.ocr_provider.configure_ocr_settings import ConfigureOCRSettingsUseCase
from src.application.use_cases.ocr_provider.execute_ocr_extraction import ExecuteOCRExtractionUseCase
from src.infrastructure.persistence.in_memory_tenant_ocr_repository import InMemoryTenantOCRRepository
from src.infrastructure.persistence.base_repository import ConcurrencyException
from src.infrastructure.ocr_provider.tesseract_adapter import TesseractAdapter
from src.infrastructure.ocr_provider.paddle_ocr_adapter import PaddleOCRAdapter
from src.infrastructure.ocr_provider.easy_ocr_adapter import EasyOCRAdapter
from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus


def test_ocr_threshold_validations() -> None:
    # 1. Valid params
    thresh = OCRThresholds(0.85)
    assert thresh.confidence_threshold == 0.85

    # 2. Invalid threshold
    with pytest.raises(ValueError):
        OCRThresholds(-0.5)

    with pytest.raises(ValueError):
        OCRThresholds(1.2)


def test_ocr_provider_config_validations() -> None:
    # 1. Valid config
    config = OCRProviderConfig("Tesseract", priority=1, language_packs=["en", "es"])
    assert config.provider_name == "Tesseract"

    # 2. Invalid priority
    with pytest.raises(ValueError):
        OCRProviderConfig("Tesseract", priority=0)

    # 3. Empty languages
    with pytest.raises(ValueError):
        OCRProviderConfig("Tesseract", priority=1, language_packs=[])


def test_ocr_routing_fallback_loop() -> None:
    # Configure Tesseract (priority 1, fails) and PaddleOCR (priority 2, succeeds)
    preprocess = ImagePreprocessing(deskew=True)
    features = ExtractionFeatures()
    thresh = OCRThresholds(0.70)
    providers = [
        OCRProviderConfig("Tesseract", priority=1),
        OCRProviderConfig("PaddleOCR", priority=2)
    ]
    config = TenantOCRConfiguration(
        tenant_id="tenant-1",
        preferred_provider="Tesseract",
        preprocessing=preprocess,
        features=features,
        thresholds=thresh,
        providers=providers
    )

    instances = {
        "Tesseract": TesseractAdapter(should_fail=True),
        "PaddleOCR": PaddleOCRAdapter(response_text="Succeeded PaddleOCR")
    }

    res = TenantOCRRoutingService.execute_ocr(
        tenant_config=config,
        document_bytes=b"PDF PAYLOAD",
        provider_instances=instances
    )

    assert res["text"] == "Succeeded PaddleOCR"
    assert res["metadata"]["provider"] == "PaddleOCR"


def test_ocr_routing_confidence_failover() -> None:
    # Tesseract (priority 1, succeeds but returns 0.50 confidence < 0.80)
    # PaddleOCR (priority 2, succeeds and returns 0.90 confidence > 0.80)
    preprocess = ImagePreprocessing(deskew=True)
    features = ExtractionFeatures()
    thresh = OCRThresholds(0.80)
    providers = [
        OCRProviderConfig("Tesseract", priority=1),
        OCRProviderConfig("PaddleOCR", priority=2)
    ]
    config = TenantOCRConfiguration(
        tenant_id="tenant-2",
        preferred_provider="Tesseract",
        preprocessing=preprocess,
        features=features,
        thresholds=thresh,
        providers=providers
    )

    instances = {
        "Tesseract": TesseractAdapter(response_text="Low Conf Tesseract", confidence=0.50),
        "PaddleOCR": PaddleOCRAdapter(response_text="High Conf PaddleOCR", confidence=0.90)
    }

    res = TenantOCRRoutingService.execute_ocr(
        tenant_config=config,
        document_bytes=b"PDF PAYLOAD",
        provider_instances=instances
    )

    # Assert it falls back and selects PaddleOCR because Tesseract's confidence was too low
    assert res["text"] == "High Conf PaddleOCR"
    assert res["confidence"] == 0.90


def test_ocr_routing_confidence_returns_best_if_all_low() -> None:
    # Tesseract returns 0.50 confidence
    # EasyOCR returns 0.65 confidence
    # Both are less than threshold 0.80. Should return EasyOCR since it is the best.
    preprocess = ImagePreprocessing(deskew=True)
    features = ExtractionFeatures()
    thresh = OCRThresholds(0.80)
    providers = [
        OCRProviderConfig("Tesseract", priority=1),
        OCRProviderConfig("EasyOCR", priority=2)
    ]
    config = TenantOCRConfiguration(
        tenant_id="tenant-3",
        preferred_provider="Tesseract",
        preprocessing=preprocess,
        features=features,
        thresholds=thresh,
        providers=providers
    )

    instances = {
        "Tesseract": TesseractAdapter(response_text="Tesseract Text", confidence=0.50),
        "EasyOCR": EasyOCRAdapter(response_text="EasyOCR Text", confidence=0.65)
    }

    res = TenantOCRRoutingService.execute_ocr(
        tenant_config=config,
        document_bytes=b"PDF PAYLOAD",
        provider_instances=instances
    )

    assert res["text"] == "EasyOCR Text"
    assert res["confidence"] == 0.65


def test_ocr_repository_concurrency() -> None:
    repo = InMemoryTenantOCRRepository()
    preprocess = ImagePreprocessing()
    features = ExtractionFeatures()
    thresh = OCRThresholds(0.80)
    providers = [OCRProviderConfig("Tesseract", priority=1)]
    config = TenantOCRConfiguration(
        tenant_id="tenant-bob",
        preferred_provider="Tesseract",
        preprocessing=preprocess,
        features=features,
        thresholds=thresh,
        providers=providers
    )

    repo.save(config)
    assert config.version == 1

    stale = repo.get_by_tenant_id("tenant-bob")

    config.preferred_provider = "PaddleOCR"
    repo.save(config)
    assert config.version == 2

    with pytest.raises(ConcurrencyException):
        repo.save(stale)
