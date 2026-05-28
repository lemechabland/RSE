"""File system helper utilities."""

from pathlib import Path


def ensure_folder(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
