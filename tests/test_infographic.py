"""
Unit Tests: Daily Infographic Generation
"""

from pathlib import Path
from src.infographic import generate_daily_infographic


def test_generate_daily_infographic(sample_papers, tmp_path: Path):
    output_png = tmp_path / "infographic.png"
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
    assert output_png.stat().st_size > 1000

    # Also assert all 3 template files were generated in the directory
    for tmpl in ["editorial", "modern", "spotlight"]:
        tmpl_file = tmp_path / f"infographic_{tmpl}.png"
        assert tmpl_file.exists()
        assert tmpl_file.stat().st_size > 1000


def test_individual_templates(sample_papers, tmp_path: Path):
    sample_papers[0].key_concepts = ["Edge AI", "Neural Pruning"]
    sample_papers[1].key_concepts = ["Diffusion Policy", "SLAM"]
    sample_papers[2].key_concepts = ["Transformers", "Autonomous Racing"]

    for tmpl in ["editorial", "modern", "spotlight"]:
        dest = tmp_path / f"test_{tmpl}.png"
        ok = generate_daily_infographic(
            papers=sample_papers,
            display_date="08 October 2026",
            output_path=dest,
            template=tmpl
        )
        assert ok is True
        assert dest.exists()
        assert dest.stat().st_size > 1000
