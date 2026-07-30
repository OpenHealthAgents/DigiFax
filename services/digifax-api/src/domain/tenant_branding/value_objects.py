"""
value_objects.py
Domain Value Objects representing Tenant Branding parameters.
"""

from dataclasses import dataclass
from typing import Any
from src.domain.common.value_object import ValueObject


@dataclass(frozen=True)
class ColorPalette(ValueObject):
    """Immutable color palette mapping (hex colors)."""
    primary: str
    secondary: str
    accent: str
    background: str

    def __post_init__(self) -> None:
        # Simple hex format validation
        for attr in ["primary", "secondary", "accent", "background"]:
            val = getattr(self, attr)
            if not val.startswith("#") or len(val) not in [4, 7]:
                raise ValueError(f"Color {attr} must be a valid hex color code (e.g. #ffffff)")


@dataclass(frozen=True)
class BrandingTheme(ValueObject):
    """Immutable branding theme packaging palette, fonts, and dark mode state."""
    palette: ColorPalette
    font_family: str
    dark_mode_preferred: bool = False


@dataclass(frozen=True)
class LogoSettings(ValueObject):
    """Immutable asset url pointers."""
    light_logo_url: str
    dark_logo_url: str
    fav_icon_url: str


@dataclass(frozen=True)
class CustomDomain(ValueObject):
    """Immutable domain routing mapping and state tracking."""
    hostname: str
    status: str  # PENDING, ACTIVE, FAILED
    ssl_configured: bool = False

    def __post_init__(self) -> None:
        if not self.hostname.strip() or "." not in self.hostname:
            raise ValueError("Hostname must be a valid domain address (e.g. portal.hospital.org)")
