import uuid
from typing import List, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.models import CodeChunk, RepositoryFile
from app.embeddings.service import embed_query


def search_semantic(db: Session, repository_id: uuid.UUID, query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Performs semantic vector search across chunks for a specific repository.
    Uses pgvector's <=> cosine distance operator.
    """
    query_vector = embed_query(query)
    if not query_vector:
        return []

    results = (
        db.query(CodeChunk, RepositoryFile)
        .join(RepositoryFile, CodeChunk.file_id == RepositoryFile.id)
        .filter(RepositoryFile.repository_id == repository_id)
        .order_by(CodeChunk.embedding.cosine_distance(query_vector))
        .limit(limit)
        .all()
    )

    return _format_results(results, "semantic")


def search_keyword(db: Session, repository_id: uuid.UUID, query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Performs a simple keyword layout search avoiding complex Full-Text-Search setups.
    Searches across chunk content and the file path.
    """
    search_term = f"%{query}%"

    results = (
        db.query(CodeChunk, RepositoryFile)
        .join(RepositoryFile, CodeChunk.file_id == RepositoryFile.id)
        .filter(
            RepositoryFile.repository_id == repository_id,
            or_(
                CodeChunk.content.ilike(search_term),
                RepositoryFile.file_path.ilike(search_term)
            )
        )
        .limit(limit)
        .all()
    )

    return _format_results(results, "keyword")


def hybrid_search(db: Session, repository_id: uuid.UUID, query: str, limit: int = 7) -> List[Dict[str, Any]]:
    """
    Combines semantic and keyword searches, deduplicating the results.
    We fetch half the limit from each to get a diverse spread of exact matches and conceptual matches.
    """
    semantic_limit = max(1, int(limit * 0.7))
    keyword_limit = max(1, limit - semantic_limit)
    
    # Simple heuristics to detect if user passes exact references (e.g. function() or camelCase)
    # If they do, we boost the keyword search limit.
    if "(" in query or "_" in query or any(c.isupper() for c in query):
        keyword_limit = max(1, int(limit * 0.5))
        semantic_limit = max(1, limit - keyword_limit)

    semantic_res = search_semantic(db, repository_id, query, limit=semantic_limit)
    keyword_res = search_keyword(db, repository_id, query, limit=keyword_limit)

    # Deduplicate by CodeChunk ID
    seen_ids = set()
    combined = []

    for res in keyword_res + semantic_res:
        chunk_id = res["chunk_id"]
        if chunk_id not in seen_ids:
            seen_ids.add(chunk_id)
            combined.append(res)
            
    # Respect strict limit to prevent blowing up the LLM context window
    return combined[:limit]


def _format_results(results: List[Any], source: str) -> List[Dict[str, Any]]:
    """Formats SQLAlchemy joined tuples into simple dictionaries."""
    formatted = []
    for chunk, file in results:
        formatted.append({
            "chunk_id": str(chunk.id),
            "file_path": file.file_path,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "content": chunk.content,
            "source": source
        })
    return formatted
