import unittest

from app.engines.action_plan import generate_action_plan
from app.engines.approval_engine import format_approvals
from app.engines.scheme_matcher import match_schemes, score_scheme


PROFILE = {
    "name": "Ramesh",
    "location": "Karnataka",
    "capital": 200000,
    "skills": ["Farming", "Animal Care"],
    "resources": ["2 acres of land", "Available water"],
    "experience": "Basic",
    "goal": "Increase income",
}

BUSINESS = {
    "id": "business-001",
    "name": "Dairy Farming",
    "category": "Agriculture and Livestock",
}

SCHEME = {
    "id": "scheme-001",
    "name": "Agri Support",
    "target_group": "Rural entrepreneurs",
    "sector": "Agriculture and Livestock",
    "location": "Karnataka",
    "minimum_capital": 50000,
    "support_type": "Capital subsidy",
    "eligibility": ["Resident of Karnataka", "Agriculture-related activity"],
    "required_documents": ["Identity proof"],
}


class Phase6EngineTests(unittest.TestCase):
    def test_scheme_score_rewards_location_sector_and_capital(self):
        self.assertEqual(score_scheme(PROFILE, BUSINESS, SCHEME), 85.0)

    def test_scheme_output_is_always_demo_and_synthetic(self):
        result = match_schemes(PROFILE, BUSINESS, [SCHEME])[0]

        self.assertEqual(result["source_type"], "synthetic")
        self.assertEqual(result["verification_status"], "demo")
        self.assertIn("verify with official sources", result["notice"])

    def test_approval_formatter_returns_required_fields(self):
        result = format_approvals(
            [{
                "id": "approval-001",
                "business_id": "business-001",
                "registration": "Udyam Registration",
                "license": "Local trade registration",
                "documents": ["Identity proof"],
                "authority": "Local authority",
                "process_steps": ["Submit application"],
            }]
        )

        self.assertEqual(result[0]["business_id"], "business-001")
        self.assertEqual(result[0]["process_steps"], ["Submit application"])

    def test_action_plan_has_three_to_five_steps(self):
        steps = generate_action_plan(
            {"business": "Dairy Farming"},
            {"financial_status": "FEASIBLE"},
            [{"scheme_name": "Agri Support"}],
            [{"business_id": "business-001"}],
        )

        self.assertGreaterEqual(len(steps), 3)
        self.assertLessEqual(len(steps), 5)
        self.assertTrue(any("documents" in step.lower() for step in steps))


if __name__ == "__main__":
    unittest.main()
