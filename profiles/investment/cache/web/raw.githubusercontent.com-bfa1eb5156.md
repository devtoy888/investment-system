"""Tool registry: auto-discovery via BaseTool.\_\_subclasses\_\_().

Adding a new tool:
 1\. Create a file in src/tools/ with a class extending BaseTool
 2\. Done. It's automatically discovered and registered.

Tools with missing dependencies can override check\_available() → False
to be silently excluded from the registry.
"""

from \_\_future\_\_ import annotations

import importlib
import logging
import pkgutil
from collections.abc import Mapping
from collections import deque
from pathlib import Path
from typing import TYPE\_CHECKING, Callable

from src.agent.tools import BaseTool, ToolRegistry

if TYPE\_CHECKING:
 from src.config.schema import AgentConfig
 from src.memory.persistent import PersistentMemory

logger = logging.getLogger(\_\_name\_\_)

\_SUBCLASSES\_CACHE: list\[type\[BaseTool\]\] \| None = None
\_SHELL\_TOOL\_NAMES = {"bash", "background\_run"}

def \_discover\_subclasses() -> list\[type\[BaseTool\]\]:
 """Import all modules in this package, then collect BaseTool subclasses.

 Results are cached after the first call.

 Returns:
 List of concrete BaseTool subclasses with a non-empty name.
 """
 global \_SUBCLASSES\_CACHE
 if \_SUBCLASSES\_CACHE is not None:
 return \_SUBCLASSES\_CACHE

 pkg\_dir = str(Path(\_\_file\_\_).parent)
 for \_, module\_name, \_ in pkgutil.iter\_modules(\[pkg\_dir\]):
 if module\_name.startswith("\_"):
 continue
 try:
 importlib.import\_module(f"src.tools.{module\_name}")
 except Exception as exc:
 logger.warning("Skipped src.tools.%s: %s", module\_name, exc)

 classes: list\[type\[BaseTool\]\] = \[\]
 queue = deque(BaseTool.\_\_subclasses\_\_())
 while queue:
 cls = queue.popleft()
 if cls.name:
 classes.append(cls)
 queue.extend(cls.\_\_subclasses\_\_())

 \_SUBCLASSES\_CACHE = classes
 return classes

def build\_registry(
 \*,
 persistent\_memory: "PersistentMemory \| None" = None,
 include\_shell\_tools: bool = False,
 agent\_config: "AgentConfig \| None" = None,
 session\_id: str \| None = None,
 event\_callback: Callable\[\[str, dict\], None\] \| None = None,
 warn\_callback: Callable\[\[str\], None\] \| None = None,
 interactive: bool \| None = None,
 \_mcp\_server\_tool\_name\_segments: Mapping\[str, str\] \| None = None,
) -\> ToolRegistry:
 """Build the tool registry via auto-discovery, optionally enriched with MCP tools.

 Local tools are discovered and registered first. When \`\`agent\_config\`\`
 provides one or more MCP server definitions, remote tools are appended
 after the local tools. Each MCP server is isolated: a failure to connect
 or discover tools for one server emits a warning and skips that server
 without affecting local tools or other MCP servers.

 Args:
 persistent\_memory: Shared PersistentMemory instance. Injected into
 tools that need it (e.g. RememberTool) so all tools share one
 instance instead of each creating their own.
 include\_shell\_tools: Whether to include tools that execute shell
 commands. Local CLI/stdin entry points can enable this; networked
 server entry points should keep it disabled unless explicitly
 opted in.
 agent\_config: Optional structured agent config. When provided and
 non-empty, MCP tools are appended to the registry after local
 tool discovery. Pass \`\`None\`\` (default) to preserve existing
 behavior with no MCP integration.
 session\_id: Optional current session id injected into local tools that
 persist per-session state.
 event\_callback: Optional event callback injected into local tools that
 mutate session-scoped state.
 warn\_callback: Optional callable invoked with operator-facing warning
 messages. When provided, server-name collision warnings are passed
 to this callback in addition to the standard logger so CLI and
 SessionService can surface them to operators.
 interactive: Whether the session is an interactive TTY. Governs whether
 a live-broker channel with no cached OAuth token is registered: a
 non-interactive run (\`\`serve\`\` / swarm) skips an unauthorized live
 channel rather than blocking on a browser that cannot open
 (SPEC Transport §4). \`\`None\`\` (default) auto-detects via
 \`\`sys.stdin.isatty()\`\`.

 Returns:
 ToolRegistry containing all available local tools followed by any
 successfully discovered MCP tools.
 """
 from src.tools.goal\_tool import (
 AddGoalEvidenceTool,
 GetResearchGoalTool,
 StartResearchGoalTool,
 UpdateResearchGoalStatusTool,
 )
 from src.tools.autopilot\_tool import RunResearchAutopilotTool
 from src.tools.remember\_tool import RememberTool
 from src.tools.swarm\_tool import SwarmTool

 goal\_tool\_classes = {
 StartResearchGoalTool,
 GetResearchGoalTool,
 AddGoalEvidenceTool,
 UpdateResearchGoalStatusTool,
 }
 # Tools that need the host session id injected: they create or mutate the
 # session's research goal, and the LLM never knows the session id.
 session\_injected\_classes = goal\_tool\_classes \| {RunResearchAutopilotTool}
 registry = ToolRegistry()
 for cls in \_discover\_subclasses():
 try:
 if cls.name in \_SHELL\_TOOL\_NAMES and not include\_shell\_tools:
 logger.info("Tool %s disabled by shell tool policy", cls.name)
 continue
 if not cls.check\_available():
 logger.info("Tool %s unavailable, skipping", cls.name)
 continue
 if cls is RememberTool and persistent\_memory is not None:
 registry.register(cls(memory=persistent\_memory))
 elif cls in session\_injected\_classes:
 registry.register(cls(default\_session\_id=session\_id, event\_callback=event\_callback))
 elif cls is SwarmTool:
 registry.register(cls(include\_shell\_tools=include\_shell\_tools, event\_callback=event\_callback))
 else:
 registry.register(cls())
 except Exception as exc:
 logger.warning("Failed to register tool %s: %s", cls.name, exc)

 if agent\_config and agent\_config.mcp\_servers:
 from src.tools.mcp import build\_mcp\_tool\_wrappers, resolve\_mcp\_server\_tool\_name\_segments

 if \_mcp\_server\_tool\_name\_segments is None:
 local\_server\_names = resolve\_mcp\_server\_tool\_name\_segments(
 agent\_config.mcp\_servers.keys(),
 warn\_callback=warn\_callback,
 )
 else:
 local\_server\_names = {
 server\_name: \_mcp\_server\_tool\_name\_segments\[server\_name\]
 for server\_name in agent\_config.mcp\_servers
 }

 if interactive is None:
 import sys

 interactive = sys.stdin.isatty()

 for server\_name, server\_config in agent\_config.mcp\_servers.items():
 try:
 # Live brokers (e.g. Robinhood) gate their order-placing tools
 # behind the mandate + kill switch; reads stay plain (read-only).
 # Detection is by config key OR URL host, so a live-broker URL
 # under an aliased key cannot bypass the gate.
 from src.live.registry import (
 is\_live\_broker,
 should\_register\_live\_channel,
 wrap\_live\_broker\_tools,
 )

 server\_url = server\_config.url
 live = is\_live\_broker(server\_name, server\_url)

 # Headless / no-token: skip an unauthorized live channel rather
 # than block on a browser that can't open (SPEC Transport §4).
 if live:
 cache\_dir = (
 server\_config.auth.cache\_dir
 if server\_config.auth is not None
 else None
 )
 if not should\_register\_live\_channel(
 interactive=interactive, url=server\_url, cache\_dir=cache\_dir
 ):
 profile\_hint = (
 "ibkr-live-official-mcp-readonly"
 if server\_name.strip().lower() == "ibkr"
 else f"{server\_name}-live-mcp"
 )
 skip\_msg = (
 f"{server\_name} live connector configured but not authorized — "
 f"run \`vibe-trading connector authorize {profile\_hint}\` "
 f"on a desktop session"
 )
 logger.warning(skip\_msg)
 if warn\_callback is not None:
 warn\_callback(skip\_msg)
 continue
 info\_msg = (
 f"{server\_name} live connector is available through trading\_\* tools; "
 "broker-specific MCP wrappers are hidden from the agent registry"
 )
 logger.info(info\_msg)
 if warn\_callback is not None:
 warn\_callback(info\_msg)
 continue

 wrappers = build\_mcp\_tool\_wrappers(
 server\_name,
 server\_config,
 local\_server\_name=local\_server\_names\[server\_name\],
 )
 if live:
 wrappers = wrap\_live\_broker\_tools(
 server\_name, wrappers, url=server\_url
 )
 for tool in wrappers:
 registry.register(tool)
 logger.info(
 "Registered %d MCP tool(s) from server '%s'",
 len(wrappers),
 server\_name,
 )
 except Exception as exc:
 skip\_msg = f"MCP server '{server\_name}' skipped: {exc}"
 logger.warning("Skipped MCP server '%s': %s", server\_name, exc)
 if warn\_callback is not None:
 warn\_callback(skip\_msg)

 return registry

def build\_filtered\_registry(tool\_names: list\[str\], \*, include\_shell\_tools: bool = False) -> ToolRegistry:
 """Build a ToolRegistry with only specified tools.

 Local-tools-only filtered builder. Swarm workers should call
 :func:\`build\_swarm\_registry\` instead so they can opt into remote MCP
 tools when the operator has configured them. This function is preserved
 for callers that explicitly want the local-only path.

 Args:
 tool\_names: Tool names to include.
 include\_shell\_tools: Whether to include filtered shell execution tools.

 Returns:
 ToolRegistry containing only the requested tools.
 """
 full = build\_registry(include\_shell\_tools=include\_shell\_tools)
 return \_filter\_registry(full, tool\_names, include\_shell\_tools=include\_shell\_tools)

def build\_swarm\_registry(
 tool\_names: list\[str\],
 \*,
 agent\_config: "AgentConfig \| None" = None,
 include\_shell\_tools: bool = False,
) -\> ToolRegistry:
 """Build a per-worker registry that merges local + remote MCP tools.

 Swarm workers receive a strict whitelist (\`\`agent\_spec.tools\`\`). This
 builder honors that whitelist while letting operator-configured MCP
 servers contribute additional tools by name (\`\`mcp\_\_\`\`).
 Tools the whitelist requests but the operator has NOT surfaced — either
 because \`\`agent\_config\`\` is \`\`None\`\`, the named MCP server is absent, or
 the server's \`\`enabled\_tools\`\` allowlist excluded it — are dropped with
 an operator-facing warning instead of failing the worker.

 Trust model: \`\`agent\_config\`\` is resolved at server boot from a static
 file or env var; callers of swarm entry points (e.g. an external MCP
 client driving \`\`mcp\_server.py::run\_swarm\`\`) cannot inject MCP server
 URLs through this path.

 Args:
 tool\_names: Per-agent tool whitelist from the preset.
 agent\_config: Optional resolved agent config. When provided, remote
 MCP wrappers are appended to the candidate pool before filtering.
 Pass \`\`None\`\` to keep the worker strictly local.
 include\_shell\_tools: Whether shell-execution tools are eligible.

 Returns:
 ToolRegistry containing the whitelist intersection of local tools
 and any operator-surfaced MCP tools.
 """
 swarm\_agent\_config, swarm\_local\_server\_names = \_prune\_agent\_config\_for\_swarm\_tools(
 agent\_config,
 tool\_names,
 )
 full = build\_registry(
 agent\_config=swarm\_agent\_config,
 include\_shell\_tools=include\_shell\_tools,
 \_mcp\_server\_tool\_name\_segments=swarm\_local\_server\_names,
 )
 return \_filter\_registry(full, tool\_names, include\_shell\_tools=include\_shell\_tools)

def \_prune\_agent\_config\_for\_swarm\_tools(
 agent\_config: "AgentConfig \| None",
 tool\_names: list\[str\],
) -\> tuple\["AgentConfig \| None", dict\[str, str\] \| None\]:
 """Keep only MCP servers whose local tool prefix appears in \`\`tool\_names\`\`."""
 if not agent\_config or not agent\_config.mcp\_servers:
 return agent\_config, None

 requested\_mcp\_tool\_names = \[name for name in tool\_names if name.startswith("mcp\_")\]
 if not requested\_mcp\_tool\_names:
 return None, None

 from src.config.schema import AgentConfig
 from src.tools.mcp import resolve\_mcp\_server\_tool\_name\_segments

 local\_server\_names = resolve\_mcp\_server\_tool\_name\_segments(agent\_config.mcp\_servers.keys())
 selected\_servers = {
 server\_name: server\_config
 for server\_name, server\_config in agent\_config.mcp\_servers.items()
 if any(
 tool\_name.startswith(f"mcp\_{local\_server\_names\[server\_name\]}\_")
 for tool\_name in requested\_mcp\_tool\_names
 )
 }
 selected\_local\_server\_names = {
 server\_name: local\_server\_names\[server\_name\]
 for server\_name in selected\_servers
 }
 return AgentConfig(mcp\_servers=selected\_servers), selected\_local\_server\_names

def \_filter\_registry(
 full: ToolRegistry,
 tool\_names: list\[str\],
 \*,
 include\_shell\_tools: bool,
) -\> ToolRegistry:
 """Project a full registry down to a whitelist with consistent drop logging."""
 filtered = ToolRegistry()
 for name in tool\_names:
 tool = full.get(name)
 if tool:
 filtered.register(tool)
 else:
 logger.warning(
 "Requested tool %r is unavailable and was dropped from the "
 "filtered registry (include\_shell\_tools=%s); a preset that "
 "depends on it cannot execute it.",
 name, include\_shell\_tools,
 )
 return filtered

\_\_all\_\_ = \["build\_registry", "build\_filtered\_registry", "build\_swarm\_registry"\]