# UdyamSaathi Implementation Guide

## Project Overview

UdyamSaathi is a Smart India Hackathon 2026 prototype for rural entrepreneurs. The product journey is:

"Here is my situation" -> "Here is the best business opportunity for me" -> "Can I afford it?" -> "What government support may apply?" -> "What approvals do I need?" -> "What should I do next?"

The prototype uses synthetic demo data for Karnataka. Synthetic records must not be presented as verified government information.

## Technology Constraints

- Frontend: React / Next.js
- Backend: Python + FastAPI
- Database: Supabase PostgreSQL only
- Recommendation: deterministic Python rule-based engine
- Financial feasibility: deterministic Python engine, planned for Phase 5
- Retrieval: FAISS, planned for Phase 7
- LLM: configurable GPT/Llama provider, planned for Phase 7
- Deployment: Docker, planned for Phase 12
- Do not add a second database.
- Do not configure local PostgreSQL.
- Keep the implementation simple and suitable for an SIH demo.
- Do not add authentication, microservices, admin dashboards, or complex repository abstractions unless a later phase explicitly requires them.

## Current Status

Completed through Phase 8:

- Phase 1: Project setup
- Phase 2: Supabase PostgreSQL and synthetic data
- Phase 3: FastAPI core APIs
- Phase 4: Business recommendation engine
- Phase 5: Deterministic financial feasibility engine
- Phase 6: Support matching and approval navigator
- Phase 7: Simple conversational AI and RAG
- Phase 8: UdyamSaathi frontend

Not started:

- Phase 9: Frontend/backend connection
- Phase 10: Complete journey and demo mode
- Phase 11: Testing and error handling expansion
- Phase 12: Docker and final SIH demo

Do not implement a later phase until the user explicitly requests it.

## Repository Structure

```text
backend/
  app/
    __init__.py
    main.py
    database.py
    seed.py
    engines/
      recommendation.py
    models/
    schemas/
      api.py
    routes/
      api.py
    services/
  requirements.txt
  .env.example
  .env                 # local only, ignored by git
frontend/
  app/
    layout.js
    page.js
    globals.css
  package.json
  package-lock.json
data/
  businesses.json
  schemes.json
  approvals.json
  market_data.json
  demo_user.json
rag/                  # reserved for Phase 7
docker/               # reserved for Phase 12
.gitignore
README.md
implementation.md
```

## Environment Setup

From the repository root:

```powershell
cd backend
python -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
```

Create `backend/.env` from `backend/.env.example` and set the Supabase Session pooler URL:

```env
DATABASE_URL=postgresql://postgres.<project-ref>:<password>@<session-pooler-host>:5432/postgres
```

Use the exact URL from Supabase Dashboard -> Connect -> Postgres -> Session pooler. Never hardcode or commit credentials. The `.env` file is ignored by git.

## Phase 1: Project Setup

Created the initial backend and Next.js frontend structure.

Backend starter endpoints:

- `GET /` -> `{ "message": "Welcome to UdyamSaathi API" }`
- `GET /health` -> API status JSON

The frontend has a simple UdyamSaathi landing page with the tagline:

`From your situation to a brighter tomorrow.`

## Phase 2: Supabase PostgreSQL and Synthetic Data

### Database Tables

`backend/app/database.py` creates these tables in Supabase:

- `users`
- `businesses`
- `schemes`
- `approvals`
- `market_data`

Important fields use PostgreSQL `JSONB`:

- `users.skills`
- `users.resources`
- `businesses.required_skills`
- `schemes.eligibility`
- `schemes.required_documents`
- `approvals.documents`
- `approvals.process_steps`

Foreign key:

- `approvals.business_id` references `businesses.id`

The connection uses `psycopg` and `DATABASE_URL`. `dict_row` is enabled so database rows map naturally into Pydantic models.

### Seed Data

`backend/app/seed.py` loads JSON files from `data/` and performs idempotent upserts:

- 21 business profiles
- 9 synthetic support records
- 10 approval records
- 12 market records
- 1 demo user profile

The demo user is Ramesh:

- Location: Karnataka
- Capital: 200000
- Land: 2 acres
- Water: Available
- Skills: Farming, Animal Care
- Experience: Basic
- Goal: Increase income
- Profile type: Demo Profile - Synthetic Data

The scheme records have:

- `source_type = synthetic`
- `verification_status = demo`

### Database Health

- `GET /health/db` returns `{ "database": "connected" }` when Supabase is reachable.

## Phase 3: FastAPI Core APIs

Routes are registered in `backend/app/routes/api.py` and included from `backend/app/main.py`.

- `POST /api/users/profile`
- `GET /api/businesses`
- `GET /api/businesses/{id}`
- `GET /api/schemes`
- `GET /api/approvals/{business_id}`
- `GET /api/market/{location}`

Pydantic models are in `backend/app/schemas/api.py`.

The profile input fields are:

```json
{
  "name": "Ramesh",
  "location": "Karnataka",
  "capital": 200000,
  "skills": ["Farming", "Animal Care"],
  "resources": ["2 acres of land", "Available water"],
  "experience": "Basic",
  "goal": "Increase income"
}
```

The API has CORS enabled for:

- `http://localhost:3000`
- `http://127.0.0.1:3000`

Database failures return controlled HTTP 503 responses. Missing businesses return HTTP 404.

## Phase 4: Business Recommendation Engine

The engine is in `backend/app/engines/recommendation.py`.

It is deterministic, rule-based, fast, and does not use an LLM.

### Scoring Weights

- Capital: 30%
- Skills: 25%
- Resources: 20%
- Location: 15%
- Experience: 10%

Formula:

```text
final_score = capital_score * 0.30
             + skill_score * 0.25
             + resource_score * 0.20
             + location_score * 0.15
             + experience_score * 0.10
```

The recommendation endpoint is:

- `POST /api/recommendations`

It returns the top three businesses, sorted by score, with:

- business name and ID
- match score
- score breakdown
- reasons
- strengths
- limitations
- alternatives
- disclaimer

Required disclaimer:

`Match score is a prototype suitability score, not a guarantee of success.`

The engine extracts land information such as `2 acres` from resource text and checks water terms such as `water`, `irrigation`, `well`, and `borewell`.

Unit tests are in:

`backend/tests/test_recommendation_engine.py`

Run them with:

```powershell
cd backend
python -m unittest discover -s tests -v
```

## Phase 5: Deterministic Financial Feasibility Engine

Implemented in `backend/app/engines/financial.py` and exposed through `POST /api/financial/feasibility`.

The endpoint accepts `user_id` and `business_id`, loads both records from Supabase, and performs all calculations in Python. The current business table has no separate startup-investment column, so `minimum_capital` is used as the synthetic `initial_investment` estimate.

Calculations:

```text
monthly_profit = monthly_revenue - monthly_cost
annual_revenue = monthly_revenue * 12
annual_cost = monthly_cost * 12
annual_profit = monthly_profit * 12
capital_gap = max(initial_investment - available_capital, 0)
ROI = annual_profit / initial_investment * 100
```

Zero investment returns ROI `0` safely. Financial status is `FEASIBLE` when available capital meets the initial investment; otherwise it is `ADDITIONAL FINANCING REQUIRED`. The response includes risk notes and the notice `Synthetic estimates for prototype demonstration.`

Unit tests are in `backend/tests/test_financial_engine.py` and cover profitable feasible cases, capital gaps, negative profit, and zero investment.

Expected future responsibility:

- Calculate startup cost, monthly cost, monthly revenue, profit, break-even estimate, and affordability.
- Use deterministic Python calculations only.
- Never use an LLM for financial calculations.
- Use business data from Supabase and the user's available capital.
- Clearly label estimates as synthetic demo estimates.

## Phase 6: Support Matching and Approval Navigator

Implemented with three small deterministic engines:

- `backend/app/engines/scheme_matcher.py`
- `backend/app/engines/approval_engine.py`
- `backend/app/engines/action_plan.py`

Support matching is exposed through `POST /api/support/match`. It accepts a user profile and `business_id`, loads the selected business and schemes from Supabase, and scores records using location, sector, capital, target group, and eligibility conditions.

Every support result forcibly returns:

- `source_type = synthetic`
- `verification_status = demo`
- `Demo information - verify with official sources before applying.`

Approval navigation remains available at `GET /api/approvals/{business_id}` and now uses the approval engine formatter. It returns registration, license, documents, authority, and process steps.

The combined action plan is exposed through `POST /api/action-plan`. It accepts a profile, `user_id`, and `business_id`, then combines recommendation, financial feasibility, support, and approvals into three to five practical next steps.

Phase 6 uses rule-based logic only. No LLM determines eligibility or compliance.

Expected future responsibility:

- Match the user and selected business against synthetic scheme records.
- Return eligibility reasons and missing documents.
- Return approvals for a selected business.
- Keep all scheme content clearly marked as synthetic/demo unless verified sources are later added.
- Use rule-based matching.

## Phase 7: Simple Conversational AI and RAG

Implemented as a lightweight demo layer.

### Conversational AI

`backend/app/services/llm_service.py` provides:

- Configurable GPT/Llama-compatible HTTP provider using `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL`.
- No hardcoded API keys.
- Rule-based fallback when any provider setting is missing or the provider fails.
- Basic profile extraction and follow-up questions.
- Intent classification for financial, support, approval, recommendation, action-plan, and informational messages.

The LLM is not used for financial calculations, official eligibility decisions, scheme invention, or approval invention.

### RAG

The `rag/` folder contains:

- `process_documents.py` for small document chunking.
- `embeddings.py` for deterministic local token embeddings.
- `vector_store.py` for FAISS index creation/loading.
- `retriever.py` for relevant chunk retrieval.
- `documents/` with three synthetic demo guidance documents.

The vector store automatically rebuilds when source documents are newer than the FAISS index. RAG responses include document name, source, and similarity score. The documents are demo guidance, not official government sources.

### Chat API

`POST /api/chat` supports conversational questions such as:

- `What business is suitable for me?`
- `Can I afford dairy farming?`
- `What support is available?`
- `What documents do I need?`
- `What should I do first?`

Deterministic topics use the existing engines. Informational topics use RAG and optional LLM explanation. No-key fallback prompts include available investment, skills, resources, and experience.

## Phase 8: UdyamSaathi Frontend

Implemented as a responsive Next.js journey in `frontend/app/page.js`, with reusable components in `frontend/components/JourneyComponents.js` and a centralized API client in `frontend/lib/api.js`.

The flow covers landing, simple profile assessment, conversational assessment, one primary recommendation with two alternatives, financial feasibility, synthetic support matches, approval checklist, and a three-to-five-step action plan.

The frontend calls FastAPI for profiles, recommendations, financial feasibility, support, approvals, action plans, and chat. Final results are never hardcoded. English copy is component-local and ready to move into a Kannada translation dictionary later.

Run the frontend:

```powershell
cd frontend
npm install
npm run dev
```

The frontend expects FastAPI at `http://127.0.0.1:8000`. Override it with `NEXT_PUBLIC_API_URL` when needed.

## Phase 9: Connect Frontend and Backend - Planned

Do not implement until requested.

Expected future responsibility:

- Connect the frontend to the FastAPI APIs.
- Add loading, error, and empty states.
- Keep API base URL configurable.
- Do not duplicate recommendation or financial logic in JavaScript.

## Phase 10: Complete Journey and Demo Mode - Planned

Do not implement until requested.

Expected journey:

1. Enter situation/profile.
2. Show one strongest business recommendation first.
3. Show two alternatives.
4. Show financial feasibility.
5. Show possible support and approvals.
6. Show next steps.
7. Support a predictable demo mode using Ramesh's synthetic profile.

## Phase 11: Testing and Error Handling - Planned

Do not implement until requested.

Expected future coverage:

- API tests
- Engine unit tests
- Database failure behavior
- Invalid input validation
- Empty result handling
- Frontend loading and error states
- Demo journey smoke test

## Phase 12: Docker and Final SIH Demo - Planned

Do not implement until requested.

Expected future responsibility:

- Add Docker configuration for the FastAPI backend and Next.js frontend.
- Continue using Supabase as the only database.
- Do not add a local PostgreSQL container.
- Add simple run instructions and final demo verification.

## Deferred Multilingual Requirement

After the planned phases are complete, add support for multiple Indian languages. This is a post-completion enhancement and must not disrupt the deterministic core engines.

Potential scope:

- Language selection in the frontend.
- Localized interface labels and instructions.
- Multilingual profile input handling.
- Translated recommendation explanations.
- Configurable translation/provider strategy for supported languages.
- Preserve original numeric values and deterministic scores regardless of language.

Do not implement multilingual support before the user requests the final enhancement.

## Running the Current System

Start FastAPI:

```powershell
cd C:\Users\shiva\OneDrive\Desktop\UdyamSaathi\backend
python -m pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload
```

Useful URLs:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/health/db`
- `http://127.0.0.1:8000/docs`

Start the frontend in a second terminal:

```powershell
cd C:\Users\shiva\OneDrive\Desktop\UdyamSaathi\frontend
npm install
npm run dev
```

## Handoff Rules for Future Agents

1. Read this file before making changes.
2. Check the current files because README or code may have user edits.
3. Work only on the phase explicitly requested.
4. Preserve Supabase as the only database.
5. Do not expose credentials from `backend/.env`.
6. Run focused tests immediately after edits.
7. Do not silently replace synthetic records with claims about real government schemes.
8. Keep recommendation and future financial logic deterministic and explainable.
9. Update this file after completing each phase.
10. Stop after the requested phase.
