"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from pydantic import BaseModel, Field


# ── Requests ───────────────────────────────────────────────

class GenerateRequest(BaseModel):
    """Body for POST /generate."""
    input: str = Field(..., min_length=1, description="The prompt to send to the AI model")


# ── Responses ──────────────────────────────────────────────

class GenerateResponse(BaseModel):
    """Response from POST /generate."""
    id: int
    input: str
    response: str
    score: float
    semantic_score: float
    keyword_score: float
    latency_ms: float
    timestamp: datetime
    status: str

    model_config = {"from_attributes": True}


class HistoryItem(BaseModel):
    """Single item in GET /history response."""
    id: int
    input: str
    response: str
    score: float
    semantic_score: float
    keyword_score: float
    latency_ms: float
    timestamp: datetime
    status: str
    error_log: str | None = None

    model_config = {"from_attributes": True}


class MetricsResponse(BaseModel):
    """Aggregated statistics from GET /metrics."""
    average_score: float
    average_latency: float
    total_requests: int
