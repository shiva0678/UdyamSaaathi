import unittest

from app.engines.recommendation import recommend_businesses, score_business


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
    "location": "Karnataka",
    "minimum_capital": 120000,
    "maximum_capital": 450000,
    "required_land": 1.0,
    "water_required": "Available",
    "required_skills": ["Animal Care", "Basic Farming"],
    "experience_level": "Basic",
    "monthly_cost": 42000,
    "monthly_revenue": 70000,
    "demand_level": "High",
}


class RecommendationEngineTests(unittest.TestCase):
    def test_matching_profile_scores_each_component(self):
        scores = score_business(PROFILE, BUSINESS)

        self.assertEqual(scores.capital_score, 69.7)
        self.assertEqual(scores.skill_score, 100.0)
        self.assertEqual(scores.resource_score, 100.0)
        self.assertEqual(scores.location_score, 100.0)
        self.assertEqual(scores.experience_score, 100.0)
        self.assertEqual(scores.final_score, 90.91)

    def test_capital_below_minimum_reduces_capital_score(self):
        profile = {**PROFILE, "capital": 60000}

        scores = score_business(profile, BUSINESS)

        self.assertEqual(scores.capital_score, 30.0)
        self.assertLess(scores.final_score, 88.0)

    def test_recommendations_return_three_in_score_order(self):
        businesses = [
            BUSINESS,
            {**BUSINESS, "id": "business-002", "name": "Poultry Farming", "minimum_capital": 100000},
            {**BUSINESS, "id": "business-003", "name": "Goat Farming", "minimum_capital": 90000},
            {
                **BUSINESS,
                "id": "business-004",
                "name": "Mushroom Farming",
                "minimum_capital": 80000,
                "maximum_capital": 250000,
                "required_skills": ["Mushroom Cultivation"],
            },
        ]

        recommendations = recommend_businesses(PROFILE, businesses)

        self.assertEqual(len(recommendations), 3)
        self.assertEqual(recommendations[0]["business"], "Goat Farming")
        self.assertGreaterEqual(
            recommendations[0]["match_score"], recommendations[1]["match_score"]
        )
        self.assertEqual(len(recommendations[0]["alternatives"]), 2)
        self.assertIn("Match score is a prototype suitability score", recommendations[0]["disclaimer"])


if __name__ == "__main__":
    unittest.main()
