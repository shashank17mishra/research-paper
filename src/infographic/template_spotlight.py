"""
Template 3: Gen-Z Editorial Spotlight Broadside
================================================
A high-impact contemporary editorial broadside inspired by modern independent
journals (Il Mestiere, BloomAfterChaos) and featuring the user's yellow-square
vignette character illustrations and stylized walking figure, alongside data
graphs and score benchmark charts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

from src.infographic.assets import place_raster_image
from src.infographic.charts import (
    draw_category_distribution,
    draw_concept_tiles,
    draw_editorial_insight_card,
    draw_score_comparison_chart,
)
from src.infographic.palette import (
    INK_MUTED,
    INK_PRIMARY,
    INK_SECONDARY,
    PAPER_BORDER,
    SPOT_BG,
    SPOT_BORDER,
    SPOT_INK,
    SPOT_INK_MUTED,
    SPOT_TERRACOTTA,
    SPOT_YELLOW,
    get_category_color,
)
from src.infographic.typography import (
    get_sans_prop,
    get_serif_prop,
    synthesize_plain_explanation,
    synthesize_why_it_matters,
    wrap_text_lines,
)
from src.utils import setup_logger

logger = setup_logger("template_spotlight")


def render_template_spotlight(data: Dict[str, Any], output_path: Path) -> bool:
    """Renders Template 3: Gen-Z Editorial Spotlight Broadside."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        papers: List[Any] = data.get("papers", [])
        raw_date: str = data.get("date", "08 October 2026")
        categories_dict: Dict[str, int] = data.get("categories", {})
        concepts_list: List[str] = data.get("concepts", [])
        insight_tuple = data.get(
            "daily_insight",
            (
                "AI research is moving towards smaller, more efficient models that can operate directly on robots and edge devices.",
                "DECENTRALIZED RESILIENCE & EDGE DEPLOYMENT."
            )
        )
        if isinstance(insight_tuple, tuple):
            insight_text, insight_kicker = insight_tuple
        else:
            insight_text = str(insight_tuple)
            insight_kicker = "DECENTRALIZED RESILIENCE."

        fig = plt.figure(figsize=(10.0, 14.14), dpi=250)
        fig.patch.set_facecolor(SPOT_BG)

        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor(SPOT_BG)
        ax.axis("off")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        mx = 0.045

        # -------------------------------------------------------------
        # 1. NEWSPAPER BROADSIDE MASTHEAD
        # -------------------------------------------------------------
        # Top Header Box
        top_y = 0.965
        ax.plot([mx, 1.0 - mx], [top_y, top_y], color=SPOT_INK, linewidth=1.5)

        # Issue / Tagline
        ax.text(
            mx, top_y - 0.015, "SPECIAL EDITION  •  ISSUE #24",
            fontproperties=get_sans_prop(7.5, weight="bold"),
            color=SPOT_INK
        )
        ax.text(
            1.0 - mx, top_y - 0.015, f"{raw_date.upper()}  •  DISPATCH",
            fontproperties=get_sans_prop(7.5, weight="bold"),
            color=SPOT_INK, ha="right"
        )

        ax.plot([mx, 1.0 - mx], [top_y - 0.024, top_y - 0.024], color=SPOT_INK, linewidth=1.0)

        # Giant High-Impact Masthead: "DAILY TECH INTELLIGENCE"
        ax.text(
            mx, top_y - 0.075, "DAILY TECH INTELLIGENCE",
            fontproperties=get_sans_prop(36, weight="bold"),
            color=SPOT_INK
        )
        ax.text(
            mx, top_y - 0.098, "A CURATED JOURNAL OF RESEARCH DISCOVERIES IN AI, ROBOTICS, AND DISTRIBUTED SYSTEMS",
            fontproperties=get_sans_prop(7.5, weight="bold"),
            color=SPOT_INK_MUTED
        )

        # Bottom Double Rule of Header
        mast_b = top_y - 0.115
        ax.plot([mx, 1.0 - mx], [mast_b, mast_b], color=SPOT_INK, linewidth=2.0)
        ax.plot([mx, 1.0 - mx], [mast_b - 0.005, mast_b - 0.005], color=SPOT_INK, linewidth=0.8)

        # Stylized Gen-Z Walking Figure stepping right on the masthead ledge
        place_raster_image(
            ax, "walking_figure.png",
            x=0.760, y=mast_b, width=0.140,
            ha="left", va="bottom", zorder=10
        )

        # -------------------------------------------------------------
        # 2. RESEARCH SPOTLIGHT ROWS (Paired with Yellow-Box Vignettes)
        # -------------------------------------------------------------
        row_start_y = mast_b - 0.035
        row_h = 0.165
        row_gap = 0.018

        top_three = papers[:3]
        vignette_assets = [
            ("vignette_01_search.png", "Perception & Locomotion", "ROBOTICS"),
            ("vignette_03_code.png", "Embedded Model Quantization", "EDGE AI"),
            ("vignette_05_read.png", "Multi-Agent Coordination", "SYSTEMS"),
        ]

        for idx, p in enumerate(top_three):
            ry = row_start_y - (idx * (row_h + row_gap))
            title = getattr(p, "title", "Research Item")
            authors_list = getattr(p, "authors", [])
            authors_str = ", ".join(authors_list[:2]) + (" et al." if len(authors_list) > 2 else "")
            abstract = getattr(p, "abstract", "")
            primary_topic = getattr(p, "primary_topic", "AI")
            score = float(getattr(p, "relevance_score", 0.90))
            insights = getattr(p, "insights", {})
            v_asset, v_sub, v_cat = vignette_assets[idx % len(vignette_assets)]

            # Background Box
            row_box = FancyBboxPatch(
                (mx, ry - row_h), 1.0 - 2 * mx, row_h,
                boxstyle="square,pad=0.0",
                facecolor="#FFFFFF", edgecolor=SPOT_BORDER, linewidth=1.0, zorder=2
            )
            ax.add_patch(row_box)

            # Left Yellow Accent Strip
            left_strip = Rectangle(
                (mx, ry - row_h), 0.008, row_h,
                facecolor=SPOT_YELLOW, edgecolor="none", zorder=3
            )
            ax.add_patch(left_strip)

            # Left Column: Yellow-Box Vignette Illustration
            place_raster_image(
                ax, v_asset,
                x=mx + 0.020, y=ry - row_h + 0.015, width=0.150,
                ha="left", va="bottom", zorder=10
            )

            # Center Column: Details, Title, Plain-Language Explanation
            c_x = mx + 0.190
            # Rank Number & Category Tag
            ax.text(
                c_x, ry - 0.022, f"FEATURE {idx+1:02d}  •  {v_cat}",
                fontproperties=get_sans_prop(8, weight="bold"),
                color=SPOT_TERRACOTTA, zorder=4
            )

            # Paper Title
            wrapped_title = wrap_text_lines(title, max_chars=40, max_lines=2)
            ax.text(
                c_x, ry - 0.040, wrapped_title,
                fontproperties=get_serif_prop(11, weight="bold"),
                color=SPOT_INK, va="top", zorder=4
            )

            t_lines = len(wrapped_title.split("\n"))
            auth_y = ry - 0.040 - (t_lines * 0.019) - 0.004
            ax.text(
                c_x, auth_y, authors_str,
                fontproperties=get_sans_prop(7),
                color=SPOT_INK_MUTED, va="top", zorder=4
            )

            # Plain explanation
            plain_text = synthesize_plain_explanation(title, abstract, primary_topic)
            wrapped_plain = wrap_text_lines(plain_text, max_chars=46, max_lines=3)
            ax.text(
                c_x, auth_y - 0.020, wrapped_plain,
                fontproperties=get_sans_prop(7.5),
                color=INK_SECONDARY, va="top", linespacing=1.35, zorder=4
            )

            # Right Column: Score Gauge & Why It Matters Box
            r_col_x = 0.720
            # Score Gauge Pill
            score_box = FancyBboxPatch(
                (r_col_x, ry - 0.055), 0.180, 0.038,
                boxstyle="round,pad=0.002,rounding_size=0.006",
                facecolor="#F4EFE6", edgecolor=SPOT_BORDER, linewidth=1.0, zorder=3
            )
            ax.add_patch(score_box)

            ax.text(
                r_col_x + 0.018, ry - 0.036, "RELEVANCE SCORE",
                fontproperties=get_sans_prop(6.5, weight="bold"),
                color=SPOT_INK_MUTED, va="center", zorder=4
            )
            ax.text(
                r_col_x + 0.160, ry - 0.036, f"{score:.2f}",
                fontproperties=get_serif_prop(14, weight="bold"),
                color=SPOT_INK, ha="right", va="center", zorder=4
            )

            # "Why it matters" callout
            why_text = synthesize_why_it_matters(insights, primary_topic)
            why_wrap = wrap_text_lines(f"Why it matters: {why_text}", max_chars=28, max_lines=3)
            ax.text(
                r_col_x, ry - 0.075, why_wrap,
                fontproperties=get_serif_prop(8, style="italic"),
                color=INK_SECONDARY, va="top", linespacing=1.25, zorder=4
            )

        # -------------------------------------------------------------
        # 3. DATA GRAPHS & COMPARATIVE BENCHMARK SECTION
        # -------------------------------------------------------------
        bottom_y = row_start_y - (3 * (row_h + row_gap)) - 0.020
        col_w = (1.0 - 2 * mx - 0.030) / 2.0

        # Left Graph Box: SCORE BENCHMARKS & CATEGORY DISTRIBUTION
        g1_box = FancyBboxPatch(
            (mx, bottom_y - 0.180), col_w, 0.180,
            boxstyle="round,pad=0.002,rounding_size=0.008",
            facecolor="#FFFFFF", edgecolor=SPOT_BORDER, linewidth=1.0, zorder=2
        )
        ax.add_patch(g1_box)

        ax.text(
            mx + 0.020, bottom_y - 0.022, "RESEARCH SCORE COMPARISON",
            fontproperties=get_sans_prop(8.5, weight="bold"),
            color=SPOT_INK, zorder=3
        )
        ax.text(
            mx + 0.020, bottom_y - 0.038, "Comparative algorithmic relevance benchmarks",
            fontproperties=get_serif_prop(7.5, style="italic"),
            color=SPOT_INK_MUTED, zorder=3
        )

        # Draw Score Comparison Chart
        draw_score_comparison_chart(
            ax, x=mx + 0.020, y=bottom_y - 0.065, width=col_w - 0.040,
            papers=papers
        )

        # Right Graph Box: TODAY'S INSIGHT & KEY CONCEPTS MATRIX
        g2_x = mx + col_w + 0.030
        g2_box = FancyBboxPatch(
            (g2_x, bottom_y - 0.180), col_w, 0.180,
            boxstyle="round,pad=0.002,rounding_size=0.008",
            facecolor="#FFFFFF", edgecolor=SPOT_BORDER, linewidth=1.0, zorder=2
        )
        ax.add_patch(g2_box)

        ax.text(
            g2_x + 0.020, bottom_y - 0.022, "TODAY'S CROSS-FIELD INSIGHT",
            fontproperties=get_sans_prop(8.5, weight="bold"),
            color=SPOT_INK, zorder=3
        )

        wrapped_insight = wrap_text_lines(f'"{insight_text}"', max_chars=36, max_lines=4)
        ax.text(
            g2_x + 0.020, bottom_y - 0.050, wrapped_insight,
            fontproperties=get_serif_prop(9.5, style="italic"),
            color=SPOT_INK, va="top", linespacing=1.35, zorder=3
        )

        # Concepts Separator Line & Header
        sep_y = bottom_y - 0.108
        ax.plot([g2_x + 0.020, g2_x + col_w - 0.020], [sep_y, sep_y], color=SPOT_BORDER, linewidth=0.8)
        
        ax.text(
            g2_x + 0.020, sep_y - 0.014, "ACTIVE CONCEPTS",
            fontproperties=get_sans_prop(7, weight="bold"),
            color=SPOT_TERRACOTTA, zorder=3
        )

        # Dynamic concept chips wrapped cleanly within the card width
        cur_x = g2_x + 0.020
        chip_y = sep_y - 0.034
        chip_h = 0.016
        max_box_x = g2_x + col_w - 0.020

        top_concepts = [c.strip() for c in concepts_list if c.strip()][:6]
        for c_text in top_concepts:
            c_w = min(0.018 + len(c_text) * 0.0055, 0.160)
            if cur_x + c_w > max_box_x:
                cur_x = g2_x + 0.020
                chip_y -= 0.022
                if chip_y - chip_h < bottom_y - 0.178:
                    break

            c_box = FancyBboxPatch(
                (cur_x, chip_y - chip_h), c_w, chip_h,
                boxstyle="round,pad=0.001,rounding_size=0.004",
                facecolor="#FEF3C7", edgecolor="#FCD34D", linewidth=0.8, zorder=3
            )
            ax.add_patch(c_box)
            ax.text(
                cur_x + c_w / 2.0, chip_y - chip_h / 2.0, c_text,
                fontproperties=get_sans_prop(6.5, weight="bold"),
                color=SPOT_INK, ha="center", va="center", zorder=4
            )
            cur_x += c_w + 0.008

        # -------------------------------------------------------------
        # 4. FOOTER
        # -------------------------------------------------------------
        ft_y = 0.030
        ax.plot([mx, 1.0 - mx], [ft_y + 0.015, ft_y + 0.015], color=SPOT_INK, linewidth=1.2)
        ax.text(
            mx, ft_y, "DAILY TECH INTELLIGENCE  •  AUTONOMOUS RESEARCH PLATFORM",
            fontproperties=get_sans_prop(7, weight="bold"),
            color=SPOT_INK, va="center"
        )
        ax.text(
            1.0 - mx, ft_y, "POWERED BY GITHUB ACTIONS & ARXIV OPEN RESEARCH",
            fontproperties=get_sans_prop(7, weight="bold"),
            color=SPOT_INK, ha="right", va="center"
        )

        plt.savefig(
            output_path,
            dpi=250,
            facecolor=SPOT_BG,
            edgecolor="none",
            bbox_inches="tight",
            pad_inches=0.0
        )
        plt.close(fig)
        logger.info(f"Successfully rendered Template 3 (Spotlight) to {output_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to render Template 3 (Spotlight): {e}", exc_info=True)
        return False
