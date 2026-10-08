"""
Data-Driven Graphs and Charts Engine
====================================
Renders clean, data-driven charts and visual graphics:
- Donut charts with center hole labels and category percentages
- Horizontal progress bars with counts and percentages
- Research score comparative benchmark graphs
- Concept tile matrices and editorial pull-quote cards
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch, Rectangle

from src.infographic.palette import (
    ACCENT_TERRACOTTA,
    INK_MUTED,
    INK_PRIMARY,
    INK_SECONDARY,
    MOD_BLUE,
    MOD_EMERALD,
    MOD_VIOLET,
    MODERN_BORDER,
    MODERN_TEXT_MAIN,
    MODERN_TEXT_MUTED,
    PAPER_BORDER,
    PAPER_PANEL,
    get_category_color,
    get_modern_category_color,
)
from src.infographic.typography import get_sans_prop, get_serif_prop, wrap_text_lines

AR = 10.0 / 14.14  # Canvas Aspect Ratio (~0.7072)


def draw_donut_chart(
    ax: plt.Axes,
    cx: float,
    cy: float,
    radius: float,
    categories: Dict[str, int],
    total_papers: int = 3,
    colors: Optional[List[str]] = None,
) -> None:
    """
    Renders a clean, modern donut chart with colored slices and center paper counter.
    Aspect-ratio corrected so the donut is a true circle on portrait canvas.
    """
    if not categories:
        categories = {"Robotics": 1, "Edge AI": 1, "Systems": 1}

    labels = list(categories.keys())
    counts = list(categories.values())
    total = sum(counts) if sum(counts) > 0 else 1

    if colors is None:
        palette = [MOD_BLUE, MOD_VIOLET, MOD_EMERALD, "#F59E0B", "#F43F5E"]
        colors = [palette[i % len(palette)] for i in range(len(labels))]

    # Draw colored wedge segments using concentric arc polygons or pie wedge calculation
    start_angle = 90.0
    hole_radius = radius * 0.58

    import numpy as np

    for count, color in zip(counts, colors):
        angle_span = (count / total) * 360.0
        theta = np.linspace(
            np.radians(start_angle),
            np.radians(start_angle - angle_span),
            30
        )
        # Outer arc
        x_out = cx + radius * np.cos(theta)
        y_out = cy + (radius * np.sin(theta)) * AR
        # Inner arc
        x_in = cx + hole_radius * np.cos(theta[::-1])
        y_in = cy + (hole_radius * np.sin(theta[::-1])) * AR

        verts = list(zip(np.concatenate([x_out, x_in]), np.concatenate([y_out, y_in])))
        poly = plt.Polygon(
            verts, closed=True, facecolor=color, edgecolor="#FFFFFF", linewidth=2.0, zorder=5
        )
        ax.add_patch(poly)
        start_angle -= angle_span

    # Center circle hole
    hole = Ellipse(
        (cx, cy),
        2 * hole_radius,
        2 * hole_radius * AR,
        facecolor="#FFFFFF",
        edgecolor="none",
        zorder=6
    )
    ax.add_patch(hole)

    # Center Text: Number and label
    ax.text(
        cx, cy + 0.010 * AR, f"{total_papers}",
        fontproperties=get_sans_prop(16, weight="bold"),
        color=MODERN_TEXT_MAIN, ha="center", va="center", zorder=7
    )
    ax.text(
        cx, cy - 0.016 * AR, "Papers",
        fontproperties=get_sans_prop(7.5, weight="bold"),
        color=MODERN_TEXT_MUTED, ha="center", va="center", zorder=7
    )


def draw_modern_category_bars(
    ax: plt.Axes,
    x: float,
    y: float,
    width: float,
    categories: Dict[str, int],
    total_papers: int = 3,
) -> None:
    """
    Renders modern horizontal progress bars with labels, tracks, and percentages.
    Example: 'cs.RO Robotics [============] 1 (33%)'
    """
    items = list(categories.items())[:3]
    if not items:
        items = [("cs.RO", 1), ("cs.DC", 1), ("cs.AI", 1)]

    cat_friendly = {
        "cs.ro": ("cs.RO", "Robotics"),
        "cs.dc": ("cs.DC", "Distributed Computing"),
        "cs.ai": ("cs.AI", "Artificial Intelligence"),
        "cs.cv": ("cs.CV", "Computer Vision"),
        "cs.lg": ("cs.LG", "Machine Learning"),
        "robotics": ("cs.RO", "Robotics"),
        "iot": ("cs.DC", "IoT & Edge"),
    }

    palette = [MOD_BLUE, MOD_VIOLET, MOD_EMERALD, "#F59E0B"]
    row_h = 0.027
    bar_w = width * 0.70
    track_h = 0.007

    for i, (cat_raw, count) in enumerate(items):
        row_y = y - (i * row_h)
        code, name = cat_friendly.get(cat_raw.lower(), (cat_raw.upper(), cat_raw.title()))
        pct = (count / max(1, total_papers)) * 100
        color = palette[i % len(palette)]

        # Code and Name text
        ax.text(
            x, row_y + 0.009, code,
            fontproperties=get_sans_prop(7.5, weight="bold"),
            color=MODERN_TEXT_MAIN, va="bottom"
        )
        ax.text(
            x + 0.040, row_y + 0.009, name,
            fontproperties=get_sans_prop(7),
            color=MODERN_TEXT_MUTED, va="bottom"
        )

        # Background track
        track = FancyBboxPatch(
            (x, row_y), bar_w, track_h,
            boxstyle="round,pad=0.001,rounding_size=0.003",
            facecolor="#E2E8F0", edgecolor="none", zorder=3
        )
        ax.add_patch(track)

        # Filled bar
        fill_w = max(0.015, bar_w * (count / max(1, total_papers)))
        fill = FancyBboxPatch(
            (x, row_y), fill_w, track_h,
            boxstyle="round,pad=0.001,rounding_size=0.003",
            facecolor=color, edgecolor="none", zorder=4
        )
        ax.add_patch(fill)

        # Count & Percentage
        ax.text(
            x + bar_w + 0.010, row_y + track_h / 2,
            f"{count} ({pct:.0f}%)",
            fontproperties=get_sans_prop(7, weight="bold"),
            color=MODERN_TEXT_MAIN, va="center"
        )


def draw_score_comparison_chart(
    ax: plt.Axes,
    x: float,
    y: float,
    width: float,
    papers: List[Any],
) -> None:
    """
    Renders a comparative research score benchmark chart for top papers.
    Shows horizontal score meters with scores and paper titles.
    """
    top = papers[:3]
    row_h = 0.038
    bar_w = width * 0.65
    bar_h = 0.010

    for i, p in enumerate(top):
        row_y = y - (i * row_h)
        score = float(getattr(p, "relevance_score", 0.90))
        title = getattr(p, "title", "Paper")
        short_title = title[:24] + "..." if len(title) > 24 else title

        ax.text(
            x, row_y + 0.013, f"#{i+1:02d} {short_title}",
            fontproperties=get_sans_prop(7.5, weight="bold"),
            color=INK_PRIMARY, va="bottom"
        )

        # Track
        track = FancyBboxPatch(
            (x, row_y), bar_w, bar_h,
            boxstyle="round,pad=0.001,rounding_size=0.003",
            facecolor="#EAE5DA", edgecolor="none", zorder=3
        )
        ax.add_patch(track)

        # Fill
        fill_w = max(0.02, bar_w * min(1.0, score))
        fill = FancyBboxPatch(
            (x, row_y), fill_w, bar_h,
            boxstyle="round,pad=0.001,rounding_size=0.003",
            facecolor=ACCENT_TERRACOTTA, edgecolor="none", zorder=4
        )
        ax.add_patch(fill)

        ax.text(
            x + bar_w + 0.012, row_y + bar_h / 2,
            f"{score:.2f}",
            fontproperties=get_serif_prop(8.5, weight="bold"),
            color=INK_PRIMARY, va="center"
        )


def draw_modern_concept_grid(
    ax: plt.Axes,
    x: float,
    y: float,
    width: float,
    concepts_list: List[str],
) -> None:
    """
    Renders the 8 modern rounded concept cards in a 2-column x 4-row layout
    with icon badges and clean subtitle descriptions.
    """
    default_concepts = [
        ("Vision Transformer", "Visual understanding + attention", MOD_BLUE),
        ("Sim-to-Real Transfer", "From simulation to real world", MOD_VIOLET),
        ("Robot Navigation", "Autonomous movement & path planning", MOD_EMERALD),
        ("Reinforcement Learning", "Learn from interaction", "#F59E0B"),
        ("TinyML", "AI on low-power devices", "#EF4444"),
        ("Quantization", "Smaller models, faster inference", "#F97316"),
        ("Edge Computing", "Compute closer to the data", "#0284C7"),
        ("Low-power", "Energy efficient AI systems", "#EC4899"),
    ]

    col_w = (width - 0.018) / 2.0
    card_h = 0.048
    gap_y = 0.010

    for i in range(8):
        c_idx = i % 2
        r_idx = i // 2
        cx = x + (c_idx * (col_w + 0.018))
        cy = y - (r_idx * (card_h + gap_y))

        title, desc, color = default_concepts[i]
        if i < len(concepts_list) and concepts_list[i]:
            title = concepts_list[i]

        card = FancyBboxPatch(
            (cx, cy), col_w, card_h,
            boxstyle="round,pad=0.002,rounding_size=0.008",
            facecolor="#F8FAFC",
            edgecolor="#E2E8F0",
            linewidth=1.0,
            zorder=3
        )
        ax.add_patch(card)

        # Icon circle
        icon_cx = cx + 0.016
        icon_cy = cy + card_h / 2
        icon_circ = Ellipse(
            (icon_cx, icon_cy),
            0.018, 0.018 * AR,
            facecolor=f"{color}18",
            edgecolor=color,
            linewidth=1.0,
            zorder=4
        )
        ax.add_patch(icon_circ)

        # Title (clean full string up to 24 chars)
        ax.text(
            cx + 0.032, cy + card_h * 0.65,
            title[:24],
            fontproperties=get_sans_prop(6.8, weight="bold"),
            color=MODERN_TEXT_MAIN, va="center", zorder=5
        )
        # Subtitle
        ax.text(
            cx + 0.032, cy + card_h * 0.30,
            desc[:32],
            fontproperties=get_sans_prop(6.0),
            color=MODERN_TEXT_MUTED, va="center", zorder=5
        )


def draw_category_distribution(
    ax: plt.Axes,
    x: float,
    y: float,
    categories: Dict[str, int],
    total_papers: int = 3,
) -> None:
    """Editorial category horizontal bars with paper counts."""
    cat_items = list(categories.items())[:4]
    if not cat_items:
        cat_items = [("Robotics", 1), ("Machine Learning", 1), ("Artificial Intelligence", 1), ("IoT & Edge Computing", 1)]

    cat_names_map = {
        "cs.ro": "Robotics",
        "cs.dc": "IoT & Edge Computing",
        "cs.ai": "Artificial Intelligence",
        "cs.lg": "Machine Learning",
        "cs.cv": "Computer Vision",
    }

    row_h = 0.028
    bar_max_w = 0.095
    bar_h = 0.010

    for i, (cat_raw, count) in enumerate(cat_items):
        row_y = y - (i * row_h)
        clean_name = cat_names_map.get(cat_raw.lower(), cat_raw.title())
        style = get_category_color(clean_name, default_idx=i)
        pct = count / max(1, total_papers)
        fill_w = max(0.015, bar_max_w * pct)

        ax.text(
            x, row_y, clean_name[:20],
            fontproperties=get_sans_prop(7.5),
            color=INK_PRIMARY, va="center"
        )

        bar_x = x + 0.110
        bar = Rectangle(
            (bar_x, row_y - bar_h / 2),
            fill_w, bar_h,
            facecolor=style["accent"], edgecolor="none"
        )
        ax.add_patch(bar)

        ax.text(
            bar_x + bar_max_w + 0.025, row_y,
            f"{count}",
            fontproperties=get_sans_prop(7.5, weight="bold"),
            color=INK_PRIMARY, va="center"
        )


def draw_concept_tiles(
    ax: plt.Axes,
    x: float,
    y: float,
    concepts: List[str],
) -> None:
    """Renders 6 editorial concept cards in 2 columns."""
    display_concepts = (concepts[:6] if len(concepts) >= 6 else concepts + [
        "Vision Transformer", "Robot Navigation", "Reinforcement Learning",
        "TinyML", "Sim-to-Real Transfer", "Quantization"
    ])[:6]

    col_w = 0.120
    card_h = 0.024
    gap_x = 0.010
    gap_y = 0.008

    for i, concept in enumerate(display_concepts):
        c_idx = i % 2
        r_idx = i // 2
        cx = x + (c_idx * (col_w + gap_x))
        cy = y - (r_idx * (card_h + gap_y))

        card = FancyBboxPatch(
            (cx, cy), col_w, card_h,
            boxstyle="round,pad=0.001,rounding_size=0.004",
            facecolor=PAPER_PANEL, edgecolor=PAPER_BORDER, linewidth=0.7
        )
        ax.add_patch(card)

        clean_concept = concept.replace("_", " ").title()
        ax.text(
            cx + col_w / 2, cy + card_h / 2,
            clean_concept[:18],
            fontproperties=get_sans_prop(7),
            color=INK_PRIMARY, ha="center", va="center"
        )


def draw_editorial_insight_card(
    ax: plt.Axes,
    x: float,
    y: float,
    insight_text: str,
    kicker: str = "SMALLER MODELS. BIGGER IMPACT.",
) -> None:
    """Renders the editorial quote card with vertical rule and red underline."""
    ax.text(
        x, y, "TODAY'S INSIGHT",
        fontproperties=get_sans_prop(8, weight="bold"),
        color=INK_PRIMARY
    )

    wrapped_quote = wrap_text_lines(f'"{insight_text}"', max_chars=34, max_lines=5)
    ax.text(
        x + 0.025, y - 0.022, wrapped_quote,
        fontproperties=get_serif_prop(11, style="italic"),
        color=INK_PRIMARY, va="top", linespacing=1.35
    )

    num_lines = len(wrapped_quote.split("\n"))
    line_y = y - 0.022 - (num_lines * 0.019) - 0.010
    ax.plot([x + 0.025, x + 0.095], [line_y, line_y], color=ACCENT_TERRACOTTA, linewidth=1.2)

    ax.text(
        x + 0.025, line_y - 0.014, kicker,
        fontproperties=get_sans_prop(7, weight="bold"),
        color=INK_MUTED, va="top"
    )
