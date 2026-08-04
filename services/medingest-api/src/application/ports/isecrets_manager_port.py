"""
isecrets_manager_port.py
Outbound port abstracting key vault secrets storage (e.g. HashiCorp Vault, AWS Secrets Manager).
"""

from abc import ABC, abstractmethod


class ISecretsManagerPort(ABC):
    """
    Interface port for retrieving system Master Keys and storing secrets.
    """

    @abstractmethod
    def get_master_key(self) -> bytes:
        """Retrieves system-wide Master Key bytes used to encrypt tenant KEKs."""
        pass

    @abstractmethod
    def store_secret(self, name: str, value: str) -> None:
        """Stores a named credential secret in vault."""
        pass

    @abstractmethod
    def get_secret(self, name: str) -> str | None:
        """Retrieves a named credential secret from vault."""
        pass
