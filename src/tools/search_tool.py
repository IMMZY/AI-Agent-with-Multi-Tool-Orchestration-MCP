"""
search_tool.py — Node 1: Web search via DuckDuckGo (no API key required).

Receives the user query from ResearchState and returns the top web results.
"""

import sys

from ddgs import DDGS # <- DuckDuckGo search (new library name)

from src.config import SEARCH_MAX_RESULTS
from src.graph.state import ResearchState


async def search_node(state: ResearchState) -> ResearchState:
    """
    Search the web using DuckDuckGo for the user query.

    Populates:
        state["search_results"] — list of result dicts (title, url, content).
    """
    print(f"[search_node] Searching for: {state['query']}")
    try:
        with DDGS() as ddgs:
            raw = list(ddgs.text(state["query"], max_results=SEARCH_MAX_RESULTS))

        # Normalise to a consistent shape (url key instead of href)
        results = [
            {
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "content": r.get("body", ""),
            }
            for r in raw
        ]
        print(f"[search_node] Got {len(results)} result(s).")
        return {**state, "search_results": results}
    except Exception as exc:
        print(f"[search_node] ERROR: {exc}", file=sys.stderr)
        return {**state, "search_results": [], "status": f"Search error: {exc}"}
