# Quickstart

Get the Research Assistant Agent running in under 5 minutes.

## 1. Clone & enter the project

```bash
git clone <your-repo-url>
cd <repo-folder>
```

## 2. Create and activate a virtual environment

```bash
python -m venv ASS2_nlp
ASS2_nlp\Scripts\activate   # Windows
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Set your API key

```bash
cp .env.example .env
# Open .env and set OPENAI_API_KEY=sk-...
```

## 5. Verify the MCP server

```bash
python test_mcp_server.py
```

Expected output:
```
[test_mcp_server] Server OK. Tools available: ['save_research', 'list_research', 'search_research']
[test_mcp_server] All required tools present.
```

## 6. Run the agent

```bash
python main.py "Explain retrieval augmented generation"
```
