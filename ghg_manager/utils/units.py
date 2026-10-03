"""Units, conversions and Global Warming Potentials (GWP).

All emission results in this package are normalised to **kilograms of CO2
equivalent (kg CO2e)** internally, and converted to tonnes (t CO2e) only at
the reporting boundary. Keeping a single internal unit avoids the classic
class of bugs where kg and tonnes are silently mixed.

GWP values follow the IPCC convention used by the GHG Protocol. The defaults
below are AR5 (100-year) values; swap ``DEFAULT_GWP`` for another assessment
report if your reporting standard requires it (e.g. AR6).
"""

from __future__ import annotations

from enum import Enum

KG_PER_TONNE: float = 1_000.0


def kg_to_tonnes(kg: float) -> float:
    """Convert kilograms of CO2e to tonnes of CO2e."""
    return kg / KG_PER_TONNE


def tonnes_to_kg(tonnes: float) -> float:
    """Convert tonnes of CO2e to kilograms of CO2e."""
    return tonnes * KG_PER_TONNE


class GreenhouseGas(str, Enum):
    """The greenhouse gases recognised by the GHG Protocol."""

    CO2 = "CO2"
    CH4 = "CH4"
    N2O = "N2O"
    HFCs = "HFCs"
    PFCs = "PFCs"
    SF6 = "SF6"
    NF3 = "NF3"


# 100-year GWP (IPCC AR5). Used to convert non-CO2 gas masses into CO2e,
# notably for Scope 1 fugitive (refrigerant) emissions. Refrigerant blends
# (R-410A, R-134a, ...) should be registered as explicit factors in the
# EmissionFactorProvider rather than approximated here.
DEFAULT_GWP: dict[GreenhouseGas, float] = {
    GreenhouseGas.CO2: 1.0,
    GreenhouseGas.CH4: 28.0,
    GreenhouseGas.N2O: 265.0,
    GreenhouseGas.SF6: 23_500.0,
    GreenhouseGas.NF3: 16_100.0,
    # HFCs / PFCs are families: register the specific species you use.
}
