from typing import Any


def generate_action_plan(
    recommendation: dict[str, Any],
    financial: dict[str, Any],
    support: list[dict[str, Any]],
    approvals: list[dict[str, Any]],
) -> list[str]:
    steps = [
        f"Review the {recommendation['business']} recommendation and its prototype suitability score.",
    ]

    if financial["financial_status"] == "ADDITIONAL FINANCING REQUIRED":
        steps.append("Explore financing options for the estimated capital gap.")
    else:
        steps.append("Set aside the estimated initial investment and confirm the operating budget.")

    if support:
        steps.append("Check the suitable support records and verify details with official sources before applying.")
    else:
        steps.append("Check official sources for support that may apply to this business.")

    if approvals:
        steps.append("Prepare the listed documents and complete the applicable registration or approval.")
    else:
        steps.append("Confirm required registrations and approvals with the relevant local authority.")

    steps.append("Begin business setup only after confirming costs, support, and approvals.")
    return steps[:5]
