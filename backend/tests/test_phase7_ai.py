import unittest

from app.services.llm_service import classify_message, fallback_response


class Phase7ServiceTests(unittest.TestCase):
    def test_fallback_asks_for_missing_capital_first(self):
        result = fallback_response("I want to start a business")

        self.assertEqual(result["provider"], "rule-based fallback")
        self.assertEqual(result["message"], "What is your available investment?")
        self.assertTrue(result["follow_up_questions"])

    def test_fallback_extracts_capital_and_skills(self):
        result = fallback_response(
            "My capital is 200000 and my skills are Farming and Animal Care",
            {"location": "Karnataka"},
        )

        self.assertEqual(result["profile"]["capital"], 200000.0)
        self.assertEqual(result["profile"]["skills"], ["Farming", "Animal Care"])

    def test_intent_classification_routes_deterministic_topics(self):
        self.assertEqual(classify_message("Can I afford dairy farming?"), "financial")
        self.assertEqual(classify_message("What support is available?"), "support")
        self.assertEqual(classify_message("Which license or approval do I need?"), "approval")
        self.assertEqual(classify_message("What documents should I prepare?"), "information")
        self.assertEqual(classify_message("What should I do first?"), "action_plan")


if __name__ == "__main__":
    unittest.main()
