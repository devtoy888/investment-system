#!/usr/bin/env python3
"""
东财502交叉验证: 海外IP是否导致 + 代理方案测试
服务器: Oracle ARM 新加坡
测试日期: 2026-07-18 (周六，非交易时段)
"""

import json, time, sys, os
import requests
from datetime import datetime

RESULTS = []

def test(name: str, url: str, method="GET", headers=None, timeout=10, proxy=None, allow_redirects=True, **kwargs):
    """执行一次HTTP测试并记录结果"""
    result = {
        "name": name,
        "url": url[:150],
        "method": method,
        "timeout": timeout,
        "proxy": proxy,
        "timestamp": datetime.now().isoformat(),
    }
    _headers = headers or {}
    
    t0 = time.time()
    try:
        proxies = {"http": proxy, "https": proxy} if proxy else None
        
        r = requests.request(
            method, url, headers=_headers, timeout=timeout,
            proxies=proxies, allow_redirects=allow_redirects, **kwargs
        )
        
        elapsed = round(time.time() - t0, 3)
        result["status_code"] = r.status_code
        result["elapsed"] = elapsed
        result["content_length"] = len(r.text)
        result["content_preview"] = r.text[:500]
        
        if r.status_code == 200:
            try:
                j = r.json()
                result["json_keys"] = list(j.keys()) if isinstance(j, dict) else "array"
                result["json_data"] = str(j)[:300]
            except:
                result["json_keys"] = None
        elif r.status_code == 502:
            result["error"] = "502 Bad Gateway — 东财拦截海外IP"
        else:
            result["error"] = f"HTTP {r.status_code}"
            
    except requests.exceptions.Timeout:
        elapsed = round(time.time() - t0, 3)
        result["status_code"] = None
        result["elapsed"] = elapsed
        result["error"] = "Timeout"
    except requests.exceptions.ConnectionError as e:
        elapsed = round(time.time() - t0, 3)
        result["status_code"] = None
        result["elapsed"] = elapsed
        result["error"] = f"ConnectionError: {str(e)[:200]}"
    except Exception as e:
        elapsed = round(time.time() - t0, 3)
        result["status_code"] = None
        result["elapsed"] = elapsed
        result["error"] = f"Exception: {type(e).__name__}: {str(e)[:200]}"
    
    RESULTS.append(result)
    status = result.get("status_code")
    status_str = str(status) if status is not None else "ERR"
    err = result.get("error", "")
    print(f"  [{status_str:>3}] {name} ({result['elapsed']}s)", end="")
    if err:
        print(f" — {err}", end="")
    print()
    return result


# ──────────── 公共头 ────────────
DEFAULT_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

EM_REFERER_HEADERS = {
    "User-Agent": DEFAULT_UA,
    "Referer": "https://quote.eastmoney.com/",
}

FULL_BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://quote.eastmoney.com/",
    "Origin": "https://quote.eastmoney.com",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
}

# ──── 测试开始 ────
print("=" * 70)
print("东财502交叉验证 — 海外IP测试")
print(f"时间: {datetime.now().isoformat()}")
print(f"服务器: Oracle ARM 新加坡")
print("=" * 70)

PUSH2_URL = "https://push2.eastmoney.com/api/qt/stock/get?secid=1.000001&fields=f57,f58,f167,f168,f169,f170,f171"
PUSH2_DELAY_URL = "https://push2delay.eastmoney.com/api/qt/stock/get?secid=1.000001&fields=f57,f58,f167,f168,f169,f170,f171"

# ============================================================================
# 测试组1: push2.eastmoney.com
# ============================================================================
print("\n─── 组1: push2.eastmoney.com (涨跌家数) ───")

test("1a_push2_current", PUSH2_URL, headers=EM_REFERER_HEADERS, timeout=15)
test("1b_push2_bare", PUSH2_URL, headers={"User-Agent": DEFAULT_UA}, timeout=15)
test("1c_push2_full_browser", PUSH2_URL, headers=FULL_BROWSER_HEADERS, timeout=15)
test("1d_push2_timeout_30s", PUSH2_URL, headers=EM_REFERER_HEADERS, timeout=30)
test("1e_push2_no_headers", PUSH2_URL, timeout=15)

# ============================================================================
# 测试组2: push2delay.eastmoney.com
# ============================================================================
print("\n─── 组2: push2delay.eastmoney.com (备胎域名) ───")

test("2a_push2delay_current", PUSH2_DELAY_URL, headers=EM_REFERER_HEADERS, timeout=15)
test("2b_push2delay_full_browser", PUSH2_DELAY_URL, headers=FULL_BROWSER_HEADERS, timeout=15)
test("2c_push2delay_no_headers", PUSH2_DELAY_URL, timeout=15)

# ============================================================================
# 测试组3: 其他东财接口
# ============================================================================
print("\n─── 组3: 其他东财接口 ───")

test("3a_reportapi",
     "https://reportapi.eastmoney.com/report/list?cb=datatable1357949&industryCode=*&pageSize=1&pageIndex=1&fields=&source=Web&beginTime=&endTime=&author=",
     headers=EM_REFERER_HEADERS, timeout=15)

test("3b_datacenter",
     "https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_DMSK_FN_INCOME&columns=ALL&pageSize=1&pageNumber=1&sortColumns=NOTICE_DATE&sortTypes=-1&source=WEB&client=WEB&filter=(REPORTTYPE='DM_GG')(DATE_TYPE='Y')",
     headers=EM_REFERER_HEADERS, timeout=15)

test("3c_search_api",
     "https://search-api-web.eastmoney.com/search/jsonp?cb=jQuery&param=%7B%22size%22%3A1%2C%22keyword%22%3A%22%E8%B4%B5%E5%B7%9E%E8%8C%85%E5%8F%B0%22%2C%22filter%22%3A%7B%7D%7D",
     headers=EM_REFERER_HEADERS, timeout=15)

test("3d_quote_page", "https://quote.eastmoney.com/",
     headers=FULL_BROWSER_HEADERS, timeout=15, allow_redirects=True)

# ============================================================================
# 测试组4: 同花顺
# ============================================================================
print("\n─── 组4: 同花顺接口 ───")

test("4a_10jqka_basic", "https://basic.10jqka.com.cn/api/stockph/basicinfo/000001/",
     headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.10jqka.com.cn/"}, timeout=10)
test("4b_10jqka_quote", "https://d.10jqka.com.cn/v2/realhead/hs_000001/last.js",
     headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.10jqka.com.cn/"}, timeout=10)

# ============================================================================
# 测试组5: Cloudflare Worker代理
# ============================================================================
print("\n─── 组5: Cloudflare Worker代理 worker.devtoy.xyz ───")

WORKER_PROXY = "http://worker.devtoy.xyz"

# 5a: Worker自身健康检查
test("5a_worker_health", WORKER_PROXY + "/", timeout=10)

# 5b: Worker作为正向代理
test("5b_worker_forward_proxy", PUSH2_URL, headers=EM_REFERER_HEADERS, timeout=15,
     proxy=WORKER_PROXY)

# 5c: Worker作为反向代理 (URL路径方式)
test("5c_worker_reverse_proxy",
     WORKER_PROXY + "/push2.eastmoney.com/api/qt/stock/get?secid=1.000001&fields=f57,f58,f167,f168,f169,f170,f171",
     timeout=15)

# 5d: 用Worker代理东财其他接口
test("5d_worker_proxy_datacenter",
     "https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_DMSK_FN_INCOME&columns=ALL&pageSize=1&pageNumber=1&sortColumns=NOTICE_DATE&sortTypes=-1&source=WEB&client=WEB&filter=(REPORTTYPE='DM_GG')(DATE_TYPE='Y')",
     headers=EM_REFERER_HEADERS, timeout=15, proxy=WORKER_PROXY)

# ============================================================================
# 测试组6: 其他东财子域名 + 镜像
# ============================================================================
print("\n─── 组6: 其他东财子域名/镜像 ───")

test("6a_fundf10", "https://fundf10.eastmoney.com/jjjz_000001.html",
     headers={"User-Agent": DEFAULT_UA}, timeout=15)
test("6b_fundgz", "https://fundgz.1234567.com.cn/js/000001.js",
     headers={"Referer": "https://fund.eastmoney.com/", "User-Agent": DEFAULT_UA}, timeout=15)
test("6c_em_www", "https://www.eastmoney.com/",
     headers=FULL_BROWSER_HEADERS, timeout=15)
test("6d_push2_http", "http://push2.eastmoney.com/api/qt/stock/get?secid=1.000001&fields=f57,f58,f167,f168,f169,f170,f171",
     headers=None, timeout=15)
test("6e_push2_with_ut", PUSH2_URL + "&ut=fa5fd1943c7b386f172d6893dbfba10b",
     headers=EM_REFERER_HEADERS, timeout=15)
test("6f_nuff_eastmoney", "https://nuff.eastmoney.com/EM_Finance/StockReport/Index?type=web",
     headers=FULL_BROWSER_HEADERS, timeout=15)

# ============================================================================
# 输出结果
# ============================================================================
print("\n" + "=" * 70)
print("📊 测试结果汇总")
print("=" * 70)

summary = {
    "server": "Oracle ARM 新加坡",
    "timestamp": datetime.now().isoformat(),
    "total_tests": len(RESULTS),
    "success_200": sum(1 for r in RESULTS if r.get("status_code") == 200),
    "failure_502": sum(1 for r in RESULTS if r.get("status_code") == 502),
    "failure_403": sum(1 for r in RESULTS if r.get("status_code") == 403),
    "failure_other": sum(1 for r in RESULTS if r.get("status_code") and r["status_code"] not in (200, 403, 502)),
    "timeout": sum(1 for r in RESULTS if r.get("error") == "Timeout"),
    "connection_error": sum(1 for r in RESULTS if r.get("error") and "ConnectionError" in r["error"]),
    "no_response": sum(1 for r in RESULTS if r.get("status_code") is None),
}

for k, v in summary.items():
    if k != "server":
        print(f"  {k}: {v}")

# 按组分析
print("\n─── 分组分析 ───")
groups = {}
for r in RESULTS:
    group = r["name"].split("_")[0]
    groups.setdefault(group, []).append(r)

for gname in sorted(groups.keys()):
    gr = groups[gname]
    ok = sum(1 for r in gr if r.get("status_code") == 200)
    ng = sum(1 for r in gr if r.get("status_code") != 200)
    print(f"  {gname}: {ok}/{len(gr)} 成功")

# ── 关键诊断 ──
print("\n─── 诊断结论 ───")
push2 = [r for r in RESULTS if "push2" in r["name"] and "push2delay" not in r["name"] and "worker" not in r["name"]]
push2delay = [r for r in RESULTS if "push2delay" in r["name"]]
worker = [r for r in RESULTS if "worker" in r["name"]]

print(f"\n push2.eastmoney.com: {sum(1 for r in push2 if r.get('status_code')==200)}/{len(push2)} 成功")
for r in push2:
    s = r.get("status_code", "ERR")
    e = r.get("error", "")
    print(f"    {r['name']}: {s} {e}")

if push2delay:
    print(f"\n push2delay.eastmoney.com: {sum(1 for r in push2delay if r.get('status_code')==200)}/{len(push2delay)} 成功")
    for r in push2delay:
        s = r.get("status_code", "ERR")
        e = r.get("error", "")
        print(f"    {r['name']}: {s} {e}")

print(f"\n Worker代理: {sum(1 for r in worker if r.get('status_code')==200)}/{len(worker)} 成功")
for r in worker:
    s = r.get("status_code", "ERR")
    e = r.get("error", "")
    print(f"    {r['name']}: {s} {e}")

# 判断
push2_all_502 = all(r.get("status_code") == 502 for r in push2)
push2_none_200 = not any(r.get("status_code") == 200 for r in push2)

if push2_all_502:
    print("\n🔴 结论: push2.eastmoney.com 全部返回502 — 确认海外IP拦截")
elif push2_none_200 and any(r.get("status_code") == 502 for r in push2):
    print("\n🟡 结论: push2 部分502 — 高度疑似海外IP限制")
else:
    print("\n🟢 push2可达")

# 保存JSON
output_path = "/opt/data/scripts/cross_validate_em_proxy_result.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump({"summary": summary, "results": RESULTS}, f, ensure_ascii=False, indent=2)

print(f"\n详细结果: {output_path}")
