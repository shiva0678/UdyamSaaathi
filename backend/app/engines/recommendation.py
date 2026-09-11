import re
from dataclasses import dataclass
from typing import Any

WEIGHTS = {
    "capital": 0.30,
    "skills": 0.25,
    "resources": 0.20,
    "location": 0.15,
    "experience": 0.10,
}
DISCLAIMER = "Match score is a prototype suitability score, not a guarantee of success."


@dataclass(frozen=True)
class ScoreBreakdown:
    capital_score: float
    skill_score: float
    resource_score: float
    location_score: float
    experience_score: float
    final_score: float


def _normalise(value: str) -> str:
    return value.strip().lower()


def _score_capital(capital: float, minimum: float, maximum: float) -> float:
    if capital < minimum:
        return max(0.0, capital / minimum * 60) if minimum else 100.0
    if capital >= maximum:
        return 100.0
    return 60.0 + ((capital - minimum) / (maximum - minimum)) * 40.0


def _score_skills(user_skills: list[str], required_skills: list[str]) -> float:
    if not required_skills:
        return 100.0
    available = {_normalise(skill) for skill in user_skills}
    matches = sum(
        1
        for required in required_skills
        if _normalise(required) in available
        or any(_normalise(required) in skill or skill in _normalise(required) for skill in available)
    )
    return matches / len(required_skills) * 100.0


def _land_from_resources(resources: list[str]) -> float | None:
    text = " ".join(resources).lower()
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:acres?|acre)", text)
    return float(match.group(1)) if match else None


def _water_available(resources: list[str]) -> bool:
    text = " ".join(resources).lower()
    return any(term in text for term in ("water", "irrigation", "well", "borewell"))


def _score_resources(user_resources: list[str], required_land: float, water_required: str) -> float:
    land = _land_from_resources(user_resources)
    land_score = 50.0 if land is None else (100.0 if land >= required_land else land / required_land * 100)
    water_score = 100.0 if _normalise(water_required) == "low" else (100.0 if _water_available(user_resources) else 0.0)
    return (land_score + water_score) / 2


def _score_location(user_location: str, business_location: str) -> float:
    return 100.0 if _normalise(user_location) == _normalise(business_location) else 0.0


def _score_experience(user_experience: str, required_experience: str) -> float:
    levels = {"basic": 1, "intermediate": 2, "advanced": 3}
    user_level = levels.get(_normalise(user_experience), 1)
    required_level = levels.get(_normalise(required_experience), 1)
    if user_level >= required_level:
        return 100.0
    return max(0.0, 100.0 - (required_level - user_level) * 40.0)


def score_business(profile: dict[str, Any], business: dict[str, Any]) -> ScoreBreakdown:
    capital_score = _score_capital(
        float(profile["capital"]),
        float(business["minimum_capital"]),
        float(business["maximum_capital"]),
    )
    skill_score = _score_skills(profile["skills"], business["required_skills"])
    resource_score = _score_resources(
        profile["resources"], float(business["required_land"]), business["water_required"]
    )
    location_score = _score_location(profile["location"], business["location"])
    experience_score = _score_experience(profile["experience"], business["experience_level"])
    final_score = (
        capital_score * WEIGHTS["capital"]
        + skill_score * WEIGHTS["skills"]
        + resource_score * WEIGHTS["resources"]
        + location_score * WEIGHTS["location"]
        + experience_score * WEIGHTS["experience"]
    )
    return ScoreBreakdown(
        capital_score=round(capital_score, 2),
        skill_score=round(skill_score, 2),
        resource_score=round(resource_score, 2),
        location_score=round(location_score, 2),
        experience_score=round(experience_score, 2),
        final_score=round(final_score, 2),
    )


def _recommendation_reasons(
    profile: dict[str, Any], business: dict[str, Any], scores: ScoreBreakdown
) -> tuple[list[str], list[str], list[str]]:
    reasons: list[str] = []
    strengths: list[str] = []
    limitations: list[str] = []

    if scores.capital_score >= 80:
        reasons.append("Your available capital matches the estimated requirement")
        strengths.append("Capital is within the estimated investment range")
    else:
        limitations.append("Your available capital may need to increase for the estimated investment")

    matching_skills = [
        required
        for required in business["required_skills"]
        if any(_normalise(required) in _normalise(skill) or _normalise(skill) in _normalise(required) for skill in profile["skills"])
    ]
    if matching_skills:
        reasons.append(f"Your {matching_skills[0].lower()} skill is relevant")
        strengths.append("Your existing skills overlap with the business requirements")
    else:
        limitations.append("You may need training for the required skills")

    if scores.resource_score >= 80:
        reasons.append("Your available land and water resources are suitable")
        strengths.append("Your listed resources support this business")
    else:
        limitations.append("Your listed land or water resources may need improvement")

    if scores.location_score == 100:
        reasons.append(f"The business is planned for {business['location']}, matching your location")
    else:
        limitations.append("The business location differs from your stated location")

    if scores.experience_score >= 80:
        strengths.append("Your experience level fits the estimated requirement")
    else:
        limitations.append("Additional experience or mentoring may be useful")

    return reasons, strengths, limitations


def build_recommendation(
    profile: dict[str, Any], business: dict[str, Any], alternatives: list[str]
) -> dict[str, Any]:
    scores = score_business(profile, business)
    reasons, strengths, limitations = _recommendation_reasons(profile, business, scores)
    return {
        "business": business["name"],
        "business_id": business["id"],
        "match_score": scores.final_score,
        "reasons": reasons,
        "strengths": strengths,
        "limitations": limitations,
        "alternatives": alternatives,
        "score_breakdown": {
            "capital_score": scores.capital_score,
            "skill_score": scores.skill_score,
            "resource_score": scores.resource_score,
            "location_score": scores.location_score,
            "experience_score": scores.experience_score,
        },
        "disclaimer": DISCLAIMER,
    }


def recommend_businesses(profile: dict[str, Any], businesses: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    ranked = sorted(
        businesses,
        key=lambda business: (-score_business(profile, business).final_score, business["id"]),
    )[:limit]
    names = [business["name"] for business in ranked]
    return [
        build_recommendation(
            profile,
            business,
            [name for name in names if name != business["name"]],
        )
        for business in ranked
    ]
