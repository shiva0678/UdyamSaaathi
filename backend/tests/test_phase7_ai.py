import unittest
from unittest.mock import Mock, patch

from app.services.llm_service import AIServiceError, ask_llm, classify_message, detect_language, extract_profile, fallback_response


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

    def test_profile_extracts_lakh_as_rupees(self):
        result = extract_profile("I have ₹2 lakh capital and 2 acres of land.")

        self.assertEqual(result["capital"], 200000.0)

    def test_missing_configuration_is_explicit(self):
        with patch("app.services.llm_service.LLM_API_KEY", ""), patch("app.services.llm_service.LLM_MODEL", ""):
            with self.assertRaisesRegex(AIServiceError, "AI is not configured"):
                ask_llm("Hello")

    def test_llm_response_is_returned_without_fallback(self):
        fake_client = Mock()
        fake_client.chat.completions.create.return_value.choices = [
            Mock(message=Mock(content="Real model response"))
        ]
        with patch("app.services.llm_service._client", return_value=fake_client):
            result = ask_llm("Hello", history=[{"role": "user", "content": "Hi"}])

        self.assertEqual(result["message"], "Real model response")
        self.assertTrue(result["success"])
        self.assertTrue(result["ai_enabled"])

    def test_kannada_language_and_profile_detection(self):
        message = "ನನ್ನ ಬಳಿ 2 ಎಕರೆ ಜಮೀನು ಮತ್ತು ₹2 ಲಕ್ಷ ಬಂಡವಾಳ ಇದೆ. ನನಗೆ ಯಾವ ವ್ಯವಹಾರ ಸೂಕ್ತ?"

        self.assertEqual(detect_language(message), "kn")
        self.assertEqual(classify_message(message), "recommendation")
        self.assertEqual(extract_profile(message)["capital"], 200000.0)

    def test_llm_prompt_uses_kannada_language(self):
        fake_client = Mock()
        fake_client.chat.completions.create.return_value.choices = [
            Mock(message=Mock(content="ನಿಮಗೆ ಸೂಕ್ತವಾದ ವ್ಯವಹಾರವನ್ನು ಪರಿಶೀಲಿಸೋಣ."))
        ]
        with patch("app.services.llm_service._client", return_value=fake_client):
            result = ask_llm("ನನಗೆ ಯಾವ ವ್ಯವಹಾರ ಸೂಕ್ತ?", language="kn")

        prompt = fake_client.chat.completions.create.call_args.kwargs["messages"][0]["content"]
        self.assertIn("Kannada", prompt)
        self.assertEqual(result["language"], "kn")

    def test_intent_classification_routes_deterministic_topics(self):
        self.assertEqual(classify_message("Can I afford dairy farming?"), "financial")
        self.assertEqual(classify_message("What support is available?"), "support")
        self.assertEqual(classify_message("Which license or approval do I need?"), "approval")
        self.assertEqual(classify_message("What documents should I prepare?"), "information")
        self.assertEqual(classify_message("What should I do first?"), "action_plan")


if __name__ == "__main__":
    unittest.main()
