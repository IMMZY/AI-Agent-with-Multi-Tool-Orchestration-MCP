"""
test_tools.py — Unit tests for the four LangGraph tool nodes.

Each node is tested in isolation by passing a minimal ResearchState.
"""

import asyncio
import pytest

from src.graph.state import ResearchState


# ── Helpers ───────────────────────────────────────────────────────────────────

def _base_state(**kwargs) -> ResearchState:
    """Return a ResearchState with sensible defaults, overridden by kwargs."""
    defaults: ResearchState = {
        "query": "test query",
        "search_results": [],
        "extracted_content": "",
        "summary": "",
        "status": "",
    }
    return {**defaults, **kwargs}


# ── extract_node ──────────────────────────────────────────────────────────────

class TestExtractNode:
    """Tests for extract_tool.extract_node (no external API calls)."""

    def test_builds_extracted_content_from_results(self):
        from src.tools.extract_tool import extract_node

        state = _base_state(
            search_results=[
                {"url": "https://example.com", "title": "Example", "content": "Some content here."},
                {"url": "https://other.com", "title": "Other", "content": "More content."},
            ]
        )
        result = asyncio.run(extract_node(state))
        assert "https://example.com" in result["extracted_content"]
        assert "Some content here." in result["extracted_content"]
        assert "More content." in result["extracted_content"]

    def test_skips_results_with_no_content(self):
        from src.tools.extract_tool import extract_node

        state = _base_state(
            search_results=[
                {"url": "https://empty.com", "title": "Empty", "content": ""},
                {"url": "https://good.com", "title": "Good", "content": "Valid content."},
            ]
        )
        result = asyncio.run(extract_node(state))
        assert "https://empty.com" not in result["extracted_content"]
        assert "Valid content." in result["extracted_content"]

    def test_empty_results_produces_empty_string(self):
        from src.tools.extract_tool import extract_node

        state = _base_state(search_results=[])
        result = asyncio.run(extract_node(state))
        assert result["extracted_content"] == ""
