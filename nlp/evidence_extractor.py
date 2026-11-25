"""Transparent symptom phrase matching with negation and uncertainty handling.

This module is intentionally offline and deterministic. It recognizes curated
phrases and safe plural variants; it does not pretend to understand every
possible English sentence.
"""
from __future__ import annotations

import re
from typing import Mapping

from .normalizer import normalize_text

NEGATION_WORDS = {"no", "not", "never", "without", "isnt", "aren't", "isn't", "doesn't", "don't", "didn't"}
UNCERTAINTY_PATTERN = re.compile(
    r"\b(?:maybe|perhaps|possibly|might|may|unsure|uncertain|not sure|"
    r"i think|i guess|seems like|appears to be|could be)\b"
)
NEGATION_PATTERNS = (
    re.compile(r"\b(?:does|do|did|is|are|was|were|has|have|had)\s+not\s+$"),
    re.compile(r"\b(?:no|not|never|without)\s+(?:any\s+)?$"),
    re.compile(r"\b(?:doesn't|don't|didn't|isn't|aren't|wasn't|weren't)\s+$"),
)


def _status(text: str, start: int) -> str:
    prefix = text[max(0, start - 80):start]
    # Negation takes priority over uncertainty when both are present.
    if any(pattern.search(prefix) for pattern in NEGATION_PATTERNS):
        return "negative"
    words = prefix.split()
    if words and words[-1] in NEGATION_WORDS:
        return "negative"
    if UNCERTAINTY_PATTERN.search(prefix):
        return "uncertain"
    return "positive"


def _phrase_variants(phrase: str) -> set[str]:
    """Create conservative singular/plural variants for a known phrase."""
    phrase = normalize_text(phrase)
    variants = {phrase}
    words = phrase.split()
    if not words:
        return variants
    last = words[-1]
    candidates = {last}
    if last.endswith("ies") and len(last) > 3:
        candidates.add(last[:-3] + "y")
    if last.endswith("es") and len(last) > 3:
        candidates.add(last[:-2])
    elif last.endswith("s") and not last.endswith("ss") and len(last) > 3:
        candidates.add(last[:-1])
    else:
        candidates.add(last + ("es" if last.endswith(("s", "x", "ch", "sh")) else "s"))
    for candidate in candidates:
        variants.add(" ".join(words[:-1] + [candidate]))
    return variants


def extract_evidence(text: str, phrase_map: Mapping[str, str]) -> dict:
    normalized = normalize_text(text)
    matches = []
    occupied = []
    expanded = []
    for phrase, canonical in phrase_map.items():
        for variant in _phrase_variants(phrase):
            if variant:
                expanded.append((variant, canonical, phrase))
    # Prefer longer phrases to prevent a short alias from stealing a match.
    expanded.sort(key=lambda item: len(item[0]), reverse=True)
    seen = set()
    for phrase_norm, canonical, original_phrase in expanded:
        pattern = re.compile(r"(?<![a-z0-9])" + re.escape(phrase_norm) + r"(?![a-z0-9])")
        for match in pattern.finditer(normalized):
            span = (match.start(), match.end())
            if any(span[0] < end and start < span[1] for start, end in occupied):
                continue
            key = (span, canonical)
            if key in seen:
                continue
            seen.add(key)
            occupied.append(span)
            matches.append({
                "phrase": original_phrase,
                "matched_text": match.group(0),
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
