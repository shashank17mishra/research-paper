"""
Infographic Design System
=========================
Modular infographic package providing print-grade editorial layouts,
modern studio layouts, and spotlight broadside templates with data-driven
graphs, charts, and authentic illustration assets.
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
    TEMPLATES,
    derive_daily_insight,
    generate_daily_infographic,
    render_infographic,
)
from src.infographic.template_editorial import render_template_editorial as render_editorial_infographic

__all__ = [
    "generate_daily_infographic",
    "render_infographic",
    "render_editorial_infographic",
    "TEMPLATES",
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
