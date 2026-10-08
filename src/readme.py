"""
README Automation Module
========================
Generates and automatically updates README.md with live daily statistics,
latest research highlights, project metrics, architecture diagram,
and synchronized repository tree.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from src.fetcher import Paper
from src.utils import format_display_date, setup_logger

logger = setup_logger("readme")


def generate_repo_tree_repr(root_dir: Path) -> str:
    """Generates a clean ASCII directory tree representation of the repository."""
    ignore_set = {
        ".git", ".pytest_cache", "__pycache__", ".venv", "venv",
        ".ruff_cache", "site", ".DS_Store"
    }

    lines = ["daily-tech-intelligence/"]

    def _walk(directory: Path, prefix: str = "", depth: int = 0):
        if depth > 2:
            return
        entries = sorted(
            [e for e in directory.iterdir() if e.name not in ignore_set and not e.name.endswith(".pyc")],
            key=lambda x: (not x.is_dir(), x.name.lower())
        )
        total = len(entries)
        for idx, entry in enumerate(entries):
            is_last = (idx == total - 1)
            connector = "└── " if is_last else "├── "
            child_prefix = "    " if is_last else "│   "

            if entry.is_dir():
                lines.append(f"{prefix}{connector}{entry.name}/")
                _walk(entry, prefix + child_prefix, depth + 1)
            else:
                lines.append(f"{prefix}{connector}{entry.name}")

    try:
        _walk(root_dir)
        return "\n".join(lines[:35])  # Cap at concise length
    except Exception:
        return (
            "daily-tech-intelligence/\n"
            "├── .github/\n"
            "│   └── workflows/daily-research.yml\n"
            "├── config/\n"
            "├── data/\n"
            "├── reports/\n"
            "├── archive/\n"
            "├── site/\n"
            "├── src/\n"
            "└── tests/\n"
        )


def build_readme_content(
    today_papers: List[Paper],
    all_papers: List[Dict[str, Any]],
    stats: Dict[str, Any],
    run_date: datetime,
    repo_root: Path
) -> str:
    """Builds the full Markdown content for README.md."""
    display_date = format_display_date(run_date)
    year, month, day = run_date.strftime("%Y"), run_date.strftime("%m"), run_date.strftime("%d")
    report_rel_path = f"reports/{year}/{month}/{day}/report.md"
    infographic_rel_path = f"reports/{year}/{month}/{day}/infographic.png"

    # Today's category counts
    today_ai = sum(1 for p in today_papers if any("ai" in c.lower() for c in p.categories) or p.primary_topic == "Artificial Intelligence")
    today_ml = sum(1 for p in today_papers if any("lg" in c.lower() for c in p.categories) or p.primary_topic == "Machine Learning")
    today_rob = sum(1 for p in today_papers if any("ro" in c.lower() for c in p.categories) or "Robotics" in p.primary_topic)
    today_iot = sum(1 for p in today_papers if any("dc" in c.lower() for c in p.categories) or "IoT" in p.primary_topic)

    # Project Stats
    total_papers = stats.get("total_papers", len(all_papers))
    total_runs = stats.get("total_runs", 1)
    cats_breakdown = stats.get("categories_breakdown", {})
    topics_breakdown = stats.get("topics_breakdown", {})

    top_topics_str = ", ".join(list(topics_breakdown.keys())[:4]) or "AI, Machine Learning, Robotics, IoT"

    # Latest 5 papers
    latest_five = all_papers[-5:] if len(all_papers) >= 5 else all_papers
    latest_five = list(reversed(latest_five))

    repo_tree_text = generate_repo_tree_repr(repo_root)

    lines = [
        "# Daily Tech Intelligence",
        "",
        "> **Autonomous Technical Research Intelligence System**  ",
        "> Researches, analyzes, synthesizes, visualizes, and publishes state-of-the-art AI, ML, Robotics, and IoT papers every day at **₹0/month cost**.",
        "",
        "[![Daily Research Workflow](https://github.com/daily-tech-intelligence/daily-tech-intelligence/actions/workflows/daily-research.yml/badge.svg)](https://github.com/daily-tech-intelligence/daily-tech-intelligence/actions/workflows/daily-research.yml)",
        "![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)",
        "![Cost: ₹0/month](https://img.shields.io/badge/Cost-%E2%82%B90%2Fmonth-brightgreen.svg)",
        "![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)",
        "",
        "---",
        "",
        "## Latest Report",
        "",
        f"📅 **[{display_date} Report]({report_rel_path})** — *{len(today_papers)} new breakthrough papers analyzed today.*",
        "",
        f"[Read Full Report →]({report_rel_path}) | [Explore Interactive Dashboard →](site/index.html)",
        "",
    ]

    infographic_file = repo_root / infographic_rel_path
    if infographic_file.exists():
        lines.extend([
            f"[![Daily Infographic]({infographic_rel_path})]({infographic_rel_path})",
            "",
        ])

    lines.extend([
        "---",
        "",
        "## Today's Statistics",
        "",
        "| Metric | Count |",
        "| :--- | :---: |",
        f"| **Papers Analyzed Today** | `{len(today_papers)}` |",
        f"| **Artificial Intelligence (AI)** | `{today_ai}` |",
        f"| **Machine Learning (ML)** | `{today_ml}` |",
        f"| **Robotics** | `{today_rob}` |",
        f"| **IoT & Edge AI** | `{today_iot}` |",
        "",
        "---",
        "",
        "## Latest Research",
        "",
        "| # | Paper Title | Topic | Relevance | Link |",
        "| :-: | :--- | :---: | :-: | :---: |"
    ])

    for idx, p in enumerate(latest_five, start=1):
        title = p.get("title", "")
        # Shorten title if very long for table formatting
        short_title = title if len(title) <= 75 else title[:72] + "..."
        topic = p.get("primary_topic", "AI")
        score = p.get("relevance_score", 0.0)
        aid = p.get("arxiv_id", "")
        url = p.get("url", f"https://arxiv.org/abs/{aid}")
        lines.append(f"| {idx} | **{short_title}** | `{topic}` | `{score:.2f}` | [arXiv]({url}) |")

    lines.extend([
        "",
        "---",
        "",
        "## Project Statistics",
        "",
        f"- **Total Papers Analyzed**: `{total_papers}`",
        f"- **Total Operational Runs**: `{total_runs} days`",
        f"- **Categories Tracked**: `{len(cats_breakdown)} categories`",
        f"- **Primary Focus Areas**: {top_topics_str}",
        "",
        "---",
        "",
        "## Architecture",
        "",
        "```mermaid",
        "flowchart TD",
        "    A[Daily Cron Schedule: 01:00 UTC] --> B[arXiv Official API]",
        "    B --> C[Candidate Ingestion cs.AI, cs.LG, cs.RO, cs.DC]",
        "    C --> D{Duplicate Filter: data/papers.json}",
        "    D -->|New Paper| E[Relevance Scorer & Ranker]",
        "    D -->|Seen| X[Skip]",
        "    E --> F[Top 10 Papers Selection]",
        "    F --> G[Extractive NLP Summarizer]",
        "    F --> H[TF-IDF Key Concept Extractor]",
        "    F --> I[Technical Insights Generator]",
        "    G & H & I --> J[Daily Markdown Report]",
        "    G & H & I --> K[Matplotlib + Pillow Infographic]",
        "    J & K --> L[Archive & Statistics Ledger Update]",
        "    L --> M[Update README & GitHub Pages]",
        "    M --> N[Autonomous Git Commit & Push]",
        "```",
        "",
        "---",
        "",
        "## Automation",
        "",
        "The system runs entirely autonomously via **GitHub Actions** (`.github/workflows/daily-research.yml`):",
        "- **Schedule**: Scheduled daily at `01:00 UTC` (~`06:30 AM IST`).",
        "- **Zero Manual Intervention**: Ingests, analyzes, generates infographics, updates data, and commits automatically.",
        "- **Zero Cost (₹0/month)**: Free GitHub Actions runners, free arXiv API, open-source Python NLP, and GitHub Pages.",
        "- **Manual Triggers**: Supports `workflow_dispatch` for on-demand execution and `--dry-run` testing.",
        "",
        "---",
        "",
        "## Repository Structure",
        "",
        "```text",
        repo_tree_text,
        "```",
        "",
        "---",
        "",
        "## Local Development",
        "",
        "```bash",
        "# 1. Create and activate virtual environment",
        "python -m venv .venv",
        "# Windows:",
        ".venv\\Scripts\\activate",
        "# Linux/macOS:",
        "source .venv/bin/activate",
        "",
        "# 2. Install dependencies",
        "pip install -r requirements.txt",
        "",
        "# 3. Run dry run pipeline (fetches and processes without committing)",
        "python src/main.py --dry-run",
        "",
        "# 4. Run tests",
        "pytest tests/",
        "```",
        "",
        "---",
        "",
        "## License",
        "",
        "This project is licensed under the [MIT License](LICENSE)."
    ])

    return "\n".join(lines) + "\n"


def update_readme(
    today_papers: List[Paper],
    all_papers: List[Dict[str, Any]],
    stats: Dict[str, Any],
    run_date: datetime,
    repo_root: Path
) -> Path:
    """Writes updated README.md to repository root."""
    readme_path = repo_root / "README.md"
    content = build_readme_content(today_papers, all_papers, stats, run_date, repo_root)
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"Updated {readme_path} successfully.")
    return readme_path
