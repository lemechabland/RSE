"""Application configuration and constants."""

from pathlib import Path

PROJECT_NAME = "ghg_manager"
DATA_FOLDER = Path.cwd() / "data"
DEFAULT_DATA_FILE = DATA_FOLDER / "ghg_data.json"
SUPPORTED_SCOPES = ["scope_1", "scope_2", "scope_3"]
