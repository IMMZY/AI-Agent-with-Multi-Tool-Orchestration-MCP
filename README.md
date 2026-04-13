|                           |                                                                                                           |
| ------------------------- | --------------------------------------------------------------------------------------------------------- |
| **Course**                | Natural Language Processing — Graduate Certificate in AI, Cambrian College                                |
| **Name**                  | Ime-Jnr Ime-Essien                                                                                        |
| **Assignment**            | AI Agent with Multi-Tool Orchestration & MCP (Option A)                                                   |
| **Weight**                | 10 Marks                                                                                                  |
| **Due Date**              | Check the Moodle Submission Folder                                                                        |
| **Submission**            | GitHub Repository + `.zip` via Moodle                                                                     |
| **Topics Covered**        | LangGraph, MCP (Model Context Protocol), Tool Integration, LLM APIs (`openai`), SQLite, DuckDuckGo Search |
| **Repository (repo_url)** | https://github.com/IMMZY/AI-Agent-with-Multi-Tool-Orchestration-MCP.git                                   |

---

# Research Assistant Agent

The Research Assistant Agent is an AI-powered pipeline built with **LangGraph** that automates the process of researching any topic. Given a user query, the agent searches the web using DuckDuckGo, extracts and cleans the most relevant content from the results, sends it to an OpenAI LLM to generate a structured summary with key points and source URLs, and finally persists the research note into a local SQLite database — all through a standardised **MCP (Model Context Protocol)** server that acts as the API layer between the agent and the database.

---

## Tool Choices

The assignment suggests Tavily Search API and Anthropic as the LLM provider. This implementation uses the following alternatives — both produce identical results:

| Suggested          | Used                       | Reason                                                               |
| ------------------ | -------------------------- | -------------------------------------------------------------------- |
| Tavily Search API  | **DuckDuckGo** (`ddgs`)    | Free, no API key or sign-up required, no rate limit on the free tier |
| Anthropic (Claude) | **OpenAI** (`gpt-4o-mini`) | Student already had an OpenAI API key                                |

All other components (LangGraph, MCP, SQLite) are used exactly as specified in the assignment.

---

## Architecture

```
User Query
    │
    ▼
┌──────────────┐     DuckDuckGo (free, no key)
│ search_node  │ ──────────────────────► Top 5 web results
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ extract_node │  Clean & consolidate text from results
└──────┬───────┘
       │
       ▼
┌───────────────┐    OpenAI (gpt-4o-mini)
│summarize_node │ ──────────────────────► Structured summary + key points
└──────┬────────┘
       │
       ▼
┌────────────┐    stdio (MCP)    ┌──────────────────┐
│ store_node │ ────────────────► │  mcp_server.py   │ ──► SQLite DB
└────────────┘                   │  (FastMCP)        │
                                 │  save_research    │
                                 │  list_research    │
                                 │  search_research  │
                                 └──────────────────┘
```

LangGraph orchestrates the four nodes in sequence. The agent **never touches the database directly** — it always goes through the MCP server, which acts as a standardised API layer.

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <repo-folder>
```

### 2. Create and activate a virtual environment

```bash
python -m venv <your_virtual_environment_name>
# Windows
ASS2_nlp\Scripts\activate
# macOS / Linux
source <your_virtual_environment_name>/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API keys

```bash
cp .env.example .env
```

Open `.env` and fill in:

| Variable         | Description                          |
| ---------------- | ------------------------------------ |
| `OPENAI_API_KEY` | OpenAI API key (platform.openai.com) |

The remaining variables have sensible defaults and are optional.

### 5. Verify the MCP server

```bash
python test_mcp_server.py
```

### 6. Run the agent

```bash
python main.py "Explain retrieval augmented generation"
```

---

## Usage

```bash
python main.py "<research topic>"
```

**Example:**

```
python main.py "What is the transformer architecture in deep learning?"
```

**Expected output:**

```
============================================================
  Research Assistant Agent
  Query: What is the transformer architecture in deep learning?
============================================================

[search_node] Searching for: What is the transformer architecture in deep learning?
[search_node] Got 5 result(s).
[extract_node] Extracting content from search results.
[extract_node] Extracted ~4821 characters.
[summarize_node] Requesting LLM summary.
[summarize_node] Summary received.
[store_node] Connecting to MCP server to save research.
[store_node] Research note saved (id=1): 'What is the transformer architecture in deep learning?'

============================================================
  RESULT
============================================================
SUMMARY:
The Transformer architecture, introduced in the 2017 paper "Attention Is All You Need"...

KEY POINTS:
- Uses self-attention mechanisms instead of recurrent layers
- Enables parallelisation during training
...

SOURCES:
- https://arxiv.org/abs/1706.03762
...

Status: Research note saved (id=1): '...'
============================================================
```

---

## MCP Server

`src/mcp_server.py` exposes three tools over a stdio-based MCP interface:

| Tool              | Arguments                                         | Description                                      |
| ----------------- | ------------------------------------------------- | ------------------------------------------------ |
| `save_research`   | `title`, `summary`, `sources` (list), `timestamp` | Insert a new research note into SQLite           |
| `list_research`   | —                                                 | Return all saved entries (id, title, timestamp)  |
| `search_research` | `keyword`                                         | Search past notes by keyword in title or summary |

The server is launched automatically as a subprocess by the agent's `store_node`. You can also call its tools manually via any MCP-compatible client.

---

## Project Structure

```
main.py                    # CLI entry point
test_mcp_server.py         # Verify MCP server before connecting clients
requirements.txt           # Python dependencies
.env.example               # Template for environment variables
pytest.ini                 # Test configuration

src/
  config.py                # Settings loaded from .env
  mcp_server.py            # MCP server exposing SQLite as tools
  token_tracker.py         # Per-step token usage tracking
  agents/
    research_agent.py      # run_research_agent() entry point
  tools/
    search_tools.py        # search_node — DuckDuckGo web search
    text_tools.py          # extract_node, summarize_node, store_node
  graph/
    state.py               # ResearchState TypedDict
    workflow.py            # build_graph() — LangGraph assembly
  evaluation/
    evaluator.py           # Heuristic output quality scoring

tests/
  test_agents.py
  test_tools.py
  test_graph.py
  test_evaluation.py

docs/
  QUICKSTART.md
  ARCHITECTURE.md
  CONCEPTS.md
  EVALUATION.md
  MCP_INTEGRATION.md
```

---

## Team Contributions

| Member             | Contribution                                                        |
| ------------------ | ------------------------------------------------------------------- |
| Ime-Jnr Ime-Essien | Full implementation: LangGraph pipeline, MCP server, config, README |

---
