"""Emission factor model definitions.

The design separates two concerns deliberately:

* :class:`EmissionFactor` — the conversion coefficient (kg CO2e per unit of
  activity). It carries provenance (source, year) because the GHG Protocol
  *requires* reporting the source of every factor used.
* :class:`ActivityData` — a measured level of activity (litres of fuel, kWh,
  kg of material, tonne-km, EUR spent ...).
* :class:`EmissionResult` — the immutable output of a calculation. It records
  not just the number but *how* it was obtained (scope, category, method,
  data-quality tier), which is what makes an inventory auditable.

Every calculator in this package returns an :class:`EmissionResult`. Nothing
returns a bare float, so context is never lost between calculation and report.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from ..utils.units import kg_to_tonnes


class Scope(int, Enum):
    """The three GHG Protocol scopes."""

    SCOPE_1 = 1
    SCOPE_2 = 2
    SCOPE_3 = 3


class DataQuality(str, Enum):
    """Qualitative data-quality tier, ordered from most to least preferred.

    Mirrors the GHG Protocol hierarchy: primary/supplier-specific data is
    preferred; spend-based (economic / EEIO) proxies sit at the bottom.
    """

    PRIMARY = "primary"            # supplier-/site-specific measured data
    SECONDARY_SPECIFIC = "secondary_specific"  # activity-specific averages
    SECONDARY_AVERAGE = "secondary_average"    # generic average data
    SPEND_BASED = "spend_based"    # economic proxy (EEIO)


@dataclass(frozen=True, slots=True)
class EmissionFactor:
    """A coefficient converting activity data into kg CO2e.

    Parameters
    ----------
    value:
        kg CO2e emitted per ``unit`` of activity.
    unit:
        The activity unit the factor applies to (e.g. ``"litre"``, ``"kWh"``,
        ``"kg"``, ``"tonne.km"``, ``"EUR"``). Used to guard against mixing
        incompatible factors and activity data.
    source:
        Provenance of the factor (e.g. ``"ADEME Base Carbone 2023"``,
        ``"DEFRA 2024"``). Required for auditable reporting.
    year:
        Reference year of the factor, for vintage tracking.
    """

    category: str
    value: float
    unit: str
    source: str
    year: int | None = None
    
    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Emission factor cannot be negative.")

@dataclass(frozen=True, slots=True)
class EmissionResult:
    """Immutable result of an emissions calculation, in kg CO2e.

    Aggregating results is associative: ``EmissionResult.aggregate([...])``
    or the ``+`` operator combine sub-results while preserving the scope.
    """

    kg_co2e: float
    scope: Scope
    category: str
    method: str
    data_quality: DataQuality
    source: str = ""
    breakdown: tuple["EmissionResult", ...] = field(default_factory=tuple)

    @property
    def tonnes_co2e(self) -> float:
        """Result expressed in tonnes CO2e (t CO2e)."""
        return kg_to_tonnes(self.kg_co2e)

    def __add__(self, other: "EmissionResult") -> "EmissionResult":
        if not isinstance(other, EmissionResult):
            return NotImplemented
        if other.scope is not self.scope:
            raise ValueError("Cannot add results from different scopes.")
        return EmissionResult(
            kg_co2e=self.kg_co2e + other.kg_co2e,
            scope=self.scope,
            category=self.category if self.category == other.category else "mixed",
            method="aggregated",
            data_quality=max(self.data_quality, other.data_quality, key=_dq_rank),
            breakdown=self.breakdown + other.breakdown or (self, other),
        )

    @staticmethod
    def aggregate(
        results: list["EmissionResult"],
        *,
        scope: Scope,
        category: str = "mixed",
    ) -> "EmissionResult":
        """Sum a list of results, keeping each as a breakdown line item."""
        total = sum(r.kg_co2e for r in results)
        worst = (
            max((r.data_quality for r in results), key=_dq_rank)
            if results
            else DataQuality.PRIMARY
        )
        return EmissionResult(
            kg_co2e=total,
            scope=scope,
            category=category,
            method="aggregated",
            data_quality=worst,
            breakdown=tuple(results),
        )
    

@dataclass(frozen=True, slots=True)
class Scope2DualResult:
    """ Holds the two mandatory Scope 2 figures, reported side by side."""
    location_based: EmissionResult
    market_based: EmissionResult


# Ordering helper so the *least* reliable tier wins when aggregating.
_DQ_ORDER = {
    DataQuality.PRIMARY: 0,
    DataQuality.SECONDARY_SPECIFIC: 1,
    DataQuality.SECONDARY_AVERAGE: 2,
    DataQuality.SPEND_BASED: 3,
}


def _dq_rank(dq: DataQuality) -> int:
    return _DQ_ORDER[dq]


"""Emission-factor sourcing.
 
Emission factors are *injected*, never hard-coded into the calculators. This
is the single most important design decision in the package: the authoritative
numbers live in published databases (ADEME Base Carbone, DEFRA, ecoinvent,
EPA, IEA grid factors ...) that are revised annually, and baking guessed
values into the calculation logic would make the inventory both wrong and
unmaintainable.
 
:class:`EmissionFactorProvider` is the abstraction (dependency inversion: the
calculators depend on this interface, not on a concrete database).

"""

class FactorNotFoundError(KeyError):
    """Raised when no emission factor is registered for a given key."""
 
 
class EmissionFactorProvider(ABC):
    """Abstract source of emission factors.
 
    Implement this against ADEME Base Carbone, DEFRA, an internal database,
    or an API. Calculators only ever see this interface.
    """
 
    @abstractmethod
    def get(self, key: str) -> EmissionFactor:
        """Returns the factor registered under ``key`` or raise."""
 
    def get_or_none(self, key: str) -> EmissionFactor | None:
        try:
            return self.get(key)
        except FactorNotFoundError:
            return None