"""Natural-language processing components."""
from .normalizer import normalize_text, tokenize
from .evidence_extractor import extract_evidence

__all__ = ["normalize_text", "tokenize", "extract_evidence"]
