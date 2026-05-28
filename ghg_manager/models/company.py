"""Company and organization data models."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Company:
    name: str
    industry: str
    location: Optional[str] = None
    fiscal_year: Optional[str] = None
    capital_amount: Optional[float] = None
    notes: Optional[str] = None
