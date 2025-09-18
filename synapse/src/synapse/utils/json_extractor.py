from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Optional


class JSONExtractor:
    """Utility for reading a JSON file and extracting specific keys from a nested object path.

    Example:
        extractor = JSONExtractor(file_path="Plot.json", nested_path=["bullseyeConcept"]) 
        data = extractor.extract_keys(["victim", "crime"])  # returns dict
        text = extractor.extract_keys_or_fallback(["victim", "crime"], fallback_json="{}")  # returns JSON string
    """

    def __init__(self, file_path: str, nested_path: Optional[Iterable[str]] = None) -> None:
        self.file_path: str = file_path
        self.nested_path: List[str] = list(nested_path or [])

    def _read_json(self) -> Any:
        with open(self.file_path, "r") as file_handle:
            return json.load(file_handle)

    def _traverse_path(self, data: Any) -> Any:
        current: Any = data
        for key in self.nested_path:
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return None
        return current

    def extract_keys(self, keys: Iterable[str]) -> Dict[str, Any]:
        """Extract key/value pairs from the nested object. Missing keys map to None.
        Raises file/JSON errors to caller.
        """
        data = self._read_json()
        target = self._traverse_path(data)
        if not isinstance(target, dict):
            return {key: None for key in keys}
        return {key: target.get(key) for key in keys}

    def extract_keys_or_fallback(self, keys: Iterable[str], fallback_json: Optional[str] = None) -> str:
        """Extract keys and return a JSON string. If reading/parsing fails and a fallback_json
        is provided, return that fallback JSON string. Otherwise re-raise the error.
        """
        try:
            result = self.extract_keys(keys)
            return json.dumps(result)
        except (json.JSONDecodeError, FileNotFoundError, TypeError):
            if fallback_json is not None:
                return fallback_json
            raise
