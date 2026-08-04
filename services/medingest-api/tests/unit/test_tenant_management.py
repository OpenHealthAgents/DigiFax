"""
test_tenant_management.py
Unit tests verifying all 12 domain objects inside the Tenant Management bounded context.
"""

from datetime import datetime, timedelta
import pytest

from src.domain.tenant_management.value_objects import (
    Permission, Role, BillingPlan, AuditPolicy, RetentionPolicy,
    SubscriptionTier, SubscriptionQuotas
)
from src.domain.tenant_management.entities import (
    Tenant, TenantStatus, Organization, Workspace, Membership,
    Invitation, InvitationStatus, Subscription, ApiKey
)


def test_permission_value_object() -> None:
    p1 = Permission("document:read")
    p2 = Permission("document:read")
    p3 = Permission("document:write")

    assert p1 == p2
    assert p1 != p3
    assert p1.name == "document:read"

    with pytest.raises(ValueError):
        Permission("  ")


def test_role_value_object() -> None:
    p = Permission("document:read")
    role1 = Role("REVIEWER", [p])
    role2 = Role("REVIEWER", [p])
    role3 = Role("ADMIN", [p])

    assert role1 == role2
    assert role1 != role3
    assert role1.name == "REVIEWER"

    with pytest.raises(ValueError):
        Role(" ", [])


def test_billing_plan_value_object() -> None:
    quotas1 = SubscriptionQuotas(500, 100, 1000, 50)
    quotas2 = SubscriptionQuotas(500, 100, 1000, 50)
    quotas3 = SubscriptionQuotas(10000, 2000, 50000, 1000)

    plan1 = BillingPlan(SubscriptionTier.FREE, 0.0, quotas1)
    plan2 = BillingPlan(SubscriptionTier.FREE, 0.0, quotas2)
    plan3 = BillingPlan(SubscriptionTier.PROFESSIONAL, 149.0, quotas3)

    assert plan1 == plan2
    assert plan1 != plan3

    with pytest.raises(ValueError):
        BillingPlan(SubscriptionTier.FREE, -10.0, quotas1)


def test_audit_policy_value_object() -> None:
    policy1 = AuditPolicy(30, ["upload"])
    policy2 = AuditPolicy(30, ["upload"])
    policy3 = AuditPolicy(90, ["upload"])

    assert policy1 == policy2
    assert policy1 != policy3

    with pytest.raises(ValueError):
        AuditPolicy(-5, [])


def test_retention_policy_value_object() -> None:
    policy1 = RetentionPolicy(90, 365)
    policy2 = RetentionPolicy(90, 365)
    policy3 = RetentionPolicy(30, 30)

    assert policy1 == policy2
    assert policy1 != policy3

    with pytest.raises(ValueError):
        RetentionPolicy(-5, 100)
    with pytest.raises(ValueError):
        RetentionPolicy(100, -10)


def test_subscription_entity() -> None:
    plan = BillingPlan(SubscriptionTier.FREE, 0.0, SubscriptionQuotas(500, 100, 1000, 50))
    start = datetime.now()
    sub = Subscription("sub-1", plan, start)

    assert sub.id == "sub-1"
    assert sub.plan == plan
    assert sub.start_date == start


def test_api_key_entity() -> None:
    expires = datetime.now() + timedelta(days=30)
    key = ApiKey("key-1", "hash-abc", "Production Gateway", expires)

    assert key.id == "key-1"
    assert key.hashed_key == "hash-abc"
    assert key.label == "Production Gateway"
    assert key.is_expired(datetime.now()) is False
    assert key.is_expired(datetime.now() + timedelta(days=40)) is True

    with pytest.raises(ValueError):
        ApiKey("key-1", "hash", "  ")


def test_tenant_aggregate() -> None:
    plan = BillingPlan(SubscriptionTier.FREE, 0.0, SubscriptionQuotas(500, 100, 1000, 50))
    sub = Subscription("sub-1", plan, datetime.now())
    audit = AuditPolicy(30, [])
    retention = RetentionPolicy(90, 365)

    tenant = Tenant("tenant-abc", "OpenHealth Group", TenantStatus.ACTIVE, sub, audit, retention)

    assert tenant.id == "tenant-abc"
    assert tenant.name == "OpenHealth Group"
    assert tenant.status == TenantStatus.ACTIVE

    tenant.suspend()
    assert tenant.status == TenantStatus.SUSPENDED

    tenant.activate()
    assert tenant.status == TenantStatus.ACTIVE

    tenant.archive()
    assert tenant.status == TenantStatus.ARCHIVED

    key = ApiKey("key-1", "hash", "Dev")
    tenant.add_api_key(key)
    assert len(tenant.api_keys) == 1

    with pytest.raises(ValueError):
        Tenant("tenant-abc", "  ", TenantStatus.ACTIVE, sub, audit, retention)


def test_organization_aggregate() -> None:
    org = Organization("org-1", "tenant-123", "Main Campus", "1234567890")
    assert org.id == "org-1"
    assert org.tenant_id == "tenant-123"
    assert org.name == "Main Campus"
    assert org.npi == "1234567890"

    with pytest.raises(ValueError):
        Organization("org-1", "tenant-123", " ", "12345")
    with pytest.raises(ValueError):
        Organization("org-1", "tenant-123", "Name", " ")


def test_workspace_entity() -> None:
    ws = Workspace("ws-1", "org-1", "Pediatrics")
    assert ws.id == "ws-1"
    assert ws.organization_id == "org-1"
    assert ws.name == "Pediatrics"

    with pytest.raises(ValueError):
        Workspace("ws-1", "org-1", " ")


def test_membership_entity() -> None:
    role = Role("REVIEWER", [])
    member = Membership("m-1", "user-abc", "org-1", role)

    assert member.id == "m-1"
    assert member.user_id == "user-abc"
    assert member.organization_id == "org-1"
    assert member.role == role


def test_invitation_lifecycle() -> None:
    role = Role("REVIEWER", [])
    expiry = datetime.now() + timedelta(hours=2)
    inv = Invitation("inv-1", "org-1", "doctor@hospital.org", role, "token-123", expiry)

    assert inv.id == "inv-1"
    assert inv.status == InvitationStatus.PENDING

    # Acceptance
    inv.accept(datetime.now())
    assert inv.status == InvitationStatus.ACCEPTED

    with pytest.raises(ValueError):
        # Accepting already accepted invitation
        inv.accept(datetime.now())

    with pytest.raises(ValueError):
        # Empty email throws ValueError
        Invitation("inv-2", "org-1", "  ", role, "token", expiry)

    # Test expiration acceptance
    inv_expired = Invitation("inv-expired", "org-1", "doctor@hospital.org", role, "token-expired", datetime.now() - timedelta(hours=1))
    with pytest.raises(ValueError):
        inv_expired.accept(datetime.now())
    assert inv_expired.status == InvitationStatus.EXPIRED


def test_domain_events() -> None:
    from src.domain.tenant_management.events import (
        TenantCreatedEvent,
        MembershipAssignedEvent,
        InvitationSentEvent,
        WorkspaceCreatedEvent,
    )

    t_event = TenantCreatedEvent("tenant-abc", "OpenHealth")
    assert t_event.aggregate_id == "tenant-abc"
    assert t_event.tenant_id == "tenant-abc"
    assert t_event.name == "OpenHealth"

    m_event = MembershipAssignedEvent("m-1", "tenant-123", "user-abc", "org-1", "REVIEWER")
    assert m_event.aggregate_id == "m-1"
    assert m_event.tenant_id == "tenant-123"
    assert m_event.user_id == "user-abc"
    assert m_event.organization_id == "org-1"
    assert m_event.role_name == "REVIEWER"

    i_event = InvitationSentEvent("inv-1", "tenant-123", "test@test.org", "tok-123")
    assert i_event.aggregate_id == "inv-1"
    assert i_event.tenant_id == "tenant-123"
    assert i_event.recipient_email == "test@test.org"
    assert i_event.token == "tok-123"

    w_event = WorkspaceCreatedEvent("ws-1", "tenant-123", "org-1", "Pediatrics")
    assert w_event.aggregate_id == "ws-1"
    assert w_event.tenant_id == "tenant-123"
    assert w_event.organization_id == "org-1"
    assert w_event.name == "Pediatrics"


