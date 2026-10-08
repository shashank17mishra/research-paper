"""
Editorial Research Overview Charts & Concept Panels
===================================================
Renders minimalist, publication-grade category distributions,
concept tiles, and the prominent daily research synthesis insight card.
"""

from __future__ import annotations

from typing import Dict, List
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

from src.infographic.palette import (
    EDITORIAL_ACCENTS,
    INK_MUTED,
    INK_PRIMARY,
    INK_SECONDARY,
    PAPER_BORDER,
    PAPER_PANEL,
)
from src.infographic.typography import get_sans_prop, get_serif_prop, wrap_text_lines

AR = 10.0 / 14.14


def draw_category_distribution(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    category_counts: Dict[str, int]
) -> None:
    """
    Renders 'TODAY'S RESEARCH AREAS' with minimal horizontal bars,
    clean editorial typography, and exact counts.
    """
    # Header
    ax.text(
        x, y + h - 0.015, "TODAY'S RESEARCH AREAS",
        fontproperties=get_sans_prop(8.5, weight="bold"),
        color=INK_PRIMARY
    )
    ax.text(
        x, y + h - 0.045, "Papers by category",
        fontproperties=get_serif_prop(8.0, style="italic"),
        color=INK_MUTED
    )

    if not category_counts:
        category_counts = {
            "Robotics": 1,
            "Machine Learning": 1,
            "Artificial Intelligence": 1,
            "IoT & Edge Computing": 0
        }

    # Ensure 4 standard slots
    standard_slots = [
        ("Robotics", category_counts.get("Robotics", category_counts.get("cs.RO", 1))),
        ("Machine Learning", category_counts.get("Machine Learning", category_counts.get("cs.LG", 1))),
        ("Artificial Intelligence", category_counts.get("Artificial Intelligence", category_counts.get("cs.AI", 1))),
        ("IoT & Edge Computing", category_counts.get("IoT & Edge AI", category_counts.get("cs.DC", 0))),
    ]

    max_count = max([c for _, c in standard_slots], default=1)
    if max_count == 0:
        max_count = 1

    bar_start_y = y + h - 0.075
    row_gap = (h - 0.09) / 4

    for i, (clean_name, count) in enumerate(standard_slots):
        row_y = bar_start_y - (i * row_gap)
        accent = EDITORIAL_ACCENTS[i % len(EDITORIAL_ACCENTS)]

        # Category Label
        ax.text(
            x, row_y, clean_name,
            fontproperties=get_sans_prop(7.5),
            color=INK_SECONDARY,
            va="center"
        )

        # Bar Track and Fill
        bar_x = x + w * 0.44
        max_bar_w = w * 0.42
        bar_w = max_bar_w * (count / max_count)
        bar_h = 0.015 * AR

        if count > 0:
            bar = Rectangle(
                (bar_x, row_y - bar_h / 2), max(bar_w, 0.01), bar_h,
                facecolor=accent, edgecolor="none"
            )
            ax.add_patch(bar)

        # Count number
        ax.text(
            bar_x + max_bar_w + 0.02, row_y, str(count),
            fontproperties=get_serif_prop(8.0, weight="bold"),
            color=INK_PRIMARY,
            ha="left", va="center"
        )


def draw_concept_tiles(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    concepts: List[str]
) -> None:
    """
    Renders 'KEY CONCEPTS TODAY' as subtle, flat, lightly bordered
    editorial cards in a neat 2-column grid.
    """
    ax.text(
        x, y + h - 0.015, "KEY CONCEPTS TODAY",
        fontproperties=get_sans_prop(8.5, weight="bold"),
        color=INK_PRIMARY
    )
    ax.text(
        x, y + h - 0.045, "The ideas showing up across today's research",
        fontproperties=get_serif_prop(8.0, style="italic"),
        color=INK_MUTED
    )

    default_pool = [
        "Vision Transformers", "Robot Navigation",
        "Reinforcement Learning", "Quantization",
        "Edge Computing", "Multi-Agent Systems"
    ]
    display_concepts = (concepts + default_pool)[:6]

    cols = 2
    rows = 3
    col_gap = 0.015
    tile_w = (w - col_gap) / cols
    row_gap = (h - 0.075) / rows
    tile_h = row_gap * 0.78

    for idx, c_name in enumerate(display_concepts):
        col = idx % cols
        row = idx // cols
        tx = x + (col * (tile_w + col_gap))
        ty = (y + h - 0.070) - ((row + 1) * row_gap) + (row_gap - tile_h) / 2

        # Card patch
        tile_patch = FancyBboxPatch(
            (tx, ty), tile_w, tile_h,
            boxstyle="round,pad=0.002,rounding_size=0.006",
            facecolor=PAPER_PANEL,
            edgecolor=PAPER_BORDER,
            linewidth=0.7
        )
        ax.add_patch(tile_patch)

        ax.text(
            tx + tile_w / 2, ty + tile_h / 2,
            c_name,
            fontproperties=get_sans_prop(7.0),
            color=INK_PRIMARY,
            ha="center", va="center"
        )


def draw_editorial_insight_card(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    insight_text: str,
    tagline: str = "SMALLER MODELS. BIGGER IMPACT."
) -> None:
    """
    Renders 'TODAY'S INSIGHT' with an elegant quote, prominent high-contrast
    italic serif body, and a punchy bottom kicker.
    """
    ax.text(
        x, y + h - 0.015, "TODAY'S INSIGHT",
        fontproperties=get_sans_prop(8.5, weight="bold"),
        color=INK_PRIMARY
    )

    # Vertical subtle rule
    ax.plot([x, x], [y + 0.015, y + h - 0.045], color=PAPER_BORDER, linewidth=1.2)

    # Main Insight Quote
    wrapped_insight = wrap_text_lines(
        f'"{insight_text}"',
        max_chars=32, max_lines=4
    )
    ax.text(
        x + 0.020, y + h - 0.050,
        wrapped_insight,
        fontproperties=get_serif_prop(10.0, style="italic"),
        color=INK_PRIMARY,
        va="top", linespacing=1.35
    )

    # Hairline divider
    ax.plot([x + 0.020, x + w], [y + 0.032, y + 0.032], color=PAPER_BORDER, linewidth=0.7)

    # Bottom Tagline Kicker
    ax.text(
        x + 0.020, y + 0.012, tagline.upper(),
        fontproperties=get_sans_prop(6.5, weight="bold"),
        color=INK_MUTED
    )
