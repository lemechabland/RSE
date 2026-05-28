"""Excel and CSV import utilities."""

from pathlib import Path
from typing import Any

import pandas as pd


def load_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".xls", ".xlsx", ".xlsm", ".xlsb"}:
        return pd.read_excel(path)
    if suffix == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported file type: {suffix}")


def normalize_columns(df: pd.DataFrame) -> list[str]:
    return [str(col) for col in df.columns]
