"""Lightweight normalization helpers for symptom text."""
import re
import unicodedata


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("Input text must be a string.")
    text = unicodedata.normalize("NFKC", text).lower().replace("-", " ")
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> list[str]:
    return normalize_text(text).split()
