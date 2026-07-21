# Docker LLM Wiki Setup

Configuring Karpathy's LLM Wiki pattern in a Docker Hermes deployment requires additional volume mounts and environment variables beyond the standard deployment. This reference covers the Docker-specific setup.

## Key Additions to docker-compose.yml

```yaml
services:
  gateway:
    volumes:
      - ~/.hermes:/opt/data
      - ~/wiki:/wiki          # ← wiki directory mount
    environment:
      - WIKI_PATH=/wiki       # ← llm-wiki skill reads this
      - HERMES_MULTIPLEX_PROFILES=true  # if using multi-profile wiki bot

  dashboard:
    volumes:
      - ~/.hermes:/opt/data
      - ~/wiki:/wiki          # ← dashboard also needs access for TUI

  # Optional: MkDocs Material frontend
  wiki-web:
    image: squidfunk/mkdocs-material:latest
    container_name: llm-wiki
    restart: unless-stopped
    volumes:
      - ~/wiki:/docs
    ports:
      - "127.0.0.1:8000:8000"
    command: ["serve", "--dev-addr", "0.0.0.0:8000"]
```

## Env Var: WIKI_PATH

The llm-wiki skill reads `WIKI_PATH` from environment. In Docker:
- Set via `environment:` in docker-compose.yml (preferred — all profiles inherit it)
- Or set per-profile in that profile's `.env` / `config.yaml` via `hermes -p <profile> config set WIKI_PATH /wiki`

Without this variable set, the skill defaults to `~/wiki` inside the container, which resolves to the container's home directory — NOT the bind-mounted host path.

## Directory Structure (host side: `~/wiki/`)

```
~/wiki/
├── SCHEMA.md           # Conventions, structure rules
├── index.md            # Content catalog
├── log.md              # Append-only action log
├── mkdocs.yml          # MkDocs config (optional)
├── raw/                # Immutable source material
│   ├── articles/
│   ├── papers/
│   ├── transcripts/
│   └── assets/
├── entities/           # Entity pages
├── concepts/           # Concept/topic pages
├── comparisons/        # Side-by-side analyses
└── queries/            # Filed query results
```

## Cross-Profile Sharing

All profiles in the same container can share the wiki directory because it's bind-mounted once at the Docker level:

```bash
# Default profile uses wiki
hermes -p default chat    # can read/write /wiki

# wiki-bot profile also uses same /wiki
hermes -p wiki-bot chat   # can read/write same /wiki
```

Just ensure every profile that needs wiki access has `WIKI_PATH=/wiki` in its environment.

## Initialization (Post-Volume-Mount)

After adding the volume and restarting:

```bash
# 1. Create base structure
docker exec hermes mkdir -p /wiki/{raw/{articles,papers,transcripts,assets},entities,concepts,comparisons,queries,_archive}

# 2. Create SCHEMA.md (customize to domain)
docker exec hermes sh -c 'cat > /wiki/SCHEMA.md << EOF
# Wiki Schema
## Domain
[your domain here]

## Conventions
- File names: lowercase-hyphens.md
- Every page has YAML frontmatter
- Use [[wikilinks]] for cross-references
...

## Tag Taxonomy
[define your tags]
EOF'

# 3. Initialize index.md and log.md
docker exec hermes sh -c 'echo "# Wiki Index" > /wiki/index.md'
docker exec hermes sh -c 'echo "# Wiki Log\n\n## [$(date +%Y-%m-%d)] create | Wiki initialized" > /wiki/log.md'

# 4. Verify WIKI_PATH is picked up
docker exec hermes env | grep WIKI_PATH
# Expected: WIKI_PATH=/wiki
```

## Feishu Wiki Bot Profile

Create a separate profile for a dedicated Feishu wiki bot:

```bash
docker exec hermes hermes profile create wiki-bot
docker exec hermes hermes -p wiki-bot gateway setup  # select feishu
```

The profile needs its own Feishu App (App ID / App Secret). With multiplex mode enabled, all profiles share the gateway process:

```bash
docker exec hermes hermes config set gateway.multiplex_profiles true
docker exec hermes hermes gateway restart
```

## Git Sync via Cron (Container)

The wiki can be auto-synced to a remote git repo (e.g., CNB, GitHub) via a cron job inside the container:

```bash
docker exec hermes hermes cron create \
  --schedule "0 3 * * *" \
  --name "wiki-git-sync" \
  --no-agent \
  --script /opt/data/scripts/wiki-sync.sh
```

The `wiki-sync.sh` script runs inside the container and has access to `/wiki`. Example:
```bash
#!/bin/bash
cd /wiki
if [ -z "$(git status --porcelain)" ]; then
  exit 0
fi
git add -A
git commit -m "auto sync $(date +%Y-%m-%d)"
git push origin main 2>&1
```

Note: git credentials need to be configured inside the container for the remote push to work:
```bash
docker exec hermes git config --global user.email "wiki@devtoy.cn"
docker exec hermes git config --global user.name "Wiki Bot"
```

## Pitfalls

- **WIKI_PATH not set** → skill defaults to `~/wiki` inside container, not the mounted volume. Always verify with `docker exec hermes env | grep WIKI_PATH`.
- **Dashboard can't read wiki** → if you access the wiki from the TUI, the dashboard container also needs the same `- ~/wiki:/wiki` volume mount.
- **git inside container** → the container's git needs user.email/user.name configured, and SSH keys or credential helpers for pushing to remotes.
- **Orphan risk** → the `~/wiki` directory on the host persists across container rebuilds, but the git remote config lives in `~/wiki/.git/config` inside the volume — safe as long as the volume isn't a named ephemeral volume.
