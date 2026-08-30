import uuid
from typing import List

from langchain_core.tools import tool, BaseTool
from sqlalchemy.orm import Session

from app.retrieval.search import hybrid_search, search_semantic, search_keyword
from app.database.models import RepositoryFile

def get_repository_tools(db: Session, repository_id: uuid.UUID) -> List[BaseTool]:
    """
    Factory function yielding LangChain tools configured for a specific repository.
    We use closures to inject the database session and repository UUID so the LLM
    only has to provide the functional arguments (e.g. `query` or `file_path`).
    """

    @tool
    def search_codebase(query: str) -> str:
        """
        Searches the targeted GitHub repository's codebase for the provided query.
        Returns a formatted string of code chunks with file paths and line numbers.
        Always use this tool first to find where concepts, variables, or functions are implemented!
        """
        results = hybrid_search(db, repository_id, query, limit=6)
        
        if not results:
            return f"No code found matching query '{query}'."
            
        formatted_results = []
        for r in results:
            header = f"\n--- File: {r['file_path']} (Lines {r['start_line']}-{r['end_line']}) ---"
            formatted_results.append(f"{header}\n{r['content']}")
            
        return "\n".join(formatted_results)

    @tool
    def read_file(file_path: str) -> str:
        """
        Reads the complete, raw content of a specific file in the repository.
        Use this when a codebase search yields interesting context but you need to see the entire file.
        Make sure to use the exact `file_path` provided in search results.
        """
        file = db.query(RepositoryFile).filter(
            RepositoryFile.repository_id == repository_id,
            RepositoryFile.file_path == file_path
        ).first()
        
        if not file:
            return f"Error: File '{file_path}' not found in the repository index."
            
        # Optional: Truncate massively large files so we don't blow up the context window.
        # 16,000 chars roughly = 4-5k tokens.
        content = file.content or ""
        if len(content) > 16000:
            content = content[:16000] + "\n\n...[FILE TRUNCATED DUE TO LENGTH]..."
            
        return f"--- Full content of {file_path} ---\n{content}"

    return [search_codebase, read_file]
