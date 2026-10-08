"""
Unit Tests: Key Concept Extraction
"""

from src.concepts import extract_key_concepts, format_concept_casing


def test_format_concept_casing():
    assert format_concept_casing("iot") == "IoT"
    assert format_concept_casing("tinyml") == "TinyML"
    assert format_concept_casing("vision transformer") == "Vision Transformer"
    assert format_concept_casing("sim-to-real") == "Sim-to-Real Transfer"


def test_extract_key_concepts_from_paper(sample_papers):
    paper = sample_papers[0]
    concepts = extract_key_concepts(paper, max_concepts=5)
    assert len(concepts) > 0
    assert len(concepts) <= 5
    # Concepts should match prominent themes in paper 0 (Vision Transformer, Robot Navigation, etc.)
    lowered = [c.lower() for c in concepts]
    assert any("vision transformer" in c or "manipulation" in c or "robot" in c for c in lowered)
