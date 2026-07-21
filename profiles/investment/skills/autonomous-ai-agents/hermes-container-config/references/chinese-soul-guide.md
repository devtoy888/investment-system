# SOUL.md for Chinese-Language Profiles

When creating a Hermes profile for a Chinese-speaking user, the SOUL.md must explicitly include:

1. **Language directive at the very top** of the file
2. **`display.language: zh`** in the profile's config.yaml
3. Full persona content in Chinese

## Language Directive

Add this as the **first line** of SOUL.md:

```markdown
请始终使用**简体中文**回复。
```

Or more elaborate:

```markdown
## 语言
请始终使用**简体中文**回复。即使对方用英文提问，也用中文回答。
```

## Display Language Config

Set in the profile's config.yaml:

```bash
export PATH="$PATH:/opt/data/.local/bin"
hermes -p <profile-name> config set display.language zh
```

## Template: Chinese SOUL.md for LLM Wiki

See the `wiki-maintainer-soul.md` template for a complete bilingual SOUL.md example.

## Why Both Are Needed

| Layer | Purpose | 
|-------|---------|
| `display.language: zh` | Hermes system-level language setting |
| SOUL.md language directive | Injects the instruction into the system prompt |
| Both together | Ensures Chinese even when the default profile uses English |

Without the SOUL.md directive, the agent may respond in English even when display.language is set to zh, because the default system prompt's language takes precedence.
