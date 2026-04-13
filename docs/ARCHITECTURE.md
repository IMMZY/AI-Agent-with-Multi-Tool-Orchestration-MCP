# Architecture

## System Overview

```
User Query
    │
    ▼
┌─────────────────────────────────────────────┐
│              LangGraph Pipeline              │
│                                             │
│  search_node  →  extract_node               │
│  (search_tools.py)  (text_tools.py)         │
│       │                  │                  │
│       ▼                  ▼                  │
│  summarize_node  →  store_node              │
│  (text_tools.py)    (text_tools.py)         │
└─────────────────────────────────────────────┘
                          │
                          │ stdio (MCP)
                          ▼
              ┌──────────────────────┐
              │    mcp_server.py     │
              │  (FastMCP / SQLite)  │
              │  save_research       │
              │  list_research       │
              │  search_research     │
              └──────────────────────┘
                          │
                          ▼
                     research.db
```

## Data Flow

1. **main.py** — receives a query string from the CLI
2. **research_agent.py** — initialises state and invokes the compiled graph
3. **search_node** — calls DuckDuckGo, returns top N results
4. **extract_node** — cleans and joins result text into one string
5. **summarize_node** — sends content to OpenAI, returns structured summary
6. **store_node** — spawns `src/mcp_server.py` as a subprocess and calls `save_research` over stdio
7. **mcp_server.py** — writes the note to SQLite and returns a confirmation

## Package Layout

```
src/
  config.py          — env vars
  mcp_server.py      — MCP tool server
  token_tracker.py   — API cost tracking
  agents/            — high-level agent runners
  graph/             — state + workflow
  tools/             — LangGraph nodes
  evaluation/        — output quality scoring
```
