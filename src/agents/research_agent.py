"""
research_agent.py — Public entry point for the Research Assistant Agent.

Provides run_research_agent(), which wires the compiled LangGraph graph to an
initial state and executes the full pipeline asynchronously.
"""

from src.graph.state import ResearchState
from src.graph.workflow import build_graph
from src.token_tracker import tracker


async def run_research_agent(query: str) -> ResearchState:
    """
    Run the full research pipeline for a given query string.

    Executes: search → extract → summarize → store (via MCP).

    Args:
        query: The topic or question to research.

    Returns:
        The final ResearchState after all four nodes have executed.
    """
    tracker.reset()  # Clear data from any previous run

    compiled = build_graph()
    initial_state: ResearchState = {
        "query": query,
        "search_results": [],
        "extracted_content": "",
        "summary": "",
        "status": "",
    }
    return await compiled.ainvoke(initial_state)
