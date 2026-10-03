"""Unit tests for the GHG calculator logic."""

import unittest

from ghg_manager.models.activity import ActivityData
from ghg_manager.models.emission import EmissionFactor, DataQuality, Scope
from ghg_manager.services.calculator import GHGCalculator


class DummyFactorProvider:
    def __init__(self, factors):
        self._factors = factors

    def get(self, key: str) -> EmissionFactor:
        return self._factors[key]


class CalculatorTests(unittest.TestCase):
    def test_compute_activity_emissions_returns_emission_result(self):
        factors = {
            "fuel": EmissionFactor(
                category="Energy",
                source="Diesel",
                value=2.68,
                unit="l",
            )
        }
        calculator = GHGCalculator(scope=Scope.SCOPE_1, factors=DummyFactorProvider(factors))
        activity = ActivityData(value=100.0, unit="l", label="Fuel consumption")

        result = calculator.compute_activity_emissions(
            factor_key="fuel",
            activity=activity,
            kwargs={
                "category": "transport",
                "method": "direct",
                "data_quality": DataQuality.PRIMARY,
            },
        )

        self.assertAlmostEqual(result.kg_co2e, 268.0)
        self.assertEqual(result.scope, Scope.SCOPE_1)
        self.assertEqual(result.category, "transport")
        self.assertEqual(result.method, "direct")

    def test_total_emissions_aggregates_results(self):
        factors = {
            "fuel": EmissionFactor(
                category="Energy",
                source="Diesel",
                value=2.68,
                unit="l",
            )
        }
        calculator = GHGCalculator(scope=Scope.SCOPE_1, factors=DummyFactorProvider(factors))
        results = [
            calculator.compute_activity_emissions(
                factor_key="fuel",
                activity=ActivityData(value=100.0, unit="l", label="Fuel"),
                kwargs={
                    "category": "transport",
                    "method": "direct",
                    "data_quality": DataQuality.PRIMARY,
                },
            )
        ]
        total = calculator.total_emissions(results, scope_flag="scope_1")

        self.assertAlmostEqual(total.kg_co2e, 268.0)
        self.assertEqual(total.scope, Scope.SCOPE_1)
        self.assertEqual(total.category, "scope_1")


if __name__ == "__main__":
    unittest.main()
