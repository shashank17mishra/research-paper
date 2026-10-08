"""
Daily Infographic Generator
===========================
Generates a minimal, modern, typography-first technical research infographic
using Matplotlib and Pillow at ₹0/month cost.
Tailored for GitHub, LinkedIn, X/Twitter, and Instagram.
"""

from __future__ import annotations

from pathlib import Path
from typing import List
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless CI
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from PIL import Image

from src.fetcher import Paper
from src.utils import setup_logger

logger = setup_logger("infographic")

# Clean, modern slate dark palette
PALETTE = {
    "bg": "#0B0F17",           # Deep space slate
    "card_bg": "#131C2E",      # Elevated dark card
    "card_border": "#1E293B",  # Subtle card stroke
    "accent_primary": "#38BDF8",  # Vibrant cyan
    "accent_indigo": "#818CF8",   # Modern indigo
    "accent_emerald": "#34D399",  # Soft emerald
    "text_primary": "#F8FAFC",    # Bright crisp white
    "text_secondary": "#94A3B8",  # Muted slate
    "text_accent": "#7DD3FC",     # Light cyan
    "bar_colors": ["#38BDF8", "#818CF8", "#34D399", "#F472B6", "#FBBF24", "#A78BFA"]
}


def wrap_text_lines(text: str, max_chars: int = 50, max_lines: int = 2) -> str:
    """Wraps text cleanly within maximum characters and limits lines."""
    words = text.split()
    lines = []
    current_line = []
    current_len = 0

    for w in words:
        if current_len + len(w) + 1 > max_chars:
            lines.append(" ".join(current_line))
            current_line = [w]
            current_len = len(w)
            if len(lines) == max_lines - 1:
                break
        else:
            current_line.append(w)
            current_len += len(w) + 1

    if current_line and len(lines) < max_lines:
        lines.append(" ".join(current_line))

    # Add ellipsis if truncated
    joined = "\n".join(lines)
    if len(" ".join(words)) > len(joined):
        if not joined.endswith("..."):
            joined = joined.rstrip(".") + "..."
    return joined


def generate_daily_infographic(
    papers: List[Paper],
    display_date: str,
    output_path: Path
) -> bool:
    """
    Renders and exports the daily summary infographic to output_path.
    Returns True on success, False on handled failure.
    """
    if not papers:
        logger.warning("No papers provided for infographic generation.")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Generating daily infographic for {display_date} -> {output_path}")

    try:
        # 1200 x 1200 square format (ideal for all platforms)
        fig = plt.figure(figsize=(10, 10), dpi=150)
        fig.patch.set_facecolor(PALETTE["bg"])

        # Grid specification:
        # [0, 0] Header
        # [1, 0] Top Papers & Insights
        # [2, 0] Category Breakdown & Key Concepts
        # [3, 0] Footer
        gs = fig.add_gridspec(
            nrows=4,
            ncols=1,
            height_ratios=[1.3, 4.4, 3.8, 0.5],
            hspace=0.18
        )

        # -------------------------------------------------------------
        # 1. HEADER SECTION
        # -------------------------------------------------------------
        ax_header = fig.add_subplot(gs[0])
        ax_header.set_facecolor(PALETTE["bg"])
        ax_header.axis("off")

        # Top Badge
        ax_header.text(
            0.04, 0.88, "A U T O N O M O U S   R E S E A R C H   I N T E L L I G E N C E",
            color=PALETTE["accent_primary"], fontsize=8, fontweight="bold"
        )

        # Main Title
        ax_header.text(
            0.04, 0.52, "Daily Tech Intelligence",
            color=PALETTE["text_primary"], fontsize=22, fontweight="bold"
        )

        # Date & Subtitle
        ax_header.text(
            0.04, 0.22, f"{display_date}   •   Top AI, ML, Robotics & IoT Research",
            color=PALETTE["text_secondary"], fontsize=10
        )

        # Metric Chips (Right aligned in Header)
        chip_box = FancyBboxPatch(
            (0.72, 0.20), 0.24, 0.65,
            boxstyle="round,pad=0.03,rounding_size=0.04",
            facecolor=PALETTE["card_bg"],
            edgecolor=PALETTE["card_border"],
            linewidth=1.2
        )
        ax_header.add_patch(chip_box)

        ax_header.text(
            0.84, 0.62, f"{len(papers)}",
            color=PALETTE["accent_primary"], fontsize=18, fontweight="bold",
            ha="center", va="center"
        )
        ax_header.text(
            0.84, 0.36, "PAPERS ANALYZED",
            color=PALETTE["text_secondary"], fontsize=7, fontweight="bold",
            ha="center", va="center"
        )

        # -------------------------------------------------------------
        # 2. TOP 3 PAPERS HIGHLIGHT SECTION
        # -------------------------------------------------------------
        ax_papers = fig.add_subplot(gs[1])
        ax_papers.set_facecolor(PALETTE["bg"])
        ax_papers.axis("off")

        ax_papers.text(
            0.04, 0.98, "FEATURED BREAKTHROUGHS",
            color=PALETTE["accent_indigo"], fontsize=9, fontweight="bold"
        )

        top_three = papers[:3]
        y_positions = [0.68, 0.36, 0.04]
        box_height = 0.28

        for idx, (p, y_pos) in enumerate(zip(top_three, y_positions)):
            # Card background
            card = FancyBboxPatch(
                (0.04, y_pos), 0.92, box_height,
                boxstyle="round,pad=0.02,rounding_size=0.03",
                facecolor=PALETTE["card_bg"],
                edgecolor=PALETTE["card_border"],
                linewidth=1.0
            )
            ax_papers.add_patch(card)

            # Rank indicator pill
            rank_bg = FancyBboxPatch(
                (0.06, y_pos + 0.16), 0.065, 0.08,
                boxstyle="round,pad=0.01,rounding_size=0.02",
                facecolor=PALETTE["accent_primary"] if idx == 0 else PALETTE["card_border"],
                edgecolor="none"
            )
            ax_papers.add_patch(rank_bg)

            rank_text_color = PALETTE["bg"] if idx == 0 else PALETTE["text_secondary"]
            ax_papers.text(
                0.092, y_pos + 0.20, f"#{idx+1:02d}",
                color=rank_text_color, fontsize=8, fontweight="bold",
                ha="center", va="center"
            )

            # Topic / Category Tag
            cat_tag = p.categories[0] if p.categories else p.primary_topic
            ax_papers.text(
                0.14, y_pos + 0.20, f"{cat_tag}   •   Score: {p.relevance_score:.2f}",
                color=PALETTE["accent_emerald"], fontsize=8, fontweight="bold"
            )

            # Paper Title
            wrapped_title = wrap_text_lines(p.title, max_chars=68, max_lines=2)
            ax_papers.text(
                0.06, y_pos + 0.09, wrapped_title,
                color=PALETTE["text_primary"], fontsize=9.5, fontweight="bold",
                va="center", linespacing=1.2
            )

            # Authors preview
            authors_str = ", ".join(p.authors[:2]) + (" et al." if len(p.authors) > 2 else "")
            ax_papers.text(
                0.06, y_pos + 0.02, authors_str,
                color=PALETTE["text_secondary"], fontsize=7.5
            )

        # -------------------------------------------------------------
        # 3. LOWER SECTION (Categories Distribution + Concept Chips)
        # -------------------------------------------------------------
        ax_bottom = fig.add_subplot(gs[2])
        ax_bottom.set_facecolor(PALETTE["bg"])
        ax_bottom.axis("off")

        # Left Column: Category Distribution Chart
        ax_bottom.text(
            0.04, 0.96, "TOP CATEGORIES",
            color=PALETTE["accent_primary"], fontsize=9, fontweight="bold"
        )

        cat_counts = {}
        for p in papers:
            for c in p.categories[:1]:
                cat_counts[c] = cat_counts.get(c, 0) + 1

        sorted_cats = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        max_cat_count = max([c[1] for c in sorted_cats], default=1)

        cat_start_y = 0.76
        for c_idx, (cat_name, count) in enumerate(sorted_cats):
            bar_y = cat_start_y - (c_idx * 0.16)
            bar_len = 0.32 * (count / max_cat_count)

            # Label
            ax_bottom.text(
                0.04, bar_y + 0.04, cat_name,
                color=PALETTE["text_primary"], fontsize=8, fontweight="bold"
            )
            # Bar background track
            track = Rectangle(
                (0.16, bar_y + 0.02), 0.30, 0.04,
                facecolor=PALETTE["card_border"]
            )
            ax_bottom.add_patch(track)

            # Value fill
            fill_bar = Rectangle(
                (0.16, bar_y + 0.02), bar_len, 0.04,
                facecolor=PALETTE["bar_colors"][c_idx % len(PALETTE["bar_colors"])]
            )
            ax_bottom.add_patch(fill_bar)

            # Count text
            ax_bottom.text(
                0.48, bar_y + 0.04, str(count),
                color=PALETTE["text_secondary"], fontsize=8
            )

        # Right Column: Prominent Key Concepts
        ax_bottom.text(
            0.56, 0.96, "KEY CONCEPTS TODAY",
            color=PALETTE["accent_indigo"], fontsize=9, fontweight="bold"
        )

        all_concepts = []
        for p in papers:
            for concept in p.key_concepts:
                if concept not in all_concepts:
                    all_concepts.append(concept)
        display_concepts = all_concepts[:8]

        chip_y = 0.80
        for i, concept in enumerate(display_concepts):
            col = 0 if i % 2 == 0 else 1
            row = i // 2
            x_pos = 0.56 if col == 0 else 0.77
            y_pos = chip_y - (row * 0.17)

            c_box = FancyBboxPatch(
                (x_pos, y_pos), 0.19, 0.12,
                boxstyle="round,pad=0.015,rounding_size=0.02",
                facecolor=PALETTE["card_bg"],
                edgecolor=PALETTE["card_border"],
                linewidth=0.8
            )
            ax_bottom.add_patch(c_box)

            ax_bottom.text(
                x_pos + 0.095, y_pos + 0.06, wrap_text_lines(concept, max_chars=18, max_lines=2),
                color=PALETTE["text_accent"], fontsize=7.2, fontweight="bold",
                ha="center", va="center"
            )

        # -------------------------------------------------------------
        # 4. FOOTER SECTION
        # -------------------------------------------------------------
        ax_footer = fig.add_subplot(gs[3])
        ax_footer.set_facecolor(PALETTE["bg"])
        ax_footer.axis("off")

        # Hairline
        ax_footer.plot([0.04, 0.96], [0.8, 0.8], color=PALETTE["card_border"], linewidth=0.8)

        ax_footer.text(
            0.04, 0.2, "Generated autonomously via GitHub Actions  •  ₹0/month Open Research Architecture",
            color=PALETTE["text_secondary"], fontsize=7.5
        )
        ax_footer.text(
            0.96, 0.2, "arXiv / Daily Tech Intelligence",
            color=PALETTE["accent_primary"], fontsize=7.5, fontweight="bold",
            ha="right"
        )

        plt.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
        fig.savefig(
            output_path,
            dpi=150,
            facecolor=fig.get_facecolor(),
            edgecolor="none",
            bbox_inches="tight"
        )
        plt.close(fig)

        # Optimize with Pillow
        try:
            with Image.open(output_path) as im:
                im.save(output_path, "PNG", optimize=True)
        except Exception as opt_err:
            logger.debug(f"Pillow image optimization notice: {opt_err}")

        logger.info(f"Successfully generated infographic at {output_path}")
        return True

    except Exception as exc:
        logger.error(f"Failed to generate daily infographic: {exc}", exc_info=True)
        plt.close("all")
        return False
