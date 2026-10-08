"""
Editorial Color Palette System
==============================
A restrained, warm, print-inspired palette inspired by independent magazines,
research publications, and classic editorial broadsheets.

Rules:
- NO blue / cyan / neon / electric colors.
- 70-80% neutral warm ivory / paper base.
- 15-20% deep charcoal ink.
- 5-10% muted accents: terracotta, sage, dusty mauve, warm ochre, olive, soft brown.
"""

from __future__ import annotations

from typing import Dict, List

# Core Neutral Foundations
PAPER_BG = "#F8F5EE"       # Warm ivory / newsprint paper
PAPER_PANEL = "#F0EAE0"    # Subtle warm tint for cards/chips
PAPER_BORDER = "#D6CFBF"   # Delicate editorial hairline rule
PAPER_BORDER_DARK = "#2B2621"  # Heavy contrast rule for headers

# Charcoal Inks
INK_PRIMARY = "#191715"    # Deep carbon charcoal for primary headings
INK_SECONDARY = "#46413A"  # Editorial muted body text
INK_MUTED = "#7D7569"      # Small caps, metadata, timestamps

# Editorial Muted Accents
ACCENT_TERRACOTTA = "#BA4D30"  # Rich terracotta
ACCENT_SAGE = "#5D7A58"        # Muted herbal sage
ACCENT_MAUVE = "#8A586B"       # Dusty editorial mauve
ACCENT_OCHRE = "#C38332"       # Warm vintage ochre
ACCENT_OLIVE = "#6E7A4A"       # Earthy olive green
ACCENT_BROWN = "#82634C"       # Soft saddle brown

EDITORIAL_ACCENTS: List[str] = [
    ACCENT_TERRACOTTA,
    ACCENT_SAGE,
    ACCENT_MAUVE,
    ACCENT_OCHRE,
    ACCENT_OLIVE,
    ACCENT_BROWN,
]

# Tinted background washes for illustration circles & pill backgrounds
ACCENT_WASHES: Dict[str, str] = {
    ACCENT_TERRACOTTA: "#F5DFD8",
    ACCENT_SAGE: "#E0EADF",
    ACCENT_MAUVE: "#ECE0E5",
    ACCENT_OCHRE: "#F6EADA",
    ACCENT_OLIVE: "#E8EDE0",
    ACCENT_BROWN: "#EBE3DC",
}


def get_accent_for_index(idx: int) -> str:
    """Returns a deterministic accent color from the editorial palette."""
    return EDITORIAL_ACCENTS[idx % len(EDITORIAL_ACCENTS)]


def get_wash_for_accent(accent: str) -> str:
    """Returns the soft tint wash corresponding to an accent color."""
    return ACCENT_WASHES.get(accent, "#EAE5DA")


def get_category_color(category_str: str, default_idx: int = 0) -> Dict[str, str]:
    """
    Returns an accent color and soft wash for a category dynamically.
    Avoids fixed color locking by hashing category name with fallback offset.
    """
    clean_cat = category_str.lower().strip()
    # Dynamic deterministic hash
    hash_val = sum(ord(c) for c in clean_cat) + default_idx
    accent = EDITORIAL_ACCENTS[hash_val % len(EDITORIAL_ACCENTS)]
    wash = get_wash_for_accent(accent)
    return {
        "accent": accent,
        "wash": wash,
        "border": PAPER_BORDER,
        "text": INK_PRIMARY
    }
