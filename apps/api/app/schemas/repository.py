from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, HttpUrl

class RepositoryCreate(BaseModel):
    url: HttpUrl

class CodeChunkResponse(BaseModel):
    id: UUID
    start_line: int
    end_line: int
    content: str
    
    class Config:
        from_attributes = True

class RepositoryFileResponse(BaseModel):
    id: UUID
    file_path: str
    language: Optional[str]
    # To prevent huge payloads, we might omit raw content in normal list responses
    
    class Config:
        from_attributes = True

class RepositoryResponse(BaseModel):
    id: UUID
    url: str
    owner: str
    name: str
    default_branch: str
    commit_sha: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
