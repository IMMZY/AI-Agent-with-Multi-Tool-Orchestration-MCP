"""
test_agents.py — Integration smoke-tests for run_research_agent.

These tests mock external dependencies (Tavily, Anthropic, MCP) so they can
run offline without real API keys.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from src.graph.state import ResearchState


class TestRunResearchAgent:
    """Smoke-tests for research_agent.run_research_agent."""

    @patch("src.tools.store_tool.stdio_client")
    @patch("src.tools.summarize_tool.anthropic.Anthropic")
    @patch("src.tools.search_tool.TavilyClient")
    def test_pipeline_returns_research_state(
        self, mock_tavily_cls, mock_anthropic_cls, mock_stdio
    ):
        from src.agents.research_agent import run_research_agent

        # ── Tavily mock ──────────────────────────────────────────────────────
        mock_tavily = MagicMock()
        mock_tavily.search.return_value = {
            "results": [{"url": "https://example.com", "title": "T", "content": "C"}]
        }
        mock_tavily_cls.return_value = mock_tavily

        # ── Anthropic mock ───────────────────────────────────────────────────
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="SUMMARY:\nTest\nKEY POINTS:\n- p\nSOURCES:\n- u")]
        mock_anthropic = MagicMock()
        mock_anthropic.messages.create.return_value = mock_message
        mock_anthropic_cls.return_value = mock_anthropic

        # ── MCP / stdio mock ─────────────────────────────────────────────────
        mock_result = MagicMock()
        mock_result.content = [MagicMock(text="Research note saved (id=1): 'test'")]
        mock_session = AsyncMock()
        mock_session.call_tool.return_value = mock_result

        async_ctx = AsyncMock()
        async_ctx.__aenter__.return_value = mock_session
        mock_stdio.return_value.__aenter__.return_value = (AsyncMock(), AsyncMock())
        mock_stdio.return_value.__aexit__.return_value = False

        # Patch ClientSession separately
        with patch("src.tools.store_tool.ClientSession") as mock_session_cls:
            mock_session_cls.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            result: ResearchState = asyncio.run(run_research_agent("test query"))

        assert result["query"] == "test query"
        assert isinstance(result["summary"], str)
        assert len(result["summary"]) > 0
