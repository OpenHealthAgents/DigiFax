"""
events.py
Domain Events generated during Tenant Configuration updates.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from src.domain.common.domain_event import DomainEvent


@dataclass(frozen=True)
class TenantConfigurationUpdatedEvent(DomainEvent):
    """Event fired when configuration parameters are updated."""
    tenant_id: str
    changes: dict[str, Any]
    occurred_at: datetime = field(default_factory=datetime.utcnow)
