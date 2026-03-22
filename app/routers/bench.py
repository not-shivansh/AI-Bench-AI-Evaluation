"""API routes for the AIBench benchmarking platform."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import BenchmarkLog
from app.schemas import GenerateRequest, GenerateResponse, HistoryItem, MetricsResponse
from app.services.groq_service import generate_response as generate_local
from app.services.evaluation import evaluate

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
@router.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest, db: Session = Depends(get_db)):
    try:
        import time

        # 🔥 Generate from local model
        start = time.time()
        response_text = generate_local(request.input)
        latency_ms = (time.time() - start) * 1000

        # 🔥 Evaluate response
        scores = evaluate(request.input, response_text)

        # 🔥 Save to DB
        log = BenchmarkLog(
            input=request.input,
            response=response_text,
            score=scores.final_score,   
            semantic_score=scores.semantic_score,
            keyword_score=scores.keyword_score,
            latency_ms=latency_ms,
            timestamp=datetime.now(timezone.utc),
            status="success",
        )

        db.add(log)
        db.commit()
        db.refresh(log)

        return log

    except Exception as exc:
        logger.exception("Error during generation pipeline")

        error_log = BenchmarkLog(
            input=request.input,
            response="",
            score=0.0,
            semantic_score=0.0,
            keyword_score=0.0,
            latency_ms=0.0,
            timestamp=datetime.now(timezone.utc),
            status="failure",
            error_log=str(exc),
        )

        db.add(error_log)
        db.commit()

        raise HTTPException(status_code=500, detail=f"Generation failed: {exc}") from exc


@router.get("/history", response_model=list[HistoryItem])
def history(db: Session = Depends(get_db)):
    """Return all benchmark logs ordered by most recent first."""
    logs = (
        db.query(BenchmarkLog)
        .order_by(BenchmarkLog.timestamp.desc())
        .all()
    )
    return logs


@router.get("/metrics", response_model=MetricsResponse)
def metrics(db: Session = Depends(get_db)):
    """Return aggregated benchmarking statistics."""
    result = db.query(
        func.avg(BenchmarkLog.score).label("average_score"),
        func.avg(BenchmarkLog.latency_ms).label("average_latency"),
        func.count(BenchmarkLog.id).label("total_requests"),
    ).one()

    return MetricsResponse(
        average_score=round(result.average_score or 0.0, 4),
        average_latency=round(result.average_latency or 0.0, 2),
        total_requests=result.total_requests or 0,
    )
