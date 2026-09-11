export function Header({ onHome, language, setLanguage, t }) {
  return <header className="app-header">
    <button className="brand-button" type="button" onClick={onHome}><span className="brand-dot" aria-hidden="true" /><span>{t("brand")}</span></button>
    <label className="language-selector"><span className="sr-only">{t("header.language")}</span><select value={language} onChange={(event) => setLanguage(event.target.value)} aria-label={t("header.language")}><option value="en">{t("header.english")}</option><option value="kn">{t("header.kannada")}</option></select></label>
  </header>;
}

export function ProgressBar({ current, total, t }) {
  return <div className="progress-wrap" aria-label={t("progress.step", { current, total })}><div className="progress-meta"><span>{t("progress.journey")}</span><strong>{String(current).padStart(2, "0")} / {String(total).padStart(2, "0")}</strong></div><div className="progress-track"><span style={{ width: `${(current / total) * 100}%` }} /></div></div>;
}

export function AssessmentForm({ profile, setProfile, onSubmit, loading, t }) {
  const update = (field, value) => setProfile((current) => ({ ...current, [field]: value }));
  return <section className="panel assessment-panel"><p className="eyebrow">{t("assessment.eyebrow")}</p><h2>{t("assessment.title")}</h2><p className="section-intro">{t("assessment.intro")}</p><div className="form-grid">
    <label>{t("assessment.name")}<input required value={profile.name} onChange={(event) => update("name", event.target.value)} placeholder={t("assessment.namePlaceholder")} /></label>
    <label>{t("assessment.location")}<input required value={profile.location} onChange={(event) => update("location", event.target.value)} placeholder={t("assessment.locationPlaceholder")} /></label>
    <label>{t("assessment.capital")}<input required type="number" min="0" value={profile.capital} onChange={(event) => update("capital", event.target.value)} placeholder={t("assessment.capitalPlaceholder")} /></label>
    <label>{t("assessment.skills")}<input value={profile.skills} onChange={(event) => update("skills", event.target.value)} placeholder={t("assessment.skillsPlaceholder")} /></label>
    <label>{t("assessment.resources")}<input value={profile.resources} onChange={(event) => update("resources", event.target.value)} placeholder={t("assessment.resourcesPlaceholder")} /></label>
    <label>{t("assessment.experience")}<select value={profile.experience} onChange={(event) => update("experience", event.target.value)}><option value="">{t("assessment.experienceChoose")}</option><option value="Basic">{t("assessment.basic")}</option><option value="Intermediate">{t("assessment.intermediate")}</option><option value="Advanced">{t("assessment.advanced")}</option></select></label>
    <label className="full-field">{t("assessment.goal")}<input value={profile.goal} onChange={(event) => update("goal", event.target.value)} placeholder={t("assessment.goalPlaceholder")} /></label>
  </div><button className="primary-button" type="button" onClick={onSubmit} disabled={loading || !profile.name.trim() || !profile.location.trim() || !profile.capital || !profile.experience}>{loading ? t("assessment.loading") : t("assessment.submit")}<span aria-hidden="true">-&gt;</span></button></section>;
}

export function ChatInterface({ messages, input, setInput, onSend, onContinue, loading, t }) {
  return <section className="panel chat-panel"><div className="chat-heading"><span className="chat-orb">✦</span><div><p className="eyebrow">{t("chat.eyebrow")}</p><h2>{t("chat.title")}</h2></div></div><div className="chat-log" aria-live="polite">{messages.map((item, index) => <div className={`chat-bubble ${item.role}`} key={`${item.role}-${index}`}>{item.text}</div>)}</div><form className="chat-input" onSubmit={(event) => { event.preventDefault(); onSend(); }}><input value={input} onChange={(event) => setInput(event.target.value)} placeholder={t("chat.placeholder")} aria-label={t("chat.placeholder")} /><button type="submit" disabled={loading || !input.trim()} aria-label={t("chat.send")}>-&gt;</button></form><button className="primary-button chat-continue" type="button" onClick={onContinue}>{t("chat.continue")} <span>→</span></button></section>;
}

export function RecommendationCard({ recommendation, primary = false, onSelect, t, localize }) {
  return <article className={`recommendation-card ${primary ? "primary-recommendation" : ""}`}><div className="card-topline"><span>{primary ? t("recommendation.best") : t("recommendation.alternative")}</span><strong>{recommendation.match_score}%</strong></div><h3>{localize(recommendation.business)}</h3>{primary && <><p className="why-label">{t("recommendation.why")}</p><ul className="reason-list">{recommendation.reasons.slice(0, 4).map((reason) => <li key={reason}>✓ {localize(reason)}</li>)}</ul><button className="text-button" type="button" onClick={() => onSelect(recommendation)}>{t("recommendation.explore")}</button></>}</article>;
}

export function FinancialCard({ data, t }) {
  const values = [[t("financial.initial"), `₹${Number(data.initial_investment).toLocaleString("en-IN")}`], [t("financial.cost"), `₹${Number(data.monthly_cost).toLocaleString("en-IN")}`], [t("financial.revenue"), `₹${Number(data.monthly_revenue).toLocaleString("en-IN")}`], [t("financial.profit"), `₹${Number(data.monthly_profit).toLocaleString("en-IN")}`], [t("financial.gap"), `₹${Number(data.capital_gap).toLocaleString("en-IN")}`], [t("financial.roi"), `${data.roi}%`]];
  const status = data.financial_status === "FEASIBLE" ? t("financial.feasible") : t("financial.financing");
  return <section className="panel financial-panel"><div className="section-heading"><div><p className="eyebrow">{t("financial.eyebrow")}</p><h2>{t("financial.title")}</h2></div><span className={`status-pill ${data.financial_status === "FEASIBLE" ? "good" : "warn"}`}>{status}</span></div><div className="metric-grid">{values.map(([label, value]) => <div className="metric" key={label}><span>{label}</span><strong>{value}</strong></div>)}</div><p className="notice">{t("financial.notice")}</p></section>;
}

export function SchemeCard({ scheme, t, localize }) {
  return <article className="scheme-card"><div className="card-topline"><span>{t("support.demo")}</span><strong>{scheme.match_score}%</strong></div><h3>{localize(scheme.scheme_name)}</h3><p>{localize(scheme.support_type)}</p><div className="detail-block"><b>{t("support.eligibility")}</b><span>{scheme.eligibility.map(localize).join(" · ")}</span></div><div className="detail-block"><b>{t("support.documents")}</b><span>{scheme.required_documents.map(localize).join(" · ")}</span></div><small>{t("common.demo")} · {t("common.synthetic")}</small></article>;
}

export function ApprovalChecklist({ approvals, t, localize }) {
  return <section className="panel approval-panel"><p className="eyebrow">{t("approvals.eyebrow")}</p><h2>{t("approvals.title")}</h2>{approvals.length ? approvals.map((approval) => <div className="approval-item" key={approval.id}><div className="check-icon">✓</div><div><h3>{localize(approval.license)}</h3><p><b>{t("approvals.registration")}</b> {localize(approval.registration)}</p><p><b>{t("approvals.authority")}</b> {localize(approval.authority)}</p><p><b>{t("approvals.documents")}</b> {approval.documents.map(localize).join(" · ")}</p><p><b>{t("approvals.process")}</b> {approval.process_steps.map(localize).join(" → ")}</p></div></div>) : <p className="empty-copy">{t("approvals.empty")}</p>}</section>;
}

export function ActionPlan({ plan, t, localize }) {
  return <section className="panel action-panel"><p className="eyebrow">{t("action.eyebrow")}</p><h2>{t("action.title")}</h2>{plan?.steps?.length ? <><ol className="action-list">{plan.steps.map((step) => <li key={step}>{localize(step)}</li>)}</ol><p className="notice">{t("support.notice")}</p></> : <p className="empty-copy">{t("action.empty")}</p>}</section>;
}

export function LoadingState({ t }) { return <div className="state-card"><span className="loader" />{t("common.loading")}</div>; }
export function ErrorState({ message, onRetry, t }) { return <div className="state-card error-state"><strong>{t("common.errorTitle")}</strong><span>{message}</span>{onRetry && <button className="secondary-button" type="button" onClick={onRetry}>{t("common.retry")}</button>}</div>; }
export function DemoProfile({ onUse, t }) { return <button className="demo-link" type="button" onClick={onUse}>{t("landing.demo")} <span>{t("landing.demoDetail")}</span></button>; }
