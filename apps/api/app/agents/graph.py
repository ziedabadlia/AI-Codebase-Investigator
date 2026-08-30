from typing import List, Literal

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from app.agents.state import AgentState
from app.core.config import settings
from app.tools.repository import get_repository_tools
from sqlalchemy.orm import Session
import uuid

# ADR-006: Bounded Agent Execution
MAX_ITERATIONS = 5

SYSTEM_PROMPT = """You are an expert AI Codebase Investigator.
You are tasked with answering technical questions about a codebase.

You have tools to:
1. Search the codebase (`search_codebase`): Input a term or concept, returns a chunk of matching code.
2. Read a full file (`read_file`): Input an exact filepath (found via search), returns the whole file context.

RULES:
- You MUST answer the user's question directly and concisely relying ON THE PROVIDED TOOLS.
- Always search before answering.
- If you cannot find the answer, state honestly that the codebase does not contain the required evidence.
- Do NOT guess file names or guess code without using the tools to verify.
- Base your final response ONLY on the results returned by your tools.

When you are ready to answer the user, do so directly without calling any further tools.
"""

def create_investigation_graph(db: Session, repository_id: uuid.UUID):
    """
    Constructs the LangGraph for the codebase investigation.
    We pass `db` and `repository_id` down to scope the tools dynamically.
    """
    
    # 1. Initialize Tools and LLM
    tools = get_repository_tools(db, repository_id)
    
    # We use gemini-2.5-flash as the primary fast investigator model
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.2 # Lower temperature for analytical tool-based workflows
    ).bind_tools(tools)
    
    # 2. Define Nodes
    
    def call_model(state: AgentState):
        """Invokes the LLM to decide the next step or return a final answer."""
        messages = state["messages"]
        iteration = state.get("iteration", 0)
        
        # Inject the system prompt if the thread is fresh
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
            
        # ADR-006: Force completion if we max out iterations to avoid infinite loops
        if iteration >= MAX_ITERATIONS:
            # Force the model to summarize based on what it found instead of looping
            # by removing the bound tools on the final pass.
            unbound_llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.1
            )
            # Append a hard hint
            messages.append(SystemMessage("MAX_ITERATIONS reached. Provide your final answer based ONLY on the evidence gathered so far. Support your answer with file paths where possible."))
            response = unbound_llm.invoke(messages)
        else:
            response = llm.invoke(messages)
            
        return {"messages": [response], "iteration": iteration + 1}

    # Built-in node that executes whatever tools the LLM requested
    tool_node = ToolNode(tools)
    
    # 3. Define State Edges and Transitions
    
    def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
        """Router to determine whether to call tools or finish."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If the LLM made a tool call (and we haven't maxed out), route to tools
        if last_message.tool_calls and state.get("iteration", 0) <= MAX_ITERATIONS:
            return "tools"
        
        # Otherwise, the LLM just replied with text - we are done
        return "__end__"
        
    # 4. Build the Graph
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "__end__": END})
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()
