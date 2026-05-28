from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parent.parent
root.joinpath("templates").mkdir(exist_ok=True)

factors = pd.DataFrame([
    {
        "key": "diesel",
        "category": "Transport",
        "source": "Diesel fuel",
        "value": 2.68,
        "unit": "kgCO2e/L",
        "scope": "scope_1",
    },
    {
        "key": "electricity_grid",
        "category": "Energy",
        "source": "Grid electricity",
        "value": 0.45,
        "unit": "kgCO2e/kWh",
        "scope": "scope_2",
    },
    {
        "key": "air_travel",
        "category": "Travel",
        "source": "Air travel",
        "value": 0.25,
        "unit": "kgCO2e/passenger_km",
        "scope": "scope_3",
    },
])

activities = pd.DataFrame([
    {
        "name": "Company vehicle fuel",
        "activity_type": "Fuel",
        "amount": 1200,
        "unit": "L",
        "emission_factor_key": "diesel",
        "scope": "scope_1",
    },
    {
        "name": "Office electricity",
        "activity_type": "Electricity",
        "amount": 3500,
        "unit": "kWh",
        "emission_factor_key": "electricity_grid",
        "scope": "scope_2",
    },
    {
        "name": "Business flights",
        "activity_type": "Travel",
        "amount": 15000,
        "unit": "passenger_km",
        "emission_factor_key": "air_travel",
        "scope": "scope_3",
    },
])

factors.to_excel(root / "templates" / "emission_factors_template.xlsx", index=False)
activities.to_excel(root / "templates" / "activity_data_template.xlsx", index=False)
print("Created templates:", root / "templates")
