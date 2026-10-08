"""
Paper Filtering and Duplicate Detection Module
==============================================
Enforces strict data quality validation and prevents duplicate publications
by maintaining a persistent ledger of processed arXiv IDs.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Set, Tuple
import re

from src.fetcher import Paper
from src.utils import extract_base_arxiv_id, safe_read_json, setup_logger

logger = setup_logger("filter")


def load_existing_arxiv_ids(data_file: Path) -> Set[str]:
    """
    Reads existing papers ledger from data/papers.json and extracts
    canonical base arXiv IDs for fast O(1) deduplication.
    """
    if not data_file.exists():
        return set()

    records = safe_read_json(data_file, default=[])
    existing_ids = set()
    for item in records:
        raw = item.get("arxiv_id", "")
        if raw:
            existing_ids.add(extract_base_arxiv_id(raw))
    logger.info(f"Loaded {len(existing_ids)} previously processed arXiv IDs from {data_file}.")
    return existing_ids


def normalize_title_for_comparison(title: str) -> str:
    """Normalizes title string for duplicate title detection."""
    clean = re.sub(r"[^a-zA-Z0-9]", "", title.lower())
    return clean


def validate_paper_quality(paper: Paper) -> Tuple[bool, str]:
    """
    Validates paper data against quality requirements:
    - arXiv ID exists
    - Title exists (minimum length and valid characters)
    - Authors list is non-empty
    - Abstract exists (meaningful length, not placeholder)
    - Paper URL exists
    """
    if not paper.arxiv_id or len(paper.arxiv_id.strip()) < 4:
        return False, "Missing or invalid arXiv ID"

    if not paper.title or len(paper.title.strip()) < 5:
        return False, "Missing or trivially short title"

    if not paper.authors:
        return False, "Missing authors list"

    if not paper.abstract or len(paper.abstract.strip()) < 50:
        return False, "Missing or trivially short abstract (<50 chars)"

    if not paper.url or not paper.url.startswith("http"):
        return False, "Missing or invalid paper URL"

    return True, "Valid"


def filter_and_deduplicate(
    candidate_papers: List[Paper],
    existing_ids: Set[str]
) -> List[Paper]:
    """
    Filters candidates by:
    1. Duplicate check against existing ledger.
    2. Quality and completeness checks.
    3. Duplicate title check within the incoming batch.
    """
    accepted: List[Paper] = []
    seen_in_batch_ids: Set[str] = set()
    seen_in_batch_titles: Set[str] = set()

    for paper in candidate_papers:
        base_id = extract_base_arxiv_id(paper.arxiv_id)

        # 1. Check existing historical database
        if base_id in existing_ids:
            logger.debug(f"Skipping paper {base_id} (already published in ledger).")
            continue

        # 2. Check intra-batch duplicate ID
        if base_id in seen_in_batch_ids:
            logger.debug(f"Skipping paper {base_id} (duplicate within current batch).")
            continue

        # 3. Validate data quality
        is_valid, reason = validate_paper_quality(paper)
        if not is_valid:
            logger.warning(f"Discarding malformed paper {paper.arxiv_id or 'unknown'}: {reason}")
            continue

        # 4. Intra-batch duplicate normalized title check
        norm_title = normalize_title_for_comparison(paper.title)
        if norm_title in seen_in_batch_titles:
            logger.debug(f"Skipping duplicate title in batch: {paper.title}")
            continue

        seen_in_batch_ids.add(base_id)
        seen_in_batch_titles.add(norm_title)
        accepted.append(paper)

    logger.info(
        f"Filtered {len(candidate_papers)} candidates: "
        f"{len(accepted)} accepted, {len(candidate_papers) - len(accepted)} filtered out."
    )
    return accepted
