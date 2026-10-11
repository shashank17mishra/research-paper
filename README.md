# Daily Tech Intelligence

> **Autonomous Technical Research Intelligence System**  
> Researches, analyzes, synthesizes, visualizes, and publishes state-of-the-art AI, ML, Robotics, and IoT papers every day at **₹0/month cost**.

[![Daily Research Workflow](https://github.com/shashank17mishra/research-paper/actions/workflows/daily-research.yml/badge.svg)](https://github.com/shashank17mishra/research-paper/actions/workflows/daily-research.yml)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Cost: ₹0/month](https://img.shields.io/badge/Cost-%E2%82%B90%2Fmonth-brightgreen.svg)
![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)

---

## Latest Report

📅 **[11 October 2026 Report](reports/2026/10/11/report.md)** — *10 new breakthrough papers analyzed today.*

[Read Full Report →](reports/2026/10/11/report.md) | [Explore Interactive Dashboard →](site/index.html)

[![Daily Infographic](reports/2026/10/11/infographic.png)](reports/2026/10/11/infographic.png)

---

## Today's Statistics

| Metric | Count |
| :--- | :---: |
| **Papers Analyzed Today** | `10` |
| **Artificial Intelligence (AI)** | `4` |
| **Machine Learning (ML)** | `4` |
| **Robotics** | `5` |
| **IoT & Edge AI** | `0` |

---

## Latest Research

| # | Paper Title | Topic | Relevance | Link |
| :-: | :--- | :---: | :-: | :---: |
| 1 | **Which Skill to Distill? SGUID: Selecting a Compact Skill Bank for Model-...** | `Machine Learning` | `0.65` | [arXiv](https://arxiv.org/abs/2610.12367v1) |
| 2 | **HRIL: Learning Multimodal Synergy via Higher-Order Tensor Modeling** | `Machine Learning` | `0.65` | [arXiv](https://arxiv.org/abs/2610.12393v1) |
| 3 | **FAITH: Feasibility-Aware Safety-Filtered RL for High-Dimensional Systems** | `Robotics` | `0.65` | [arXiv](https://arxiv.org/abs/2610.12432v1) |
| 4 | **OmniCapBench: A Deep-Structured Evaluation Framework for Fine-Grained Au...** | `Artificial Intelligence` | `0.65` | [arXiv](https://arxiv.org/abs/2610.12458v1) |
| 5 | **Embodied Turing Machines: Stateful Code for Robot Recursive Self-Improve...** | `Robotics` | `0.66` | [arXiv](https://arxiv.org/abs/2610.12369v1) |

---

## Project Statistics

- **Total Papers Analyzed**: `38`
- **Total Operational Runs**: `16 days`
- **Categories Tracked**: `9 categories`
- **Primary Focus Areas**: Robotics, Artificial Intelligence, Machine Learning, IoT & Edge AI

---

## Architecture

```mermaid
flowchart TD
    A[Daily Cron Schedule: 01:00 UTC] --> B[arXiv Official API]
    B --> C[Candidate Ingestion cs.AI, cs.LG, cs.RO, cs.DC]
    C --> D{Duplicate Filter: data/papers.json}
    D -->|New Paper| E[Relevance Scorer & Ranker]
    D -->|Seen| X[Skip]
    E --> F[Top 10 Papers Selection]
    F --> G[Extractive NLP Summarizer]
    F --> H[TF-IDF Key Concept Extractor]
    F --> I[Technical Insights Generator]
    G & H & I --> J[Daily Markdown Report]
    G & H & I --> K[Matplotlib + Pillow Infographic]
    J & K --> L[Archive & Statistics Ledger Update]
    L --> M[Update README & GitHub Pages]
    M --> N[Autonomous Git Commit & Push]
```

---

## Automation

The system runs entirely autonomously via **GitHub Actions** (`.github/workflows/daily-research.yml`):
- **Schedule**: Scheduled daily at `01:00 UTC` (~`06:30 AM IST`).
- **Zero Manual Intervention**: Ingests, analyzes, generates infographics, updates data, and commits automatically.
- **Zero Cost (₹0/month)**: Free GitHub Actions runners, free arXiv API, open-source Python NLP, and GitHub Pages.
- **Manual Triggers**: Supports `workflow_dispatch` for on-demand execution and `--dry-run` testing.

---

## Repository Structure

```text
daily-tech-intelligence/
├── .github/
│   └── workflows/
│       └── daily-research.yml
├── archive/
│   ├── 2026/
│   │   └── 10/
│   └── index.json
├── assets/
│   └── illustrations/
│       ├── ed_book_stack.png
│       ├── ed_chip.png
│       ├── ed_quadruped.png
│       ├── ed_warehouse.png
│       ├── mod_chip.png
│       ├── mod_header_laptop.png
│       ├── mod_quadruped.png
│       ├── mod_warehouse.png
│       ├── researcher_laptop.png
│       ├── vignette_01_search.png
│       ├── vignette_02_notes.png
│       ├── vignette_03_code.png
│       ├── vignette_04_rain.png
│       ├── vignette_05_read.png
│       ├── vignette_06_coffee.png
│       ├── vignette_07_dog.png
│       ├── vignette_08_plant.png
│       └── walking_figure.png
├── config/
│   ├── config.yaml
│   └── topics.yaml
├── data/
│   ├── papers.json
│   └── statistics.json
├── reports/
```

---

## Local Development

```bash
# 1. Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run dry run pipeline (fetches and processes without committing)
python src/main.py --dry-run

# 4. Run tests
pytest tests/
```

---

## License

This project is licensed under the [MIT License](LICENSE).
