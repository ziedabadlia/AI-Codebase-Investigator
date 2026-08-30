# GitHub Workflow

## Purpose

All development must follow a controlled:

```text
branch → commit → push → pull request → manual review → merge
```

workflow.

`main` represents the reviewed and stable project state.

---

# 1. MAIN BRANCH

Never develop directly on `main`.

Never commit feature work directly to `main`.

Never push feature work directly to:

```text
main
```

---

# 2. STARTING A FEATURE

Before implementation:

```bash
git checkout main
git pull origin main
git checkout -b feature/<feature-name>
```

Example:

```bash
git checkout -b feature/repository-ingestion
```

---

# 3. FEATURE BRANCH NAMING

Use:

```text
feature/<short-description>
```

Examples:

```text
feature/repository-ingestion
feature/hybrid-retrieval
feature/investigation-agent
```

Bug fixes:

```text
fix/<short-description>
```

Refactoring:

```text
refactor/<short-description>
```

Documentation:

```text
docs/<short-description>
```

---

# 4. TASK BREAKDOWN

Every feature must be divided into logical tasks.

Example:

```text
Feature: Repository Ingestion

Task 1:
Validate GitHub repository URLs

Task 2:
Implement GitHub API client

Task 3:
Persist repository metadata

Task 4:
Fetch repository files

Task 5:
Implement file filtering

Task 6:
Implement code chunking

Task 7:
Add tests
```

The coding agent should determine the appropriate task breakdown after
inspecting the existing code.

---

# 5. ONE TASK = ONE COMMIT

Each logical task gets its own commit.

Example:

```text
feat: validate GitHub repository URLs

feat: implement GitHub repository client

feat: persist repository metadata

feat: implement repository file ingestion

feat: add source file filtering

feat: implement code chunking

test: add repository ingestion tests
```

Do not combine unrelated tasks into one commit.

---

# 6. COMMIT FORMAT

Use conventional commit style where appropriate:

```text
feat: ...
fix: ...
refactor: ...
test: ...
docs: ...
chore: ...
```

Commit messages must:

- describe the change
- be concise
- use imperative language
- avoid meaningless descriptions

Bad:

```text
update
changes
stuff
final
fix
```

Good:

```text
feat: add GitHub repository URL validation
fix: prevent duplicate repository indexing
test: cover invalid repository URLs
```

---

# 7. BEFORE COMMIT

Before creating a commit:

1. Inspect the changed files.
2. Confirm the changes belong to the current task.
3. Run relevant tests.
4. Verify formatting.
5. Verify linting where appropriate.
6. Verify types.
7. Check `git diff`.

Do not commit unrelated modifications.

---

# 8. BEFORE PUSH

Before pushing a feature branch:

```text
1. Run tests
2. Run lint
3. Run type checks
4. Run build
5. Inspect git diff
6. Inspect git status
7. Confirm no secrets are staged
8. Review commit history
```

Do not knowingly push broken code unless the user explicitly requests it.

---

# 9. PUSH

Push the feature branch:

```bash
git push -u origin feature/<feature-name>
```

The branch should track the corresponding remote branch.

---

# 10. PULL REQUEST

After implementation and validation, create a pull request:

```text
feature/<feature-name>
        ↓
      main
```

The PR should contain:

## Summary

What was implemented.

## Changes

Important implementation changes.

## Architecture

Relevant architectural decisions.

## Testing

Commands that were run and their results.

## Screenshots

For significant UI changes.

## Known Limitations

Anything intentionally left out.

---

# 11. MANUAL REVIEW

The coding agent may create the PR but must NOT merge it automatically.

After creating the PR:

```text
STOP
```

Wait for the user to review it.

The user decides whether it should be merged.

---

# 12. PR REVIEW FEEDBACK

If the user requests changes:

1. Continue working on the same feature branch.
2. Implement the requested changes.
3. Create additional focused commits.
4. Run relevant checks.
5. Push the branch.
6. Update the existing PR.

Do not create a second PR for the same feature unless explicitly requested.

---

# 13. MERGE

Only merge into `main` when explicitly instructed by the user.

Example:

```text
User:
"Approved. Merge the PR."
```

Only after explicit approval may the agent perform the merge.

---

# 14. AFTER MERGE

After the PR has been merged:

```bash
git checkout main
git pull origin main
```

The next feature must start from the updated `main`.

---

# 15. FEATURE LIFECYCLE

Every feature follows:

```text
MAIN
 │
 ▼
Update main
 │
 ▼
Create feature branch
 │
 ▼
Inspect existing implementation
 │
 ▼
Break feature into tasks
 │
 ▼
Implement Task 1
 │
 ▼
Commit Task 1
 │
 ▼
Implement Task 2
 │
 ▼
Commit Task 2
 │
 ▼
...
 │
 ▼
Run tests / lint / typecheck / build
 │
 ▼
Review diff
 │
 ▼
Push branch
 │
 ▼
Create PR → main
 │
 ▼
STOP
 │
 ▼
Manual user review
 │
 ├── Changes requested
 │       ↓
 │    Same branch
 │       ↓
 │    Additional commits
 │       ↓
 │    Push
 │
 └── Approved
        ↓
      Merge
        ↓
    Update main
        ↓
    Next feature
```

---

# 16. IMPORTANT: DO NOT REWRITE SHARED HISTORY

Do not force-push a branch that has already been pushed unless explicitly
requested.

Avoid:

```bash
git push --force
```

If history needs to be rewritten, ask the user first.

Prefer normal commits when fixing PR feedback.

---

# 17. MERGE STRATEGY

Prefer a clean merge strategy that preserves understandable project history.

The exact merge method may depend on repository configuration.

Do not change repository-wide merge settings without approval.

---

# 18. PR QUALITY

A PR should be:

- focused
- understandable
- reviewable
- tested
- documented when necessary

Avoid giant PRs containing unrelated features.

---

# 19. AGENT RESPONSIBILITY

The coding agent is responsible for:

- branch creation
- task breakdown
- implementation
- task-level commits
- tests
- linting
- type checking
- build verification
- diff review
- pushing
- PR creation

The user is responsible for:

- reviewing the implementation
- reviewing the PR
- approving changes
- approving merges
- making final architectural decisions when significant trade-offs exist

---

# 20. ABSOLUTE RULE

Creating a PR does NOT imply permission to merge it.

The agent must wait for explicit user approval.
