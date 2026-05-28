"""Unit tests for chart generation in the GHG Manager."""

import unittest

from ghg_manager.ui.charts import build_scope_chart


class ChartTests(unittest.TestCase):
    def test_build_scope_chart_returns_figure(self):
        totals = {"total_co2e": 1000, "scope_1": 400, "scope_2": 300, "scope_3": 300}
        figure = build_scope_chart(totals)
        self.assertEqual(figure.gca().get_title(), "GHG Emissions by Scope")
        self.assertListEqual([text.get_text() for text in figure.gca().get_xticklabels()], ["scope_1", "scope_2", "scope_3"])


if __name__ == "__main__":
    unittest.main()
