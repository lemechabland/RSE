"""Scope 3 — all other indirect value-chain emissions, organised into the 15
categories of the GHG Protocol *Corporate Value Chain (Scope 3) Standard* and
its *Technical Guidance for Calculating Scope 3 Emissions (v1.0)*.
 
Each category offers one or more **calculation methods** (the leaves of the
guidance's decision trees), ordered from most to least data-specific:
 
    supplier/site-specific  >  hybrid  >  average-data  >  spend-based
 
Every method is still ``activity_data x emission_factor``; the category just
fixes which activity (mass, distance, kWh, EUR, tonne-km ...) and which factor
(cradle-to-gate, life-cycle, waste-treatment, EEIO ...) are paired. Factors are
always injected via the provider — this module never embeds numeric factors.
 
Upstream categories 1-8, downstream categories 9-15.
"""


from enum import Enum

 
class Scope3Category(int, Enum):
    """The 15 Scope 3 categories (upstream 1-8, downstream 9-15)."""
 
    PURCHASED_GOODS_SERVICES = 1
    CAPITAL_GOODS = 2
    FUEL_ENERGY_RELATED = 3
    UPSTREAM_TRANSPORT = 4
    WASTE_GENERATED = 5
    BUSINESS_TRAVEL = 6
    EMPLOYEE_COMMUTING = 7
    UPSTREAM_LEASED_ASSETS = 8
    DOWNSTREAM_TRANSPORT = 9
    PROCESSING_SOLD_PRODUCTS = 10
    USE_OF_SOLD_PRODUCTS = 11
    END_OF_LIFE = 12
    DOWNSTREAM_LEASED_ASSETS = 13
    FRANCHISES = 14
    INVESTMENTS = 15
 
    @property
    def label(self) -> str:
        return f"cat{self.value}_{self.name.lower()}"