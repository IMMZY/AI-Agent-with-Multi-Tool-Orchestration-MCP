# Concepts

## LangGraph

LangGraph is a library for building stateful, multi-step AI agent workflows as directed graphs.  Each **node** is a Python function that receives the current state and returns an updated copy.  **Edges** define the execution order.

This project uses a simple linear graph:
```
search → extract → summarize → store
```

## MCP (Model Context Protocol)

MCP is an open standard by Anthropic that defines how AI agents communicate with external tools.  Instead of calling functions directly, the agent sends structured requests to an **MCP server** over stdio.

Benefits:
- The agent and the database are decoupled — swap SQLite for PostgreSQL by changing only `mcp_server.py`
- Any MCP-compatible client can reuse the same server
- Tools are self-describing (the agent discovers them at runtime)

## RAG (Retrieval-Augmented Generation)

This agent is a simple implementation of RAG:
1. **Retrieve** — DuckDuckGo fetches relevant web pages
2. **Augment** — the LLM receives the retrieved text as context
3. **Generate** — the LLM produces a grounded summary with sources

## TypedDict State

LangGraph passes a `TypedDict` between nodes.  Each node receives the full state and returns an updated copy — nodes never mutate state in place.
