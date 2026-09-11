import logging
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)

logger = logging.getLogger(__name__)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "").strip().lower() or "openai"
LLM_API_KEY = (os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY") or "").strip()
LLM_BASE_URL = (os.getenv("OPENAI_BASE_URL") or os.getenv("LLM_BASE_URL") or "").strip()
LLM_MODEL = (os.getenv("OPENAI_MODEL") or os.getenv("LLM_MODEL") or "").strip()

FALLBACK_QUESTIONS = [
    "What is your available investment?",
    "What skills do you have?",
    "Do you have land or other resources?",
    "How much experience do you have?",
]


class AIServiceError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def detect_language(text: str) -> str:
    return "kn" if re.search(r"[\u0C80-\u0CFF]", text) else "en"


def classify_message(message: str) -> str:
    text = message.lower()
    if any(term in text for term in ("business", "suitable", "recommend", "opportunity", "ವ್ಯವಹಾರ", "ಸೂಕ್ತ", "ಉದ್ಯಮ")):
        return "recommendation"
    if any(term in text for term in ("afford", "cost", "profit", "roi", "capital", "finance", "ಹಣ", "ಬಂಡವಾಳ", "ವೆಚ್ಚ", "ಲಾಭ")):
        return "financial"
    if any(term in text for term in ("support", "scheme", "subsidy", "grant", "loan", "ಬೆಂಬಲ", "ಯೋಜನೆ", "ಸಹಾಯ")):
        return "support"
    if any(term in text for term in ("approval", "license", "registration", "permission", "ಅನುಮತಿ", "ಪರವಾನಗಿ", "ನೋಂದಣಿ")):
        return "approval"
    if "document" in text or "ದಾಖಲೆ" in text:
        return "information"
    if any(term in text for term in ("first", "next", "start", "setup", "step", "ಮೊದಲು", "ಮುಂದೆ", "ಹಂತ")):
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

    capital_matches = list(re.finditer(
        r"(?:rs\.?|inr|₹)?\s*([\d,]+(?:\.\d+)?)\s*(lakh|lakhs|crore|crores|ಲಕ್ಷ|ಕೋಟಿ|rupees?|rs)?",
        message.lower(),
    ))
    capital_match = next(
        (match for match in capital_matches if match.group(2) or any(symbol in match.group(0) for symbol in ("₹", "rs", "inr"))),
        capital_matches[-1] if capital_matches else None,
    )
    if capital_match and any(term in message.lower() for term in ("capital", "invest", "budget", "rupee", "rs", "₹", "ಬಂಡವಾಳ", "ಹೂಡಿಕೆ")):
        amount = float(capital_match.group(1).replace(",", ""))
        unit = capital_match.group(2) or ""
        if unit.startswith("lakh") or unit == "ಲಕ್ಷ":
            amount *= 100000
        elif unit.startswith("crore") or unit == "ಕೋಟಿ":
            amount *= 10000000
        profile["capital"] = amount

    skill_match = re.search(r"skills?\s*(?:are|:)?\s*([^.!?]+)", message, re.IGNORECASE)
    if skill_match:
        profile["skills"] = [item.strip() for item in re.split(r",| and ", skill_match.group(1)) if item.strip()]

    if any(term in message.lower() for term in ("land", "acre", "water", "well", "irrigation", "ಜಮೀನು", "ಎಕರೆ", "ನೀರು")):
        profile["resources"] = [message.strip()]
    return profile


def missing_profile_questions(profile: dict[str, Any], language: str = "en") -> list[str]:
    missing = []
    if not profile.get("capital"):
        missing.append(FALLBACK_QUESTIONS[0])
    if not profile.get("skills"):
        missing.append(FALLBACK_QUESTIONS[1])
    if not profile.get("resources"):
        missing.append(FALLBACK_QUESTIONS[2])
    if not profile.get("experience"):
        missing.append(FALLBACK_QUESTIONS[3])
    if language == "kn":
        return [
            {FALLBACK_QUESTIONS[0]: "ನಿಮ್ಮ ಲಭ್ಯವಿರುವ ಹೂಡಿಕೆ ಎಷ್ಟು?", FALLBACK_QUESTIONS[1]: "ನಿಮ್ಮ ಕೌಶಲ್ಯಗಳು ಯಾವುವು?", FALLBACK_QUESTIONS[2]: "ನಿಮ್ಮ ಬಳಿ ಜಮೀನು ಅಥವಾ ಇತರ ಸಂಪನ್ಮೂಲಗಳಿವೆಯೇ?", FALLBACK_QUESTIONS[3]: "ನಿಮಗೆ ಎಷ್ಟು ಅನುಭವವಿದೆ?"}[question]
            for question in missing
        ]
    return missing


def fallback_response(message: str, profile: dict[str, Any] | None = None) -> dict[str, Any]:
    extracted = extract_profile(message, profile)
    questions = missing_profile_questions(extracted)
    return {
        "message": questions[0] if questions else "I have captured your situation.",
        "profile": extracted,
        "follow_up_questions": questions,
        "provider": "rule-based fallback",
    }


def ai_status() -> dict[str, Any]:
    try:
        import openai  # noqa: F401
        sdk_available = True
    except ImportError:
        sdk_available = False
    return {
        "configured": bool(LLM_API_KEY and LLM_MODEL and sdk_available),
        "provider": LLM_PROVIDER,
        "model": LLM_MODEL or "not configured",
        "sdk_available": sdk_available,
    }


def _client() -> Any:
    if not LLM_API_KEY or not LLM_MODEL:
        logger.warning("AI is not configured: API key or model is missing")
        raise AIServiceError(
            "LLM_NOT_CONFIGURED",
            "AI is not configured. Please add OPENAI_API_KEY and OPENAI_MODEL to backend/.env.",
        )
    try:
        from openai import OpenAI
    except ImportError as error:
        logger.exception("OpenAI SDK is not installed")
        raise AIServiceError(
            "LLM_SDK_MISSING",
            "AI service is unavailable because the OpenAI SDK is not installed.",
        ) from error
    kwargs = {"api_key": LLM_API_KEY}
    if LLM_BASE_URL:
        kwargs["base_url"] = LLM_BASE_URL
    return OpenAI(**kwargs)


def ask_llm(
    message: str,
    context: list[dict[str, Any]] | None = None,
    history: list[dict[str, str]] | None = None,
    language: str | None = None,
) -> dict[str, Any]:
    client = _client()
    context_text = "\n\n".join(
        f"Source: {item.get('document_name', 'Prototype document')}\n{item.get('text', '')}"
        for item in (context or [])
    )
    response_language = language if language in {"en", "kn"} else detect_language(message)
    language_instruction = (
        "Respond in clear, simple Kannada using Kannada script. Preserve business names, official scheme names, numbers, currency, percentages, acres, months, and years exactly."
        if response_language == "kn"
        else "Respond in clear, simple English."
    )
    system_message = (
        "You are the UdyamSaathi conversational assistant. Give practical, concise answers. "
        f"{language_instruction} "
        "Use only the supplied prototype context for scheme and approval information. "
        "Never invent official eligibility, subsidies, amounts, deadlines, or requirements. "
        "If no trusted context is supplied, do not name schemes or claim specific approval requirements; "
        "say that official verification is required. "
        "Clearly say when a detail must be verified with an official authority. "
        "Do not calculate recommendation or financial results; those come from deterministic backend engines."
    )
    messages: list[dict[str, str]] = [{"role": "system", "content": system_message}]
    messages.extend(
        item for item in (history or [])
        if item.get("role") in {"user", "assistant"} and item.get("content")
    )
    messages.append({
        "role": "user",
        "content": f"Prototype context:\n{context_text or 'No trusted context was retrieved.'}\n\nQuestion: {message}",
    })
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.2,
            timeout=20,
        )
        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise AIServiceError("LLM_EMPTY_RESPONSE", "AI service returned an empty response.")
        return {
            "message": content,
            "profile": {},
            "follow_up_questions": [],
            "provider": LLM_PROVIDER,
            "success": True,
            "ai_enabled": True,
            "rag_used": bool(context),
            "language": response_language,
        }
    except AIServiceError:
        raise
    except Exception as error:
        logger.exception("LLM request failed")
        error_name = error.__class__.__name__
        code = "LLM_AUTH_ERROR" if "Authentication" in error_name else "LLM_API_ERROR"
        raise AIServiceError(code, "AI service is currently unavailable. Check the backend logs.") from error
