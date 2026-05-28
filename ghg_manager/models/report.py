"""GHG reporting and summary model."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class GHGReport:
    company_name: str
    fiscal_year: str
    totals: Dict[str, float]
    scope_breakdown: Dict[str, float]
    activities: int
    generated_at: str
