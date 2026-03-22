"""SQLAlchemy ORM models for AIBench."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime

from app.database import Base


class BenchmarkLog(Base):
    """Stores each AI generation request with evaluation scores and metadata."""

    __tablename__ = "benchmark_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    input = Column(Text, nullable=False)
    response = Column(Text, nullable=False)

    # ── Evaluation scores ──────────────────────────────────
    score = Column(Float, nullable=False, default=0.0)
    semantic_score = Column(Float, nullable=False, default=0.0)
    keyword_score = Column(Float, nullable=False, default=0.0)

    # ── Performance ────────────────────────────────────────
    latency_ms = Column(Float, nullable=False, default=0.0)

    # ── Metadata ───────────────────────────────────────────
    timestamp = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    status = Column(String(16), nullable=False, default="success")
    error_log = Column(Text, nullable=True)
