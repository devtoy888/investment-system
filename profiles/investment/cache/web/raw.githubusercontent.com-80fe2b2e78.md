"""A股全栈数据层 —— 移植自 a-stock-data 工具包（五层数据源，自包含）。

分级依赖：
 \- 行情（腾讯） : 仅需标准库 urllib —— 永远可用
 \- 研报（东财）\+ PDF : 仅需 requests —— 轻量必装
 \- 一致预期/新闻/公告 : akshare（惰性导入，缺失时优雅报错）
 \- K线/财务/F10 : mootdx（惰性导入，缺失时优雅报错）

合规：本模块只按用户传入的代码返回客观数据，不预置任何标的、不排名、不建议。
"""

from \_\_future\_\_ import annotations

import math
import os
import random
import re
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10\_15\_7) AppleWebKit/537.36"

def get\_prefix(code: str) -> str:
 """6 位代码 → 交易所前缀。5 开头是沪市基金/ETF（51/56/58 等），深市基金 15/16 开头走默认 sz。"""
 if code.startswith(("6", "9", "5")):
 return "sh"
 if code.startswith("8"):
 return "bj"
 return "sz"

class DependencyMissing(RuntimeError):
 """惰性依赖未安装时抛出，前端据此提示 pip install。"""

\# ---------------------------------------------------------------------------
\# Layer 1 · 行情（腾讯财经，仅标准库，不封 IP）
\# ---------------------------------------------------------------------------

def \_fetch\_gtimg(prefixed\_codes: list\[str\]) -> str:
 url = "https://qt.gtimg.cn/q=" + ",".join(prefixed\_codes)
 req = urllib.request.Request(url, headers={"User-Agent": UA})
 with urllib.request.urlopen(req, timeout=10) as resp:
 return resp.read().decode("gbk")

def \_parse\_gtimg(data: str) -> dict\[str, dict\]:
 result: dict\[str, dict\] = {}
 for line in data.strip().split(";"):
 if not line.strip() or "=" not in line or '"' not in line:
 continue
 key = line.split("=")\[0\].split("\_")\[-1\]
 vals = line.split('"')\[1\].split("~")
 if len(vals) < 53:
 continue
 code = key\[2:\]

 def num(i: int) -> float:
 try:
 return float(vals\[i\]) if vals\[i\] else 0.0
 except (ValueError, IndexError):
 return 0.0

 result\[code\] = {
 "name": vals\[1\],
 "price": num(3),
 "last\_close": num(4),
 "open": num(5),
 "change\_amt": num(31),
 "change\_pct": num(32),
 "high": num(33),
 "low": num(34),
 "amount\_wan": num(37),
 "turnover\_pct": num(38),
 "pe\_ttm": num(39),
 "amplitude\_pct": num(43),
 "mcap\_yi": num(44),
 "float\_mcap\_yi": num(45),
 "pb": num(46),
 "limit\_up": num(47),
 "limit\_down": num(48),
 "vol\_ratio": num(49),
 "pe\_static": num(52),
 }
 return result

def tencent\_quote(codes: list\[str\]) -> dict\[str, dict\]:
 """批量个股实时行情：现价 / 涨跌 / PE / PB / 市值 / 换手 / 涨跌停。"""
 prefixed = \[f"{get\_prefix(c)}{c}" for c in codes\]
 return \_parse\_gtimg(\_fetch\_gtimg(prefixed))

\# A股大盘指数（前缀规则与个股不同，固定带前缀代码）
A\_INDICES = \["sh000001", "sz399001", "sz399006", "sh000300"\]

def index\_quote() -> list\[dict\]:
 """A股大盘指数实时行情（上证/深证成指/创业板指/沪深300）。"""
 parsed = \_parse\_gtimg(\_fetch\_gtimg(A\_INDICES))
 out = \[\]
 for full in A\_INDICES:
 q = parsed.get(full\[2:\])
 if q:
 out.append({"name": q\["name"\], "price": q\["price"\], "change\_pct": q\["change\_pct"\], "change\_amt": q\["change\_amt"\]})
 return out

\# ---------------------------------------------------------------------------
\# Layer 2 · 研报（东财 reportapi，仅 requests）
\# ---------------------------------------------------------------------------

\_REPORT\_API = "https://reportapi.eastmoney.com/report/list"
\_PDF\_TPL = "https://pdf.dfcfw.com/pdf/H3\_{info\_code}\_1.pdf"

def \_report\_session():
 import requests # 轻依赖，随后端一起装

 s = requests.Session()
 s.headers.update({"User-Agent": UA, "Referer": "https://data.eastmoney.com/"})
 return s

def eastmoney\_reports(code: str, max\_pages: int = 3) -> list\[dict\]:
 """按个股代码拉研报列表（qType=0）。"""
 session = \_report\_session()
 out: list\[dict\] = \[\]
 for page in range(1, max\_pages + 1):
 params = {
 "industryCode": "\*", "pageSize": "100", "industry": "\*",
 "rating": "\*", "ratingChange": "\*",
 "beginTime": "2000-01-01", "endTime": "2030-01-01",
 "pageNo": str(page), "fields": "", "qType": "0",
 "orgCode": "", "code": code, "rcode": "",
 "p": str(page), "pageNum": str(page), "pageNumber": str(page),
 }
 r = session.get(\_REPORT\_API, params=params, timeout=30)
 d = r.json()
 rows = d.get("data") or \[\]
 if not rows:
 break
 out.extend(rows)
 if page >= (d.get("TotalPage", 1) or 1):
 break
 time.sleep(0.3)
 return out

def eastmoney\_industry\_reports(keywords: list\[str\] \| None = None, days: int = 90, max\_pages: int = 3) -> list\[dict\]:
 """按行业拉研报（qType=1）——适合产业链 / 主题级检索。keywords 在标题上过滤。"""
 from datetime import date, timedelta

 session = \_report\_session()
 end = date.today()
 begin = end - timedelta(days=days)
 out: list\[dict\] = \[\]
 for page in range(1, max\_pages + 1):
 params = {
 "industryCode": "\*", "pageSize": "100", "industry": "\*",
 "rating": "\*", "ratingChange": "\*",
 "beginTime": begin.isoformat(), "endTime": end.isoformat(),
 "pageNo": str(page), "fields": "", "qType": "1",
 "orgCode": "", "code": "", "rcode": "",
 }
 r = session.get(\_REPORT\_API, params=params, timeout=30)
 rows = r.json().get("data") or \[\]
 if not rows:
 break
 out.extend(rows)
 time.sleep(0.3)
 if keywords:
 out = \[r for r in out if any(k in r.get("title", "") for k in keywords)\]
 return out

def pdf\_url(info\_code: str) -> str:
 return \_PDF\_TPL.format(info\_code=info\_code)

\# ---------------------------------------------------------------------------
\# Layer 3/4/5 · akshare 惰性封装（一致预期 / 新闻 / 公告 / 基本面）
\# ---------------------------------------------------------------------------

def \_akshare():
 try:
 import akshare as ak
 return ak
 except ImportError as e:
 raise DependencyMissing("akshare 未安装：pip install akshare") from e

def profit\_forecast(code: str) -> list\[dict\]:
 """机构一致预期 EPS（同花顺）。"""
 ak = \_akshare()
 df = ak.stock\_profit\_forecast\_ths(symbol=code, indicator="预测年报每股收益")
 return df.to\_dict("records") if df is not None and not df.empty else \[\]

def stock\_news(code: str, limit: int = 20) -> list\[dict\]:
 """个股新闻（东财）。"""
 ak = \_akshare()
 df = ak.stock\_news\_em(symbol=code)
 return df.head(limit).to\_dict("records") if df is not None and not df.empty else \[\]

def individual\_info(code: str) -> dict:
 """个股基本面（东财）：行业 / 总股本 / 上市时间等。"""
 ak = \_akshare()
 df = ak.stock\_individual\_info\_em(symbol=code)
 if df is None or df.empty:
 return {}
 return {str(row\["item"\]): row\["value"\] for \_, row in df.iterrows()}

def disclosure(code: str) -> list\[dict\]:
 """巨潮公告全文列表（akshare cninfo，本环境不稳，保留作备用）。"""
 ak = \_akshare()
 market = "沪市" if code.startswith("6") else ("北交所" if code.startswith("8") else "深市")
 df = ak.stock\_zh\_a\_disclosure\_report\_cninfo(symbol=code, market=market)
 return df.head(30).to\_dict("records") if df is not None and not df.empty else \[\]

def announcements(code: str, limit: int = 15) -> list\[dict\]:
 """个股近期公告（东财公开接口，仅 requests，稳定）。返回 日期/标题/类型/详情链接。"""
 import requests

 r = requests.get(
 "https://np-anotice-stock.eastmoney.com/api/security/ann",
 params={"sr": -1, "page\_size": limit, "page\_index": 1, "ann\_type": "A",
 "client\_source": "web", "stock\_list": code, "f\_node": 0, "s\_node": 0},
 headers={"User-Agent": UA}, timeout=20,
 )
 lst = (r.json().get("data") or {}).get("list") or \[\]
 out = \[\]
 for a in lst:
 cols = \[c.get("column\_name") for c in (a.get("columns") or \[\]) if c.get("column\_name")\]
 art = a.get("art\_code", "")
 out.append({
 "date": (a.get("notice\_date", "") or "")\[:10\],
 "title": a.get("title", ""),
 "type": cols\[0\] if cols else "",
 "url": f"https://data.eastmoney.com/notices/detail/{code}/{art}.html" if art else "",
 })
 return out

\# ---------------------------------------------------------------------------
\# mootdx 惰性封装（K线 / 财务 / F10）
\# ---------------------------------------------------------------------------

def \_mootdx\_client():
 try:
 from mootdx.quotes import Quotes
 return Quotes.factory(market="std")
 except ImportError as e:
 raise DependencyMissing("mootdx 未安装：pip install mootdx") from e

def kline(code: str, category: int = 4, offset: int = 60) -> list\[dict\]:
 """K线：category 4=日 5=周 6=月 11=60分钟。"""
 client = \_mootdx\_client()
 df = client.bars(symbol=code, category=category, offset=offset)
 return df.to\_dict("records") if df is not None and not df.empty else \[\]

def finance(code: str) -> dict:
 """季报财务快照（37 字段）。"""
 client = \_mootdx\_client()
 df = client.finance(symbol=code)
 if df is None or (hasattr(df, "empty") and df.empty):
 return {}
 return df.to\_dict("records")\[0\] if hasattr(df, "to\_dict") else dict(df)

\# ---------------------------------------------------------------------------
\# 估值计算
\# ---------------------------------------------------------------------------

def calc\_peg(pe: float, cagr: float) -> float:
 if cagr <= 0:
 return float("inf")
 return pe / (cagr \* 100)

def pe\_digestion(current\_pe: float, cagr: float, target\_pe: float = 30) -> float:
 if current\_pe <= target\_pe:
 return 0.0
 if cagr <= 0:
 return float("inf")
 return math.log(current\_pe / target\_pe) / math.log(1 + cagr)

def financials(code: str) -> dict:
 """财务关键指标（同花顺财务摘要，最新报告期）—— 干净可靠的营收/净利/ROE/毛利率等。

 注：mootdx finance() 的营收/净利数值不可靠(实测放大数倍)，故财务摘要走此源。
 """
 ak = \_akshare()
 df = ak.stock\_financial\_abstract\_ths(symbol=code, indicator="按报告期")
 if df is None or df.empty:
 return {}
 row = df.iloc\[-1\].to\_dict() # 最新报告期（按报告期升序，取末行）

 def g(k):
 v = row.get(k)
 return None if v in (False, "false", "", None) else v

 return {
 "period": g("报告期"),
 "revenue": g("营业总收入"), "revenue\_yoy": g("营业总收入同比增长率"),
 "net\_profit": g("净利润"), "net\_profit\_yoy": g("净利润同比增长率"),
 "eps": g("基本每股收益"), "bvps": g("每股净资产"),
 "roe": g("净资产收益率"), "gross\_margin": g("销售毛利率"), "net\_margin": g("销售净利率"),
 "op\_cf\_ps": g("每股经营现金流"),
 }

def valuation\_percentile(code: str, period: str = "近五年") -> dict:
 """历史估值分位（百度股市通）：PE-TTM / PB 的当前值 + 历史 20/50/80 分位带 + 所处分位。

 只表达"处于历史什么位置"，不划买卖线（理杏仁式中立呈现）。
 """
 ak = \_akshare()

 def \_q(vals: list, p: float) -> float:
 if not vals:
 return 0.0
 idx = p \* (len(vals) - 1)
 lo = int(idx)
 if lo + 1 >= len(vals):
 return vals\[-1\]
 frac = idx - lo
 return vals\[lo\] \* (1 - frac) + vals\[lo + 1\] \* frac

 metrics = {}
 for key, ind in (("pe\_ttm", "市盈率(TTM)"), ("pb", "市净率")):
 try:
 df = ak.stock\_zh\_valuation\_baidu(symbol=code, indicator=ind, period=period)
 raw = df.iloc\[:, 1\].dropna().astype(float).tolist()
 if not raw:
 continue
 cur = float(raw\[-1\])
 s = sorted(raw)
 below = sum(1 for x in s if x < cur)
 metrics\[key\] = {
 "current": round(cur, 2),
 "percentile": round(below / max(len(s) - 1, 1) \* 100, 1),
 "min": round(s\[0\], 2), "max": round(s\[-1\], 2),
 "p20": round(\_q(s, 0.2), 2), "p50": round(\_q(s, 0.5), 2), "p80": round(\_q(s, 0.8), 2),
 "n": len(s),
 }
 except Exception:
 continue
 return {"period": "近5年", "metrics": metrics}

def full\_valuation(code: str) -> dict:
 """单票完整估值：腾讯行情 \+ 一致预期 EPS + 前向PE/PEG/消化年数。"""
 quotes = tencent\_quote(\[code\])
 q = quotes.get(code)
 if not q:
 raise ValueError(f"未取到 {code} 的行情")

 price = q\["price"\]
 out = {
 "name": q\["name"\], "code": code, "price": price,
 "mcap\_yi": q\["mcap\_yi"\], "pe\_ttm": q\["pe\_ttm"\], "pb": q\["pb"\],
 "eps\_26e": None, "eps\_27e": None, "pe\_26e": None,
 "cagr\_pct": None, "peg": None, "digest\_years": None, "analyst\_count": 0,
 }

 try:
 rows = profit\_forecast(code)
 except DependencyMissing:
 out\["forecast\_note"\] = "一致预期需安装 akshare"
 return out

 def \_eps(row: dict):
 # 同花顺对覆盖不全的股票会缺「均值」或给 '-' 占位，硬取会让整只票的估值接口 502
 try:
 return float(str(row.get("均值", "")).replace(",", ""))
 except ValueError:
 return None

 eps\_26 = eps\_27 = None
 for row in rows:
 y = str(row.get("年度", ""))
 if "2026" in y:
 eps\_26 = \_eps(row)
 try:
 out\["analyst\_count"\] = int(float(row.get("预测机构数") or 0))
 except (TypeError, ValueError):
 pass
 elif "2027" in y:
 eps\_27 = \_eps(row)

 out\["eps\_26e"\], out\["eps\_27e"\] = eps\_26, eps\_27
 if eps\_26 and eps\_26 > 0:
 pe\_26e = price / eps\_26
 out\["pe\_26e"\] = round(pe\_26e, 1)
 if eps\_27:
 cagr = eps\_27 / eps\_26 - 1
 out\["cagr\_pct"\] = round(cagr \* 100, 0)
 peg = calc\_peg(pe\_26e, cagr)
 out\["peg"\] = round(peg, 2) if peg != float("inf") else None
 dig = pe\_digestion(pe\_26e, cagr)
 out\["digest\_years"\] = round(dig, 1) if dig != float("inf") else None
 return out

\# ===========================================================================
\# Layer 3/4/10 · 资金面 / 筹码 / 信号（东财数据中心，移植自 a-stock-data v3.3）
#
\# 合规：以下端点全部按【用户传入的单个代码】返回该股的客观公开数据（龙虎榜记录、
\# 融资融券、大宗交易、股东户数、分红、资金流、解禁、板块归属、投资者问答），
\# 不预置标的、不做主观评分、不给买卖建议。
\# 定位调整（2026-07-05）：涨停池 / 全市场成交额榜等【客观公开榜单】现已用于产品 UI
\# （每日复盘的连板股 + 成交额 TOP20）——如实展示公开榜单≠荐股，只要不附推荐/评分/预测。
\# 仍不做：主观评分排名、买卖点位、涨跌预测；龙虎榜个股名单/强势股/人气榜等带隐性倾向的甩单暂不进 UI。
\# ===========================================================================

\_DATACENTER\_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
\_EM\_MIN\_INTERVAL = 1.0 # 两次东财请求最小间隔（秒），内置防封节流
\_em\_last\_call = \[0.0\]
\_EM\_SESSIONS: dict = {} # {direct(bool): requests.Session}

\# 数据层连接模式：国内财经站（东财/腾讯/新浪）本应「直连」——很多用户开着 Clash/V2Ray
\# 科学上网，系统代理会把东财这类国内站路由挂掉（典型：push2.eastmoney.com 的 CONNECT 被掐）。
\# 默认 auto：先试直连、失败再降级走系统代理；探测一次后固定，避免每次都重试。
\# 只有少数「必须靠代理才能出网」的环境需要 VR\_DATA\_PROXY=1 强制走代理。
\# 注意：这只影响数据层；AI 层（可能要调国外模型）仍走各自的系统代理，不受影响。
\_em\_mode = \["proxy" if os.environ.get("VR\_DATA\_PROXY", "").strip().lower() in ("1", "true", "yes") else "auto"\]

def \_em\_session(direct: bool):
 """东财专用会话。direct=True → \`trust\_env=False\` 忽略 HTTP(S)\_PROXY 环境变量、直连。

 直连会话不重试（探测要快，失败即降级）；代理会话保留瞬态错误退避重试。惰性构建、复用。
 """
 if direct in \_EM\_SESSIONS:
 return \_EM\_SESSIONS\[direct\]
 import requests

 s = requests.Session()
 s.headers.update({"User-Agent": UA})
 s.trust\_env = not direct # 直连会话不读环境里的代理配置
 try:
 from requests.adapters import HTTPAdapter
 from urllib3.util.retry import Retry

 retry = Retry(total=0) if direct else Retry(
 total=3, connect=3, backoff\_factor=0.6,
 status\_forcelist=\[429, 500, 502, 503, 504\], allowed\_methods=\["GET"\])
 adapter = HTTPAdapter(max\_retries=retry)
 s.mount("https://", adapter)
 s.mount("http://", adapter)
 except Exception:
 pass # 老版本 urllib3 缺参数时降级为无重试
 \_EM\_SESSIONS\[direct\] = s
 return s

def em\_get(url: str, params: dict \| None = None, headers: dict \| None = None, timeout: int = 15):
 """东财统一请求入口：串行限流 \+ \*\*直连优先、失败降级系统代理\*\*（避免科学上网代理挂掉国内站）。

 第一次请求探测：先直连（短超时、不重试），成功即固定走直连；失败则降级走系统代理并固定。
 探测结果整个进程复用，避免每次重试。\`VR\_DATA\_PROXY=1\` 可跳过探测、强制走代理。
 """
 wait = \_EM\_MIN\_INTERVAL - (time.time() - \_em\_last\_call\[0\])
 if wait > 0:
 time.sleep(wait + random.uniform(0.1, 0.5))
 try:
 mode = \_em\_mode\[0\]
 if mode != "auto":
 return \_em\_session(mode == "direct").get(url, params=params, headers=headers, timeout=timeout)
 # auto：先直连，成功固定 direct；直连失败再走系统代理、成功固定 proxy。
 try:
 r = \_em\_session(True).get(url, params=params, headers=headers, timeout=min(timeout, 8))
 \_em\_mode\[0\] = "direct"
 return r
 except Exception:
 r = \_em\_session(False).get(url, params=params, headers=headers, timeout=timeout)
 \_em\_mode\[0\] = "proxy"
 return r
 finally:
 \_em\_last\_call\[0\] = time.time()

\# ---------------------------------------------------------------------------
\# 打板层 · 涨停/炸板/跌停/昨涨停 原始池（东财 push2ex，走 em\_get 限流）
\# ⚠️ 合规：原始池含个股 code/name —— 仅供 market.py 聚合成【不含个股名】的短线情绪指标。
\# 切勿把原始池直接接成 API/UI（会甩个股名单、破产品「零标的」红线）。
\# ---------------------------------------------------------------------------
\_ZTB\_UT = "7eea3edcaed734bea9cbfc24409ed989"

def em\_zt\_topic\_pool(endpoint: str, date: str, sort: str = "fbt:asc") -> list\[dict\]:
 """东财涨停板行情中心原始池（push2ex）。
 endpoint: getTopicZTPool(涨停) / getTopicZBPool(炸板) / getTopicDTPool(跌停) / getYesterdayZTPool(昨涨停)
 date: YYYYMMDD 交易日。非交易日 / 参数错 → \[\]。
 池内每项字段含 lbc(连板数) / zbc(炸板次数) / hybk(行业) 等。"""
 url = f"https://push2ex.eastmoney.com/{endpoint}"
 params = {"ut": \_ZTB\_UT, "dpt": "wz.ztzt", "Pageindex": 0,
 "pagesize": 10000, "sort": sort, "date": date}
 headers = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
 try:
 r = em\_get(url, params=params, headers=headers, timeout=10)
 return (r.json().get("data") or {}).get("pool") or \[\]
 except Exception:
 return \[\]

def \_numf(v):
 """东财数值字段可能是 '-'（停牌/无数据）→ 归一成 float 或 None。"""
 return v if isinstance(v, (int, float)) else None

def market\_turnover\_rank(n: int = 20) -> list\[dict\]:
 """全市场成交额榜（沪深京 A 股按成交额降序 TopN）。

 东财行情中心 clist。\*\*push2(实时) 不可达时降级 push2delay(延迟行情，日榜场景足够)\*\*。
 返回每只: code / name / price / pct / amount(成交额,元) / mcap(总市值,元) /
 float\_cap(流通市值,元) / industry。
 ⚠️ 这是客观公开榜单数据（东财/同花顺同款），产品侧只做客观展示——非推荐、非预测、不评分。
 """
 params = {"pn": 1, "pz": n, "po": 1, "np": 1, "fltt": 2, "invt": 2, "fid": "f6",
 "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048",
 "fields": "f12,f14,f2,f3,f6,f20,f21,f100"}
 diff: list\[dict\] = \[\]
 for host in ("push2.eastmoney.com", "push2delay.eastmoney.com"):
 try:
 r = em\_get(f"https://{host}/api/qt/clist/get", params=params,
 headers={"User-Agent": UA}, timeout=12)
 diff = (r.json().get("data") or {}).get("diff") or \[\]
 if diff:
 break
 except Exception:
 continue
 return \[{\
 "code": str(d.get("f12", "")), "name": d.get("f14", ""),\
 "price": \_numf(d.get("f2")), "pct": \_numf(d.get("f3")),\
 "amount": \_numf(d.get("f6")), "mcap": \_numf(d.get("f20")),\
 "float\_cap": \_numf(d.get("f21")), "industry": d.get("f100", "") or "",\
 } for d in diff\]

def eastmoney\_datacenter(report\_name: str, columns: str = "ALL", filter\_str: str = "",
 page\_size: int = 50, sort\_columns: str = "", sort\_types: str = "-1") -> list\[dict\]:
 """东财数据中心统一查询 —— 龙虎榜/解禁/融资融券/大宗交易/股东户数/分红 共用（已内置限流）。"""
 params = {
 "reportName": report\_name, "columns": columns, "filter": filter\_str,
 "pageNumber": "1", "pageSize": str(page\_size),
 "sortColumns": sort\_columns, "sortTypes": sort\_types, "source": "WEB", "client": "WEB",
 }
 try:
 d = em\_get(\_DATACENTER\_URL, params=params, timeout=15).json()
 except Exception:
 return \[\]
 if d.get("result") and d\["result"\].get("data"):
 return d\["result"\]\["data"\]
 return \[\]

def margin\_trading(code: str, page\_size: int = 30) -> list\[dict\]:
 """融资融券明细（日级）：融资余额 / 融资买入 / 融券余额 / 两融合计。"""
 data = eastmoney\_datacenter(
 "RPTA\_WEB\_RZRQ\_GGMX", filter\_str=f'(SCODE="{code}")',
 page\_size=page\_size, sort\_columns="DATE", sort\_types="-1")
 return \[{\
 "date": str(r.get("DATE", ""))\[:10\],\
 "rzye": r.get("RZYE", 0), "rzmre": r.get("RZMRE", 0), "rzche": r.get("RZCHE", 0),\
 "rqye": r.get("RQYE", 0), "rqmcl": r.get("RQMCL", 0),\
 "rzrqye": r.get("RZRQYE", 0),\
 } for r in data\]

def block\_trade(code: str, page\_size: int = 20) -> list\[dict\]:
 """大宗交易：成交价 / 折溢价率 / 量 / 买卖方营业部。"""
 data = eastmoney\_datacenter(
 "RPT\_DATA\_BLOCKTRADE", filter\_str=f'(SECURITY\_CODE="{code}")',
 page\_size=page\_size, sort\_columns="TRADE\_DATE", sort\_types="-1")
 rows = \[\]
 for r in data:
 close = r.get("CLOSE\_PRICE") or 0
 deal = r.get("DEAL\_PRICE") or 0
 rows.append({
 "date": str(r.get("TRADE\_DATE", ""))\[:10\],
 "price": deal, "close": close,
 "premium\_pct": round((deal / close - 1) \* 100, 2) if close else 0,
 "vol": r.get("DEAL\_VOLUME", 0), "amount": r.get("DEAL\_AMT", 0),
 "buyer": r.get("BUYER\_NAME", ""), "seller": r.get("SELLER\_NAME", ""),
 })
 return rows

def holder\_num\_change(code: str, page\_size: int = 10) -> list\[dict\]:
 """股东户数变化（季度级）：户数 / 环比 / 户均持股。持续减少 = 筹码集中。"""
 data = eastmoney\_datacenter(
 "RPT\_HOLDERNUMLATEST", filter\_str=f'(SECURITY\_CODE="{code}")',
 page\_size=page\_size, sort\_columns="END\_DATE", sort\_types="-1")
 return \[{\
 "date": str(r.get("END\_DATE", ""))\[:10\],\
 "holder\_num": r.get("HOLDER\_NUM", 0),\
 "change\_ratio": r.get("HOLDER\_NUM\_RATIO", 0),\
 "avg\_shares": r.get("AVG\_FREE\_SHARES", 0),\
 } for r in data\]

def dividend\_history(code: str, page\_size: int = 20) -> list\[dict\]:
 """分红送转历史：每股派息（税前）/ 每10股转增 / 每10股送股 / 进度。"""
 data = eastmoney\_datacenter(
 "RPT\_SHAREBONUS\_DET", filter\_str=f'(SECURITY\_CODE="{code}")',
 page\_size=page\_size, sort\_columns="EX\_DIVIDEND\_DATE", sort\_types="-1")
 return \[{\
 "date": str(r.get("EX\_DIVIDEND\_DATE", ""))\[:10\],\
 "bonus\_rmb": r.get("PRETAX\_BONUS\_RMB", 0),\
 "transfer\_ratio": r.get("TRANSFER\_RATIO", 0),\
 "bonus\_ratio": r.get("BONUS\_RATIO", 0),\
 "plan": r.get("ASSIGN\_PROGRESS", ""),\
 } for r in data\]

def stock\_fund\_flow\_120d(code: str) -> list\[dict\]:
 """个股资金流（日级，最近 120 交易日）：主力 / 小单 / 中单 / 大单 / 超大单净流入（元）。"""
 market\_code = 1 if code.startswith("6") else 0
 params = {
 "secid": f"{market\_code}.{code}",
 "fields1": "f1,f2,f3,f7",
 "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65",
 "lmt": "120",
 }
 headers = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/", "Origin": "https://quote.eastmoney.com"}
 try:
 d = em\_get("https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get",
 params=params, headers=headers, timeout=15).json()
 except Exception:
 return \[\]
 rows = \[\]
 for line in d.get("data", {}).get("klines", \[\]):
 p = line.split(",")
 if len(p) >= 6:
 def \_f(x):
 try:
 return float(x) if x not in ("-", "") else 0.0
 except ValueError:
 return 0.0
 rows.append({
 "date": p\[0\], "main\_net": \_f(p\[1\]), "small\_net": \_f(p\[2\]),
 "mid\_net": \_f(p\[3\]), "large\_net": \_f(p\[4\]), "super\_net": \_f(p\[5\]),
 })
 return rows

def dragon\_tiger\_board(code: str, trade\_date: str \| None = None, look\_back: int = 30) -> dict:
 """龙虎榜：该股近期上榜记录 \+ 最近一次买卖席位 TOP5 + 机构专用席位净买。"""
 trade\_date = trade\_date or datetime.now().strftime("%Y-%m-%d")
 start = (datetime.strptime(trade\_date, "%Y-%m-%d") - timedelta(days=look\_back)).strftime("%Y-%m-%d")
 records = \[\]
 data = eastmoney\_datacenter(
 "RPT\_DAILYBILLBOARD\_DETAILSNEW",
 filter\_str=f'(TRADE\_DATE>=\\'{start}\\')(TRADE\_DATE<=\\'{trade\_date}\\')(SECURITY\_CODE="{code}")',
 page\_size=50, sort\_columns="TRADE\_DATE", sort\_types="-1")
 for r in data:
 records.append({
 "date": str(r.get("TRADE\_DATE", ""))\[:10\],
 "reason": r.get("EXPLANATION", ""),
 "net\_buy": round((r.get("BILLBOARD\_NET\_AMT") or 0) / 10000, 1), # 万元
 "turnover": round(float(r.get("TURNOVERRATE") or 0), 2),
 })

 seats = {"buy": \[\], "sell": \[\]}
 institution = {"buy\_amt": 0.0, "sell\_amt": 0.0, "net\_amt": 0.0}
 if records:
 latest = records\[0\]\["date"\]
 buy\_data = eastmoney\_datacenter(
 "RPT\_BILLBOARD\_DAILYDETAILSBUY",
 filter\_str=f'(TRADE\_DATE=\\'{latest}\\')(SECURITY\_CODE="{code}")',
 page\_size=10, sort\_columns="BUY", sort\_types="-1")
 sell\_data = eastmoney\_datacenter(
 "RPT\_BILLBOARD\_DAILYDETAILSSELL",
 filter\_str=f'(TRADE\_DATE=\\'{latest}\\')(SECURITY\_CODE="{code}")',
 page\_size=10, sort\_columns="SELL", sort\_types="-1")
 for r in buy\_data\[:5\]:
 seats\["buy"\].append({"name": r.get("OPERATEDEPT\_NAME", ""),
 "buy\_amt": round((r.get("BUY") or 0) / 10000, 1),
 "sell\_amt": round((r.get("SELL") or 0) / 10000, 1),
 "net": round((r.get("NET") or 0) / 10000, 1)})
 for r in sell\_data\[:5\]:
 seats\["sell"\].append({"name": r.get("OPERATEDEPT\_NAME", ""),
 "buy\_amt": round((r.get("BUY") or 0) / 10000, 1),
 "sell\_amt": round((r.get("SELL") or 0) / 10000, 1),
 "net": round((r.get("NET") or 0) / 10000, 1)})
 for detail, side in ((buy\_data, "buy"), (sell\_data, "sell")):
 for r in detail:
 if str(r.get("OPERATEDEPT\_CODE", "")) == "0": # 机构专用席位
 amt = (r.get("BUY") or 0) if side == "buy" else (r.get("SELL") or 0)
 institution\[f"{side}\_amt"\] += amt
 institution\["buy\_amt"\] = round(institution\["buy\_amt"\] / 10000, 1)
 institution\["sell\_amt"\] = round(institution\["sell\_amt"\] / 10000, 1)
 institution\["net\_amt"\] = round(institution\["buy\_amt"\] - institution\["sell\_amt"\], 1)
 return {"records": records, "seats": seats, "institution": institution}

def lockup\_expiry(code: str, trade\_date: str \| None = None, forward\_days: int = 90) -> dict:
 """限售解禁日历：历史解禁记录 \+ 未来 N 天待解禁事件。

 字段随东财 2026 改列名同步（a-stock-data §3.6）：旧 LIMITED\_STOCK\_TYPE/FREE\_SHARES\_NUM
 已废、致 type/shares 恒空 → 改 FREE\_SHARES\_TYPE/FREE\_SHARES，并补 able\_shares（实际可流通股数）。
 """
 trade\_date = trade\_date or datetime.now().strftime("%Y-%m-%d")
 history = \[{\
 "date": str(r.get("FREE\_DATE", ""))\[:10\], "type": r.get("FREE\_SHARES\_TYPE", ""),\
 "shares": r.get("FREE\_SHARES", 0), "able\_shares": r.get("ABLE\_FREE\_SHARES", 0),\
 "ratio": r.get("FREE\_RATIO", 0),\
 } for r in eastmoney\_datacenter(\
 "RPT\_LIFT\_STAGE", filter\_str=f'(SECURITY\_CODE="{code}")',\
 page\_size=15, sort\_columns="FREE\_DATE", sort\_types="-1")\]

 end = (datetime.strptime(trade\_date, "%Y-%m-%d") + timedelta(days=forward\_days)).strftime("%Y-%m-%d")
 upcoming = \[{\
 "date": str(r.get("FREE\_DATE", ""))\[:10\], "type": r.get("FREE\_SHARES\_TYPE", ""),\
 "shares": r.get("FREE\_SHARES", 0), "able\_shares": r.get("ABLE\_FREE\_SHARES", 0),\
 "ratio": r.get("FREE\_RATIO", 0),\
 } for r in eastmoney\_datacenter(\
 "RPT\_LIFT\_STAGE",\
 filter\_str=f'(SECURITY\_CODE="{code}")(FREE\_DATE>=\\'{trade\_date}\\')(FREE\_DATE<=\\'{end}\\')',\
 page\_size=20, sort\_columns="FREE\_DATE", sort\_types="1")\]
 return {"history": history, "upcoming": upcoming}

def concept\_blocks(code: str) -> dict:
 """个股所属板块/概念归属（东财 slist，行业/概念/地域混合，板块名自解释）。"""
 market\_code = 1 if code.startswith("6") else 0
 params = {"fltt": "2", "invt": "2", "secid": f"{market\_code}.{code}",
 "spt": "3", "pi": "0", "pz": "200", "po": "1", "fields": "f12,f14,f3,f128"}
 headers = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
 try:
 d = em\_get("https://push2.eastmoney.com/api/qt/slist/get", params=params, headers=headers, timeout=15).json()
 except Exception:
 return {"total": 0, "boards": \[\], "concept\_tags": \[\]}
 diff = (d.get("data") or {}).get("diff") or {}
 items = diff.values() if isinstance(diff, dict) else diff
 boards = \[{"name": it.get("f14", ""), "code": it.get("f12", ""),\
 "change\_pct": it.get("f3", ""), "lead\_stock": it.get("f128", "")} for it in items\]
 return {"total": len(boards), "boards": boards, "concept\_tags": \[b\["name"\] for b in boards\]}

def hot\_concepts(code: str) -> list\[dict\]:
 """个股当下被市场归到哪些概念在炒（东财热门概念命中，按热度降序）。"""
 import requests

 try:
 prefix = "SH" if code.startswith("6") else "SZ"
 r = requests.post(
 "https://emappdata.eastmoney.com/stockrank/getHotStockRankList",
 json={"appId": "appId01", "globalId": "786e4c21-70dc-435a-93bb-38", "srcSecurityCode": prefix + code},
 headers={"User-Agent": UA}, timeout=10)
 data = r.json().get("data") or \[\]
 except Exception:
 return \[\]
 return \[{"concept": x.get("conceptName"), "bk": x.get("conceptId"), "hit": x.get("hitCount")} for x in data\]

def investor\_qa(code: str, page\_size: int = 30) -> list\[dict\]:
 """互动易问答（巨潮）：投资者提问 \+ 公司回复（answer=None 表示未回复）。"""
 import requests

 try:
 r1 = requests.post("https://irm.cninfo.com.cn/newircs/index/queryKeyboardInfo",
 data={"keyWord": code}, headers={"User-Agent": UA}, timeout=10)
 d1 = r1.json().get("data") or \[\]
 if not d1:
 return \[\]
 org\_id = d1\[0\].get("secid")
 params = {"\_t": 1, "stockcode": code, "orgId": org\_id, "pageSize": page\_size,
 "pageNum": 1, "keyWord": "", "startDay": "", "endDay": ""}
 rows = requests.post("https://irm.cninfo.com.cn/newircs/company/question",
 params=params, headers={"User-Agent": UA}, timeout=10).json().get("rows") or \[\]
 except Exception:
 return \[\]
 out = \[\]
 for it in rows:
 ts = it.get("pubDate")
 out.append({
 "company": it.get("companyShortName"),
 "question": it.get("mainContent"), "answer": it.get("attachedContent"),
 "answerer": it.get("attachedAuthor"),
 "ask\_time": datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M") if ts else "",
 })
 return out

def industry\_comparison(top\_n: int = 20) -> dict:
 """全行业涨跌幅排名（东财行业板块，~100 个行业）：板块级涨跌 / 涨跌家数 / 领涨。"""
 params = {"pn": "1", "pz": "100", "po": "1", "np": "1", "fltt": "2", "invt": "2",
 "fid": "f3", # fid=f3 + po=1：按涨跌幅降序，否则 top/bottom 切片非涨幅序（a-stock-data §3.7）
 "fs": "m:90+t:2", "fields": "f2,f3,f4,f12,f13,f14,f104,f105,f128,f136,f140,f141,f207"}
 try:
 d = em\_get("https://push2.eastmoney.com/api/qt/clist/get",
 params=params, headers={"User-Agent": UA}, timeout=15).json()
 except Exception:
 return {"top": \[\], "bottom": \[\], "total": 0}
 items = d.get("data", {}).get("diff", \[\])
 if isinstance(items, dict):
 items = list(items.values())
 if not items:
 return {"top": \[\], "bottom": \[\], "total": 0}
 rows = \[{\
 "rank": i + 1, "name": it.get("f14", ""), "change\_pct": it.get("f3", 0),\
 "code": it.get("f12", ""), "up\_count": it.get("f104", 0), "down\_count": it.get("f105", 0),\
 } for i, it in enumerate(items)\]
 return {"top": rows\[:top\_n\], "bottom": rows\[-top\_n:\], "total": len(rows)}