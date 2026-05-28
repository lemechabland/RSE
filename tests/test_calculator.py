"""Unit tests for the GHG calculator logic."""

import unittest

from ghg_manager.models.activity import Activity
from ghg_manager.models.emission_factor import EmissionFactor
from ghg_manager.services.calculator import GHGCalculator


class CalculatorTests(unittest.TestCase):
    def test_compute_report_counts_scope_totals(self):
        calculator = GHGCalculator()
        activities = [
            Activity(name="Fuel", activity_type="energy", amount=100, unit="l", emission_factor_key="fuel", scope="scope_1"),
            Activity(name="Electricity", activity_type="energy", amount=200, unit="kWh", emission_factor_key="electricity", scope="scope_2"),
        ]
        factors = {
            "fuel": EmissionFactor(category="Energy", source="Diesel", value=2.68, unit="kgCO2e/L", scope="scope_1"),
            "electricity": EmissionFactor(category="Energy", source="Grid", value=0.5, unit="kgCO2e/kWh", scope="scope_2"),
        }
        totals = calculator.compute_report(activities, factors)
        self.assertAlmostEqual(totals["scope_1"], 268.0)
        self.assertAlmostEqual(totals["scope_2"], 100.0)
        self.assertAlmostEqual(totals["total_co2e"], 368.0)


if __name__ == "__main__":
    unittest.main()
