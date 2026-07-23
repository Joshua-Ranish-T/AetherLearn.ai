"""
OCR Service — Low-level OCR integration.

Provides:
- PDF text extraction via PyMuPDF
- Image OCR via Tesseract (primary) + EasyOCR (fallback)
- Mathematical expression detection
- Code block detection
- Table detection
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from app.core.exceptions import OCRError
from app.core.logging_config import get_logger
from app.schemas.content import ContentChunk, ExtractedContent, InputType

logger = get_logger(__name__)


class OCRService:
    """
    Low-level OCR operations. Uses:
    - PyMuPDF (fitz) for PDF extraction
    - pytesseract for image OCR (primary)
    - easyocr for image OCR (fallback / handwriting)
    """

    # ── PDF Extraction ─────────────────────────────────────────────────────

    def extract_from_pdf(self, file_path: str) -> ExtractedContent:
        """Extract all content from a PDF file."""
        try:
            import fitz  # PyMuPDF
        except ImportError as exc:
            raise OCRError("PyMuPDF not installed. Run: pip install pymupdf") from exc

        path = Path(file_path)
        if not path.exists():
            raise OCRError(f"PDF file not found: {file_path}")

        logger.info("Extracting PDF", path=file_path)

        try:
            doc = fitz.open(str(path))
        except Exception as exc:
            raise OCRError(f"Failed to open PDF: {exc}", context={"path": file_path}) from exc

        all_text: list[str] = []
        chunks: list[ContentChunk] = []
        all_equations: list[str] = []
        all_code: list[str] = []
        all_tables: list[list[list[str]]] = []

        for page_num, page in enumerate(doc, start=1):
            # Extract text blocks
            blocks = page.get_text("blocks")
            page_text_parts: list[str] = []

            for block in blocks:
                if block[6] == 0:  # Text block (not image)
                    text = block[4].strip()
                    if not text:
                        continue

                    page_text_parts.append(text)

                    # Classify chunk
                    chunk_type = self._classify_text_chunk(text)
                    chunks.append(
                        ContentChunk(
                            chunk_type=chunk_type,
                            content=text,
                            confidence=1.0,
                            page_number=page_num,
                            metadata={"block_bbox": list(block[:4])},
                        )
                    )

                    # Extract specialized content
                    equations = self._extract_equations(text)
                    all_equations.extend(equations)

                    code = self._extract_code_blocks(text)
                    all_code.extend(code)

            # Extract tables
            tables = page.find_tables()
            if tables and tables.tables:
                for table in tables.tables:
                    extracted_table = table.extract()
                    if extracted_table:
                        all_tables.append(extracted_table)
                        chunks.append(
                            ContentChunk(
                                chunk_type="table",
                                content=str(extracted_table),
                                page_number=page_num,
                                metadata={"rows": len(extracted_table)},
                            )
                        )

            all_text.append("\n".join(page_text_parts))

        doc.close()

        raw_text = "\n\n".join(all_text)
        word_count = len(raw_text.split())

        extracted = ExtractedContent(
            input_type=InputType.PDF,
            raw_text=raw_text,
            chunks=chunks,
            equations=list(dict.fromkeys(all_equations)),  # deduplicate
            code_blocks=all_code,
            tables=all_tables,
            language="en",
            subject_domain=self._detect_subject(raw_text),
            word_count=word_count,
            ocr_used=False,
            source_file_name=path.name,
            extraction_metadata={
                "page_count": len(doc) if not doc.is_closed else 0,
                "file_size_bytes": path.stat().st_size,
            },
        )

        logger.info(
            "PDF extracted",
            pages=len(all_text),
            words=word_count,
            equations=len(all_equations),
        )

        return extracted

    # ── Image Extraction ───────────────────────────────────────────────────

    def extract_from_image(
        self, file_path: str, is_handwritten: bool = False
    ) -> ExtractedContent:
        """Extract text from an image using Tesseract (or EasyOCR for handwriting)."""
        path = Path(file_path)
        if not path.exists():
            raise OCRError(f"Image file not found: {file_path}")

        logger.info(
            "Extracting image",
            path=file_path,
            handwritten=is_handwritten,
        )

        if is_handwritten:
            return self._extract_with_easyocr(path)
        else:
            try:
                return self._extract_with_tesseract(path)
            except Exception as exc:
                logger.warning(
                    "Tesseract failed, falling back to EasyOCR",
                    error=str(exc),
                )
                return self._extract_with_easyocr(path)

    def _extract_with_tesseract(self, path: Path) -> ExtractedContent:
        """Use pytesseract for image OCR."""
        try:
            import pytesseract
            from PIL import Image
        except ImportError as exc:
            raise OCRError(
                "pytesseract or Pillow not installed.", context={"error": str(exc)}
            ) from exc

        try:
            image = Image.open(str(path))
            # Get detailed output with confidence scores
            data = pytesseract.image_to_data(
                image,
                output_type=pytesseract.Output.DICT,
                lang="eng",
            )
            # Build text from confident words
            words = []
            for i, word in enumerate(data["text"]):
                conf = int(data["conf"][i])
                if conf > 30 and word.strip():
                    words.append(word)

            raw_text = pytesseract.image_to_string(image, lang="eng").strip()
        except Exception as exc:
            raise OCRError(
                f"Tesseract OCR failed: {exc}",
                context={"path": str(path)},
            ) from exc

        return self._build_extracted_content(
            raw_text=raw_text,
            input_type=InputType.IMAGE,
            source_name=path.name,
            ocr_used=True,
        )

    def _extract_with_easyocr(self, path: Path) -> ExtractedContent:
        """Use EasyOCR as primary or fallback OCR engine."""
        try:
            import easyocr
        except ImportError as exc:
            raise OCRError(
                "easyocr not installed. Run: pip install easyocr"
            ) from exc

        try:
            reader = easyocr.Reader(["en"], gpu=False, verbose=False)
            results = reader.readtext(str(path), detail=1)
            # results: list of (bbox, text, confidence)
            high_conf = [
                (text, conf)
                for (_, text, conf) in results
                if conf > 0.3 and text.strip()
            ]
            raw_text = " ".join(text for text, _ in high_conf)
        except Exception as exc:
            raise OCRError(
                f"EasyOCR failed: {exc}",
                context={"path": str(path)},
            ) from exc

        return self._build_extracted_content(
            raw_text=raw_text,
            input_type=InputType.HANDWRITTEN,
            source_name=path.name,
            ocr_used=True,
        )

    def _build_extracted_content(
        self,
        raw_text: str,
        input_type: InputType,
        source_name: str,
        ocr_used: bool,
    ) -> ExtractedContent:
        """Construct ExtractedContent from raw OCR text."""
        equations = self._extract_equations(raw_text)
        code_blocks = self._extract_code_blocks(raw_text)
        chunks = self._segment_into_chunks(raw_text)

        return ExtractedContent(
            input_type=input_type,
            raw_text=raw_text,
            chunks=chunks,
            equations=equations,
            code_blocks=code_blocks,
            tables=[],
            language="en",
            subject_domain=self._detect_subject(raw_text),
            word_count=len(raw_text.split()),
            ocr_used=ocr_used,
            source_file_name=source_name,
        )

    # ── Content Analysis Helpers ──────────────────────────────────────────

    def _classify_text_chunk(self, text: str) -> str:
        """Classify a text chunk by type."""
        stripped = text.strip()
        if re.search(r"\\[a-zA-Z]+\{|\\frac|\\sum|\\int|\$.*\$", stripped):
            return "equation"
        if re.search(r"^\s*(def |class |import |#|//|/\*)", stripped, re.MULTILINE):
            return "code"
        if re.search(r"^\s*[\w\s]+\s*\|\s*[\w\s]+", stripped, re.MULTILINE):
            return "table"
        if len(stripped) < 80 and stripped.isupper():
            return "heading"
        return "paragraph"

    def _extract_equations(self, text: str) -> list[str]:
        """Extract mathematical expressions from text."""
        equations = []

        # LaTeX patterns
        latex_patterns = [
            r"\$\$(.+?)\$\$",        # Display math
            r"\$(.+?)\$",            # Inline math
            r"\\begin\{equation\}(.+?)\\end\{equation\}",
            r"\\begin\{align\}(.+?)\\end\{align\}",
        ]
        for pattern in latex_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            equations.extend(m.strip() for m in matches if m.strip())

        # Common math patterns (without LaTeX markers)
        math_patterns = [
            r"[a-zA-Z]\s*=\s*[-+]?\d*\.?\d+\s*[+\-*/]\s*\d",   # a = 3 + 2
            r"[∫∑∏√∞±≤≥≠≈]",                                    # Special math symbols
            r"d/d[a-z]|∂/∂[a-z]",                               # Derivatives
            r"lim\s*[_\^]",                                       # Limits
        ]
        for pattern in math_patterns:
            matches = re.findall(pattern, text)
            equations.extend(m.strip() for m in matches if m.strip())

        return list(dict.fromkeys(equations))[:20]  # Deduplicate, limit 20

    def _extract_code_blocks(self, text: str) -> list[str]:
        """Extract programming code blocks from text."""
        blocks = []

        # Markdown fenced code blocks
        pattern = r"```(?:\w+)?\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        blocks.extend(m.strip() for m in matches if m.strip())

        # Indented code (4+ spaces)
        indented = re.findall(r"(?:^    .+\n?)+", text, re.MULTILINE)
        blocks.extend(m.strip() for m in indented if m.strip() and len(m) > 20)

        return blocks[:5]  # Limit to 5

    def _segment_into_chunks(self, text: str) -> list[ContentChunk]:
        """Segment plain text into typed content chunks."""
        chunks = []
        paragraphs = re.split(r"\n{2,}", text.strip())
        for para in paragraphs:
            if not para.strip():
                continue
            chunk_type = self._classify_text_chunk(para)
            chunks.append(
                ContentChunk(
                    chunk_type=chunk_type,
                    content=para.strip(),
                    confidence=0.9,
                )
            )
        return chunks

    def _detect_subject(self, text: str) -> str:
        """Heuristic subject domain detection."""
        text_lower = text.lower()
        kw_map = {
            "math": ["derivative", "integral", "equation", "theorem", "calculus", "matrix"],
            "physics": ["force", "velocity", "acceleration", "quantum", "wave", "momentum"],
            "cs": ["algorithm", "function", "recursion", "class", "array", "loop", "variable"],
            "chemistry": ["molecule", "atom", "reaction", "bond", "element", "compound"],
        }
        scores = {}
        for domain, keywords in kw_map.items():
            scores[domain] = sum(1 for kw in keywords if kw in text_lower)
        best = max(scores, key=lambda k: scores[k])
        return best if scores[best] > 0 else "general"
