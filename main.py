"""
main.py — CLI entry point for the Research Assistant Agent.

Usage:
    python main.py "Explain retrieval augmented generation"
"""

import argparse
import asyncio

from src.agents.research_agent import run_research_agent
from src.graph.state import ResearchState
from src.token_tracker import tracker


def main() -> None:
    """Parse CLI arguments and run the research agent."""
    parser = argparse.ArgumentParser(
        description="Research Assistant Agent — LangGraph + DuckDuckGo + OpenAI + MCP"
    )
    parser.add_argument("query", type=str, help='Research topic, e.g. "Explain RAG"')
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("  Research Assistant Agent")
    print(f"  Query: {args.query}")
    print(f"{'='*60}\n")

    final_state: ResearchState = asyncio.run(run_research_agent(args.query))

    # ── Result ────────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  RESULT")
    print(f"{'='*60}")
    print(final_state["summary"])

    # ── Activity log & token summary ──────────────────────────────────────────
    print()
    print(tracker.display_activity_log())
    print()
    if tracker.total_tokens() > 0:
        print(tracker.display_token_summary())
        print()


if __name__ == "__main__":
    main()
