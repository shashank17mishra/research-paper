"""
Key Concept Extraction Module
==============================
Extracts prominent technical concepts, frameworks, and methodologies
using TF-IDF n-gram scoring, regex noun-phrase heuristics, and technical domain gazetteers.
Completely zero-cost and lightweight for GitHub Actions runners.
"""

from __future__ import annotations

import re
from typing import List, Set
from sklearn.feature_extraction.text import TfidfVectorizer

from src.fetcher import Paper
from src.utils import clean_text, setup_logger

logger = setup_logger("concepts")

# Curated high-signal technical terms and acronyms to prioritize
DOMAIN_PATTERNS = [
    r"vision transformer",
    r"latent world model",
    r"world model",
    r"world-action model",
    r"imitation learning",
    r"policy steering",
    r"scaling laws?",
    r"joint embedding(?:\s+predictive\s+architecture)?",
    r"reinforcement learning",
    r"sim-to-real(?:\s+transfer)?",
    r"robot navigation",
    r"multi-modal(?:ity)?",
    r"foundation model",
    r"diffusion model",
    r"diffusion policy",
    r"representation learning",
    r"few-shot learning",
    r"zero-shot(?:\s+learning|\s+deployment)?",
    r"self-supervised learning",
    r"graph neural network",
    r"trajectory planning",
    r"point cloud",
    r"edge computing",
    r"tinyml",
    r"low-power",
    r"on-device learning",
    r"quantization",
    r"pruning",
    r"knowledge distillation",
    r"retrieval-augmented generation",
    r"large language model",
    r"autonomous navigation",
    r"dexterous manipulation",
    r"manipulation",
    r"gaussian splatting",
    r"neural radiance field",
    r"slam",
    r"sensor fusion",
    r"domain adaptation",
    r"embodied ai",
    r"embodied intelligence",
    r"deep q-learning",
    r"actor-critic",
    r"attention mechanism",
    r"neuro-symbolic",
]

COMMON_STOPWORDS = {
    "paper", "propose", "presents", "presents a", "method", "approach", "results",
    "show", "demonstrate", "state-of-the-art", "sota", "performance", "task",
    "tasks", "study", "studies", "data", "dataset", "datasets", "model", "models",
    "system", "systems", "work", "novel", "framework", "architecture", "evaluation",
    "experimental", "experiments", "baseline", "benchmarks", "benchmark", "analysis",
    "based", "using", "via", "towards", "improved", "new", "effective", "efficient",
    "future", "recent", "existing", "first", "second", "high", "low", "different",
    "ability", "allowing", "allows", "average", "trained", "training", "checkpoints",
    "prompt", "sparse", "input", "round", "rounds", "making", "remain", "remains",
    "providing", "provides", "scale", "predict", "predictive", "agents", "human"
}


def format_concept_casing(concept: str) -> str:
    """Formats concept with proper capitalization (preserving acronyms like SLAM, IoT)."""
    special_cases = {
        "iot": "IoT",
        "tinyml": "TinyML",
        "slam": "SLAM",
        "rag": "RAG",
        "llm": "LLM",
        "jepa": "JEPA",
        "wam": "WAM",
        "nerf": "NeRF",
        "sota": "SOTA",
        "nlp": "NLP",
        "cv": "CV",
        "ai": "AI",
        "ml": "ML",
        "rl": "RL",
        "sim-to-real": "Sim-to-Real Transfer",
        "sim-to-real transfer": "Sim-to-Real Transfer",
    }
    lowered = concept.strip().lower()
    if lowered in special_cases:
        return special_cases[lowered]

    # Split words and title case while preserving special acronym components
    words = lowered.split()
    capitalized = []
    for w in words:
        if w in special_cases:
            capitalized.append(special_cases[w])
        elif w.upper() in ["3D", "2D", "RGB", "RGB-D", "UAV", "LIDAR", "IMU"]:
            capitalized.append(w.upper())
        else:
            capitalized.append(w.capitalize())
    return " ".join(capitalized)


def extract_key_concepts(paper: Paper, max_concepts: int = 5) -> List[str]:
    """
    Extracts 4 to 6 key technical concepts from a paper's title and abstract.
    Combines domain pattern recognition with TF-IDF n-gram scoring.
    """
    full_text = f"{paper.title}. {paper.abstract}".lower()
    selected: List[str] = []
    seen_lowered: Set[str] = set()

    # 1. Check curated high-value domain patterns
    for pat in DOMAIN_PATTERNS:
        match = re.search(r"\b" + pat + r"\b", full_text)
        if match:
            raw_match = match.group(0)
            formatted = format_concept_casing(raw_match)
            low = formatted.lower()
            if low not in seen_lowered:
                selected.append(formatted)
                seen_lowered.add(low)
                if len(selected) >= max_concepts:
                    paper.key_concepts = selected
                    return selected

    # 2. Extract technical n-grams via TF-IDF if more concepts needed
    corpus = [clean_text(paper.abstract)]
    try:
        tfidf = TfidfVectorizer(
            ngram_range=(2, 3),
            stop_words="english",
            max_features=25,
            token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z\-]{2,}\b"
        )
        tfidf.fit(corpus)
        features = tfidf.get_feature_names_out()

        # Score phrases based on tfidf and presence in title
        scored_phrases = []
        for feat in features:
            f_clean = feat.strip().lower()
            words = f_clean.split()
            # Skip if contains common stopwords or too short
            if any(w in COMMON_STOPWORDS for w in words):
                continue
            if len(f_clean) < 5:
                continue

            # Title occurrence bonus
            score = 1.0
            if f_clean in paper.title.lower():
                score += 2.0
            scored_phrases.append((score, f_clean))

        scored_phrases.sort(key=lambda x: x[0], reverse=True)

        for _, phrase in scored_phrases:
            formatted = format_concept_casing(phrase)
            low = formatted.lower()
            # Avoid redundant substrings (e.g. "Transformer" if "Vision Transformer" is chosen)
            if any(low in s.lower() or s.lower() in low for s in seen_lowered):
                continue
            if low not in seen_lowered:
                selected.append(formatted)
                seen_lowered.add(low)
                if len(selected) >= max_concepts:
                    break

    except Exception as exc:
        logger.debug(f"TF-IDF extraction notice for {paper.arxiv_id}: {exc}")

    # Fallback to topic category if fewer than 2 concepts found
    if len(selected) < 2:
        for cat in paper.categories:
            cat_clean = cat.replace("cs.", "").upper()
            formatted = f"{cat_clean} Architecture"
            if formatted.lower() not in seen_lowered:
                selected.append(formatted)
                seen_lowered.add(formatted.lower())

    result = selected[:max_concepts]
    paper.key_concepts = result
    return result
