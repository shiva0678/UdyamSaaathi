const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });

    const payload = await response.json().catch(() => null);
    if (!response.ok) {
      const error = new Error(payload?.message || "The service could not complete this step.");
      error.code = payload?.error_code;
      throw error;
    }

    return payload;
  } catch (error) {
    if (error instanceof TypeError || error.name === "AbortError") {
      throw new Error("UdyamSaathi is temporarily unavailable. Please try again.");
    }
    if (error.code) throw error;
    throw new Error("We couldn't complete this step right now. Please try again.");
  }
}

export function createUserProfile(profile) {
  return request("/api/users/profile", {
    method: "POST",
    body: JSON.stringify(profile),
  });
}

export function getRecommendations(profile) {
  return request("/api/recommendations", {
    method: "POST",
    body: JSON.stringify(profile),
  });
}

export function getFinancialFeasibility(userId, businessId) {
  return request("/api/financial/feasibility", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, business_id: businessId }),
  });
}

export function getSupportMatches(profile, businessId) {
  return request("/api/support/match", {
    method: "POST",
    body: JSON.stringify({ profile, business_id: businessId }),
  });
}

export function getApprovals(businessId) {
  return request(`/api/approvals/${businessId}`);
}

export function getActionPlan(profile, userId, businessId) {
  return request("/api/action-plan", {
    method: "POST",
    body: JSON.stringify({ profile, user_id: userId, business_id: businessId }),
  });
}

export function sendChat(message, profile, history = [], language = "en") {
  return request("/api/chat", {
    method: "POST",
    body: JSON.stringify({ message, profile, history, language }),
  });
}
