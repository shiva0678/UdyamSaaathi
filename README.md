# UdyamSaathi

UdyamSaathi is a Smart India Hackathon 2026 prototype that helps rural entrepreneurs move from their current situation to a practical business path.

This repository currently contains **Phase 8: UdyamSaathi Frontend**. The datasets are synthetic demo records and must not be presented as verified government information.

## Project Structure

```text
backend/   FastAPI service
frontend/  Next.js web application
data/      Synthetic demo datasets for the Phase 2 prototype
rag/       Reserved for future RAG assets
docker/    Reserved for future deployment files
```

## Backend Setup

From the repository root:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a local `backend/.env` file from `backend/.env.example` and set the Supabase PostgreSQL connection string:

```env
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@[pooler-host]:5432/postgres
```

In Supabase, open **Connect** and choose **Postgres**, then copy the **Session pooler** connection string. Use the Session pooler when your network does not support IPv6; the direct `db.<project-ref>.supabase.co` host may resolve only to IPv6. Replace the password placeholder and URL-encode special characters in the password if needed. Do not commit `backend/.env` or hardcode credentials.

Create the tables and seed the synthetic demo data:

```powershell
python -m app.seed
```

The seed command creates `users`, `businesses`, `schemes`, `approvals`, and `market_data`, then upserts the records from `data/`.

## Core API Endpoints

All API endpoints are served by FastAPI at `http://127.0.0.1:8000`:

| Method | Endpoint                       | Purpose                             |
| ------ | ------------------------------ | ----------------------------------- |
| `POST` | `/api/users/profile`           | Save a user profile                 |
| `GET`  | `/api/businesses`              | List synthetic business profiles    |
| `GET`  | `/api/businesses/{id}`         | Get one business profile            |
| `GET`  | `/api/schemes`                 | List synthetic support records      |
| `GET`  | `/api/approvals/{business_id}` | Get approvals for a business        |
| `GET`  | `/api/market/{location}`       | Get market data for a location      |
| `POST` | `/api/recommendations`         | Get the top three business matches  |
| `POST` | `/api/financial/feasibility`   | Calculate financial feasibility     |
| `POST` | `/api/support/match`           | Match synthetic support records     |
| `POST` | `/api/action-plan`             | Generate practical next steps       |
| `POST` | `/api/chat`                    | Conversational AI and RAG assistant |

Recommendations use a deterministic rule-based score with these weights: capital 30%, skills 25%, resources 20%, location 15%, and experience 10%. Every response includes component scores, reasons, strengths, limitations, alternatives, and the statement: `Match score is a prototype suitability score, not a guarantee of success.`

Financial feasibility is calculated by Python from the user's capital and the selected business record. The current synthetic data uses `minimum_capital` as the initial-investment estimate. The response includes monthly and annual totals, capital gap, ROI, financial status, risk notes, and `Synthetic estimates for prototype demonstration.`

Support matching is deterministic and uses location, business sector, capital, target group, and eligibility conditions. Every support result contains `source_type: synthetic` and `verification_status: demo`, together with `Demo information - verify with official sources before applying.` Approval navigation is available through `/api/approvals/{business_id}`. The action-plan endpoint combines the recommendation, financial feasibility, support matches, and approvals into three to five next steps.

The chat endpoint accepts a message and optional `user_id`, `business_id`, and structured profile. Financial, support, approval, recommendation, and action-plan questions are routed to the existing deterministic/database engines. Informational questions use the small FAISS RAG index and return source attribution. When `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_BASE_URL`, or `LLM_MODEL` is missing, the rule-based fallback remains active.

To rebuild the demo FAISS index manually:

```powershell
cd ..
python -c "from rag.vector_store import build_vector_store; build_vector_store()"
```

The RAG documents are synthetic demo guidance. They are not official government sources.

## Frontend Journey

The Next.js frontend provides an action-first guided journey:

1. Landing page with assessment and demo-profile entry points.
2. Simple profile assessment for location, capital, skills, resources, experience, and goal.
3. Conversational assessment with the optional LLM/RAG assistant.
4. One primary recommendation followed by two alternatives.
5. Financial feasibility cards.
6. Synthetic support matches with verification warnings.
7. Approval and document checklist.
8. Personalized next-step action plan.

The frontend uses `frontend/lib/api.js` as its centralized FastAPI client and reusable components in `frontend/components/`. The English copy is kept at the component boundary, making a later Kannada dictionary straightforward.

Example profile request:

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

Example response:

```json
{
  "id": "user-generated-id",
  "name": "Ramesh",
  "location": "Karnataka",
  "capital": 200000,
  "skills": ["Farming", "Animal Care"],
  "resources": ["2 acres of land", "Available water"],
  "experience": "Basic",
  "goal": "Increase income",
  "profile_type": "User Profile"
}
```

Interactive Swagger documentation is available at `http://127.0.0.1:8000/docs`.

Run the API:

```powershell
uvicorn app.main:app --reload
```

The backend is available at `http://127.0.0.1:8000`.

- `GET /` returns the welcome message.
- `GET /health` returns the API health status.
- `GET /health/db` checks the Supabase database connection.
- `GET /docs` opens the FastAPI documentation.

When the database is connected, `GET /health/db` returns:

```json
{ "database": "connected" }
```

To verify seeded records in Supabase, open the SQL Editor and run:

```sql
select 'users' as table_name, count(*) from users
union all select 'businesses', count(*) from businesses
union all select 'schemes', count(*) from schemes
union all select 'approvals', count(*) from approvals
union all select 'market_data', count(*) from market_data;
```

## Frontend Setup

Open a second terminal from the repository root:

```powershell
cd frontend
npm install
```

Run the web application:

```powershell
npm run dev
```

The frontend is available at `http://localhost:3000`.

## Running Both Applications

Keep the backend terminal running with `uvicorn app.main:app --reload` and the frontend terminal running with `npm run dev`. Open `http://localhost:3000` in a browser.

## Production Frontend Check

```powershell
cd frontend
npm run build
npm run start
```
