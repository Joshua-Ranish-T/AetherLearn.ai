"""
Content extraction schemas.

Represents the normalized output from the OCR & Content Extraction Agent.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class InputType(str, Enum):
    TEXT = "text"
    TOPIC = "topic"
    PDF = "pdf"
    IMAGE = "image"
    SCREENSHOT = "screenshot"
    HANDWRITTEN = "handwritten"


class ContentChunk(BaseModel):
    """A single piece of extracted content with type information."""

    chunk_type: str = Field(
        description="Type: paragraph | equation | code | table | figure | heading"
    )
    content: str = Field(description="The raw extracted text/expression")
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="OCR confidence score"
    )
    page_number: int | None = Field(
        default=None, description="Source page (for PDFs)"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extra metadata: bbox, font_size, language, etc."
    )


class ExtractedContent(BaseModel):
    """
    Fully normalized content extracted from any supported input.
    This is the input to the Content Generation Agent.
    """

    input_type: InputType
    raw_text: str = Field(description="Full concatenated raw text")
    chunks: list[ContentChunk] = Field(
        default_factory=list,
        description="Structured content chunks"
    )
    equations: list[str] = Field(
        default_factory=list,
        description="Detected mathematical expressions (LaTeX or raw)"
    )
    code_blocks: list[str] = Field(
        default_factory=list,
        description="Detected programming code blocks"
    )
    tables: list[list[list[str]]] = Field(
        default_factory=list,
        description="Detected tables as list-of-rows-of-cells"
    )
    figures_described: list[str] = Field(
        default_factory=list,
        description="Textual descriptions of detected figures/diagrams"
    )
    language: str = Field(
        default="en",
        description="Detected language (ISO 639-1)"
    )
    subject_domain: str = Field(
        default="",
        description="Detected subject: math | physics | cs | chemistry | general"
    )
    word_count: int = Field(default=0)
    ocr_used: bool = Field(
        default=False,
        description="Whether OCR was used to extract this content"
    )
    source_file_name: str = Field(default="")
    extraction_metadata: dict[str, Any] = Field(default_factory=dict)
