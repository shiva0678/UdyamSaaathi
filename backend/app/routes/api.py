from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from psycopg.types.json import Jsonb

from app.database import get_connection
from app.engines.action_plan import generate_action_plan
from app.engines.approval_engine import format_approvals
from app.engines.financial import calculate_from_records
from app.engines.recommendation import DISCLAIMER, build_recommendation, recommend_businesses
from app.engines.scheme_matcher import DEMO_NOTICE, match_schemes
from app.services.llm_service import (
    ask_llm,
    classify_message,
    extract_profile,
    missing_profile_questions,
)
from app.services.rag_service import retrieve_context
from app.schemas.api import (
    ActionPlanRequest,
    ActionPlanResponse,
    Approval,
    BusinessProfile,
    ChatRequest,
    ChatResponse,
    ChatSource,
    FinancialFeasibilityRequest,
    FinancialFeasibilityResponse,
    MarketData,
    RecommendationResponse,
    Scheme,
    SupportMatchRequest,
    SupportMatchResponse,
    UserProfileCreate,
    UserProfileResponse,
)

router = APIRouter(prefix="/api")


def _profile_from_user(row: dict) -> dict:
    return {
        "name": row.get("name", ""),
        "location": row.get("location", ""),
        "capital": float(row.get("capital", 0)),
        "skills": row.get("skills", []),
        "resources": row.get("resources", []),
        "experience": row.get("experience", ""),
        "goal": row.get("goal", ""),
    }


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    intent = classify_message(request.message)
    profile = request.profile or {}
    user = None
    business = None
    businesses = []
    schemes = []
    approval_rows = []

    needs_database = intent in {
        "financial", "support", "approval", "recommendation", "action_plan"
    }
    try:
        if needs_database:
            with get_connection() as connection:
                with connection.cursor() as cursor:
                    if request.user_id:
                        cursor.execute("SELECT * FROM users WHERE id = %s", (request.user_id,))
                        user = cursor.fetchone()
                    cursor.execute("SELECT * FROM businesses ORDER BY id")
                    businesses = cursor.fetchall()
                    if request.business_id:
                        business = next(
                            (row for row in businesses if row["id"] == request.business_id),
                            None,
                        )
                    if intent in {"support", "action_plan"}:
                        cursor.execute("SELECT * FROM schemes ORDER BY id")
                        schemes = cursor.fetchall()
                    if request.business_id and intent in {"approval", "action_plan"}:
                        cursor.execute(
                            "SELECT * FROM approvals WHERE business_id = %s ORDER BY id",
                            (request.business_id,),
                        )
                        approval_rows = cursor.fetchall()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to load chat context from the database.",
        ) from error

    if user:
        profile = {**_profile_from_user(user), **profile}
    extracted_profile = extract_profile(request.message, profile)

    if intent == "information":
        context = retrieve_context(request.message)
        result = ask_llm(request.message, context)
        sources = [
            ChatSource(
                document_name=item["document_name"],
                source=item["source"],
                score=item["score"],
            )
            for item in context
        ]
        return ChatResponse(intent=intent, sources=sources, **result)

    if intent in {"financial", "support", "recommendation", "action_plan"} and (
        not profile.get("capital") or not profile.get("location")
    ):
        fallback = ask_llm(request.message, extracted_profile)
        fallback["profile"] = extracted_profile
        fallback["follow_up_questions"] = missing_profile_questions(extracted_profile)
        return ChatResponse(
            intent=intent,
            **fallback,
        )

    if business is None and businesses:
        message_text = request.message.lower()
        business = next(
            (row for row in businesses if row["name"].lower() in message_text),
            None,
        )

    if intent == "recommendation":
        recommendations = recommend_businesses(extracted_profile, businesses)
        first = recommendations[0] if recommendations else None
        message = (
            f"The strongest prototype match is {first['business']} with a "
            f"match score of {first['match_score']}."
            if first
            else "I could not find a recommendation from the available records."
        )
        return ChatResponse(
            message=message,
            intent=intent,
            profile=extracted_profile,
            provider="rule-based engine",
        )

    if business is None:
        return ChatResponse(
            message="Which business would you like me to check? Please provide its business_id or name.",
            intent=intent,
            profile=extracted_profile,
            follow_up_questions=["Which business should I check?"],
            provider="rule-based fallback",
        )

    if intent == "financial":
        financial = calculate_from_records(
            {"capital": extracted_profile["capital"]}, business
        )
        return ChatResponse(
            message=(
                f"{business['name']} is {financial['financial_status']} based on the "
                f"synthetic estimate. Monthly profit is {financial['monthly_profit']} "
                f"and the estimated capital gap is {financial['capital_gap']}."
            ),
            intent=intent,
            profile=extracted_profile,
            provider="deterministic financial engine",
        )

    if intent == "support":
        matches = match_schemes(extracted_profile, business, schemes)
        names = ", ".join(item["scheme_name"] for item in matches[:3])
        return ChatResponse(
            message=f"Potential demo support records for {business['name']}: {names}. Verify official sources before applying.",
            intent=intent,
            profile=extracted_profile,
            provider="rule-based support matcher",
        )

    if intent == "approval":
        approvals = format_approvals(approval_rows)
        message = (
            f"For {business['name']}, review: "
            + "; ".join(item["license"] for item in approvals)
            if approvals
            else "No synthetic approval record is available for this business. Verify with the relevant authority."
        )
        return ChatResponse(
            message=message,
            intent=intent,
            profile=extracted_profile,
            provider="rule-based approval navigator",
        )

    recommendations = recommend_businesses(extracted_profile, [business], limit=1)
    financial = calculate_from_records(
        {"capital": extracted_profile["capital"]}, business
    )
    support = match_schemes(extracted_profile, business, schemes)
    action_plan = generate_action_plan(
        recommendations[0], financial, support, format_approvals(approval_rows)
    )
    return ChatResponse(
        message="\n".join(f"{index}. {step}" for index, step in enumerate(action_plan, 1)),
        intent=intent,
        profile=extracted_profile,
        provider="rule-based action-plan engine",
    )


@router.post("/support/match", response_model=SupportMatchResponse)
def match_support(request: SupportMatchRequest) -> SupportMatchResponse:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM businesses WHERE id = %s", (request.business_id,))
                business = cursor.fetchone()
                cursor.execute("SELECT * FROM schemes ORDER BY id")
                schemes = cursor.fetchall()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to load support data from the database.",
        ) from error

    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")

    matches = match_schemes(request.profile.model_dump(), business, schemes)
    return SupportMatchResponse(matches=matches, notice=DEMO_NOTICE)


@router.post("/action-plan", response_model=ActionPlanResponse)
def create_action_plan(request: ActionPlanRequest) -> ActionPlanResponse:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (request.user_id,))
                user = cursor.fetchone()
                cursor.execute("SELECT * FROM businesses WHERE id = %s", (request.business_id,))
                business = cursor.fetchone()
                cursor.execute("SELECT * FROM schemes ORDER BY id")
                schemes = cursor.fetchall()
                cursor.execute(
                    "SELECT * FROM approvals WHERE business_id = %s ORDER BY id",
                    (request.business_id,),
                )
                approval_rows = cursor.fetchall()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to load action-plan data from the database.",
        ) from error

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")

    profile = request.profile.model_dump()
    recommendation = build_recommendation(profile, business, [])
    financial = calculate_from_records(user, business)
    support = match_schemes(profile, business, schemes)
    approvals = format_approvals(approval_rows)
    return ActionPlanResponse(
        business=business["name"],
        steps=generate_action_plan(recommendation, financial, support, approvals),
        notice=DEMO_NOTICE,
    )


@router.post(
    "/financial/feasibility",
    response_model=FinancialFeasibilityResponse,
)
def financial_feasibility(
    request: FinancialFeasibilityRequest,
) -> FinancialFeasibilityResponse:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT capital FROM users WHERE id = %s", (request.user_id,))
                user = cursor.fetchone()
                cursor.execute(
                    """
                    SELECT minimum_capital, monthly_cost, monthly_revenue
                    FROM businesses
                    WHERE id = %s
                    """,
                    (request.business_id,),
                )
                business = cursor.fetchone()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to load financial data from the database.",
        ) from error

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")

    return FinancialFeasibilityResponse(
        **calculate_from_records(user, business)
    )


@router.post("/recommendations", response_model=RecommendationResponse)
def get_recommendations(profile: UserProfileCreate) -> RecommendationResponse:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM businesses ORDER BY id")
                businesses = cursor.fetchall()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to load businesses for recommendations.",
        ) from error

    recommendations = recommend_businesses(profile.model_dump(), businesses)
    return RecommendationResponse(
        recommendations=recommendations,
        disclaimer=DISCLAIMER,
    )


@router.post(
    "/users/profile",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_profile(profile: UserProfileCreate) -> UserProfileResponse:
    profile_id = f"user-{uuid4().hex}"
    query = """
        INSERT INTO users (
            id, name, location, capital, land, water, skills, resources,
            experience, goal, profile_type
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, name, location, capital, skills, resources, experience,
                  goal, profile_type
    """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        profile_id,
                        profile.name,
                        profile.location,
                        profile.capital,
                        0,
                        "Unknown",
                        Jsonb(profile.skills),
                        Jsonb(profile.resources),
                        profile.experience,
                        profile.goal,
                        "User Profile",
                    ),
                )
                row = cursor.fetchone()
            connection.commit()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to save the user profile to the database.",
        ) from error

    return UserProfileResponse(**row)


@router.get("/businesses", response_model=list[BusinessProfile])
def list_businesses() -> list[BusinessProfile]:
    query = "SELECT * FROM businesses ORDER BY id"
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to load businesses from the database.",
        ) from error
    return [BusinessProfile(**row) for row in rows]


@router.get("/businesses/{business_id}", response_model=BusinessProfile)
def get_business(business_id: str) -> BusinessProfile:
    query = "SELECT * FROM businesses WHERE id = %s"
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (business_id,))
                row = cursor.fetchone()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to load the business from the database.",
        ) from error

    if row is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return BusinessProfile(**row)


@router.get("/schemes", response_model=list[Scheme])
def list_schemes() -> list[Scheme]:
    query = "SELECT * FROM schemes ORDER BY id"
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to load schemes from the database.",
        ) from error
    return [Scheme(**row) for row in rows]


@router.get("/approvals/{business_id}", response_model=list[Approval])
def list_approvals(business_id: str) -> list[Approval]:
    query = "SELECT * FROM approvals WHERE business_id = %s ORDER BY id"
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (business_id,))
                rows = cursor.fetchall()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to load approvals from the database.",
        ) from error
    return [Approval(**row) for row in format_approvals(rows)]


@router.get("/market/{location}", response_model=list[MarketData])
def list_market_data(location: str) -> list[MarketData]:
    query = """
        SELECT * FROM market_data
        WHERE LOWER(location) = LOWER(%s)
        ORDER BY id
    """
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (location,))
                rows = cursor.fetchall()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to load market data from the database.",
        ) from error
    return [MarketData(**row) for row in rows]
