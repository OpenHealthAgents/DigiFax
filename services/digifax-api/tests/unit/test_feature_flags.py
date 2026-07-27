"""
test_feature_flags.py
Unit tests asserting FeatureFlagEngine evaluations under beta gates, licenses, and limits.
"""

from src.domain.organizations.value_objects import TenantConfiguration
from src.domain.tenant_management.feature_flag_engine import FeatureFlagEngine


def test_standard_feature_flags() -> None:
    engine = FeatureFlagEngine()
    
    # Configure tenant with explicitly enabled/disabled features
    config = TenantConfiguration(
        max_daily_uploads=5,
        allowed_mime_types=["application/pdf"],
        feature_flags={
            "auto_ocr": True,
            "loinc_mapping": False
        }
    )

    assert engine.evaluate_feature("auto_ocr", config) is True
    assert engine.evaluate_feature("loinc_mapping", config) is False
    # Defaults to True if not present and not beta/restricted
    assert engine.evaluate_feature("some_random_feature", config) is True


def test_beta_features_gate() -> None:
    engine = FeatureFlagEngine()
    
    # Opted-in beta feature
    config_opted_in = TenantConfiguration(
        max_daily_uploads=5,
        allowed_mime_types=["application/pdf"],
        feature_flags={"beta_opt_in": ["ai_summarization"]}
    )
    # Not opted-in beta feature
    config_opted_out = TenantConfiguration(
        max_daily_uploads=5,
        allowed_mime_types=["application/pdf"],
        feature_flags={}
    )

    assert engine.evaluate_feature("ai_summarization", config_opted_in) is True
    assert engine.evaluate_feature("ai_summarization", config_opted_out) is False


def test_license_restrictions_gate() -> None:
    engine = FeatureFlagEngine()
    
    config = TenantConfiguration(max_daily_uploads=5, allowed_mime_types=[])

    # billing_write requires Enterprise license
    assert engine.evaluate_feature("billing_write", config, license_tier="Enterprise") is True
    assert engine.evaluate_feature("billing_write", config, license_tier="Standard") is False


def test_usage_limits_gate() -> None:
    engine = FeatureFlagEngine()
    
    config = TenantConfiguration(max_daily_uploads=3, allowed_mime_types=[])

    # Uploads usage check: max is 3
    assert engine.evaluate_feature("document_upload", config, usage_count=1) is True
    assert engine.evaluate_feature("document_upload", config, usage_count=2) is True
    assert engine.evaluate_feature("document_upload", config, usage_count=3) is False
    assert engine.evaluate_feature("document_upload", config, usage_count=4) is False
