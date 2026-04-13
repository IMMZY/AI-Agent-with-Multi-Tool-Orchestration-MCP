"""
test_graph.py — Tests for the LangGraph workflow assembly.

Verifies that build_graph() produces a valid compiled graph without
executing any real API calls.
"""

from src.graph.workflow import build_graph
from src.graph.state import ResearchState


class TestBuildGraph:
    """Tests for workflow.build_graph."""

    def test_returns_compiled_graph(self):
        graph = build_graph()
        # A compiled LangGraph graph exposes .ainvoke
        assert hasattr(graph, "ainvoke"), "Compiled graph must have ainvoke method"

    def test_graph_has_expected_nodes(self):
        graph = build_graph()
        node_names = set(graph.get_graph().nodes.keys())
        for expected in ("search", "extract", "summarize", "store"):
            assert expected in node_names, f"Node '{expected}' missing from graph"
