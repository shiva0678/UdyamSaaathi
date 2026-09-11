import unittest

from app.engines.financial import (
    ADDITIONAL_FINANCING_REQUIRED,
    FEASIBLE,
    calculate_financial_feasibility,
)


class FinancialEngineTests(unittest.TestCase):
    def test_feasible_business_calculates_annual_values_and_roi(self):
        result = calculate_financial_feasibility(
            available_capital=200000,
            initial_investment=120000,
            monthly_cost=42000,
            monthly_revenue=70000,
        )

        self.assertEqual(result["monthly_profit"], 28000)
        self.assertEqual(result["annual_revenue"], 840000)
        self.assertEqual(result["annual_cost"], 504000)
        self.assertEqual(result["annual_profit"], 336000)
        self.assertEqual(result["capital_gap"], 0)
        self.assertEqual(result["roi"], 280.0)
        self.assertEqual(result["financial_status"], FEASIBLE)
        self.assertIn("Synthetic estimates", result["notice"])

    def test_insufficient_capital_requires_additional_financing(self):
        result = calculate_financial_feasibility(
            available_capital=50000,
            initial_investment=120000,
            monthly_cost=42000,
            monthly_revenue=70000,
        )

        self.assertEqual(result["capital_gap"], 70000)
        self.assertEqual(result["financial_status"], ADDITIONAL_FINANCING_REQUIRED)
        self.assertTrue(any("Additional capital" in note for note in result["risk_notes"]))

    def test_negative_profit_is_reported_as_a_risk(self):
        result = calculate_financial_feasibility(
            available_capital=100000,
            initial_investment=100000,
            monthly_cost=60000,
            monthly_revenue=40000,
        )

        self.assertEqual(result["monthly_profit"], -20000)
        self.assertEqual(result["annual_profit"], -240000)
        self.assertTrue(any("operating costs exceed" in note for note in result["risk_notes"]))

    def test_zero_investment_has_safe_zero_roi(self):
        result = calculate_financial_feasibility(
            available_capital=100000,
            initial_investment=0,
            monthly_cost=1000,
            monthly_revenue=2000,
        )

        self.assertEqual(result["roi"], 0.0)
        self.assertEqual(result["financial_status"], FEASIBLE)
        self.assertTrue(any("ROI is shown as 0" in note for note in result["risk_notes"]))


if __name__ == "__main__":
    unittest.main()
