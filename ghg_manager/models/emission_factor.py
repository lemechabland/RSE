"""Emission factor model definitions."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class EmissionFactor:
    category: str
    source: str
    value: float
    unit: str
    scope: str
    description: Optional[str] = None
