"""
Unit Tests: Deduplication and Ledger Tracking
"""

from pathlib import Path
from src.fetcher import Paper
from src.filter import filter_and_deduplicate, load_existing_arxiv_ids
from src.utils import atomic_write_json


def test_load_existing_arxiv_ids_empty(tmp_path: Path):
    non_existent = tmp_path / "papers.json"
    ids = load_existing_arxiv_ids(non_existent)
    assert len(ids) == 0


def test_load_existing_arxiv_ids_populated(tmp_path: Path):
    data_file = tmp_path / "papers.json"
    dummy_data = [
        {"arxiv_id": "2403.00101", "title": "Paper 1"},
        {"arxiv_id": "2403.00102v2", "title": "Paper 2"},
    ]
    atomic_write_json(data_file, dummy_data)
    ids = load_existing_arxiv_ids(data_file)
    assert "2403.00101" in ids
    assert "2403.00102" in ids  # Normalized base id


def test_filter_and_deduplicate_skips_known_papers(sample_papers):
    existing = {"2403.00101"}
    accepted = filter_and_deduplicate(sample_papers, existing)
    # 2403.00101 must be skipped, leaving 2403.00102 and 2403.00103
    assert len(accepted) == 2
    assert all(p.arxiv_id != "2403.00101" for p in accepted)


def test_filter_and_deduplicate_removes_intra_batch_duplicates(sample_papers):
    duplicated_batch = [sample_papers[0], sample_papers[0], sample_papers[1]]
    accepted = filter_and_deduplicate(duplicated_batch, set())
    assert len(accepted) == 2
