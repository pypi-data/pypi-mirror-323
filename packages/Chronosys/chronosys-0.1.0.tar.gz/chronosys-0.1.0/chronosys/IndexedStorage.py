from collections import defaultdict
from typing import Dict, List, Any, Tuple

from chronosys import Chronosys


class IndexedStorage(Chronosys):
    """Base class adding indexing capabilities to JsonStorage"""

    def __init__(self, filename: str = "config.json", encoder_cls=None):
        super().__init__(filename, encoder_cls=encoder_cls)
        self._path_index = defaultdict(set)
        self._build_index()

    def _build_index(self) -> None:
        """Build the initial path index"""
        with self.lock:
            data = self._load_data()
            self._path_index.clear()
            self._index_dict(data)

    def _index_dict(self, data: Dict, current_path: List[str] = None) -> None:
        if current_path is None:
            current_path = []

        for key, value in data.items():
            path_tuple = tuple(current_path + [key])
            self._path_index[key].add(path_tuple)

            if isinstance(value, dict):
                self._index_dict(value, list(path_tuple))

    def _update_index(self, path: List[str], value: Any) -> None:
        key = path[-1]
        self._path_index[key] = {p for p in self._path_index[key]
                                 if not self._is_subpath(path, p)}
        self._path_index[key].add(tuple(path))

        if isinstance(value, dict):
            self._index_dict(value, path)

    def _is_subpath(self, path: List[str], indexed_path: Tuple[str, ...]) -> bool:
        return len(path) <= len(indexed_path) and all(
            a == b for a, b in zip(path, indexed_path)
        )

    def find(self, key: str) -> List[Tuple[List[str], Any]]:
        """Find all occurrences of a key using the index"""
        with self.lock:
            data = self._load_data()
            results = []

            for path_tuple in self._path_index.get(key, set()):
                value = data
                for part in path_tuple:
                    value = value[part]
                results.append((list(path_tuple), value))

            return results

    def get_first(self, key: str, default: Any = None) -> Any:
        """Get first occurrence of a key using the index"""
        paths = self._path_index.get(key, set())
        if not paths:
            return default

        with self.lock:
            data = self._load_data()
            path = next(iter(paths))
            value = data
            for part in path:
                value = value.get(part, default)
                if value is default:
                    return default
            return value

    def set(self, *path_parts: str, value: Any) -> None:
        """Set a value and update the index"""
        if not path_parts:
            raise ValueError("Path cannot be empty")

        with self.lock:
            data = self._load_data()
            current = data

            for part in path_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            current[path_parts[-1]] = value
            self._update_index(list(path_parts), value)
            self._save_data(data)

    def get(self, *path_parts: str, default: Any = None) -> Any:
        """Get a value using direct path access"""
        with self.lock:
            data = self._load_data()
            current = data

            for part in path_parts:
                if not isinstance(current, dict):
                    return default
                current = current.get(part, default)
                if current is default:
                    return default

            return current
