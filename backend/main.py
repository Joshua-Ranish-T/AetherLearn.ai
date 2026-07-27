"""
AetherLearn.ai Platform — FastAPI Application Entry Point.

Startup sequence:
1. Configure logging
2. Initialize Firebase (Firestore + Storage)
3. Initialize LangGraph compiled graph
4. Mount API router
5. Register exception handlers

Usage:
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import shutil
import sys
from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging_config import configure_logging, get_logger

settings = get_settings()

# Configure structured logging before anything else
configure_logging(
    log_level=settings.log_level,
    json_logs=settings.is_production,
)

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Startup / Shutdown Lifespan
# ─────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan — run startup checks, init Firebase, warm up graph."""
    logger.info(
        "Starting AetherLearn.ai Platform",
        version=settings.app_version,
        env=settings.app_env,
    )

    # ── System dependency checks ───────────────────────────────────────────
    _check_system_dependencies()

    # ── Firebase initialization ────────────────────────────────────────────
    try:
        from app.core.firebase import initialize_firebase
        initialize_firebase()
    except Exception as exc:
        logger.error("Firebase initialization failed or disabled", error=str(exc))
        logger.warning("Running in Local Development Mode (local JSON & disk storage)")

    # ── Create render output directory ─────────────────────────────────────
    settings.render_output_path.mkdir(parents=True, exist_ok=True)
    logger.info("Render output directory ready", path=str(settings.render_output_path))

    # ── Pre-warm LangGraph ─────────────────────────────────────────────────
    try:
        from app.graph.builder import get_graph
        get_graph()
        logger.info("LangGraph compiled and ready")
    except Exception as exc:
        logger.error("LangGraph initialization failed", error=str(exc))

    logger.info("AetherLearn.ai Platform is ready", host=settings.api_host, port=settings.api_port)

    yield  # ── Application runs here ──────────────────────────────────────

    # ── Cleanup ────────────────────────────────────────────────────────────
    logger.info("Shutting down AetherLearn.ai Platform")
    try:
        from app.core.firebase import shutdown_firebase
        shutdown_firebase()
    except Exception:
        pass


def _check_system_dependencies() -> None:
    """Verify that required system tools (Manim, FFmpeg) are available."""
    if shutil.which("manim"):
        logger.info("manim found", path=shutil.which("manim"))
    else:
        logger.warning("manim not found in PATH", hint="Manim CE — required for video rendering. Install: pip install manim")

    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        try:
            import imageio_ffmpeg
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass

    if ffmpeg_path:
        logger.info("ffmpeg found", path=ffmpeg_path)
    else:
        logger.warning("ffmpeg not found in PATH", hint="FFmpeg — required for video/audio sync. Install from ffmpeg.org")


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI Application Factory
# ─────────────────────────────────────────────────────────────────────────────

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "AI-Powered Educational Video Generation Platform. "
            "Converts educational content into fully narrated Manim videos "
            "through an intelligent multi-agent LangGraph workflow."
        ),
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────
    allow_all_origins = "*" in settings.cors_origins
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins if not allow_all_origins else [],
        allow_origin_regex=".*" if allow_all_origins else r"https://.*\.vercel\.app|https://.*\.onrender\.com|http://localhost:.*|http://127\.0\.0\.1:.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────
    application.include_router(api_router)

    # ── Static Files ──────────────────────────────────────────────────────
    from fastapi.staticfiles import StaticFiles
    import os
    storage_dir = os.path.join(os.getcwd(), "data", "storage")
    os.makedirs(storage_dir, exist_ok=True)
    application.mount("/storage", StaticFiles(directory=storage_dir), name="storage")

    # ── Exception Handlers ────────────────────────────────────────────────
    @application.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "Application error",
            error_code=exc.error_code,
            message=exc.message,
            path=str(request.url),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
        )

    @application.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception", path=str(request.url))
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content={
                "error_code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
                "context": {},
            },
        )

    # ── Health Check ──────────────────────────────────────────────────────
    @application.get("/health", tags=["Health"])
    async def health_check() -> dict:
        return {
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.app_env,
        }

    @application.get("/", tags=["Root"])
    async def root() -> dict:
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health",
        }

    return application


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
