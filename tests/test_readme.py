"""
Unit Tests: README Generation and Synchronization
"""

from datetime import datetime, timezone
from pathlib import Path
from src.readme import build_readme_content, update_readme


def test_readme_generation(sample_papers, tmp_path: Path):
    run_date = datetime(2026, 10, 8, 6, 30, tzinfo=timezone.utc)
    paper_dicts = [p.to_dict() for p in sample_papers]
    stats = {
        "total_papers": 3,
        "total_runs": 1,
        "categories_breakdown": {"cs.RO": 2, "cs.DC": 1},
        "topics_breakdown": {"Robotics": 2, "IoT": 1}
    }

    readme_path = update_readme(
        today_papers=sample_papers,
        all_papers=paper_dicts,
        stats=stats,
        run_date=run_date,
        repo_root=tmp_path
    )

    assert readme_path.exists()
    content = readme_path.read_text(encoding="utf-8")

    assert "# Daily Tech Intelligence" in content
    assert "Today's Statistics" in content
    assert "Latest Research" in content
    assert "Project Statistics" in content
    assert "```mermaid" in content
    assert "daily-tech-intelligence/" in content
