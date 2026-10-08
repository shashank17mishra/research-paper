"""
Infographic Color Palette System
================================
Supports multiple distinct publication styles:
1. Editorial Journal: Warm ivory, deep charcoal, muted terracotta/sage/mauve/ochre.
2. Modern Studio: Soft slate/white, tech indigo, violet, emerald, amber.
3. Spotlight Broadside: Warm parchment, canary yellow, deep carbon black, terracotta.
"""

from __future__ import annotations

from typing import Dict, List

# ==============================================================================
# 1. EDITORIAL BROADSHEET PALETTE
# ==============================================================================
PAPER_BG = "#F8F5EE"          # Warm ivory / newsprint paper
PAPER_PANEL = "#F0EAE0"       # Subtle warm tint for cards/chips
PAPER_BORDER = "#D6CFBF"      # Delicate editorial hairline rule
PAPER_BORDER_DARK = "#2B2621" # Heavy contrast rule for headers

INK_PRIMARY = "#191715"       # Deep carbon charcoal for primary headings
INK_SECONDARY = "#46413A"     # Editorial muted body text
INK_MUTED = "#7D7569"         # Small caps, metadata, timestamps

ACCENT_TERRACOTTA = "#BA4D30" # Rich terracotta
ACCENT_SAGE = "#5D7A58"       # Muted herbal sage
ACCENT_MAUVE = "#8A586B"      # Dusty editorial mauve
ACCENT_OCHRE = "#C38332"      # Warm vintage ochre
ACCENT_OLIVE = "#6E7A4A"      # Earthy olive green
ACCENT_BROWN = "#82634C"      # Soft saddle brown

EDITORIAL_ACCENTS: List[str] = [
    ACCENT_TERRACOTTA,
    ACCENT_SAGE,
    ACCENT_MAUVE,
    ACCENT_OCHRE,
    ACCENT_OLIVE,
    ACCENT_BROWN,
]

ACCENT_WASHES: Dict[str, str] = {
    ACCENT_TERRACOTTA: "#F5DFD8",
    ACCENT_SAGE: "#E0EADF",
    ACCENT_MAUVE: "#ECE0E5",
    ACCENT_OCHRE: "#F6EADA",
    ACCENT_OLIVE: "#E8EDE0",
    ACCENT_BROWN: "#EBE3DC",
}

# ==============================================================================
# 2. MODERN STUDIO PALETTE
# ==============================================================================
MODERN_BG = "#F7F9FC"
MODERN_CARD_BG = "#FFFFFF"
MODERN_BORDER = "#E2E8F0"
MODERN_TEXT_MAIN = "#0F172A"
MODERN_TEXT_MUTED = "#64748B"
MODERN_TEXT_SUB = "#334155"

MOD_BLUE = "#4F46E5"
MOD_VIOLET = "#8B5CF6"
MOD_EMERALD = "#10B981"
MOD_AMBER = "#F59E0B"
MOD_ROSE = "#F43F5E"
MOD_CYAN = "#06B6D4"

MODERN_ACCENTS: List[str] = [MOD_BLUE, MOD_VIOLET, MOD_EMERALD, MOD_AMBER, MOD_ROSE, MOD_CYAN]

MODERN_WASHES: Dict[str, str] = {
    MOD_BLUE: "#EEF2FF",
    MOD_VIOLET: "#F5F3FF",
    MOD_EMERALD: "#ECFDF5",
    MOD_AMBER: "#FFFBEB",
    MOD_ROSE: "#FFF1F2",
    MOD_CYAN: "#ECFEFF",
}

# ==============================================================================
# 3. SPOTLIGHT GEN-Z BROADSIDE PALETTE
# ==============================================================================
SPOT_BG = "#F9F7F1"
SPOT_YELLOW = "#FCD34D"       # Yellow square vignette background
SPOT_YELLOW_DARK = "#D97706"
SPOT_INK = "#111111"
SPOT_INK_MUTED = "#555555"
SPOT_BORDER = "#E5E1D5"
SPOT_TERRACOTTA = "#C2410C"
SPOT_SAGE = "#4D7C0F"


def get_accent_for_index(idx: int) -> str:
    """Returns a deterministic accent color from the editorial palette."""
    return EDITORIAL_ACCENTS[idx % len(EDITORIAL_ACCENTS)]


def get_wash_for_accent(accent: str) -> str:
    """Returns the soft tint wash corresponding to an accent color."""
    if accent in ACCENT_WASHES:
        return ACCENT_WASHES[accent]
    if accent in MODERN_WASHES:
        return MODERN_WASHES[accent]
    return "#EAE5DA"


def get_category_color(category_str: str, default_idx: int = 0) -> Dict[str, str]:
    """Returns an accent color and soft wash for a category dynamically."""
    clean_cat = category_str.lower().strip()
    hash_val = sum(ord(c) for c in clean_cat) + default_idx
    accent = EDITORIAL_ACCENTS[hash_val % len(EDITORIAL_ACCENTS)]
    wash = get_wash_for_accent(accent)
    return {
        "accent": accent,
        "wash": wash,
        "border": PAPER_BORDER,
        "text": INK_PRIMARY
    }


def get_modern_category_color(category_str: str, default_idx: int = 0) -> Dict[str, str]:
    """Returns modern studio accent colors for category tags and chart wedges."""
    clean_cat = category_str.lower().strip()
    hash_val = sum(ord(c) for c in clean_cat) + default_idx
    accent = MODERN_ACCENTS[hash_val % len(MODERN_ACCENTS)]
    wash = MODERN_WASHES.get(accent, "#F1F5F9")
    return {
        "accent": accent,
        "wash": wash,
        "border": MODERN_BORDER,
        "text": accent
    }
