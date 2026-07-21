"""
QQ Bot platform adapter using the Official QQ Bot API (v2).

Connects to the QQ Bot WebSocket Gateway for inbound events and uses the
REST API (\`\`api.sgroup.qq.com\`\`) for outbound messages and media uploads.

Configuration in config.yaml:
 platforms:
 qq:
 enabled: true
 extra:
 app\_id: "your-app-id" # or QQ\_APP\_ID env var
 client\_secret: "your-secret" # or QQ\_CLIENT\_SECRET env var
 markdown\_support: true # enable QQ markdown (msg\_type 2)
 dm\_policy: "pairing" # open \| allowlist \| disabled \| pairing
 allow\_from: \["openid\_1"\]
 group\_policy: "pairing" # open \| allowlist \| disabled \| pairing
 group\_allow\_from: \["group\_openid\_1"\]
 stt: # Voice-to-text config (optional)
 provider: "zai" # zai (GLM-ASR), openai (Whisper), etc.
 baseUrl: "https://open.bigmodel.cn/api/coding/paas/v4"
 apiKey: "your-stt-api-key" # or set QQ\_STT\_API\_KEY env var
 model: "glm-asr" # glm-asr, whisper-1, etc.

 Voice transcription priority:
 1\. QQ's built-in \`\`asr\_refer\_text\`\` (Tencent ASR — free, always tried first)
 2\. Configured STT provider via \`\`stt\`\` config or \`\`QQ\_STT\_\*\`\` env vars

Reference: https://bot.q.qq.com/wiki/develop/api-v2/
"""

from \_\_future\_\_ import annotations

import asyncio
import base64
import json
import logging
import mimetypes
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlparse

try:
 import aiohttp

 AIOHTTP\_AVAILABLE = True
except ImportError:
 AIOHTTP\_AVAILABLE = False
 aiohttp = None # type: ignore\[assignment\]

try:
 import httpx

 HTTPX\_AVAILABLE = True
except ImportError:
 HTTPX\_AVAILABLE = False
 httpx = None # type: ignore\[assignment\]

from gateway.config import Platform, PlatformConfig
from gateway.platforms.base import (
 BasePlatformAdapter,
 MessageEvent,
 MessageType,
 SendResult,
 \_ssrf\_redirect\_guard,
 cache\_document\_from\_bytes,
 cache\_image\_from\_bytes,
)
from gateway.platforms.helpers import strip\_markdown

logger = logging.getLogger(\_\_name\_\_)

class QQCloseError(Exception):
 """Raised when QQ WebSocket closes with a specific code.

 Carries the close code and reason for proper handling in the reconnect loop.
 """

 def \_\_init\_\_(self, code, reason=""):
 self.code = int(code) if code else None
 self.reason = str(reason) if reason else ""
 super().\_\_init\_\_(f"WebSocket closed (code={self.code}, reason={self.reason})")

\# ---------------------------------------------------------------------------
\# Constants — imported from the shared constants module.
\# ---------------------------------------------------------------------------

from gateway.platforms.qqbot.constants import (
 API\_BASE,
 TOKEN\_URL,
 GATEWAY\_URL\_PATH,
 DEFAULT\_API\_TIMEOUT,
 FILE\_UPLOAD\_TIMEOUT,
 CONNECT\_TIMEOUT\_SECONDS,
 RECONNECT\_BACKOFF,
 MAX\_RECONNECT\_ATTEMPTS,
 RATE\_LIMIT\_DELAY,
 QUICK\_DISCONNECT\_THRESHOLD,
 MAX\_QUICK\_DISCONNECT\_COUNT,
 MAX\_MESSAGE\_LENGTH,
 DEDUP\_WINDOW\_SECONDS,
 DEDUP\_MAX\_SIZE,
 MSG\_TYPE\_TEXT,
 MSG\_TYPE\_MARKDOWN,
 MSG\_TYPE\_MEDIA,
 MSG\_TYPE\_INPUT\_NOTIFY,
 MEDIA\_TYPE\_IMAGE,
 MEDIA\_TYPE\_VIDEO,
 MEDIA\_TYPE\_VOICE,
 MEDIA\_TYPE\_FILE,
)
from gateway.platforms.qqbot.utils import (
 coerce\_list as \_coerce\_list\_impl,
 build\_user\_agent,
)
from gateway.platforms.qqbot.chunked\_upload import (
 ChunkedUploader,
 UploadDailyLimitExceededError,
 UploadFileTooLargeError,
)
from gateway.platforms.qqbot.keyboards import (
 ApprovalRequest,
 InlineKeyboard,
 InteractionEvent,
 build\_approval\_keyboard,
 build\_update\_prompt\_keyboard,
 parse\_approval\_button\_data,
 parse\_interaction\_event,
 parse\_update\_prompt\_button\_data,
)

def check\_qq\_requirements() -> bool:
 """Check if QQ runtime dependencies are available."""
 return AIOHTTP\_AVAILABLE and HTTPX\_AVAILABLE

def \_coerce\_list(value: Any) -> List\[str\]:
 """Coerce config values into a trimmed string list."""
 return \_coerce\_list\_impl(value)

\# ---------------------------------------------------------------------------
\# QQAdapter
\# ---------------------------------------------------------------------------

class QQAdapter(BasePlatformAdapter):
 """QQ Bot adapter backed by the official QQ Bot WebSocket Gateway + REST API."""

 # QQ Bot API does not support editing sent messages.
 SUPPORTS\_MESSAGE\_EDITING = False
 MAX\_MESSAGE\_LENGTH = MAX\_MESSAGE\_LENGTH
 \_TYPING\_INPUT\_SECONDS = 60 # input\_notify duration reported to QQ
 \_TYPING\_DEBOUNCE\_SECONDS = 50 # refresh before it expires

 @property
 def \_log\_tag(self) -> str:
 """Log prefix including app\_id for multi-instance disambiguation."""
 app\_id = getattr(self, "\_app\_id", None)
 if app\_id:
 return f"QQBot:{app\_id}"
 return "QQBot"

 def \_fail\_pending(self, reason: str) -> None:
 """Fail all pending response futures."""
 for fut in self.\_pending\_responses.values():
 if not fut.done():
 fut.set\_exception(RuntimeError(reason))
 self.\_pending\_responses.clear()

 def \_mark\_transport\_disconnected(self) -> None:
 """Mark QQ WS down without stopping the reconnect loop.

 BasePlatformAdapter uses \_running for both process lifecycle and
 connection status. QQBot needs to keep the listener task alive across
 transient transport drops so it can continue reconnect attempts after a
 short-lived gateway or network failure.
 """
 if self.has\_fatal\_error:
 return
 self.\_write\_runtime\_status\_safe(
 "disconnected",
 platform\_state="disconnected",
 error\_code=None,
 error\_message=None,
 )

 @property
 def is\_connected(self) -> bool:
 """Return True only when the QQ WebSocket transport is usable."""
 return bool(self.\_running and self.\_ws and not self.\_ws.closed)

 def \_\_init\_\_(self, config: PlatformConfig):
 super().\_\_init\_\_(config, Platform.QQBOT)

 extra = config.extra or {}
 self.\_app\_id = str(extra.get("app\_id") or os.getenv("QQ\_APP\_ID", "")).strip()
 self.\_client\_secret = str(
 extra.get("client\_secret") or os.getenv("QQ\_CLIENT\_SECRET", "")
 ).strip()
 self.\_markdown\_support = bool(extra.get("markdown\_support", True))

 # Auth/ACL policies
 self.\_dm\_policy = str(extra.get("dm\_policy", "pairing")).strip().lower()
 self.\_allow\_from = \_coerce\_list(
 extra.get("allow\_from") or extra.get("allowFrom")
 )
 self.\_group\_policy = str(extra.get("group\_policy", "pairing")).strip().lower()
 self.\_group\_allow\_from = \_coerce\_list(
 extra.get("group\_allow\_from") or extra.get("groupAllowFrom")
 )

 # Connection state
 self.\_session: Optional\[aiohttp.ClientSession\] = None
 self.\_ws: Optional\[aiohttp.ClientWebSocketResponse\] = None
 self.\_http\_client: Optional\[httpx.AsyncClient\] = None
 self.\_listen\_task: Optional\[asyncio.Task\] = None
 self.\_heartbeat\_task: Optional\[asyncio.Task\] = None
 self.\_heartbeat\_interval: float = 30.0 # seconds, updated by Hello
 self.\_session\_id: Optional\[str\] = None
 self.\_last\_seq: Optional\[int\] = None
 self.\_chat\_type\_map: Dict\[str, str\] = {} # chat\_id → "c2c"\|"group"\|"guild"\|"dm"

 # Request/response correlation
 self.\_pending\_responses: Dict\[str, asyncio.Future\] = {}
 self.\_seen\_messages: Dict\[str, float\] = {}

 # Last inbound message ID per chat — used by send\_typing
 self.\_last\_msg\_id: Dict\[str, str\] = {}
 # Typing debounce: chat\_id → last send\_typing timestamp
 self.\_typing\_sent\_at: Dict\[str, float\] = {}

 # Token cache
 self.\_access\_token: Optional\[str\] = None
 self.\_token\_expires\_at: float = 0.0
 self.\_token\_lock = asyncio.Lock()

 # Upload cache: content\_hash -> {file\_info, file\_uuid, expires\_at}
 self.\_upload\_cache: Dict\[str, Dict\[str, Any\]\] = {}

 # Inline-keyboard interaction routing. The callback (if set) is invoked
 # for every INTERACTION\_CREATE event after the adapter has already
 # ACKed it. Callers (gateway wiring for approvals / update prompts)
 # register via set\_interaction\_callback().
 self.\_interaction\_callback: Optional\[\
 Callable\[\[InteractionEvent\], Awaitable\[None\]\]\
 \] = None

 # Default interaction dispatcher: routes approval-button clicks to
 # tools.approval.resolve\_gateway\_approval() and update-prompt clicks
 # to ~/.hermes/.update\_response. Set here so the cross-adapter gateway
 # contract (send\_exec\_approval / send\_update\_prompt) works out of the
 # box; callers can override with set\_interaction\_callback(None) or
 # register a custom handler.
 self.\_interaction\_callback = self.\_default\_interaction\_dispatch

 # ------------------------------------------------------------------
 # Properties
 # ------------------------------------------------------------------

 @property
 def name(self) -> str:
 return "QQBot"

 @property
 def enforces\_own\_access\_policy(self) -> bool:
 """QQBot gates DM/group access at intake via dm\_policy/group\_policy."""
 return True

 # ------------------------------------------------------------------
 # Connection lifecycle
 # ------------------------------------------------------------------

 async def connect(self, \*, is\_reconnect: bool = False) -> bool:
 """
 Authenticate, obtain gateway URL, and open the WebSocket.

 Args:
 is\_reconnect: False on a cold first boot; True when the
 reconnect watcher is re-establishing this platform after
 an outage. QQBot has no server-side update queue so this
 flag is accepted for interface conformance only.
 """
 if not AIOHTTP\_AVAILABLE:
 message = "QQ startup failed: aiohttp not installed"
 self.\_set\_fatal\_error("qq\_missing\_dependency", message, retryable=True)
 logger.warning("\[%s\] %s. Run: pip install aiohttp", self.\_log\_tag, message)
 return False
 if not HTTPX\_AVAILABLE:
 message = "QQ startup failed: httpx not installed"
 self.\_set\_fatal\_error("qq\_missing\_dependency", message, retryable=True)
 logger.warning("\[%s\] %s. Run: pip install httpx", self.\_log\_tag, message)
 return False
 if not self.\_app\_id or not self.\_client\_secret:
 message = "QQ startup failed: QQ\_APP\_ID and QQ\_CLIENT\_SECRET are required"
 self.\_set\_fatal\_error("qq\_missing\_credentials", message, retryable=True)
 logger.warning("\[%s\] %s", self.\_log\_tag, message)
 return False

 # Prevent duplicate connections with the same credentials
 if not self.\_acquire\_platform\_lock("qqbot-appid", self.\_app\_id, "QQBot app ID"):
 return False

 try:
 # Tighter keepalive pool so idle CLOSE\_WAIT sockets drain
 # faster behind proxies like Cloudflare Warp (#18451).
 from gateway.platforms.\_http\_client\_limits import platform\_httpx\_limits
 self.\_http\_client = httpx.AsyncClient(
 timeout=30.0,
 follow\_redirects=True,
 event\_hooks={"response": \[\_ssrf\_redirect\_guard\]},
 limits=platform\_httpx\_limits(),
 )

 # 1\. Get access token
 await self.\_ensure\_token()

 # 2\. Get WebSocket gateway URL
 gateway\_url = await self.\_get\_gateway\_url()
 logger.info("\[%s\] Gateway URL: %s", self.\_log\_tag, gateway\_url)

 # 3\. Open WebSocket
 await self.\_open\_ws(gateway\_url)

 # 4\. Start listeners
 self.\_listen\_task = asyncio.create\_task(self.\_listen\_loop())
 self.\_heartbeat\_task = asyncio.create\_task(self.\_heartbeat\_loop())
 self.\_mark\_connected()
 logger.info("\[%s\] Connected", self.\_log\_tag)
 return True
 except Exception as exc:
 message = f"QQ startup failed: {exc}"
 self.\_set\_fatal\_error("qq\_connect\_error", message, retryable=True)
 logger.error("\[%s\] %s", self.\_log\_tag, message, exc\_info=True)
 await self.\_cleanup()
 self.\_release\_platform\_lock()
 return False

 async def disconnect(self) -> None:
 """Close all connections and stop listeners."""
 self.\_running = False
 self.\_mark\_disconnected()

 if self.\_listen\_task:
 self.\_listen\_task.cancel()
 try:
 await self.\_listen\_task
 except asyncio.CancelledError:
 pass
 self.\_listen\_task = None

 if self.\_heartbeat\_task:
 self.\_heartbeat\_task.cancel()
 try:
 await self.\_heartbeat\_task
 except asyncio.CancelledError:
 pass
 self.\_heartbeat\_task = None

 await self.\_cleanup()
 self.\_release\_platform\_lock()
 logger.info("\[%s\] Disconnected", self.\_log\_tag)

 async def \_cleanup(self) -> None:
 """Close WebSocket, HTTP session, and client."""
 if self.\_ws and not self.\_ws.closed:
 await self.\_ws.close()
 self.\_ws = None

 if self.\_session and not self.\_session.closed:
 await self.\_session.close()
 self.\_session = None

 if self.\_http\_client:
 await self.\_http\_client.aclose()
 self.\_http\_client = None

 # Fail pending
 for fut in self.\_pending\_responses.values():
 if not fut.done():
 fut.set\_exception(RuntimeError("Disconnected"))
 self.\_pending\_responses.clear()

 # ------------------------------------------------------------------
 # Token management
 # ------------------------------------------------------------------

 async def \_ensure\_token(self) -> str:
 """Return a valid access token, refreshing if needed (with singleflight)."""
 if self.\_access\_token and time.time() < self.\_token\_expires\_at - 60:
 return self.\_access\_token

 async with self.\_token\_lock:
 # Double-check after acquiring lock
 if self.\_access\_token and time.time() < self.\_token\_expires\_at - 60:
 return self.\_access\_token

 try:
 resp = await self.\_http\_client.post(
 TOKEN\_URL,
 json={"appId": self.\_app\_id, "clientSecret": self.\_client\_secret},
 timeout=DEFAULT\_API\_TIMEOUT,
 )
 resp.raise\_for\_status()
 data = resp.json()
 except Exception as exc:
 raise RuntimeError(f"Failed to get QQ Bot access token: {exc}") from exc

 token = data.get("access\_token")
 if not token:
 raise RuntimeError(
 f"QQ Bot token response missing access\_token: {data}"
 )

 expires\_in = int(data.get("expires\_in", 7200))
 self.\_access\_token = token
 self.\_token\_expires\_at = time.time() + expires\_in
 logger.info(
 "\[%s\] Access token refreshed, expires in %ds", self.\_log\_tag, expires\_in
 )
 return self.\_access\_token

 async def \_get\_gateway\_url(self) -> str:
 """Fetch the WebSocket gateway URL from the REST API."""
 token = await self.\_ensure\_token()
 try:
 resp = await self.\_http\_client.get(
 f"{API\_BASE}{GATEWAY\_URL\_PATH}",
 headers={
 "Authorization": f"QQBot {token}",
 "User-Agent": build\_user\_agent(),
 },
 timeout=DEFAULT\_API\_TIMEOUT,
 )
 resp.raise\_for\_status()
 data = resp.json()
 except Exception as exc:
 raise RuntimeError(f"Failed to get QQ Bot gateway URL: {exc}") from exc

 url = data.get("url")
 if not url:
 raise RuntimeError(f"QQ Bot gateway response missing url: {data}")
 return url

 # ------------------------------------------------------------------
 # WebSocket lifecycle
 # ------------------------------------------------------------------

 async def \_open\_ws(self, gateway\_url: str) -> None:
 """Open a WebSocket connection to the QQ Bot gateway."""
 # Only clean up WebSocket resources — keep \_http\_client alive for REST API calls.
 if self.\_ws and not self.\_ws.closed:
 await self.\_ws.close()
 self.\_ws = None
 if self.\_session and not self.\_session.closed:
 await self.\_session.close()
 self.\_session = None

 # Honor WSL proxy env for QQ WebSocket. Hermes upgrades overwrite this
 # local patch, so QQ can regress to direct-connect timeouts after update.
 self.\_session = aiohttp.ClientSession(trust\_env=True)
 ws\_proxy = (
 os.getenv("WSS\_PROXY")
 or os.getenv("wss\_proxy")
 or os.getenv("HTTPS\_PROXY")
 or os.getenv("https\_proxy")
 or os.getenv("ALL\_PROXY")
 or os.getenv("all\_proxy")
 )
 self.\_ws = await self.\_session.ws\_connect(
 gateway\_url,
 headers={
 "User-Agent": build\_user\_agent(),
 },
 timeout=CONNECT\_TIMEOUT\_SECONDS,
 proxy=ws\_proxy,
 )
 logger.info("\[%s\] WebSocket connected to %s", self.\_log\_tag, gateway\_url)

 async def \_listen\_loop(self) -> None:
 """Read WebSocket events and reconnect on errors.

 Close code handling follows the OpenClaw qqbot reference implementation:
 4004 → invalid token, refresh and reconnect
 4006/4007/4009 → session invalid, clear session and re-identify
 4008 → rate limited, back off 60s
 4914 → bot offline/sandbox, stop reconnecting
 4915 → bot banned, stop reconnecting
 """
 backoff\_idx = 0
 connect\_time = 0.0
 quick\_disconnect\_count = 0

 while self.\_running:
 try:
 connect\_time = time.monotonic()
 await self.\_read\_events()
 backoff\_idx = 0
 quick\_disconnect\_count = 0
 except asyncio.CancelledError:
 return
 except QQCloseError as exc:
 if not self.\_running:
 return

 code = exc.code
 logger.warning(
 "\[%s\] WebSocket closed: code=%s reason=%s",
 self.\_log\_tag,
 code,
 exc.reason,
 )

 # Quick disconnect detection (permission issues, misconfiguration)
 duration = time.monotonic() - connect\_time
 if duration < QUICK\_DISCONNECT\_THRESHOLD and connect\_time > 0:
 quick\_disconnect\_count += 1
 logger.info(
 "\[%s\] Quick disconnect (%.1fs), count: %d",
 self.\_log\_tag,
 duration,
 quick\_disconnect\_count,
 )
 if quick\_disconnect\_count >= MAX\_QUICK\_DISCONNECT\_COUNT:
 logger.error(
 "\[%s\] Too many quick disconnects. "
 "Check: 1) AppID/Secret correct 2) Bot permissions on QQ Open Platform",
 self.\_log\_tag,
 )
 self.\_set\_fatal\_error(
 "qq\_quick\_disconnect",
 "Too many quick disconnects — check bot permissions",
 retryable=True,
 )
 return
 else:
 quick\_disconnect\_count = 0

 self.\_mark\_transport\_disconnected()
 self.\_fail\_pending("Connection closed")

 # Stop reconnecting for fatal codes (unrecoverable errors)
 if code in {
 4001, # Invalid opcode
 4002, # Invalid payload
 4010, # Invalid shard
 4011, # Sharding required
 4012, # Invalid API version
 4013, # Invalid intent
 4014, # Intent not authorized
 4914, # Offline/sandbox-only
 4915, # Banned
 }:
 fatal\_descriptions = {
 4001: "invalid opcode",
 4002: "invalid payload",
 4010: "invalid shard",
 4011: "sharding required",
 4012: "invalid API version",
 4013: "invalid intent",
 4014: "intent not authorized",
 4914: "offline/sandbox-only",
 4915: "banned",
 }
 desc = fatal\_descriptions.get(code, f"fatal error (code={code})")
 logger.error(
 "\[%s\] Bot is %s. Check QQ Open Platform.", self.\_log\_tag, desc
 )
 self.\_set\_fatal\_error(
 f"qq\_{desc}", f"Bot is {desc}", retryable=False
 )
 return

 # Rate limited
 if code == 4008:
 logger.info(
 "\[%s\] Rate limited (4008), waiting %ds",
 self.\_log\_tag,
 RATE\_LIMIT\_DELAY,
 )
 if backoff\_idx >= MAX\_RECONNECT\_ATTEMPTS:
 self.\_mark\_disconnected()
 return
 await asyncio.sleep(RATE\_LIMIT\_DELAY)
 if await self.\_reconnect(backoff\_idx):
 backoff\_idx = 0
 quick\_disconnect\_count = 0
 else:
 backoff\_idx += 1
 continue

 # Token invalid → clear cached token so \_ensure\_token() refreshes
 if code == 4004:
 logger.info(
 "\[%s\] Invalid token (4004), will refresh and reconnect",
 self.\_log\_tag,
 )
 self.\_access\_token = None
 self.\_token\_expires\_at = 0.0

 # Session invalid → clear session, will re-identify on next Hello
 # Note: 4009 (connection timeout) is NOT included here — it is
 # resumable per the QQ protocol and should preserve session state.
 if code in {
 4006,
 4007,
 4900,
 4901,
 4902,
 4903,
 4904,
 4905,
 4906,
 4907,
 4908,
 4909,
 4910,
 4911,
 4912,
 4913,
 }:
 logger.info(
 "\[%s\] Session error (%d), clearing session for re-identify",
 self.\_log\_tag,
 code,
 )
 self.\_session\_id = None
 self.\_last\_seq = None

 if await self.\_reconnect(backoff\_idx):
 backoff\_idx = 0
 quick\_disconnect\_count = 0
 else:
 backoff\_idx += 1
 if backoff\_idx >= MAX\_RECONNECT\_ATTEMPTS:
 logger.error("\[%s\] Max reconnect attempts reached (QQCloseError)", self.\_log\_tag)
 self.\_mark\_disconnected()
 return

 except Exception as exc:
 if not self.\_running:
 return
 logger.warning("\[%s\] WebSocket error: %s", self.\_log\_tag, exc)
 self.\_mark\_transport\_disconnected()
 self.\_fail\_pending("Connection interrupted")

 if backoff\_idx >= MAX\_RECONNECT\_ATTEMPTS:
 logger.error("\[%s\] Max reconnect attempts reached", self.\_log\_tag)
 self.\_mark\_disconnected()
 return

 if await self.\_reconnect(backoff\_idx):
 backoff\_idx = 0
 quick\_disconnect\_count = 0
 else:
 backoff\_idx += 1

 async def \_reconnect(self, backoff\_idx: int) -> bool:
 """Attempt to reconnect the WebSocket. Returns True on success."""
 delay = RECONNECT\_BACKOFF\[min(backoff\_idx, len(RECONNECT\_BACKOFF) - 1)\]
 logger.info(
 "\[%s\] Reconnecting in %ds (attempt %d)...",
 self.\_log\_tag,
 delay,
 backoff\_idx + 1,
 )
 await asyncio.sleep(delay)

 self.\_heartbeat\_interval = 30.0 # reset until Hello
 try:
 await self.\_ensure\_token()
 gateway\_url = await self.\_get\_gateway\_url()
 await self.\_open\_ws(gateway\_url)
 self.\_mark\_connected()
 logger.info("\[%s\] Reconnected", self.\_log\_tag)
 return True
 except Exception as exc:
 logger.warning("\[%s\] Reconnect failed: %s", self.\_log\_tag, exc)
 return False

 async def \_read\_events(self) -> None:
 """Read WebSocket frames until connection closes."""
 if not self.\_ws:
 raise RuntimeError("WebSocket not connected")
 if self.\_ws.closed:
 # A closed-but-non-None ws makes the while-condition false on entry,
 # so this would return normally — which \_listen\_loop treats as a
 # clean read and immediately retries with backoff reset to 0,
 # producing a 100% CPU spin. Raise so the reconnect/backoff path runs.
 raise RuntimeError("WebSocket closed")

 while self.\_running and self.\_ws and not self.\_ws.closed:
 msg = await self.\_ws.receive()
 if msg.type == aiohttp.WSMsgType.TEXT:
 payload = self.\_parse\_json(msg.data)
 if payload:
 self.\_dispatch\_payload(payload)
 elif msg.type in {aiohttp.WSMsgType.PING,}:
 # aiohttp auto-replies with PONG
 pass
 elif msg.type == aiohttp.WSMsgType.CLOSE:
 raise QQCloseError(msg.data, msg.extra)
 elif msg.type in {aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR}:
 raise RuntimeError("WebSocket closed")

 async def \_heartbeat\_loop(self) -> None:
 """Send periodic heartbeats (QQ Gateway expects op 1 heartbeat with latest seq).

 The interval is set from the Hello (op 10) event's heartbeat\_interval.
 QQ's default is ~41s; we send at 80% of the interval to stay safe.
 """
 try:
 while self.\_running:
 await asyncio.sleep(self.\_heartbeat\_interval)
 if not self.\_ws or self.\_ws.closed:
 continue
 try:
 # d should be the latest sequence number received, or null
 await self.\_ws.send\_json({"op": 1, "d": self.\_last\_seq})
 except Exception as exc:
 logger.debug("\[%s\] Heartbeat failed: %s", self.\_log\_tag, exc)
 except asyncio.CancelledError:
 pass

 async def \_send\_identify(self) -> None:
 """Send op 2 Identify to authenticate the WebSocket connection.

 After receiving op 10 Hello, the client must send op 2 Identify with
 the bot token and intents. On success the server replies with a
 READY dispatch event.

 Reference: https://bot.q.qq.com/wiki/develop/api-v2/dev-prepare/interface-framework/reference.html
 """
 token = await self.\_ensure\_token()
 identify\_payload = {
 "op": 2,
 "d": {
 "token": f"QQBot {token}",
 "intents": (1 << 25)
 \| (1 << 30)
 \| (1 << 12)
 \| (1 << 26), # C2C\_GROUP\_AT\_MESSAGES + PUBLIC\_GUILD\_MESSAGES + DIRECT\_MESSAGE + INTERACTION
 "shard": \[0, 1\],
 "properties": {
 "$os": "macOS",
 "$browser": "hermes-agent",
 "$device": "hermes-agent",
 },
 },
 }
 try:
 if self.\_ws and not self.\_ws.closed:
 await self.\_ws.send\_json(identify\_payload)
 logger.info("\[%s\] Identify sent", self.\_log\_tag)
 else:
 logger.warning(
 "\[%s\] Cannot send Identify: WebSocket not connected", self.\_log\_tag
 )
 except Exception as exc:
 logger.error("\[%s\] Failed to send Identify: %s", self.\_log\_tag, exc)

 async def \_send\_resume(self) -> None:
 """Send op 6 Resume to re-authenticate after a reconnection.

 Reference: https://bot.q.qq.com/wiki/develop/api-v2/dev-prepare/interface-framework/reference.html
 """
 token = await self.\_ensure\_token()
 resume\_payload = {
 "op": 6,
 "d": {
 "token": f"QQBot {token}",
 "session\_id": self.\_session\_id,
 "seq": self.\_last\_seq,
 },
 }
 try:
 if self.\_ws and not self.\_ws.closed:
 await self.\_ws.send\_json(resume\_payload)
 logger.info(
 "\[%s\] Resume sent (session\_id=%s, seq=%s)",
 self.\_log\_tag,
 self.\_session\_id,
 self.\_last\_seq,
 )
 else:
 logger.warning(
 "\[%s\] Cannot send Resume: WebSocket not connected", self.\_log\_tag
 )
 except Exception as exc:
 logger.error("\[%s\] Failed to send Resume: %s", self.\_log\_tag, exc)
 # If resume fails, clear session and fall back to identify on next Hello
 self.\_session\_id = None
 self.\_last\_seq = None

 @staticmethod
 def \_create\_task(coro):
 """Schedule a coroutine, silently skipping if no event loop is running.

 This avoids \`\`RuntimeError: no running event loop\`\` when tests call
 \`\`\_dispatch\_payload\`\` synchronously outside of \`\`asyncio.run()\`\`.
 """
 try:
 loop = asyncio.get\_running\_loop()
 return loop.create\_task(coro)
 except RuntimeError:
 return None

 def \_dispatch\_payload(self, payload: Dict\[str, Any\]) -> None:
 """Route inbound WebSocket payloads (dispatch synchronously, spawn async handlers)."""
 op = payload.get("op")
 t = payload.get("t")
 s = payload.get("s")
 d = payload.get("d")
 if isinstance(s, int) and (self.\_last\_seq is None or s > self.\_last\_seq):
 self.\_last\_seq = s

 # op 10 = Hello (heartbeat interval) — must reply with Identify/Resume
 if op == 10:
 d\_data = d if isinstance(d, dict) else {}
 interval\_ms = d\_data.get("heartbeat\_interval", 30000)
 # Send heartbeats at 80% of the server interval to stay safe
 self.\_heartbeat\_interval = interval\_ms / 1000.0 \* 0.8
 logger.debug(
 "\[%s\] Hello received, heartbeat\_interval=%dms (sending every %.1fs)",
 self.\_log\_tag,
 interval\_ms,
 self.\_heartbeat\_interval,
 )
 # Authenticate: send Resume if we have a session, else Identify.
 # Use \_create\_task which is safe when no event loop is running (tests).
 if self.\_session\_id and self.\_last\_seq is not None:
 self.\_create\_task(self.\_send\_resume())
 else:
 self.\_create\_task(self.\_send\_identify())
 return

 # op 0 = Dispatch
 if op == 0 and t:
 if t == "READY":
 self.\_handle\_ready(d)
 elif t == "RESUMED":
 logger.info("\[%s\] Session resumed", self.\_log\_tag)
 elif t in {
 "C2C\_MESSAGE\_CREATE",
 "GROUP\_AT\_MESSAGE\_CREATE",
 "DIRECT\_MESSAGE\_CREATE",
 "GUILD\_MESSAGE\_CREATE",
 "GUILD\_AT\_MESSAGE\_CREATE",
 }:
 asyncio.create\_task(self.\_on\_message(t, d))
 elif t == "INTERACTION\_CREATE":
 self.\_create\_task(self.\_on\_interaction(d))
 else:
 logger.debug("\[%s\] Unhandled dispatch: %s", self.\_log\_tag, t)
 return

 # op 11 = Heartbeat ACK
 if op == 11:
 return

 # op 7 = Server Reconnect — server asks client to reconnect (e.g.
 # load-balancing, maintenance). Close the WS so \_read\_events raises
 # and the outer loop triggers a reconnect with Resume.
 if op == 7:
 logger.info("\[%s\] Server requested reconnect (op 7)", self.\_log\_tag)
 if self.\_ws and not self.\_ws.closed:
 self.\_create\_task(self.\_ws.close())
 return

 # op 9 = Invalid Session — d=True means session is resumable,
 # d=False means we must re-identify from scratch.
 if op == 9:
 resumable = bool(d) if d is not None else False
 if not resumable:
 logger.info(
 "\[%s\] Invalid session (op 9, not resumable), clearing session",
 self.\_log\_tag,
 )
 self.\_session\_id = None
 self.\_last\_seq = None
 else:
 logger.info("\[%s\] Invalid session (op 9, resumable)", self.\_log\_tag)
 if self.\_ws and not self.\_ws.closed:
 self.\_create\_task(self.\_ws.close())
 return

 logger.debug("\[%s\] Unknown op: %s", self.\_log\_tag, op)

 def \_handle\_ready(self, d: Any) -> None:
 """Handle the READY event — store session\_id for resume."""
 if isinstance(d, dict):
 self.\_session\_id = d.get("session\_id")
 logger.info("\[%s\] Ready, session\_id=%s", self.\_log\_tag, self.\_session\_id)

 # ------------------------------------------------------------------
 # JSON helpers
 # ------------------------------------------------------------------

 @staticmethod
 def \_parse\_json(raw: Any) -> Optional\[Dict\[str, Any\]\]:
 try:
 payload = json.loads(raw)
 except Exception:
 logger.warning("\[QQBot\] Failed to parse JSON: %r", raw)
 return None
 return payload if isinstance(payload, dict) else None

 @staticmethod
 def \_next\_msg\_seq(msg\_id: str) -> int:
 """Generate a message sequence number in 0..65535 range."""
 time\_part = int(time.time()) % 100000000
 rand = int(uuid.uuid4().hex\[:4\], 16)
 return (time\_part ^ rand) % 65536

 # ------------------------------------------------------------------
 # Inbound message handling
 # ------------------------------------------------------------------

 async def handle\_message(self, event: MessageEvent) -> None:
 """Cache the last message ID per chat, then delegate to base."""
 if event.message\_id and event.source.chat\_id:
 self.\_last\_msg\_id\[event.source.chat\_id\] = event.message\_id
 await super().handle\_message(event)

 async def \_on\_message(self, event\_type: str, d: Any) -> None:
 """Process an inbound QQ Bot message event."""
 if not isinstance(d, dict):
 return

 # Extract common fields
 msg\_id = str(d.get("id", ""))
 if not msg\_id or self.\_is\_duplicate(msg\_id):
 logger.debug(
 "\[%s\] Duplicate or missing message id: %s", self.\_log\_tag, msg\_id
 )
 return

 timestamp = str(d.get("timestamp", ""))
 content = str(d.get("content", "")).strip()
 author = d.get("author") if isinstance(d.get("author"), dict) else {}

 # Route by event type
 if event\_type == "C2C\_MESSAGE\_CREATE":
 await self.\_handle\_c2c\_message(d, msg\_id, content, author, timestamp)
 elif event\_type in {"GROUP\_AT\_MESSAGE\_CREATE",}:
 await self.\_handle\_group\_message(d, msg\_id, content, author, timestamp)
 elif event\_type in {"GUILD\_MESSAGE\_CREATE", "GUILD\_AT\_MESSAGE\_CREATE"}:
 await self.\_handle\_guild\_message(d, msg\_id, content, author, timestamp)
 elif event\_type == "DIRECT\_MESSAGE\_CREATE":
 await self.\_handle\_dm\_message(d, msg\_id, content, author, timestamp)

 # ------------------------------------------------------------------
 # Inline-keyboard interactions (INTERACTION\_CREATE)
 # ------------------------------------------------------------------

 def set\_interaction\_callback(
 self,
 callback: Optional\[Callable\[\[InteractionEvent\], Awaitable\[None\]\]\],
 ) -\> None:
 """Register (or clear) the interaction callback.

 Invoked once per \`\`INTERACTION\_CREATE\`\` event \*after\* the adapter has
 ACKed the interaction. The callback is responsible for routing the
 button click to the right subsystem (approval resolver, update-prompt
 resolver, etc.) based on the \`\`button\_data\`\` payload.
 """
 self.\_interaction\_callback = callback

 async def \_on\_interaction(self, d: Any) -> None:
 """Handle an \`\`INTERACTION\_CREATE\`\` event.

 Responsibilities:

 1\. Parse the raw payload into an :class:\`InteractionEvent\`.
 2\. ACK the interaction (\`\`PUT /interactions/{id}\`\`) so the client
 stops showing a loading indicator on the button.
 3\. Dispatch to the registered interaction callback, if any.
 """
 if not isinstance(d, dict):
 return
 try:
 event = parse\_interaction\_event(d)
 except Exception as exc:
 logger.warning(
 "\[%s\] Failed to parse INTERACTION\_CREATE: %s", self.\_log\_tag, exc
 )
 return

 if not event.id:
 logger.warning(
 "\[%s\] INTERACTION\_CREATE missing id, skipping ACK", self.\_log\_tag
 )
 return

 # ACK the interaction promptly — per the QQ docs the client will show
 # an error icon on the button if we don't respond quickly.
 try:
 await self.\_acknowledge\_interaction(event.id)
 except Exception as exc:
 logger.warning(
 "\[%s\] Failed to ACK interaction %s: %s",
 self.\_log\_tag, event.id, exc,
 )

 logger.info(
 "\[%s\] Interaction: scene=%s button\_data=%r operator=%s",
 self.\_log\_tag, event.scene, event.button\_data, event.operator\_openid,
 )

 callback = self.\_interaction\_callback
 if callback is None:
 logger.debug(
 "\[%s\] No interaction callback registered; dropping button "
 "click %r",
 self.\_log\_tag, event.button\_data,
 )
 return
 try:
 await callback(event)
 except Exception as exc:
 logger.error(
 "\[%s\] Interaction callback raised: %s",
 self.\_log\_tag, exc, exc\_info=True,
 )

 async def \_acknowledge\_interaction(
 self,
 interaction\_id: str,
 code: int = 0,
 ) -\> None:
 """ACK a button interaction via \`\`PUT /interactions/{id}\`\`.

 :param interaction\_id: The \`\`id\`\` field from the
 \`\`INTERACTION\_CREATE\`\` event.
 :param code: Response code (\`\`0\`\` = success).
 """
 if not self.\_http\_client:
 raise RuntimeError("HTTP client not initialized — not connected?")
 token = await self.\_ensure\_token()
 headers = {
 "Authorization": f"QQBot {token}",
 "Content-Type": "application/json",
 "User-Agent": build\_user\_agent(),
 }
 resp = await self.\_http\_client.put(
 f"{API\_BASE}/interactions/{interaction\_id}",
 headers=headers,
 json={"code": code},
 timeout=DEFAULT\_API\_TIMEOUT,
 )
 if resp.status\_code >= 400:
 raise RuntimeError(
 f"Interaction ACK failed \[{resp.status\_code}\]: "
 f"{resp.text\[:200\]}"
 )

 # Mapping from QQ keyboard button decisions → the \`\`choice\`\` vocabulary
 # accepted by \`\`tools.approval.resolve\_gateway\_approval\`\`. QQ's 3-button
 # layout (mobile-space constraint) collapses "session" and "always" into
 # a single "always" button; users wanting session-only approval can fall
 # back to the \`\`/approve session\`\` text command.
 \_APPROVAL\_BUTTON\_TO\_CHOICE = {
 "allow-once": "once",
 "allow-always": "always",
 "deny": "deny",
 }

 @staticmethod
 def \_parse\_gateway\_session\_key(session\_key: str) -> Optional\[Dict\[str, str\]\]:
 """Parse \`\`agent:main:::\[:\]\`\`."""
 parts = str(session\_key or "").split(":")
 if len(parts) < 5 or parts\[0\] != "agent" or parts\[1\] != "main":
 return None
 parsed = {
 "platform": parts\[2\],
 "chat\_type": parts\[3\],
 "chat\_id": parts\[4\],
 }
 if len(parts) > 5:
 parsed\["user\_id"\] = parts\[5\]
 return parsed

 def \_is\_authorized\_interaction\_for\_session(
 self,
 event: InteractionEvent,
 session\_key: str,
 ) -\> bool:
 """Authorize approval/update interactions against session + operator."""
 parsed = self.\_parse\_gateway\_session\_key(session\_key)
 operator = str(event.operator\_openid or "").strip()
 if not parsed or parsed.get("platform") != "qqbot" or not operator:
 return False

 chat\_type = parsed.get("chat\_type", "")
 chat\_id = parsed.get("chat\_id", "")
 if chat\_type == "c2c":
 return bool(chat\_id) and operator == chat\_id

 if chat\_type in {"group", "guild"}:
 event\_chat = str(event.group\_openid or event.guild\_id or "").strip()
 if not event\_chat or event\_chat != chat\_id:
 return False
 session\_user = str(parsed.get("user\_id", "")).strip()
 return bool(session\_user) and operator == session\_user

 return False

 async def \_default\_interaction\_dispatch(
 self,
 event: InteractionEvent,
 ) -\> None:
 """Route \`\`INTERACTION\_CREATE\`\` button clicks to the right subsystem.

 \- \`\`approve::\`\` →
 :func:\`tools.approval.resolve\_gateway\_approval\`
 (unblocks the agent thread waiting on a dangerous-command approval).
 \- \`\`update\_prompt:\`\` →
 writes the answer to \`\`~/.hermes/.update\_response\`\` for the
 detached \`\`hermes update --gateway\`\` process to consume.
 \- Anything else is logged at DEBUG and ignored.

 Installed as the adapter's default interaction callback in
 \`\`\_\_init\_\_\`\`. Callers can replace via
 :meth:\`set\_interaction\_callback\` to route clicks elsewhere (or pass
 \`\`None\`\` to drop them entirely).
 """
 button\_data = event.button\_data
 if not button\_data:
 return

 approval = parse\_approval\_button\_data(button\_data)
 if approval is not None:
 session\_key, decision = approval
 choice = self.\_APPROVAL\_BUTTON\_TO\_CHOICE.get(decision)
 if choice is None:
 logger.warning(
 "\[%s\] Unknown approval decision %r (session=%s)",
 self.\_log\_tag, decision, session\_key,
 )
 return
 if not self.\_is\_authorized\_interaction\_for\_session(event, session\_key):
 logger.warning(
 "\[%s\] Rejected unauthorized approval click for session %s "
 "(operator=%s)",
 self.\_log\_tag, session\_key, event.operator\_openid,
 )
 return
 try:
 # Import lazily to keep the adapter importable in tests that
 # don't exercise the approval subsystem.
 from tools.approval import resolve\_gateway\_approval
 count = resolve\_gateway\_approval(session\_key, choice)
 logger.info(
 "\[%s\] Button resolved %d approval(s) for session %s "
 "(choice=%s, operator=%s)",
 self.\_log\_tag, count, session\_key, choice,
 event.operator\_openid,
 )
 except Exception as exc:
 logger.error(
 "\[%s\] resolve\_gateway\_approval failed for session %s: %s",
 self.\_log\_tag, session\_key, exc,
 )
 return

 update\_answer = parse\_update\_prompt\_button\_data(button\_data)
 if update\_answer is not None:
 update\_session\_key = f"agent:main:qqbot:{event.scene}:{event.group\_openid or event.guild\_id or event.user\_openid}"
 if not self.\_is\_authorized\_interaction\_for\_session(event, update\_session\_key):
 logger.warning(
 "\[%s\] Rejected unauthorized update prompt click (operator=%s)",
 self.\_log\_tag, event.operator\_openid,
 )
 return
 self.\_write\_update\_response(update\_answer, event.operator\_openid)
 return

 logger.debug(
 "\[%s\] Unrecognised button\_data %r from interaction %s",
 self.\_log\_tag, button\_data, event.id,
 )

 @staticmethod
 def \_write\_update\_response(answer: str, operator: str = "") -> None:
 """Atomically write the update-prompt answer to \`\`.update\_response\`\`.

 Mirrors the Discord / Telegram / Feishu adapters: the detached
 \`\`hermes update --gateway\`\` watcher polls this file for a \`\`y\`\`/\`\`n\`\`
 response to its interactive prompts (stash-restore, config migration).
 Writes via \`\`tmp + rename\`\` so a partial write can't fool the reader.
 """
 try:
 from hermes\_constants import get\_hermes\_home
 home = get\_hermes\_home()
 response\_path = home / ".update\_response"
 tmp = response\_path.with\_suffix(".tmp")
 tmp.write\_text(answer)
 tmp.replace(response\_path)
 logger.info(
 "QQ update prompt answered %r by %s",
 answer, operator or "(unknown)",
 )
 except Exception as exc:
 logger.error("Failed to write update response: %s", exc)

 async def \_handle\_c2c\_message(
 self,
 d: Dict\[str, Any\],
 msg\_id: str,
 content: str,
 author: Dict\[str, Any\],
 timestamp: str,
 ) -\> None:
 """Handle a C2C (private) message event."""
 user\_openid = str(author.get("user\_openid", ""))
 if not user\_openid:
 return
 if not self.\_is\_dm\_intake\_allowed(user\_openid):
 return

 text = content
 attachments\_raw = d.get("attachments")
 logger.info(
 "\[%s\] C2C message: id=%s content=%r attachments=%s",
 self.\_log\_tag,
 msg\_id,
 content\[:50\] if content else "",
 (
 f"{len(attachments\_raw) if isinstance(attachments\_raw, list) else 0} items"
 if attachments\_raw
 else "None"
 ),
 )
 if attachments\_raw and isinstance(attachments\_raw, list):
 for \_i, \_att in enumerate(attachments\_raw):
 if isinstance(\_att, dict):
 logger.info(
 "\[%s\] attachment\[%d\]: content\_type=%s url=%s filename=%s",
 self.\_log\_tag,
 \_i,
 \_att.get("content\_type", ""),
 str(\_att.get("url", ""))\[:80\],
 \_att.get("filename", ""),
 )

 # Process all attachments uniformly (images, voice, files)
 att\_result = await self.\_process\_attachments(attachments\_raw)
 image\_urls = att\_result\["image\_urls"\]
 image\_media\_types = att\_result\["image\_media\_types"\]
 voice\_transcripts = att\_result\["voice\_transcripts"\]
 attachment\_info = att\_result\["attachment\_info"\]

 # Append voice transcripts to the text body
 if voice\_transcripts:
 voice\_block = "\\n".join(voice\_transcripts)
 text = (
 (text + "\\n\\n" + voice\_block).strip() if text.strip() else voice\_block
 )
 # Append non-media attachment info
 if attachment\_info:
 text = (
 (text + "\\n\\n" + attachment\_info).strip()
 if text.strip()
 else attachment\_info
 )

 logger.info(
 "\[%s\] After processing: images=%d, voice=%d",
 self.\_log\_tag,
 len(image\_urls),
 len(voice\_transcripts),
 )

 # Merge any quoted-message context (message\_type=103 → msg\_elements\[0\]).
 quoted = await self.\_process\_quoted\_context(d)
 text = self.\_merge\_quote\_into(text, quoted\["quote\_block"\])
 if quoted\["image\_urls"\]:
 image\_urls = image\_urls + quoted\["image\_urls"\]
 image\_media\_types = image\_media\_types + quoted\["image\_media\_types"\]

 if not text.strip() and not image\_urls:
 return

 self.\_chat\_type\_map\[user\_openid\] = "c2c"
 event = MessageEvent(
 source=self.build\_source(
 chat\_id=user\_openid,
 user\_id=user\_openid,
 chat\_type="dm",
 ),
 text=text,
 message\_type=self.\_detect\_message\_type(image\_urls, image\_media\_types),
 raw\_message=d,
 message\_id=msg\_id,
 media\_urls=image\_urls,
 media\_types=image\_media\_types,
 timestamp=self.\_parse\_qq\_timestamp(timestamp),
 )
 await self.handle\_message(event)

 async def \_handle\_group\_message(
 self,
 d: Dict\[str, Any\],
 msg\_id: str,
 content: str,
 author: Dict\[str, Any\],
 timestamp: str,
 ) -\> None:
 """Handle a group @-message event."""
 group\_openid = str(d.get("group\_openid", ""))
 if not group\_openid:
 return
 if not self.\_is\_group\_allowed(
 group\_openid, str(author.get("member\_openid", ""))
 ):
 return

 # Strip the @bot mention prefix from content
 text = self.\_strip\_at\_mention(content)
 att\_result = await self.\_process\_attachments(d.get("attachments"))
 image\_urls = att\_result\["image\_urls"\]
 image\_media\_types = att\_result\["image\_media\_types"\]
 voice\_transcripts = att\_result\["voice\_transcripts"\]
 attachment\_info = att\_result\["attachment\_info"\]

 # Append voice transcripts
 if voice\_transcripts:
 voice\_block = "\\n".join(voice\_transcripts)
 text = (
 (text + "\\n\\n" + voice\_block).strip() if text.strip() else voice\_block
 )
 if attachment\_info:
 text = (
 (text + "\\n\\n" + attachment\_info).strip()
 if text.strip()
 else attachment\_info
 )

 # Merge any quoted-message context (message\_type=103 → msg\_elements\[0\]).
 quoted = await self.\_process\_quoted\_context(d)
 text = self.\_merge\_quote\_into(text, quoted\["quote\_block"\])
 if quoted\["image\_urls"\]:
 image\_urls = image\_urls + quoted\["image\_urls"\]
 image\_media\_types = image\_media\_types + quoted\["image\_media\_types"\]

 if not text.strip() and not image\_urls:
 return

 self.\_chat\_type\_map\[group\_openid\] = "group"
 event = MessageEvent(
 source=self.build\_source(
 chat\_id=group\_openid,
 user\_id=str(author.get("member\_openid", "")),
 chat\_type="group",
 ),
 text=text,
 message\_type=self.\_detect\_message\_type(image\_urls, image\_media\_types),
 raw\_message=d,
 message\_id=msg\_id,
 media\_urls=image\_urls,
 media\_types=image\_media\_types,
 timestamp=self.\_parse\_qq\_timestamp(timestamp),
 )
 await self.handle\_message(event)

 async def \_handle\_guild\_message(
 self,
 d: Dict\[str, Any\],
 msg\_id: str,
 content: str,
 author: Dict\[str, Any\],
 timestamp: str,
 ) -\> None:
 """Handle a guild/channel message event."""
 channel\_id = str(d.get("channel\_id", ""))
 if not channel\_id:
 return

 # Apply group\_policy ACL — guild channels are group-like contexts.
 # Without this check any member of any guild the bot is in could
 # bypass the configured allowlist.
 guild\_id = str(d.get("guild\_id", ""))
 author\_id = str(author.get("id", ""))
 if not self.\_is\_group\_allowed(guild\_id or channel\_id, author\_id):
 logger.debug(
 "\[%s\] Guild message blocked by ACL: channel=%s user=%s",
 self.\_log\_tag, channel\_id, author\_id,
 )
 return

 member = d.get("member") if isinstance(d.get("member"), dict) else {}
 nick = str(member.get("nick", "")) or str(author.get("username", ""))

 text = content
 att\_result = await self.\_process\_attachments(d.get("attachments"))
 image\_urls = att\_result\["image\_urls"\]
 image\_media\_types = att\_result\["image\_media\_types"\]
 voice\_transcripts = att\_result\["voice\_transcripts"\]
 attachment\_info = att\_result\["attachment\_info"\]

 if voice\_transcripts:
 voice\_block = "\\n".join(voice\_transcripts)
 text = (
 (text + "\\n\\n" + voice\_block).strip() if text.strip() else voice\_block
 )
 if attachment\_info:
 text = (
 (text + "\\n\\n" + attachment\_info).strip()
 if text.strip()
 else attachment\_info
 )

 # Merge any quoted-message context (message\_type=103 → msg\_elements\[0\]).
 quoted = await self.\_process\_quoted\_context(d)
 text = self.\_merge\_quote\_into(text, quoted\["quote\_block"\])
 if quoted\["image\_urls"\]:
 image\_urls = image\_urls + quoted\["image\_urls"\]
 image\_media\_types = image\_media\_types + quoted\["image\_media\_types"\]

 if not text.strip() and not image\_urls:
 return

 self.\_chat\_type\_map\[channel\_id\] = "guild"
 event = MessageEvent(
 source=self.build\_source(
 chat\_id=channel\_id,
 user\_id=str(author.get("id", "")),
 user\_name=nick or None,
 chat\_type="group",
 ),
 text=text,
 message\_type=self.\_detect\_message\_type(image\_urls, image\_media\_types),
 raw\_message=d,
 message\_id=msg\_id,
 media\_urls=image\_urls,
 media\_types=image\_media\_types,
 timestamp=self.\_parse\_qq\_timestamp(timestamp),
 )
 await self.handle\_message(event)

 async def \_handle\_dm\_message(
 self,
 d: Dict\[str, Any\],
 msg\_id: str,
 content: str,
 author: Dict\[str, Any\],
 timestamp: str,
 ) -\> None:
 """Handle a guild DM message event."""
 guild\_id = str(d.get("guild\_id", ""))
 if not guild\_id:
 return

 # Apply dm\_policy ACL — guild DMs were previously unauthenticated.
 # Without this check any member of any guild the bot is in could
 # bypass the configured allowlist via direct messages.
 author\_id = str(author.get("id", ""))
 if not self.\_is\_dm\_intake\_allowed(author\_id):
 logger.debug(
 "\[%s\] Guild DM blocked by ACL: guild=%s user=%s",
 self.\_log\_tag, guild\_id, author\_id,
 )
 return

 text = content
 att\_result = await self.\_process\_attachments(d.get("attachments"))
 image\_urls = att\_result\["image\_urls"\]
 image\_media\_types = att\_result\["image\_media\_types"\]
 voice\_transcripts = att\_result\["voice\_transcripts"\]
 attachment\_info = att\_result\["attachment\_info"\]

 if voice\_transcripts:
 voice\_block = "\\n".join(voice\_transcripts)
 text = (
 (text + "\\n\\n" + voice\_block).strip() if text.strip() else voice\_block
 )
 if attachment\_info:
 text = (
 (text + "\\n\\n" + attachment\_info).strip()
 if text.strip()
 else attachment\_info
 )

 # Merge any quoted-message context (message\_type=103 → msg\_elements\[0\]).
 quoted = await self.\_process\_quoted\_context(d)
 text = self.\_merge\_quote\_into(text, quoted\["quote\_block"\])
 if quoted\["image\_urls"\]:
 image\_urls = image\_urls + quoted\["image\_urls"\]
 image\_media\_types = image\_media\_types + quoted\["image\_media\_types"\]

 if not text.strip() and not image\_urls:
 return

 self.\_chat\_type\_map\[guild\_id\] = "dm"
 event = MessageEvent(
 source=self.build\_source(
 chat\_id=guild\_id,
 user\_id=str(author.get("id", "")),
 chat\_type="dm",
 ),
 text=text,
 message\_type=self.\_detect\_message\_type(image\_urls, image\_media\_types),
 raw\_message=d,
 message\_id=msg\_id,
 media\_urls=image\_urls,
 media\_types=image\_media\_types,
 timestamp=self.\_parse\_qq\_timestamp(timestamp),
 )
 await self.handle\_message(event)

 # ------------------------------------------------------------------
 # Quoted-message handling
 # ------------------------------------------------------------------

 async def \_process\_quoted\_context(
 self,
 d: Dict\[str, Any\],
 ) -\> Dict\[str, Any\]:
 """Process the quoted message a user is replying to.

 When a user replies while quoting another message, the platform sets
 \`\`message\_type = 103\`\` and pushes the referenced message's content and
 attachments inside \`\`msg\_elements\[0\]\`\`. The old adapter ignored
 \`\`msg\_elements\`\` entirely, so:

 \- Quoted text was surfaced only when the user typed something of
 their own — bare quote-replies showed nothing.
 \- Quoted attachments (images, voice, files) were never downloaded
 or described.
 \- Quoted voice messages specifically produced no transcript, so the
 LLM had no way to see what the user was referring to.

 This method parses \`\`msg\_elements\`\` and runs the quoted attachments
 through the same :meth:\`\_process\_attachments\` pipeline as the main
 message body, so quoted voice messages get STT transcripts and
 quoted images are cached identically.

 :param d: Raw inbound message dict (from the WS dispatch payload).
 :returns: Dict with keys:

 \- \`\`quote\_block\`\`: string to prepend to the user's text body
 (empty when there's nothing quoted).
 \- \`\`image\_urls\`\`: list of cached quoted-image paths.
 \- \`\`image\_media\_types\`\`: parallel list of image MIME types.
 """
 empty = {
 "quote\_block": "",
 "image\_urls": \[\],
 "image\_media\_types": \[\],
 }
 # Short-circuit: only message\_type 103 indicates a quote.
 try:
 if int(d.get("message\_type", 0) or 0) != 103:
 return empty
 except (TypeError, ValueError):
 return empty

 elements = d.get("msg\_elements")
 if not isinstance(elements, list) or not elements:
 return empty

 # msg\_elements\[0\] carries the referenced message. Additional elements
 # (if any) are very rare in practice; we concatenate their text and
 # union their attachments for completeness.
 quoted\_text\_parts: List\[str\] = \[\]
 all\_attachments: List\[Dict\[str, Any\]\] = \[\]
 for elem in elements:
 if not isinstance(elem, dict):
 continue
 etext = str(elem.get("content", "")).strip()
 if etext:
 quoted\_text\_parts.append(etext)
 eatts = elem.get("attachments")
 if isinstance(eatts, list):
 for a in eatts:
 if isinstance(a, dict):
 all\_attachments.append(a)

 att\_result = await self.\_process\_attachments(all\_attachments)
 quoted\_voice = att\_result.get("voice\_transcripts") or \[\]
 quoted\_info = att\_result.get("attachment\_info") or ""
 quoted\_images = att\_result.get("image\_urls") or \[\]
 quoted\_image\_types = att\_result.get("image\_media\_types") or \[\]

 lines: List\[str\] = \[\]
 if quoted\_text\_parts:
 lines.append(" ".join(quoted\_text\_parts))
 for t in quoted\_voice:
 lines.append(t)
 if quoted\_info:
 lines.append(quoted\_info)

 if not lines and not quoted\_images:
 return empty

 if lines:
 quote\_block = "\[Quoted message\]:\\n" + "\\n".join(lines)
 else:
 # Images-only quote: give the LLM at least a marker so it knows
 # context was referenced.
 quote\_block = "\[Quoted message\]: (image)"

 return {
 "quote\_block": quote\_block,
 "image\_urls": quoted\_images,
 "image\_media\_types": quoted\_image\_types,
 }

 @staticmethod
 def \_merge\_quote\_into(text: str, quote\_block: str) -> str:
 """Prepend \`\`quote\_block\`\` to \*text\*, separated by a blank line."""
 if not quote\_block:
 return text
 if text.strip():
 return f"{quote\_block}\\n\\n{text}".strip()
 return quote\_block

 # ------------------------------------------------------------------
 # Attachment processing
 # ------------------------------------------------------------------

 @staticmethod
 def \_detect\_message\_type(media\_urls: list, media\_types: list):
 """Determine MessageType from attachment content types."""
 if not media\_urls:
 return MessageType.TEXT
 if not media\_types:
 return MessageType.PHOTO
 first\_type = media\_types\[0\].lower() if media\_types else ""
 if "audio" in first\_type or "voice" in first\_type or "silk" in first\_type:
 return MessageType.VOICE
 if "video" in first\_type:
 return MessageType.VIDEO
 if "image" in first\_type or "photo" in first\_type:
 return MessageType.PHOTO
 logger.debug(
 "Unknown media content\_type '%s', defaulting to TEXT",
 first\_type,
 )
 return MessageType.TEXT

 async def \_process\_attachments(
 self,
 attachments: Any,
 ) -\> Dict\[str, Any\]:
 """Process inbound attachments (all message types).

 Mirrors OpenClaw's \`\`processAttachments\`\` — handles images, voice, and
 other files uniformly.

 Returns a dict with:
 \- image\_urls: list\[str\] — cached local image paths
 \- image\_media\_types: list\[str\] — MIME types of cached images
 \- voice\_transcripts: list\[str\] — STT transcripts for voice messages
 \- attachment\_info: str — text description of non-image, non-voice attachments
 """
 if not isinstance(attachments, list):
 return {
 "image\_urls": \[\],
 "image\_media\_types": \[\],
 "voice\_transcripts": \[\],
 "attachment\_info": "",
 }

 image\_urls: List\[str\] = \[\]
 image\_media\_types: List\[str\] = \[\]
 voice\_transcripts: List\[str\] = \[\]
 other\_attachments: List\[str\] = \[\]

 for att in attachments:
 if not isinstance(att, dict):
 continue

 ct = str(att.get("content\_type", "")).strip().lower()
 url\_raw = str(att.get("url", "")).strip()
 filename = str(att.get("filename", ""))
 if url\_raw.startswith("//"):
 url = f"https:{url\_raw}"
 elif url\_raw:
 url = url\_raw
 else:
 url = ""
 continue

 logger.debug(
 "\[%s\] Processing attachment: content\_type=%s, url=%s, filename=%s",
 self.\_log\_tag,
 ct,
 url\[:80\],
 filename,
 )

 if self.\_is\_voice\_content\_type(ct, filename):
 # Voice: use QQ's asr\_refer\_text first, then voice\_wav\_url, then STT.
 asr\_refer = (
 str(att.get("asr\_refer\_text", "")).strip()
 if isinstance(att.get("asr\_refer\_text"), str)
 else ""
 )
 voice\_wav\_url = (
 str(att.get("voice\_wav\_url", "")).strip()
 if isinstance(att.get("voice\_wav\_url"), str)
 else ""
 )

 transcript = await self.\_stt\_voice\_attachment(
 url,
 ct,
 filename,
 asr\_refer\_text=asr\_refer or None,
 voice\_wav\_url=voice\_wav\_url or None,
 )
 if transcript:
 voice\_transcripts.append(f"\[Voice\] {transcript}")
 logger.debug("\[%s\] Voice transcript: %s", self.\_log\_tag, transcript)
 else:
 logger.warning("\[%s\] Voice STT failed for %s", self.\_log\_tag, url\[:60\])
 voice\_transcripts.append("\[Voice\] \[语音识别失败\]")
 elif ct.startswith("image/"):
 # Image: download and cache locally.
 try:
 cached\_path = await self.\_download\_and\_cache(url, ct, filename)
 if cached\_path and os.path.isfile(cached\_path):
 image\_urls.append(cached\_path)
 image\_media\_types.append(ct or "image/jpeg")
 elif cached\_path:
 logger.warning(
 "\[%s\] Cached image path does not exist: %s",
 self.\_log\_tag,
 cached\_path,
 )
 except Exception as exc:
 logger.debug("\[%s\] Failed to cache image: %s", self.\_log\_tag, exc)
 else:
 # Other attachments (video, file, etc.): download and record with path.
 try:
 cached\_path = await self.\_download\_and\_cache(url, ct, filename)
 if cached\_path:
 name = filename or ct
 if ct.startswith("video/"):
 other\_attachments.append(f"\[video: {name} ({cached\_path})\]")
 else:
 other\_attachments.append(f"\[file: {name} ({cached\_path})\]")
 except Exception as exc:
 logger.debug("\[%s\] Failed to cache attachment: %s", self.\_log\_tag, exc)

 attachment\_info = "\\n".join(other\_attachments) if other\_attachments else ""
 return {
 "image\_urls": image\_urls,
 "image\_media\_types": image\_media\_types,
 "voice\_transcripts": voice\_transcripts,
 "attachment\_info": attachment\_info,
 }

 async def \_download\_and\_cache(
 self, url: str, content\_type: str, original\_name: str = "",
 ) -\> Optional\[str\]:
 """Download a URL and cache it locally.

 :param original\_name: Preferred filename from attachment metadata.
 Falls back to the URL path basename if empty.
 """
 from tools.url\_safety import is\_safe\_url

 if not is\_safe\_url(url):
 raise ValueError(f"Blocked unsafe URL: {url\[:80\]}")

 if not self.\_http\_client:
 return None

 try:
 resp = await self.\_http\_client.get(
 url,
 timeout=30.0,
 headers=self.\_qq\_media\_headers(),
 )
 resp.raise\_for\_status()
 data = resp.content
 except Exception as exc:
 logger.debug(
 "\[%s\] Download failed for %s: %s", self.\_log\_tag, url\[:80\], exc
 )
 return None

 if content\_type.startswith("image/"):
 ext = mimetypes.guess\_extension(content\_type) or ".jpg"
 return cache\_image\_from\_bytes(data, ext)
 elif content\_type == "voice" or content\_type.startswith("audio/"):
 # QQ voice messages are typically .amr or .silk format.
 # Convert to .wav using ffmpeg so STT engines can process it.
 return await self.\_convert\_audio\_to\_wav(data, url)
 else:
 filename = (
 original\_name
 or Path(urlparse(url).path).name
 or "qq\_attachment"
 )
 return cache\_document\_from\_bytes(data, filename)

 @staticmethod
 def \_is\_voice\_content\_type(content\_type: str, filename: str) -> bool:
 """Check if an attachment is a voice/audio message."""
 ct = content\_type.strip().lower()
 fn = filename.strip().lower()
 if ct == "voice" or ct.startswith("audio/"):
 return True
 \_VOICE\_EXTENSIONS = (
 ".silk",
 ".amr",
 ".mp3",
 ".wav",
 ".ogg",
 ".m4a",
 ".aac",
 ".speex",
 ".flac",
 )
 if any(fn.endswith(ext) for ext in \_VOICE\_EXTENSIONS):
 return True
 return False

 def \_qq\_media\_headers(self) -> Dict\[str, str\]:
 """Return Authorization headers for QQ multimedia CDN downloads.

 QQ's multimedia URLs (multimedia.nt.qq.com.cn) require the bot's
 access token in an Authorization header, otherwise the download
 returns a non-200 status.
 """
 if self.\_access\_token:
 return {"Authorization": f"QQBot {self.\_access\_token}"}
 return {}

 async def \_stt\_voice\_attachment(
 self,
 url: str,
 content\_type: str,
 filename: str,
 \*,
 asr\_refer\_text: Optional\[str\] = None,
 voice\_wav\_url: Optional\[str\] = None,
 ) -\> Optional\[str\]:
 """Download a voice attachment, convert to wav, and transcribe.

 Priority:
 1\. QQ's built-in \`\`asr\_refer\_text\`\` (Tencent's own ASR — free, no API call).
 2\. Self-hosted STT on \`\`voice\_wav\_url\`\` (pre-converted WAV from QQ, avoids SILK decoding).
 3\. Self-hosted STT on the original attachment URL (requires SILK→WAV conversion).

 Returns the transcript text, or None on failure.
 """
 # 1\. Use QQ's built-in ASR text if available
 if asr\_refer\_text:
 logger.debug(
 "\[%s\] STT: using QQ asr\_refer\_text: %r", self.\_log\_tag, asr\_refer\_text\[:100\]
 )
 return asr\_refer\_text

 # Determine which URL to download (prefer voice\_wav\_url — already WAV)
 download\_url = url
 is\_pre\_wav = False
 if voice\_wav\_url:
 if voice\_wav\_url.startswith("//"):
 voice\_wav\_url = f"https:{voice\_wav\_url}"
 download\_url = voice\_wav\_url
 is\_pre\_wav = True
 logger.debug("\[%s\] STT: using voice\_wav\_url (pre-converted WAV)", self.\_log\_tag)

 from tools.url\_safety import is\_safe\_url
 if not is\_safe\_url(download\_url):
 logger.warning("\[QQ\] STT blocked unsafe URL: %s", download\_url\[:80\])
 return None

 try:
 # 2\. Download audio (QQ CDN requires Authorization header)
 if not self.\_http\_client:
 logger.warning("\[%s\] STT: no HTTP client", self.\_log\_tag)
 return None

 download\_headers = self.\_qq\_media\_headers()
 logger.debug(
 "\[%s\] STT: downloading voice from %s (pre\_wav=%s, headers=%s)",
 self.\_log\_tag,
 download\_url\[:80\],
 is\_pre\_wav,
 bool(download\_headers),
 )
 resp = await self.\_http\_client.get(
 download\_url,
 timeout=30.0,
 headers=download\_headers,
 follow\_redirects=True,
 )
 resp.raise\_for\_status()
 audio\_data = resp.content
 logger.debug(
 "\[%s\] STT: downloaded %d bytes, content\_type=%s",
 self.\_log\_tag,
 len(audio\_data),
 resp.headers.get("content-type", "unknown"),
 )

 if len(audio\_data) < 10:
 logger.warning(
 "\[%s\] STT: downloaded data too small (%d bytes), skipping",
 self.\_log\_tag,
 len(audio\_data),
 )
 return None

 # 3\. Convert to wav (skip if we already have a pre-converted WAV)
 if is\_pre\_wav:
 import tempfile

 with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
 tmp.write(audio\_data)
 wav\_path = tmp.name
 logger.debug(
 "\[%s\] STT: using pre-converted WAV directly (%d bytes)",
 self.\_log\_tag,
 len(audio\_data),
 )
 else:
 logger.debug(
 "\[%s\] STT: converting to wav, filename=%r", self.\_log\_tag, filename
 )
 wav\_path = await self.\_convert\_audio\_to\_wav\_file(audio\_data, filename)
 if not wav\_path or not Path(wav\_path).exists():
 logger.warning(
 "\[%s\] STT: ffmpeg conversion produced no output", self.\_log\_tag
 )
 return None

 # 4\. Call STT API
 logger.debug("\[%s\] STT: calling ASR on %s", self.\_log\_tag, wav\_path)
 transcript = await self.\_call\_stt(wav\_path)

 # 5\. Cleanup temp file
 try:
 os.unlink(wav\_path)
 except OSError:
 pass

 if transcript:
 logger.debug("\[%s\] STT success: %r", self.\_log\_tag, transcript\[:100\])
 else:
 logger.warning("\[%s\] STT: ASR returned empty transcript", self.\_log\_tag)
 return transcript
 except (httpx.HTTPStatusError, httpx.TransportError, IOError) as exc:
 logger.warning(
 "\[%s\] STT failed for voice attachment: %s: %s",
 self.\_log\_tag,
 type(exc).\_\_name\_\_,
 exc,
 )
 return None

 async def \_convert\_audio\_to\_wav\_file(
 self, audio\_data: bytes, filename: str
 ) -\> Optional\[str\]:
 """Convert audio bytes to a temp .wav file using pilk (SILK) or ffmpeg.

 QQ voice messages are typically SILK format which ffmpeg cannot decode.
 Strategy: always try pilk first, fall back to ffmpeg if pilk fails.

 Returns the wav file path, or None on failure.
 """
 import tempfile

 ext = (
 Path(filename).suffix.lower()
 if Path(filename).suffix
 else self.\_guess\_ext\_from\_data(audio\_data)
 )
 logger.info(
 "\[%s\] STT: audio\_data size=%d, ext=%r, first\_20\_bytes=%r",
 self.\_log\_tag,
 len(audio\_data),
 ext,
 audio\_data\[:20\],
 )

 with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp\_src:
 tmp\_src.write(audio\_data)
 src\_path = tmp\_src.name

 wav\_path = src\_path.rsplit(".", 1)\[0\] + ".wav"

 # Try pilk first (handles SILK and many other formats)
 result = await self.\_convert\_silk\_to\_wav(src\_path, wav\_path)

 # If pilk failed, try ffmpeg
 if not result:
 result = await self.\_convert\_ffmpeg\_to\_wav(src\_path, wav\_path)

 # If ffmpeg also failed, try writing raw PCM as WAV (last resort)
 if not result:
 result = await self.\_convert\_raw\_to\_wav(audio\_data, wav\_path)

 # Cleanup source file
 try:
 os.unlink(src\_path)
 except OSError:
 pass

 return result

 @staticmethod
 def \_guess\_ext\_from\_data(data: bytes) -> str:
 """Guess file extension from magic bytes."""
 if data\[:9\] == b"#!SILK\_V3" or data\[:6\] == b"#!SILK":
 return ".silk"
 if data\[:2\] == b"\\x02!":
 return ".silk"
 if data\[:4\] == b"RIFF":
 return ".wav"
 if data\[:4\] == b"fLaC":
 return ".flac"
 if data\[:2\] in {b"\\xff\\xfb", b"\\xff\\xf3", b"\\xff\\xf2"}:
 return ".mp3"
 if data\[:4\] == b"\\x30\\x26\\xb2\\x75" or data\[:4\] == b"\\x4f\\x67\\x67\\x53":
 return ".ogg"
 if data\[:4\] == b"\\x00\\x00\\x00\\x20" or data\[:4\] == b"\\x00\\x00\\x00\\x1c":
 return ".amr"
 # Default to .amr for unknown (QQ's most common voice format)
 return ".amr"

 @staticmethod
 def \_looks\_like\_silk(data: bytes) -> bool:
 """Check if bytes look like a SILK audio file."""
 return data\[:6\] == b"#!SILK" or data\[:2\] == b"\\x02!" or data\[:9\] == b"#!SILK\_V3"

 async def \_convert\_silk\_to\_wav(self, src\_path: str, wav\_path: str) -> Optional\[str\]:
 """Convert audio file to WAV using the pilk library.

 Tries the file as-is first, then as .silk if the extension differs.
 pilk can handle SILK files with various headers (or no header).
 """
 try:
 import pilk
 except ImportError:
 logger.warning(
 "\[%s\] pilk not installed — cannot decode SILK audio. Run: pip install pilk",
 self.\_log\_tag,
 )
 return None

 # Try converting the file as-is
 try:
 pilk.silk\_to\_wav(src\_path, wav\_path, rate=16000)
 if Path(wav\_path).exists() and Path(wav\_path).stat().st\_size > 44:
 logger.debug(
 "\[%s\] pilk converted %s to wav (%d bytes)",
 self.\_log\_tag,
 Path(src\_path).name,
 Path(wav\_path).stat().st\_size,
 )
 return wav\_path
 except Exception as exc:
 logger.debug("\[%s\] pilk direct conversion failed: %s", self.\_log\_tag, exc)

 # Try renaming to .silk and converting (pilk checks the extension)
 silk\_path = src\_path.rsplit(".", 1)\[0\] + ".silk"
 try:
 import shutil

 shutil.copy2(src\_path, silk\_path)
 pilk.silk\_to\_wav(silk\_path, wav\_path, rate=16000)
 if Path(wav\_path).exists() and Path(wav\_path).stat().st\_size > 44:
 logger.debug(
 "\[%s\] pilk converted %s (as .silk) to wav (%d bytes)",
 self.\_log\_tag,
 Path(src\_path).name,
 Path(wav\_path).stat().st\_size,
 )
 return wav\_path
 except Exception as exc:
 logger.debug("\[%s\] pilk .silk conversion failed: %s", self.\_log\_tag, exc)
 finally:
 try:
 os.unlink(silk\_path)
 except OSError:
 pass

 return None

 async def \_convert\_raw\_to\_wav(self, audio\_data: bytes, wav\_path: str) -> Optional\[str\]:
 """Last resort: try writing audio data as raw PCM 16-bit mono 16kHz WAV.

 This will produce garbage if the data isn't raw PCM, but at least
 the ASR engine won't crash — it'll just return empty.
 """
 try:
 import wave

 with wave.open(wav\_path, "w") as wf:
 wf.setnchannels(1)
 wf.setsampwidth(2)
 wf.setframerate(16000)
 wf.writeframes(audio\_data)
 return wav\_path
 except Exception as exc:
 logger.debug("\[%s\] raw PCM fallback failed: %s", self.\_log\_tag, exc)
 return None

 async def \_convert\_ffmpeg\_to\_wav(self, src\_path: str, wav\_path: str) -> Optional\[str\]:
 """Convert audio file to WAV using ffmpeg."""
 try:
 proc = await asyncio.create\_subprocess\_exec(
 "ffmpeg",
 "-y",
 "-i",
 src\_path,
 "-ar",
 "16000",
 "-ac",
 "1",
 wav\_path,
 stdout=asyncio.subprocess.DEVNULL,
 stderr=asyncio.subprocess.PIPE,
 )
 await asyncio.wait\_for(proc.wait(), timeout=30)
 if proc.returncode != 0:
 stderr = await proc.stderr.read() if proc.stderr else b""
 logger.warning(
 "\[%s\] ffmpeg failed for %s: %s",
 self.\_log\_tag,
 Path(src\_path).name,
 stderr\[:200\].decode(errors="replace"),
 )
 return None
 except (asyncio.TimeoutError, FileNotFoundError) as exc:
 logger.warning("\[%s\] ffmpeg conversion error: %s", self.\_log\_tag, exc)
 return None

 if not Path(wav\_path).exists() or Path(wav\_path).stat().st\_size <= 44:
 logger.warning(
 "\[%s\] ffmpeg produced no/small output for %s",
 self.\_log\_tag,
 Path(src\_path).name,
 )
 return None
 logger.debug(
 "\[%s\] ffmpeg converted %s to wav (%d bytes)",
 self.\_log\_tag,
 Path(src\_path).name,
 Path(wav\_path).stat().st\_size,
 )
 return wav\_path

 def \_resolve\_stt\_config(self) -> Optional\[Dict\[str, str\]\]:
 """Resolve STT backend configuration from config/environment.

 Priority:
 1\. Plugin-specific: \`\`channels.qqbot.stt\`\` in config.yaml → \`\`self.config.extra\["stt"\]\`\`
 2\. QQ-specific env vars: \`\`QQ\_STT\_API\_KEY\`\` / \`\`QQ\_STT\_BASE\_URL\`\` / \`\`QQ\_STT\_MODEL\`\`
 3\. Return None if nothing is configured (STT will be skipped, QQ built-in ASR still works).
 """
 extra = self.config.extra or {}

 # 1\. Plugin-specific STT config (matches OpenClaw's channels.qqbot.stt)
 stt\_cfg = extra.get("stt")
 if isinstance(stt\_cfg, dict) and stt\_cfg.get("enabled") is not False:
 base\_url = stt\_cfg.get("baseUrl") or stt\_cfg.get("base\_url", "")
 api\_key = stt\_cfg.get("apiKey") or stt\_cfg.get("api\_key", "")
 model = stt\_cfg.get("model", "")
 if base\_url and api\_key:
 return {
 "base\_url": base\_url.rstrip("/"),
 "api\_key": api\_key,
 "model": model or "whisper-1",
 }
 # Provider-only config: just model name, use default provider
 if api\_key:
 provider = stt\_cfg.get("provider", "zai")
 # Map provider to base URL
 \_PROVIDER\_BASE\_URLS = {
 "zai": "https://open.bigmodel.cn/api/coding/paas/v4",
 "openai": "https://api.openai.com/v1",
 "glm": "https://open.bigmodel.cn/api/coding/paas/v4",
 }
 base\_url = \_PROVIDER\_BASE\_URLS.get(provider, "")
 if base\_url:
 return {
 "base\_url": base\_url,
 "api\_key": api\_key,
 "model": model
 or ("glm-asr" if provider in {"zai", "glm"} else "whisper-1"),
 }

 # 2\. QQ-specific env vars (set by \`hermes setup gateway\` / \`hermes gateway\`)
 qq\_stt\_key = os.getenv("QQ\_STT\_API\_KEY", "")
 if qq\_stt\_key:
 base\_url = os.getenv(
 "QQ\_STT\_BASE\_URL",
 "https://open.bigmodel.cn/api/coding/paas/v4",
 )
 model = os.getenv("QQ\_STT\_MODEL", "glm-asr")
 return {
 "base\_url": base\_url.rstrip("/"),
 "api\_key": qq\_stt\_key,
 "model": model,
 }

 return None

 async def \_call\_stt(self, wav\_path: str) -> Optional\[str\]:
 """Call an OpenAI-compatible STT API to transcribe a wav file.

 Uses the provider configured in \`\`channels.qqbot.stt\`\` config,
 falling back to QQ's built-in \`\`asr\_refer\_text\`\` if not configured.
 Returns None if STT is not configured or the call fails.
 """
 stt\_cfg = self.\_resolve\_stt\_config()
 if not stt\_cfg:
 logger.warning(
 "\[%s\] STT not configured (no stt config or QQ\_STT\_API\_KEY)",
 self.\_log\_tag,
 )
 return None

 base\_url = stt\_cfg\["base\_url"\]
 api\_key = stt\_cfg\["api\_key"\]
 model = stt\_cfg\["model"\]

 try:
 with open(wav\_path, "rb") as f:
 resp = await self.\_http\_client.post(
 f"{base\_url}/audio/transcriptions",
 headers={"Authorization": f"Bearer {api\_key}"},
 files={"file": (Path(wav\_path).name, f, "audio/wav")},
 data={"model": model},
 timeout=30.0,
 )
 resp.raise\_for\_status()
 result = resp.json()
 # Zhipu/GLM format: {"choices": \[{"message": {"content": "transcript text"}}\]}
 choices = result.get("choices", \[\])
 if choices:
 content = choices\[0\].get("message", {}).get("content", "")
 if content.strip():
 return content.strip()
 # OpenAI/Whisper format: {"text": "transcript text"}
 text = result.get("text", "")
 if text.strip():
 return text.strip()
 return None
 except (httpx.HTTPStatusError, IOError) as exc:
 logger.warning(
 "\[%s\] STT API call failed (model=%s, base=%s): %s",
 self.\_log\_tag,
 model,
 base\_url\[:50\],
 exc,
 )
 return None

 async def \_convert\_audio\_to\_wav(
 self, audio\_data: bytes, source\_url: str
 ) -\> Optional\[str\]:
 """Convert audio bytes to .wav using pilk (SILK) or ffmpeg, caching the result."""
 import tempfile

 # Determine source format from magic bytes or URL
 ext = (
 Path(urlparse(source\_url).path).suffix.lower()
 if urlparse(source\_url).path
 else ""
 )
 if not ext or ext not in {
 ".silk",
 ".amr",
 ".mp3",
 ".wav",
 ".ogg",
 ".m4a",
 ".aac",
 ".flac",
 }:
 ext = self.\_guess\_ext\_from\_data(audio\_data)

 with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp\_src:
 tmp\_src.write(audio\_data)
 src\_path = tmp\_src.name

 wav\_path = src\_path.rsplit(".", 1)\[0\] + ".wav"
 try:
 is\_silk = ext == ".silk" or self.\_looks\_like\_silk(audio\_data)
 if is\_silk:
 result = await self.\_convert\_silk\_to\_wav(src\_path, wav\_path)
 else:
 result = await self.\_convert\_ffmpeg\_to\_wav(src\_path, wav\_path)

 if not result:
 logger.warning(
 "\[%s\] audio conversion failed for %s (format=%s)",
 self.\_log\_tag,
 source\_url\[:60\],
 ext,
 )
 return cache\_document\_from\_bytes(audio\_data, f"qq\_voice{ext}")
 except Exception:
 return cache\_document\_from\_bytes(audio\_data, f"qq\_voice{ext}")
 finally:
 try:
 os.unlink(src\_path)
 except OSError:
 pass

 # Verify output and cache
 try:
 wav\_data = Path(wav\_path).read\_bytes()
 os.unlink(wav\_path)
 return cache\_document\_from\_bytes(wav\_data, "qq\_voice.wav")
 except Exception as exc:
 logger.debug("\[%s\] Failed to read converted wav: %s", self.\_log\_tag, exc)
 return None

 # ------------------------------------------------------------------
 # Outbound messaging — REST API
 # ------------------------------------------------------------------

 async def \_api\_request(
 self,
 method: str,
 path: str,
 body: Optional\[Dict\[str, Any\]\] = None,
 timeout: float = DEFAULT\_API\_TIMEOUT,
 ) -\> Dict\[str, Any\]:
 """Make an authenticated REST API request to QQ Bot API."""
 if not self.\_http\_client:
 raise RuntimeError("HTTP client not initialized — not connected?")

 token = await self.\_ensure\_token()
 headers = {
 "Authorization": f"QQBot {token}",
 "Content-Type": "application/json",
 "User-Agent": build\_user\_agent(),
 }

 try:
 resp = await self.\_http\_client.request(
 method,
 f"{API\_BASE}{path}",
 headers=headers,
 json=body,
 timeout=timeout,
 )
 data = resp.json()
 if resp.status\_code >= 400:
 raise RuntimeError(
 f"QQ Bot API error \[{resp.status\_code}\] {path}: "
 f"{data.get('message', data)}"
 )
 return data
 except httpx.TimeoutException as exc:
 raise RuntimeError(f"QQ Bot API timeout \[{path}\]: {exc}") from exc

 async def \_upload\_media(
 self,
 target\_type: str,
 target\_id: str,
 file\_type: int,
 url: Optional\[str\] = None,
 file\_data: Optional\[str\] = None,
 srv\_send\_msg: bool = False,
 file\_name: Optional\[str\] = None,
 ) -\> Dict\[str, Any\]:
 """Upload media and return file\_info."""
 path = (
 f"/v2/users/{target\_id}/files"
 if target\_type == "c2c"
 else f"/v2/groups/{target\_id}/files"
 )

 body: Dict\[str, Any\] = {
 "file\_type": file\_type,
 "srv\_send\_msg": srv\_send\_msg,
 }
 if url:
 body\["url"\] = url
 elif file\_data:
 body\["file\_data"\] = file\_data
 if file\_type == MEDIA\_TYPE\_FILE and file\_name:
 body\["file\_name"\] = file\_name

 # Retry transient upload failures
 for attempt in range(3):
 try:
 return await self.\_api\_request(
 "POST", path, body, timeout=FILE\_UPLOAD\_TIMEOUT
 )
 except RuntimeError as exc:
 err\_msg = str(exc)
 if any(
 kw in err\_msg
 for kw in ("400", "401", "Invalid", "timeout", "Timeout")
 ):
 raise
 if attempt < 2:
 await asyncio.sleep(1.5 \* (attempt + 1))
 else:
 raise

 # Maximum time (seconds) to wait for reconnection before giving up on send.
 \_RECONNECT\_WAIT\_SECONDS = 15.0
 # How often (seconds) to poll is\_connected while waiting.
 \_RECONNECT\_POLL\_INTERVAL = 0.5

 async def \_wait\_for\_reconnection(self) -> bool:
 """Wait for the WebSocket listener to reconnect.

 The listener loop (\_listen\_loop) auto-reconnects on disconnect, but
 there is a race window where send() is called right after a disconnect
 and before the reconnect completes. This method polls is\_connected
 for up to \_RECONNECT\_WAIT\_SECONDS.

 Returns True if reconnected, False if still disconnected.
 """
 logger.info("\[%s\] Not connected — waiting for reconnection (up to %.0fs)",
 self.\_log\_tag, self.\_RECONNECT\_WAIT\_SECONDS)
 waited = 0.0
 while waited < self.\_RECONNECT\_WAIT\_SECONDS:
 await asyncio.sleep(self.\_RECONNECT\_POLL\_INTERVAL)
 waited += self.\_RECONNECT\_POLL\_INTERVAL
 if self.is\_connected:
 logger.info("\[%s\] Reconnected after %.1fs", self.\_log\_tag, waited)
 return True
 logger.warning("\[%s\] Still not connected after %.0fs", self.\_log\_tag, self.\_RECONNECT\_WAIT\_SECONDS)
 return False

 async def send(
 self,
 chat\_id: str,
 content: str,
 reply\_to: Optional\[str\] = None,
 metadata: Optional\[Dict\[str, Any\]\] = None,
 ) -\> SendResult:
 """Send a text or markdown message to a QQ user or group.

 Applies format\_message(), splits long messages via truncate\_message(),
 and retries transient failures with exponential backoff.
 """
 del metadata

 if not self.is\_connected:
 if not await self.\_wait\_for\_reconnection():
 return SendResult(success=False, error="Not connected", retryable=True)

 if not content or not content.strip():
 return SendResult(success=True)

 formatted = self.format\_message(content)
 chunks = self.truncate\_message(formatted, self.MAX\_MESSAGE\_LENGTH)

 last\_result = SendResult(success=False, error="No chunks")
 for chunk in chunks:
 last\_result = await self.\_send\_chunk(chat\_id, chunk, reply\_to)
 if not last\_result.success:
 return last\_result
 # Only reply\_to the first chunk
 reply\_to = None
 return last\_result

 async def \_send\_chunk(
 self,
 chat\_id: str,
 content: str,
 reply\_to: Optional\[str\] = None,
 ) -\> SendResult:
 """Send a single chunk with retry + exponential backoff."""
 last\_exc: Optional\[Exception\] = None
 chat\_type = self.\_guess\_chat\_type(chat\_id)

 for attempt in range(3):
 try:
 if chat\_type == "c2c":
 return await self.\_send\_c2c\_text(chat\_id, content, reply\_to)
 elif chat\_type == "group":
 return await self.\_send\_group\_text(chat\_id, content, reply\_to)
 elif chat\_type == "guild":
 return await self.\_send\_guild\_text(chat\_id, content, reply\_to)
 else:
 return SendResult(
 success=False, error=f"Unknown chat type for {chat\_id}"
 )
 except Exception as exc:
 last\_exc = exc
 err = str(exc).lower()
 # Permanent errors — don't retry
 if any(
 k in err
 for k in ("invalid", "forbidden", "not found", "bad request")
 ):
 break
 # Transient — back off and retry
 if attempt < 2:
 delay = 1.0 \* (2 \*\* attempt)
 logger.warning(
 "\[%s\] send retry %d/3 after %.1fs: %s",
 self.\_log\_tag,
 attempt + 1,
 delay,
 exc,
 )
 await asyncio.sleep(delay)

 error\_msg = str(last\_exc) if last\_exc else "Unknown error"
 logger.error("\[%s\] Send failed: %s", self.\_log\_tag, error\_msg)
 retryable = not any(
 k in error\_msg.lower() for k in ("invalid", "forbidden", "not found")
 )
 return SendResult(success=False, error=error\_msg, retryable=retryable)

 async def \_send\_c2c\_text(
 self,
 openid: str,
 content: str,
 reply\_to: Optional\[str\] = None,
 keyboard: Optional\[InlineKeyboard\] = None,
 ) -\> SendResult:
 """Send text to a C2C user via REST API.

 :param keyboard: Optional inline keyboard attached to the message.
 """
 self.\_next\_msg\_seq(reply\_to or openid)
 body = self.\_build\_text\_body(content, reply\_to)
 if reply\_to:
 body\["msg\_id"\] = reply\_to
 if keyboard is not None:
 body\["keyboard"\] = keyboard.to\_dict()

 data = await self.\_api\_request("POST", f"/v2/users/{openid}/messages", body)
 msg\_id = str(data.get("id", uuid.uuid4().hex\[:12\]))
 return SendResult(success=True, message\_id=msg\_id, raw\_response=data)

 async def \_send\_group\_text(
 self,
 group\_openid: str,
 content: str,
 reply\_to: Optional\[str\] = None,
 keyboard: Optional\[InlineKeyboard\] = None,
 ) -\> SendResult:
 """Send text to a group via REST API.

 :param keyboard: Optional inline keyboard attached to the message.
 """
 self.\_next\_msg\_seq(reply\_to or group\_openid)
 body = self.\_build\_text\_body(content, reply\_to)
 if reply\_to:
 body\["msg\_id"\] = reply\_to
 if keyboard is not None:
 body\["keyboard"\] = keyboard.to\_dict()

 data = await self.\_api\_request(
 "POST", f"/v2/groups/{group\_openid}/messages", body
 )
 msg\_id = str(data.get("id", uuid.uuid4().hex\[:12\]))
 return SendResult(success=True, message\_id=msg\_id, raw\_response=data)

 async def \_send\_guild\_text(
 self, channel\_id: str, content: str, reply\_to: Optional\[str\] = None
 ) -\> SendResult:
 """Send text to a guild channel via REST API."""
 body: Dict\[str, Any\] = {"content": content\[: self.MAX\_MESSAGE\_LENGTH\]}
 if reply\_to:
 body\["msg\_id"\] = reply\_to

 data = await self.\_api\_request("POST", f"/channels/{channel\_id}/messages", body)
 msg\_id = str(data.get("id", uuid.uuid4().hex\[:12\]))
 return SendResult(success=True, message\_id=msg\_id, raw\_response=data)

 # ------------------------------------------------------------------
 # Inline-keyboard outbound helpers (approval / update-prompt flows)
 # ------------------------------------------------------------------

 async def send\_with\_keyboard(
 self,
 chat\_id: str,
 content: str,
 keyboard: InlineKeyboard,
 reply\_to: Optional\[str\] = None,
 ) -\> SendResult:
 """Send a single text message with an inline keyboard attached.

 Unlike :meth:\`send\`, this does NOT split long content into chunks —
 a keyboard message has exactly one interactive surface, and splitting
 would orphan the buttons from the first chunk. Callers should keep
 approval/update-prompt bodies short.

 Guild (channel) chats don't support inline keyboards; returns a
 non-retryable failure for those.
 """
 if not self.is\_connected:
 if not await self.\_wait\_for\_reconnection():
 return SendResult(
 success=False, error="Not connected", retryable=True
 )

 chat\_type = self.\_guess\_chat\_type(chat\_id)
 formatted = self.format\_message(content)
 truncated = formatted\[: self.MAX\_MESSAGE\_LENGTH\]
 try:
 if chat\_type == "c2c":
 return await self.\_send\_c2c\_text(
 chat\_id, truncated, reply\_to, keyboard=keyboard,
 )
 if chat\_type == "group":
 return await self.\_send\_group\_text(
 chat\_id, truncated, reply\_to, keyboard=keyboard,
 )
 return SendResult(
 success=False,
 error=(
 f"Inline keyboards not supported for chat\_type "
 f"{chat\_type!r}"
 ),
 retryable=False,
 )
 except Exception as exc:
 logger.error(
 "\[%s\] send\_with\_keyboard failed: %s", self.\_log\_tag, exc
 )
 return SendResult(success=False, error=str(exc))

 async def send\_approval\_request(
 self,
 chat\_id: str,
 req: ApprovalRequest,
 reply\_to: Optional\[str\] = None,
 ) -\> SendResult:
 """Send a 3-button approval request (\`\`allow-once / allow-always / deny\`\`).

 The rendered text comes from :func:\`build\_approval\_text\`; callers can
 override by passing a custom :class:\`ApprovalRequest\`.

 Users click the button → \`\`INTERACTION\_CREATE\`\` fires → the adapter's
 registered :meth:\`set\_interaction\_callback\` handler decodes
 \`\`button\_data\`\` via :func:\`parse\_approval\_button\_data\`.
 """
 from gateway.platforms.qqbot.keyboards import build\_approval\_text
 return await self.send\_with\_keyboard(
 chat\_id,
 build\_approval\_text(req),
 build\_approval\_keyboard(
 req.session\_key,
 allow\_permanent=getattr(req, "allow\_permanent", True),
 ),
 reply\_to=reply\_to,
 )

 # ------------------------------------------------------------------
 # Cross-adapter gateway contract — send\_exec\_approval + send\_update\_prompt
 # ------------------------------------------------------------------
 #
 # These mirror the signatures that gateway/run.py detects on the adapter
 # class (e.g. type(adapter).send\_exec\_approval, type(adapter).send\_update\_prompt)
 # for button-based approval / update-confirm UX. Discord, Telegram, Slack,
 # Matrix, and Feishu already implement the same contract.

 async def send\_exec\_approval(
 self,
 chat\_id: str,
 command: str,
 session\_key: str,
 description: str = "dangerous command",
 metadata: Optional\[Dict\[str, Any\]\] = None,
 allow\_permanent: bool = True,
 smart\_denied: bool = False,
 ) -\> SendResult:
 """Send a button-based exec-approval prompt for a dangerous command.

 Called by \`\`gateway/run.py\`\`'s \`\`\_approval\_notify\_sync\`\` when the
 agent is blocked waiting for approval. Button clicks resolve via
 :func:\`tools.approval.resolve\_gateway\_approval\` — dispatched by the
 adapter's interaction callback (:meth:\`\_default\_interaction\_dispatch\`).
 """
 del metadata # QQ doesn't have thread\_id / DM targeting overrides.
 if smart\_denied:
 description += " Owner override applies to this one operation only."

 # Use the reply-to message for passive-message context when we have one.
 # QQ requires a msg\_id on outbound messages to a user we've never
 # seen; the last inbound msg\_id is the natural choice.
 msg\_id = self.\_last\_msg\_id.get(chat\_id)

 req = ApprovalRequest(
 session\_key=session\_key,
 title="Execute this command?",
 description=description,
 command\_preview=command,
 timeout\_sec=self.\_APPROVAL\_TIMEOUT\_SECONDS,
 allow\_permanent=allow\_permanent and not smart\_denied,
 )
 return await self.send\_approval\_request(
 chat\_id, req, reply\_to=msg\_id,
 )

 \_APPROVAL\_TIMEOUT\_SECONDS = 300 # matches gateway's default gateway\_timeout

 async def send\_update\_prompt(
 self,
 chat\_id: str,
 prompt: str,
 default: str = "",
 session\_key: str = "",
 metadata: Optional\[Dict\[str, Any\]\] = None,
 ) -\> SendResult:
 """Send a Yes/No update-confirmation prompt with inline buttons.

 Matches the cross-adapter contract used by
 \`\`gateway/run.py\`\`'s \`\`hermes update --gateway\`\` watcher. Button
 clicks surface as \`\`INTERACTION\_CREATE\`\` with
 \`\`button\_data = 'update\_prompt:y'\`\` or \`\`'update\_prompt:n'\`\`;
 the adapter's interaction callback writes the answer to
 \`\`~/.hermes/.update\_response\`\` so the detached update process
 can read it.
 """
 del session\_key, metadata # present for contract parity only.

 default\_hint = f" (default: {default})" if default else ""
 content = f"⚕ \*\*Update Needs Your Input\*\*\\n\\n{prompt}{default\_hint}"
 msg\_id = self.\_last\_msg\_id.get(chat\_id)
 return await self.send\_with\_keyboard(
 chat\_id,
 content,
 build\_update\_prompt\_keyboard(),
 reply\_to=msg\_id,
 )

 def \_build\_text\_body(
 self, content: str, reply\_to: Optional\[str\] = None
 ) -\> Dict\[str, Any\]:
 """Build the message body for C2C/group text sending."""
 msg\_seq = self.\_next\_msg\_seq(reply\_to or "default")

 if self.\_markdown\_support:
 body: Dict\[str, Any\] = {
 "markdown": {"content": content\[: self.MAX\_MESSAGE\_LENGTH\]},
 "msg\_type": MSG\_TYPE\_MARKDOWN,
 "msg\_seq": msg\_seq,
 }
 else:
 body = {
 "content": content\[: self.MAX\_MESSAGE\_LENGTH\],
 "msg\_type": MSG\_TYPE\_TEXT,
 "msg\_seq": msg\_seq,
 }

 if reply\_to:
 # For non-markdown mode, add message\_reference
 if not self.\_markdown\_support:
 body\["message\_reference"\] = {"message\_id": reply\_to}

 return body

 # ------------------------------------------------------------------
 # Native media sending
 # ------------------------------------------------------------------

 async def send\_image(
 self,
 chat\_id: str,
 image\_url: str,
 caption: Optional\[str\] = None,
 reply\_to: Optional\[str\] = None,
 metadata: Optional\[Dict\[str, Any\]\] = None,
 ) -\> SendResult:
 """Send an image natively via QQ Bot API upload."""
 del metadata

 result = await self.\_send\_media(
 chat\_id, image\_url, MEDIA\_TYPE\_IMAGE, "image", caption, reply\_to
 )
 if result.success or not self.\_is\_url(image\_url):
 return result

 # Fallback to text URL
 logger.warning(
 "\[%s\] Image send failed, falling back to text: %s",
 self.\_log\_tag,
 result.error,
 )
 fallback = f"{caption}\\n{image\_url}" if caption else image\_url
 return await self.send(chat\_id=chat\_id, content=fallback, reply\_to=reply\_to)

 async def send\_image\_file(
 self,
 chat\_id: str,
 image\_path: str,
 caption: Optional\[str\] = None,
 reply\_to: Optional\[str\] = None,
 \*\*kwargs,
 ) -\> SendResult:
 """Send a local image file natively."""
 del kwargs
 return await self.\_send\_media(
 chat\_id, image\_path, MEDIA\_TYPE\_IMAGE, "image", caption, reply\_to
 )

 async def send\_voice(
 self,
 chat\_id: str,
 audio\_path: str,
 caption: Optional\[str\] = None,
 reply\_to: Optional\[str\] = None,
 \*\*kwargs,
 ) -\> SendResult:
 """Send a voice message natively."""
 del kwargs
 return await self.\_send\_media(
 chat\_id, audio\_path, MEDIA\_TYPE\_VOICE, "voice", caption, reply\_to
 )

 async def send\_video(
 self,
 chat\_id: str,
 video\_path: str,
 caption: Optional\[str\] = None,
 reply\_to: Optional\[str\] = None,
 \*\*kwargs,
 ) -\> SendResult:
 """Send a video natively."""
 del kwargs
 return await self.\_send\_media(
 chat\_id, video\_path, MEDIA\_TYPE\_VIDEO, "video", caption, reply\_to
 )

 async def send\_document(
 self,
 chat\_id: str,
 file\_path: str,
 caption: Optional\[str\] = None,
 file\_name: Optional\[str\] = None,
 reply\_to: Optional\[str\] = None,
 \*\*kwargs,
 ) -\> SendResult:
 """Send a file/document natively."""
 del kwargs
 return await self.\_send\_media(
 chat\_id,
 file\_path,
 MEDIA\_TYPE\_FILE,
 "file",
 caption,
 reply\_to,
 file\_name=file\_name,
 )

 async def \_send\_media(
 self,
 chat\_id: str,
 media\_source: str,
 file\_type: int,
 kind: str,
 caption: Optional\[str\] = None,
 reply\_to: Optional\[str\] = None,
 file\_name: Optional\[str\] = None,
 ) -\> SendResult:
 """Upload media and send as a native message.

 Upload strategy:

 \- \*\*HTTP(S) URLs\*\* → single \`\`POST /v2/{users\|groups}/{id}/files\`\`
 with \`\`url=...\`\`. The QQ platform fetches the URL directly; fastest
 path when the source is already hosted.
 \- \*\*Local files\*\* → three-step chunked upload (prepare / PUT parts /
 complete). Handles files up to the platform's ~100 MB per-file
 limit without the ~10 MB inline-base64 cap of the old adapter.
 """
 if not self.is\_connected:
 if not await self.\_wait\_for\_reconnection():
 return SendResult(success=False, error="Not connected", retryable=True)

 chat\_type = self.\_guess\_chat\_type(chat\_id)
 if chat\_type == "guild":
 # Guild channels don't support native media upload in the same way.
 return SendResult(
 success=False,
 error="Guild media send not supported via this path",
 )

 try:
 if self.\_is\_url(media\_source):
 # URL upload — let the platform fetch it directly.
 resolved\_name = (
 file\_name
 or Path(urlparse(media\_source).path).name
 or "media"
 )
 upload = await self.\_upload\_media(
 chat\_type,
 chat\_id,
 file\_type,
 url=media\_source,
 srv\_send\_msg=False,
 file\_name=resolved\_name if file\_type == MEDIA\_TYPE\_FILE else None,
 )
 else:
 # Local file — chunked upload (prepare / PUT parts / complete).
 resolved\_name, upload = await self.\_upload\_local\_file(
 chat\_type,
 chat\_id,
 media\_source,
 file\_type,
 file\_name,
 )

 file\_info = upload.get("file\_info") or (
 upload.get("data", {}) or {}
 ).get("file\_info")
 if not file\_info:
 return SendResult(
 success=False,
 error=f"Upload returned no file\_info: {upload}",
 )

 # Send media message
 msg\_seq = self.\_next\_msg\_seq(chat\_id)
 body: Dict\[str, Any\] = {
 "msg\_type": MSG\_TYPE\_MEDIA,
 "media": {"file\_info": file\_info},
 "msg\_seq": msg\_seq,
 }
 if caption:
 body\["content"\] = caption\[: self.MAX\_MESSAGE\_LENGTH\]
 if reply\_to:
 body\["msg\_id"\] = reply\_to

 send\_data = await self.\_api\_request(
 "POST",
 (
 f"/v2/users/{chat\_id}/messages"
 if chat\_type == "c2c"
 else f"/v2/groups/{chat\_id}/messages"
 ),
 body,
 )
 return SendResult(
 success=True,
 message\_id=str(send\_data.get("id", uuid.uuid4().hex\[:12\])),
 raw\_response=send\_data,
 )
 except UploadDailyLimitExceededError as exc:
 # Non-retryable: daily quota hit. Give the caller actionable text
 # so the model can compose a helpful reply.
 logger.warning(
 "\[%s\] Daily upload limit exceeded for %s (%s)",
 self.\_log\_tag, exc.file\_name, exc.file\_size\_human,
 )
 return SendResult(
 success=False,
 error=(
 f"QQ daily upload limit exceeded for {exc.file\_name!r} "
 f"({exc.file\_size\_human}). Retry tomorrow."
 ),
 retryable=False,
 )
 except UploadFileTooLargeError as exc:
 logger.warning(
 "\[%s\] File too large: %s (%s, platform limit %s)",
 self.\_log\_tag, exc.file\_name, exc.file\_size\_human, exc.limit\_human,
 )
 return SendResult(
 success=False,
 error=(
 f"{exc.file\_name!r} ({exc.file\_size\_human}) exceeds the "
 f"QQ per-file upload limit ({exc.limit\_human})."
 ),
 retryable=False,
 )
 except Exception as exc:
 logger.error("\[%s\] Media send failed: %s", self.\_log\_tag, exc)
 return SendResult(success=False, error=str(exc))

 async def \_upload\_local\_file(
 self,
 chat\_type: str,
 chat\_id: str,
 media\_source: str,
 file\_type: int,
 file\_name: Optional\[str\],
 ) -\> Tuple\[str, Dict\[str, Any\]\]:
 """Chunked-upload a local file and return \`\`(resolved\_name, complete\_response)\`\`.

 The returned \`\`complete\_response\`\` contains the \`\`file\_info\`\` token
 that goes into the subsequent RichMedia message body.

 :raises UploadDailyLimitExceededError: On biz\_code 40093002.
 :raises UploadFileTooLargeError: When the file exceeds the platform limit.
 :raises FileNotFoundError: If the path does not exist.
 :raises ValueError: If the path looks like a placeholder (\`\`\`\`).
 :raises RuntimeError: If the HTTP client is not initialized.
 """
 if not self.\_http\_client:
 raise RuntimeError("HTTP client not initialized — not connected?")

 local\_path = Path(media\_source).expanduser()
 if not local\_path.is\_absolute():
 local\_path = (Path.cwd() / local\_path).resolve()

 if not local\_path.exists() or not local\_path.is\_file():
 if media\_source.startswith("<") or len(media\_source) < 3:
 raise ValueError(
 f"Invalid media source (looks like a placeholder): {media\_source!r}"
 )
 raise FileNotFoundError(f"Media file not found: {local\_path}")

 resolved\_name = file\_name or local\_path.name
 uploader = ChunkedUploader(
 api\_request=self.\_api\_request,
 http\_put=self.\_http\_client.put,
 log\_tag=self.\_log\_tag,
 )
 complete = await uploader.upload(
 chat\_type=chat\_type,
 target\_id=chat\_id,
 file\_path=str(local\_path),
 file\_type=file\_type,
 file\_name=resolved\_name,
 )
 return resolved\_name, complete

 async def \_load\_media(
 self, source: str, file\_name: Optional\[str\] = None
 ) -\> Tuple\[str, str, str\]:
 """Load media from URL or local path. Returns (base64\_or\_url, content\_type, filename)."""
 source = str(source).strip()
 if not source:
 raise ValueError("Media source is required")

 parsed = urlparse(source)
 if parsed.scheme in {"http", "https"}:
 # For URLs, pass through directly to the upload API
 content\_type = mimetypes.guess\_type(source)\[0\] or "application/octet-stream"
 resolved\_name = file\_name or Path(parsed.path).name or "media"
 return source, content\_type, resolved\_name

 # Local file — encode as raw base64 for QQ Bot API file\_data field.
 # The QQ API expects plain base64, NOT a data URI.
 local\_path = Path(source).expanduser()
 if not local\_path.is\_absolute():
 local\_path = (Path.cwd() / local\_path).resolve()

 if not local\_path.exists() or not local\_path.is\_file():
 # Guard against placeholder paths like "" that the LLM
 # sometimes emits instead of real file paths.
 if source.startswith("<") or len(source) < 3:
 raise ValueError(
 f"Invalid media source (looks like a placeholder): {source!r}"
 )
 raise FileNotFoundError(f"Media file not found: {local\_path}")

 raw = local\_path.read\_bytes()
 resolved\_name = file\_name or local\_path.name
 content\_type = (
 mimetypes.guess\_type(str(local\_path))\[0\] or "application/octet-stream"
 )
 b64 = base64.b64encode(raw).decode("ascii")
 return b64, content\_type, resolved\_name

 # ------------------------------------------------------------------
 # Typing indicator
 # ------------------------------------------------------------------

 async def send\_typing(self, chat\_id: str, metadata=None) -> None:
 """Send an input notify to a C2C user (only supported for C2C).

 Debounced to one request per ~50s (the API sets a 60s indicator).
 The QQ API requires the originating message ID — retrieved from
 \`\`\_last\_msg\_id\`\` which is populated by \`\`\_on\_message\`\`.
 """
 if not self.is\_connected:
 return

 chat\_type = self.\_guess\_chat\_type(chat\_id)
 if chat\_type != "c2c":
 return

 msg\_id = self.\_last\_msg\_id.get(chat\_id)
 if not msg\_id:
 return

 # Debounce — skip if we sent recently
 now = time.time()
 last\_sent = self.\_typing\_sent\_at.get(chat\_id, 0.0)
 if now - last\_sent < self.\_TYPING\_DEBOUNCE\_SECONDS:
 return

 try:
 msg\_seq = self.\_next\_msg\_seq(chat\_id)
 body = {
 "msg\_type": MSG\_TYPE\_INPUT\_NOTIFY,
 "msg\_id": msg\_id,
 "input\_notify": {
 "input\_type": 1,
 "input\_second": self.\_TYPING\_INPUT\_SECONDS,
 },
 "msg\_seq": msg\_seq,
 }
 await self.\_api\_request("POST", f"/v2/users/{chat\_id}/messages", body)
 self.\_typing\_sent\_at\[chat\_id\] = now
 except Exception as exc:
 logger.debug("\[%s\] send\_typing failed: %s", self.\_log\_tag, exc)

 # ------------------------------------------------------------------
 # Format
 # ------------------------------------------------------------------

 def format\_message(self, content: str) -> str:
 """Format message for QQ.

 When markdown\_support is enabled, content is sent as-is (QQ renders it).
 When disabled, strip markdown via shared helper (same as BlueBubbles/SMS).
 """
 if self.\_markdown\_support:
 return content
 return strip\_markdown(content)

 # ------------------------------------------------------------------
 # Chat info
 # ------------------------------------------------------------------

 async def get\_chat\_info(self, chat\_id: str) -> Dict\[str, Any\]:
 """Return chat info based on chat type heuristics."""
 chat\_type = self.\_guess\_chat\_type(chat\_id)
 return {
 "name": chat\_id,
 "type": "group" if chat\_type in {"group", "guild"} else "dm",
 }

 # ------------------------------------------------------------------
 # Helpers
 # ------------------------------------------------------------------

 @staticmethod
 def \_is\_url(source: str) -> bool:
 return urlparse(str(source)).scheme in {"http", "https"}

 def \_guess\_chat\_type(self, chat\_id: str) -> str:
 """Determine chat type from stored inbound metadata, fallback to 'c2c'."""
 if chat\_id in self.\_chat\_type\_map:
 return self.\_chat\_type\_map\[chat\_id\]
 return "c2c"

 @staticmethod
 def \_strip\_at\_mention(content: str) -> str:
 """Strip the @bot mention prefix from group message content."""
 # QQ group @-messages may have the bot's QQ/ID as prefix
 import re

 stripped = re.sub(r"^@\\S+\\s\*", "", content.strip())
 return stripped

 def \_open\_dm\_opted\_in(self) -> bool:
 if os.getenv("GATEWAY\_ALLOW\_ALL\_USERS", "").lower() in {"true", "1", "yes"}:
 return True
 return os.getenv("QQ\_ALLOW\_ALL\_USERS", "").lower() in {"true", "1", "yes"}

 def \_is\_dm\_allowed(self, user\_id: str) -> bool:
 if self.\_dm\_policy == "disabled":
 return False
 if self.\_dm\_policy == "allowlist":
 return self.\_entry\_matches(self.\_allow\_from, user\_id)
 if self.\_dm\_policy == "open":
 return self.\_open\_dm\_opted\_in()
 return False

 def \_is\_dm\_intake\_allowed(self, user\_id: str) -> bool:
 principal = str(user\_id or "").strip()
 if not principal:
 return False
 if self.\_dm\_policy == "disabled":
 return False
 if self.\_dm\_policy == "allowlist":
 return self.\_entry\_matches(self.\_allow\_from, principal)
 if self.\_dm\_policy == "pairing":
 return True
 if self.\_dm\_policy == "open":
 return self.\_open\_dm\_opted\_in()
 return False

 def \_is\_group\_allowed(self, group\_id: str, user\_id: str) -> bool:
 if self.\_group\_policy == "disabled":
 return False
 if self.\_group\_policy == "allowlist":
 return self.\_entry\_matches(self.\_group\_allow\_from, group\_id)
 if self.\_group\_policy == "pairing":
 return False
 if self.\_group\_policy == "open":
 return True
 return False

 @staticmethod
 def \_entry\_matches(entries: List\[str\], target: str) -> bool:
 normalized\_target = str(target).strip().lower()
 for entry in entries:
 normalized = str(entry).strip().lower()
 if normalized == "\*" or normalized == normalized\_target:
 return True
 return False

 def \_parse\_qq\_timestamp(self, raw: str) -> datetime:
 """Parse QQ API timestamp (ISO 8601 string or integer ms).

 The QQ API changed from integer milliseconds to ISO 8601 strings.
 This handles both formats gracefully.
 """
 if not raw:
 return datetime.now(tz=timezone.utc)
 try:
 return datetime.fromisoformat(raw)
 except (ValueError, TypeError):
 pass
 try:
 return datetime.fromtimestamp(int(raw) / 1000, tz=timezone.utc)
 except (ValueError, TypeError):
 pass
 return datetime.now(tz=timezone.utc)

 def \_is\_duplicate(self, msg\_id: str) -> bool:
 now = time.time()
 if len(self.\_seen\_messages) > DEDUP\_MAX\_SIZE:
 cutoff = now - DEDUP\_WINDOW\_SECONDS
 self.\_seen\_messages = {
 key: ts for key, ts in self.\_seen\_messages.items() if ts > cutoff
 }
 if msg\_id in self.\_seen\_messages:
 return True
 self.\_seen\_messages\[msg\_id\] = now
 return False