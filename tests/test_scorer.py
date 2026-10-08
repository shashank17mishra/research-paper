"""
Unit Tests: Relevance Scoring and Ranking
"""

from src.scorer import RelevanceScorer


def test_scoring_bounded(sample_papers, test_config):
    scorer = RelevanceScorer(test_config)
    for p in sample_papers:
        score = scorer.score_paper(p)
        assert 0.0 <= score <= 1.0
        assert p.relevance_score == score


def test_robotics_paper_classification(sample_papers, test_config):
    scorer = RelevanceScorer(test_config)
    # The first sample paper is robotics
    scorer.score_paper(sample_papers[0])
    assert sample_papers[0].primary_topic in ["Robotics", "Computer Vision", "Artificial Intelligence"]


def test_rank_and_select(sample_papers, test_config):
    test_config.papers_per_day = 2
    test_config.minimum_relevance_score = 0.30
    scorer = RelevanceScorer(test_config)

    ranked = scorer.rank_and_select(sample_papers)
    assert len(ranked) <= 2
    # Ensure descending order
    if len(ranked) == 2:
        assert ranked[0].relevance_score >= ranked[1].relevance_score


def test_threshold_filtering(sample_papers, test_config):
    test_config.minimum_relevance_score = 0.99  # Excessively high
    scorer = RelevanceScorer(test_config)
    ranked = scorer.rank_and_select(sample_papers)
    assert len(ranked) == 0
