"""
branding_validator_service.py
Domain Service performing cross-attribute visual validation checks (WCAG accessibility contrast).
"""

from src.domain.tenant_branding.value_objects import ColorPalette


class BrandingValidatorService:
    """
    Domain Service enforcing accessibility gates (WCAG contrast checks) across color parameters.
    """

    @staticmethod
    def _get_luminance(hex_color: str) -> float:
        """Calculates relative sRGB luminance of a hex color code."""
        color = hex_color.lstrip('#')
        if len(color) == 3:
            color = "".join(c * 2 for c in color)
        
        # Convert hex channels to normalized sRGB floats
        r, g, b = [int(color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
        
        # Apply standard gamma expansion
        def expand(c: float) -> float:
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        return 0.2126 * expand(r) + 0.7152 * expand(g) + 0.0722 * expand(b)

    @classmethod
    def check_accessibility(cls, palette: ColorPalette) -> None:
        """
        Validates WCAG contrast ratio bounds between primary branding color and backgrounds.
        
        Formula:
            Ratio = (L1 + 0.05) / (L2 + 0.05)
            where L1 is the lighter relative luminance, and L2 is the darker.
        """
        l_primary = cls._get_luminance(palette.primary)
        l_background = cls._get_luminance(palette.background)

        l1 = max(l_primary, l_background)
        l2 = min(l_primary, l_background)

        contrast_ratio = (l1 + 0.05) / (l2 + 0.05)

        # WCAG minimum contrast ratio requirement for large text is 3.0:1
        if contrast_ratio < 3.0:
            raise ValueError(
                f"Contrast ratio between primary ({palette.primary}) and background "
                f"({palette.background}) is {contrast_ratio:.2f}:1, which is below the WCAG 3.0:1 threshold."
            )
