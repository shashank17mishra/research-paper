"""
Relevance Scorer Module
=======================
Calculates multi-dimensional relevance scores for research papers based on:
keyword matches, topic alignment, category matching, recency decay, and title relevance.
Selects and ranks the top N papers per day.
"""

from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from src.config import AppConfig, TopicsConfig
from src.fetcher import Paper
from src.utils import parse_datetime, setup_logger

logger = setup_logger("scorer")


class RelevanceScorer:
    """Scores candidate research papers against configured topics and keywords."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.topics_cfg: TopicsConfig = config.topics_config

    def score_paper(self, paper: Paper) -> float:
        """
        Calculates normalized relevance score (0.0 to 1.0) using configured weights:
        relevance_score =
            w_kw * keyword_match
          + w_topic * topic_match
          + w_cat * category_match
          + w_rec * recency_score
          + w_title * title_relevance
        """
        weights = self.topics_cfg.scoring_weights

        kw_score, matched_topic = self._compute_keyword_score(paper)
        topic_score = self._compute_topic_score(paper, matched_topic)
        cat_score = self._compute_category_score(paper)
        recency_score = self._compute_recency_score(paper)
        title_score = self._compute_title_relevance(paper)

        raw_score = (
            weights.keyword_match * kw_score +
            weights.topic_match * topic_score +
            weights.category_match * cat_score +
            weights.recency_score * recency_score +
            weights.title_relevance * title_score
        )

        final_score = max(0.0, min(1.0, round(raw_score, 3)))
        paper.relevance_score = final_score
        paper.primary_topic = matched_topic or "AI"
        return final_score

    def _compute_keyword_score(self, paper: Paper) -> Tuple[float, str]:
        """
        Scans title and abstract against defined keyword groups.
        Title matches receive 2x weighting.
        Identifies highest matching topic.
        """
        title_lower = paper.title.lower()
        abstract_lower = paper.abstract.lower()

        group_hits: Dict[str, int] = {}
        total_unique_hits = 0

        for group_name, keywords in self.topics_cfg.keyword_groups.items():
            hits = 0
            for kw in keywords:
                pattern = r"\b" + re.escape(kw.lower()) + r"\b"
                in_title = len(re.findall(pattern, title_lower))
                in_abstract = len(re.findall(pattern, abstract_lower))
                if in_title > 0 or in_abstract > 0:
                    hits += (in_title * 2) + min(in_abstract, 3)
                    total_unique_hits += 1
            group_hits[group_name] = hits

        # Identify dominant group
        best_group = "AI_KEYWORDS"
        if group_hits:
            best_group = max(group_hits, key=lambda k: group_hits[k])

        topic_label_map = {
            "AI_KEYWORDS": "Artificial Intelligence",
            "ML_KEYWORDS": "Machine Learning",
            "ROBOTICS_KEYWORDS": "Robotics",
            "IOT_KEYWORDS": "IoT & Edge AI",
            "CV_KEYWORDS": "Computer Vision",
            "NLP_KEYWORDS": "Natural Language Processing"
        }
        dominant_topic = topic_label_map.get(best_group, "Artificial Intelligence")

        # Normalize hits with saturation curve (e.g. 5+ distinct hits yields ~1.0)
        norm_kw = 1.0 - math.exp(-total_unique_hits / 3.5)
        return min(1.0, norm_kw), dominant_topic

    def _compute_topic_score(self, paper: Paper, dominant_topic: str) -> float:
        """Computes topic alignment and applies topic-specific weight multipliers."""
        score = 0.5
        for t in self.topics_cfg.topics:
            if t.label.lower() in dominant_topic.lower():
                score = min(1.0, 0.7 * t.weight)
                break
            for cat in paper.categories:
                if cat in t.category_codes:
                    score = min(1.0, max(score, 0.8 * t.weight))
        return score

    def _compute_category_score(self, paper: Paper) -> float:
        """Scores category overlap against configured target categories."""
        if not paper.categories:
            return 0.3
        target_cats = set(self.config.arxiv_categories)
        matches = [c for c in paper.categories if c in target_cats]
        if not matches:
            return 0.2
        # If primary category (first listed) matches target list
        primary_match = paper.categories[0] in target_cats
        overlap_ratio = len(matches) / len(paper.categories)
        base = 0.8 if primary_match else 0.5
        return min(1.0, base + 0.2 * overlap_ratio)

    def _compute_recency_score(self, paper: Paper) -> float:
        """
        Exponential decay scoring based on days since publication.
        0 days = 1.0, 3 days = ~0.7, 7 days = ~0.5, >14 days decays further.
        """
        pub_dt = parse_datetime(paper.published_date)
        now = datetime.now(timezone.utc)
        delta_days = max(0.0, (now - pub_dt).total_seconds() / 86400.0)
        # Half-life of 7 days
        return max(0.1, math.exp(-0.1 * delta_days))

    def _compute_title_relevance(self, paper: Paper) -> float:
        """Checks presence of technical keywords directly in the paper title."""
        title_lower = paper.title.lower()
        score = 0.2
        high_signal_terms = [
            "framework", "architecture", "model", "network", "system", "algorithm",
            "transformer", "reinforcement", "autonomous", "robot", "edge", "efficient",
            "benchmark", "foundation", "generative", "neural", "vision", "agent"
        ]
        term_hits = sum(1 for term in high_signal_terms if term in title_lower)
        score += min(0.8, term_hits * 0.2)
        return min(1.0, score)

    def rank_and_select(self, papers: List[Paper]) -> List[Paper]:
        """
        Scores all papers, filters those below threshold, and returns
        the top N papers sorted descending by relevance score.
        """
        scored_papers: List[Paper] = []
        for p in papers:
            score = self.score_paper(p)
            if score >= self.config.minimum_relevance_score:
                scored_papers.append(p)
            else:
                logger.debug(f"Paper {p.arxiv_id} below threshold ({score:.3f} < {self.config.minimum_relevance_score})")

        # Sort descending by relevance score, secondary sort by recency
        scored_papers.sort(
            key=lambda item: (item.relevance_score, item.published_date),
            reverse=True
        )

        selected = scored_papers[:self.config.papers_per_day]
        logger.info(
            f"Ranked {len(scored_papers)} qualifying papers. "
            f"Selected top {len(selected)} (limit={self.config.papers_per_day})."
        )
        return selected
