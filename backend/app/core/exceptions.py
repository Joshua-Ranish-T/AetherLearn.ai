"""
Custom exception hierarchy for the AetherLearn.ai platform.

Every exception carries:
- A human-readable message
- An optional error code for API responses
- Optional structured context for logging

Usage:
    raise RenderError("Manim subprocess failed", context={"exit_code": 1})
"""

from __future__ import annotations

from http import HTTPStatus
from typing import Any


class AppError(Exception):
    """Base exception for all application-level errors."""

    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str,
        *,
        error_code: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}
        if error_code:
            self.error_code = error_code

    def to_dict(self) -> dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
        }


# ── Configuration Errors ──────────────────────────────────────────────────────

class ConfigurationError(AppError):
    """Raised when required configuration is missing or invalid."""
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code = "CONFIGURATION_ERROR"


class AuthenticationError(AppError):
    """Raised when authentication fails or token is invalid."""
    status_code = HTTPStatus.UNAUTHORIZED
    error_code = "AUTHENTICATION_ERROR"


# ── Agent Errors ──────────────────────────────────────────────────────────────

class AgentError(AppError):
    """Base class for errors raised inside LangGraph agent nodes."""
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = "AGENT_ERROR"


class SupervisorError(AgentError):
    """Raised by the Supervisor Agent."""
    error_code = "SUPERVISOR_ERROR"


class OCRError(AgentError):
    """Raised by the OCR & Content Extraction Agent."""
    error_code = "OCR_ERROR"


class ContentGenerationError(AgentError):
    """Raised by the Content Generation Agent."""
    error_code = "CONTENT_GENERATION_ERROR"


class ManimScriptError(AgentError):
    """Raised by the Manim Script Generation Agent."""
    error_code = "MANIM_SCRIPT_ERROR"


class RepairError(AgentError):
    """Raised by the Repair Agent when max retries are exhausted."""
    error_code = "REPAIR_EXHAUSTED"


class NarrationError(AgentError):
    """Raised by the Narration Agent."""
    error_code = "NARRATION_ERROR"


# ── Service Errors ────────────────────────────────────────────────────────────

class ServiceError(AppError):
    """Base class for errors raised inside service layer."""
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code = "SERVICE_ERROR"


class RenderError(ServiceError):
    """Raised when the Manim execution service fails."""
    error_code = "RENDER_ERROR"


class SynchronizationError(ServiceError):
    """Raised when FFmpeg synchronization fails."""
    error_code = "SYNC_ERROR"


class TTSError(ServiceError):
    """Raised when text-to-speech generation fails."""
    error_code = "TTS_ERROR"


class StorageError(ServiceError):
    """Raised when Firebase Storage upload/download fails."""
    error_code = "STORAGE_ERROR"


# ── Database Errors ───────────────────────────────────────────────────────────

class DatabaseError(AppError):
    """Base class for Firestore operation errors."""
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code = "DATABASE_ERROR"


class NotFoundError(DatabaseError):
    """Raised when a requested document does not exist in Firestore."""
    status_code = HTTPStatus.NOT_FOUND
    error_code = "NOT_FOUND"


class DuplicateError(DatabaseError):
    """Raised when a document with the same ID already exists."""
    status_code = HTTPStatus.CONFLICT
    error_code = "DUPLICATE"


# ── API / Validation Errors ───────────────────────────────────────────────────

class ValidationError(AppError):
    """Raised when input validation fails at the API layer."""
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = "VALIDATION_ERROR"


class InputError(AppError):
    """Raised when user-provided input is invalid or unsupported."""
    status_code = HTTPStatus.BAD_REQUEST
    error_code = "INPUT_ERROR"


class UnsupportedInputTypeError(InputError):
    """Raised when an unsupported file type is uploaded."""
    error_code = "UNSUPPORTED_INPUT_TYPE"
