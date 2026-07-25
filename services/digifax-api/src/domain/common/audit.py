from datetime import datetime

from src.domain.common.value_object import ValueObject


class AuditFields(ValueObject):
    """Value object capturing typical database row audit timestamps/users."""

    def __init__(
        self,
        created_at: datetime,
        created_by: str,
        updated_at: datetime | None = None,
        updated_by: str | None = None
    ):
        self.created_at = created_at
        self.created_by = created_by
        self.updated_at = updated_at or created_at
        self.updated_by = updated_by or created_by

    def update(self, updated_at: datetime, updated_by: str) -> 'AuditFields':
        """Returns a new AuditFields instance reflecting the update."""
        return AuditFields(
            created_at=self.created_at,
            created_by=self.created_by,
            updated_at=updated_at,
            updated_by=updated_by
        )
