"""AIBench – FastAPI application entry point."""

import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import init_db
from app.routers import bench

# ── Paths ──────────────────────────────────────────────────
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

# ── Logging ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ───────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Initializing database…")
        init_db()
        logger.info("✅ DB connected")
    except Exception as e:
        logger.warning(f"⚠️ DB skipped: {e}")

    yield

# ── App ────────────────────────────────────────────────────
app = FastAPI(
    title="AIBench",
    description="AI API Playground & Benchmarking Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS – allow all origins during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes (must come before static files mount)
app.include_router(bench.router, prefix="/api", tags=["Benchmarking"])


@app.get("/health")
def health():
    """Health-check endpoint."""
    return {"status": "ok", "service": "AIBench"}


@app.get("/")
def serve_frontend():
    """Serve the dashboard."""
    return FileResponse(FRONTEND_DIR / "index.html")


# Mount static assets (CSS, JS) – explicit routes above take priority
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
