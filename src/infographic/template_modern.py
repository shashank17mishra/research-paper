"""
Template 2: Modern Tech Studio Infographic
==========================================
Clean, contemporary, modern research studio aesthetic modeled directly
on the primary visual reference. Features the researcher at laptop
artwork, rounded cards, donut chart, category progress bars, 8 concept tiles,
and metric counters.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch

from src.infographic.assets import place_raster_image
from src.infographic.charts import (
    draw_donut_chart,
    draw_modern_category_bars,
    draw_modern_concept_grid,
)
from src.infographic.palette import (
    MOD_BLUE,
    MOD_EMERALD,
    MOD_VIOLET,
    MODERN_BG,
    MODERN_BORDER,
    MODERN_CARD_BG,
    MODERN_TEXT_MAIN,
    MODERN_TEXT_MUTED,
    MODERN_TEXT_SUB,
    get_modern_category_color,
)
from src.infographic.typography import (
    get_sans_prop,
    get_serif_prop,
    synthesize_plain_explanation,
    wrap_text_lines,
)
from src.utils import setup_logger

logger = setup_logger("template_modern")

AR = 10.0 / 14.14  # Canvas Aspect Ratio (~0.7072)


def render_template_modern(data: Dict[str, Any], output_path: Path) -> bool:
    """Renders Template 2: Modern Tech Studio Infographic."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        papers: List[Any] = data.get("papers", [])
        raw_date: str = data.get("date", "08 October 2026")
        categories_dict: Dict[str, int] = data.get("categories", {})
        concepts_list: List[str] = data.get("concepts", [])

        fig = plt.figure(figsize=(10.0, 14.14), dpi=250)
        fig.patch.set_facecolor(MODERN_BG)

        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor(MODERN_BG)
        ax.axis("off")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        mx = 0.045  # Outer margin

        # -------------------------------------------------------------
        # 1. HEADER
        # -------------------------------------------------------------
        # Top kicker
        ax.text(
            mx, 0.965, "AUTONOMOUS RESEARCH INTELLIGENCE",
            fontproperties=get_sans_prop(7.5, weight="bold"),
            color=MODERN_TEXT_MUTED
        )

        # Title: "Daily Tech" in dark slate, "Intelligence" in vibrant indigo
        ax.text(
            mx, 0.915, "Daily Tech",
            fontproperties=get_sans_prop(32, weight="bold"),
            color=MODERN_TEXT_MAIN
        )
        ax.text(
            mx, 0.865, "Intelligence",
            fontproperties=get_sans_prop(32, weight="bold"),
            color=MOD_BLUE
        )

        # Date & Topic Badges
        p_y = 0.835
        # Calendar Date Pill
        date_pill = FancyBboxPatch(
            (mx, p_y), 0.170, 0.022,
            boxstyle="round,pad=0.002,rounding_size=0.006",
            facecolor="#FFFFFF", edgecolor=MODERN_BORDER, linewidth=1.0
        )
        ax.add_patch(date_pill)
        ax.text(
            mx + 0.085, p_y + 0.011, raw_date,
            fontproperties=get_sans_prop(7, weight="bold"),
            color=MODERN_TEXT_MAIN, ha="center", va="center"
        )

        # Topics Pill
        topics_pill = FancyBboxPatch(
            (mx + 0.185, p_y), 0.240, 0.022,
            boxstyle="round,pad=0.002,rounding_size=0.006",
            facecolor="#EEF2FF", edgecolor="none"
        )
        ax.add_patch(topics_pill)
        ax.text(
            mx + 0.185 + 0.120, p_y + 0.011, "AI  •  ML  •  Robotics  •  IoT",
            fontproperties=get_sans_prop(7, weight="bold"),
            color=MOD_BLUE, ha="center", va="center"
        )

        # Top Right: Real Researcher at Laptop Illustration with Lightbulb
        place_raster_image(
            ax, "researcher_laptop.png",
            x=0.620, y=0.815, width=0.340,
            ha="left", va="bottom", zorder=10
        )
        ax.text(
            0.630, 0.940, "Better\nResearch.\nBrighter\nIdeas.",
            fontproperties=get_serif_prop(10, style="italic"),
            color=MODERN_TEXT_SUB, ha="center", va="top", linespacing=1.2
        )

        # -------------------------------------------------------------
        # 2. FEATURED BREAKTHROUGHS (3 Rounded Cards)
        # -------------------------------------------------------------
        fb_y = 0.795
        # Header line
        ax.text(
            mx, fb_y, "FEATURED BREAKTHROUGHS",
            fontproperties=get_sans_prop(9.5, weight="bold"),
            color=MODERN_TEXT_MAIN, va="center"
        )

        # Papers Analyzed Pill Badge on right
        pa_pill = FancyBboxPatch(
            (1.0 - mx - 0.170, fb_y - 0.011), 0.170, 0.022,
            boxstyle="round,pad=0.002,rounding_size=0.006",
            facecolor="#EEF2FF", edgecolor="none"
        )
        ax.add_patch(pa_pill)
        ax.text(
            1.0 - mx - 0.085, fb_y, f"{len(papers)}  PAPERS ANALYZED",
            fontproperties=get_sans_prop(7.5, weight="bold"),
            color=MOD_BLUE, ha="center", va="center"
        )

        # 3 Paper Cards
        card_w = 1.0 - 2 * mx
        card_h = 0.108
        card_gap = 0.012
        card_start_y = fb_y - 0.022 - card_h

        top_three = papers[:3]
        badge_palette = [
            ("#3B82F6", "#DBEAFE", "ROBOTICS"),
            ("#8B5CF6", "#EDE9FE", "ML"),
            ("#10B981", "#D1FAE5", "AI"),
        ]
        modern_illus_assets = ["mod_quadruped.png", "mod_chip.png", "mod_warehouse.png"]

        for idx, p in enumerate(top_three):
            cy = card_start_y - (idx * (card_h + card_gap))
            title = getattr(p, "title", "Research Breakthrough")
            authors_list = getattr(p, "authors", [])
            authors_str = ", ".join(authors_list[:2]) + (" et al." if len(authors_list) > 2 else "")
            abstract = getattr(p, "abstract", "")
            primary_topic = getattr(p, "primary_topic", "AI")
            score = float(getattr(p, "relevance_score", 0.90))

            # Outer Card Box
            card = FancyBboxPatch(
                (mx, cy), card_w, card_h,
                boxstyle="round,pad=0.003,rounding_size=0.010",
                facecolor=MODERN_CARD_BG,
                edgecolor=MODERN_BORDER,
                linewidth=1.2,
                zorder=2
            )
            ax.add_patch(card)

            # Badges Row inside Card
            b_color, b_wash, b_label = badge_palette[idx % len(badge_palette)]
            bx = mx + 0.022
            by = cy + card_h - 0.022

            # #01 Rank Pill
            r_pill = FancyBboxPatch(
                (bx, by), 0.038, 0.015,
                boxstyle="round,pad=0.001,rounding_size=0.004",
                facecolor=b_color, edgecolor="none", zorder=3
            )
            ax.add_patch(r_pill)
            ax.text(
                bx + 0.019, by + 0.0075, f"#{idx+1:02d}",
                fontproperties=get_sans_prop(6.5, weight="bold"),
                color="#FFFFFF", ha="center", va="center", zorder=4
            )

            # Category Pill
            c_pill = FancyBboxPatch(
                (bx + 0.045, by), 0.065, 0.015,
                boxstyle="round,pad=0.001,rounding_size=0.004",
                facecolor=b_wash, edgecolor="none", zorder=3
            )
            ax.add_patch(c_pill)
            ax.text(
                bx + 0.045 + 0.0325, by + 0.0075, b_label,
                fontproperties=get_sans_prop(6.5, weight="bold"),
                color=b_color, ha="center", va="center", zorder=4
            )

            # Score Text
            ax.text(
                bx + 0.120, by + 0.0075, f"Score: {score:.2f}",
                fontproperties=get_sans_prop(7, weight="bold"),
                color="#059669", va="center", zorder=4
            )

            # Title & Authors
            wrapped_title = wrap_text_lines(title, max_chars=36, max_lines=2)
            ax.text(
                bx, by - 0.012, wrapped_title,
                fontproperties=get_sans_prop(9, weight="bold"),
                color=MODERN_TEXT_MAIN, va="top", zorder=4
            )

            t_lines = len(wrapped_title.split("\n"))
            auth_y = by - 0.012 - (t_lines * 0.016) - 0.004
            ax.text(
                bx, auth_y, authors_str,
                fontproperties=get_sans_prop(6.8),
                color=MODERN_TEXT_MUTED, va="top", zorder=4
            )

            # Plain English Explanation (Middle Column inside Card)
            plain_x = mx + 0.420
            plain_text = synthesize_plain_explanation(title, abstract, primary_topic)
            wrapped_plain = wrap_text_lines(plain_text, max_chars=34, max_lines=4)
            ax.text(
                plain_x, by + 0.008, wrapped_plain,
                fontproperties=get_sans_prop(7.2),
                color=MODERN_TEXT_SUB, va="top", linespacing=1.35, zorder=4
            )

            # Real Illustration on Right
            illus_asset = modern_illus_assets[idx % len(modern_illus_assets)]
            place_raster_image(
                ax, illus_asset,
                x=1.0 - mx - 0.180, y=cy + 0.012, width=0.165,
                ha="left", va="bottom", zorder=10
            )

        # -------------------------------------------------------------
        # 3. DATA ANALYTICS & CHARTS SECTION
        # -------------------------------------------------------------
        analytics_y = card_start_y - (2 * (card_h + card_gap)) - 0.035
        half_w = (card_w - 0.025) / 2.0

        # --- LEFT CARD: TOP CATEGORIES (Bars + Donut Chart) ---
        left_box = FancyBboxPatch(
            (mx, analytics_y - 0.230), half_w, 0.230,
            boxstyle="round,pad=0.003,rounding_size=0.010",
            facecolor=MODERN_CARD_BG, edgecolor=MODERN_BORDER, linewidth=1.2, zorder=2
        )
        ax.add_patch(left_box)

        # Section Title
        ax.text(
            mx + 0.022, analytics_y - 0.022, "TOP CATEGORIES",
            fontproperties=get_sans_prop(9, weight="bold"),
            color=MODERN_TEXT_MAIN, zorder=3
        )

        # Horizontal progress bars (top portion of left card)
        draw_modern_category_bars(
            ax, x=mx + 0.022, y=analytics_y - 0.044, width=half_w - 0.044,
            categories=categories_dict, total_papers=len(papers)
        )

        # Donut Chart inside Left Card (lower portion of left card)
        donut_cx = mx + 0.080
        donut_cy = analytics_y - 0.168
        draw_donut_chart(
            ax, cx=donut_cx, cy=donut_cy, radius=0.038,
            categories=categories_dict, total_papers=len(papers)
        )

        # Donut Legend on right side of donut
        leg_x = mx + 0.165
        leg_palette = [MOD_BLUE, MOD_VIOLET, MOD_EMERALD]
        cat_items = list(categories_dict.items())[:3]
        if not cat_items:
            cat_items = [("Robotics", 1), ("Distributed Computing", 1), ("AI", 1)]

        for l_i, (l_cat, l_cnt) in enumerate(cat_items):
            ly = donut_cy + 0.022 - (l_i * 0.022)
            dot = Ellipse((leg_x, ly), 0.009, 0.009 * AR, facecolor=leg_palette[l_i % len(leg_palette)])
            ax.add_patch(dot)
            ax.text(
                leg_x + 0.014, ly, l_cat[:18],
                fontproperties=get_sans_prop(7),
                color=MODERN_TEXT_SUB, va="center", zorder=4
            )
            ax.text(
                mx + half_w - 0.025, ly, f"{l_cnt} (33%)",
                fontproperties=get_sans_prop(7, weight="bold"),
                color=MODERN_TEXT_MAIN, ha="right", va="center", zorder=4
            )

        # --- RIGHT CARD: KEY CONCEPTS TODAY (8 Modern Concept Tiles) ---
        right_x = mx + half_w + 0.025
        right_box = FancyBboxPatch(
            (right_x, analytics_y - 0.230), half_w, 0.230,
            boxstyle="round,pad=0.003,rounding_size=0.010",
            facecolor=MODERN_CARD_BG, edgecolor=MODERN_BORDER, linewidth=1.2, zorder=2
        )
        ax.add_patch(right_box)

        ax.text(
            right_x + 0.022, analytics_y - 0.022, "KEY CONCEPTS TODAY",
            fontproperties=get_sans_prop(9, weight="bold"),
            color=MODERN_TEXT_MAIN, zorder=3
        )

        # 8 Concept Tiles Grid
        draw_modern_concept_grid(
            ax, x=right_x + 0.018, y=analytics_y - 0.055,
            width=half_w - 0.036, concepts_list=concepts_list
        )

        # -------------------------------------------------------------
        # 4. BOTTOM METRIC BAR & FOOTER
        # -------------------------------------------------------------
        bot_bar_y = analytics_y - 0.230 - 0.022
        bot_box = FancyBboxPatch(
            (mx, bot_bar_y - 0.065), card_w, 0.065,
            boxstyle="round,pad=0.003,rounding_size=0.010",
            facecolor=MODERN_CARD_BG, edgecolor=MODERN_BORDER, linewidth=1.2, zorder=2
        )
        ax.add_patch(bot_box)

        # Left: Tagline
        ax.text(
            mx + 0.030, bot_bar_y - 0.025, "Small steps\nin research,\nbig leaps in\ninnovation.",
            fontproperties=get_serif_prop(7.5, style="italic"),
            color=MODERN_TEXT_SUB, va="center", linespacing=1.2, zorder=3
        )

        # 4 Metric Counters
        metrics = [
            ("3", "Papers Analyzed"),
            ("1", "Day Running"),
            ("3", "Categories"),
            ("12", "Total Concepts"),
        ]
        m_start_x = mx + 0.220
        m_spacing = 0.120

        for m_i, (m_val, m_lbl) in enumerate(metrics):
            m_x = m_start_x + (m_i * m_spacing)
            # Value
            ax.text(
                m_x, bot_bar_y - 0.025, m_val,
                fontproperties=get_sans_prop(14, weight="bold"),
                color=MODERN_TEXT_MAIN, ha="center", va="center", zorder=3
            )
            # Label
            ax.text(
                m_x, bot_bar_y - 0.046, m_lbl,
                fontproperties=get_sans_prop(6.5),
                color=MODERN_TEXT_MUTED, ha="center", va="center", zorder=3
            )

        # Right: Calendar callout
        ax.text(
            1.0 - mx - 0.040, bot_bar_y - 0.032, "Next update\ntomorrow",
            fontproperties=get_serif_prop(8, style="italic"),
            color=MODERN_TEXT_MUTED, ha="center", va="center", linespacing=1.2, zorder=3
        )

        # Bottom-most footer line
        ft_y = 0.020
        ax.text(
            mx, ft_y, "Generated automatically via GitHub Actions",
            fontproperties=get_sans_prop(6.5),
            color=MODERN_TEXT_MUTED, va="center"
        )
        ax.text(
            1.0 - mx, ft_y, "Daily Tech Intelligence  •  arXiv / Research / Innovation",
            fontproperties=get_sans_prop(6.5),
            color=MODERN_TEXT_MUTED, ha="right", va="center"
        )

        plt.savefig(
            output_path,
            dpi=250,
            facecolor=MODERN_BG,
            edgecolor="none",
            bbox_inches="tight",
            pad_inches=0.0
        )
        plt.close(fig)
        logger.info(f"Successfully rendered Template 2 (Modern) to {output_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to render Template 2 (Modern): {e}", exc_info=True)
        return False
