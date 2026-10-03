"""Calculation logic for greenhouse gas emissions."""

# from typing import Iterable, Dict
# from abc import ABC, abstractmethod

from ..models.activity import ActivityData
from ..models.emission import (
    EmissionResult, 
    DataQuality, 
    Scope, 
    EmissionFactorProvider,
    Scope2DualResult
)
from .core import apply_factor


class GHGCalculator:

    def __init__(self, scope: Scope, factors: EmissionFactorProvider) -> None:
        self._scope = scope
        self._factors = factors

    def compute_activity_emissions(self, factor_key: str, activity: ActivityData, kwargs) -> EmissionResult:
        factor = self._factors.get(factor_key)
        return apply_factor(
            activity=activity,
            factor=factor,
            scope=self._scope,
            category=kwargs.get("category", "unknown"),
            method=kwargs.get("method", "unknown"),
            data_quality=kwargs.get("data_quality", DataQuality.PRIMARY),
        )
    
    def dual(
            self,
            *, 
            grid_factor_key: str, 
            supplier_factor_key:str,
            activity: ActivityData
    ) -> Scope2DualResult:
        if self._scope is Scope.SCOPE_2:
            return Scope2DualResult(
                location_based = self.compute_activity_emissions(
                    factor_key=grid_factor_key,
                    activity=activity,
                    kwargs={
                        "category": "purchased_energy",
                        "method": "location_based",
                        "data_quality": DataQuality.SECONDARY_SPECIFIC,
                    }),
                market_based = self.compute_activity_emissions(
                    factor_key=supplier_factor_key,
                    activity=activity,
                    kwargs={
                        "category": "purchased_energy",
                        "method": "market_based",
                        "data_quality": DataQuality.PRIMARY,
                    })

            )
        else:
            raise ValueError("Dual reporting is only applicable for Scope 2 emissions.")
        
    
    def total_emissions(self, results: list[EmissionResult], scope_flag: str) -> EmissionResult:
        """Aggregate a list of results into a single total."""
        return EmissionResult.aggregate(results, scope=self._scope, category=scope_flag)


    
# class GHGCalculator:
#     """Compute emissions, scope breakdown, and report totals."""

#     def compute_activity_emissions(self, activity: Activity, factor: EmissionFactor) -> float:
#         return activity.amount * factor.value

#     def compute_report(self, activities: Iterable[Activity], factors: Dict[str, EmissionFactor]) -> Dict[str, float]:
#         totals = {"total_co2e": 0.0, "scope_1": 0.0, "scope_2": 0.0, "scope_3": 0.0}
#         for activity in activities:
#             factor = factors.get(activity.emission_factor_key)
#             if factor is None:
#                 continue
#             emission = self.compute_activity_emissions(activity, factor)
#             totals["total_co2e"] += emission
#             totals.setdefault(factor.scope, 0.0)
#             totals[factor.scope] += emission
#         return totals
