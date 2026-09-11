"use client";

import { useState } from "react";
import { ActionPlan, ApprovalChecklist, AssessmentForm, ChatInterface, DemoProfile, ErrorState, FinancialCard, Header, LoadingState, ProgressBar, RecommendationCard, SchemeCard } from "../components/JourneyComponents";
import { createUserProfile, getActionPlan, getApprovals, getFinancialFeasibility, getRecommendations, getSupportMatches, sendChat } from "../lib/api";

const EMPTY_PROFILE = { name: "", location: "", capital: "", skills: "", resources: "", experience: "", goal: "Increase income" };
const DEMO_PROFILE = { name: "Ramesh", location: "Karnataka", capital: "200000", skills: "Farming, Animal Care", resources: "2 acres of land, Available water", experience: "Basic", goal: "Increase income" };
const DEFAULT_GOAL = "Increase income";

function toApiProfile(profile) {
  return { ...profile, capital: Number(profile.capital), goal: profile.goal.trim() || DEFAULT_GOAL, skills: profile.skills.split(",").map((item) => item.trim()).filter(Boolean), resources: profile.resources.split(",").map((item) => item.trim()).filter(Boolean) };
}

export default function Home() {
  const [screen, setScreen] = useState(1);
  const [profile, setProfile] = useState(EMPTY_PROFILE);
  const [user, setUser] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [selected, setSelected] = useState(null);
  const [financial, setFinancial] = useState(null);
  const [support, setSupport] = useState(null);
  const [approvals, setApprovals] = useState(null);
  const [plan, setPlan] = useState(null);
  const [messages, setMessages] = useState([{ role: "ai", text: "Let’s understand your situation. You can answer here or continue with the simple form." }]);
  const [chatInput, setChatInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const start = (demo = false) => { setProfile(demo ? DEMO_PROFILE : EMPTY_PROFILE); setScreen(2); setError(""); };
  const reset = () => { setScreen(1); setProfile(EMPTY_PROFILE); setUser(null); setRecommendations(null); setSelected(null); setFinancial(null); setSupport(null); setApprovals(null); setPlan(null); };

  async function submitAssessment() {
    setLoading(true); setError("");
    try {
      if (!profile.name.trim() || !profile.location.trim() || !profile.capital || !profile.experience) {
        throw new Error("Please complete your name, location, investment, and experience before continuing.");
      }
      const apiProfile = toApiProfile(profile);
      const createdUser = await createUserProfile(apiProfile);
      const results = await getRecommendations(apiProfile);
      if (!results.recommendations?.length) {
        throw new Error("We couldn't find a suitable business from the available records. Please try again with more detail.");
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
      const result = await sendChat(text, toApiProfile(profile), history);
      setMessages((current) => [...current, { role: "ai", text: result.message }]);
    } catch (requestError) {
      setMessages((current) => [...current, { role: "error", text: requestError.message }]);
    } finally { setLoading(false); }
  }

  const supportContent = support?.length ? <div className="scheme-grid">{support.slice(0, 3).map((scheme) => <SchemeCard key={scheme.scheme_id} scheme={scheme} />)}</div> : <p className="empty-copy">No matching support records were found. Check official sources for current options.</p>;

  return <main className="app-shell">
    <Header onHome={reset} />
    {screen === 1 && <section className="landing-screen"><div className="landing-copy"><p className="eyebrow">A practical companion for rural entrepreneurs</p><h1>From your situation to a <em>brighter tomorrow.</em></h1><p className="landing-description">Find a suitable business, understand feasibility, discover relevant support and know your next steps.</p><div className="landing-actions"><button className="primary-button" type="button" onClick={() => start(false)}>Start Assessment <span>→</span></button><DemoProfile onUse={() => start(true)} /></div></div><div className="landing-art"><img className="landing-logo" src="/udyamsaath--logo.jpeg" alt="UdyamSaathi: ideas today, livelihoods tomorrow" /></div></section>}
    {screen > 1 && <div className="journey-wrap"><ProgressBar current={screen} total={8} />{error && <ErrorState message={error} onRetry={() => screen === 2 ? submitAssessment() : loadResults()} />}{screen === 2 && <AssessmentForm profile={profile} setProfile={setProfile} onSubmit={submitAssessment} loading={loading} />}{screen === 3 && <ChatInterface messages={messages} input={chatInput} setInput={setChatInput} onSend={sendMessage} onContinue={() => setScreen(4)} loading={loading} />}{screen === 4 && recommendations && <section className="panel recommendation-panel"><p className="eyebrow">STEP 04 / BEST-FIT BUSINESS</p><h2>One strong place to begin.</h2><p className="section-intro">Based on what you shared, this is your clearest starting point.</p><RecommendationCard recommendation={recommendations[0]} primary onSelect={loadResults} /><div className="alternatives"><p className="why-label">Two other paths to explore</p>{recommendations.slice(1).map((recommendation) => <RecommendationCard key={recommendation.business_id} recommendation={recommendation} onSelect={loadResults} />)}</div><button className="quiet-button" type="button" onClick={() => setScreen(3)}>Talk through my situation first</button></section>}{screen === 5 && financial && <><FinancialCard data={financial} /><section className="panel support-panel"><p className="eyebrow">STEP 06 / RELEVANT SUPPORT</p><h2>Support worth checking.</h2><p className="section-intro">These backend records may be relevant to {selected.business}. Verify details with official sources.</p>{supportContent}<p className="notice">Demo information - verify with official sources before applying.</p></section><ApprovalChecklist approvals={approvals || []} /><ActionPlan plan={plan} /><button className="primary-button journey-end-button" type="button" onClick={reset}>Start another assessment <span>→</span></button></>}{loading && screen > 3 && <LoadingState />}</div>}
  </main>;
}
