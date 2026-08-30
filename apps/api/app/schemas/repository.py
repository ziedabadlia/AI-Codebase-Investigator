from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, HttpUrl, ConfigDict

class RepositoryCreate(BaseModel):
    url: HttpUrl

class CodeChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    start_line: int
    end_line: int
    content: str

class RepositoryFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    file_path: str
    language: Optional[str]

class RepositoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    url: str
    owner: str
    name: str
    default_branch: str
    commit_sha: str
    created_at: datetime
    updated_at: Optional[datetime]

