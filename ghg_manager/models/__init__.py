"""Data model package for the GHG Manager."""

from .company import Company
from .emission import (
    EmissionFactor, 
    EmissionResult, 
    Scope,
    Scope2DualResult
)
from .activity import ActivityData
from .report import GHGInventory #,GHGReport

__all__ = [
    "Company", 
    "EmissionFactor",
    "EmissionResult",
    "Scope",
    "Scope2DualResult",
    "ActivityData", 
    # "GHGReport", 
    "GHGInventory"
]

