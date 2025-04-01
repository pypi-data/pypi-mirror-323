import json
import os
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from filelock import FileLock

from chronosys import StorageJSONEncoder


class StorageException(Exception):
    pass


class Chronosys:
    """Thread-safe JSON storage system with versioning and backup capabilities"""

    def __init__(
            self,
            filename: str = "config.json",
            backup_count: int = 3,
            indent: int = 2,
            encoder_cls: json.JSONEncoder = None,
            max_workers: int = 4
    ):
        self.filename = Path(filename)
        self.backup_count = backup_count
        self.indent = indent
        self.encoder = encoder_cls or StorageJSONEncoder
        self.lock = FileLock(f"{filename}.lock", timeout=10)
        self.memory_cache: Dict[str, Any] = {}
        self.cache_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # Ensure directory exists
        self.filename.parent.mkdir(parents=True, exist_ok=True)

        # Initialize file if it doesn't exist
        if not self.filename.exists():
            self._save_data({})

    def _save_data(self, data: Dict[str, Any]) -> None:
        """Save data to file with proper error handling"""
        temp_file = self.filename.with_suffix('.tmp')
        backup_file = self.filename.with_suffix('.bak')

        try:
            # Write to temporary file first
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=self.indent, cls=self.encoder)

            # Create backup of current file if it exists
            if self.filename.exists():
                shutil.copy2(self.filename, backup_file)

            # Atomic rename of temporary file to actual file
            os.replace(temp_file, self.filename)

            # Update memory cache
            with self.cache_lock:
                self.memory_cache = data.copy()

        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            raise StorageException(f"Failed to save data: {str(e)}") from e

    def _load_data(self) -> Dict[str, Any]:
        """Load data from file with fallback to backup"""
        try:
            # Try loading from memory cache first
            with self.cache_lock:
                if self.memory_cache:
                    return self.memory_cache.copy()

            # Try loading from main file
            if self.filename.exists():
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    with self.cache_lock:
                        self.memory_cache = data.copy()
                    return data

            # Try loading from backup if main file fails
            backup_file = self.filename.with_suffix('.bak')
            if backup_file.exists():
                with open(backup_file, 'r') as f:
                    data = json.load(f)
                    self._save_data(data)  # Restore from backup
                    return data

            return {}

        except json.JSONDecodeError as e:
            raise StorageException(f"Invalid JSON in storage file: {str(e)}") from e
        except Exception as e:
            raise StorageException(f"Failed to load data: {str(e)}") from e

    def set(self, key: str, value: Any) -> None:
        """Set a value in storage"""
        with self.lock:
            data = self._load_data()
            data[key] = value
            self._save_data(data)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from storage"""
        with self.lock:
            data = self._load_data()
            return data.get(key, default)

    def delete(self, key: str) -> bool:
        """Delete a key from storage"""
        with self.lock:
            data = self._load_data()
            if key in data:
                del data[key]
                self._save_data(data)
                return True
            return False

    def get_all(self) -> Dict[str, Any]:
        """Get all data from storage"""
        with self.lock:
            return self._load_data()

    def clear(self) -> None:
        """Clear all data from storage"""
        with self.lock:
            self._save_data({})

    async def async_set(self, key: str, value: Any) -> None:
        """Asynchronously set a value"""
        await self.executor.submit(self.set, key, value)

    async def async_get(self, key: str, default: Any = None) -> Any:
        """Asynchronously get a value"""
        return await self.executor.submit(self.get, key, default)

    def create_backup(self) -> Path:
        """Create a timestamped backup of the current data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.filename.with_name(f"{self.filename.stem}_backup_{timestamp}.json")

        with self.lock:
            if self.filename.exists():
                shutil.copy2(self.filename, backup_path)

                # Remove old backups if exceeding backup_count
                backups = sorted(
                    self.filename.parent.glob(f"{self.filename.stem}_backup_*.json")
                )
                while len(backups) > self.backup_count:
                    backups[0].unlink()
                    backups = backups[1:]

        return backup_path
