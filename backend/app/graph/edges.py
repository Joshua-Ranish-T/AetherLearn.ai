"""
LangGraph conditional edge routing functions.

These pure functions inspect the current state and return the name
of the next node to execute. They contain NO business logic —
only routing decisions based on state flags.
"""

from __future__ import annotations

from app.schemas.state import VideoGenerationState


def route_after_supervisor(state: VideoGenerationState) -> str:
    """
    After the Supervisor node:
    - Route to OCR if input requires extraction
    - Route directly to content generation if input is plain text/topic
    - Route to error handler if supervisor detected an issue
    """
    if state.get("has_error"):
        return "error_handler"
    if state.get("requires_ocr"):
        return "ocr_agent"
    return "content_generation_agent"


def route_after_ocr(state: VideoGenerationState) -> str:
    """
    After the OCR Agent:
    - Route to content generation if OCR succeeded
    - Route to error handler if OCR failed
    """
    if state.get("has_error"):
        return "error_handler"
    return "content_generation_agent"


def route_after_content_generation(state: VideoGenerationState) -> str:
    """
    After Content Generation Agent:
    - Always proceed to Manim script generation
    - Route to error handler on failure
    """
    if state.get("has_error"):
        return "error_handler"
    return "manim_script_agent"


def route_after_manim_script(state: VideoGenerationState) -> str:
    """
    After Manim Script Generation Agent:
    - Proceed to execution service
    - Route to error handler on failure
    """
    if state.get("has_error"):
        return "error_handler"
    return "manim_execution_service"


def route_after_execution(state: VideoGenerationState) -> str:
    """
    After Manim Execution Service:
    - If successful: proceed to narration generation
    - If failed and retries remain: proceed to repair agent
    - If failed and retries exhausted: route to error handler
    """
    if state.get("execution_successful"):
        return "narration_agent"

    retry_count = state.get("repair_retry_count", 0)
    max_retries = state.get("max_repair_retries", 3)

    if retry_count < max_retries:
        return "repair_agent"

    return "error_handler"


def route_after_repair(state: VideoGenerationState) -> str:
    """
    After Repair Agent:
    - Always retry execution
    - Route to error handler if repair itself failed
    """
    if state.get("has_error"):
        return "error_handler"
    return "manim_execution_service"


def route_after_narration(state: VideoGenerationState) -> str:
    """
    After Narration Agent:
    - Proceed to synchronization service
    - Route to error handler on failure
    """
    if state.get("has_error"):
        return "error_handler"
    return "synchronization_service"


def route_after_synchronization(state: VideoGenerationState) -> str:
    """
    After Synchronization Service:
    - Proceed to finalization
    - Route to error handler on failure
    """
    if state.get("has_error"):
        return "error_handler"
    return "finalize"
