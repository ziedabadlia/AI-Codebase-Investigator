import json
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from sqlalchemy.orm import Session

from app.agents.graph import create_investigation_graph
from app.core.config import settings
from app.database.models import Repository
from app.database.session import get_db
from app.github.client import GitHubClient, GitHubAPIError
from app.core.filtering import is_file_allowed
from app.embeddings.chunker import chunk_file
from app.embeddings.service import embed_texts
from app.database.models import RepositoryFile, CodeChunk as CodeChunkModel

router = APIRouter(
    prefix="/api/stream",
    tags=["stream"],
)


def _sse(event: str, data: dict) -> str:
    """Formats a single Server-Sent Event string."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _detect_language(file_path: str) -> str | None:
    ext_map = {
        ".py": "python", ".ts": "typescript", ".tsx": "typescript",
        ".js": "javascript", ".jsx": "javascript", ".go": "go",
        ".rs": "rust", ".java": "java", ".rb": "ruby",
        ".cs": "csharp", ".cpp": "cpp", ".c": "c",
        ".md": "markdown", ".json": "json", ".yaml": "yaml", ".yml": "yaml",
        ".toml": "toml", ".sh": "shell", ".sql": "sql",
        ".html": "html", ".css": "css",
    }
    dot = file_path.rfind(".")
    if dot != -1:
        return ext_map.get(file_path[dot:].lower())
    return None


async def _ingest_repository(
    db: Session, url: str, owner: str, repo_name: str, metadata: dict
) -> AsyncGenerator[str, None]:
    """
    Runs the repository ingestion pipeline and yields SSE progress events.
    This allows the frontend to show ingestion progress before the agent starts.
    """
    client = GitHubClient()
    commit_sha = metadata["commit_sha"]

    yield _sse("status", {"type": "ingesting", "message": f"Fetching file tree for {owner}/{repo_name}…"})

    try:
        tree = await client.get_repo_tree(owner, repo_name, commit_sha)
    except GitHubAPIError as exc:
        yield _sse("error", {"message": str(exc)})
        return

    allowed_files = [item for item in tree if item.get("type") == "blob" and is_file_allowed(item.get("path", ""))]
    total = len(allowed_files)

    yield _sse("status", {"type": "ingesting", "message": f"Indexing {total} source files…"})

    # Create repository record
    repository = Repository(
        url=url,
        owner=owner,
        name=repo_name,
        default_branch=metadata["default_branch"],
        commit_sha=commit_sha,
    )
    db.add(repository)
    db.flush()

    for i, item in enumerate(allowed_files):
        file_path: str = item.get("path", "")
        blob_url: str = item.get("url", "")

        try:
            raw_content = await client.get_file_content(blob_url)
        except GitHubAPIError:
            continue

        language = _detect_language(file_path)
        repo_file = RepositoryFile(
            repository_id=repository.id,
            file_path=file_path,
            language=language,
            content=raw_content,
        )
        db.add(repo_file)
        db.flush()

        chunks = chunk_file(raw_content)
        if chunks:
            vectors = embed_texts([c.content for c in chunks])
            for chunk, vector in zip(chunks, vectors):
                db.add(CodeChunkModel(
                    file_id=repo_file.id,
                    start_line=chunk.start_line,
                    end_line=chunk.end_line,
                    content=chunk.content,
                    embedding=vector,
                ))

        # Emit progress every 10 files to avoid flooding SSE
        if (i + 1) % 10 == 0 or (i + 1) == total:
            yield _sse("status", {
                "type": "ingesting",
                "message": f"Indexed {i + 1}/{total} files…"
            })

    db.commit()
    db.refresh(repository)
    yield _sse("status", {"type": "ingested", "message": "Repository indexed successfully.", "repository_id": str(repository.id)})
    return


async def _stream_investigation(
    db: Session, repository_id: uuid.UUID, question: str
) -> AsyncGenerator[str, None]:
    """Streams LangGraph agent events as SSE."""
    graph = create_investigation_graph(db, repository_id)
    initial_state = {
        "messages": [HumanMessage(content=question)],
        "iteration": 0,
    }

    answer_buffer = ""

    async for event in graph.astream_events(initial_state, version="v2", config={"recursion_limit": 50}):
        kind = event["event"]
        name = event.get("name", "")

        if kind == "on_tool_start":
            tool_name = name
            tool_input = event.get("data", {}).get("input", {})
            if tool_name == "search_codebase":
                yield _sse("status", {"type": "searching", "query": tool_input.get("query", "")})
            elif tool_name == "read_file":
                yield _sse("status", {"type": "reading", "file": tool_input.get("file_path", "")})

        elif kind == "on_chat_model_stream":
            chunk = event.get("data", {}).get("chunk")
            if chunk and hasattr(chunk, "content") and chunk.content:
                answer_buffer += chunk.content
                yield _sse("token", {"content": chunk.content})

        elif kind == "on_chain_end" and name == "LangGraph":
            # Graph finished — emit any accumulated evidence from the last tool results
            # Walk the messages for ToolMessages to extract evidence
            final_state = event.get("data", {}).get("output", {})
            messages = final_state.get("messages", [])
            for msg in messages:
                # ToolMessages contain the raw output of search_codebase / read_file
                if hasattr(msg, "content") and "--- File:" in str(msg.content):
                    # Parse evidence segments from the tool output
                    for segment in str(msg.content).split("\n--- File:"):
                        if not segment.strip():
                            continue
                        lines = segment.splitlines()
                        header = lines[0] if lines else ""
                        code = "\n".join(lines[1:]) if len(lines) > 1 else ""

                        # Parse "path/to/file.py (Lines X-Y) ---"
                        import re
                        match = re.search(r"^(.+?)\s+\(Lines (\d+)-(\d+)\)", header.strip(" -"))
                        if match:
                            yield _sse("evidence", {
                                "file": match.group(1).strip(),
                                "start_line": int(match.group(2)),
                                "end_line": int(match.group(3)),
                                "content": code.strip(),
                            })

    yield _sse("done", {})


@router.get("")
async def stream_investigation(
    repo_url: str = Query(..., description="Public GitHub repository URL"),
    question: str = Query(..., description="Technical question about the codebase"),
    db: Session = Depends(get_db),
):
    """
    SSE endpoint that:
    1. Ingests the repository (if not already indexed at the current commit).
    2. Streams the LangGraph investigation events in real time.
    """
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GEMINI_API_KEY is not configured.",
        )

    client = GitHubClient()
    try:
        owner, repo_name = client.parse_url(repo_url)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    try:
        metadata = await client.get_repo_metadata(owner, repo_name)
    except GitHubAPIError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    commit_sha = metadata["commit_sha"]

    async def event_generator() -> AsyncGenerator[str, None]:
        # Check idempotency
        existing = db.query(Repository).filter(
            Repository.owner == owner,
            Repository.name == repo_name,
            Repository.commit_sha == commit_sha,
        ).first()

        repository_id: uuid.UUID

        if existing:
            yield _sse("status", {"type": "cached", "message": "Repository already indexed."})
            repository_id = existing.id
        else:
            # Remove stale record if commit changed
            stale = db.query(Repository).filter(Repository.url == repo_url).first()
            if stale:
                db.delete(stale)
                db.flush()

            async for sse_chunk in _ingest_repository(db, repo_url, owner, repo_name, metadata):
                yield sse_chunk

            # Re-query after ingestion
            new_repo = db.query(Repository).filter(
                Repository.owner == owner,
                Repository.name == repo_name,
                Repository.commit_sha == commit_sha,
            ).first()

            if not new_repo:
                yield _sse("error", {"message": "Repository ingestion failed."})
                return

            repository_id = new_repo.id

        yield _sse("status", {"type": "investigating", "message": "Starting investigation…"})

        async for sse_chunk in _stream_investigation(db, repository_id, question):
            yield sse_chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering for SSE
        },
    )
