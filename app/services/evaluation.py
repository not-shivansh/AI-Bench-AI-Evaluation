"""
Scorix AI — Hybrid Evaluation Engine (Production Ready)

Rule-based + NLP-based metrics.

Metrics:
    - semantic_similarity
    - keyword_relevance
    - coherence_score
    - length_score
    - error_score
"""

import re
import logging
from dataclasses import dataclass

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# ---------------------------
# GLOBAL MODEL (LAZY LOAD)
# ---------------------------
_model: SentenceTransformer | None = None

# ---------------------------
# ERROR PATTERNS
# ---------------------------
_ERROR_PATTERNS = [
    r"i'm sorry",
    r"i cannot",
    r"i can't",
    r"as an ai",
    r"i don't have access",
    r"error",
    r"unable to",
]

# ---------------------------
# WEIGHTS
# ---------------------------
WEIGHT_SEMANTIC = 0.30
WEIGHT_KEYWORD = 0.20
WEIGHT_COHERENCE = 0.20
WEIGHT_LENGTH = 0.15
WEIGHT_ERROR = 0.15


# ---------------------------
# DATA CLASS
# ---------------------------
@dataclass
class EvaluationResult:
    semantic_score: float
    keyword_score: float
    coherence_score: float
    length_score: float
    error_score: float
    final_score: float


# ---------------------------
# TEXT CLEANER (CRITICAL FIX)
# ---------------------------
def _clean_text(x):
    if x is None:
        return ""
    if isinstance(x, float):
        return ""
    return str(x).strip()


# ---------------------------
# LOAD MODEL
# ---------------------------
def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("Loading sentence-transformer model (first request may be slow)…")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


# ---------------------------
# RULE-BASED METRICS
# ---------------------------
def _length_score(response: str) -> float:
    response = _clean_text(response)

    length = len(response)
    if length == 0:
        return 0.0
    if length < 50:
        return length / 50.0
    if length <= 500:
        return 1.0
    return max(0.5, 1.0 - (length - 500) / 2000.0)


def _error_score(response: str) -> float:
    response = _clean_text(response)
    lower = response.lower()

    for pattern in _ERROR_PATTERNS:
        if re.search(pattern, lower):
            return 0.0
    return 1.0


# ---------------------------
# NLP METRICS
# ---------------------------
def _semantic_similarity(input_text: str, response: str) -> float:
    input_text = _clean_text(input_text)
    response = _clean_text(response)

    if not input_text or not response:
        return 0.0

    model = _get_model()

    try:
        embeddings = model.encode([input_text, response])
        sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return float(np.clip(sim, 0.0, 1.0))
    except Exception as e:
        logger.warning(f"Semantic similarity failed: {e}")
        return 0.0


def _keyword_relevance(input_text: str, response: str) -> float:
    input_text = _clean_text(input_text)
    response = _clean_text(response)

    input_words = set(
        w.lower() for w in re.findall(r"\b\w+\b", input_text) if len(w) >= 3
    )

    if not input_words:
        return 1.0

    response_lower = response.lower()
    matches = sum(1 for w in input_words if w in response_lower)

    return matches / len(input_words)


def _coherence_score(response: str) -> float:
    response = _clean_text(response)

    sentences = [
        s.strip()
        for s in re.split(r"[.!?]+", response)
        if len(s.strip()) > 10
    ]

    if len(sentences) < 2:
        return 1.0

    model = _get_model()

    try:
        embeddings = model.encode(sentences)

        similarities = []
        for i in range(len(embeddings) - 1):
            sim = cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
            similarities.append(float(sim))

        return float(np.clip(np.mean(similarities), 0.0, 1.0))

    except Exception as e:
        logger.warning(f"Coherence calculation failed: {e}")
        return 0.0


# ---------------------------
# MAIN EVALUATION FUNCTION
# ---------------------------
def evaluate(input_text: str, response: str) -> EvaluationResult:
    input_text = _clean_text(input_text)
    response = _clean_text(response)

    if not input_text or not response:
        return EvaluationResult(0, 0, 0, 0, 0, 0)

    semantic = _semantic_similarity(input_text, response)
    keyword = _keyword_relevance(input_text, response)
    coherence = _coherence_score(response)
    length = _length_score(response)
    error = _error_score(response)

    final = (
        WEIGHT_SEMANTIC * semantic
        + WEIGHT_KEYWORD * keyword
        + WEIGHT_COHERENCE * coherence
        + WEIGHT_LENGTH * length
        + WEIGHT_ERROR * error
    )

    final = round(final, 4)

    logger.info(
        "Evaluation → sem=%.3f  kw=%.3f  coh=%.3f  len=%.3f  err=%.3f  final=%.4f",
        semantic, keyword, coherence, length, error, final,
    )

    return EvaluationResult(
        semantic_score=round(semantic, 4),
        keyword_score=round(keyword, 4),
        coherence_score=round(coherence, 4),
        length_score=round(length, 4),
        error_score=round(error, 4),
        final_score=final,
    )