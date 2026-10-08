"""
Unit Tests: Paper Data Quality Validation
"""

from src.fetcher import Paper
from src.filter import validate_paper_quality, filter_and_deduplicate


def test_validate_valid_paper(sample_papers):
    valid, reason = validate_paper_quality(sample_papers[0])
    assert valid is True
    assert reason == "Valid"


def test_reject_missing_title(sample_papers):
    bad = Paper(**sample_papers[0].to_dict())
    bad.title = ""
    valid, reason = validate_paper_quality(bad)
    assert valid is False
    assert "title" in reason.lower()


def test_reject_short_abstract(sample_papers):
    bad = Paper(**sample_papers[0].to_dict())
    bad.abstract = "Too short"
    valid, reason = validate_paper_quality(bad)
    assert valid is False
    assert "abstract" in reason.lower()


def test_reject_empty_authors(sample_papers):
    bad = Paper(**sample_papers[0].to_dict())
    bad.authors = []
    valid, reason = validate_paper_quality(bad)
    assert valid is False
    assert "authors" in reason.lower()


def test_reject_duplicate_titles_in_batch(sample_papers):
    p1 = sample_papers[0]
    p2 = Paper(**sample_papers[1].to_dict())
    p2.title = p1.title.upper()  # Same title, different casing
    p2.arxiv_id = "9999.99999"

    filtered = filter_and_deduplicate([p1, p2], set())
    assert len(filtered) == 1
