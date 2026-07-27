"""
test_auth.py
Unit tests verifying Hexagonal authentication adapters, SSO providers, and SCIM provisioners.
"""

from datetime import datetime, timedelta
import pytest

from src.domain.auth.value_objects import AuthToken, SsoConfig, UserSession
from src.infrastructure.auth.better_auth_adapter import BetterAuthAdapter
from src.infrastructure.auth.sso_adapter import SsoAdapter
from src.infrastructure.auth.scim_adapter import ScimAdapter


def test_auth_token_value_object() -> None:
    expiry = datetime.now() + timedelta(hours=1)
    token = AuthToken("jwt-123", expiry)
    
    assert token.value == "jwt-123"
    assert token.expires_at == expiry
    assert token.is_expired(datetime.now()) is False
    assert token.is_expired(datetime.now() + timedelta(hours=2)) is True

    with pytest.raises(ValueError):
        AuthToken("  ", expiry)


def test_sso_config_value_object() -> None:
    config = SsoConfig("SAML", "https://okta.com/sso", "cert-bytes")
    assert config.provider_type == "SAML"
    assert config.entry_point == "https://okta.com/sso"
    assert config.certificate == "cert-bytes"

    with pytest.raises(ValueError):
        SsoConfig("INVALID", "https://okta.com/sso")
    with pytest.raises(ValueError):
        SsoConfig("SAML", "   ")


def test_better_auth_adapter_login_success() -> None:
    adapter = BetterAuthAdapter()
    session = adapter.login_tenant("practitioner@openhealth.org", "tenant-123")

    assert session.user_id == "usr-1"
    assert session.email == "practitioner@openhealth.org"
    assert session.tenant_id == "tenant-123"
    assert session.organization_id == "org-main"
    assert "CLINICAL_REVIEWER" in session.roles


def test_better_auth_adapter_login_fail() -> None:
    adapter = BetterAuthAdapter()
    with pytest.raises(ValueError):
        adapter.login_tenant("missing@openhealth.org", "tenant-123")


def test_better_auth_adapter_switch_org_success() -> None:
    adapter = BetterAuthAdapter()
    # Log in first to get mock token
    session = adapter.login_tenant("practitioner@openhealth.org", "tenant-123")
    
    # Switch organization context to org-stjude
    new_token = adapter.switch_organization(session.token.value, "org-stjude")
    assert new_token.value == f"jwt_token_for_usr-1_scoped_org-stjude"


def test_better_auth_adapter_switch_org_fail() -> None:
    adapter = BetterAuthAdapter()
    session = adapter.login_tenant("practitioner@openhealth.org", "tenant-123")
    
    # Switch to unauthorized org
    with pytest.raises(PermissionError):
        adapter.switch_organization(session.token.value, "org-unauthorized")

    # Switch with malformed token
    with pytest.raises(PermissionError):
        adapter.switch_organization("malformed-token", "org-stjude")


def test_better_auth_adapter_refresh() -> None:
    adapter = BetterAuthAdapter()
    session = adapter.refresh_session("refresh_token_for_usr-1")

    assert session.user_id == "usr-1"
    assert session.token.value == "jwt_token_for_usr-1"

    with pytest.raises(ValueError):
        adapter.refresh_session("invalid-refresh")


def test_better_auth_adapter_verify_invitation() -> None:
    adapter = BetterAuthAdapter()
    inv_data = adapter.verify_invitation_token("inv-token-valid")

    assert inv_data["email"] == "practitioner@stjude.org"
    assert inv_data["org_id"] == "org-stjude"
    assert inv_data["role"] == "CLINICAL_REVIEWER"

    with pytest.raises(ValueError):
        adapter.verify_invitation_token("inv-token-invalid")


def test_sso_adapter_flow() -> None:
    adapter = SsoAdapter()
    config = SsoConfig("OIDC", "https://auth.openhealth.org/authorize")
    
    # Configure and Redirect
    adapter.configure_sso("tenant-123", config)
    redirect_url = adapter.get_redirect_url("tenant-123")
    assert redirect_url.startswith("https://auth.openhealth.org/authorize")

    # Attempt redirect lookup for missing tenant
    with pytest.raises(ValueError):
        adapter.get_redirect_url("tenant-missing")

    # Callback parsing
    user_details = adapter.handle_callback_assertion({"code": "auth-code-valid"})
    assert user_details["email"] == "federated-practitioner@openhealth.org"

    # Callback with invalid code
    with pytest.raises(ValueError):
        adapter.handle_callback_assertion({"code": "invalid-code"})


def test_scim_adapter_flow() -> None:
    adapter = ScimAdapter()
    
    # Provision
    scim_payload = {"displayName": "Elizabeth Blackwell", "userName": "eblackwell"}
    user_id = adapter.provision_user("tenant-123", "eblackwell@openhealth.org", scim_payload)
    assert user_id.startswith("usr-scim-")

    with pytest.raises(ValueError):
        adapter.provision_user("tenant-123", "   ", scim_payload)

    # Deprovision
    adapter.deprovision_user("tenant-123", user_id)
    
    # Deprovision non-existent
    with pytest.raises(ValueError):
        adapter.deprovision_user("tenant-123", "usr-scim-missing")
