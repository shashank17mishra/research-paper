"""
Utility Functions
=================
Logging, text sanitization, date formatting, and resilient atomic file I/O.
"""

from __future__ import annotations

import json
import logging
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def setup_logger(name: str = "daily_tech_intel", level: str = "INFO") -> logging.Logger:
    """Configures and returns a structured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(numeric_level)

        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def clean_text(text: Optional[str]) -> str:
    """Normalizes whitespace and removes stray formatting/LaTeX artifacts."""
    if not text:
        return ""
    # Replace newlines, tabs and multiple spaces with a single space
    cleaned = re.sub(r"\s+", " ", text)
    # Remove common LaTeX math wraps if simple ($x$ -> x)
    cleaned = re.sub(r"\$([^$]+)\$", r"\1", cleaned)
    # Strip unnecessary quotes and leading/trailing whitespace
    return cleaned.strip()


def extract_base_arxiv_id(raw_id: str) -> str:
    """
    Extracts the normalized canonical arXiv ID without URL prefix or version suffix.
    Examples:
        'http://arxiv.org/abs/2403.01234v2' -> '2403.01234'
        '2403.01234v1' -> '2403.01234'
        'cs/0102034v1' -> 'cs/0102034'
    """
    if not raw_id:
        return ""
    cleaned = raw_id.strip()
    # Strip URL prefixes
    if "arxiv.org/abs/" in cleaned:
        cleaned = cleaned.split("arxiv.org/abs/")[-1]
    elif "arxiv.org/pdf/" in cleaned:
        cleaned = cleaned.split("arxiv.org/pdf/")[-1].replace(".pdf", "")

    # Strip version suffix if standard numeric (e.g. v1, v2)
    cleaned = re.sub(r"v\d+$", "", cleaned)
    return cleaned.strip("/")


def parse_datetime(date_str: str) -> datetime:
    """Parses an ISO 8601 date string into a UTC datetime."""
    if not date_str:
        return datetime.now(timezone.utc)
    # Clean Z suffix for fromisoformat compatibility
    cleaned = date_str.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(cleaned)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return datetime.now(timezone.utc)


def format_display_date(dt: datetime) -> str:
    """Formats datetime as '08 October 2026'."""
    return dt.strftime("%d %B %Y")


def format_path_date(dt: datetime) -> tuple[str, str, str]:
    """Returns tuple of strings: (YYYY, MM, DD)."""
    return dt.strftime("%Y"), dt.strftime("%m"), dt.strftime("%d")


def atomic_write_json(file_path: Path, data: Any, indent: int = 2) -> None:
    """
    Safely writes JSON data to a file using an atomic write pattern
    to prevent file corruption during pipeline failures.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = file_path.parent
    with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False, encoding="utf-8") as tf:
        json.dump(data, tf, indent=indent, ensure_ascii=False)
        temp_name = Path(tf.name)
    temp_name.replace(file_path)


def safe_read_json(file_path: Path, default: Any = None) -> Any:
    """Safely reads a JSON file; returns default if missing or invalid."""
    if not file_path.exists():
        return default if default is not None else []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default if default is not None else []


def count_words(text: str) -> int:
    """Counts words in a string."""
    return len(text.split())
