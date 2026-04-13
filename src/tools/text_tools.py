"""
text_tools.py — Nodes 2, 3 & 4: Text extraction, LLM summarisation, and MCP storage.

Contains:
    extract_node    — cleans raw search results into plain text
    summarize_node  — sends content to OpenAI and returns a structured summary
    store_node      — persists the research note via the MCP server
"""

import sys
from datetime import datetime, timezone

import openai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.config import LLM_MAX_TOKENS, LLM_MODEL, MCP_SERVER_SCRIPT, OPENAI_API_KEY
from src.graph.state import ResearchState
from src.token_tracker import tracker


# ── Node 2: Extract ───────────────────────────────────────────────────────────

async def extract_node(state: ResearchState) -> ResearchState:
    """
    Clean and consolidate text from the raw search results.

    Populates:
        state["extracted_content"] — a single string ready to send to the LLM.
    """
    print("[extract_node] Extracting content from search results.")
    try:
        parts: list[str] = []
        for result in state["search_results"]:
            url: str = result.get("url", "")
            title: str = result.get("title", "")
            content: str = result.get("content", "").strip()
            if content:
                parts.append(f"Source: {url}\nTitle: {title}\n{content}")

        extracted = "\n\n---\n\n".join(parts)
        print(f"[extract_node] Extracted ~{len(extracted)} characters.")
        tracker.log("extract_node", f"Extracted ~{len(extracted):,} characters from {len(parts)} source(s)")
        return {**state, "extracted_content": extracted}
    except Exception as exc:
        print(f"[extract_node] ERROR: {exc}", file=sys.stderr)
        tracker.log("extract_node", f"Extraction failed: {exc}")
        return {**state, "extracted_content": "", "status": f"Extraction error: {exc}"}


# ── Node 3: Summarise ─────────────────────────────────────────────────────────

async def summarize_node(state: ResearchState) -> ResearchState:
    """
    Send the extracted content to the OpenAI LLM and ask for a structured summary.

    Populates:
        state["summary"] — text with summary, key points, and sources.
    """
    print("[summarize_node] Requesting LLM summary.")
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        prompt = (
            f'You are a research assistant. Summarize the following web search results '
            f'on the topic: "{state["query"]}"\n\n'
            f'{state["extracted_content"]}\n\n'
            "Respond using exactly this format:\n\n"
            "SUMMARY:\n<2-3 paragraph overview>\n\n"
            "KEY POINTS:\n- <point 1>\n- <point 2>\n- <point 3>\n- <point 4>\n- <point 5>\n\n"
            "SOURCES:\n- <url 1>\n- <url 2>\n..."
        )

        response = client.chat.completions.create(
            model=LLM_MODEL,
            max_tokens=LLM_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        summary: str = response.choices[0].message.content

        # Record token usage
        if response.usage:
            tracker.record(
                "summarize_node",
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
            )
            tracker.log(
                "summarize_node",
                f"Summary received — {response.usage.prompt_tokens} prompt / "
                f"{response.usage.completion_tokens} completion tokens",
            )
        else:
            tracker.log("summarize_node", "Summary received")

        print("[summarize_node] Summary received.")
        return {**state, "summary": summary}
    except Exception as exc:
        print(f"[summarize_node] ERROR: {exc}", file=sys.stderr)
        tracker.log("summarize_node", f"Summarisation failed: {exc}")
        return {**state, "summary": "", "status": f"Summarisation error: {exc}"}


# ── Node 4: Store (via MCP) ───────────────────────────────────────────────────

async def store_node(state: ResearchState) -> ResearchState:
    """
    Call the MCP server's save_research tool to persist the research note in SQLite.

    The agent communicates with src/mcp_server.py over stdio (subprocess).
    All database writes are handled exclusively by the MCP server.

    Populates:
        state["status"] — confirmation message returned by the MCP tool.
    """
    print("[store_node] Connecting to MCP server to save research.")
    try:
        sources: list[str] = [
            r.get("url", "") for r in state["search_results"] if r.get("url")
        ]
        timestamp: str = datetime.now(timezone.utc).isoformat()

        server_params = StdioServerParameters(
            command=sys.executable,
            args=[MCP_SERVER_SCRIPT],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "save_research",
                    {
                        "title": state["query"],
                        "summary": state["summary"],
                        "sources": sources,
                        "timestamp": timestamp,
                    },
                )
                status_msg: str = (
                    result.content[0].text
                    if result.content
                    else "Saved successfully (no message returned)."
                )
                print(f"[store_node] {status_msg}")
                tracker.log("store_node", status_msg)
                return {**state, "status": status_msg}
    except Exception as exc:
        print(f"[store_node] ERROR: {exc}", file=sys.stderr)
        tracker.log("store_node", f"Storage failed: {exc}")
        return {**state, "status": f"Storage error: {exc}"}
