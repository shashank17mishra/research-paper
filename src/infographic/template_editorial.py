"""
Template 1: Editorial Research Journal / Classic Broadsheet
============================================================
A sophisticated print publication layout inspired by independent magazines
and minimalist research journals. Uses authentic illustration assets,
high-contrast typography, and horizontal category distribution charts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from src.infographic.assets import place_raster_image
from src.infographic.charts import (
    draw_category_distribution,
    draw_concept_tiles,
    draw_editorial_insight_card,
)
from src.infographic.layout import compute_editorial_layout
from src.infographic.palette import (
    ACCENT_TERRACOTTA,
    INK_MUTED,
    INK_PRIMARY,
    INK_SECONDARY,
    PAPER_BG,
    PAPER_BORDER,
    PAPER_BORDER_DARK,
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

logger = setup_logger("template_editorial")

CATEGORY_DISPLAY_MAP: Dict[str, str] = {
    "cs.ro": "ROBOTICS",
    "cs.ai": "AI",
    "cs.lg": "MACHINE LEARNING",
    "cs.cv": "COMPUTER VISION",
    "cs.dc": "EDGE & IOT",
    "cs.ne": "NEURAL SYSTEMS",
    "cs.cl": "NLP / AI",
    "robotics": "ROBOTICS",
    "artificial intelligence": "AI",
    "machine learning": "MACHINE LEARNING",
    "iot": "IOT & EDGE",
    "iot & edge computing": "IOT & EDGE",
    "edge computing": "EDGE & IOT",
    "distributed computing": "DISTRIBUTED",
}


def render_template_editorial(data: Dict[str, Any], output_path: Path) -> bool:
    """Renders Template 1: Classic Editorial Research Journal."""
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
                "SMALLER MODELS. BIGGER IMPACT."
            )
        )
        if isinstance(insight_tuple, tuple):
            insight_text, insight_kicker = insight_tuple
        else:
            insight_text = str(insight_tuple)
            insight_kicker = "SMALLER MODELS. BIGGER IMPACT."

        parts = raw_date.replace(",", "").split()
        if len(parts) >= 3:
            display_date_short = f"{parts[0]} {parts[1][:3].upper()} {parts[2]}"
        else:
            display_date_short = raw_date.upper()

        layout = compute_editorial_layout()

        fig = plt.figure(figsize=(10.0, 14.14), dpi=250)
        fig.patch.set_facecolor(PAPER_BG)

        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor(PAPER_BG)
        ax.axis("off")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        # -------------------------------------------------------------
        # 1. HEADER SECTION
        # -------------------------------------------------------------
        mx = layout.margin_x

        # Top Kicker line
        ax.text(
            mx, 0.965, "AUTONOMOUS RESEARCH INTELLIGENCE",
            fontproperties=get_sans_prop(7.5, weight="bold"),
            color=INK_MUTED
        )
        ax.text(
            1.0 - mx, 0.965, "Better Research. A Smarter Tomorrow.",
            fontproperties=get_serif_prop(8.5, style="italic"),
            color=INK_SECONDARY, ha="right"
        )

        # Main Masthead
        ax.text(
            mx, 0.905, "Daily Tech",
            fontproperties=get_serif_prop(38, weight="bold"),
            color=INK_PRIMARY
        )
        ax.text(
            mx, 0.850, "Intelligence",
            fontproperties=get_serif_prop(38, style="italic"),
            color=ACCENT_TERRACOTTA
        )

        # Thin Vertical Divider
        divider_x = 0.505
        ax.plot([divider_x, divider_x], [0.840, 0.935], color=PAPER_BORDER, linewidth=1.0)

        # Metadata Block
        meta_x = divider_x + 0.025
        ax.text(
            meta_x, 0.930, display_date_short,
            fontproperties=get_sans_prop(9.5, weight="bold"),
            color=INK_PRIMARY
        )
        ax.text(
            meta_x, 0.910, "AI   /   ML   /   ROBOTICS   /   IoT",
            fontproperties=get_sans_prop(7.5, weight="bold"),
            color=INK_MUTED
        )

        # Papers Analyzed
        paper_count = len(papers)
        ax.text(
            meta_x, 0.872, f"{paper_count}",
            fontproperties=get_serif_prop(22, weight="bold"),
            color=INK_PRIMARY, va="center"
        )
        ax.text(
            meta_x + 0.040, 0.872, "PAPERS ANALYZED",
            fontproperties=get_sans_prop(8, weight="bold"),
            color=INK_MUTED, va="center"
        )

        # Tagline
        ax.text(
            meta_x, 0.842, "Real research. Summarized. For curious minds.",
            fontproperties=get_serif_prop(8.5, style="italic"),
            color=INK_SECONDARY
        )

        # Header Book Stack Illustration (Loaded directly from user assets)
        place_raster_image(
            ax, "ed_book_stack.png",
            x=0.790, y=0.835, width=0.155,
            ha="left", va="bottom", zorder=10
        )

        # -------------------------------------------------------------
        # 2. FEATURED RESEARCH HEADER (Double Rules)
        # -------------------------------------------------------------
        f_y = layout.featured_header_y
        ax.plot([mx, 1.0 - mx], [f_y + 0.012, f_y + 0.012], color=PAPER_BORDER_DARK, linewidth=1.8)
        ax.plot([mx, 1.0 - mx], [f_y - 0.010, f_y - 0.010], color=PAPER_BORDER, linewidth=0.8)

        ax.text(
            mx, f_y + 0.001, "FEATURED RESEARCH",
            fontproperties=get_sans_prop(9.5, weight="bold"),
            color=INK_PRIMARY, va="center"
        )
        ax.text(
            1.0 - mx, f_y + 0.001, "Today's top 3 papers, simplified.",
            fontproperties=get_serif_prop(8.5, style="italic"),
            color=INK_SECONDARY, ha="right", va="center"
        )

        # -------------------------------------------------------------
        # 3. FEATURED RESEARCH ROWS (01, 02, 03)
        # -------------------------------------------------------------
        top_three = papers[:3]
        row_layouts = [layout.row_1, layout.row_2, layout.row_3]
        editorial_assets = ["ed_quadruped.png", "ed_chip.png", "ed_warehouse.png"]

        for idx, (p, r_lay) in enumerate(zip(top_three, row_layouts)):
            title = getattr(p, "title", "Untitled Research")
            authors_list = getattr(p, "authors", [])
            authors_str = ", ".join(authors_list[:2]) + (" et al." if len(authors_list) > 2 else "")
            abstract = getattr(p, "abstract", "")
            categories = getattr(p, "categories", [])
            primary_topic = getattr(p, "primary_topic", "AI")
            score = float(getattr(p, "relevance_score", 0.90))
            insights = getattr(p, "insights", {})
            p_concepts = getattr(p, "key_concepts", [])

            cat_label = categories[0] if categories else primary_topic
            cat_style = get_category_color(cat_label, default_idx=idx)

            y_top = r_lay.y_top
            y_bot = r_lay.y_bottom

            # --- COLUMN 1: Large Rank Number, Score & Badge ---
            c_rank_x = r_lay.col_rank[0]
            ax.text(
                c_rank_x, y_top - 0.045, f"{idx+1:02d}",
                fontproperties=get_serif_prop(32, weight="bold"),
                color=INK_PRIMARY
            )
            ax.text(
                c_rank_x, y_top - 0.075, "SCORE",
                fontproperties=get_sans_prop(7, weight="bold"),
                color=INK_MUTED
            )
            ax.text(
                c_rank_x, y_top - 0.098, f"{score:.2f}",
                fontproperties=get_serif_prop(12, weight="bold"),
                color=INK_PRIMARY
            )

            # Category Pill Badge
            clean_cat_badge = CATEGORY_DISPLAY_MAP.get(
                cat_label.lower(),
                CATEGORY_DISPLAY_MAP.get(primary_topic.lower(), cat_label.replace("cs.", "").upper())
            )
            pill_w = max(0.062, min(0.125, len(clean_cat_badge) * 0.0068 + 0.024))
            pill_h = 0.018
            pill_y = y_top - 0.128
            pill = FancyBboxPatch(
                (c_rank_x, pill_y), pill_w, pill_h,
                boxstyle="round,pad=0.002,rounding_size=0.005",
                facecolor=cat_style["accent"],
                edgecolor="none"
            )
            ax.add_patch(pill)

            ax.text(
                c_rank_x + pill_w / 2, pill_y + pill_h / 2,
                clean_cat_badge,
                fontproperties=get_sans_prop(6.5, weight="bold"),
                color="#FFFFFF", ha="center", va="center"
            )

            # --- COLUMN 2: Title, Authors, Plain Language Explanation ---
            c_cont_x = r_lay.col_content[0]
            wrapped_title = wrap_text_lines(title, max_chars=36, max_lines=3)
            ax.text(
                c_cont_x, y_top - 0.012, wrapped_title,
                fontproperties=get_serif_prop(10.5, weight="bold"),
                color=INK_PRIMARY, va="top", linespacing=1.2
            )

            num_title_lines = len(wrapped_title.split("\n"))
            auth_y = y_top - 0.012 - (num_title_lines * 0.019) - 0.005

            ax.text(
                c_cont_x, auth_y, authors_str,
                fontproperties=get_sans_prop(7),
                color=INK_MUTED, va="top"
            )

            plain_text = synthesize_plain_explanation(title, abstract, primary_topic)
            ax.text(
                c_cont_x, auth_y - 0.022, plain_text,
                fontproperties=get_sans_prop(7.5),
                color=INK_SECONDARY, va="top", linespacing=1.35
            )

            # --- COLUMN 3: Real Illustration Asset ---
            c_illus_x = (r_lay.col_illus[0] + r_lay.col_illus[1]) / 2.0
            c_illus_y = (y_top + y_bot) / 2.0
            asset_name = editorial_assets[idx % len(editorial_assets)]
            place_raster_image(
                ax, asset_name,
                x=c_illus_x, y=c_illus_y, width=0.175,
                ha="center", va="center", zorder=10
            )

            # --- COLUMN 4: Key Concepts & "Why It Matters" ---
            c_conc_x = r_lay.col_concepts[0]
            ax.text(
                c_conc_x, y_top - 0.012, "KEY CONCEPTS",
                fontproperties=get_sans_prop(7, weight="bold"),
                color=INK_PRIMARY, va="top"
            )

            display_kcs = p_concepts[:5] if p_concepts else ["Deep Learning", "Autonomous Systems", "Real-World Evaluation"]
            for kc_i, kc in enumerate(display_kcs):
                kc_y = y_top - 0.032 - (kc_i * 0.016)
                clean_kc = kc.replace("_", " ").title()
                ax.text(
                    c_conc_x, kc_y, clean_kc,
                    fontproperties=get_sans_prop(7),
                    color=INK_SECONDARY, va="top"
                )

            # "Why It Matters"
            why_statement = synthesize_why_it_matters(insights, primary_topic)
            why_wrapped = wrap_text_lines(why_statement, max_chars=22, max_lines=3)
            ax.text(
                c_conc_x, y_bot + 0.038, why_wrapped,
                fontproperties=get_serif_prop(8, style="italic"),
                color=INK_SECONDARY, va="bottom", linespacing=1.25
            )

            # Thin horizontal divider between rows
            if idx < 2:
                ax.plot([mx, 1.0 - mx], [y_bot, y_bot], color=PAPER_BORDER, linewidth=0.8)

        # Bottom Double Rule above overview
        ov_y = layout.bottom_y_top
        ax.plot([mx, 1.0 - mx], [ov_y + 0.025, ov_y + 0.025], color=PAPER_BORDER, linewidth=0.8)

        # -------------------------------------------------------------
        # 4. BOTTOM EDITORIAL OVERVIEW
        # -------------------------------------------------------------
        col_w = (1.0 - 2 * mx) / 3.0

        # Column A: Category Distribution
        c_a_x = mx
        ax.text(
            c_a_x, ov_y, "TODAY'S RESEARCH AREAS",
            fontproperties=get_sans_prop(8.5, weight="bold"),
            color=INK_PRIMARY
        )
        ax.text(
            c_a_x, ov_y - 0.016, "Papers by category",
            fontproperties=get_serif_prop(8, style="italic"),
            color=INK_MUTED
        )
        draw_category_distribution(ax, c_a_x, ov_y - 0.042, categories_dict, total_papers=len(papers))

        # Vertical hairline between Col A and Col B
        sep_1_x = mx + col_w - 0.025
        ax.plot([sep_1_x, sep_1_x], [ov_y + 0.005, ov_y - 0.160], color=PAPER_BORDER, linewidth=0.8)

        # Column B: Key Concepts Matrix
        c_b_x = sep_1_x + 0.025
        ax.text(
            c_b_x, ov_y, "KEY CONCEPTS TODAY",
            fontproperties=get_sans_prop(8.5, weight="bold"),
            color=INK_PRIMARY
        )
        ax.text(
            c_b_x, ov_y - 0.016, "The ideas showing up across today's research",
            fontproperties=get_serif_prop(8, style="italic"),
            color=INK_MUTED
        )
        draw_concept_tiles(ax, c_b_x, ov_y - 0.048, concepts_list)

        # Vertical hairline between Col B and Col C
        sep_2_x = c_b_x + col_w - 0.010
        ax.plot([sep_2_x, sep_2_x], [ov_y + 0.005, ov_y - 0.160], color=PAPER_BORDER, linewidth=0.8)

        # Column C: Today's Insight Card
        c_c_x = sep_2_x + 0.025
        draw_editorial_insight_card(ax, c_c_x, ov_y, insight_text, kicker=insight_kicker)

        # -------------------------------------------------------------
        # 5. FOOTER
        # -------------------------------------------------------------
        ft_y = layout.footer_y
        ax.plot([mx, 1.0 - mx], [ft_y + 0.020, ft_y + 0.020], color=PAPER_BORDER, linewidth=0.8)

        # Footer Compass Monogram
        ax.plot([mx, mx + 0.006], [ft_y, ft_y + 0.015], color=INK_PRIMARY, linewidth=1.2)
        ax.plot([mx + 0.006, mx + 0.012], [ft_y + 0.015, ft_y], color=INK_PRIMARY, linewidth=1.2)
        ax.plot([mx + 0.002, mx + 0.010], [ft_y + 0.005, ft_y + 0.005], color=INK_PRIMARY, linewidth=1.0)

        ax.text(
            mx + 0.020, ft_y + 0.005,
            "DAILY TECH INTELLIGENCE  •  RESEARCH  /  ANALYZE  /  BUILD",
            fontproperties=get_sans_prop(6.5, weight="bold"),
            color=INK_MUTED, va="center"
        )
        ax.text(
            0.58, ft_y + 0.005,
            "GENERATED AUTOMATICALLY VIA GITHUB ACTIONS",
            fontproperties=get_sans_prop(6, weight="bold"),
            color=INK_MUTED, ha="center", va="center"
        )
        ax.text(
            1.0 - mx, ft_y + 0.005,
            f"{display_date_short}  •  ISSUE #01",
            fontproperties=get_sans_prop(6.5, weight="bold"),
            color=INK_PRIMARY, ha="right", va="center"
        )

        plt.savefig(
            output_path,
            dpi=250,
            facecolor=PAPER_BG,
            edgecolor="none",
            bbox_inches="tight",
            pad_inches=0.0
        )
        plt.close(fig)
        logger.info(f"Successfully rendered Template 1 (Editorial) to {output_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to render Template 1 (Editorial): {e}", exc_info=True)
        return False
