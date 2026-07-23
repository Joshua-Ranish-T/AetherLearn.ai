"""
Local Storage Service mock.

Bypasses Firebase for local development.
Copies files to a local directory and returns a local URL.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Optional

from app.core.exceptions import StorageError
from app.core.logging_config import get_logger

logger = get_logger(__name__)

LOCAL_STORAGE_DIR = os.path.join(os.getcwd(), "data", "storage")

class StorageService:
    """
    Mock storage service that saves files locally.
    """

    def __init__(self) -> None:
        os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)

    def upload_file(
        self,
        local_path: str,
        storage_path: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Upload a local file to the local storage mock.
        """
        if not Path(local_path).exists():
            raise StorageError(f"Local file not found for upload: {local_path}")

        dest_path = os.path.join(LOCAL_STORAGE_DIR, storage_path.replace("/", os.sep))
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        try:
            shutil.copy2(local_path, dest_path)
            logger.info("File copied to local storage mock", dest_path=dest_path)
            return f"/storage/{storage_path}"  # Mock URL
        except Exception as exc:
            raise StorageError(f"Failed to copy file to mock storage: {exc}") from exc

    def download_file(self, storage_path_or_url: str, local_path: str) -> None:
        """
        Download a file from local storage mock.
        """
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)

        storage_path = self._normalize_storage_path(storage_path_or_url)
        src_path = os.path.join(LOCAL_STORAGE_DIR, storage_path.replace("/", os.sep))
        
        try:
            shutil.copy2(src_path, local_path)
            logger.info("File copied from local storage mock", src_path=src_path)
        except Exception as exc:
            raise StorageError(f"Failed to copy from mock storage: {exc}") from exc

    def delete_file(self, storage_path: str) -> None:
        """Delete a file from mock storage."""
        dest_path = os.path.join(LOCAL_STORAGE_DIR, storage_path.replace("/", os.sep))
        if os.path.exists(dest_path):
            os.remove(dest_path)

    def get_signed_url(self, storage_path: str) -> str:
        return f"/storage/{storage_path}"

    def file_exists(self, storage_path: str) -> bool:
        dest_path = os.path.join(LOCAL_STORAGE_DIR, storage_path.replace("/", os.sep))
        return os.path.exists(dest_path)

    @staticmethod
    def _normalize_storage_path(path_or_url: str) -> str:
        if path_or_url.startswith("/storage/"):
            return path_or_url.replace("/storage/", "")
        return path_or_url
