
"""The single calculation primitive used by every scope and category.
 
The whole of GHG accounting reduces to one equation:
 
    << emissions = activity_data x emission_factor >>
 
Everything else — the 15 Scope 3 categories, the location/market split in
Scope 2, fugitive GWP weighting in Scope 1 — is a matter of *which* activity
data and *which* factor to pair, and how to label the result. Centralising the
multiplication here means unit checking and rounding behaviour are defined
once and inherited everywhere.
"""

from __future__ import annotations 
from ..models.activity import ActivityData
from ..models.emission import EmissionFactor, EmissionResult, Scope, DataQuality


def apply_factor(
    activity: ActivityData,
    factor: EmissionFactor,
    *,
    scope: Scope,
    category: str,
    method: str,
    data_quality: DataQuality,
    check_units: bool = True,
) -> EmissionResult:
    """Multiply activity data by an emission factor to get kg CO2e.
 
    Parameters
    ----------
    activity, factor:
        The two inputs of the GHG equation.
    scope, category, method, data_quality:
        Metadata stamped onto the result so the inventory stays auditable.
    check_units:
        When ``True`` (default), raise if ``activity.unit`` does not match
        ``factor.unit``. This catches the most common real-world error —
        applying a per-litre factor to a kWh figure — at source.
    """
    if check_units and activity.unit != factor.unit:
        raise ValueError(
            f"Unit mismatch in {category}/{method}: activity is "
            f"{activity.unit!r} but factor is per {factor.unit!r}."
        )
    return EmissionResult(
        kg_co2e=activity.value * factor.value,
        scope=scope,
        category=category,
        method=method,
        data_quality=data_quality,
        source=factor.source,
    )

