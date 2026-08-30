import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage

from app.database.session import get_db
from app.database.models import Repository
from app.agents.graph import create_investigation_graph

router = APIRouter(
    prefix="/api/investigate",
    tags=["investigation"],
)

class InvestigationRequest(BaseModel):
    repository_id: uuid.UUID
    question: str

class InvestigationResponse(BaseModel):
    answer: str

@router.post("", response_model=InvestigationResponse)
async def investigate_codebase(
    payload: InvestigationRequest,
    db: Session = Depends(get_db)
) -> InvestigationResponse:
    """
    Executes a synchronous codebase investigation cycle using the Agent.
    Streaming via SSE will be deferred to a separate endpoint (ADR-002, /stream).
    """
    # 1. Verify repository exists
    repo = db.query(Repository).filter(Repository.id == payload.repository_id).first()
    if not repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found.")
        
    # 2. Re-create graph scoped to this DB and repo
    graph = create_investigation_graph(db, payload.repository_id)
    
    # 3. Initialize state and run
    # (Here we use .invoke() for a synchronous response. For streaming, we'd use .astream_events())
    initial_state = {
        "messages": [HumanMessage(content=payload.question)],
        "iteration": 0
    }
    
    try:
        # We cap recursion deep inside graph.py (MAX_ITERATIONS), but a recursion_limit 
        # on the graph invocation provides a hard safety net.
        result_state = graph.invoke(initial_state, {"recursion_limit": 50})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Agent execution failed: {str(e)}")
        
    # 4. Extract final AIMessage
    messages = result_state.get("messages", [])
    if not messages:
         return InvestigationResponse(answer="No response generated.")
         
    final_message = messages[-1]
    
    # Verify it's not a lingering tool call
    if hasattr(final_message, "tool_calls") and final_message.tool_calls:
        return InvestigationResponse(answer="Agent failed to produce a final textual answer without tool calls.")
        
    return InvestigationResponse(answer=final_message.content)
