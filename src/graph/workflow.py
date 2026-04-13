"""
workflow.py — LangGraph graph assembly for the Research Assistant Agent.

Wires the four tool nodes into a sequential pipeline and compiles it into
a runnable LangGraph object.

Pipeline:
    search_node → extract_node → summarize_node → store_node → END
"""

from langgraph.graph import END, StateGraph

from src.graph.state import ResearchState
from src.tools.search_tools import search_node
from src.tools.text_tools import extract_node, store_node, summarize_node


def build_graph():
    """
    Build and compile the LangGraph research workflow.

    Returns:
        A compiled LangGraph runnable (supports .invoke and .ainvoke).
    """
    graph: StateGraph = StateGraph(ResearchState)

    graph.add_node("search", search_node)
    graph.add_node("extract", extract_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("store", store_node)

    graph.set_entry_point("search")
    graph.add_edge("search", "extract")
    graph.add_edge("extract", "summarize")
    graph.add_edge("summarize", "store")
    graph.add_edge("store", END)

    return graph.compile()
