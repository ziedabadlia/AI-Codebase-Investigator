from app.agents.graph import create_investigation_graph
from app.tools.repository import get_repository_tools
import uuid
from unittest.mock import MagicMock
from langchain_core.messages import HumanMessage

def test_tools_factory_returns_expected_tools():
    # Mock DB session
    db_mock = MagicMock()
    repo_id = uuid.uuid4()
    
    tools = get_repository_tools(db_mock, repo_id)
    
    # We expect 2 tools: search_codebase and read_file
    assert len(tools) == 2
    tool_names = [t.name for t in tools]
    assert "search_codebase" in tool_names
    assert "read_file" in tool_names

def test_graph_compiles_successfully(monkeypatch):
    """
    Validates that the LangGraph state transitions and node wiring are valid.
    Compilation will throw an exception if edges are broken.
    """
    from app.core.config import settings
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "mock_key_for_testing_graph_compilation")
    
    db_mock = MagicMock()
    repo_id = uuid.uuid4()
    
    graph = create_investigation_graph(db_mock, repo_id)
    assert graph is not None

def test_tool_search_codebase_handles_empty_db():
    db_mock = MagicMock()
    # Mock SQLAlchemy query chain to return empty results for hybrid search
    db_mock.query.return_value.join.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
    db_mock.query.return_value.join.return_value.filter.return_value.limit.return_value.all.return_value = []
    
    repo_id = uuid.uuid4()
    tools = get_repository_tools(db_mock, repo_id)
    
    search_tool = next(t for t in tools if t.name == "search_codebase")
    
    # Execute the tool
    # Note: query is required, 'mode' isn't explicitly defined in our tool, just 'query'
    result = search_tool.invoke({"query": "verifyToken"})
    
    assert "No code found matching query" in result

def test_tool_read_file_handles_missing_file():
    db_mock = MagicMock()
    # Mock SQLAlchemy query returning Nothing
    db_mock.query.return_value.filter.return_value.first.return_value = None
    
    repo_id = uuid.uuid4()
    tools = get_repository_tools(db_mock, repo_id)
    read_tool = next(t for t in tools if t.name == "read_file")
    
    result = read_tool.invoke({"file_path": "nonexistent.py"})
    assert "Error: File" in result
    assert "not found" in result
