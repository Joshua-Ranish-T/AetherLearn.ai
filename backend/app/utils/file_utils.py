"""
File utilities — common file system operations used across services and agents.
"""

from __future__ import annotations

import os
from pathlib import Path


def ensure_dir(path: str) -> Path:
    """Create a directory (and parents) if it doesn't exist."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_text_file(path: str, content: str, encoding: str = "utf-8") -> None:
    """Write text content to a file, creating parent directories as needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding=encoding)


def read_text_file(path: str, encoding: str = "utf-8") -> str:
    """Read and return the content of a text file."""
    return Path(path).read_text(encoding=encoding)


def file_exists(path: str) -> bool:
    """Return True if the file exists and is a regular file."""
    return Path(path).is_file()


def get_file_size(path: str) -> int:
    """Return file size in bytes, or 0 if file doesn't exist."""
    try:
        return Path(path).stat().st_size
    except (FileNotFoundError, OSError):
        return 0


def safe_delete(path: str) -> bool:
    """Delete a file if it exists. Returns True if deleted."""
    try:
        p = Path(path)
        if p.exists():
            p.unlink()
            return True
        return False
    except Exception:
        return False


def list_files_by_extension(directory: str, extension: str) -> list[str]:
    """Return all files with a given extension in a directory (recursive)."""
    ext = extension if extension.startswith(".") else f".{extension}"
    return [
        str(p)
        for p in Path(directory).rglob(f"*{ext}")
        if p.is_file()
    ]


def get_project_render_dir(base_dir: str, project_id: str) -> Path:
    """Return (and create) the render directory for a project."""
    return ensure_dir(str(Path(base_dir) / project_id))
