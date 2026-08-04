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
        for attr in ["primary", "secondary", "accent", "background"]:
            val = getattr(self, attr)
            if not val.startswith("#") or len(val) not in [4, 7]:
                raise ValueError(f"Color {attr} must be a valid hex color code (e.g. #ffffff)")


@dataclass(frozen=True)
class Typography(ValueObject):
    """Immutable typography styles."""
    font_family: str
    font_size_base: str = "14px"

    def __post_init__(self) -> None:
        if not self.font_family.strip():
            raise ValueError("Font family cannot be empty")


@dataclass(frozen=True)
class ContactSupport(ValueObject):
    """Immutable support support contact details."""
    support_email: str
    support_phone: str
    support_website: str

    def __post_init__(self) -> None:
        if "@" not in self.support_email or "." not in self.support_email:
            raise ValueError("Support email must be valid")
        if not self.support_phone.strip():
            raise ValueError("Support phone cannot be empty")
        if not self.support_website.startswith("http://") and not self.support_website.startswith("https://"):
            raise ValueError("Support website must be a valid URL starting with http:// or https://")


@dataclass(frozen=True)
class EmailBranding(ValueObject):
    """Immutable outbound emails styling attributes."""
    primary_color: str
    header_html: str
    footer_html: str

    def __post_init__(self) -> None:
        if not self.primary_color.startswith("#") or len(self.primary_color) not in [4, 7]:
            raise ValueError("Email primary color must be a valid hex color code")


@dataclass(frozen=True)
class CustomAssets(ValueObject):
    """Immutable custom portal media URLs."""
    login_background_url: str
    dashboard_banner_url: str


@dataclass(frozen=True)
class DocumentAssets(ValueObject):
    """Immutable watermark and PDF layout templates."""
    watermark_text_or_url: str
    report_header_html: str
    report_footer_html: str


@dataclass(frozen=True)
class BrandingTheme(ValueObject):
    """Immutable branding theme packaging palette, fonts, and dark mode state."""
    palette: ColorPalette
    typography: Typography
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
