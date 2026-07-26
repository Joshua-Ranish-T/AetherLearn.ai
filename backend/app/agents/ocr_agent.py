"""
OCR & Content Extraction Agent.

Responsibilities:
- Handle PDF, image, screenshot, and handwritten note inputs
- Extract: text, equations, tables, code blocks, figures
- Return structured ExtractedContent

Supports:
- PyMuPDF for PDF text extraction
- Tesseract (primary) + EasyOCR (fallback) for images
"""

from __future__ import annotations

import os
from pathlib import Path

from app.core.exceptions import OCRError
from app.core.logging_config import get_logger
from app.schemas.content import ContentChunk, ExtractedContent, InputType
from app.schemas.state import VideoGenerationState
from app.services.ocr_service import OCRService

logger = get_logger(__name__)


class OCRAgent:
    """
    OCR & Content Extraction Agent.

    Delegates actual OCR work to OCRService and returns
    a structured ExtractedContent object.
    """

    def __init__(self) -> None:
        self._ocr_service = OCRService()

    def run(self, state: VideoGenerationState) -> dict:
        """
        Extract content from the input file.

        Returns:
            Partial state update with extracted_content.
        """
        input_type = state.get("input_type", "")
        input_file_path = state.get("input_file_path", "")
        input_file_url = state.get("input_file_url", "")

        logger.info(
            "OCR agent executing",
            input_type=input_type,
            file_path=input_file_path,
        )

        # Resolve file path (download from storage if only URL available)
        file_path = self._resolve_file_path(input_file_path, input_file_url)

        if not file_path or not os.path.exists(file_path):
            raise OCRError(
                f"Input file not found: {file_path}",
                context={"input_file_path": input_file_path, "resolved": file_path},
            )

        # ── Dispatch to appropriate extractor ────────────────────────────
        try:
            if input_type == InputType.PDF.value:
                extracted = self._ocr_service.extract_from_pdf(file_path)
            elif input_type in (
                InputType.IMAGE.value,
                InputType.SCREENSHOT.value,
                InputType.HANDWRITTEN.value,
            ):
                extracted = self._ocr_service.extract_from_image(
                    file_path,
                    is_handwritten=(input_type == InputType.HANDWRITTEN.value),
                )
            else:
                raise OCRError(
                    f"OCR not supported for input type '{input_type}'",
                    context={"input_type": input_type},
                )
        except OCRError:
            raise
        except Exception as exc:
            raise OCRError(
                f"OCR extraction failed: {exc}",
                context={"file_path": file_path, "input_type": input_type},
            ) from exc
        finally:
            if file_path != input_file_path and os.path.exists(file_path):
                try:
                    from app.services.storage_service import StorageService
                    StorageService().cleanup_local_file(file_path)
                except Exception as cleanup_exc:
                    logger.warning("Failed to clean up temp OCR file", path=file_path, error=str(cleanup_exc))

        logger.info(
            "OCR agent completed",
            word_count=extracted.word_count,
            equations=len(extracted.equations),
            chunks=len(extracted.chunks),
        )

        return {"extracted_content": extracted}

    def _resolve_file_path(
        self, file_path: str, file_url: str
    ) -> str:
        """
        Return the local file path. If only a URL is available,
        download the file to a temp location.
        """
        if file_path and os.path.exists(file_path):
            return file_path

        if file_url:
            # Download from Firebase Storage to a temp path
            try:
                from app.services.storage_service import StorageService
                import tempfile

                storage = StorageService()
                suffix = Path(file_url).suffix or ".bin"
                tmp_file = tempfile.NamedTemporaryFile(
                    suffix=suffix, delete=False
                )
                tmp_path = tmp_file.name
                tmp_file.close()
                storage.download_file(file_url, tmp_path)
                return tmp_path
            except Exception as exc:
                logger.warning(
                    "Failed to download input file from URL",
                    url=file_url,
                    error=str(exc),
                )

        return file_path
