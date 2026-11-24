"""Phrase-based symptom evidence extraction with negation and uncertainty.

This is deliberately transparent lightweight NLP, not a general language model.
Only phrases present in the supplied symptom dictionary can become evidence.
"""
from __future__ import annotations

import re
from typing import Mapping

from .normalizer import normalize_text

NEGATION_WORDS = {"no", "not", "never", "without", "isnt", "aren't", "isn't"}
UNCERTAINTY_WORDS = {"maybe", "perhaps", "possibly", "might", "may", "unsure", "uncertain", "think"}
NEGATION_PATTERNS = (
    re.compile(r"\b(?:does|do|did|is|are|was|were|has|have|had)\s+not\s+$"),
    re.compile(r"\b(?:no|not|never|without|isnt|isn't|aren't)\s+(?:any\s+)?$"),
    re.compile(r"\b(?:doesn't|don't|didn't|isn't|aren't|wasn't|weren't)\s+$"),
)
UNCERTAINTY_PATTERN = re.compile(r"\b(?:maybe|perhaps|possibly|might|may|unsure|uncertain|think|appears to be)\b")


def _status(text: str, start: int) -> str:
    prefix = text[max(0, start - 60):start]
    if UNCERTAINTY_PATTERN.search(prefix):
        return "uncertain"
    if any(pattern.search(prefix) for pattern in NEGATION_PATTERNS):
        return "negative"
    # Handle short standalone negation words immediately before the phrase.
    words = prefix.split()
    if words and words[-1] in NEGATION_WORDS:
        return "negative"
    return "positive"


def extract_evidence(text: str, phrase_map: Mapping[str, str]) -> dict:
    normalized = normalize_text(text)
    matches = []
    occupied = []
    # Prefer longer phrases, then record all distinct occurrences.
    phrases = sorted(phrase_map.items(), key=lambda item: len(normalize_text(item[0])), reverse=True)
    for phrase, canonical in phrases:
        phrase_norm = normalize_text(phrase)
        if not phrase_norm:
            continue
        pattern = re.compile(r"(?<![a-z0-9])" + re.escape(phrase_norm) + r"(?![a-z0-9])")
        for match in pattern.finditer(normalized):
            span = (match.start(), match.end())
            if any(span[0] < end and start < span[1] for start, end in occupied):
                continue
            occupied.append(span)
            matches.append({
                "phrase": phrase,
                "fact": canonical,
                "status": _status(normalized, match.start()),
                "start": match.start(),
                "end": match.end(),
            })
    matches.sort(key=lambda item: item["start"])
    positive = sorted({item["fact"] for item in matches if item["status"] == "positive"})
    negative = sorted({item["fact"] for item in matches if item["status"] == "negative"})
    uncertain = sorted({item["fact"] for item in matches if item["status"] == "uncertain"})
    contradictions = sorted(set(positive) & set(negative))
    # Conflicted facts are withheld from confirmed positive evidence.
    confirmed = sorted(set(positive) - set(contradictions))
    return {
        "normalized_text": normalized,
        "mentions": matches,
        "positive_facts": positive,
        "negative_facts": negative,
        "uncertain_facts": uncertain,
        "contradictions": contradictions,
        "confirmed_facts": confirmed,
        "unknown_input": not bool(matches),
    }
