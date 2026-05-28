"""Persistence abstraction for company data and emission factors."""

import json
from pathlib import Path
from typing import Any

from ..config import DEFAULT_DATA_FILE, DATA_FOLDER


class DataStore:
    """Simple JSON-backed data store for GHG data."""

    def __init__(self, path: Path = DEFAULT_DATA_FILE):
        self.path = path
        DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    def load(self) -> Any:
        if not self.path.exists():
            return {}
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def save(self, data: Any) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
