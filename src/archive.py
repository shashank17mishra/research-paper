"""
Archive, Report, and Persistence Manager
========================================
Generates daily Markdown reports, updates the persistent paper ledger,
manages monthly/global JSON archives, and aggregates system statistics.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from src.fetcher import Paper
from src.utils import (
    atomic_write_json,
    format_display_date,
    format_path_date,
    safe_read_json,
    setup_logger,
)

logger = setup_logger("archive")


def generate_daily_markdown_report(
    papers: List[Paper],
    run_date: datetime,
    report_path: Path,
    has_infographic: bool = False
) -> str:
    """
    Constructs the standardized daily Markdown research report
    following Section 10 specification.
    """
    report_path.parent.mkdir(parents=True, exist_ok=True)
    display_date = format_display_date(run_date)

    # Collect distinct topics today
    topics_today = sorted(list({p.primary_topic for p in papers}))

    lines: List[str] = [
        "# Daily Tech Intelligence",
        "",
        f"## {display_date}",
        "",
        "### Today's Overview",
        "",
        f"{len(papers)} research papers analyzed.",
        "",
        "Topics:",
        ""
    ]

    for topic in topics_today:
        lines.append(f"* {topic}")

    lines.append("")

    if has_infographic:
        lines.append("![Daily Research Infographic](infographic.png)")
        lines.append("")
        lines.append("### Visual Intelligence Templates")
        lines.append("")
        lines.append("* **Template 3: Gen-Z Spotlight Broadside (Primary)**: [View High-Res](infographic_spotlight.png)")
        lines.append("* **Template 2: Modern Tech Studio**: [View High-Res](infographic_modern.png)")
        lines.append("* **Template 1: Editorial Research Journal**: [View High-Res](infographic_editorial.png)")
        lines.append("")

    lines.append("---")
    lines.append("")

    for idx, paper in enumerate(papers, start=1):
        lines.append(f"## {idx}. {paper.title}")
        lines.append("")
        lines.append(f"Authors: {', '.join(paper.authors)}")
        lines.append("")
        lines.append(f"Publication: {paper.published_date}")
        lines.append("")
        lines.append(f"Category: {', '.join(paper.categories)}")
        lines.append("")
        lines.append(f"Relevance Score: {paper.relevance_score:.2f}")
        lines.append("")
        lines.append(f"Paper: [arXiv:{paper.arxiv_id}]({paper.url}) | [PDF]({paper.pdf_url})")
        lines.append("")

        lines.append("### Summary")
        lines.append("")
        lines.append(paper.summary or "Summary not available.")
        lines.append("")

        lines.append("### Key Concepts")
        lines.append("")
        if paper.key_concepts:
            for concept in paper.key_concepts:
                lines.append(f"* {concept}")
        else:
            lines.append("* Technology intelligence")
        lines.append("")

        lines.append("### Technical Insights")
        lines.append("")
        ins = paper.insights or {}
        lines.append("**Problem**")
        lines.append("")
        lines.append(ins.get("problem", "Not specified in the available abstract."))
        lines.append("")
        lines.append("**Approach**")
        lines.append("")
        lines.append(ins.get("approach", "Not specified in the available abstract."))
        lines.append("")
        lines.append("**Key Innovation**")
        lines.append("")
        lines.append(ins.get("key_innovation", "Not specified in the available abstract."))
        lines.append("")
        lines.append("**Results**")
        lines.append("")
        lines.append(ins.get("results", "Not specified in the available abstract."))
        lines.append("")
        lines.append("**Applications**")
        lines.append("")
        lines.append(ins.get("applications", "Not specified in the available abstract."))
        lines.append("")
        lines.append("**Limitations**")
        lines.append("")
        lines.append(ins.get("limitations", "Not specified in the available abstract."))
        lines.append("")
        lines.append("---")
        lines.append("")

    content = "\n".join(lines)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"Daily report generated successfully at {report_path}")
    return content


def update_papers_ledger(new_papers: List[Paper], data_file: Path) -> List[Dict[str, Any]]:
    """Appends newly processed papers to the primary persistent ledger (data/papers.json)."""
    existing_records: List[Dict[str, Any]] = safe_read_json(data_file, default=[])

    # Convert new Paper objects to dict
    new_dicts = [p.to_dict() for p in new_papers]

    # Combine ensuring no duplicate arxiv_id
    seen_ids = set()
    combined: List[Dict[str, Any]] = []

    for item in existing_records:
        aid = item.get("arxiv_id")
        if aid and aid not in seen_ids:
            seen_ids.add(aid)
            combined.append(item)

    for item in new_dicts:
        aid = item.get("arxiv_id")
        if aid and aid not in seen_ids:
            seen_ids.add(aid)
            combined.append(item)

    atomic_write_json(data_file, combined)
    logger.info(f"Updated {data_file}: total persistent papers = {len(combined)}")
    return combined


def update_statistics(
    new_papers: List[Paper],
    run_date: datetime,
    stats_file: Path,
    all_papers: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Updates and computes aggregate metrics in data/statistics.json."""
    stats = safe_read_json(stats_file, default={})

    total_papers = len(all_papers)
    total_runs = stats.get("total_runs", 0) + (1 if new_papers else 0)

    # Categories breakdown
    cat_counter: Counter[str] = Counter()
    topic_counter: Counter[str] = Counter()
    daily_counts = stats.get("daily_counts", {})

    for p in all_papers:
        for c in p.get("categories", []):
            cat_counter[c] += 1
        topic = p.get("primary_topic", "AI")
        topic_counter[topic] += 1

    date_str = run_date.strftime("%Y-%m-%d")
    daily_counts[date_str] = daily_counts.get(date_str, 0) + len(new_papers)

    updated_stats = {
        "total_papers": total_papers,
        "total_runs": total_runs,
        "last_run_date": date_str,
        "categories_breakdown": dict(cat_counter.most_common(15)),
        "topics_breakdown": dict(topic_counter.most_common(10)),
        "daily_counts": daily_counts
    }

    atomic_write_json(stats_file, updated_stats)
    logger.info(f"Updated statistics: total_papers={total_papers}, runs={total_runs}")
    return updated_stats


def update_archives(all_papers: List[Dict[str, Any]], archive_dir: Path) -> None:
    """
    Builds global archive/index.json and monthly partition archives
    in archive/YYYY/MM/index.json.
    """
    archive_dir.mkdir(parents=True, exist_ok=True)

    # Group papers by YYYY/MM
    monthly_groups: Dict[str, List[Dict[str, Any]]] = {}
    for p in all_papers:
        pub = p.get("published_date", "")
        if len(pub) >= 7:
            key = pub[:7]  # YYYY-MM
        else:
            key = datetime.now().strftime("%Y-%m")
        monthly_groups.setdefault(key, []).append(p)

    # Write each monthly archive
    for month_key, month_papers in monthly_groups.items():
        parts = month_key.split("-")
        if len(parts) == 2:
            year, month = parts
            month_dir = archive_dir / year / month
            month_dir.mkdir(parents=True, exist_ok=True)
            month_index_file = month_dir / "index.json"
            atomic_write_json(month_index_file, {
                "month": month_key,
                "total_papers": len(month_papers),
                "papers": month_papers
            })

    # Write global index
    global_index_file = archive_dir / "index.json"
    atomic_write_json(global_index_file, {
        "updated_at": datetime.now().isoformat(),
        "total_entries": len(all_papers),
        "months": sorted(list(monthly_groups.keys()), reverse=True),
        "papers": all_papers
    })
    logger.info(f"Global and monthly archives successfully synchronized in {archive_dir}")


import shutil


def sync_site_data(
    site_dir: Path,
    reports_dir: Path,
    all_papers: List[Dict[str, Any]],
    stats: Dict[str, Any]
) -> None:
    """
    Copies current data directly to site/data/ and mirrors reports/
    into site/reports/ for self-contained GitHub Pages deployment.
    """
    site_data_dir = site_dir / "data"
    site_data_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_json(site_data_dir / "papers.json", all_papers)
    atomic_write_json(site_data_dir / "statistics.json", stats)

    # Mirror reports into site/reports so they are served directly by GitHub Pages
    if reports_dir.exists():
        site_reports_dir = site_dir / "reports"
        site_reports_dir.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copytree(reports_dir, site_reports_dir, dirs_exist_ok=True)
        except Exception as copy_err:
            logger.warning(f"Notice while mirroring reports to site: {copy_err}")

    logger.info(f"Synchronized static dataset and reports to {site_dir}")
