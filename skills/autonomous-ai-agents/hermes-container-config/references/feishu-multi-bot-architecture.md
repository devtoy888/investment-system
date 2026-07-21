# Feishu Multi-Bot Architecture for Hermes

When you want multiple distinct agent personas (personal assistant, investment advisor, research coder, content creator) all accessible via Feishu, the architecture that maps most cleanly to Hermes is:

```
                   ┌───────────────────────────────┐
                   │  Hermes Multiplex Gateway      │
                   │  (gateway.multiplex_profiles)   │
                   └─────┬──────────┬──────────┬────┘
                         │          │          │
                  Profile:A    Profile:B    Profile:C
                  personal     investor     coder
                         │          │          │
                 Feishu Bot A  Feishu Bot B  Feishu Bot C
                 App ID: cli_1 App ID: cli_2 App ID: cli_3
```

## How It Works

### Option A: Interactive Setup (per-profile `gateway setup`)

1. **Create one Hermes profile per agent persona:**
   ```bash
   hermes profile create personal
   hermes profile create investor
   hermes profile create coder
   ```

2. **Configure each profile with its own Feishu bot credentials:**
   ```bash
   personal gateway setup    # ← scan QR for App A
   investor gateway setup    # ← scan QR for App B
   coder gateway setup       # ← scan QR for App C
   ```
   Each `hermes gateway setup` run registers a different Feishu App ID/Secret in that profile's `.env`.

### Option B: Non-Interactive Setup (preferred for Docker/automated envs)

When you want to avoid interactive wizards or the user prefers to self-manage `.env`:

1. **Create profile by cloning default** (copies ALL existing .env keys, config, skills):
   ```bash
   hermes profile create llm-wiki --clone
   ```

2. **Edit only the Feishu-specific lines** in the new profile's `.env`:
   ```bash
   # $HERMES_HOME/profiles/<name>/.env
   # Change only these two lines:
   FEISHU_APP_ID=cli_xxxxx_new
   FEISHU_APP_SECRET=***
   # All other keys (DEEPSEEK_API_KEY, OPENROUTER_API_KEY, etc.) stay as-is from --clone
   ```

3. **(Optional) Customize per-profile persona** via `SOUL.md`:
   ```bash
   cp /path/to/custom-soul.md $HERMES_HOME/profiles/<name>/SOUL.md
   ```
   Each profile gets its own SOUL.md, loaded automatically. Use this to give the `llm-wiki` profile a "disciplined wiki librarian" persona and the `investor` profile a "financial analyst" persona.

**Why --clone works:** It copies `.env`, `config.yaml`, `SOUL.md`, and skills from the current profile to the new one. The only lines you need to change are the bot credentials for the new profile. All shared API keys carry over automatically.

3. **Enable multiplex mode** so one process manages all three:
   ```bash
   hermes config set gateway.multiplex_profiles true
   hermes gateway restart    # (or s6-svc -r /run/service/gateway-default/)
   ```

4. **Add each bot to its relevant group chats:**
   - Bot A (personal) → 家庭群、朋友群
   - Bot B (investor) → 投资讨论群
   - Bot C (coder) → 技术交流群

## Why This Works

- Each Feishu bot = independent Feishu App → separate App ID/Secret → maps to one Hermes profile
- Each profile has its own config, skills, memory, cron jobs → agents don't leak state
- Multiplex mode: single gateway process, single container, single supervisor unit
- Users @-mention the right bot for the right task (Feishu groups can have multiple bots)

## Key Constraints (from docs)

- **Port-binding platforms** (feishu webhook mode, wecom_callback, webhook, api_server, bluebubbles, sms) must only be on the default profile. Use WebSocket mode for Feishu bots (recommended anyway).
- **Each profile must use its own Feishu App credentials** — duplicate App IDs cause startup failure.
- Restart gateway once after all profiles are configured: `s6-svc -r /run/service/gateway-default/`

## When NOT to Use Multiple Bots

- If all agents should share the same memory/skills and just vary behavior by chat, use a **single bot + single profile** with a chat-routing system prompt
- If you're still prototyping, start with one bot one profile — splitting later is easy
- If your Feishu workspace has strict App approval processes, the overhead of N apps may not be worth it

## Worked Setup for One Profile

Each profile's `.env` must have:

```bash
FEISHU_APP_ID=cli_xxxxx           # Unique per bot
FEISHU_APP_SECRET=your-secret     # Unique per bot
FEISHU_DOMAIN=feishu              # feishu for CN, lark for intl
FEISHU_CONNECTION_MODE=websocket
```

And in its `config.yaml` (typically set automatically by `hermes gateway setup`):
```yaml
gateway:
  platforms:
    feishu:
      enabled: true
plugins:
  enabled:
    - hermes-feishu
platform_toolsets:
  feishu:
    - hermes-feishu
```
