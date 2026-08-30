import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import Repository, RepositoryFile, CodeChunk as CodeChunkModel
from app.schemas.repository import RepositoryCreate, RepositoryResponse
from app.github.client import GitHubClient, GitHubAPIError
from app.core.filtering import is_file_allowed
from app.embeddings.chunker import chunk_file
from app.embeddings.service import embed_texts

router = APIRouter(
    prefix="/api/repositories",
    tags=["repositories"],
)


def _detect_language(file_path: str) -> str | None:
    """Best-effort language detection from file extension."""
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


@router.post("", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
async def ingest_repository(
    payload: RepositoryCreate,
    db: Session = Depends(get_db),
) -> RepositoryResponse:
    """
    Accepts a public GitHub URL, runs the ingestion pipeline, and returns
    the persisted repository record.

    Pipeline:
      1. Validate the URL is a GitHub repository.
      2. Fetch repository metadata (owner, name, default_branch, commit_sha).
      3. Check idempotency: skip re-ingestion if same commit SHA already indexed.
      4. Fetch the repository file tree.
      5. Filter files using the allow-list rules.
      6. For each allowed file: fetch content → chunk → embed → persist.
    """
    url_str = str(payload.url)
    client = GitHubClient()

    # 1. Parse and validate GitHub URL
    try:
        owner, repo_name = client.parse_url(url_str)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    # 2. Fetch repository metadata
    try:
        metadata = await client.get_repo_metadata(owner, repo_name)
    except GitHubAPIError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    commit_sha = metadata["commit_sha"]

    # 3. Idempotency check — avoid re-indexing the same commit
    existing = db.query(Repository).filter(
        Repository.owner == owner,
        Repository.name == repo_name,
        Repository.commit_sha == commit_sha,
    ).first()

    if existing:
        return existing

    # Remove old records for this URL if they exist (re-index on new commit)
    stale = db.query(Repository).filter(Repository.url == url_str).first()
    if stale:
        db.delete(stale)
        db.flush()

    # Create the repository record
    repository = Repository(
        url=url_str,
        owner=owner,
        name=repo_name,
        default_branch=metadata["default_branch"],
        commit_sha=commit_sha,
    )
    db.add(repository)
    db.flush()  # Get the ID without committing yet

    # 4. Fetch repository tree
    try:
        tree = await client.get_repo_tree(owner, repo_name, commit_sha)
    except GitHubAPIError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    # 5 & 6. Filter, fetch content, chunk, embed, persist
    for item in tree:
        if item.get("type") != "blob":
            continue

        file_path: str = item.get("path", "")
        blob_url: str = item.get("url", "")

        if not is_file_allowed(file_path):
            continue

        try:
            raw_content = await client.get_file_content(blob_url)
        except GitHubAPIError:
            # Non-fatal: skip files that fail to download
            continue

        language = _detect_language(file_path)

        # Persist the file record with its full raw content
        repo_file = RepositoryFile(
            repository_id=repository.id,
            file_path=file_path,
            language=language,
            content=raw_content,
        )
        db.add(repo_file)
        db.flush()

        # Chunk and embed
        chunks = chunk_file(raw_content)
        if not chunks:
            continue

        chunk_texts = [c.content for c in chunks]
        vectors = embed_texts(chunk_texts)

        for chunk, vector in zip(chunks, vectors):
            db.add(
                CodeChunkModel(
                    file_id=repo_file.id,
                    start_line=chunk.start_line,
                    end_line=chunk.end_line,
                    content=chunk.content,
                    embedding=vector,
                )
            )

    db.commit()
    db.refresh(repository)
    return repository


@router.get("/{repository_id}", response_model=RepositoryResponse)
def get_repository(
    repository_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> RepositoryResponse:
    """Returns metadata for a previously ingested repository."""
    repository = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repository:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found.")
    return repository
