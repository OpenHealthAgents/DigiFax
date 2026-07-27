"""
test_subscriptions.py
Unit tests asserting BillingPlan quotas, SubscriptionUsage tracking, and limits checks.
"""

from datetime import datetime
import pytest

from src.domain.tenant_management.entities import Subscription
from src.domain.tenant_management.value_objects import (
    SubscriptionTier,
    SubscriptionQuotas,
    SubscriptionUsage,
    BillingPlan
)


def test_subscription_quota_boundaries() -> None:
    # Negative bounds checking
    with pytest.raises(ValueError):
        SubscriptionQuotas(-10, 100, 1000, 50)
    with pytest.raises(ValueError):
        SubscriptionUsage(100.0, -1, 100, 5)


def test_free_subscription_limits() -> None:
    # 500MB storage, 100 ocr pages, 1000 api calls, 50 documents limit
    free_quotas = SubscriptionQuotas(
        max_storage_mb=500,
        max_ocr_pages=100,
        max_api_calls_monthly=1000,
        max_documents_monthly=50
    )
    plan = BillingPlan(tier=SubscriptionTier.FREE, monthly_price_usd=0.0, quotas=free_quotas)

    # 1. Under limits usage
    under_usage = SubscriptionUsage(
        storage_used_mb=120.5,
        ocr_pages_used=45,
        api_calls_used=300,
        documents_used=12
    )
    sub = Subscription("sub-123", plan, datetime.now(), under_usage)
    exceeded = sub.has_exceeded_limits()
    assert not any(exceeded.values())

    # 2. Exceeded storage limit
    over_storage = SubscriptionUsage(
        storage_used_mb=550.0,
        ocr_pages_used=45,
        api_calls_used=300,
        documents_used=12
    )
    sub_storage = Subscription("sub-123", plan, datetime.now(), over_storage)
    assert sub_storage.has_exceeded_limits()["storage"] is True
    assert sub_storage.has_exceeded_limits()["ocr"] is False

    # 3. Exceeded OCR pages limit
    over_ocr = SubscriptionUsage(
        storage_used_mb=120.5,
        ocr_pages_used=105,
        api_calls_used=300,
        documents_used=12
    )
    sub_ocr = Subscription("sub-123", plan, datetime.now(), over_ocr)
    assert sub_ocr.has_exceeded_limits()["ocr"] is True

    # 4. Exceeded documents limit
    over_docs = SubscriptionUsage(
        storage_used_mb=120.5,
        ocr_pages_used=45,
        api_calls_used=300,
        documents_used=51
    )
    sub_docs = Subscription("sub-123", plan, datetime.now(), over_docs)
    assert sub_docs.has_exceeded_limits()["documents"] is True


def test_billing_plan_equality() -> None:
    quotas_1 = SubscriptionQuotas(500, 100, 1000, 50)
    quotas_2 = SubscriptionQuotas(500, 100, 1000, 50)
    
    plan_1 = BillingPlan(SubscriptionTier.FREE, 0.0, quotas_1)
    plan_2 = BillingPlan(SubscriptionTier.FREE, 0.0, quotas_2)

    assert plan_1 == plan_2
    assert quotas_1 == quotas_2
