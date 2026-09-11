from typing import Any

DEMO_NOTICE = "Demo information - verify with official sources before applying."


def _text_matches(text: str, values: list[str]) -> int:
    normalised = text.lower()
    return sum(1 for value in values if value.lower() in normalised)


def _target_group_score(profile: dict[str, Any], business: dict[str, Any], scheme: dict[str, Any]) -> float:
    target = scheme["target_group"].lower()
    profile_text = " ".join(
        [
            profile.get("name", ""),
            profile.get("location", ""),
            profile.get("experience", ""),
            profile.get("goal", ""),
            *profile.get("skills", []),
            *profile.get("resources", []),
        ]
    ).lower()
    category = business["category"].lower()

    if "all sectors" in target or "rural entrepreneur" in target:
        return 100.0
    if "farmer" in target and "agriculture" in category:
        return 100.0
    if "livestock" in target and ("livestock" in category or "animal" in profile_text):
        return 100.0
    if "artisan" in target and ("craft" in category or "craft" in profile_text):
        return 100.0
    if "food" in target and "food" in category:
        return 100.0
    if target.rstrip("s") in profile_text:
        return 100.0
    return 0.0


def score_scheme(profile: dict[str, Any], business: dict[str, Any], scheme: dict[str, Any]) -> float:
    location_score = 100.0 if profile["location"].lower() == scheme["location"].lower() else 0.0
    sector_score = 100.0 if (
        scheme["sector"].lower() in ("all sectors", business["category"].lower())
        or business["category"].lower() in scheme["sector"].lower()
    ) else 0.0
    minimum_capital = float(scheme["minimum_capital"])
    capital_score = 100.0 if float(profile["capital"]) >= minimum_capital else max(
        0.0, float(profile["capital"]) / minimum_capital * 100
    )
    target_score = _target_group_score(profile, business, scheme)
    eligibility_score = min(
        100.0,
        _text_matches(
            " ".join(
                [
                    profile["location"],
                    business["name"],
                    business["category"],
                    *profile.get("skills", []),
                    *profile.get("resources", []),
                ]
            ),
            scheme["eligibility"],
        )
        / max(len(scheme["eligibility"]), 1)
        * 100,
    )
    return round(
        location_score * 0.30
        + sector_score * 0.25
        + capital_score * 0.20
        + target_score * 0.10
        + eligibility_score * 0.15,
        2,
    )


def match_schemes(
    profile: dict[str, Any], business: dict[str, Any], schemes: list[dict[str, Any]], limit: int = 5
) -> list[dict[str, Any]]:
    ranked = sorted(
        schemes,
        key=lambda scheme: (-score_scheme(profile, business, scheme), scheme["id"]),
    )[:limit]
    return [
        {
            "scheme_name": scheme["name"],
            "scheme_id": scheme["id"],
            "match_score": score_scheme(profile, business, scheme),
            "support_type": scheme["support_type"],
            "eligibility": scheme["eligibility"],
            "required_documents": scheme["required_documents"],
            "verification_status": "demo",
            "source_type": "synthetic",
            "notice": DEMO_NOTICE,
        }
        for scheme in ranked
    ]
