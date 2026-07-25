import uuid


class UniqueId:
    """Utility to generate and check UUID identifiers."""

    @staticmethod
    def generate() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def is_valid(val: str) -> bool:
        try:
            uuid.UUID(val)
            return True
        except (ValueError, TypeError):
            return False
