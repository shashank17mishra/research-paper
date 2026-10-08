"""
Unit Tests: Technical Summary Generation
"""

from src.summarizer import (
    classify_sentences,
    generate_summary,
    split_into_sentences,
)
from src.utils import count_words


def test_split_into_sentences():
    text = "We evaluate on robots (e.g. quadrupeds). The results demonstrate 95% accuracy."
    s = split_into_sentences(text)
    assert len(s) == 2
    assert "e.g." in s[0]


def test_classify_sentences():
    sentences = [
        "However, existing methods suffer from high computational overhead.",
        "We propose a novel attention pruning mechanism.",
        "Experiments demonstrate superior performance on real hardware.",
    ]
    classified = classify_sentences(sentences)
    assert len(classified["problem"]) == 1
    assert len(classified["approach"]) == 1
    assert len(classified["results"]) == 1


def test_generate_summary_length_and_content(sample_papers):
    paper = sample_papers[0]
    summary = generate_summary(paper, target_min=70, target_max=200)
    w_count = count_words(summary)
    assert w_count >= 60
    assert w_count <= 220
    assert paper.summary == summary


def test_generate_summary_fallback_on_empty(sample_papers):
    paper = sample_papers[0]
    paper.abstract = ""
    summary = generate_summary(paper)
    assert len(summary) > 30
    assert paper.title in summary
