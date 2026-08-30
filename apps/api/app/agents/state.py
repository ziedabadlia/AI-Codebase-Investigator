from typing import Annotated, TypedDict
import operator
from langchain_core.messages import AnyMessage

class AgentState(TypedDict):
    """
    The state for the LangGraph investigation agent.
    - messages: Thread of conversation including HumanMessage, AIMessage, and ToolMessages.
                The `operator.add` reducer appends new messages rather than overwriting.
    - iteration: Tracks the number of LLM tool invocation loops to prevent unbounded execution (ADR-006).
    """
    messages: Annotated[list[AnyMessage], operator.add]
    iteration: int
