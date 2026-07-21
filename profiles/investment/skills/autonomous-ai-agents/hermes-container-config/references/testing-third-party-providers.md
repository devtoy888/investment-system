# Testing Third-Party OpenAI-Compatible API Providers

## ⚡ Preferred: Test via Hermes Built-In Tools

Before writing any curl/Python, use Hermes' own tools — they test the ACTIVE backend chain that the running agent uses:

| What to test | Hermes tool |
|---|---|
| Search API key (Tavily/Exa/Parallel) | `web_search(query="test", limit=1)` |
| Web extraction (Firecrawl/Tavily) | `web_extract(urls=["https://httpbin.org/get"])` |
| Model provider (DeepSeek/xAI/Agnes) | `delegate_task(goal="Say OK", toolsets=[])` or `hermes chat -q "Say OK"` |

**What to look for:**
- `web_search` returns `{"success": true, "data": {"web": [...]}}` → search works
- `web_extract` returns content with no `error` → extraction works
- `delegate_task` returns the expected response → model works

## When to Use curl/Python Instead

Use direct API calls when:

```bash
curl -s https://<provider-url>/v1/chat/completions \
  -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d '{"model": "<model>", "messages": [{"role": "user", "content": "Hi"}]}'
```

Success: non-empty `choices`. Failure: 401 (bad key) or 404 (wrong endpoint/model).

## Full Test Suite (Python)

```python
import json, urllib.request, time

API_KEY = "sk-..."_URL = "https://apihub.example.com/v1"

def api(method, data, timeout=30):
    url = f"{BASE_URL}/{method}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req, data=json.dumps(data).encode(), timeout=timeout)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()[:300]}
```

### 1. List Models
```python
api("models", {}, timeout=10)
```

### 2. Basic Chat + Speed
```python
times = []
for _ in range(5):
    t0 = time.time()
    r = api("chat/completions", {"model":"<model>", "messages":[{"role":"user","content":"ok"}], "max_tokens":10})
    times.append(time.time() - t0)
```

### 3. Streaming
```python
test streaming by setting stream=True, count SSE chunks
```

### 4. Image Generation
```python
api("images/generations", {"model":"<image-model>","prompt":"a cat","n":1,"size":"1024x768"}, timeout=30)
```

## Report Template

| Test | Status | Notes |
|------|--------|-------|
| Models list | ✅/❌ | List model IDs |
| Basic chat | ✅/❌ | Avg speed: X.Xs |
| Streaming | ✅/❌ | |
| Image gen | ✅/❌/N/A | |
| Long context | ✅/❌ | Test with 500+ tokens |
| Tool calling | ✅/❌/N/A | If supported |
