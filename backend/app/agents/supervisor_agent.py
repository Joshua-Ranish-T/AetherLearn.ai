"""
Supervisor Agent — Entry point of the LangGraph workflow.

Responsibilities:
- Validate user input
- Determine input type and routing flags
- Set up render configuration
- Detect whether OCR extraction is required
- Update project/job status in Firestore
"""

from __future__ import annotations

from app.core.exceptions import SupervisorError, InputError
from app.core.logging_config import get_logger
from app.database.repositories.job_repository import JobRepository
from app.database.repositories.project_repository import ProjectRepository
from app.schemas.content import InputType
from app.schemas.state import VideoGenerationState

logger = get_logger(__name__)

# Input types that require OCR processing
OCR_REQUIRED_TYPES = {
    InputType.PDF.value,
    InputType.IMAGE.value,
    InputType.SCREENSHOT.value,
    InputType.HANDWRITTEN.value,
}

# Input types that work directly with text
TEXT_INPUT_TYPES = {
    InputType.TEXT.value,
    InputType.TOPIC.value,
}


class SupervisorAgent:
    """
    Entry point supervisor that orchestrates workflow routing.
    Runs synchronously as a LangGraph node.
    """

    def __init__(self) -> None:
        self._project_repo = ProjectRepository()
        self._job_repo = JobRepository()

    def run(self, state: VideoGenerationState) -> dict:
        """
        Validate input and set routing flags.

        Returns:
            Partial state update dict.
        """
        project_id = state.get("project_id", "")
        job_id = state.get("job_id", "")
        input_type = state.get("input_type", "")

        logger.info(
            "Supervisor executing",
            project_id=project_id,
            input_type=input_type,
        )

        # ── Validate input type ────────────────────────────────────────────
        valid_types = {t.value for t in InputType}
        if input_type not in valid_types:
            raise InputError(
                f"Unsupported input type: '{input_type}'. "
                f"Supported: {', '.join(valid_types)}",
                context={"input_type": input_type},
            )

        # ── Validate content ───────────────────────────────────────────────
        if input_type in TEXT_INPUT_TYPES:
            input_text = state.get("input_text", "").strip()
            if not input_text:
                raise InputError(
                    "Input text cannot be empty for text/topic input types.",
                    context={"input_type": input_type},
                )
            if len(input_text) < 10:
                raise InputError(
                    "Input text is too short. Please provide at least 10 characters.",
                    context={"length": len(input_text)},
                )

        elif input_type in OCR_REQUIRED_TYPES:
            input_file_path = state.get("input_file_path", "")
            input_file_url = state.get("input_file_url", "")
            if not input_file_path and not input_file_url:
                raise InputError(
                    f"A file path or URL is required for input type '{input_type}'.",
                    context={"input_type": input_type},
                )

        # ── Determine routing flags ────────────────────────────────────────
        requires_ocr = input_type in OCR_REQUIRED_TYPES

        # ── Update job status in Firestore ─────────────────────────────────
        if job_id:
            try:
                self._job_repo.update_stage(job_id, "supervisor")
                self._job_repo.append_log(
                    job_id,
                    {
                        "stage": "supervisor",
                        "status": "completed",
                        "message": f"Input validated. Type: {input_type}. OCR required: {requires_ocr}",
                    },
                )
            except Exception as exc:
                logger.warning("Failed to update job in supervisor", error=str(exc))

        if project_id:
            try:
                self._project_repo.update_status(project_id, "running")
            except Exception as exc:
                logger.warning("Failed to update project status", error=str(exc))

        logger.info(
            "Supervisor completed",
            requires_ocr=requires_ocr,
            input_type=input_type,
        )

        return {
            "requires_ocr": requires_ocr,
            "current_stage": "supervisor",
            "has_error": False,
        }
