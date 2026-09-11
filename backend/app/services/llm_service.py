import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "").strip().lower()
LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "").strip()

FALLBACK_QUESTIONS = [
    "What is your available investment?",
    "What skills do you have?",
    "Do you have land or other resources?",
    "How much experience do you have?",
]


def classify_message(message: str) -> str:
    text = message.lower()
    if any(term in text for term in ("afford", "cost", "profit", "roi", "capital", "finance")):
        return "financial"
    if any(term in text for term in ("support", "scheme", "subsidy", "grant", "loan")):
        return "support"
    if any(term in text for term in ("approval", "license", "registration", "permission")):
        return "approval"
    if "document" in text:
        return "information"
    if any(term in text for term in ("business", "suitable", "recommend", "opportunity")):
        return "recommendation"
    if any(term in text for term in ("first", "next", "start", "setup", "step")):
        return "action_plan"
    return "information"


def extract_profile(message: str, current_profile: dict[str, Any] | None = None) -> dict[str, Any]:
    profile = {
        "name": "",
        "location": "",
        "capital": None,
        "skills": [],
        "resources": [],
        "experience": "",
        "goal": "",
    }
    if current_profile:
        profile.update(current_profile)

    capital_match = re.search(r"(?:rs\.?|inr|₹)?\s*([\d,]+)\s*(?:rupees?|rs)?", message.lower())
    if capital_match and any(term in message.lower() for term in ("capital", "invest", "budget", "rupee", "rs", "₹")):
        profile["capital"] = float(capital_match.group(1).replace(",", ""))

    skill_match = re.search(r"skills?\s*(?:are|:)?\s*([^.!?]+)", message, re.IGNORECASE)
    if skill_match:
        profile["skills"] = [item.strip() for item in re.split(r",| and ", skill_match.group(1)) if item.strip()]

    if any(term in message.lower() for term in ("land", "acre", "water", "well", "irrigation")):
        profile["resources"] = [message.strip()]
    return profile


def missing_profile_questions(profile: dict[str, Any]) -> list[str]:
    missing = []
    if not profile.get("capital"):
        missing.append(FALLBACK_QUESTIONS[0])
    if not profile.get("skills"):
        missing.append(FALLBACK_QUESTIONS[1])
    if not profile.get("resources"):
        missing.append(FALLBACK_QUESTIONS[2])
    if not profile.get("experience"):
        missing.append(FALLBACK_QUESTIONS[3])
    return missing


def fallback_response(message: str, profile: dict[str, Any] | None = None) -> dict[str, Any]:
    extracted = extract_profile(message, profile)
    questions = missing_profile_questions(extracted)
    if questions:
        response = questions[0]
    else:
        response = "I have captured your situation. I can now help compare a business, affordability, support, approvals, or next steps."
    return {
        "message": response,
        "profile": extracted,
        "follow_up_questions": questions,
        "provider": "rule-based fallback",
    }


def _llm_available() -> bool:
    return bool(LLM_PROVIDER and LLM_API_KEY and LLM_BASE_URL and LLM_MODEL)


def ask_llm(message: str, context: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    if not _llm_available():
        if context and isinstance(context, list):
            return {
                "message": context[0]["text"],
                "profile": {},
                "follow_up_questions": [],
                "provider": "rule-based RAG fallback",
            }
        return fallback_response(message)

    prompt = {
        "role": "user",
        "content": (
            "Answer the user's question using only the supplied context. "
            "Do not calculate finances, invent schemes, or decide official eligibility. "
            "Say when information must be verified.\n\n"
            f"Context:\n{json.dumps(context or [], ensure_ascii=False)}\n\n"
            f"Question: {message}"
        ),
    }
    request = Request(
        LLM_BASE_URL.rstrip("/") + "/chat/completions",
        data=json.dumps(
            {
                "model": LLM_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a careful UdyamSaathi information assistant."},
                    prompt,
                ],
                "temperature": 0.2,
            }
        ).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLM_API_KEY}",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        content = payload["choices"][0]["message"]["content"]
        return {"message": content, "profile": {}, "follow_up_questions": [], "provider": LLM_PROVIDER}
    except Exception:
        if context and isinstance(context, list):
            return {
                "message": context[0]["text"],
                "profile": {},
                "follow_up_questions": [],
                "provider": "rule-based RAG fallback (LLM unavailable)",
            }
        fallback = fallback_response(message)
        fallback["provider"] = "rule-based fallback (LLM unavailable)"
        return fallback
