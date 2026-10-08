"""
Editorial Infographic Design System
====================================
Modular infographic package providing print-grade editorial layouts,
ink scientific illustrations, typography, and palette utilities.
"""

from src.infographic.palette import (
    ACCENT_MAUVE,
    ACCENT_OCHRE,
    ACCENT_SAGE,
    ACCENT_TERRACOTTA,
    EDITORIAL_ACCENTS,
    PAPER_BG,
    PAPER_BORDER,
    PAPER_PANEL,
    get_category_color,
)
from src.infographic.renderer import (
    derive_daily_insight,
    generate_daily_infographic,
    render_editorial_infographic,
)
from src.infographic.layout import compute_editorial_layout

__all__ = [
    "generate_daily_infographic",
    "render_editorial_infographic",
    "compute_editorial_layout",
    "derive_daily_insight",
    "PAPER_BG",
    "PAPER_BORDER",
    "PAPER_PANEL",
    "EDITORIAL_ACCENTS",
    "ACCENT_TERRACOTTA",
    "ACCENT_SAGE",
    "ACCENT_MAUVE",
    "ACCENT_OCHRE",
    "get_category_color",
]
