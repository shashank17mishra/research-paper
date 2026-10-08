"""
Unit Tests: Daily Infographic Generation
"""

from pathlib import Path
from src.infographic import generate_daily_infographic


def test_generate_daily_infographic(sample_papers, tmp_path: Path):
    output_png = tmp_path / "infographic.png"
    # Ensure sample papers have concepts
    sample_papers[0].key_concepts = ["Vision Transformer", "Sim-to-Real Transfer"]
    sample_papers[1].key_concepts = ["TinyML", "Quantization"]
    sample_papers[2].key_concepts = ["Multi-Agent RL", "Drone Swarm"]

    success = generate_daily_infographic(
        papers=sample_papers,
        display_date="08 October 2026",
        output_path=output_png
    )

    assert success is True
    assert output_png.exists()
    assert output_png.stat().st_size > 1000  # Valid non-empty PNG
