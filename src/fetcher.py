"""
Paper Fetcher Module
====================
Retrieves the latest academic research from arXiv using the official API,
with rate limiting, polite User-Agent headers, exponential backoff, and Atom parsing.
Architected modularly to support future sources (Hugging Face, GitHub Trending, etc.).
"""

from __future__ import annotations

import time
import urllib.parse
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import requests

from src.config import AppConfig
from src.utils import clean_text, extract_base_arxiv_id, setup_logger

logger = setup_logger("fetcher")

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


@dataclass
class Paper:
    arxiv_id: str
    raw_id: str
    title: str
    authors: List[str]
    published_date: str
    updated_date: str
    categories: List[str]
    abstract: str
    url: str
    pdf_url: str
    relevance_score: float = 0.0
    processed_date: str = ""
    summary: str = ""
    key_concepts: List[str] = field(default_factory=list)
    insights: Dict[str, str] = field(default_factory=dict)
    primary_topic: str = "AI"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Paper:
        return cls(
            arxiv_id=data.get("arxiv_id", ""),
            raw_id=data.get("raw_id", data.get("arxiv_id", "")),
            title=data.get("title", ""),
            authors=data.get("authors", []),
            published_date=data.get("published_date", ""),
            updated_date=data.get("updated_date", ""),
            categories=data.get("categories", []),
            abstract=data.get("abstract", ""),
            url=data.get("url", ""),
            pdf_url=data.get("pdf_url", ""),
            relevance_score=float(data.get("relevance_score", 0.0)),
            processed_date=data.get("processed_date", ""),
            summary=data.get("summary", ""),
            key_concepts=data.get("key_concepts", []),
            insights=data.get("insights", {}),
            primary_topic=data.get("primary_topic", "AI")
        )


class BaseFetcher(ABC):
    """Abstract base class for all paper collection sources."""

    @abstractmethod
    def fetch_papers(self, limit: int) -> List[Paper]:
        """Fetch recent papers up to specified limit."""
        pass


class ArxivFetcher(BaseFetcher):
    """
    Fetches recent papers from the arXiv API with query categorization,
    polite headers, exponential backoff, and XML parsing.
    """

    BASE_URL = "https://export.arxiv.org/api/query"

    def __init__(self, config: AppConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.config.user_agent,
            "Accept": "application/atom+xml,application/xml"
        })

    def _build_query_url(self, limit: int) -> str:
        """Constructs the arXiv API query for target categories."""
        # Join categories with OR logic
        cat_query = " OR ".join(f"cat:{cat.strip()}" for cat in self.config.arxiv_categories)
        params = {
            "search_query": cat_query,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "start": 0,
            "max_results": limit
        }
        return f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"

    def fetch_papers(self, limit: Optional[int] = None) -> List[Paper]:
        fetch_limit = limit or self.config.fetch_limit
        url = self._build_query_url(fetch_limit)
        logger.info(f"Querying arXiv API for categories {self.config.arxiv_categories} (limit={fetch_limit})")

        response_text = self._request_with_retry(url)
        if not response_text:
            logger.warning("Empty response received from arXiv API.")
            return []

        papers = self._parse_atom_feed(response_text)
        logger.info(f"Successfully retrieved and parsed {len(papers)} candidate papers from arXiv.")
        return papers

    def _request_with_retry(self, url: str) -> Optional[str]:
        """Performs HTTP GET with exponential backoff on retryable HTTP errors or network glitches."""
        retries = self.config.max_retries
        backoff = self.config.retry_backoff_seconds

        for attempt in range(1, retries + 1):
            try:
                response = self.session.get(url, timeout=self.config.request_timeout_seconds)
                if response.status_code == 200:
                    return response.text
                elif response.status_code in (429, 500, 502, 503, 504):
                    logger.warning(
                        f"arXiv API returned status {response.status_code} (attempt {attempt}/{retries}). "
                        f"Backing off {backoff}s..."
                    )
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    logger.error(f"arXiv API request failed with status {response.status_code}: {response.text[:200]}")
                    return None
            except requests.RequestException as exc:
                logger.warning(f"Network error contacting arXiv (attempt {attempt}/{retries}): {exc}")
                if attempt == retries:
                    logger.error("Max retries exceeded when calling arXiv API.")
                    return None
                time.sleep(backoff)
                backoff *= 2

        return None

    def _parse_atom_feed(self, xml_content: str) -> List[Paper]:
        """Parses arXiv Atom XML feed into Paper dataclass instances."""
        papers: List[Paper] = []
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as err:
            logger.error(f"Failed to parse XML response from arXiv: {err}")
            return []

        for entry in root.findall("atom:entry", ATOM_NS):
            try:
                raw_id_elem = entry.find("atom:id", ATOM_NS)
                raw_id = clean_text(raw_id_elem.text) if raw_id_elem is not None and raw_id_elem.text else ""
                base_id = extract_base_arxiv_id(raw_id)

                title_elem = entry.find("atom:title", ATOM_NS)
                title = clean_text(title_elem.text) if title_elem is not None and title_elem.text else ""

                summary_elem = entry.find("atom:summary", ATOM_NS)
                abstract = clean_text(summary_elem.text) if summary_elem is not None and summary_elem.text else ""

                published_elem = entry.find("atom:published", ATOM_NS)
                published = clean_text(published_elem.text) if published_elem is not None and published_elem.text else ""

                updated_elem = entry.find("atom:updated", ATOM_NS)
                updated = clean_text(updated_elem.text) if updated_elem is not None and updated_elem.text else published

                # Authors
                authors: List[str] = []
                for author_elem in entry.findall("atom:author", ATOM_NS):
                    name_elem = author_elem.find("atom:name", ATOM_NS)
                    if name_elem is not None and name_elem.text:
                        authors.append(clean_text(name_elem.text))

                # Categories
                categories: List[str] = []
                for cat_elem in entry.findall("atom:category", ATOM_NS):
                    term = cat_elem.attrib.get("term")
                    if term:
                        categories.append(term.strip())

                # Links (HTML page & PDF)
                paper_url = f"https://arxiv.org/abs/{base_id}" if base_id else raw_id
                pdf_url = f"https://arxiv.org/pdf/{base_id}.pdf" if base_id else ""

                for link_elem in entry.findall("atom:link", ATOM_NS):
                    rel = link_elem.attrib.get("rel", "")
                    title_attr = link_elem.attrib.get("title", "")
                    href = link_elem.attrib.get("href", "")
                    if rel == "alternate" and href:
                        paper_url = href
                    elif title_attr == "pdf" and href:
                        pdf_url = href

                if not pdf_url and base_id:
                    pdf_url = f"https://arxiv.org/pdf/{base_id}.pdf"

                papers.append(Paper(
                    arxiv_id=base_id,
                    raw_id=raw_id,
                    title=title,
                    authors=authors,
                    published_date=published,
                    updated_date=updated,
                    categories=categories,
                    abstract=abstract,
                    url=paper_url,
                    pdf_url=pdf_url
                ))
            except Exception as entry_err:
                logger.warning(f"Error parsing single paper entry; skipping: {entry_err}")
                continue

        return papers
