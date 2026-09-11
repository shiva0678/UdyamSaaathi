from typing import Any

SYNTHETIC_ESTIMATE_NOTICE = "Synthetic estimates for prototype demonstration."
FEASIBLE = "FEASIBLE"
ADDITIONAL_FINANCING_REQUIRED = "ADDITIONAL FINANCING REQUIRED"


def calculate_financial_feasibility(
    available_capital: float,
    initial_investment: float,
    monthly_cost: float,
    monthly_revenue: float,
) -> dict[str, Any]:
    monthly_profit = monthly_revenue - monthly_cost
    annual_revenue = monthly_revenue * 12
    annual_cost = monthly_cost * 12
    annual_profit = monthly_profit * 12
    capital_gap = max(initial_investment - available_capital, 0)
    roi = annual_profit / initial_investment * 100 if initial_investment > 0 else 0.0
    financial_status = (
        FEASIBLE
        if available_capital >= initial_investment
        else ADDITIONAL_FINANCING_REQUIRED
    )

    risk_notes: list[str] = []
    if monthly_profit < 0:
        risk_notes.append("Estimated monthly operating costs exceed expected monthly revenue")
    if capital_gap > 0:
        risk_notes.append("Additional capital is required to meet the estimated initial investment")
    if initial_investment == 0:
        risk_notes.append("ROI is shown as 0 because the estimated initial investment is zero")
    if not risk_notes:
        risk_notes.append("No immediate risk identified from the supplied synthetic estimates")

    return {
        "initial_investment": round(initial_investment, 2),
        "monthly_cost": round(monthly_cost, 2),
        "monthly_revenue": round(monthly_revenue, 2),
        "monthly_profit": round(monthly_profit, 2),
        "annual_revenue": round(annual_revenue, 2),
        "annual_cost": round(annual_cost, 2),
        "annual_profit": round(annual_profit, 2),
        "capital_gap": round(capital_gap, 2),
        "roi": round(roi, 2),
        "financial_status": financial_status,
        "risk_notes": risk_notes,
        "notice": SYNTHETIC_ESTIMATE_NOTICE,
    }


def calculate_from_records(user: dict[str, Any], business: dict[str, Any]) -> dict[str, Any]:
    return calculate_financial_feasibility(
        available_capital=float(user["capital"]),
        initial_investment=float(business["minimum_capital"]),
        monthly_cost=float(business["monthly_cost"]),
        monthly_revenue=float(business["monthly_revenue"]),
    )
