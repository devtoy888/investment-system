"""Security regression tests for API authentication boundaries."""

from \_\_future\_\_ import annotations

import ipaddress
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import api\_server

def \_remote\_client() -> TestClient:
 """Return a TestClient that simulates a non-loopback caller."""
 return TestClient(api\_server.app, client=("203.0.113.10", 50000))

def \_local\_client() -> TestClient:
 """Return a TestClient that simulates a loopback caller."""
 return TestClient(api\_server.app, client=("127.0.0.1", 50000))

@pytest.fixture(autouse=True)
def clear\_api\_key(monkeypatch: pytest.MonkeyPatch) -> None:
 """Start every auth test from dev-mode auth."""
 monkeypatch.delenv("API\_AUTH\_KEY", raising=False)
 monkeypatch.delenv("VIBE\_TRADING\_TRUST\_DOCKER\_LOOPBACK", raising=False)
 monkeypatch.delenv("VIBE\_TRADING\_ENABLE\_SHELL\_TOOLS", raising=False)
 monkeypatch.setattr(api\_server, "\_API\_KEY", "")

def test\_remote\_write\_requires\_api\_key\_when\_key\_unset() -> None:
 response = \_remote\_client().post("/sessions", json={})

 assert response.status\_code == 403
 assert "API\_AUTH\_KEY" in response.json()\["detail"\]

def test\_remote\_goal\_endpoints\_require\_api\_key\_when\_key\_unset() -> None:
 client = \_remote\_client()

 cases = \[\
 ("post", "/sessions/abcdef012345/goal", {"objective": "Evaluate NVDA", "criteria": \["Define thesis"\]}),\
 ("get", "/sessions/abcdef012345/goal", None),\
 (\
 "post",\
 "/sessions/abcdef012345/goal/evidence",\
 {\
 "goal\_id": "goal\_123",\
 "expected\_goal\_id": "goal\_123",\
 "text": "Evidence",\
 },\
 ),\
 \]
 for method, path, body in cases:
 kwargs = {"json": body} if body is not None else {}
 response = getattr(client, method)(path, \*\*kwargs)
 assert response.status\_code == 403, f"{method.upper()} {path}"

def test\_local\_dev\_write\_allowed\_when\_key\_unset() -> None:
 response = \_local\_client().post("/sessions", json={})

 assert response.status\_code in {201, 501}

def test\_docker\_gateway\_dev\_write\_allowed\_only\_with\_compose\_trust\_flag(
 monkeypatch: pytest.MonkeyPatch,
) -\> None:
 request = SimpleNamespace(client=SimpleNamespace(host="172.18.0.1"))
 monkeypatch.setattr(
 api\_server,
 "\_default\_gateway\_ips",
 lambda: {ipaddress.IPv4Address("172.18.0.1")},
 )

 assert not api\_server.\_is\_local\_client(request)

 monkeypatch.setenv("VIBE\_TRADING\_TRUST\_DOCKER\_LOOPBACK", "1")
 from src.config.accessor import reset\_env\_config
 reset\_env\_config()

 assert api\_server.\_is\_local\_client(request)

def test\_docker\_network\_peer\_is\_not\_local\_even\_with\_compose\_trust\_flag(
 monkeypatch: pytest.MonkeyPatch,
) -\> None:
 request = SimpleNamespace(client=SimpleNamespace(host="172.18.0.42"))
 monkeypatch.setenv("VIBE\_TRADING\_TRUST\_DOCKER\_LOOPBACK", "1")
 monkeypatch.setattr(
 api\_server,
 "\_default\_gateway\_ips",
 lambda: {ipaddress.IPv4Address("172.18.0.1")},
 )

 assert not api\_server.\_is\_local\_client(request)

def test\_configured\_api\_key\_required\_for\_sensitive\_reads(
 monkeypatch: pytest.MonkeyPatch,
) -\> None:
 monkeypatch.setenv("API\_AUTH\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_API\_KEY", "secret")
 client = \_remote\_client()

 for path in \[\
 "/runs",\
 "/sessions",\
 "/sessions/abcdef012345/goal",\
 "/swarm/runs",\
 \]:
 response = client.get(path)
 assert response.status\_code == 401, path

def test\_configured\_api\_key\_accepts\_bearer\_for\_sensitive\_reads(
 monkeypatch: pytest.MonkeyPatch,
) -\> None:
 monkeypatch.setenv("API\_AUTH\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_API\_KEY", "secret")

 response = \_remote\_client().get(
 "/runs",
 headers={"Authorization": "Bearer secret"},
 )

 assert response.status\_code == 200

def test\_loopback\_bypasses\_auth\_even\_when\_api\_key\_configured(
 monkeypatch: pytest.MonkeyPatch,
) -\> None:
 """Loopback clients remain trusted for non-settings reads."""
 monkeypatch.setenv("API\_AUTH\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_API\_KEY", "secret")

 local = \_local\_client()
 remote = \_remote\_client()

 # Loopback: no bearer needed → should succeed
 local\_response = local.get("/runs")
 assert local\_response.status\_code == 200

 # Remote without bearer: still rejected
 remote\_response = remote.get("/runs")
 assert remote\_response.status\_code == 401

 # Remote with bearer: accepted
 remote\_bearer = remote.get("/runs", headers={"Authorization": "Bearer secret"})
 assert remote\_bearer.status\_code == 200

def \_llm\_settings\_payload(base\_url: str = "https://api.openai.com/v1") -> dict\[str, object\]:
 return {
 "provider": "openai",
 "model\_name": "gpt-4o-mini",
 "base\_url": base\_url,
 "temperature": 0,
 "timeout\_seconds": 120,
 "max\_retries": 2,
 }

def test\_dns\_rebound\_loopback\_cannot\_write\_llm\_settings\_without\_bearer(
 monkeypatch: pytest.MonkeyPatch,
 tmp\_path,
) -\> None:
 """Configured API keys must gate credential-routing settings writes."""
 monkeypatch.setenv("API\_AUTH\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_API\_KEY", "secret")
 env\_path = tmp\_path / ".env"
 env\_path.write\_text(
 "\\n".join(
 \[\
 "LANGCHAIN\_PROVIDER=openai",\
 "LANGCHAIN\_MODEL\_NAME=gpt-4o-mini",\
 "OPENAI\_BASE\_URL=https://api.openai.com/v1",\
 "OPENAI\_API\_KEY=sk-existing-test-key",\
 "",\
 \]
 ),
 encoding="utf-8",
 )
 monkeypatch.setattr(api\_server, "ENV\_PATH", env\_path)

 response = \_local\_client().put(
 "/settings/llm",
 headers={"host": "attacker.example:8899", "origin": "http://attacker.example:8899"},
 json=\_llm\_settings\_payload("https://attacker.example/openai-compatible/v1"),
 )

 # The rebound-host middleware (#242) rejects this loopback request with an
 # attacker-controlled Host before the settings-write auth layer is reached;
 # either layer must prevent the credential-routing write from persisting.
 assert response.status\_code == 403
 saved = env\_path.read\_text(encoding="utf-8")
 assert "https://attacker.example/openai-compatible/v1" not in saved
 assert "OPENAI\_BASE\_URL=https://api.openai.com/v1" in saved
 assert "OPENAI\_API\_KEY=sk-existing-test-key" in saved

def test\_authorized\_client\_can\_write\_llm\_settings\_when\_api\_key\_configured(
 monkeypatch: pytest.MonkeyPatch,
 tmp\_path,
) -\> None:
 monkeypatch.setenv("API\_AUTH\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_API\_KEY", "secret")
 env\_path = tmp\_path / ".env"
 env\_path.write\_text("", encoding="utf-8")
 monkeypatch.setattr(api\_server, "ENV\_PATH", env\_path)

 response = \_remote\_client().put(
 "/settings/llm",
 headers={"Authorization": "Bearer secret"},
 json=\_llm\_settings\_payload("https://api.openai.com/v1"),
 )

 assert response.status\_code == 200
 assert "OPENAI\_BASE\_URL=https://api.openai.com/v1" in env\_path.read\_text(encoding="utf-8")

def test\_local\_dev\_can\_write\_llm\_settings\_when\_api\_key\_unset(
 monkeypatch: pytest.MonkeyPatch,
 tmp\_path,
) -\> None:
 env\_path = tmp\_path / ".env"
 monkeypatch.setattr(api\_server, "ENV\_PATH", env\_path)

 response = \_local\_client().put(
 "/settings/llm",
 json=\_llm\_settings\_payload("https://api.openai.com/v1"),
 )

 assert response.status\_code == 200
 assert "OPENAI\_BASE\_URL=https://api.openai.com/v1" in env\_path.read\_text(encoding="utf-8")

def test\_loopback\_rejects\_rebound\_host\_before\_auth\_bypass(
 monkeypatch: pytest.MonkeyPatch,
) -\> None:
 """A loopback peer is not enough when Host is attacker-controlled."""
 monkeypatch.setenv("API\_AUTH\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_API\_KEY", "secret")

 response = \_local\_client().get(
 "/runs",
 headers={"Host": "attacker.example:8899", "Origin": "http://attacker.example:8899"},
 )

 assert response.status\_code == 403
 assert response.json()\["detail"\] == "Untrusted local API host"

def test\_remote\_untrusted\_host\_still\_uses\_bearer\_auth(
 monkeypatch: pytest.MonkeyPatch,
) -\> None:
 """The Host gate only narrows loopback trust; remote clients still use API\_AUTH\_KEY."""
 monkeypatch.setenv("API\_AUTH\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_API\_KEY", "secret")

 response = \_remote\_client().get(
 "/runs",
 headers={"Host": "attacker.example:8899", "Origin": "http://attacker.example:8899"},
 )

 assert response.status\_code == 401

def test\_rebound\_host\_cannot\_start\_live\_runner(
 monkeypatch: pytest.MonkeyPatch,
) -\> None:
 """DNS-rebound loopback JSON requests must not reach live-runner control."""
 monkeypatch.setenv("API\_AUTH\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_API\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_active\_mandate\_state", lambda broker: SimpleNamespace(expired=False))

 reached = {"factory": False}

 class DummyRunner:
 async def run\_loop(self):
 return None

 def build\_runner(broker: str) -> DummyRunner:
 reached\["factory"\] = True
 return DummyRunner()

 monkeypatch.setattr(api\_server, "\_runner\_factory", build\_runner)
 monkeypatch.setattr("src.trading.service.broker\_supports\_live\_runner", lambda broker: True)
 monkeypatch.setattr("src.live.halt.halt\_flag\_set", lambda broker=None: False)
 api\_server.\_runner\_tasks.clear()

 response = \_local\_client().post(
 "/live/runner/start",
 headers={
 "Host": "attacker.example:8899",
 "Origin": "http://attacker.example:8899",
 "Content-Type": "application/json",
 },
 json={"broker": "robinhood", "session\_id": "proof-session"},
 )

 assert response.status\_code == 403
 assert reached\["factory"\] is False
 assert "robinhood" not in api\_server.\_runner\_tasks

def test\_allowed\_loopback\_host\_can\_start\_live\_runner\_dev\_mode(
 monkeypatch: pytest.MonkeyPatch,
) -\> None:
 """Allowed local hosts preserve the loopback dev-mode runner control path."""
 monkeypatch.setattr(api\_server, "\_active\_mandate\_state", lambda broker: SimpleNamespace(expired=False))

 reached = {"factory": False}

 class DummyRunner:
 async def run\_loop(self):
 return None

 def build\_runner(broker: str) -> DummyRunner:
 reached\["factory"\] = True
 return DummyRunner()

 monkeypatch.setattr(api\_server, "\_runner\_factory", build\_runner)
 monkeypatch.setattr("src.trading.service.broker\_supports\_live\_runner", lambda broker: True)
 monkeypatch.setattr("src.live.halt.halt\_flag\_set", lambda broker=None: False)
 api\_server.\_runner\_tasks.clear()

 response = \_local\_client().post(
 "/live/runner/start",
 headers={"Host": "127.0.0.1:8899", "Content-Type": "application/json"},
 json={"broker": "robinhood", "session\_id": "proof-session"},
 )

 assert response.status\_code == 200
 assert reached\["factory"\] is True
 task = api\_server.\_runner\_tasks.pop("robinhood", None)
 if task is not None and not task.done():
 task.cancel()

def test\_configured\_api\_key\_required\_for\_session\_event\_stream(
 monkeypatch: pytest.MonkeyPatch,
) -\> None:
 monkeypatch.setenv("API\_AUTH\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_API\_KEY", "secret")

 response = \_remote\_client().get("/sessions/missing/events")

 assert response.status\_code == 401

def test\_session\_event\_stream\_rejects\_long\_lived\_api\_key\_query(
 monkeypatch: pytest.MonkeyPatch,
) -\> None:
 """VT-003: the long-lived key is no longer accepted in the SSE query string."""
 monkeypatch.setenv("API\_AUTH\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_API\_KEY", "secret")

 response = \_remote\_client().get("/sessions/missing/events?api\_key=secret")

 assert response.status\_code == 401

def test\_session\_event\_stream\_accepts\_single\_use\_ticket\_for\_browser\_eventsource(
 monkeypatch: pytest.MonkeyPatch,
) -\> None:
 """VT-003: a header-minted single-use ticket authenticates the EventSource."""
 monkeypatch.setenv("API\_AUTH\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_API\_KEY", "secret")

 ticket = api\_server.\_mint\_sse\_ticket()
 response = \_remote\_client().get(f"/sessions/missing/events?ticket={ticket}")

 # Auth passed (the 404/501 comes from the missing session / disabled runtime,
 # not from the auth layer).
 assert response.status\_code in {404, 501}

def test\_shell\_tools\_disabled\_for\_loopback\_api\_request\_by\_default() -> None:
 request = SimpleNamespace(client=SimpleNamespace(host="127.0.0.1"))

 assert not api\_server.\_shell\_tools\_enabled\_for\_request(request)

def test\_shell\_tools\_disabled\_for\_remote\_api\_request\_by\_default() -> None:
 request = SimpleNamespace(client=SimpleNamespace(host="203.0.113.10"))

 assert not api\_server.\_shell\_tools\_enabled\_for\_request(request)

def test\_shell\_tools\_api\_request\_accepts\_explicit\_opt\_in(
 monkeypatch: pytest.MonkeyPatch,
) -\> None:
 request = SimpleNamespace(client=SimpleNamespace(host="127.0.0.1"))
 monkeypatch.setenv("VIBE\_TRADING\_ENABLE\_SHELL\_TOOLS", "1")

 assert api\_server.\_shell\_tools\_enabled\_for\_request(request)

def test\_dns\_rebound\_swarm\_run\_does\_not\_enable\_shell\_tools\_by\_default(
 monkeypatch: pytest.MonkeyPatch,
) -\> None:
 captured: dict\[str, object\] = {}

 class FakeRuntime:
 def start\_run(self, preset\_name: str, user\_vars: dict, include\_shell\_tools: bool = False):
 captured\["preset\_name"\] = preset\_name
 captured\["user\_vars"\] = user\_vars
 captured\["include\_shell\_tools"\] = include\_shell\_tools
 return SimpleNamespace(
 id="swarm-test-no-shell",
 status=SimpleNamespace(value="running"),
 preset\_name=preset\_name,
 )

 monkeypatch.setattr(api\_server, "\_get\_swarm\_runtime", lambda: FakeRuntime())
 monkeypatch.setenv("API\_AUTH\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_API\_KEY", "secret")

 response = \_local\_client().post(
 "/swarm/runs",
 headers={
 "Host": "attacker.example:8899",
 "Origin": "http://attacker.example:8899",
 },
 json={
 "preset\_name": "technical\_analysis\_panel",
 "user\_vars": {"target": "NVDA", "timeframe": "1d"},
 },
 )

 # The rebound-host middleware (#242) rejects the attacker-controlled Host
 # before /swarm/runs runs, so the request never reaches the point where shell
 # tools would be granted — the swarm runtime is never invoked.
 assert response.status\_code == 403
 assert "include\_shell\_tools" not in captured

def test\_dns\_rebound\_session\_message\_does\_not\_enable\_shell\_tools\_by\_default(
 monkeypatch: pytest.MonkeyPatch,
) -\> None:
 captured: dict\[str, object\] = {}

 class FakeSessionService:
 async def send\_message(self, session\_id: str, content: str, include\_shell\_tools: bool = False):
 captured\["session\_id"\] = session\_id
 captured\["content"\] = content
 captured\["include\_shell\_tools"\] = include\_shell\_tools
 return {"message\_id": "msg-test", "attempt\_id": "attempt-test"}

 monkeypatch.setattr(api\_server, "\_get\_session\_service", lambda: FakeSessionService())
 monkeypatch.setenv("API\_AUTH\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_API\_KEY", "secret")

 response = \_local\_client().post(
 "/sessions/abcdef012345/messages",
 headers={
 "Host": "attacker.example:8899",
 "Origin": "http://attacker.example:8899",
 },
 json={"content": "SESSION\_DNS\_REBIND\_PROOF\_PAYLOAD"},
 )

 # The rebound-host middleware (#242) rejects the attacker-controlled Host
 # before /sessions/{id}/messages runs, so the session service is never
 # invoked and shell tools can never be granted via a DNS-rebound request.
 assert response.status\_code == 403
 assert "include\_shell\_tools" not in captured

def test\_default\_cors\_origins\_are\_loopback\_only() -> None:
 origins = api\_server.\_parse\_cors\_origins(None)

 assert origins
 assert "\*" not in origins
 assert all(
 origin.startswith("http://localhost:") or origin.startswith("http://127.0.0.1:")
 for origin in origins
 )

def test\_cors\_origins\_reject\_credentialed\_wildcard() -> None:
 with pytest.raises(RuntimeError, match="CORS\_ORIGINS"):
 api\_server.\_parse\_cors\_origins("https://app.example.com,\*")

def test\_cors\_origins\_accept\_explicit\_remote\_origins() -> None:
 origins = api\_server.\_parse\_cors\_origins(" https://app.example.com,https://admin.example.com ")

 assert origins == \["https://app.example.com", "https://admin.example.com"\]

def test\_loopback\_shutdown\_requires\_bearer\_when\_api\_key\_configured(
 monkeypatch: pytest.MonkeyPatch,
) -\> None:
 """Loopback alone must not authorize the browser-reachable shutdown action."""
 called: list\[bool\] = \[\]
 monkeypatch.setenv("API\_AUTH\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_API\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_terminate\_current\_process", lambda: called.append(True))

 response = \_local\_client().post("/system/shutdown")

 assert response.status\_code == 401
 assert called == \[\]

def test\_loopback\_shutdown\_rejects\_cross\_site\_browser\_request(
 monkeypatch: pytest.MonkeyPatch,
) -\> None:
 """CORS is not enough; unsafe cross-site browser POSTs must be rejected."""
 called: list\[bool\] = \[\]
 monkeypatch.setenv("API\_AUTH\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_API\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_terminate\_current\_process", lambda: called.append(True))

 response = \_local\_client().post(
 "/system/shutdown",
 headers={"Origin": "https://attacker.example"},
 )

 assert response.status\_code == 403
 assert called == \[\]

def test\_loopback\_shutdown\_accepts\_valid\_bearer(
 monkeypatch: pytest.MonkeyPatch,
) -\> None:
 called: list\[bool\] = \[\]
 monkeypatch.setenv("API\_AUTH\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_API\_KEY", "secret")
 monkeypatch.setattr(api\_server, "\_terminate\_current\_process", lambda: called.append(True))

 response = \_local\_client().post(
 "/system/shutdown",
 headers={"Authorization": "Bearer secret", "Origin": "http://127.0.0.1:8899"},
 )

 assert response.status\_code == 200
 assert response.json()\["status"\] == "shutting-down"
 assert called == \[True\]

\# ============================================================================
\# Path-parameter validation (run\_id / session\_id)
\# ============================================================================

@pytest.mark.parametrize(
 "value",
 \[\
 # Real formats produced by the codebase.\
 "20260105\_120342\_12\_a1b2c3", # state.create\_run\_dir\
 "swarm-20260105\_120342-a1b2c3", # swarm presets.run\_id\
 "abcdef012345", # session\_id (uuid.uuid4().hex\[:12\])\
 "run-1",\
 "A" \* 128,\
 \],
)
def test\_validate\_path\_param\_accepts\_known\_good\_values(value: str) -> None:
 api\_server.\_validate\_path\_param(value, "run\_id")

@pytest.mark.parametrize(
 "value",
 \[\
 "",\
 "..",\
 "../etc",\
 "foo/bar",\
 "foo\\\bar",\
 "foo bar",\
 "foo.bar", # dot is not in the safe class\
 "foo\\n",\
 "foo\\r",\
 "foo\\t",\
 "foo\\x00bar",\
 "A" \* 129,\
 \],
)
def test\_validate\_path\_param\_rejects\_traversal\_inputs(value: str) -> None:
 with pytest.raises(api\_server.HTTPException) as excinfo:
 api\_server.\_validate\_path\_param(value, "run\_id")

 assert excinfo.value.status\_code == 400
 assert "run\_id" in excinfo.value.detail

def test\_get\_run\_code\_rejects\_dot\_run\_id() -> None:
 response = \_local\_client().get("/runs/../code")

 # Either rejected at routing (404) or by the validator (400). Both are safe;
 # what we forbid is reading code from outside RUNS\_DIR.
 assert response.status\_code in {400, 404}

def test\_get\_run\_pine\_rejects\_traversal\_run\_id() -> None:
 response = \_local\_client().get("/runs/foo.bar/pine")

 assert response.status\_code == 400
 assert response.json()\["detail"\] == "invalid run\_id"

def test\_get\_run\_pine\_rejects\_url\_encoded\_newline\_run\_id() -> None:
 response = \_local\_client().get("/runs/foo%0A/pine")

 assert response.status\_code == 400
 assert response.json()\["detail"\] == "invalid run\_id"

def test\_get\_run\_result\_rejects\_traversal\_run\_id() -> None:
 response = \_local\_client().get("/runs/foo.bar")

 assert response.status\_code == 400
 assert response.json()\["detail"\] == "invalid run\_id"

def test\_session\_endpoints\_reject\_traversal\_session\_id() -> None:
 client = \_local\_client()

 cases = \[\
 ("get", "/sessions/foo.bar", None),\
 ("delete", "/sessions/foo.bar", None),\
 ("patch", "/sessions/foo.bar", {"title": "x"}),\
 ("post", "/sessions/foo.bar/messages", {"content": "x"}),\
 ("get", "/sessions/foo.bar/messages", None),\
 ("post", "/sessions/foo.bar/cancel", None),\
 ("post", "/sessions/foo.bar/goal", {"objective": "x", "criteria": \["y"\]}),\
 ("get", "/sessions/foo.bar/goal", None),\
 (\
 "post",\
 "/sessions/foo.bar/goal/evidence",\
 {"goal\_id": "goal\_123", "expected\_goal\_id": "goal\_123", "text": "x"},\
 ),\
 \]
 for method, path, body in cases:
 kwargs = {"json": body} if body is not None else {}
 response = getattr(client, method)(path, \*\*kwargs)
 assert response.status\_code == 400, f"{method.upper()} {path} should be rejected"
 assert response.json()\["detail"\] == "invalid session\_id"

def test\_session\_event\_stream\_rejects\_traversal\_session\_id() -> None:
 response = \_local\_client().get("/sessions/foo.bar/events")

 assert response.status\_code == 400
 assert response.json()\["detail"\] == "invalid session\_id"

def test\_swarm\_run\_endpoints\_reject\_traversal\_run\_id() -> None:
 client = \_local\_client()

 for method, path in (
 ("get", "/swarm/runs/foo.bar"),
 ("get", "/swarm/runs/foo.bar/events"),
 ("post", "/swarm/runs/foo.bar/cancel"),
 ("post", "/swarm/runs/foo.bar/retry"),
 ):
 response = getattr(client, method)(path)
 assert response.status\_code == 400, f"{method.upper()} {path} should be rejected"
 assert response.json()\["detail"\] == "invalid run\_id"