import re
from collections import Counter

def _tokenize(s: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z0-9_+#.]+", s.lower())
    return [t for t in tokens if len(t) > 1]

def keyword_overlap_score(text: str, reference: str) -> float:
    """Very simple heuristic: Jaccard over top keywords.
    Returns 0..1.
    """
    t1 = set(_tokenize(text))
    t2 = set(_tokenize(reference))
    if not t1 or not t2:
        return 0.0
    inter = len(t1 & t2)
    union = len(t1 | t2)
    return round(inter / union, 3)

def bounded_to_scale(val: float, lo: float = 0.0, hi: float = 1.0, scale: int = 5) -> float:
    if hi <= lo:
        return 0
    r = (val - lo) / (hi - lo)
    r = min(max(r, 0.0), 1.0)
    return round(1 + r * (scale - 1), 2)  # 1..5