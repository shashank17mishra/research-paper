"""
Unit Tests: Report Generation, Ledger, and Archive Management
"""

from datetime import datetime, timezone
from pathlib import Path

from src.archive import (
    generate_daily_markdown_report,
    sync_site_data,
    update_archives,
    update_papers_ledger,
    update_statistics,
)
from src.utils import safe_read_json


def test_generate_daily_markdown_report(sample_papers, tmp_path: Path):
    report_file = tmp_path / "reports" / "2026" / "10" / "08" / "report.md"
    run_date = datetime(2026, 10, 8, 6, 30, tzinfo=timezone.utc)

    # Populate basic summary/insights for test papers
    sample_papers[0].summary = "Sample summary text."
    sample_papers[0].insights = {"problem": "Problem text", "approach": "Approach text"}

    content = generate_daily_markdown_report(
        sample_papers, run_date, report_file, has_infographic=True
    )

    assert report_file.exists()
    assert "# Daily Tech Intelligence" in content
    assert "## 08 October 2026" in content
    assert "![Daily Research Infographic]" in content
    assert sample_papers[0].title in content


def test_update_papers_ledger_and_stats(sample_papers, tmp_path: Path):
    data_file = tmp_path / "papers.json"
    stats_file = tmp_path / "statistics.json"
    run_date = datetime(2026, 10, 8, tzinfo=timezone.utc)

    all_papers = update_papers_ledger(sample_papers, data_file)
    assert len(all_papers) == len(sample_papers)
    assert data_file.exists()

    stats = update_statistics(sample_papers, run_date, stats_file, all_papers)
    assert stats["total_papers"] == len(sample_papers)
    assert stats["total_runs"] == 1
    assert stats_file.exists()


def test_update_archives(sample_papers, tmp_path: Path):
    archive_dir = tmp_path / "archive"
    paper_dicts = [p.to_dict() for p in sample_papers]

    update_archives(paper_dicts, archive_dir)

    index_file = archive_dir / "index.json"
    assert index_file.exists()
    index_data = safe_read_json(index_file)
    assert index_data["total_entries"] == len(sample_papers)
