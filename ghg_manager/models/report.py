"""GHG reporting and summary model."""

from dataclasses import dataclass
from collections import defaultdict
from dataclasses import dataclass, field
from .emission import EmissionResult, Scope, Scope2DualResult
from ..utils.units import kg_to_tonnes



# from typing import Dict
# @dataclass
# class GHGReport:
#     company_name: str
#     fiscal_year: str
#     totals: Dict[str, float]
#     scope_breakdown: Dict[str, float]
#     activities: int
#     generated_at: str


 
@dataclass
class GHGInventory:
    """Accumulates emission results and summarises an organisation's footprint.
 
    Parameters
    ----------
    reporting_entity, reporting_year:
        Inventory metadata, surfaced in the report header.
    scope2_market_based_kg:
        Running total of the market-based Scope 2 figure, kept separate from
        the headline (location-based) total for dual reporting.
    """
 
    reporting_entity: str
    reporting_year: int
    _items: list[EmissionResult] = field(default_factory=list)
    scope2_market_based_kg: float = 0.0
 
    # -- ingestion --------------------------------------------------------
    def add(self, *results: EmissionResult) -> None:
        """Add one or more line items to the inventory."""
        self._items.extend(results)
 
    def add_scope2_dual(self, dual: Scope2DualResult) -> None:
        """Add a Scope 2 dual result: location-based feeds the headline total,
        market-based is tracked separately."""
        self._items.append(dual.location_based)
        self.scope2_market_based_kg += dual.market_based.kg_co2e
 
    # -- aggregation ------------------------------------------------------
    def by_scope_kg(self) -> dict[Scope, float]:
        totals: dict[Scope, float] = defaultdict(float)
        for item in self._items:
            totals[item.scope] += item.kg_co2e
        return dict(totals)
 
    def by_category_kg(self) -> dict[str, float]:
        totals: dict[str, float] = defaultdict(float)
        for item in self._items:
            totals[item.category] += item.kg_co2e
        return dict(totals)
 
    def total_kg(self) -> float:
        return sum(item.kg_co2e for item in self._items)
 
    def total_tonnes(self) -> float:
        return kg_to_tonnes(self.total_kg())
 
    # -- reporting --------------------------------------------------------
    def report(self) -> str:
        """Return a plain-text summary in tonnes CO2e (t CO2e)."""
        by_scope = self.by_scope_kg()
        lines = [
            f"GHG Inventory — {self.reporting_entity} ({self.reporting_year})",
            "=" * 56,
        ]
        for scope in Scope:
            t = kg_to_tonnes(by_scope.get(scope, 0.0))
            lines.append(f"Scope {scope.value:<2}{'':2}: {t:>14,.2f} t CO2e")
        if self.scope2_market_based_kg:
            mb = kg_to_tonnes(self.scope2_market_based_kg)
            lines.append(f"  (Scope 2 market-based: {mb:,.2f} t CO2e)")
        lines.append("-" * 56)
        lines.append(f"{'TOTAL':<8}: {self.total_tonnes():>14,.2f} t CO2e")
        lines.append("")
        lines.append("By category:")
        for cat, kg in sorted(
            self.by_category_kg().items(), key=lambda kv: kv[1], reverse=True
        ):
            lines.append(f"  {cat:<34}{kg_to_tonnes(kg):>12,.2f} t CO2e")
        return "\n".join(lines)