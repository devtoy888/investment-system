# Hermes WebUI Deployment (Docker + Cloudflare Tunnel)

## Context

A user with an existing Heremes Docker deployment (3 profiles: default, investment, llm-wiki) wanted to add hermes-webui as a browser-based chat frontend alongside their existing gateway. They use Cloudflare Tunnel for public access.

## Architecture

```
hermes-network (bridge)
├── hermes-main:9119     ← Dashboard (Basic Auth)
├── hermes-main:8642     ← API Server (for webui connection)
├── hermes-webui:8787    ← New: WebUI frontend
├── llm-wiki:8456        ← MkDocs
└── cloudflared          ← Tunnel proxy for all above
```

## Key Decisions

### Why Multi-Container Mode (not Single-Container)

The user already has a running hermes-main gateway with 3 profiles. The WebUI should connect to the **existing gateway** via API, not run its own agent process. This avoids:
- Two agents sharing the same `~/.hermes` data directory → session conflicts
- Duplicate cron job triggers
- Race conditions on `state.db`

### Why API Server (not internal agent)

The WebUI uses `HERMES_API_URL=http://hermes-main:8642` to connect to the gateway's API Server. This requires enabling `API_SERVER_ENABLED=true` on the gateway — a v0.18 feature, NOT deprecated (the user confused it with Dashboard's `--insecure` which WAS deprecated).

## Configuration

### Gateway Service Changes

```yaml
services:
  hermes-main:
    # ... existing config
    ports:
      - "8642:8642"                        # ADD: expose API port
    environment:
      - API_SERVER_ENABLED=true            # ADD: enable the API server
      - API_SERVER_HOST=0.0.0.0            # ADD: allow webui container to reach it
      - API_SERVER_KEY=${API_SERVER_KEY}   # ADD: auth token (set in .env)
```

### New WebUI Service

```yaml
services:
  hermes-webui:
    image: ghcr.io/nesquena/hermes-webui:latest
    container_name: hermes-webui
    restart: unless-stopped
    ports:
      - "8787:8787"
    volumes:
      - ~/.hermes-main:/home/hermeswebui/.hermes
    environment:
      - HERMES_WEBUI_HOST=0.0.0.0
      - HERMES_WEBUI_PORT=8787
      - HERMES_WEBUI_PASSWORD=${HERMES_WEBUI_PASSWORD}
      - HERMES_API_URL=http://hermes-main:8642    # connect to existing gateway
      - WANTED_UID=${HERMES_UID:-10000}
      - WANTED_GID=${HERMES_GID:-10000}
    depends_on:
      - hermes-main
    networks:
      - hermes-network
```

### .env Additions

```
API_SERVER_KEY=your-random-secret
HERMES_WEBUI_PASSWORD=another-secret
```

### Cloudflare Tunnel

No container config changes needed. In Cloudflare Dashboard, add a new public hostname:

| Domain | Target |
|--------|--------|
| `chat.yourdomain.com` | `http://hermes-webui:8787` |

The existing cloudflared container on the same bridge network resolves `hermes-webui` via Docker DNS.

## Verification

```bash
# 1. API Server running?
curl -s -H "Authorization: Bearer $API_SERVER_KEY" \
  http://localhost:8642/v1/models | python3 -m json.tool

# 2. WebUI healthy?
curl -s http://localhost:8787/health
```

## Pitfalls

- **API Server is NOT deprecated** — do not confuse with Dashboard's `--insecure` (which WAS deprecated in v0.18). The API Server is fully documented and supported: https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server
- **Must set `API_SERVER_HOST=0.0.0.0`** — default is `127.0.0.1` which other containers on a bridge network cannot reach
- **Must set `HERMES_WEBUI_PASSWORD`** when behind Cloudflare Tunnel — the tunnel makes the site publicly accessible
- **Single-container mode** (WebUI runs its own agent) is only for standalone deployments. Never use it alongside an existing gateway sharing the same data directory.
