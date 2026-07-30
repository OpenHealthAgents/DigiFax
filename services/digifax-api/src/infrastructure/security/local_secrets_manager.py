"""
local_secrets_manager.py
Local in-memory Secrets Manager adapter.
"""

from src.application.ports.isecrets_manager_port import ISecretsManagerPort


class LocalSecretsManager(ISecretsManagerPort):
    """
    Local secrets store pre-seeding an immutable Master Key for KEK wrapping.
    """

    def __init__(self) -> None:
        # Pre-seed a 32-byte Master Key (256-bit AES)
        self._master_key = b"OpenHealthSystemMasterKeyVault32"
        self._secrets: dict[str, str] = {}

    def get_master_key(self) -> bytes:
        """Retrieves 32-byte Master Key bytes."""
        return self._master_key

    def store_secret(self, name: str, value: str) -> None:
        """Saves credentials in secrets cache."""
        self._secrets[name] = value

    def get_secret(self, name: str) -> str | None:
        """Retrieves credentials from secrets cache."""
        return self._secrets.get(name)
