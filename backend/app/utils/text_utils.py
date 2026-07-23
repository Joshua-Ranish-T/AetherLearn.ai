"""
Text utility functions.
"""

from __future__ import annotations

import re
import unicodedata


def sanitize_filename(name: str, max_length: int = 100) -> str:
    """
    Convert an arbitrary string into a safe filename.
    Replaces non-alphanumeric chars with underscores.
    """
    name = unicodedata.normalize("NFKD", name)
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s-]+", "_", name)
    return name[:max_length].strip("_").lower()


def truncate(text: str, max_chars: int = 500, suffix: str = "...") -> str:
    """Truncate text to max_chars characters with a suffix."""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - len(suffix)] + suffix


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def extract_first_line(text: str) -> str:
    """Return the first non-empty line of text."""
    for line in text.split("\n"):
        line = line.strip()
        if line:
            return line
    return ""


def clean_whitespace(text: str) -> str:
    """Normalize whitespace — collapse multiple spaces and strip."""
    return re.sub(r"[ \t]+", " ", text).strip()


def remove_markdown(text: str) -> str:
    """Strip basic markdown formatting for plain-text output."""
    # Remove headers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}(.+?)_{1,3}", r"\1", text)
    # Remove inline code
    text = re.sub(r"`(.+?)`", r"\1", text)
    # Remove links
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    # Remove horizontal rules
    text = re.sub(r"^[-*_]{3,}$", "", text, flags=re.MULTILINE)
    return clean_whitespace(text)


def estimate_speaking_duration(text: str, words_per_minute: int = 140) -> float:
    """Estimate speaking duration in seconds based on word count."""
    words = count_words(text)
    return max(2.0, (words / words_per_minute) * 60)


def build_safe_class_name(title: str) -> str:
    """Convert a title string into a valid Python class name."""
    # Capitalize words and remove non-alphanumeric
    words = re.sub(r"[^a-zA-Z0-9\s]", "", title).split()
    return "".join(word.capitalize() for word in words[:5]) or "DefaultScene"
