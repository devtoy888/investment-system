"""Structured agent config loading utilities."""

from \_\_future\_\_ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Mapping

from pydantic import ValidationError

from src.config.paths import get\_config\_path, get\_runtime\_root
from src.config.schema import AgentConfig, AgentConfigOverride, MCPServerConfig

logger = logging.getLogger(\_\_name\_\_)

\_SWARM\_AGENT\_CONFIG\_ENV\_VAR = "VIBE\_TRADING\_SWARM\_AGENT\_CONFIG"
\_SWARM\_AGENT\_CONFIG\_FILENAME = "swarm-agent.json"
\_MAIN\_AGENT\_FALLBACK\_FILENAMES = ("agent.json", "agent.yaml", "agent.yml")

try:
 import yaml
except ImportError:
 yaml = None # type: ignore

def load\_agent\_config(config\_path: Path \| None = None) -> AgentConfig:
 """Load structured agent config from disk with safe fallback.

 Args:
 config\_path: Optional explicit config path. When omitted, the default
 config discovery path is used.

 Returns:
 The validated agent config. Invalid or unreadable config files fall
 back to \`\`AgentConfig()\`\`.
 """
 path = get\_config\_path(config\_path)

 if not path.exists():
 return AgentConfig()

 try:
 raw = \_read\_config\_file(path)
 return AgentConfig.model\_validate(raw)
 except (OSError, ValueError, ValidationError) as exc:
 logger.warning(
 "Failed to load agent config from %s: %s",
 path,
 type(exc).\_\_name\_\_,
 )
 logger.debug("Agent config load error details: %s", exc)
 return AgentConfig()

def merge\_agent\_config\_overrides(
 config: AgentConfig,
 overrides: Mapping\[str, Any\] \| None,
) -\> AgentConfig:
 """Merge runtime overrides on top of a base config.

 Overrides are validated against a partial schema first so both snake\_case
 and camelCase keys are accepted while only explicitly provided fields
 override the base config.

 Args:
 config: Base agent config loaded from disk or defaults.
 overrides: Runtime overrides, typically from session-level config.

 Returns:
 A new validated config containing the merged result.
 """
 if not overrides:
 return config

 try:
 override\_model = AgentConfigOverride.model\_validate(dict(overrides))
 except ValidationError as exc:
 logger.warning(
 "Ignoring invalid agent config overrides (%s): %s — using base config",
 type(exc).\_\_name\_\_,
 \[str(e\["loc"\]) for e in exc.errors()\],
 )
 return config

 merged = \_merge\_agent\_config\_dicts(
 config.model\_dump(mode="json"),
 override\_model.model\_dump(mode="json", exclude\_unset=True),
 )
 try:
 return AgentConfig.model\_validate(merged)
 except ValidationError as exc:
 logger.warning(
 "Ignoring merged agent config overrides after validation failure (%s): %s — using base config",
 type(exc).\_\_name\_\_,
 \[str(e\["loc"\]) for e in exc.errors()\],
 )
 return config

\# Keys in session overrides that carry subprocess definitions and therefore
\# require operator-level trust rather than API-caller trust.
\_SESSION\_RESTRICTED\_KEYS: frozenset\[str\] = frozenset({"mcpServers", "mcp\_servers"})

def sanitize\_session\_overrides(overrides: Mapping\[str, Any\]) -> dict\[str, Any\]:
 """Strip operator-only keys from API-caller-supplied session overrides.

 \`\`mcpServers\`\` / \`\`mcp\_servers\`\` define subprocess \`\`command\`\`/\`\`args\`\`/\`\`env\`\`
 and therefore grant execution-level capabilities. They must originate from
 the operator-controlled config file on disk, not from unauthenticated or
 semi-trusted API callers. Operators who deliberately want to allow session-
 level MCP injection can set \`\`ALLOW\_SESSION\_MCP\_SERVERS=1\`\`.

 Args:
 overrides: Raw session config dict received from the API caller.

 Returns:
 A new dict with restricted keys removed (or the original mapping
 converted to dict if the env opt-in is active).
 """
 if os.environ.get("ALLOW\_SESSION\_MCP\_SERVERS", "").strip().lower() in {"1", "true", "yes"}:
 return dict(overrides)

 restricted\_present = \_SESSION\_RESTRICTED\_KEYS & overrides.keys()
 if restricted\_present:
 logger.warning(
 "Stripped %s from session config overrides: MCP server definitions "
 "require operator-level trust (disk config). "
 "Set ALLOW\_SESSION\_MCP\_SERVERS=1 to allow session-level injection.",
 sorted(restricted\_present),
 )
 return {k: v for k, v in overrides.items() if k not in \_SESSION\_RESTRICTED\_KEYS}

def load\_runtime\_agent\_config(
 config\_path: Path \| None = None,
 overrides: Mapping\[str, Any\] \| None = None,
) -\> AgentConfig:
 """Load disk config and apply runtime overrides.

 Args:
 config\_path: Optional explicit config file path.
 overrides: Runtime override mapping applied on top of file-based config.

 Returns:
 The merged runtime config.
 """
 config = load\_agent\_config(config\_path)
 return merge\_agent\_config\_overrides(config, overrides)

def \_resolve\_swarm\_agent\_config\_path(
 \*,
 runtime\_root: Path \| None = None,
) -\> Path \| None:
 """Pick the operator config the swarm runtime should boot against.

 Resolution order (first hit wins):

 1\. \`\`VIBE\_TRADING\_SWARM\_AGENT\_CONFIG\`\` env var — absolute override hatch
 for CI / sandbox deployments where the runtime root is read-only.
 Returned even if the file does not yet exist; the caller logs &
 degrades gracefully so a misconfigured env var doesn't crash boot.
 2\. \`\`/swarm-agent.json\`\` — the swarm-specific operator
 allowlist. Lets the swarm path use a \*different\* set of MCP servers
 from the main agent without duplicating non-MCP fields.
 3\. \`\`/{agent.json,agent.yaml,agent.yml}\`\` — fallback to the
 main agent config so single-config operators don't have to duplicate
 their MCP allowlist.
 4\. \`\`None\`\` when nothing matches — preserves byte-for-byte legacy
 behaviour where the swarm runs strictly on local tools.

 Trust model: callers of swarm entry points (e.g. an external MCP client
 invoking \`\`run\_swarm\`\`) cannot influence this path — config resolution is
 a boot-time / operator-trusted action.

 Args:
 runtime\_root: Override the directory the on-disk lookup uses. Defaults
 to \`\`~/.vibe-trading\`\`. Tests pass a \`\`tmp\_path\`\` here to keep
 assertions hermetic.

 Returns:
 The chosen config path, or \`\`None\`\` when no candidate is available.
 """
 env\_value = os.environ.get(\_SWARM\_AGENT\_CONFIG\_ENV\_VAR, "").strip()
 if env\_value:
 return Path(env\_value).expanduser()

 root = runtime\_root if runtime\_root is not None else get\_runtime\_root()
 swarm\_specific = root / \_SWARM\_AGENT\_CONFIG\_FILENAME
 if swarm\_specific.exists():
 return swarm\_specific

 for fallback in \_MAIN\_AGENT\_FALLBACK\_FILENAMES:
 candidate = root / fallback
 if candidate.exists():
 return candidate

 return None

def load\_swarm\_agent\_config(
 \*,
 runtime\_root: Path \| None = None,
) -\> AgentConfig:
 """Load the swarm-side AgentConfig using the M3 boot resolution order.

 This is the helper boot wiring (\`\`mcp\_server.py\`\`, \`\`api\_server.py\`\`, CLI
 swarm runners, in-process \`\`swarm\_tool\`\`) calls before constructing
 \`\`SwarmRuntime\`\`. It returns an :class:\`AgentConfig\` (never \`\`None\`\`) so
 every caller can pass the result through to \`\`SwarmRuntime(agent\_config=...)\`\`
 without conditional unwrapping. An empty config (\`\`mcp\_servers={}\`\`) is
 treated identically to \`\`agent\_config=None\`\` by \`\`build\_swarm\_registry\`\`,
 so the swarm stays strictly local-tool-only when nothing is configured.

 Args:
 runtime\_root: Override the directory the on-disk lookup uses. Defaults
 to \`\`~/.vibe-trading\`\`.

 Returns:
 The validated swarm agent config, or an empty :class:\`AgentConfig\`
 when no candidate is on disk / the chosen file fails to parse.
 """
 path = \_resolve\_swarm\_agent\_config\_path(runtime\_root=runtime\_root)
 if path is None:
 return AgentConfig()
 return load\_agent\_config(path)

def \_read\_config\_file(path: Path) -> dict\[str, Any\]:
 """Read a supported config file format into a dictionary.

 Args:
 path: Config file path to decode.

 Returns:
 The decoded config object as a dictionary.

 Raises:
 ValueError: If the file format is unsupported, YAML support is
 unavailable, or the decoded payload is not an object.
 """
 suffix = path.suffix.lower()
 text = path.read\_text(encoding="utf-8")

 if suffix == ".json":
 data = json.loads(text)
 elif suffix in {".yaml", ".yml"}:
 if yaml is None:
 raise ValueError("YAML config is not available because PyYAML is missing")
 data = yaml.safe\_load(text) or {}
 else:
 raise ValueError(f"Unsupported config file format: {suffix or ''}")

 if not isinstance(data, dict):
 raise ValueError("Agent config must decode to a JSON/YAML object")
 return data

def \_merge\_agent\_config\_dicts(base: dict\[str, Any\], override: dict\[str, Any\]) -> dict\[str, Any\]:
 """Merge top-level agent config payloads with MCP-aware server replacement."""
 non\_mcp\_override = {key: value for key, value in override.items() if key != "mcp\_servers"}
 merged = \_merge\_dicts(base, non\_mcp\_override)

 override\_servers = override.get("mcp\_servers")
 if not isinstance(override\_servers, dict):
 if "mcp\_servers" in override:
 merged\["mcp\_servers"\] = override\_servers
 return merged

 merged\_servers = dict(base.get("mcp\_servers", {}))
 for server\_name, server\_override in override\_servers.items():
 current\_server = merged\_servers.get(server\_name)
 if isinstance(current\_server, dict) and isinstance(server\_override, dict):
 merged\_servers\[server\_name\] = \_merge\_mcp\_server\_dicts(current\_server, server\_override)
 else:
 merged\_servers\[server\_name\] = server\_override

 merged\["mcp\_servers"\] = merged\_servers
 return merged

def \_merge\_mcp\_server\_dicts(base: dict\[str, Any\], override: dict\[str, Any\]) -> dict\[str, Any\]:
 """Merge one MCP server payload, resetting incompatible transport fields when needed."""
 if \_override\_switches\_transport(base, override):
 return \_merge\_dicts(\_default\_mcp\_server\_payload(base), override)
 return \_merge\_dicts(base, override)

def \_override\_switches\_transport(base: dict\[str, Any\], override: dict\[str, Any\]) -> bool:
 """Return whether a partial override changes the server transport family."""
 override\_transport = \_resolve\_override\_transport(override)
 if override\_transport is None:
 return False
 base\_transport = MCPServerConfig.model\_validate(base).resolved\_transport()
 return override\_transport != base\_transport

def \_resolve\_override\_transport(override: dict\[str, Any\]) -> str \| None:
 """Infer transport intent from a partial MCP server override."""
 explicit\_type = override.get("type")
 if explicit\_type in {"stdio", "sse", "streamableHttp"}:
 return str(explicit\_type)
 if any(key in override for key in ("command", "args", "env")):
 return "stdio"
 return None

def \_default\_mcp\_server\_payload(base: dict\[str, Any\]) -> dict\[str, Any\]:
 """Return a transport-neutral MCP server payload preserving non-transport defaults."""
 enabled\_tools = base.get("enabled\_tools")
 return {
 "type": None,
 "command": "",
 "args": \[\],
 "env": {},
 "url": "",
 "headers": {},
 "tool\_timeout": base.get("tool\_timeout", 30.0),
 "init\_timeout": base.get("init\_timeout"),
 "enabled\_tools": list(enabled\_tools) if isinstance(enabled\_tools, list) else \["\*"\],
 }

def \_merge\_dicts(base: dict\[str, Any\], override: dict\[str, Any\]) -> dict\[str, Any\]:
 """Recursively merge two plain dictionaries.

 Args:
 base: Base dictionary.
 override: Override dictionary applied on top of \`\`base\`\`.

 Returns:
 A merged dictionary where nested mappings are merged recursively and
 scalar values from \`\`override\`\` replace those in \`\`base\`\`.
 """
 merged = dict(base)
 for key, value in override.items():
 current = merged.get(key)
 if isinstance(current, dict) and isinstance(value, dict):
 merged\[key\] = \_merge\_dicts(current, value)
 else:
 merged\[key\] = value
 return merged