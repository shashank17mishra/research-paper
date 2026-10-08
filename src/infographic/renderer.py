"""
Master Editorial Infographic Renderer
=====================================
Orchestrates layout geometry, typography, palette, illustrations, and charts
into a print-ready, high-resolution editorial research publication page.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import matplotlib
matplotlib.use("Agg")  # Headless rendering for GitHub Actions
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PIL import Image

from src.infographic.charts import (
    draw_category_distribution,
    draw_concept_tiles,
    draw_editorial_insight_card,
)
from src.infographic.illustrations import (
    draw_book_stack_header,
    draw_botanical_sprig,
    render_paper_illustration,
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

logger = setup_logger("infographic_renderer")

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


def derive_daily_insight(papers: List[Any]) -> tuple[str, str]:
    """
    Derives a genuine, meaningful cross-paper synthesis insight and punchy tagline
    from the daily research papers.
    """
    combined_text = " ".join([
        f"{getattr(p, 'title', '')} {getattr(p, 'abstract', '')} {' '.join(getattr(p, 'categories', []))}"
        for p in papers
    ]).lower()

    if any(k in combined_text for k in ["tinyml", "edge", "milliwatt", "quantiz", "embedded"]) and "robot" in combined_text:
        return (
            "AI research is moving towards smaller, more efficient models that can operate directly on robots and edge devices.",
            "SMALLER MODELS. BIGGER IMPACT."
        )
    elif "warehouse" in combined_text or "multi-agent" in combined_text or "coordination" in combined_text:
        return (
            "Autonomous systems are shifting from fragile central controllers to decentralized, self-organizing multi-agent fleets.",
            "DECENTRALIZED RESILIENCE."
        )
    elif "transformer" in combined_text and ("quadruped" in combined_text or "manipulat" in combined_text or "locomotion" in combined_text):
        return (
            "Vision transformers are breaking out of pure software benchmarks to solve physical real-time control in unpredictable terrain.",
            "EMBODIED PERCEPTION."
        )
    else:
        return (
            "Modern research is bridging the gap between theoretical foundation models and physical-world hardware constraints.",
            "THEORY MEETS EMBODIMENT."
        )


def render_editorial_infographic(data: Dict[str, Any], output_path: Path) -> bool:
    """
    Renders the complete editorial magazine research page from the data dictionary.
    Canvas: 10 x 14.14 inches at 250 DPI (~2500 x 3535 px, portrait A4 ratio).
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        papers: List[Any] = data.get("papers", [])
        raw_date: str = data.get("date", "08 October 2026")
        categories_dict: Dict[str, int] = data.get("categories", {})
        concepts_list: List[str] = data.get("concepts", [])

        # Format date as '08 OCT 2026'
        parts = raw_date.replace(",", "").split()
        if len(parts) >= 3:
            display_date_short = f"{parts[0]} {parts[1][:3].upper()} {parts[2]}"
        else:
            display_date_short = raw_date.upper()

        layout = compute_editorial_layout()

        # Canvas initialization (A4 ratio at 250 DPI = 2500 x 3535 px)
        fig = plt.figure(figsize=(10.0, 14.14), dpi=250)
        fig.patch.set_facecolor(PAPER_BG)

        # Single absolute master axis spanning [0, 1]
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
        # "Daily Tech" in heavy black serif, "Intelligence" in terracotta italic serif
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

        # Thin Vertical Divider between Masthead and Metadata
        divider_x = 0.505
        ax.plot([divider_x, divider_x], [0.840, 0.935], color=PAPER_BORDER, linewidth=1.0)

        # Center-Right Metadata Block
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

        # Papers Analyzed Metric
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

        # Header Book Stack Illustration on Far Right (Compact and perfectly framed)
        draw_book_stack_header(ax, x=0.795, y=0.840, scale=0.30)

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

            # Dynamic category color
            cat_label = categories[0] if categories else primary_topic
            cat_style = get_category_color(cat_label, default_idx=idx)

            y_top = r_lay.y_top
            y_bot = r_lay.y_bottom

            # --- COLUMN 1: Large Rank Number, Score & Badge ---
            c_rank_x = r_lay.col_rank[0]
            # Huge 01, 02, 03
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

            # Authors line
            ax.text(
                c_cont_x, auth_y, authors_str,
                fontproperties=get_sans_prop(7.8),
                color=INK_MUTED
            )

            # Hairline divider under authors
            divider_y = auth_y - 0.008
            ax.plot([c_cont_x, c_cont_x + 0.10], [divider_y, divider_y], color=PAPER_BORDER, linewidth=0.7)

            # Accessible Plain Language Explanation (What & How)
            plain_summary = synthesize_plain_explanation(title, abstract, primary_topic)
            ax.text(
                c_cont_x, divider_y - 0.010, plain_summary,
                fontproperties=get_sans_prop(7.8),
                color=INK_SECONDARY, va="top", linespacing=1.35
            )

            # --- COLUMN 3: Hand-Drawn Scientific Illustration ---
            c_illus_x = (r_lay.col_illus[0] + r_lay.col_illus[1]) / 2
            c_illus_y = (y_top + y_bot) / 2
            render_paper_illustration(
                paper_title=title,
                abstract=abstract,
                category=cat_label,
                ax=ax,
                cx=c_illus_x,
                cy=c_illus_y,
                scale=0.34,
                accent=cat_style["accent"]
            )

            # --- COLUMN 4: Key Concepts & Why It Matters ---
            c_conc_x = r_lay.col_concepts[0]
            ax.text(
                c_conc_x, y_top - 0.012, "KEY CONCEPTS",
                fontproperties=get_sans_prop(7.5, weight="bold"),
                color=INK_PRIMARY, va="top"
            )

            # Concepts bullets
            display_p_concepts = p_concepts[:5] if p_concepts else ["Autonomous Learning", "Neural Policy"]
            c_line_y = y_top - 0.034
            for c_item in display_p_concepts:
                ax.text(
                    c_conc_x, c_line_y, c_item,
                    fontproperties=get_sans_prop(7.6),
                    color=INK_SECONDARY, va="top"
                )
                c_line_y -= 0.016

            # Why It Matters section (italic serif)
            why_text = synthesize_why_it_matters(insights, primary_topic)
            wrapped_why = wrap_text_lines(why_text, max_chars=26, max_lines=3)
            ax.text(
                c_conc_x, y_bot + 0.020, wrapped_why,
                fontproperties=get_serif_prop(8.2, style="italic"),
                color=INK_PRIMARY, va="bottom", linespacing=1.25
            )

            # Hairline divider below row
            ax.plot([mx, 1.0 - mx], [y_bot + 0.005, y_bot + 0.005], color=PAPER_BORDER, linewidth=0.8)

        # -------------------------------------------------------------
        # 4. BOTTOM OVERVIEW SECTION (3 Columns)
        # -------------------------------------------------------------
        by_b = layout.bottom_y_bottom
        by_t = layout.bottom_y_top
        bh = by_t - by_b

        # Column 1: Today's Research Areas (Minimal Bars)
        c1_x, c1_r = layout.col_areas
        draw_category_distribution(ax, c1_x, by_b, c1_r - c1_x, bh, categories_dict)

        # Subtle vertical divider
        v1_x = (c1_r + layout.col_concepts_grid[0]) / 2
        ax.plot([v1_x, v1_x], [by_b, by_t], color=PAPER_BORDER, linewidth=0.8)

        # Column 2: Key Concepts Today (6 Flat Tiles)
        c2_x, c2_r = layout.col_concepts_grid
        draw_concept_tiles(ax, c2_x, by_b, c2_r - c2_x, bh, concepts_list)

        # Subtle vertical divider
        v2_x = (c2_r + layout.col_insight[0]) / 2
        ax.plot([v2_x, v2_x], [by_b, by_t], color=PAPER_BORDER, linewidth=0.8)

        # Column 3: Today's Insight (Quote Card)
        c3_x, c3_r = layout.col_insight
        custom_insight = data.get("daily_insight")
        if custom_insight:
            insight_text = custom_insight
            tagline = "DAILY RESEARCH SYNTHESIS"
        else:
            insight_text, tagline = derive_daily_insight(papers)

        draw_editorial_insight_card(ax, c3_x, by_b, c3_r - c3_x, bh, insight_text, tagline)

        # -------------------------------------------------------------
        # 5. FOOTER SECTION
        # -------------------------------------------------------------
        foot_y = layout.footer_y
        ax.plot([mx, 1.0 - mx], [foot_y + 0.016, foot_y + 0.016], color=PAPER_BORDER, linewidth=0.8)

        draw_botanical_sprig(ax, mx + 0.008, foot_y + 0.006, scale=0.07, angle=35)

        ax.text(
            mx + 0.035, foot_y + 0.007,
            "DAILY TECH INTELLIGENCE   •   RESEARCH  /  ANALYZE  /  BUILD",
            fontproperties=get_sans_prop(7, weight="bold"),
            color=INK_MUTED, va="center"
        )

        ax.text(
            0.58, foot_y + 0.007,
            "GENERATED AUTOMATICALLY VIA GITHUB ACTIONS",
            fontproperties=get_sans_prop(6.5),
            color=INK_MUTED, ha="center", va="center"
        )

        ax.text(
            1.0 - mx, foot_y + 0.007,
            f"{display_date_short}   •   ISSUE #01",
            fontproperties=get_sans_prop(7, weight="bold"),
            color=INK_PRIMARY, ha="right", va="center"
        )

        # Save high-resolution PNG
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        fig.savefig(
            output_path,
            dpi=250,
            facecolor=PAPER_BG,
            edgecolor="none",
            bbox_inches="tight",
            pad_inches=0
        )
        plt.close(fig)

        # Optimize image with Pillow
        try:
            with Image.open(output_path) as im:
                im.save(output_path, "PNG", optimize=True)
        except Exception as opt_err:
            logger.debug(f"Pillow optimization notice: {opt_err}")

        logger.info(f"Successfully rendered editorial infographic to {output_path}")
        return True

    except Exception as exc:
        logger.error(f"Error rendering editorial infographic: {exc}", exc_info=True)
        plt.close("all")
        return False


def generate_daily_infographic(
    papers: List[Any],
    display_date: str,
    output_path: Path
) -> bool:
    """
    Adapter function providing backward compatibility with src/main.py,
    src/archive.py, and scripts/seed_demo_data.py.
    """
    if not papers:
        logger.warning("No papers provided for infographic rendering.")
        return False

    category_counts: Dict[str, int] = {}
    all_concepts: List[str] = []

    for p in papers:
        for c in getattr(p, "categories", [])[:1]:
            category_counts[c] = category_counts.get(c, 0) + 1
        for concept in getattr(p, "key_concepts", []):
            if concept not in all_concepts:
                all_concepts.append(concept)

    data = {
        "date": display_date,
        "papers": papers,
        "categories": category_counts,
        "concepts": all_concepts[:8],
        "statistics": {"total_papers": len(papers)}
    }

    return render_editorial_infographic(data, output_path)
