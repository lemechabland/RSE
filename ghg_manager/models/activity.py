"""Activity and company operations models."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Activity:
    name: str
    activity_type: str
    amount: float
    unit: str
    emission_factor_key: str
    scope: str
    notes: Optional[str] = None
