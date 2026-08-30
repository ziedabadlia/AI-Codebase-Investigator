# Architecture

## 1. SYSTEM OVERVIEW

The AI Codebase Investigator is a full-stack AI application.

High-level architecture:

```text
                         User
                           │
                           ▼
                    ┌─────────────┐
                    │   Next.js   │
                    │  Frontend   │
                    └──────┬──────┘
                           │
                    REST + SSE
                           │
                           ▼
                    ┌─────────────┐
                    │   FastAPI   │
                    │   Backend   │
                    └──────┬──────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
         GitHub API    LangGraph      PostgreSQL
                           │           + pgvector
                           │
                           ▼
                         Gemini
```

---

# 2. FRONTEND

Technology:

- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui where appropriate

Responsibilities:

- repository URL input
- repository status
- investigation interface
- streamed investigation events
- final AI response
- evidence display
- code viewer

The frontend should not contain backend business logic.

---

# 3. BACKEND

Technology:

- FastAPI
- Python
- Pydantic

Responsibilities:

- API endpoints
- GitHub integration
- repository ingestion
- file filtering
- code chunking
- embeddings
- retrieval
- agent orchestration
- investigation tools
- database access
- streaming events

Routers should remain thin.

Business logic belongs in appropriate service/domain modules.

---

# 4. DATABASE

Technology:

- PostgreSQL
- pgvector

Primary concepts:

```text
Repository
    │
    ├── Files
    │      │
    │      └── Code Chunks
    │              │
    │              └── Embedding
    │
    └── Investigations
```

Important database principles:

- use foreign keys
- use appropriate indexes
- use unique constraints
- use NOT NULL where appropriate
- use CHECK constraints where appropriate
- use migrations
- avoid duplicated data when unnecessary

---

# 5. REPOSITORY INGESTION

The application initially supports public GitHub repositories.

Pipeline:

```text
GitHub URL
    ↓
Validate URL
    ↓
Fetch repository metadata
    ↓
Fetch repository tree
    ↓
Filter unsupported/unwanted files
    ↓
Read source files
    ↓
Chunk source code
    ↓
Generate embeddings
    ↓
Persist data
```

The application must never execute repository code.

---

# 6. FILE FILTERING

The ingestion pipeline should avoid indexing:

- binary files
- generated files
- dependency directories
- build output
- obvious secret files
- excessively large files

Examples:

```text
.env
.env.*
*.pem
*.key
node_modules/
dist/
build/
.next/
```

The filtering strategy should be explicit and testable.

---

# 7. RETRIEVAL

The system uses hybrid retrieval.

Two retrieval mechanisms are used.

## Semantic Retrieval

Uses embeddings and pgvector to find conceptually relevant code.

Useful for questions such as:

```text
"Where is authentication implemented?"
```

## Keyword Retrieval

Used for exact:

- function names
- class names
- variables
- imports
- filenames
- identifiers

Useful for questions such as:

```text
"Where is verifyToken defined?"
```

Results should be combined and ranked before being provided to the investigation
agent.

---

# 8. AI INVESTIGATOR

The investigator is implemented using LangGraph.

The agent has access to repository investigation tools.

Initial tools:

```text
search_code
read_file
find_references
get_file_tree
```

The agent should investigate iteratively.

Conceptually:

```text
Question
   ↓
Analyze
   ↓
Search
   ↓
Inspect
   ↓
Need more evidence?
  │          │
 YES        NO
  │          │
  ▼          ▼
Search      Answer
again
```

Agent execution must have bounded iterations.

Avoid uncontrolled tool loops.

---

# 9. TOOL DESIGN

Agent tools should:

- have explicit inputs
- have validated outputs
- have clear descriptions
- perform one focused operation
- avoid hidden side effects

Tools should not execute arbitrary code.

Tools should not allow the model to access resources outside the intended
repository scope.

---

# 10. STRUCTURED OUTPUT

The final investigation result should use a validated schema.

Example conceptual structure:

```text
summary
confidence
findings
evidence
```

Pydantic should validate backend-facing AI output.

Do not rely on parsing arbitrary natural-language responses.

---

# 11. EVIDENCE

AI answers must reference repository evidence.

Evidence should identify:

```text
repository
file
line range
relevant code
```

The system should prefer evidence over unsupported claims.

If sufficient evidence cannot be found, the system should explicitly indicate
that the answer is uncertain.

---

# 12. STREAMING

Investigation progress is streamed from FastAPI to Next.js using SSE.

SSE is intentionally used because the primary communication pattern is:

```text
Server → Client
```

The server streams investigation events while the agent works.

WebSockets are not required for the initial MVP.

WebSockets may become appropriate in the future if the product requires
continuous bidirectional communication.

---

# 13. REST API

REST is used for resource-oriented operations.

Examples:

```http
POST /repositories
GET  /repositories/{id}

POST /investigations
GET  /investigations/{id}
```

API contracts should be explicit and validated.

Use HTTP methods according to their semantics.

---

# 14. IDEMPOTENCY

Repository ingestion should avoid duplicating work.

A repository revision should be identifiable using repository metadata such as
the commit SHA.

If the same repository revision has already been indexed, the system should
reuse existing indexed data instead of blindly duplicating it.

This behavior should be enforced both by application logic and appropriate
database constraints where practical.

---

# 15. DATABASE MIGRATIONS

All schema changes must be version controlled through migrations.

A migration should represent a specific schema change.

Examples:

```text
Create repositories
Create files
Create code_chunks
Create investigations
Add embedding column
Add indexes
Add constraints
```

Never rely on manually modifying a deployed database.

---

# 16. SECURITY

Repository contents are untrusted.

The application must protect against:

- prompt injection
- SSRF
- SQL injection
- XSS
- secret exposure

Do not execute repository code.

Do not index obvious secret files.

Validate GitHub URLs.

Use parameterized database access / ORM mechanisms.

Escape or safely render repository content.

---

# 17. ERROR HANDLING

The backend should distinguish between:

- validation errors
- GitHub API errors
- repository access errors
- indexing errors
- retrieval errors
- AI errors
- internal errors

Errors returned to the frontend must not expose secrets or sensitive internals.

---

# 18. PROJECT BOUNDARIES

The application is intentionally a modular monolith.

Do not introduce microservices for the MVP.

Current boundaries:

```text
Frontend
    ↓
Backend API
    ↓
Application Services
    ↓
Infrastructure
    ├── GitHub
    ├── PostgreSQL
    └── AI Provider
```

---

# 19. MVP SCOPE

The MVP supports:

- public GitHub repositories
- repository indexing
- hybrid retrieval
- AI investigation
- evidence-backed answers
- streamed investigation progress

The MVP does not require:

- user accounts
- billing
- teams
- organization management
- private repositories
- GitLab
- Bitbucket
- code editing
- pull request creation
- AI code generation

Do not add these unless explicitly requested.

---

# 20. ARCHITECTURAL CHANGES

Significant architecture changes require explicit user approval.

Examples:

- introducing Redis
- introducing a message queue
- replacing PostgreSQL
- replacing pgvector
- replacing LangGraph
- replacing FastAPI
- introducing microservices
- changing the AI provider
- changing the retrieval architecture
- introducing authentication

Before making such a change, explain:

1. Current limitation.
2. Proposed solution.
3. Alternatives.
4. Trade-offs.
5. Impact on complexity.

Then wait for approval.
