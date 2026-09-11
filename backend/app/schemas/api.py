from typing import Any

from pydantic import BaseModel, Field


class UserProfileCreate(BaseModel):
    name: str = Field(min_length=1)
    location: str = Field(min_length=1)
    capital: float = Field(ge=0)
    skills: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)
    experience: str = Field(min_length=1)
    goal: str = Field(min_length=1)


class UserProfileResponse(UserProfileCreate):
    id: str
    profile_type: str


class Recommendation(BaseModel):
    business: str
    business_id: str
    match_score: float
    reasons: list[str]
    strengths: list[str]
    limitations: list[str]
    alternatives: list[str]
    score_breakdown: dict[str, float]
    disclaimer: str


class RecommendationResponse(BaseModel):
    recommendations: list[Recommendation]
    disclaimer: str


class FinancialFeasibilityRequest(BaseModel):
    user_id: str = Field(min_length=1)
    business_id: str = Field(min_length=1)


class FinancialFeasibilityResponse(BaseModel):
    initial_investment: float
    monthly_cost: float
    monthly_revenue: float
    monthly_profit: float
    annual_revenue: float
    annual_cost: float
    annual_profit: float
    capital_gap: float
    roi: float
    financial_status: str
    risk_notes: list[str]
    notice: str


class SupportMatchRequest(BaseModel):
    profile: UserProfileCreate
    business_id: str = Field(min_length=1)


class SupportMatch(BaseModel):
    scheme_name: str
    scheme_id: str
    match_score: float
    support_type: str
    eligibility: list[str]
    required_documents: list[str]
    verification_status: str
    source_type: str
    notice: str


class SupportMatchResponse(BaseModel):
    matches: list[SupportMatch]
    notice: str


class ActionPlanRequest(BaseModel):
    profile: UserProfileCreate
    user_id: str = Field(min_length=1)
    business_id: str = Field(min_length=1)


class ActionPlanResponse(BaseModel):
    business: str
    steps: list[str]
    notice: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    language: str | None = None
    user_id: str | None = None
    business_id: str | None = None
    profile: dict[str, Any] | None = None
    history: list[dict[str, str]] = Field(default_factory=list)


class ChatSource(BaseModel):
    document_name: str
    source: str
    score: float


class ChatResponse(BaseModel):
    message: str
    intent: str
    profile: dict[str, Any] = Field(default_factory=dict)
    follow_up_questions: list[str] = Field(default_factory=list)
    provider: str
    sources: list[ChatSource] = Field(default_factory=list)
    success: bool = True
    ai_enabled: bool = False
    rag_used: bool = False
    error_code: str | None = None


class BusinessProfile(BaseModel):
    id: str
    name: str
    category: str
    location: str
    minimum_capital: float
    maximum_capital: float
    required_land: float
    water_required: str
    required_skills: list[str]
    experience_level: str
    monthly_cost: float
    monthly_revenue: float
    demand_level: str


class Scheme(BaseModel):
    id: str
    name: str
    target_group: str
    sector: str
    location: str
    minimum_capital: float
    support_type: str
    maximum_support: float
    eligibility: list[str]
    required_documents: list[str]
    source_type: str
    verification_status: str


class Approval(BaseModel):
    id: str
    business_id: str
    registration: str
    license: str
    documents: list[str]
    authority: str
    process_steps: list[str]


class MarketData(BaseModel):
    id: str
    location: str
    business_category: str
    demand_level: str
    competition_level: str
    market_score: float
