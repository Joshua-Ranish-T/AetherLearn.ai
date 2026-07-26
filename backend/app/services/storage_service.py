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

from app.core.config import get_settings
from app.core.exceptions import StorageError
from app.core.logging_config import get_logger
from app.core.firebase import is_firebase_initialized, get_storage_bucket

logger = get_logger(__name__)

LOCAL_STORAGE_DIR = os.path.join(os.getcwd(), "data", "storage")

class StorageService:
    """
    Storage service supporting Firebase Cloud Storage with local disk fallback.
    """

    def __init__(self) -> None:
        if not self._use_firebase:
            os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)

    @property
    def _use_firebase(self) -> bool:
        settings = get_settings()
        if not is_firebase_initialized():
            if settings.use_firebase or settings.is_production:
                from app.core.firebase import initialize_firebase
                try:
                    initialize_firebase()
                except Exception as exc:
                    if settings.is_production:
                        raise StorageError(
                            f"Firebase initialization required in cloud/production mode failed: {exc}"
                        ) from exc
                    logger.warning("Firebase init failed, falling back to local disk storage", error=str(exc))
        return is_firebase_initialized()

    def upload_file(
        self,
        local_path: str,
        storage_path: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Upload a local file to Firebase Cloud Storage or local storage fallback.
        """
        if not Path(local_path).exists():
            raise StorageError(f"Local file not found for upload: {local_path}")

        if self._use_firebase:
            try:
                bucket = get_storage_bucket()
                blob = bucket.blob(storage_path)
                blob.upload_from_filename(local_path, content_type=content_type)
                try:
                    blob.make_public()
                    url = blob.public_url
                except Exception:
                    from datetime import timedelta
                    url = blob.generate_signed_url(expiration=timedelta(days=365), version="v4")
                logger.info("File uploaded to Firebase Cloud Storage", url=url, path=storage_path)
                return url
            except Exception as exc:
                logger.warning("Firebase Cloud Storage upload unavailable; falling back to local server disk storage", error=str(exc))

        dest_path = os.path.join(LOCAL_STORAGE_DIR, storage_path.replace("/", os.sep))
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        try:
            shutil.copy2(local_path, dest_path)
            logger.info("File copied to local storage mock", dest_path=dest_path)
            return f"/storage/{storage_path}"
        except Exception as exc:
            raise StorageError(f"Failed to copy file to storage: {exc}") from exc

    def download_file(self, storage_path_or_url: str, local_path: str) -> None:
        """
        Download a file from Firebase Cloud Storage or local storage fallback.
        """
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)

        if self._use_firebase and ("storage.googleapis.com" in storage_path_or_url or "firebasestorage" in storage_path_or_url or not storage_path_or_url.startswith("/storage/")):
            try:
                storage_path = self._normalize_storage_path(storage_path_or_url)
                bucket = get_storage_bucket()
                blob = bucket.blob(storage_path)
                if blob.exists():
                    blob.download_to_filename(local_path)
                    logger.info("File downloaded from Firebase Cloud Storage", path=storage_path)
                    return
            except Exception as exc:
                logger.warning("Firebase Cloud Storage download unavailable; falling back to local server disk storage", error=str(exc))

        storage_path = self._normalize_storage_path(storage_path_or_url)
        src_path = os.path.join(LOCAL_STORAGE_DIR, storage_path.replace("/", os.sep))
        
        try:
            shutil.copy2(src_path, local_path)
            logger.info("File copied from local storage mock", src_path=src_path)
        except Exception as exc:
            raise StorageError(f"Failed to copy from storage: {exc}") from exc

    def cleanup_local_file(self, local_path: str) -> None:
        """Safely remove a temporary local file after upload if in production mode or requested."""
        if not local_path or not os.path.exists(local_path):
            return
        try:
            if get_settings().is_production or "renders" in local_path or "uploads" in local_path or "tmp" in local_path:
                os.remove(local_path)
                logger.info("Cleaned up local temporary file", path=local_path)
        except Exception as exc:
            logger.warning("Failed to clean up local file", path=local_path, error=str(exc))

    def cleanup_directory(self, dir_path: str) -> None:
        """Safely remove an entire local directory after upload if in production mode or requested."""
        if not dir_path or not os.path.exists(dir_path):
            return
        try:
            if get_settings().is_production or "renders" in dir_path or "uploads" in dir_path or "tmp" in dir_path:
                shutil.rmtree(dir_path, ignore_errors=True)
                logger.info("Cleaned up local temporary directory", path=dir_path)
        except Exception as exc:
            logger.warning("Failed to clean up local directory", path=dir_path, error=str(exc))

    def delete_file(self, storage_path: str) -> None:
        """Delete a file from storage."""
        if self._use_firebase:
            try:
                bucket = get_storage_bucket()
                blob = bucket.blob(storage_path)
                if blob.exists():
                    blob.delete()
                    logger.info("File deleted from Firebase Cloud Storage", path=storage_path)
            except Exception as exc:
                logger.warning("Firebase Cloud Storage delete unavailable; falling back to local server disk storage", error=str(exc))

        dest_path = os.path.join(LOCAL_STORAGE_DIR, storage_path.replace("/", os.sep))
        if os.path.exists(dest_path):
            os.remove(dest_path)

    def get_signed_url(self, storage_path: str) -> str:
        if self._use_firebase and not storage_path.startswith("/storage/") and not storage_path.startswith("http"):
            try:
                bucket = get_storage_bucket()
                blob = bucket.blob(storage_path)
                if blob.exists():
                    try:
                        from datetime import timedelta
                        return blob.generate_signed_url(expiration=timedelta(days=365), version="v4")
                    except Exception:
                        return blob.public_url
            except Exception:
                pass
        if storage_path.startswith("http://") or storage_path.startswith("https://"):
            return storage_path
        return f"/storage/{storage_path}"

    def file_exists(self, storage_path: str) -> bool:
        if self._use_firebase and not storage_path.startswith("/storage/"):
            try:
                bucket = get_storage_bucket()
                blob = bucket.blob(storage_path)
                if blob.exists():
                    return True
            except Exception:
                pass
        dest_path = os.path.join(LOCAL_STORAGE_DIR, storage_path.replace("/", os.sep))
        return os.path.exists(dest_path)

    @staticmethod
    def _normalize_storage_path(path_or_url: str) -> str:
        if not path_or_url:
            return ""
        if path_or_url.startswith("/storage/"):
            return path_or_url.replace("/storage/", "", 1)
        if "firebasestorage" in path_or_url and "/o/" in path_or_url:
            try:
                import urllib.parse
                parts = path_or_url.split("/o/", 1)[1]
                encoded_path = parts.split("?", 1)[0]
                return urllib.parse.unquote(encoded_path)
            except Exception:
                pass
        if "storage.googleapis.com" in path_or_url:
            try:
                import urllib.parse
                parts = path_or_url.split("storage.googleapis.com/", 1)[1]
                subparts = parts.split("/", 1)
                if len(subparts) > 1:
                    path_part = subparts[1].split("?", 1)[0]
                    return urllib.parse.unquote(path_part)
            except Exception:
                pass
        return path_or_url.split("?", 1)[0]

