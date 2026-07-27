"""
Background Worker entry point for AetherLearn.ai.

This service polls the job repository for jobs with status='queued',
and runs the LangGraph video generation pipeline asynchronously.
Because Background Workers on Render are not health-checked by HTTP probes,
running Manim and FFmpeg subprocesses here will never trigger CPU-starvation
health check timeouts or SIGTERM server restarts.
"""

import asyncio
import os
import signal
import sys
from typing import Any

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.api.v1.generation import _run_generation_pipeline
from app.core.config import get_settings
from app.core.logging_config import configure_logging, get_logger
from app.database.repositories.job_repository import JobRepository

configure_logging()
logger = get_logger("worker")

# Global flag for graceful shutdown
_shutdown_requested = False


def _signal_handler(sig: int, frame: Any) -> None:
    global _shutdown_requested
    logger.info("Shutdown signal received by worker. Finishing active task if any...", signal=sig)
    _shutdown_requested = True


async def worker_loop() -> None:
    """Main worker polling loop."""
    logger.info("Starting AetherLearn.ai Background Worker")
    settings = get_settings()

    # Initialize Firebase if configured
    if settings.use_firebase or settings.is_production:
        try:
            from app.core.firebase import initialize_firebase
            initialize_firebase()
            logger.info("Firebase initialized in worker")
        except Exception as exc:
            logger.warning("Firebase init failed in worker, falling back to local storage", error=str(exc))

    job_repo = JobRepository()

    while not _shutdown_requested:
        try:
            job = job_repo.get_next_queued()
            if job:
                job_id = job.get("id", "")
                project_id = job.get("project_id", "")
                initial_state = job.get("initial_state", {})

                logger.info(
                    "Worker picked up queued job",
                    job_id=job_id,
                    project_id=project_id,
                )

                if not initial_state:
                    logger.warning("No initial_state found in queued job, marking failed", job_id=job_id)
                    job_repo.mark_failed(job_id, "Missing initial_state in queued job document", "initialized")
                    continue

                try:
                    await _run_generation_pipeline(job_id, project_id, initial_state)
                    logger.info("Worker completed generation pipeline", job_id=job_id)
                except Exception as exc:
                    logger.exception("Worker failed executing pipeline", job_id=job_id, error=str(exc))
                    try:
                        job_repo.mark_failed(job_id, str(exc), "worker_execution")
                    except Exception:
                        pass
            else:
                # No queued jobs found, wait before polling again
                await asyncio.sleep(2.0)
        except Exception as exc:
            logger.exception("Error in worker polling loop", error=str(exc))
            await asyncio.sleep(5.0)

    logger.info("Background Worker shut down gracefully.")


def main() -> None:
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        logger.info("Worker terminated by KeyboardInterrupt")


if __name__ == "__main__":
    main()
