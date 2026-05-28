"""Calculation logic for greenhouse gas emissions."""

from typing import Iterable, Dict

from ..models.activity import Activity
from ..models.emission_factor import EmissionFactor


class GHGCalculator:
    """Compute emissions, scope breakdown, and report totals."""

    def compute_activity_emissions(self, activity: Activity, factor: EmissionFactor) -> float:
        return activity.amount * factor.value

    def compute_report(self, activities: Iterable[Activity], factors: Dict[str, EmissionFactor]) -> Dict[str, float]:
        totals = {"total_co2e": 0.0, "scope_1": 0.0, "scope_2": 0.0, "scope_3": 0.0}
        for activity in activities:
            factor = factors.get(activity.emission_factor_key)
            if factor is None:
                continue
            emission = self.compute_activity_emissions(activity, factor)
            totals["total_co2e"] += emission
            totals.setdefault(factor.scope, 0.0)
            totals[factor.scope] += emission
        return totals
