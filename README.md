# AI Codebase Investigator

AI Codebase Investigator is a full-stack, evidence-backed developer tool designed to answer technical questions about GitHub codebases. The application utilizes a FastAPI backend running a LangGraph investigation agent with semantic retrieval powered by pgvector, local sentence-transformers, and Gemini 2.5 Flash.

This is a personal interview showcase built for the Full Stack AI-Assisted Development position at Lasting Dynamics, proving robust engineering principles with $0 operational cost constraints.

---

## Technical Stack

* **Frontend:** Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, shadcn/ui, TanStack Query
* **Backend:** Python 3.12, FastAPI, Uvicorn, LangGraph, SQLAlchemy, Alembic, Pydantic v2
* **AI Ecosystem:** Gemini 2.5 Flash (via free API tier), local `sentence-transformers` CPU embeddings (`all-MiniLM-L6-v2`)
* **Vector Database:** PostgreSQL with `pgvector` extension hosted on a free **Supabase** instance.

---

## Directory Architecture

```text
ai-codebase-investigator/
├── apps/
│   ├── web/                    # Next.js 15 Frontend
│   └── api/                    # FastAPI Backend
├── docker-compose.yml          # Optional local PostgreSQL with pgvector container
├── package.json                # Monorepo task orchestration
├── pnpm-workspace.yaml         # PNPM workspaces configuration
├── turbo.json                  # Turborepo task runner caching
├── .env.example                # Root environment template
└── README.md                   # This documentation
```

---

## Local Development Setup

### 1. Prerequisites
* **Node.js:** v18+ (tested on v22)
* **Python:** v3.10+ (tested on v3.12)
* **pnpm:** Installed globally (`npm install -g pnpm`)
* **Supabase / Postgres DB:** A free Supabase database with the `pgvector` extension enabled.

### 2. Environment Configuration
Copy the `.env.example` at the root folder to `.env`:
```bash
cp .env.example .env
```
Fill in the credentials:
* `DATABASE_URL`: Your Supabase connection string or local Postgres container.
* `GEMINI_API_KEY`: Get your free Gemini developer key from Google AI Studio.
* `GITHUB_TOKEN`: Create a personal access token to prevent API rate limiting.

### 3. Backend Setup
Initialize the virtual environment and install the Python dependencies:
```bash
# From workspace root
python3 -m venv apps/api/.venv
source apps/api/.venv/bin/activate
pip install -r apps/api/requirements.txt
```

### 4. Frontend Setup & Monorepo Lockfile
Resolve and install the frontend dependencies in the workspaces:
```bash
# From workspace root
pnpm install --ignore-scripts
```

### 5. Running the Application
We use **Turborepo** to orchestrate both backend and frontend execution concurrently:
```bash
# From workspace root
pnpm dev
```
* **Frontend UI:** App boots at [http://localhost:3000](http://localhost:3000)
* **Backend Docs:** OpenAPI docs boot at [http://localhost:8000/docs](http://localhost:8000/docs)
* **Backend Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

---

## Engineering Guidelines
Please follow the rules laid out in:
* `AGENTS.md` (Agent developer rules)
* `docs/CODE_STANDARDS.md` (Formatting, linting, styles)
* `docs/ARCHITECTURE.md` (System flows, security)
* `docs/DECISIONS.md` (Architecture decisions log)
