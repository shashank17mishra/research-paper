"""
Pytest Fixtures and Test Helpers
================================
"""

import pytest
from pathlib import Path
from src.config import AppConfig, load_config
from src.fetcher import Paper


@pytest.fixture
def sample_papers():
    """Provides a realistic set of sample research papers across target domains."""
    return [
        Paper(
            arxiv_id="2403.00101",
            raw_id="http://arxiv.org/abs/2403.00101v1",
            title="Vision Transformer Adaptation for Agile Robot Navigation and Manipulation",
            authors=["Alex Rivera", "Elena Vance", "Hao Zhang"],
            published_date="2026-10-07T10:00:00Z",
            updated_date="2026-10-07T10:00:00Z",
            categories=["cs.RO", "cs.CV", "cs.AI"],
            abstract=(
                "Autonomous mobile manipulators operating in unstructured real-world environments face "
                "severe perception bottlenecks and sim-to-real transfer gaps. However, existing methods struggle "
                "with distribution shifts and latency constraints on edge hardware. In this paper, we propose "
                "AgileViT, a lightweight vision transformer framework for end-to-end robot navigation and dexterous "
                "manipulation. Unlike previous approaches that rely on dense point clouds, our method introduces "
                "a novel cross-attention token pruning mechanism that reduces inference latency by 45%. "
                "Experiments demonstrate that AgileViT achieves state-of-the-art success rates on real physical robots, "
                "outperforming prior baselines by 18.4% across 100 challenging trials. The proposed approach paves the "
                "way for scalable embodied intelligence on low-power platforms."
            ),
            url="https://arxiv.org/abs/2403.00101",
            pdf_url="https://arxiv.org/pdf/2403.00101.pdf"
        ),
        Paper(
            arxiv_id="2403.00102",
            raw_id="http://arxiv.org/abs/2403.00102v1",
            title="EdgeTinyML: Ultra Low-Power Neural Network Quantization for IoT Sensor Networks",
            authors=["Kenji Sato", "Priya Sharma"],
            published_date="2026-10-06T15:30:00Z",
            updated_date="2026-10-06T15:30:00Z",
            categories=["cs.DC", "cs.LG"],
            abstract=(
                "Deploying deep neural networks onto microcontroller-class IoT sensors is severely constrained by "
                "energy budgets and sub-megabyte memory limits. Traditional post-training quantization often suffers "
                "from significant accuracy degradation. To address this challenge, we introduce EdgeTinyML, a 2-bit "
                "weight quantization scheme with on-device fine-tuning tailored for embedded systems. Our key innovation "
                "is an integer-only matrix multiplication kernel optimized for ARM Cortex-M cores. Comprehensive benchmarks "
                "show an 8x memory reduction with less than 0.8% loss in classification accuracy. This enables reliable "
                "autonomous edge intelligence on solar-powered sensor nodes."
            ),
            url="https://arxiv.org/abs/2403.00102",
            pdf_url="https://arxiv.org/pdf/2403.00102.pdf"
        ),
        Paper(
            arxiv_id="2403.00103",
            raw_id="http://arxiv.org/abs/2403.00103v1",
            title="Multi-Agent Reinforcement Learning for Autonomous Drone Swarm Coordination",
            authors=["Sarah Connor", "Marcus Vance"],
            published_date="2026-10-05T08:00:00Z",
            updated_date="2026-10-05T08:00:00Z",
            categories=["cs.AI", "cs.RO", "cs.LG"],
            abstract=(
                "Coordinating decentralized drone swarms in communication-denied operational zones remains an open "
                "challenge in autonomous robotics. Existing centralized planning systems fail under network latency. "
                "We formulate a scalable multi-agent reinforcement learning algorithm featuring graph attention communication. "
                "The primary novelty is a predictive trajectory consensus policy that eliminates inter-agent collisions. "
                "Simulation and flight tests show a 32% increase in target search efficiency compared to standard baselines."
            ),
            url="https://arxiv.org/abs/2403.00103",
            pdf_url="https://arxiv.org/pdf/2403.00103.pdf"
        )
    ]


@pytest.fixture
def test_config(tmp_path: Path):
    """Provides an isolated test configuration pointing to temporary directory."""
    cfg = load_config(repo_root=tmp_path)
    cfg.data_file = tmp_path / "data" / "papers.json"
    cfg.statistics_file = tmp_path / "data" / "statistics.json"
    cfg.reports_dir = tmp_path / "reports"
    cfg.archive_dir = tmp_path / "archive"
    cfg.site_dir = tmp_path / "site"
    return cfg
