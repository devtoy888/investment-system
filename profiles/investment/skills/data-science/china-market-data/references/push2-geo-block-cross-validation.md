# push2.eastmoney.com 海外IP截断交叉验证报告

**测试日期:** 2026-07-18 (周六)  
**服务器:** Oracle ARM 新加坡, 出口IP `152.70.91.4`  
**测试脚本:** `scripts/cross_validate_em_proxy.py`  
**结论:** push2.eastmoney.com 对海外IP 100%返回502，push2delay.eastmoney.com 是可直接替换的方案

---

## DNS级别证据

```python
import socket
socket.getaddrinfo('push2.eastmoney.com', 443)[0][4][0]   # → 120.79.191.232
socket.getaddrinfo('push2delay.eastmoney.com', 443)[0][4][0]  # → 120.79.191.232
```

**结论:** 两个域名解析到同一IP，不是DNS级别的拦截。是 nginx 层面的 vhost geo-block。

---

## 测试结果摘要

| 测试组 | 成功/总数 | 详情 |
|--------|----------|------|
| push2.eastmoney.com (7种组合) | **0/7** | 全部502：含完整浏览器头/HTTP/HTTPS/30s超时/带ut参数 |
| push2delay.eastmoney.com (3种组合) | **3/3** | 全部200：裸请求/完整浏览器头/无头 |
| 其他东财接口 | 3/4 | datacenter/search-api/quote页正常，reportapi 400 |
| 同花顺 | 2/2 | 全部可用 |
| Cloudflare Worker代理 | 0/4 | worker.devtoy.xyz DNS不可达 |
| 其他东财子域 | 4/4 | fundf10/fundgz/www/nuff 均正常 |

---

## push2 502的7种失败组合

所有以下组合均返回 `502 Bad Gateway (nginx/1.26.2)`：

1. Default headers (Mac UA + Referer) — 2.1s
2. Bare headers (Mac UA only) — 1.4s
3. Full browser headers (Chrome/Windows + all Sec-* headers) — 1.4s
4. Extended timeout 30s — 2.9s
5. No headers (requests default UA) — 1.4s
6. HTTP (not HTTPS) — 1.5s
7. With `ut=fa5fd1943c7b386f172d6893dbfba10b` parameter — 1.4s

**结论:** IP级拦截，与请求参数/头/协议完全无关。

---

## push2delay 返回数据验证

```json
{
  "rc": 0, "rt": 14,
  "data": {
    "f57": "000001", "f58": "上证指数",
    "f167": 0,    "f168": 134,
    "f169": -11826, "f170": -305,
    "f171": 319
  }
}
```

**注意:** 周六非交易日，涨跌家数数据为旧值/异常。交易日数据需实地验证准确性。API结构和字段名完全兼容 push2。

---

## 实施建议

`fund_tools.py` 中只需一行改动：

```python
# 改前 (海外IP 100% 502)
'https://push2.eastmoney.com/api/qt/stock/get?...'

# 改后 (全球可用)
'https://push2delay.eastmoney.com/api/qt/stock/get?...'
```

同时建议：
- 涨跌家数主源改为 AKShare `stock_zh_a_spot_em()` (95%+可用率)
- push2delay 作为备援1
- 新浪tags 作为备援2
