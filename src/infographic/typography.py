"""
Editorial Typography Engine
===========================
Configures font styling, hierarchy, plain-language text synthesis,
and line wrapping for the editorial research publication layout.
"""

from __future__ import annotations

import re
from typing import Dict, List
import matplotlib.font_manager as fm

# Matplotlib Font Configuration (Arial / DejaVu first to avoid font warnings on Windows/CI)
SERIF_FAMILY = ["Georgia", "DejaVu Serif", "Times New Roman", "serif"]
SANS_FAMILY = ["Arial", "DejaVu Sans", "sans-serif"]


def get_serif_prop(
    size: float = 12,
    weight: str = "normal",
    style: str = "normal"
) -> fm.FontProperties:
    """Returns FontProperties for classic high-contrast editorial serif."""
    return fm.FontProperties(
        family=SERIF_FAMILY,
        size=size,
        weight=weight,
        style=style
    )


def get_sans_prop(
    size: float = 10,
    weight: str = "normal",
    style: str = "normal"
) -> fm.FontProperties:
    """Returns FontProperties for clean editorial sans-serif metadata."""
    return fm.FontProperties(
        family=SANS_FAMILY,
        size=size,
        weight=weight,
        style=style
    )


def wrap_text_lines(text: str, max_chars: int = 50, max_lines: int = 3) -> str:
    """
    Wraps text cleanly into multiple lines with a soft character threshold per line
    and limits the total number of lines with an ellipsis.
    """
    if not text:
        return ""
    words = text.split()
    lines: List[str] = []
    current_line: List[str] = []
    current_len = 0

    for w in words:
        if current_len + len(w) + 1 > max_chars:
            lines.append(" ".join(current_line))
            if len(lines) >= max_lines:
                current_line = []
                break
            current_line = [w]
            current_len = len(w)
        else:
            current_line.append(w)
            current_len += len(w) + 1

    if current_line and len(lines) < max_lines:
        lines.append(" ".join(current_line))

    joined = "\n".join(lines)
    if len(" ".join(words)) > len(joined.replace("\n", " ")):
        if not joined.endswith("..."):
            joined = joined.rstrip(".,;: ") + "..."
    return joined


def synthesize_plain_explanation(title: str, abstract: str, topic: str) -> str:
    """
    Synthesizes a 2-3 sentence plain-language explanation of WHAT the research does
    and HOW it accomplishes it, translating academic jargon into readable editorial prose.
    """
    clean_abs = " ".join(abstract.split())
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean_abs) if s.strip()]

    what_part = ""
    how_part = ""

    for s in sentences:
        s_low = s.lower()
        if any(k in s_low for k in ["we propose", "we present", "we introduce", "this work develops", "our method", "st-locovit", "microquant", "consensusnet"]):
            what_part = s.strip()
            break

    if not what_part and len(sentences) > 0:
        what_part = sentences[0]

    # Clean academic self-referential filler phrases into readable editorial style
    jargon_prefixes = [
        r"^in this paper,?\s*(we\s+(propose|present|introduce|develop)\s+)?",
        r"^in this work,?\s*(we\s+(propose|present|introduce|develop)\s+)?",
        r"^we (propose|present|introduce|develop)\s+",
        r"^to overcome this fundamental bottleneck,?\s*(we\s+(develop|propose)\s+)?",
        r"^to address this issue,?\s*(we\s+(propose|introduce)\s+)?",
    ]
    cleaned_what = what_part
    for pat in jargon_prefixes:
        cleaned_what = re.sub(pat, "A new ", cleaned_what, flags=re.IGNORECASE)
    cleaned_what = re.sub(r"^a new a new\b", "A new", cleaned_what, flags=re.IGNORECASE)
    if cleaned_what:
        cleaned_what = cleaned_what[0].upper() + cleaned_what[1:]

    # Append second sentence only if the first is short enough to fit cleanly without truncation
    combined = cleaned_what
    if len(cleaned_what) < 130:
        for s in sentences:
            s_low = s.lower()
            if any(k in s_low for k in ["experiments show", "demonstrates", "achieves", "reduces", "improves", "enables", "our key innovation"]):
                if s != what_part:
                    how_part = s.strip()
                    break
        if how_part and (len(combined) + len(how_part) < 210):
            combined = f"{combined} {how_part}".strip()

    combined = re.sub(r"\[\d+\]", "", combined)
    combined = re.sub(r"\\(?:cite|ref)\{[^}]+\}", "", combined)

    return wrap_text_lines(combined, max_chars=48, max_lines=4)


def synthesize_why_it_matters(insights: Dict[str, str], topic: str) -> str:
    """Synthesizes a short, punchy 1-sentence 'Why it matters' editorial statement."""
    apps = insights.get("applications", "")
    innov = insights.get("key_innovation", "")

    if "robot" in topic.lower() or "manipulat" in apps.lower() or "quadruped" in apps.lower():
        return "Helps robots move smarter and navigate reliably in complex spaces."
    elif "iot" in topic.lower() or "edge" in apps.lower() or "quantiz" in innov.lower():
        return "Smarter AI that works on small devices with far less battery power."
    elif "multi-agent" in topic.lower() or "warehouse" in apps.lower() or "swarm" in apps.lower() or "deadlock" in innov.lower():
        return "Better autonomous coordination for smarter, more efficient factories."
    elif "vision" in topic.lower():
        return "Enables cameras to understand and react to 3D scenes in real time."
    elif "nlp" in topic.lower() or "language" in topic.lower():
        return "Provides grounded and reliable reasoning for complex AI agents."
    else:
        return "Paves the way for practical, scalable deployment in real environments."
