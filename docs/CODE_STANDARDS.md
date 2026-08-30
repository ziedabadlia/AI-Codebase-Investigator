# Code Standards

## 1. GENERAL RULE

Write code that a human engineer can understand, review, maintain, and explain
during a technical interview.

Prefer explicit and readable code over clever code.

---

# 2. TYPESCRIPT

Use strict TypeScript.

Avoid:

```ts
any;
```

unless there is a documented reason.

Prefer:

```ts
unknown;
```

when the type is genuinely unknown.

Define explicit types for:

- API responses
- component props
- domain objects
- AI responses
- investigation events

Avoid unnecessary type assertions.

---

# 3. REACT

Prefer functional components.

Keep components focused.

Avoid components that simultaneously handle:

- API communication
- complex business logic
- state management
- data transformation
- large UI trees

Move reusable business logic into appropriate hooks/services.

Be careful with:

- useEffect dependencies
- state updates
- unnecessary re-renders
- stale closures
- infinite render loops

Do not add `"use client"` unless client-side behavior is actually required.

---

# 4. NEXT.JS

Use the App Router.

Follow the existing project convention for:

- Server Components
- Client Components
- server-side data fetching
- API communication

Prefer Server Components when client-side interactivity is not required.

Do not make an entire page a Client Component simply because one child
component requires client-side behavior.

---

# 5. PYTHON

Use type hints.

Prefer:

```python
def search_code(query: str) -> list[CodeChunk]:
```

over untyped functions.

Use Pydantic models for external/API data.

Keep functions focused.

Avoid excessively large service classes.

---

# 6. FASTAPI

Validate:

- request bodies
- query parameters
- path parameters
- external data

Use appropriate HTTP status codes.

Keep routers thin.

Business logic should live in appropriate service/domain modules.

---

# 7. DATABASE

Use migrations for schema changes.

Do not manually modify database schemas as part of normal development.

Use constraints where appropriate.

Prefer database-level guarantees for important invariants.

Examples:

```text
NOT NULL
UNIQUE
FOREIGN KEY
CHECK
```

Use indexes based on actual query patterns.

Do not add indexes without understanding why they are needed.

---

# 8. API DESIGN

Endpoints should be:

- predictable
- resource-oriented
- validated
- documented

Use HTTP methods according to their semantics.

Do not use POST for everything.

Use appropriate status codes.

Avoid leaking internal implementation details through API contracts.

---

# 9. ERROR HANDLING

Errors should be:

- explicit
- actionable
- logged appropriately
- safe for users

Never expose:

- API keys
- database credentials
- internal secrets
- stack traces in production responses

Do not silently swallow exceptions.

Avoid broad exception handling unless there is a clear recovery strategy.

---

# 10. LOGGING

Logs should provide useful operational information.

Avoid logging:

- API keys
- authentication tokens
- secrets
- sensitive repository contents

Use structured logging where practical.

---

# 11. NAMING

Names should communicate intent.

Bad:

```text
data
result
thing
temp
x
helper
```

Prefer:

```text
repository
investigation
retrieved_chunks
embedding_result
```

Avoid unexplained abbreviations.

---

# 12. COMMENTS

Comments should explain WHY, not WHAT.

Bad:

```ts
// Set loading to true
setLoading(true);
```

Good:

```ts
// Prevent duplicate investigation requests while the current
// investigation is still running.
setLoading(true);
```

Do not add comments everywhere.

Prefer readable code over comments explaining obvious behavior.

---

# 13. DEPENDENCIES

Before adding a dependency:

1. Check whether the functionality already exists.
2. Check whether the existing stack can solve the problem.
3. Consider maintenance cost.
4. Consider bundle/runtime impact.
5. Consider whether it is free and compatible with the project requirements.
6. Explain why the dependency is justified.

Do not add dependencies simply because an AI-generated solution commonly uses
them.

---

# 14. TESTS

Tests should focus on behavior and important business logic.

Prioritize tests for:

- repository URL validation
- repository ingestion
- file filtering
- chunking
- retrieval
- API validation
- idempotency
- agent/tool behavior
- security-sensitive logic

Avoid tests that simply duplicate implementation details.

---

# 15. FORMATTING AND LINTING

All code must follow the project's configured:

- formatter
- linter
- TypeScript configuration
- Python tooling

Do not bypass linting or type checking just to make a feature pass.

---

# 16. FUNCTION SIZE

Functions should have one clear responsibility.

If a function becomes difficult to understand, consider splitting it into
smaller units.

Do not split functions artificially just to make them shorter.

---

# 17. COMPONENT SIZE

Components should have a clear responsibility.

If a component contains multiple unrelated concerns, consider extracting:

- subcomponents
- hooks
- utility functions
- domain-specific logic

Do not create abstractions without a real reuse or clarity benefit.

---

# 18. STATE MANAGEMENT

Use the simplest state management mechanism appropriate for the problem.

Prefer:

1. local React state
2. server state / data fetching patterns
3. shared state only when genuinely necessary

Do not introduce a global state library without a demonstrated need.

---

# 19. ASYNC CODE

Handle asynchronous operations explicitly.

Account for:

- loading
- success
- failure
- cancellation where appropriate
- duplicate requests
- stale requests

Avoid unhandled promises.

---

# 20. AI-GENERATED CODE

AI-generated code must be reviewed before committing.

The coding agent must understand the code it writes.

Do not blindly copy generated implementations.

The final implementation must follow this document even if an external example
uses different conventions.

---

# 21. REFACTORING

Do not mix large refactors with unrelated feature work.

If a refactor is necessary:

1. Explain why.
2. Keep it focused.
3. Use a separate commit where appropriate.
4. Avoid changing behavior unintentionally.

---

# 22. SECURITY

Never commit:

- `.env`
- API keys
- tokens
- passwords
- private keys
- credentials

Use environment variables for secrets.

Validate external input.

Treat AI-generated content as untrusted until validated.

---

# 23. CODE REVIEW STANDARD

Before creating a PR, ask:

- Is this the simplest solution?
- Is the code readable?
- Is there duplicated logic?
- Are types correct?
- Are errors handled?
- Are security concerns addressed?
- Are tests sufficient?
- Did I introduce an unnecessary dependency?
- Does the implementation follow the architecture?
- Does it follow the design system?
