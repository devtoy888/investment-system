# Agent Reach — Exa Search via mcporter

## Prerequisites
- Node.js installed (available on our Oracle ARM server)
- npm available
- Exa API key from https://dashboard.exa.ai

## Installation
```bash
# Install mcporter (npm global needs --prefix since no root):
npm install -g mcporter --prefix "$HOME/.local"

# Register Exa as MCP server:
mcporter config add exa https://mcp.exa.ai/mcp
```

## Usage
```bash
# Web search — use keyword positional args (NOT JSON):
mcporter call exa.web_search_exa query: "Hermes Agent AI" numResults: 3

# Content fetch
mcporter call exa.web_fetch_exa urls: ["https://example.com"]
```

## Troubleshooting
- **JSON format fails** — mcporter expects `toolName key: "value"` positional syntax, not JSON objects
- **Timeout** — Exa can be slow, use `--timeout 60` flag
- **401 error** — verify Exa API key is configured in mcporter config