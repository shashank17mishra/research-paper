"""
Configuration Loader
====================
Manages application configuration, topic taxonomies, scoring weights,
and environment overrides.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml


def get_repo_root() -> Path:
    """Returns the absolute root directory of the repository."""
    return Path(__file__).resolve().parent.parent


@dataclass
class TopicDefinition:
    id: str
    label: str
    category_codes: List[str]
    weight: float = 1.0


@dataclass
class ScoringWeights:
    keyword_match: float = 0.35
    topic_match: float = 0.20
    category_match: float = 0.20
    recency_score: float = 0.15
    title_relevance: float = 0.10


@dataclass
class TopicsConfig:
    topics: List[TopicDefinition] = field(default_factory=list)
    keyword_groups: Dict[str, List[str]] = field(default_factory=dict)
    scoring_weights: ScoringWeights = field(default_factory=ScoringWeights)


@dataclass
class AppConfig:
    repo_root: Path
    papers_per_day: int = 10
    minimum_relevance_score: float = 0.40
    fetch_limit: int = 60
    arxiv_categories: List[str] = field(default_factory=lambda: [
        "cs.AI", "cs.LG", "cs.CV", "cs.CL", "cs.RO", "cs.NE", "cs.DC"
    ])
    user_agent: str = "DailyTechIntelligenceBot/1.0 (+https://github.com/daily-tech-intelligence)"
    request_timeout_seconds: int = 30
    max_retries: int = 3
    retry_backoff_seconds: int = 4
    data_file: Path = field(default_factory=lambda: Path("data/papers.json"))
    statistics_file: Path = field(default_factory=lambda: Path("data/statistics.json"))
    reports_dir: Path = field(default_factory=lambda: Path("reports"))
    archive_dir: Path = field(default_factory=lambda: Path("archive"))
    site_dir: Path = field(default_factory=lambda: Path("site"))
    summary_word_min: int = 100
    summary_word_max: int = 200
    max_key_concepts: int = 6
    infographic_width: int = 1200
    infographic_height: int = 1200
    infographic_dpi: int = 150
    dry_run: bool = False
    log_level: str = "INFO"
    topics_config: TopicsConfig = field(default_factory=TopicsConfig)


def load_yaml(file_path: Path) -> Dict[str, Any]:
    """Safely loads a YAML file if it exists, otherwise returns empty dict."""
    if not file_path.exists():
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data or {}


def load_topics_config(repo_root: Path) -> TopicsConfig:
    """Loads topics and keyword definitions from config/topics.yaml."""
    topics_file = repo_root / "config" / "topics.yaml"
    raw_data = load_yaml(topics_file)

    topic_defs: List[TopicDefinition] = []
    for t in raw_data.get("topics", []):
        topic_defs.append(TopicDefinition(
            id=t.get("id", ""),
            label=t.get("label", ""),
            category_codes=t.get("category_codes", []),
            weight=float(t.get("weight", 1.0))
        ))

    keyword_groups = raw_data.get("keyword_groups", {})
    raw_weights = raw_data.get("scoring_weights", {})
    weights = ScoringWeights(
        keyword_match=float(raw_weights.get("keyword_match", 0.35)),
        topic_match=float(raw_weights.get("topic_match", 0.20)),
        category_match=float(raw_weights.get("category_match", 0.20)),
        recency_score=float(raw_weights.get("recency_score", 0.15)),
        title_relevance=float(raw_weights.get("title_relevance", 0.10))
    )

    return TopicsConfig(
        topics=topic_defs,
        keyword_groups=keyword_groups,
        scoring_weights=weights
    )


def load_config(repo_root: Optional[Path] = None, overrides: Optional[Dict[str, Any]] = None) -> AppConfig:
    """
    Loads full application configuration merging config.yaml, topics.yaml,
    environment variables, and dynamic overrides.
    """
    if repo_root is None:
        repo_root = get_repo_root()

    config_file = repo_root / "config" / "config.yaml"
    raw = load_yaml(config_file)
    paths_cfg = raw.get("paths", {})
    summary_cfg = raw.get("summary", {})
    infographic_cfg = raw.get("infographic", {})

    topics_cfg = load_topics_config(repo_root)

    # Base values
    papers_per_day = int(raw.get("papers_per_day", 10))
    min_score = float(raw.get("minimum_relevance_score", 0.40))
    fetch_limit = int(raw.get("fetch_limit", 60))
    arxiv_cats = raw.get("arxiv_categories", [
        "cs.AI", "cs.LG", "cs.CV", "cs.CL", "cs.RO", "cs.NE", "cs.DC"
    ])
    user_agent = raw.get("user_agent", "DailyTechIntelligenceBot/1.0 (+https://github.com/daily-tech-intelligence)")
    timeout = int(raw.get("request_timeout_seconds", 30))
    max_retries = int(raw.get("max_retries", 3))
    backoff = int(raw.get("retry_backoff_seconds", 4))

    # Paths resolved against repo root
    data_file = repo_root / paths_cfg.get("data_file", "data/papers.json")
    stats_file = repo_root / paths_cfg.get("statistics_file", "data/statistics.json")
    reports_dir = repo_root / paths_cfg.get("reports_dir", "reports")
    archive_dir = repo_root / paths_cfg.get("archive_dir", "archive")
    site_dir = repo_root / paths_cfg.get("site_dir", "site")

    # Env overrides
    env_dry_run = os.environ.get("DRY_RUN", "false").lower() in ("true", "1", "yes")
    env_papers_per_day = os.environ.get("PAPERS_PER_DAY")
    if env_papers_per_day and env_papers_per_day.isdigit():
        papers_per_day = int(env_papers_per_day)
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()

    cfg = AppConfig(
        repo_root=repo_root,
        papers_per_day=papers_per_day,
        minimum_relevance_score=min_score,
        fetch_limit=fetch_limit,
        arxiv_categories=arxiv_cats,
        user_agent=user_agent,
        request_timeout_seconds=timeout,
        max_retries=max_retries,
        retry_backoff_seconds=backoff,
        data_file=data_file,
        statistics_file=stats_file,
        reports_dir=reports_dir,
        archive_dir=archive_dir,
        site_dir=site_dir,
        summary_word_min=int(summary_cfg.get("target_word_min", 100)),
        summary_word_max=int(summary_cfg.get("target_word_max", 200)),
        max_key_concepts=int(summary_cfg.get("max_key_concepts", 6)),
        infographic_width=int(infographic_cfg.get("width", 1200)),
        infographic_height=int(infographic_cfg.get("height", 1200)),
        infographic_dpi=int(infographic_cfg.get("dpi", 150)),
        dry_run=env_dry_run,
        log_level=log_level,
        topics_config=topics_cfg
    )

    if overrides:
        for k, v in overrides.items():
            if hasattr(cfg, k):
                setattr(cfg, k, v)

    return cfg
