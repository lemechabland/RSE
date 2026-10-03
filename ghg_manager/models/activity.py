"""Activity and company operations models."""

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ActivityData:
    """A measured level of activity that produces emissions."""
 
    value: float
    unit: str
    label: str = ""
 
    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Activity data cannot be negative.")

        
from typing import Optional

@dataclass
class Activity:
    name: str
    activity_type: str
    amount: float
    unit: str
    emission_factor_key: str
    scope: str
    category: Optional[str] = None
    notes: Optional[str] = None
