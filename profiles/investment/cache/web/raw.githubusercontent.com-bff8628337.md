"""Pre-trade enforcement gate (SPEC.md Mandate Enforcement §3).

:class:\`LiveOrderGuardTool\` is the dedicated wrapper that owns the live-order
gate. It subclasses :class:\`~src.tools.mcp.MCPRemoteTool\` and is instantiated
only for a broker's order-placing (WRITE/UNKNOWN) remote tools; every read tool
keeps the untouched plain \`\`MCPRemoteTool.execute()\`\` path with no gate.

On every \`\`execute()\`\` it runs, in order and \*\*all fail-closed\*\* before any
broker call:

1\. \`\`load\_mandate\`\` — no valid mandate / unknown schema version → DENY.
2\. expiry — past \`\`consent.expires\_at\`\` → DENY (routes to re-auth).
3\. \`\`halt\_flag\_set\`\` — kill switch tripped → DENY, NO remote call.
4\. \`\`extract\_order\_intent\`\` — unparseable order → DENY.
5\. read positions + balance via the broker's READ MCP tools (plain path).
6\. \`\`check\_mandate\`\` — ALLOW (forward via \`\`super().execute\`\`) / DENY
 (structural: universe\|instrument) / PAUSE\_FOR\_REAUTH (quantitative).

The daily \`\`trade\_counter.json\`\` is incremented only on a confirmed ALLOW whose
forwarded broker result is \*\*non-error\*\* (\`\`MCPServerAdapter.call\_tool\`\` returns
an error envelope, it does not raise — a failed forward never placed an order and
never consumes a count), with UTC-date rollover. Every decision writes one
live-action audit event via :func:\`src.live.audit.write\_live\_action\`, and the
returned tool\_result carries that redacted record under the frozen
\`\`"live\_action"\`\` key so the api\_server SSE relay can emit a \`\`live.action\`\`
event without touching the agent loop.

When the order is sized by \`\`quantity\`\`, the gate derives a live quote (the
broker-specific quote READ tool first, then the data loaders) and enforces the
LARGER of the explicit notional and \`\`quantity\`\` × price — fail-closed DENY when
no quote is obtainable — so the notional/exposure/leverage caps stay enforceable.

\`\`repeatable = False\`\` mirrors the no-retry stance in
\`\`MCPServerAdapter.\_call\_tool\`\` — a live order must never be silently re-issued.
"""

from \_\_future\_\_ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

from src.config.accessor import get\_env\_config
from src.live.advisory import (
 AdvisoryContext,
 AdvisoryOrchestrator,
 Verdict,
 get\_advisory\_providers,
)
from src.live.audit import LiveActionEvent, write\_live\_action
from src.live.enforcement import (
 BREACH\_KIND\_INSTRUMENT,
 BREACH\_KIND\_UNIVERSE,
 BreachEvent,
 OrderIntent,
 check\_mandate,
 instrument\_asset\_class,
 last\_price\_usd,
)
from src.live.extractors import get\_extractor
from src.live.halt import halt\_flag\_set
from src.live.mandate.model import MANDATE\_SCHEMA\_VERSION, Mandate
from src.live.mandate.store import load\_mandate
from src.live.daily\_count import increment\_daily\_count, read\_daily\_count
from src.tools.mcp import MCPRemoteTool, MCPRemoteToolSpec, MCPServerAdapter

logger = logging.getLogger(\_\_name\_\_)

#: Frozen marker key the api\_server SSE relay reads off the returned tool\_result
#: to emit a \`\`live.action\`\` event without touching the agent loop.
LIVE\_ACTION\_RESULT\_KEY = "live\_action"

#: Fallback READ tools the gate uses to snapshot positions/balance and live
#: quotes. Connector mappings in \`\`src.trading\`\` override these when available.
\_POSITIONS\_TOOLS = ("get\_positions",)
\_BALANCE\_TOOLS = ("get\_account",)
\_QUOTE\_TOOLS = ("get\_quotes",)

\_DECISION\_ALLOW = "allow"
\_DECISION\_DENY = "deny"
\_DECISION\_PAUSE = "pause\_for\_reauth"

#: Environment variable controlling advisory review activation.
#: Truthy values (case-insensitive): \`\`"1"\`\`, \`\`"true"\`\`, \`\`"yes"\`\`.
#: Default: off (advisory layer is purely observational and opt-in).
\_ADVISORY\_ENABLED\_ENV = "VIBE\_TRADING\_ENABLE\_ADVISORY"
\_ADVISORY\_TRUTHY = frozenset({"1", "true", "yes"})

class LiveOrderGuardTool(MCPRemoteTool):
 """Mandate-enforcing wrapper for a broker's order-placing remote tool."""

 repeatable = False
 is\_readonly = False

 def \_\_init\_\_(
 self,
 adapter: MCPServerAdapter,
 spec: MCPRemoteToolSpec,
 \*,
 broker: str \| None = None,
 session\_id: str = "",
 ) -\> None:
 """Initialize the gate wrapper.

 Args:
 adapter: Adapter used to invoke the remote server (read + write).
 spec: Resolved local metadata for the order-placing remote tool.
 broker: Broker key for mandate/counter/halt lookups. Defaults to the
 spec's \`\`server\_name\`\` (the channel is keyed by broker, e.g.
 \`\`"robinhood"\`\`).
 session\_id: Originating session id, stamped onto audit events.
 """
 super().\_\_init\_\_(adapter, spec)
 self.broker = (broker or spec.server\_name or "").strip().lower()
 self.session\_id = session\_id

 @property
 def remote\_name(self) -> str:
 """The broker's un-prefixed remote tool name (e.g. \`\`place\_order\`\`)."""
 return self.\_spec.remote\_name

 def execute(self, \*\*kwargs: Any) -> str:
 """Run the pre-trade gate, then ALLOW / DENY / PAUSE the order.

 Args:
 \*\*kwargs: Order-tool arguments from the agent loop.

 Returns:
 JSON string: on ALLOW, the forwarded broker result; otherwise a
 structured refusal envelope (\`\`status: "blocked"\`\`) carrying the
 decision and, for quantitative breaches, the :class:\`BreachEvent\`.
 """
 mandate = load\_mandate(self.broker)
 if mandate is None or mandate.schema\_version != MANDATE\_SCHEMA\_VERSION:
 return self.\_deny(
 reason="no valid mandate on file",
 checked=\["mandate"\],
 mandate=mandate,
 )

 if self.\_is\_expired(mandate):
 return self.\_deny(
 reason="mandate expired — re-authorize",
 checked=\["mandate", "expiry"\],
 mandate=mandate,
 reauth=True,
 )

 if halt\_flag\_set(self.broker):
 return self.\_deny(
 reason="live trading halted",
 checked=\["mandate", "expiry", "halt\_flag"\],
 mandate=mandate,
 )

 extractor = get\_extractor(self.broker)
 intent = extractor(self.remote\_name, kwargs) if extractor is not None else None
 if intent is None:
 return self.\_deny(
 reason="order intent could not be parsed",
 checked=\["mandate", "expiry", "halt\_flag", "intent"\],
 mandate=mandate,
 )

 # Reconcile any quantity into a single authoritative notional BEFORE the
 # mandate checks so a {notional\_usd, quantity} pair can't bypass the
 # notional cap (H3) and a quantity-only order stays cap-enforceable (H4).
 intent = self.\_normalize\_intent\_notional(intent)
 if intent is None:
 return self.\_deny(
 reason="quantity order notional could not be priced (fail-closed)",
 checked=\["mandate", "expiry", "halt\_flag", "intent", "quote"\],
 mandate=mandate,
 )

 positions = self.\_read\_first(self.\_read\_tools("positions", \_POSITIONS\_TOOLS))
 balance = self.\_read\_first(self.\_read\_tools("account", \_BALANCE\_TOOLS))
 daily\_count = self.\_read\_daily\_count()

 breach = check\_mandate(
 mandate,
 intent,
 positions,
 balance,
 broker=self.broker,
 remote\_tool=self.remote\_name,
 daily\_count=daily\_count,
 )

 if breach is None:
 return self.\_allow(
 mandate=mandate, intent=intent, kwargs=kwargs,
 positions=positions, balance=balance,
 )

 if breach.kind in (BREACH\_KIND\_UNIVERSE, BREACH\_KIND\_INSTRUMENT):
 return self.\_deny\_breach(breach, mandate=mandate, intent=intent, reauth=False)
 return self.\_deny\_breach(breach, mandate=mandate, intent=intent, reauth=True)

 # \-\- intent normalization (quantity → notional) -------------------------

 def \_normalize\_intent\_notional(self, intent: OrderIntent) -> OrderIntent \| None:
 """Stamp a single authoritative \`\`notional\_usd\`\` onto the intent.

 Closes two bypasses (SPEC §4):

 \\* \*\*H3\*\* — an order carrying BOTH \`\`notional\_usd\`\` and \`\`quantity\`\` is
 enforced on the LARGER of (explicit notional, \`\`quantity\`\` × live
 price), so a small notional can't smuggle a huge quantity past the
 notional / exposure / leverage math.
 \\* \*\*H4\*\* — a quantity-only order derives its notional from a live quote
 so the notional cap stays enforceable.

 Fail-closed: when \`\`quantity\`\` is present but NO quote can be obtained
 from the broker quote tool or any data loader, the order is DENIED
 (returns \`\`None\`\`) rather than waved through. When no \`\`quantity\`\` is
 present the intent passes through unchanged (its explicit notional, if
 any, is validated downstream).

 Args:
 intent: The extractor's normalized intent.

 Returns:
 A new :class:\`OrderIntent\` with \`\`notional\_usd\`\` set to the enforced
 value, or \`\`None\`\` when a quantity order cannot be priced.
 """
 if intent.quantity is None:
 return intent

 price = self.\_quote\_price(intent)
 if price is None:
 return None
 implied = intent.quantity \* price
 if implied != implied or implied <= 0: # NaN / non-positive → fail-closed
 return None

 explicit = intent.notional\_usd if intent.notional\_usd is not None else 0.0
 enforced = max(float(explicit), implied)
 return OrderIntent(
 symbol=intent.symbol,
 side=intent.side,
 notional\_usd=enforced,
 quantity=intent.quantity,
 instrument\_type=intent.instrument\_type,
 )

 def \_quote\_price(self, intent: OrderIntent) -> float \| None:
 """Return a live USD price for the intent's symbol, fail-closed.

 Prefers the broker's mapped READ quote tool so the price is the broker's
 own; falls back to Vibe-Trading's data loaders
 (:func:\`src.live.enforcement.last\_price\_usd\`, standard auto-fallback)
 when the broker quote is unavailable. Returns \`\`None\`\` when no source
 yields a usable price.

 Args:
 intent: The order intent whose symbol is priced.

 Returns:
 A positive USD price, or \`\`None\`\` (→ fail-closed DENY upstream).
 """
 broker\_price = self.\_broker\_quote\_price(intent.symbol)
 if broker\_price is not None:
 return broker\_price
 asset\_class = instrument\_asset\_class(intent.instrument\_type)
 if asset\_class is None:
 return None
 try:
 return last\_price\_usd(intent.symbol, asset\_class)
 except Exception as exc: # loader chain failure → fail-closed
 logger.warning("loader quote failed for %s: %s", intent.symbol, exc)
 return None

 def \_broker\_quote\_price(self, symbol: str) -> float \| None:
 """Read a USD price for \`\`symbol\`\` from the broker's quote tool.

 Calls the ungated read path (never the guard) for the mapped quote tool
 with the symbol argument and parses a price from the common envelope shapes.
 Returns \`\`None\`\` on any error envelope, missing field, or unparseable
 value — the caller then falls back to the data loaders.

 Args:
 symbol: Normalized upper-case symbol.

 Returns:
 A positive USD price, or \`\`None\`\`.
 """
 for remote in self.\_read\_tools("quote", \_QUOTE\_TOOLS):
 try:
 result = self.\_adapter.call\_tool(
 remote, {"symbol": symbol}, local\_name=remote
 )
 except Exception as exc:
 logger.warning("broker quote tool %s failed: %s", remote, exc)
 continue
 if isinstance(result, dict) and result.get("status") == "error":
 continue
 price = \_parse\_quote\_price(result, symbol)
 if price is not None:
 return price
 return None

 # \-\- decision helpers ---------------------------------------------------

 def \_allow(
 self,
 \*,
 mandate: Mandate,
 intent: OrderIntent,
 kwargs: dict,
 positions: object = None,
 balance: object = None,
 ) -\> str:
 """Forward the order unchanged; consume a count + audit only on success.

 \`\`MCPServerAdapter.call\_tool\`\` does NOT raise on broker/network failure —
 it returns a \`\`{"status": "error", ...}\`\` envelope. So the gate inspects
 the forwarded payload (H2):

 \\* \*\*non-error\*\* → increment the daily counter and audit
 \`\`kind="order\_placed"\`\` / \`\`outcome="accepted"\`\`.
 \\* \*\*error envelope\*\* → audit \`\`kind="order\_rejected"\`\` /
 \`\`outcome="error"\`\` and do NOT consume a daily count (a failed forward
 never placed an order).

 Either way the returned tool\_result carries the redacted audit record
 under :data:\`LIVE\_ACTION\_RESULT\_KEY\` so the api\_server SSE relay can emit
 a \`\`live.action\`\` event without touching the agent loop (H5).
 """
 advisory = self.\_advisory\_review(intent, positions, balance, mandate)
 forwarded = super().execute(\*\*kwargs)
 broker\_response = self.\_safe\_json(forwarded)
 is\_error = self.\_is\_error\_envelope(broker\_response)

 checked = \[\
 "mandate", "expiry", "halt\_flag", "intent",\
 "exclude\_symbols", "allowed\_instruments", "asset\_classes",\
 "max\_order\_notional\_usd", "max\_total\_exposure\_usd",\
 "max\_leverage", "max\_trades\_per\_day", "account\_funding\_usd",\
 "universe\_floors",\
 \]
 if advisory is not None:
 checked.append("advisory")
 gate\_decision: dict\[str, Any\] = {
 "allowed": True,
 "decision": \_DECISION\_ALLOW,
 "checked\_limits": checked,
 "advisory": advisory,
 }
 if is\_error:
 record = self.\_audit(
 kind="order\_rejected",
 outcome="error",
 mandate=mandate,
 intent=intent,
 broker\_request=dict(kwargs),
 broker\_response=broker\_response,
 gate\_decision=gate\_decision,
 error=self.\_error\_message(broker\_response),
 )
 else:
 # Only a confirmed ALLOW + non-error forward consumes a daily count.
 self.\_increment\_daily\_count()
 record = self.\_audit(
 kind="order\_placed",
 outcome="accepted",
 mandate=mandate,
 intent=intent,
 broker\_request=dict(kwargs),
 broker\_response=broker\_response,
 gate\_decision=gate\_decision,
 )
 return self.\_embed\_live\_action(forwarded, record)

 # \-\- advisory review (observational, never blocks) ----------------------

 def \_advisory\_review(
 self,
 intent: OrderIntent,
 positions: object,
 balance: object,
 mandate: Mandate,
 ) -\> dict \| None:
 """Run advisory providers if enabled; return verdict dict or None.

 Returns None when advisory is disabled or no providers are configured.
 Returns a dict with \`\`verdict\`\`, \`\`concerns\`\`, \`\`results\`\` keys otherwise.
 Never raises — all exceptions are caught and converted to
 REVIEW\_UNAVAILABLE.
 """
 if not get\_env\_config().agent\_tuning.vibe\_trading\_enable\_advisory:
 return None

 providers = get\_advisory\_providers()
 if not providers:
 logger.info(
 "advisory enabled but no providers registered — skipping review"
 )
 return None

 try:
 from src.live.enforcement import (
 account\_balance\_market\_value,
 coerce\_position\_rows,
 positions\_market\_value,
 )

 equity = account\_balance\_market\_value(balance) or 0.0
 exposure = positions\_market\_value(positions) or 0.0
 funding\_usd = mandate.hard\_caps.account\_funding\_usd

 if equity > 0 and funding\_usd > 0:
 utilization = max(0.0, 1.0 - equity / funding\_usd)
 else:
 utilization = 0.0

 pos\_rows = coerce\_position\_rows(positions)
 open\_count = len(pos\_rows) if pos\_rows is not None else 0

 context = AdvisoryContext(
 symbol=intent.symbol,
 side=intent.side,
 notional\_usd=intent.notional\_usd or 0.0,
 account\_equity=equity,
 utilization\_ratio=utilization,
 open\_position\_count=open\_count,
 total\_exposure\_usd=exposure,
 funding\_usd=funding\_usd,
 )

 orchestrator = AdvisoryOrchestrator(providers)
 aggregated = orchestrator.review(context)
 return {
 "verdict": aggregated.verdict.value,
 "concerns": list(aggregated.all\_concerns),
 "results": \[\
 {\
 "verdict": r.verdict.value,\
 "summary": r.summary,\
 "concerns": list(r.concerns),\
 "provider": r.provider,\
 "confidence": r.confidence,\
 }\
 for r in aggregated.results\
 \],
 }
 except Exception as exc:
 logger.warning("advisory review failed: %s", exc, exc\_info=True)
 return {
 "verdict": Verdict.REVIEW\_UNAVAILABLE.value,
 "concerns": \[\],
 "error": type(exc).\_\_name\_\_,
 }

 def \_deny(
 self,
 \*,
 reason: str,
 checked: list\[str\],
 mandate: Mandate \| None,
 reauth: bool = False,
 ) -\> str:
 """Audit + return a refusal envelope for a pre-intent / structural DENY."""
 record = self.\_audit(
 kind="order\_rejected",
 outcome="blocked",
 mandate=mandate,
 intent=None,
 broker\_request=None,
 broker\_response=None,
 gate\_decision={"allowed": False, "decision": \_DECISION\_DENY, "checked\_limits": checked},
 error=reason,
 )
 return self.\_refusal(
 decision=\_DECISION\_DENY, reason=reason, reauth=reauth, record=record
 )

 def \_deny\_breach(
 self,
 breach: BreachEvent,
 \*,
 mandate: Mandate,
 intent: OrderIntent,
 reauth: bool,
 ) -\> str:
 """Audit + return a refusal for a \`\`check\_mandate\`\` breach.

 Structural breaches (\`\`reauth=False\`\`) DENY outright; quantitative
 breaches (\`\`reauth=True\`\`) PAUSE for re-authorization and surface the
 full :class:\`BreachEvent\` so the consent layer can render a widen-prompt.
 """
 decision = \_DECISION\_PAUSE if reauth else \_DECISION\_DENY
 record = self.\_audit(
 kind="breach",
 outcome="blocked",
 mandate=mandate,
 intent=intent,
 broker\_request=None,
 broker\_response=None,
 gate\_decision={
 "allowed": False,
 "decision": decision,
 "limit": breach.limit,
 "kind": breach.kind,
 "limit\_value": breach.limit\_value,
 "attempted\_value": breach.attempted\_value,
 },
 error=breach.detail or f"order breaches {breach.limit}",
 )
 return self.\_refusal(
 decision=decision,
 reason=breach.detail or f"order breaches {breach.limit}",
 reauth=reauth,
 breach=breach,
 record=record,
 )

 def \_refusal(
 self,
 \*,
 decision: str,
 reason: str,
 reauth: bool,
 breach: BreachEvent \| None = None,
 record: dict \| None = None,
 ) -\> str:
 """Build the structured refusal envelope returned to the agent loop."""
 payload: dict\[str, Any\] = {
 "status": "blocked",
 "decision": decision,
 "reason": reason,
 "broker": self.broker,
 "remote\_tool": self.remote\_name,
 "requires\_reauthorization": reauth,
 }
 if record is not None:
 payload\[LIVE\_ACTION\_RESULT\_KEY\] = record
 if breach is not None:
 payload\["breach"\] = {
 "broker": breach.broker,
 "limit": breach.limit,
 "limit\_value": breach.limit\_value,
 "attempted\_value": breach.attempted\_value,
 "overage": breach.overage,
 "remote\_tool": breach.remote\_tool,
 "created\_at": breach.created\_at,
 "kind": breach.kind,
 "detail": breach.detail,
 "proposed\_action": {
 "symbol": breach.proposed\_action.symbol,
 "side": breach.proposed\_action.side,
 "notional\_usd": breach.proposed\_action.notional\_usd,
 "quantity": breach.proposed\_action.quantity,
 "instrument\_type": breach.proposed\_action.instrument\_type.value,
 },
 }
 return json.dumps(payload, ensure\_ascii=False)

 # \-\- read snapshot ------------------------------------------------------

 def \_read\_first(self, candidates: tuple\[str, ...\]) -> object:
 """Read the first responsive broker read tool, fail-closed.

 Routes through the plain \`\`MCPServerAdapter.call\_tool\`\` path (NOT the
 guard) so reads are never gated. Returns \`\`None\`\` on any error envelope
 or exception so the downstream check fail-closes.

 Args:
 candidates: Ordered remote read-tool names to try.

 Returns:
 The first successful tool result payload, or \`\`None\`\`.
 """
 for remote in candidates:
 try:
 result = self.\_adapter.call\_tool(remote, {}, local\_name=remote)
 except Exception as exc:
 logger.warning("live read tool %s failed: %s", remote, exc)
 continue
 if isinstance(result, dict) and result.get("status") == "error":
 continue
 return result
 return None

 def \_read\_tools(self, operation: str, fallback: tuple\[str, ...\]) -> tuple\[str, ...\]:
 """Return connector-specific read tools, falling back to legacy names."""
 try:
 from src.trading.service import runner\_tool\_name

 remote = runner\_tool\_name(self.broker, operation)
 except Exception: # pragma: no cover - guard must fail closed later
 remote = None
 return (remote,) if remote else fallback

 # \-\- daily counter ------------------------------------------------------

 def \_read\_daily\_count(self) -> int:
 """Return today's order count via the shared per-broker counter."""
 return read\_daily\_count(self.broker)

 def \_increment\_daily\_count(self) -> None:
 """Increment today's order count via the shared per-broker counter."""
 increment\_daily\_count(self.broker)

 # \-\- audit + misc -------------------------------------------------------

 def \_audit(
 self,
 \*,
 kind: str,
 outcome: str,
 mandate: Mandate \| None,
 intent: OrderIntent \| None,
 broker\_request: dict \| None,
 broker\_response: dict \| None,
 gate\_decision: dict,
 error: str \| None = None,
 ) -\> dict \| None:
 """Write one live-action audit event and return the redacted record.

 The returned record (identical to what was written to the ledger) is
 embedded under :data:\`LIVE\_ACTION\_RESULT\_KEY\` in the tool\_result so the
 SSE relay can emit a \`\`live.action\`\` event. Auditing must never block a
 decision, so a write failure logs and returns \`\`None\`\`.

 Returns:
 The redacted audit record, or \`\`None\`\` when the write failed.
 """
 consent = mandate.consent if mandate is not None else None
 try:
 event = LiveActionEvent(
 kind=kind, # type: ignore\[arg-type\]
 session\_id=self.session\_id,
 outcome=outcome, # type: ignore\[arg-type\]
 server=self.broker,
 remote\_tool=self.remote\_name,
 intent\_normalized=\_describe\_intent(intent),
 mandate\_snapshot\_ref=consent.consent\_token\_sha256 if consent else None,
 consent\_record\_ref=consent.account\_ref if consent else None,
 broker\_request=broker\_request,
 broker\_response=broker\_response,
 gate\_decision=gate\_decision,
 error=error,
 )
 return \_record\_live\_action(event)
 except Exception as exc: # auditing must never block a decision
 logger.warning("live-action audit write failed (%s): %s", kind, exc)
 return None

 def \_is\_expired(self, mandate: Mandate) -> bool:
 """Return whether the mandate is past its \`\`expires\_at\`\` (fail-closed).

 An unparseable \`\`expires\_at\`\` is treated as expired (fail-closed): a
 live mandate with a malformed expiry must not keep trading.
 """
 raw = mandate.consent.expires\_at
 try:
 expires = datetime.fromisoformat(raw)
 except (TypeError, ValueError):
 return True
 if expires.tzinfo is None:
 expires = expires.replace(tzinfo=timezone.utc)
 return datetime.now(timezone.utc) >= expires

 @staticmethod
 def \_safe\_json(text: str) -> dict \| None:
 """Best-effort parse of the forwarded broker result for the audit record."""
 try:
 parsed = json.loads(text)
 except (TypeError, ValueError):
 return {"raw": text}
 return parsed if isinstance(parsed, dict) else {"raw": parsed}

 @staticmethod
 def \_is\_error\_envelope(broker\_response: dict \| None) -> bool:
 """Whether the forwarded result is an error envelope (H2).

 \`\`MCPServerAdapter.call\_tool\`\` returns \`\`{"status": "error", ...}\`\` on
 broker/network failure without raising. Treats a missing/unparseable
 response as an error too (fail-closed: no order was confirmed placed).
 """
 if not isinstance(broker\_response, dict):
 return True
 return str(broker\_response.get("status", "")).lower() == "error"

 @staticmethod
 def \_error\_message(broker\_response: dict \| None) -> str:
 """Extract a human-readable error from an error envelope."""
 if isinstance(broker\_response, dict):
 for key in ("error", "message", "detail"):
 value = broker\_response.get(key)
 if isinstance(value, str) and value:
 return value
 return "broker forward returned an error"

 @staticmethod
 def \_embed\_live\_action(forwarded: str, record: dict \| None) -> str:
 """Embed the redacted audit record under the frozen live-action key (H5).

 The forwarded broker result is a JSON object string; the record is added
 as a top-level \`\`live\_action\`\` key so the api\_server SSE relay can emit a
 \`\`live.action\`\` event without touching \`\`loop.py\`\`. If the result isn't a
 JSON object or there is no record, the forwarded string is returned
 unchanged.
 """
 if record is None:
 return forwarded
 try:
 payload = json.loads(forwarded)
 except (TypeError, ValueError):
 return forwarded
 if not isinstance(payload, dict):
 return forwarded
 payload\[LIVE\_ACTION\_RESULT\_KEY\] = record
 return json.dumps(payload, ensure\_ascii=False)

def \_record\_live\_action(event: LiveActionEvent) -> dict \| None:
 """Call \`\`write\_live\_action\`\` with the keyword contract, fall back positional.

 The frozen contract is
 \`\`write\_live\_action(event, \*, event\_callback=None, trace\_writer=None)\`\` (G2
 is updating the signature). If only the positional form exists today, the
 keyword call raises \`\`TypeError\`\` and we retry positionally so this parcel
 works against either signature.
 """
 try:
 return write\_live\_action(event, event\_callback=None, trace\_writer=None)
 except TypeError:
 return write\_live\_action(event)

def \_parse\_quote\_price(result: object, symbol: str) -> float \| None:
 """Extract a positive USD price from a broker quote-tool payload, fail-closed.

 Accepts the common envelope shapes a \`\`get\_quotes\`\` read tool may return:

 \\* a flat dict with a price field (\`\`price\`\` / \`\`last\_price\`\` / \`\`last\`\` /
 \`\`mark\_price\`\` / \`\`ask\`\` / \`\`bid\`\`);
 \\* a dict keyed by symbol → quote dict;
 \\* a dict with a \`\`quotes\`\` / \`\`data\`\` list of quote dicts (matched on
 \`\`symbol\`\` / \`\`ticker\`\` when present, else the sole entry).

 Unknown extra keys are ignored, never guessed. Returns \`\`None\`\` on anything
 unparseable so the caller falls back to the data loaders.

 Args:
 result: The broker quote tool's normalized payload.
 symbol: The normalized upper-case symbol requested.

 Returns:
 A positive USD price, or \`\`None\`\`.
 """
 if not isinstance(result, dict):
 return None

 direct = \_price\_from\_quote\_dict(result)
 if direct is not None:
 return direct

 keyed = result.get(symbol)
 if isinstance(keyed, dict):
 price = \_price\_from\_quote\_dict(keyed)
 if price is not None:
 return price

 for container\_key in ("quotes", "data", "results"):
 rows = result.get(container\_key)
 if not isinstance(rows, list):
 continue
 match = \_match\_quote\_row(rows, symbol)
 if match is not None:
 price = \_price\_from\_quote\_dict(match)
 if price is not None:
 return price
 return None

def \_match\_quote\_row(rows: list, symbol: str) -> dict \| None:
 """Pick the quote row for \`\`symbol\`\` from a list, or the sole entry."""
 dict\_rows = \[row for row in rows if isinstance(row, dict)\]
 for row in dict\_rows:
 for key in ("symbol", "ticker", "instrument"):
 value = row.get(key)
 if isinstance(value, str) and value.strip().upper() == symbol:
 return row
 return dict\_rows\[0\] if len(dict\_rows) == 1 else None

def \_price\_from\_quote\_dict(quote: dict) -> float \| None:
 """Return the first parseable positive price from a quote dict, else None."""
 for key in ("price", "last\_price", "last", "mark\_price", "close", "ask", "bid"):
 if key in quote:
 try:
 value = float(quote\[key\])
 except (TypeError, ValueError):
 continue
 if value == value and value > 0: # finite + positive
 return value
 return None

def \_describe\_intent(intent: OrderIntent \| None) -> str \| None:
 """Render a human-readable normalized intent for the audit record."""
 if intent is None:
 return None
 size = (
 f"${intent.notional\_usd:g}"
 if intent.notional\_usd is not None
 else f"{intent.quantity:g} units"
 if intent.quantity is not None
 else "?"
 )
 return f"{intent.side} {size} {intent.symbol} ({intent.instrument\_type.value})"