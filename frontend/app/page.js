"use client";

import { useEffect, useState } from "react";
import { ActionPlan, ApprovalChecklist, AssessmentForm, ChatInterface, DemoProfile, ErrorState, FinancialCard, Header, LoadingState, ProgressBar, RecommendationCard, SchemeCard } from "../components/JourneyComponents";
import { createUserProfile, getActionPlan, getApprovals, getFinancialFeasibility, getRecommendations, getSupportMatches, sendChat } from "../lib/api";
import { localizeDynamic, useLanguage } from "../lib/i18n";

const EMPTY_PROFILE = { name: "", location: "", capital: "", skills: "", resources: "", experience: "", goal: "Increase income" };
const DEMO_PROFILE = { name: "Ramesh", location: "Karnataka", capital: "200000", skills: "Farming, Animal Care", resources: "2 acres of land, Available water", experience: "Basic", goal: "Increase income" };
const DEFAULT_GOAL = "Increase income";

function toApiProfile(profile) {
  return { ...profile, capital: Number(profile.capital), goal: profile.goal.trim() || DEFAULT_GOAL, skills: profile.skills.split(",").map((item) => item.trim()).filter(Boolean), resources: profile.resources.split(",").map((item) => item.trim()).filter(Boolean) };
}

export default function Home() {
  const { language, setLanguage, t } = useLanguage();
  const [screen, setScreen] = useState(1);
  const [profile, setProfile] = useState(EMPTY_PROFILE);
  const [user, setUser] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [selected, setSelected] = useState(null);
  const [financial, setFinancial] = useState(null);
  const [support, setSupport] = useState(null);
  const [approvals, setApprovals] = useState(null);
  const [plan, setPlan] = useState(null);
  const [messages, setMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setMessages((current) => current.length === 0 || (current.length === 1 && current[0].role === "ai") ? [{ role: "ai", text: t("chat.intro") }] : current);
  }, [language]);

  const start = (demo = false) => { setProfile(demo ? DEMO_PROFILE : EMPTY_PROFILE); setScreen(2); setError(""); };
  const reset = () => { setScreen(1); setProfile(EMPTY_PROFILE); setUser(null); setRecommendations(null); setSelected(null); setFinancial(null); setSupport(null); setApprovals(null); setPlan(null); };

  async function submitAssessment() {
    setLoading(true); setError("");
    try {
      if (!profile.name.trim() || !profile.location.trim() || !profile.capital || !profile.experience) {
        throw new Error(t("assessment.validation"));
      }
      const apiProfile = toApiProfile(profile);
      const createdUser = await createUserProfile(apiProfile);
      const results = await getRecommendations(apiProfile);
      if (!results.recommendations?.length) {
        throw new Error(language === "kn" ? "ಲಭ್ಯವಿರುವ ದಾಖಲೆಗಳಿಂದ ಸೂಕ್ತ ವ್ಯವಹಾರ ಕಂಡುಬಂದಿಲ್ಲ. ಹೆಚ್ಚಿನ ವಿವರಗಳೊಂದಿಗೆ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ." : "We couldn't find a suitable business from the available records. Please try again with more detail.");
      }
      setUser(createdUser); setRecommendations(results.recommendations); setSelected(results.recommendations[0]); setScreen(3);
    }
    catch (requestError) { setError(requestError.message); } finally { setLoading(false); }
  }

  async function loadResults(business = selected) {
    if (!user || !business) return;
    setLoading(true); setError("");
    try {
      const apiProfile = toApiProfile(profile);
      const [financialResult, supportResult, approvalResult, actionResult] = await Promise.all([getFinancialFeasibility(user.id, business.business_id), getSupportMatches(apiProfile, business.business_id), getApprovals(business.business_id), getActionPlan(apiProfile, user.id, business.business_id)]);
      setFinancial(financialResult); setSupport(supportResult.matches || []); setApprovals(approvalResult || []); setPlan(actionResult); setSelected(business); setScreen(5);
    }
    catch (requestError) { setError(requestError.message); } finally { setLoading(false); }
  }

  async function sendMessage() {
    if (!chatInput.trim()) return;
    const text = chatInput.trim(); setMessages((current) => [...current, { role: "user", text }]); setChatInput(""); setLoading(true);
    try {
      const history = messages.filter((item) => item.role === "ai" || item.role === "user").slice(-8).map((item) => ({ role: item.role === "ai" ? "assistant" : "user", content: item.text }));
      const result = await sendChat(text, toApiProfile(profile), history, language);
      setMessages((current) => [...current, { role: "ai", text: result.message }]);
    } catch (requestError) {
      setMessages((current) => [...current, { role: "error", text: requestError.message }]);
    } finally { setLoading(false); }
  }

  const localize = (value) => localizeDynamic(value, language);
  const supportContent = support?.length ? <div className="scheme-grid">{support.slice(0, 3).map((scheme) => <SchemeCard key={scheme.scheme_id} scheme={scheme} t={t} localize={localize} />)}</div> : <p className="empty-copy">{t("support.empty")}</p>;

  return <main className="app-shell">
    <Header onHome={reset} language={language} setLanguage={setLanguage} t={t} />
    {screen === 1 && <section className="landing-screen"><div className="landing-copy"><p className="eyebrow">{t("landing.eyebrow")}</p><h1>{t("landing.title")} <em>{t("landing.titleAccent")}</em></h1><p className="landing-description">{t("landing.description")}</p><div className="landing-actions"><button className="primary-button" type="button" onClick={() => start(false)}>{t("landing.start")} <span>→</span></button><DemoProfile onUse={() => start(true)} t={t} /></div></div><div className="landing-art"><img className="landing-logo" src="/udyamsaath--logo.jpeg" alt={t("landing.logoAlt")} /></div></section>}
    {screen > 1 && <div className="journey-wrap"><ProgressBar current={screen} total={8} t={t} />{error && <ErrorState message={error} onRetry={() => screen === 2 ? submitAssessment() : loadResults()} t={t} />}{screen === 2 && <AssessmentForm profile={profile} setProfile={setProfile} onSubmit={submitAssessment} loading={loading} t={t} />}{screen === 3 && <ChatInterface messages={messages} input={chatInput} setInput={setChatInput} onSend={sendMessage} onContinue={() => setScreen(4)} loading={loading} t={t} />}{screen === 4 && recommendations && <section className="panel recommendation-panel"><p className="eyebrow">{t("recommendation.eyebrow")}</p><h2>{t("recommendation.title")}</h2><p className="section-intro">{t("recommendation.intro")}</p><RecommendationCard recommendation={recommendations[0]} primary onSelect={loadResults} t={t} localize={localize} /><div className="alternatives"><p className="why-label">{t("recommendation.alternatives")}</p>{recommendations.slice(1).map((recommendation) => <RecommendationCard key={recommendation.business_id} recommendation={recommendation} onSelect={loadResults} t={t} localize={localize} />)}</div><button className="quiet-button" type="button" onClick={() => setScreen(3)}>{t("recommendation.talk")}</button></section>}{screen === 5 && financial && <><FinancialCard data={financial} t={t} /><section className="panel support-panel"><p className="eyebrow">{t("support.eyebrow")}</p><h2>{t("support.title")}</h2><p className="section-intro">{t("support.intro", { business: localize(selected.business) })}</p>{supportContent}<p className="notice">{t("support.notice")}</p></section><ApprovalChecklist approvals={approvals || []} t={t} localize={localize} /><ActionPlan plan={plan} t={t} localize={localize} /><button className="primary-button journey-end-button" type="button" onClick={reset}>{t("common.startAgain")} <span>→</span></button></>}{loading && screen > 3 && <LoadingState t={t} />}</div>}
  </main>;
}
