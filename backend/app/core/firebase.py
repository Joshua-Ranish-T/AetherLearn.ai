"""
Firebase Admin SDK initializer.

Provides singleton Firestore client and Storage bucket instances.
Call `initialize_firebase()` once during application startup lifespan.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import TYPE_CHECKING

import firebase_admin
from firebase_admin import credentials, firestore, storage

from app.core.config import get_settings
from app.core.exceptions import ConfigurationError
from app.core.logging_config import get_logger

if TYPE_CHECKING:
    from google.cloud.firestore import Client as FirestoreClient
    from firebase_admin.storage import Bucket

logger = get_logger(__name__)

_lock = threading.Lock()
_initialized: bool = False
_firestore_client: "FirestoreClient | None" = None
_storage_bucket: "Bucket | None" = None


def initialize_firebase() -> None:
    """
    Initialize Firebase Admin SDK.

    Must be called once before any Firestore / Storage operation.
    Thread-safe; subsequent calls are no-ops.
    """
    global _initialized, _firestore_client, _storage_bucket

    with _lock:
        if _initialized:
            return

        settings = get_settings()
        creds_path = Path(settings.firebase_credentials_path)

        if not creds_path.exists():
            raise ConfigurationError(
                f"Firebase credentials file not found: {creds_path}",
                context={"path": str(creds_path)},
            )

        if not settings.firebase_storage_bucket:
            raise ConfigurationError(
                "FIREBASE_STORAGE_BUCKET is not configured.",
                context={"env_var": "FIREBASE_STORAGE_BUCKET"},
            )

        try:
            cred = credentials.Certificate(str(creds_path))
            firebase_admin.initialize_app(
                cred,
                {
                    "storageBucket": settings.firebase_storage_bucket,
                    "projectId": settings.firebase_project_id,
                },
            )
            _firestore_client = firestore.client()
            _storage_bucket = storage.bucket()
            _initialized = True
            logger.info(
                "Firebase initialized",
                project_id=settings.firebase_project_id,
                bucket=settings.firebase_storage_bucket,
            )
        except Exception as exc:
            raise ConfigurationError(
                f"Failed to initialize Firebase: {exc}",
                context={"error": str(exc)},
            ) from exc


def get_firestore() -> "FirestoreClient":
    """Return the Firestore client singleton.  Raises if not initialized."""
    if _firestore_client is None:
        raise ConfigurationError(
            "Firebase has not been initialized. Call initialize_firebase() first."
        )
    return _firestore_client


def get_storage_bucket() -> "Bucket":
    """Return the Firebase Storage bucket singleton. Raises if not initialized."""
    if _storage_bucket is None:
        raise ConfigurationError(
            "Firebase has not been initialized. Call initialize_firebase() first."
        )
    return _storage_bucket


def shutdown_firebase() -> None:
    """Clean up Firebase app on application shutdown."""
    global _initialized, _firestore_client, _storage_bucket
    with _lock:
        if _initialized:
            try:
                firebase_admin.delete_app(firebase_admin.get_app())
            except Exception:
                pass
            _initialized = False
            _firestore_client = None
            _storage_bucket = None
            logger.info("Firebase shut down")
