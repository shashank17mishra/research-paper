"""
Master Infographic Renderer Dispatcher
======================================
Coordinates rendering across all 3 publication templates:
1. 'editorial': Classic Editorial Research Journal
2. 'modern': Modern Tech Studio Infographic (with donut chart & laptop researcher)
3. 'spotlight': Gen-Z Editorial Spotlight Broadside (with yellow vignettes & walking figure)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import matplotlib
matplotlib.use("Agg")  # Headless rendering for GitHub Actions

from src.infographic.template_editorial import render_template_editorial
from src.infographic.template_modern import render_template_modern
from src.infographic.template_spotlight import render_template_spotlight
from src.utils import setup_logger

logger = setup_logger("infographic_master")

TEMPLATES = {
    "editorial": render_template_editorial,
    "modern": render_template_modern,
    "spotlight": render_template_spotlight,
}


def derive_daily_insight(papers: List[Any]) -> tuple[str, str]:
    """Derives a meaningful cross-paper synthesis insight and tagline from daily research."""
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


def render_infographic(
    data: Dict[str, Any],
    output_path: Path,
    template: str = "spotlight",
) -> bool:
    """
    Renders an infographic using the specified template ('editorial', 'modern', or 'spotlight').
    """
    renderer_func = TEMPLATES.get(template.lower(), render_template_spotlight)
    return renderer_func(data, output_path)


def generate_daily_infographic(
    papers: List[Any],
    display_date: str,
    output_path: Path,
    template: Optional[str] = None,
) -> bool:
    """
    High-level entry point used by the main pipeline and archive generation.
    Generates the primary infographic and all 3 template variants in the destination directory.

    Outputs:
      - output_path (primary, defaults to spotlight template)
      - output_path.parent / 'infographic_editorial.png'
      - output_path.parent / 'infographic_modern.png'
      - output_path.parent / 'infographic_spotlight.png'
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        top_papers = papers[:3] if len(papers) >= 3 else papers

        # Category counts
        cat_counts: Dict[str, int] = {}
        for p in papers:
            for cat in getattr(p, "categories", []):
                cat_counts[cat] = cat_counts.get(cat, 0) + 1
        if not cat_counts:
            cat_counts = {"cs.RO": 1, "cs.DC": 1, "cs.AI": 1}

        # Concept aggregation
        all_concepts: List[str] = []
        for p in papers:
            for c in getattr(p, "key_concepts", []):
                if c not in all_concepts:
                    all_concepts.append(c)

        insight_tuple = derive_daily_insight(papers)

        data = {
            "date": display_date,
            "papers": top_papers,
            "categories": cat_counts,
            "concepts": all_concepts,
            "statistics": {
                "papers_analyzed": len(papers),
                "categories_count": len(cat_counts),
                "concepts_count": len(all_concepts),
            },
            "daily_insight": insight_tuple,
        }

        # 1. Render all 3 templates
        editorial_path = output_path.parent / "infographic_editorial.png"
        modern_path = output_path.parent / "infographic_modern.png"
        spotlight_path = output_path.parent / "infographic_spotlight.png"

        render_template_editorial(data, editorial_path)
        render_template_modern(data, modern_path)
        render_template_spotlight(data, spotlight_path)

        # 2. Render primary output_path with chosen or default template (spotlight)
        chosen = template if template in TEMPLATES else "spotlight"
        success = render_infographic(data, output_path, template=chosen)

        logger.info(f"Generated all 3 infographic templates successfully in {output_path.parent}")
        return success

    except Exception as e:
        logger.error(f"Failed to generate daily infographics: {e}", exc_info=True)
        return False
