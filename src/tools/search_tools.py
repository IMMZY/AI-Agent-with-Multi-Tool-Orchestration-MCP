"""
search_tools.py — Node 1: Web search tools (DuckDuckGo search).

Contains the search_node LangGraph node and any helper search utilities.
"""

import sys

from ddgs import DDGS

from src.config import SEARCH_MAX_RESULTS
from src.graph.state import ResearchState
from src.token_tracker import tracker


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

        results = [
            {
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "content": r.get("body", ""),
            }
            for r in raw
        ]
        print(f"[search_node] Got {len(results)} result(s).")
        tracker.log("search_node", f"Searched for: \"{state['query']}\" — {len(results)} result(s) found")
        return {**state, "search_results": results}
    except Exception as exc:
        print(f"[search_node] ERROR: {exc}", file=sys.stderr)
        tracker.log("search_node", f"Search failed: {exc}")
        return {**state, "search_results": [], "status": f"Search error: {exc}"}
