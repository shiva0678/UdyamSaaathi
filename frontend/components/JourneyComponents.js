export function Header({ onHome }) {
  return (
    <header className="app-header">
      <button className="brand-button" type="button" onClick={onHome}>
        <span className="brand-dot" aria-hidden="true" />
        <span>UdyamSaathi</span>
      </button>
      <span className="language-note">English / Kannada-ready</span>
    </header>
  );
}

export function ProgressBar({ current, total }) {
  return (
    <div className="progress-wrap" aria-label={`Step ${current} of ${total}`}>
      <div className="progress-meta">
        <span>YOUR JOURNEY</span>
        <strong>{String(current).padStart(2, "0")} / {String(total).padStart(2, "0")}</strong>
      </div>
      <div className="progress-track"><span style={{ width: `${(current / total) * 100}%` }} /></div>
    </div>
  );
}

export function AssessmentForm({ profile, setProfile, onSubmit, loading }) {
  const update = (field, value) => setProfile((current) => ({ ...current, [field]: value }));
  return (
    <section className="panel assessment-panel">
      <p className="eyebrow">STEP 02 / UNDERSTAND YOU</p>
      <h2>Tell us about your starting point.</h2>
      <p className="section-intro">A few simple answers help us find a practical match for you.</p>
      <div className="form-grid">
        <label>What is your name?<input value={profile.name} onChange={(event) => update("name", event.target.value)} placeholder="e.g. Ramesh" /></label>
        <label>Where are you based?<input value={profile.location} onChange={(event) => update("location", event.target.value)} placeholder="e.g. Karnataka" /></label>
        <label>Available investment (INR)<input type="number" min="0" value={profile.capital} onChange={(event) => update("capital", event.target.value)} placeholder="200000" /></label>
        <label>What skills do you have?<input value={profile.skills} onChange={(event) => update("skills", event.target.value)} placeholder="Farming, Animal Care" /></label>
        <label>What resources do you have?<input value={profile.resources} onChange={(event) => update("resources", event.target.value)} placeholder="2 acres of land, Available water" /></label>
        <label>How much experience do you have?
          <select value={profile.experience} onChange={(event) => update("experience", event.target.value)}>
            <option value="">Choose one</option><option>Basic</option><option>Intermediate</option><option>Advanced</option>
          </select>
        </label>
        <label className="full-field">What would you like to achieve?<input value={profile.goal} onChange={(event) => update("goal", event.target.value)} placeholder="Increase income" /></label>
      </div>
      <button className="primary-button" type="button" onClick={onSubmit} disabled={loading || !profile.name || !profile.location || !profile.capital || !profile.experience}>
        {loading ? "Preparing your path..." : "Continue to assessment"}<span aria-hidden="true">-&gt;</span>
      </button>
    </section>
  );
}

export function ChatInterface({ messages, input, setInput, onSend, onContinue, loading }) {
  return (
    <section className="panel chat-panel">
      <div className="chat-heading"><span className="chat-orb">✦</span><div><p className="eyebrow">STEP 03 / AI ASSESSMENT</p><h2>Let&apos;s understand your situation.</h2></div></div>
      <div className="chat-log" aria-live="polite">
        {messages.map((item, index) => <div className={`chat-bubble ${item.role}`} key={`${item.role}-${index}`}>{item.text}</div>)}
      </div>
      <form className="chat-input" onSubmit={(event) => { event.preventDefault(); onSend(); }}>
        <input value={input} onChange={(event) => setInput(event.target.value)} placeholder="Type your answer..." aria-label="Your answer" />
        <button type="submit" disabled={loading || !input.trim()} aria-label="Send answer">-&gt;</button>
      </form>
      <button className="primary-button chat-continue" type="button" onClick={onContinue}>See my best-fit business <span>→</span></button>
    </section>
  );
}

export function RecommendationCard({ recommendation, primary = false, onSelect }) {
  return <article className={`recommendation-card ${primary ? "primary-recommendation" : ""}`}>
    <div className="card-topline"><span>{primary ? "BEST FIT FOR YOU" : "ALTERNATIVE"}</span><strong>{recommendation.match_score}%</strong></div>
    <h3>{recommendation.business}</h3>
    {primary && <><p className="why-label">Why this fits you</p><ul className="reason-list">{recommendation.reasons.slice(0, 4).map((reason) => <li key={reason}>✓ {reason}</li>)}</ul><button className="text-button" type="button" onClick={() => onSelect(recommendation)}>Explore this path -&gt;</button></>}
  </article>;
}

export function FinancialCard({ data }) {
  const values = [["Initial investment", `₹${Number(data.initial_investment).toLocaleString("en-IN")}`], ["Monthly cost", `₹${Number(data.monthly_cost).toLocaleString("en-IN")}`], ["Expected revenue", `₹${Number(data.monthly_revenue).toLocaleString("en-IN")}`], ["Estimated profit", `₹${Number(data.monthly_profit).toLocaleString("en-IN")}`], ["Capital gap", `₹${Number(data.capital_gap).toLocaleString("en-IN")}`], ["ROI", `${data.roi}%`]];
  return <section className="panel financial-panel"><div className="section-heading"><div><p className="eyebrow">STEP 05 / FINANCIAL FEASIBILITY</p><h2>Can you afford this path?</h2></div><span className={`status-pill ${data.financial_status === "FEASIBLE" ? "good" : "warn"}`}>{data.financial_status}</span></div><div className="metric-grid">{values.map(([label, value]) => <div className="metric" key={label}><span>{label}</span><strong>{value}</strong></div>)}</div><p className="notice">{data.notice}</p></section>;
}

export function SchemeCard({ scheme }) {
  return <article className="scheme-card"><div className="card-topline"><span>DEMO SUPPORT</span><strong>{scheme.match_score}%</strong></div><h3>{scheme.scheme_name}</h3><p>{scheme.support_type}</p><div className="detail-block"><b>Eligibility</b><span>{scheme.eligibility.join(" · ")}</span></div><div className="detail-block"><b>Documents</b><span>{scheme.required_documents.join(" · ")}</span></div><small>{scheme.verification_status} · {scheme.source_type}</small></article>;
}

export function ApprovalChecklist({ approvals }) {
  return <section className="panel approval-panel"><p className="eyebrow">STEP 07 / APPROVALS</p><h2>Know what comes next.</h2>{approvals.length ? approvals.map((approval) => <div className="approval-item" key={approval.id}><div className="check-icon">✓</div><div><h3>{approval.license}</h3><p><b>Registration:</b> {approval.registration}</p><p><b>Authority:</b> {approval.authority}</p><p><b>Documents:</b> {approval.documents.join(" · ")}</p><p><b>Process:</b> {approval.process_steps.join(" → ")}</p></div></div>) : <p className="empty-copy">No demo approval record is available. Check with the relevant local authority.</p>}</section>;
}

export function ActionPlan({ plan }) {
  return <section className="panel action-panel"><p className="eyebrow">STEP 08 / YOUR NEXT STEPS</p><h2>A clear way forward.</h2><ol className="action-list">{plan.steps.map((step) => <li key={step}>{step}</li>)}</ol><p className="notice">{plan.notice}</p></section>;
}

export function LoadingState() { return <div className="state-card"><span className="loader" />Building your personalized path...</div>; }
export function ErrorState({ message, onRetry }) { return <div className="state-card error-state"><strong>We couldn&apos;t load that just now.</strong><span>{message}</span>{onRetry && <button className="secondary-button" type="button" onClick={onRetry}>Try again</button>}</div>; }
export function DemoProfile({ onUse }) { return <button className="demo-link" type="button" onClick={onUse}>Try Demo Profile <span>Ramesh · Karnataka · ₹2,00,000</span></button>; }
