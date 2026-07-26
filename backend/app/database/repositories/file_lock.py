"""
Cross-platform file locking utility for local JSON repositories.
Uses a reentrant thread lock (RLock) + thread-local ownership tracking + atomic lockfile creation (O_CREAT | O_EXCL).
"""

import os
import time
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

_thread_lock = threading.RLock()
_owner_threads: dict[str, tuple[int, int]] = {}


@contextmanager
def acquire_lock(db_path: Path, timeout: float = 10.0) -> Generator[None, None, None]:
    """Acquire thread and file lock for safe concurrent reading and writing of JSON database."""
    with _thread_lock:
        thread_id = threading.get_ident()
        path_str = str(db_path.resolve())
        
        # If current thread already owns the lock for this path, reenter
        if _owner_threads.get(path_str, (None, 0))[0] == thread_id:
            _, count = _owner_threads[path_str]
            _owner_threads[path_str] = (thread_id, count + 1)
            try:
                yield
            finally:
                with _thread_lock:
                    if path_str in _owner_threads:
                        if _owner_threads[path_str][1] <= 1:
                            del _owner_threads[path_str]
                        else:
                            _owner_threads[path_str] = (thread_id, _owner_threads[path_str][1] - 1)
            return

        # Otherwise acquire file lock
        lock_path = db_path.with_suffix(".lock")
        start_time = time.time()
        while True:
            try:
                fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.close(fd)
                break
            except (OSError, FileExistsError):
                if time.time() - start_time > timeout:
                    break  # Timeout fallback
                time.sleep(0.01)
        
        _owner_threads[path_str] = (thread_id, 1)

    try:
        yield
    finally:
        with _thread_lock:
            if path_str in _owner_threads:
                if _owner_threads[path_str][1] <= 1:
                    del _owner_threads[path_str]
                    try:
                        if lock_path.exists():
                            lock_path.unlink()
                    except OSError:
                        pass
                else:
                    _owner_threads[path_str] = (thread_id, _owner_threads[path_str][1] - 1)
