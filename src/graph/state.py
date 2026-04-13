"""
state.py — LangGraph state definition for the Research Assistant Agent.

ResearchState is the single TypedDict that flows through all four pipeline
nodes (search → extract → summarize → store).  Keeping it in its own module
avoids circular imports between the graph and tool layers.
"""

from typing import TypedDict


class ResearchState(TypedDict):
    """Shared state passed between every node in the LangGraph pipeline."""

    query: str              # User-supplied research topic
    search_results: list    # Raw results returned by Tavily
    extracted_content: str  # Cleaned, concatenated text ready for the LLM
    summary: str            # Structured summary produced by the LLM
    status: str             # Success / error message from the MCP store step
