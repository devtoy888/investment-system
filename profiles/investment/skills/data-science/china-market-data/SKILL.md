---
name: china-market-data
description: 中国A股/基金市场数据采集 — 腾讯行情(不封IP) + 天天基金净值 + mootdx(通达信TCP) + 东财(限流)数据接口，零API Key，pip安装即用。
origin: custom
---

# 中国金融市场数据采集

A股行情、基金净值、ETF、指数、资金流向等数据的一站式采集方案，全部免费、零API Key。

## 触发条件

- 用户需要拉取A股/基金/ETF/指数行情
- 用户需要基金净值或实时估值
- 用户需要北向资金、龙虎榜等市场信号
- 用户需要构建定时数据采集流水线

## 依赖安装

```bash
pip install mootdx requests pandas stockstats
```

## 数据源优先级

| 优先级 | 数据源 | 协议 | 封IP风险 | 用途 |
|-------|--------|------|---------|------|
| 1 | **腾讯财经** | HTTP | **不封** | 实时价/PE/PB/市值/指数/ETF - 首选 |
| 2 | **天天基金** | HTTP | 低 | 基金净值/实时估值 |
| 3 | **AKShare** | HTTP | 低 | 基金实时估值/北向资金/板块资金流向/历史净值（`pip install akshare`） |
| 4 | **mootdx(通达信)** | TCP 7709 | **不封** | K线/五档/财务(海外IP可能超时) |
| 5 | 东财(限流) | HTTP | 有风控 | 龙虎榜/北向/资金流/研报(已内置限流)。**push2涨跌家数海外IP必502，改用push2delay** |
| 6 | 同花顺 | HTTP | 极低 | 热点题材 |
| 7 | 新浪tags | HTTP | 极低 | **涨跌家数/北向资金备援** — 文本提取，非结构化API |

> **核心原则：** 能用腾讯/天天就不用东财。东财push2近期502。所有数据源必须实现多级降级。
>
> **⚠️ 实际可用率（2026-07实测，560条追踪记录）：**
> - 腾讯行业ETF批量：**99.2%** ✅ → 最可靠（优先用）
> - 腾讯成交额field[35]：**95.8%** ✅
> - 天天基金净值：~94% ✅
> - 同花顺hexin北向：**52.5%** ⚠️ → 需备援
> - **东财push2涨跌家数：22.7%** ❌ → 应降级，AKShare主源替代
>
> **涨跌家数**: AKShare全量A股 → 东财push2 → 新浪tags → 快照
> **北向资金**: hexin → AKShare官方 → 新浪tags → 快照
> **基金净值**: 天天基金 → AKShare(备援, 需pip install) → None

## 关键API（已验证可用的）

### 1. 腾讯财经实时行情（不封IP）

```python
import requests

def get_tencent_quote(code):
    """获取个股/指数/ETF实时行情"""
    url = f"https://qt.gtimg.cn/q={code}"
    r = requests.get(url, timeout=5)
    line = r.text.strip().rstrip(';')
    if '="' in line:
        parts = line.split('="')[1].rstrip('"').split('~')
        return {
            'name': parts[1],
            'price': parts[3],
            'change_pct': parts[32],      # 涨跌幅%
            'change_amt': parts[31],       # 涨跌额
            'open': parts[5],
            'high': parts[33],
            'low': parts[34],
            'volume': parts[6],
            'turnover': parts[37],         # 换手率
            'pe': parts[39],               # 动态市盈率
            'pb': parts[46],               # 市净率
            'market_cap': parts[45],       # 总市值
            'float_cap': parts[44],        # 流通市值
        }
    return None
```

**代码前缀规则：** 6/9开头 → `sh`, 8开头 → `bj`, 其他 → `sz`

**批量化查询（重要提速技巧）：** 腾讯支持一次HTTP请求查多个标的，用逗号分隔。10个ETF一次返回约180ms，逐个查询需~1.5s。适用于定时采集脚本避免超时。

```python
def batch_tencent_quotes(codes: list[str]) -> dict[str, dict]:
    """批量查询Tencent行情，返回 {code: {name, price, change_pct, ...}}
    注意：返回的code字段[2]不带sh/sz前缀（如'159813'而非'sz159813'）"""
    url = f"https://qt.gtimg.cn/q={','.join(codes)}"
    r = requests.get(url, timeout=8)
    lines = r.text.strip().rstrip(';').split(';')
    results = {}
    for line in lines:
        if '=\"' not in line:
            continue
        parts = line.split('=\"')[1].rstrip('\"').split('~')
        if len(parts) < 32:
            continue
        code = parts[2]  # 纯数字，不带sh/sz前缀
        results[code] = {
            'name': parts[1],
            'price': parts[3],
            'change_pct': float(parts[32]),
            'volume': parts[6],
            'change_amt': parts[31],
            'high': parts[33] if len(parts) > 33 else '',
            'low': parts[34] if len(parts) > 34 else '',
        }
    return results
```

**指数成交额提取（field[35]技巧）：** 腾讯对指数（sh000001/sh000002等）的field[35]格式为 `price/volume/turnover`，第三段是成交额(元)。可用于计算两市总成交额。

```python
def parse_index_turnover(tencent_line: str) -> float:
    """从腾讯指数行情提取成交额（元）"""
    if '=\"' not in tencent_line:
        return 0.0
    parts = tencent_line.strip().rstrip(';').split('=\"')[1].rstrip('\"').split('~')
    f35 = parts[35] if len(parts) > 35 else ''
    if '/' in f35:
        try:
            return float(f35.split('/')[2])  # 第三段=成交额(元)
        except (ValueError, IndexError):
            pass
    return 0.0

# 用法：上证A股成交额 = parse_index_turnover(腾讯返回sh000002)
#      深证成交额 = parse_index_turnover(腾讯返回sz399001)
#      两市合计 = 上证 + 深证
```

**常用代码扩展：**
| 标的 | 代码 |
|------|------|
| 上证指数 | `sh000001` |
| A股指数 | `sh000002`（统计上证成交额用） |
| 深证成指 | `sz399001`（统计深证成交额用） |
| 创业板指 | `sz399006` |
| 科创50 | `sh000688` |
| 沪深300 | `sh000300` |
| 上证50 | `sh000016` |
| 黄金ETF | `sz159934` |
| 行业ETF | 见 `references/sector-etf-codes.md` |

### 2. 天天基金净值/实时估值（免费）

```python
import requests, json

def get_fund_value(fund_code):
    """获取基金当日净值+实时估算"""
    url = f"https://fundgz.1234567.com.cn/js/{fund_code}.js"
    r = requests.get(url, timeout=5,
        headers={'Referer': 'https://fund.eastmoney.com/'})
    txt = r.text.strip()
    if 'jsonpgz(' in txt:
        data = json.loads(txt[txt.index('(')+1:txt.rindex(')')])
        return {
            'name': data.get('name'),
            'nav': data.get('dwjz'),           # 昨日净值
            'estimated_nav': data.get('gsz'),   # 实时估算净值
            'estimated_change': data.get('gszzl'),  # 估算涨幅%
            'nav_date': data.get('jzrq'),       # 净值日期
        }
    return None
```

### 3. mootdx 通达信TCP（含BESTIP修复）

> **已知Bug (mootdx 0.11.x):** 全新安装后`Quotes.factory()`可能抛`ValueError`。用下面helper规避。

```python
import socket
from mootdx.quotes import Quotes

_TDX_SERVERS = [
    ('119.97.185.59', 7709), ('124.70.133.119', 7709), ('116.205.183.150', 7709),
    ('123.60.73.44', 7709),  ('116.205.163.254', 7709), ('121.36.225.169', 7709),
    ('123.60.70.228', 7709), ('124.71.9.153', 7709),    ('110.41.147.114', 7709),
    ('124.71.187.122', 7709),
]

def tdx_client(market='std'):
    for ip, port in _TDX_SERVERS:
        try:
            with socket.create_connection((ip, port), timeout=2):
                return Quotes.factory(market=market, server=(ip, port))
        except Exception:
            continue
    # fallback
    try: return Quotes.factory(market=market, bestip=True)
    except Exception: pass
    raise RuntimeError("所有mootdx服务器不可达，海外网络通常全部超时")
```

### 4. 东财统一限流入口

```python
import time, random
import requests

EM_SESSION = requests.Session()
EM_SESSION.headers.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
EM_MIN_INTERVAL = 1.0
_em_last_call = [0.0]

def em_get(url, params=None, headers=None, timeout=15):
    """东财统一请求入口：自动节流+复用session"""
    wait = EM_MIN_INTERVAL - (time.time() - _em_last_call[0])
    if wait > 0:
        time.sleep(wait + random.uniform(0.1, 0.5))
    try:
        return EM_SESSION.get(url, params=params, headers=headers, timeout=timeout)
    finally:
        _em_last_call[0] = time.time()
```

### 5. 涨跌家数 — 东财push2delay + 新浪tags备援

**主源: 东财push2delay**（海外IP用push2delay，不用push2！）

> **🔴 push2.eastmoney.com 海外IP必502（2026-07-18交叉验证结论）：**
> - push2 和 push2delay 解析到同一IP (`120.79.191.232`)，是 nginx vhost geo-block
> - 换UA/Referer/超时/HTTP协议均无效 — 7种组合全502
> - **解决方案：`push2.eastmoney.com` → `push2delay.eastmoney.com`**，API字段完全兼容
> - 详细验证报告见 `references/push2-geo-block-cross-validation.md`

```python
import requests
# ✅ 海外IP用push2delay（已验证200），国内IP两者皆可
OVERSEAS_PUSH2_URL = 'https://push2delay.eastmoney.com/api/qt/stock/get?secid=1.000001&fields=f57,f58,f167,f168,f169,f170,f171'
# ❌ push2.eastmoney.com 海外IP 100% 502
r = requests.get(OVERSEAS_PUSH2_URL, timeout=8,
    headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://quote.eastmoney.com/'})
data = r.json().get('data', {})
rise = int(data.get('f169', 0)); fall = int(data.get('f170', 0))
```

**备援: 新浪tags文本提取**

东财push2经常返回502（不仅是海外超时，国内也有此问题）。备援从新浪tags页面提取涨跌家数文本：

```python
import re, requests
r = requests.get('https://tags.sina.com.cn/finance_beixiangzijin',
    headers={'User-Agent': 'Mozilla/5.0'}, timeout=8)
html = r.text
m_up = re.search(r'(?:超|约|共|近|达)?(\d+)只个股上涨', html)
m_down = re.search(r'(?:超|约|共|近|达)?(\d+)只个股下跌', html)
if m_up: rise = int(m_up.group(1))
if m_down: fall = int(m_down.group(1))
# 验证：总数>1000视为有效，否则偏少可能不准
```

**三级降级链**: 东财push2(502) → 新浪tags文本提取(~4200涨/4600跌) → 昨日快照 → None

### 6. 北向资金 — 同花顺hexin + 新浪tags备援

**主源: 同花顺hexin**（不稳定，约50%超时+格式变化）

hexin数据中心提供沪深股通实时分钟级北向资金数据，262个时间点。**注意：实际使用发现 `list index out of range` 错误频繁**，需备援。

```python
import requests
r = requests.get('https://data.hexin.cn/market/hsgtApi/method/dayChart/',
    headers={'User-Agent':'Mozilla/5.0','Host':'data.hexin.cn','Referer':'https://data.hexin.cn/'},
    timeout=10)
d = r.json()
times = d.get('time', []); hgt = d.get('hgt', []); sgt = d.get('sgt', [])
for i in range(len(times)-1, -1, -1):
    if times[i] and hgt[i] is not None and sgt[i] is not None:
        return {'hgt': hgt[i], 'sgt': sgt[i], 'total': (hgt[i] or 0)+(sgt[i] or 0), 'time': times[i]}
```

**备援: 新浪tags每日净流入提取**

从新浪tags新闻页面提取北向资金每日总额（不在行情页面，而是在新闻聚合页）：

```python
import re, requests
r = requests.get('https://tags.sina.com.cn/finance_beixiangzijin',
    headers={'User-Agent':'Mozilla/5.0'}, timeout=10)
html = r.text
all_m = list(re.finditer(r'北向资金\s*(?:今天|昨日|当日|合计)?\s*净([买卖出入]+)\s*([\d.]+)\s*亿', html))
# 取金额最接近10-100亿的（每日总流入通常在10-100亿范围），排除万元级个股数据
best = min([m for m in all_m if 1 <= float(m.group(2)) <= 200],
           key=lambda m: abs(float(m.group(2)) - 50))
```

**关键正则技巧（已踩坑记录）**: (1) `[买卖出入]` 必须含'入'字，因为"买入"是两个字符 买+入，`[买卖出]` 只匹配到'买'，遇到'入'就失败了（被用户纠正过）；(2) 只匹配亿级金额(1-200亿范围过滤)，页面同时有万元级个股数据需排除；(3) 匹配后还有 `!` 或 `！`：文本是"北向资金今天净买入10.45亿!..."，亿后面跟的是感叹号。正则 `\s*亿` 后要加 `[!.\s<]` 或改为只要求亿后面是非汉字字符即可匹配。

**备援2: 东财push2**（返回数据格式不明确/清零，暂不可靠）

```python
em_url = 'https://push2.eastmoney.com/api/qt/kamt.kline/get?fields1=f1,f3,f5&fields2=f51,f52,f53,f54,f55&klt=1&lmt=1'
r = requests.get(em_url, headers=HEADERS, timeout=8)
kl = r.json().get('data', {}).get('klines', [])
# 注意：数据格式为 [date, val1, val2, val3]，val2=5200000.00(单位不明)，非直接可用格式
```

**四级降级链**: 同花顺hexin(超时/格式错) → 新浪tags(26.45亿✅) → 东财push2(格式不明) → 昨日快照文件

### 8. AKShare 数据源（免费备援）

[AKShare](https://github.com/akfamily/akshare) 是开源A股数据接口，无需注册token，`pip install akshare` 即用。覆盖基金实时估值、板块资金流向、北向资金、历史净值等。

**优点：** 零配置、中文数据全、覆盖基金/ETF/板块/北向/宏观经济。  
**缺点：** 依赖较多（pandas/numpy/lxml等），首次安装较慢(~2分钟)，包较大(~100MB)。

#### 8.1 关键API（开放式基金 vs ETF 区分）

**注意：** 开放式基金（代码如017103、011103）和场内ETF（代码如159813）使用不同的AKShare API，不要混用。

```python
import akshare as ak
os.environ["TQDM_DISABLE"] = "1"  # 关闭进度条（非交互环境）

# ── 开放式基金实时估值（替代天天基金）──
# fund_value_estimation_em() 返回全市场基金实时估值（约20000条），慢
# fund_open_fund_info_em() 返回单只基金历史净值，快
# ★ 必须动态匹配列名，AKShare列名含日期（如"2026-07-17-估算数据-估算增长率"）
from datetime import date
today_str = date.today().isoformat()
df = ak.fund_value_estimation_em()                     # 全量实时估值(慢, ~40s)
row = df[df["基金代码"] == "017103"]                    # 筛选单只
est_col = [c for c in df.columns if "估算增长率" in c]  # ← 动态匹配！
est = row.iloc[0][est_col[0]] if est_col else "0"       # 实时估算涨跌幅

# ── 开放式基金历史净值（快，用于决策日志/因子分析）──
df = ak.fund_open_fund_info_em(symbol="017103", indicator="单位净值走势")
latest = df.iloc[-1]                                   # 最近交易日
nav = float(latest["单位净值"])                          # 单位净值
change = float(latest["日增长率"])                       # 日增长率%

# ── ETF/LOF实时行情（仅场内基金）──
# 注意：017103等场外基金不在此表
df = ak.fund_etf_spot_em()                             # 全部ETF+LOF
row = df[df['代码'] == '159813']                       # 半导体ETF
price = float(row.iloc[0]['最新价'])

# ── 北向资金（可替代hexin/新浪tags）──
df = ak.stock_hsgt_fund_flow_summary_em()              # 北向资金日度汇总
north_df = df[df['资金方向'] == '北向']
hgt = north_df[north_df['板块'].str.contains('沪')]['成交净买额'].sum()
sgt = north_df[north_df['板块'].str.contains('深')]['成交净买额'].sum()

# ── 板块资金流向（新增能力，天天基金无此接口）──
df = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="行业资金流向")

# ── 基金基本信息查询 ──
df = ak.fund_name_em()                                 # 27271只基金名称+类型
```

#### 8.2 Docker容器安装 + 持久化

Hermes容器（Docker）中，`/opt/hermes/.venv/` 是root用户创建，pip install会因权限失败。**推荐用 `--target` 安装到持久化目录：**

```bash
# 进容器
docker exec -it hermes-main bash

# 安装到持久化目录（容器重启/更新不丢）
pip install --target /opt/data/akshare-deps akshare
exit
```

**代码端适配：** 在AKShare适配器/调用模块的顶部加上sys.path注入，无需修改docker-compose或PYTHONPATH：

```python
# ── AKShare 查找路径（支持Docker独立目录安装）──
_AKSHARE_DEPS = "/opt/data/akshare-deps"
if os.path.isdir(_AKSHARE_DEPS) and _AKSHARE_DEPS not in sys.path:
    sys.path.insert(0, _AKSHARE_DEPS)

# 关掉进度条
os.environ["TQDM_DISABLE"] = "1"

try:
    import akshare as ak
    HAS_AKSHARE = True
except ImportError:
    HAS_AKSHARE = False  # 优雅降级，系统照常工作
```

**依赖冲突注意：** akshare 会安装 certifi/requests/rich 等新版本，与 Hermes 原有包冲突。用 `--target` 安装到隔离目录 + sys.path注入可以隔离冲突。

#### 8.4 硬编码日期陷阱（CRITICAL）

AKShare的实时估算API列名包含日期（如`2026-07-15-估算数据-估算增长率`），**绝对不能硬编码**：

```python
# ❌ 错误：硬编码日期→跨天后永久失效
est = row.iloc[0]["2026-07-15-估算数据-估算增长率"]

# ✅ 正确：动态匹配列名
today_str = date.today().isoformat()
est_col = [c for c in df.columns if "估算增长率" in c]
nav_col = [c for c in df.columns if "单位净值" in c and today_str[:7] in c]
est = float(row.get(est_col[0] if est_col else "", "0").replace("%", "") or 0)
nav = float(row.get(nav_col[0], 0) or 0) if nav_col else 0
```

> **实证（2026-07-18发现）：** `fund_source_akshare.py` 硬编码了`"2026-07-15-估算数据-估算增长率"`，2026-07-16之后该备援路径**永久返回None**，而主路径天天基金成功时这个bug被静默吞掉——直到天天基金也失败时才会暴露。**所有备援路径必须用真实数据跑一轮验证。**

#### 8.5 AKShare备援增强：涨跌家数和北向资金

AKShare已安装在 `/opt/data/akshare-deps`，但以下备援路径需要手动接通才能在fund_tools.py中生效：

```python
# 在主采集函数get_market_overview()中增加AKShare备援
def get_market_breadth_akshare():
    import akshare as ak
    df = ak.stock_zh_a_spot_em()
    if df is not None and not df.empty:
        rise = int((df['涨跌幅'] > 0).sum())
        fall = int((df['涨跌幅'] < 0).sum())
        return {'rise': rise, 'fall': fall}
    return None

# 在主采集函数get_northbound_flow()中增加AKShare备援
def get_northbound_akshare():
    # ── 北向资金（可替代hexin/新浪tags）──
    df = ak.stock_hsgt_fund_flow_summary_em()              # 北向资金日度汇总（注意：stock_hsgt_north_net_flow_in_em在AKShare 1.18.64不存在）
    north_df = df[df['资金方向'] == '北向']
    hgt = north_df[north_df['板块'].str.contains('沪')]['成交净买额'].sum()
    sgt = north_df[north_df['板块'].str.contains('深')]['成交净买额'].sum()
```

| 文件 | 职责 |
|:-----|:------|
| `fund_source_akshare.py` | AKShare API 封装 + 优雅降级 + sys.path注入 |
| `fund_tools.py` | 主数据采集，末尾调用 akshare 适配器做备援 |

在 `get_fund_value()` 的 exception handler 中增加备援调用：

```python
# 备援: AKShare
try:
    from fund_source_akshare import get_fund_realtime
    ak_data = get_fund_realtime(fund_code)
    if ak_data:
        return {'code': code, 'nav': ..., 'estimated_change': ..., 'change_source': 'akshare'}
except Exception:
    pass
```

**注意：** `get_fund_realtime()` 内部含两层备援：(A) `fund_value_estimation_em()` 全量实时估值（10秒超时）→ (B) `fund_open_fund_info_em()` 历史净值（快但只给昨日数据）。方案A超时时自动回退到方案B。

| 返回值 | 数据新鲜度 | 速度 |
|:-------|:----------|:----:|
| source=akshare_est | 当日实时估算 | 慢(~40s, 受超时保护) |
| source=akshare_hist | 上一交易日净值 | 快(<1s) |

## 数据源降级架构（2026-07-15新增）

中文金融API极其不稳定，每个数据源必须实现多级降级：

```python
try:
    result = PRIMARY_SOURCE()        # 主源
    if validate(result): return result
except:
    result = FALLBACK_SOURCE_A()     # 备援1（新浪tags/AKShare）
    if validate(result): return result
except:
    result = CACHE_OR_SNAPSHOT()     # 备援2（昨日快照）
    if validate(result): return result
return None  # 标注数据不足
```

### 实际降级链路（2026-07-18已验证，按可用率排序）

| 数据 | 首选源 | 备援1 | 备援2 | 备援3 | 末路 |
|:-----|:-------|:------|:------|:------|:-----|
| 基金净值 | 天天基金(8s+重试) | AKShare实时估算(10s超时) | AKShare历史净值(<1s) | — | None |
| 涨跌家数 | **AKShare全量A股(10s)** | 东财push2(15s,仅22.7%可用) | 新浪tags文本(8s,4种正则模式) | 同花顺(8s) | 昨日快照 |
| 北向资金 | 同花顺hexin(8s×2,仅52.5%) | **AKShare汇总(8s)** | 新浪tags新闻提取(8s) | 东财push2(8s) | 昨日快照 |
| 成交额 | 腾讯field[35](5s) | AKShare板块资金流(8s) | — | — | 0 |
| 外盘 | Yahoo Finance(8s×4并发) | 新浪美股(8s) | — | — | None |

> **涨跌家数备援链选择理由（2026-07-18实测）：** 东财push2海外IP仅22.7%可用率，而AKShare `stock_zh_a_spot_em()` 在交易日稳定95%+，因此首选改为AKShare。东财push2降为备援1（超时从8s→15s+重试2次）。新浪tags正则扩展为4种模式解决格式变化问题。

### 新浪tags文本提取经验

新浪tags页面(`https://tags.sina.com.cn/finance_beixiangzijin`)是新闻聚合页，非结构化API，通过正则提取关键数据：

1. **涨跌家数** — `(?:超|约|共|近|达)?(\d+)只个股上涨` / `...下跌`。验证条件：总数>1000才有效。
2. **北向资金** — `北向资金\s*(?:今天|昨日|当日|合计)?\s*净([买卖出入]+)\s*([\d.]+)\s*亿`。注意：(a) 用`[买卖出入]`含'入'字匹配\"买入\"; (b) 只匹配亿级(1-200亿范围); (c) 选最接近50亿的匹配过滤个股级噪声。
3. **正则调试**：Python中`[买卖出]`不包含`入`，`净买入`的`入`导致匹配失败。用`[买卖出入]`解决。

当构建定时采集流水线时，推荐加入 `track_source()` + 周度验证脚本：

1. 每次API调用后调用 `track_source('数据源名', success_bool, detail_str)`，写入JSONL追踪文件
2. 每周运行验证脚本，计算每个数据源的可用率
3. 连续14天可用率 < 50% → 建议移除该数据源

```python
def track_source(name: str, success: bool, detail: str = ""):
    record = {
        '_ts': datetime.now().isoformat(),
        '_date': date.today().isoformat(),
        'source': name,
        'success': success,
        'detail': detail[:200],
    }
    with open('fund_system_data/_source_availability.jsonl', 'a') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
```

## 非交易日API行为与数据新鲜度（2026-07-18新增）

### 各API非交易日行为速查表

| 数据源 | 非交易日行为 | 风险 | 处理建议 |
|:-------|:------------|:----:|:---------|
| **腾讯行情** | 静默返回上周五收盘数据(price=prev_close, change_pct=历史涨跌) | 🔴 | 必须加is_trading_day前置检查；输出加stale=True |
| **天天基金** | 正确返回jzrq!=today，已有stale标记 | ✅ | 持续使用现有stale字段 |
| **东财push2** | 非交易日也返回502（和平常一样） | 🟡 | 502视为正常，不额外处理 |
| **新浪tags** | 返回旧新闻文本，时效不可靠 | 🔴 | 输出必须结合交易日历判断 |
| **Yahoo Finance** | 外盘不受A股假日影响，美股夜盘仍有数据 | ✅ | 外盘独立于A股交易日判断 |

### 腾讯API的"静默返回旧数据"陷阱

腾讯API与mootdx TCP/同花顺HTTP不同——后两者在非交易日主动返回空值。腾讯是行情展示接口，非交易日返回最近交易日数据且不做无数据标记。这是引用仓库(a-stock-data, Vibe-Trading)不需要处理但我们必须处理的根本原因。

### 数据源可用率 vs 数据新鲜度（两个独立维度）

当前track_source只追踪API是否返回数据（可用率），不追踪数据是否新鲜（新鲜度）。两者完全不同：API返回502可用率下降；API 200返回上周五数据可用率上升但数据不可用。

### 验证铁律（防本session错误重现）

1. 非交易日只能验证API结构和错误处理，不能验证数值准确性
2. 交易日必须交叉对照（腾讯 vs AKShare 偏差>1%告警）
3. 验证报告必须标注验证时间和交易日状态

实战：2026-07-18周六验证拿到的所有数据都是上周五缓存，不能作为准确性证据。

## 涨跌颜色约定（A股惯例）

推送给用户时，用 emoji 标注涨跌必须符合 A股/国内习惯：
- **🔴 = 上涨**（红色代表涨）
- **🟢 = 下跌**（绿色代表跌）
- **🟡 = 持平**

这是 A 股惯例（与美股相反），用户会纠正你。所有行情展示、基金分组、持仓概览都必须遵守。

## 外盘行情（Yahoo Finance）

非A股数据（美股指数、黄金期货、美元等）使用 Yahoo Finance API，零配置。

**⚠️ 数据新鲜度标记（2026-07-18新增）：** 利用Yahoo返回的`regularMarketTime`时间戳动态判断，**不依赖硬编码日历**——任何市场、任何节假日都自动适配：

```python
import requests
from datetime import datetime, timezone

def get_overnight_quotes():
    symbols = {
        '道琼斯': '^DJI', '标普500': '^GSPC', '纳斯达克': '^IXIC',
        '黄金期货': 'GC=F', '美元指数': 'DX-Y.NYB',
    }
    result = {}
    for name, symbol in symbols.items():
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
        r = requests.get(url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        data = r.json()
        meta = data['chart']['result'][0]['meta']
        price = meta['regularMarketPrice']
        prev_close = meta.get('chartPreviousClose', 0)
        change_pct = round((price - prev_close) / prev_close * 100, 2) if prev_close else 0
        
        # ★ 动态新鲜度判断（不依赖硬编码日历）
        market_time = meta.get('regularMarketTime')
        now_ts = datetime.now().timestamp()
        age_hours = (now_ts - market_time) / 3600 if market_time else 999
        is_fresh = age_hours < 24  # <24h视为新鲜(覆盖隔夜数据)
        
        result[name] = {
            'price': price,
            'change_pct': change_pct,
            '_stale': not is_fresh,
            '_stale_reason': f"data_age={age_hours:.1f}h" if not is_fresh else None,
            '_data_time': datetime.fromtimestamp(market_time, tz=timezone.utc).isoformat() if market_time else None,
            '_fetch_time': datetime.now().isoformat(),
        }
        time.sleep(0.3)
    return result
```

**已验证（2026-07-18，33/33测试通过）：**
- 7个外盘标的全部正确标记`_stale`
- 美股(16h前)标记为fresh ✅（隔夜数据合理）
- 韩股(52.5h前)标记为stale ✅（周四数据）
- 恒指(29.4h前)标记为stale ✅（周五早盘数据）
- 4个字段齐全：`_stale`, `_stale_reason`, `_data_time`, `_fetch_time`

**注意：** Yahoo Finance 接口对 A 股/港股不准确（盘后数据延迟），只用于美股和大宗商品。

### 9. 交易日自动验证（cron脚本，2026-07-18新增）

数据源修复后需持续验证。设置3轮自动验证cron job覆盖整个交易日：

| 轮次 | 时间 | 验证内容 |
|:----:|:----:|:---------|
| 第1轮 | 09:35 | 各源是否正常开盘、`_stale`标记是否=False |
| 第2轮 | 13:00 | 交叉验证(腾讯vsAKShare、天天vsAKShare)、涨跌三源对比 |
| 第3轮 | 15:30 | 收盘数据准确性、归档完整性 |

**脚本路径**：`/opt/data/scripts/trading_day_validate.py`（no_agent模式，自动检测交易日）  
**部署方式**：`cronjob(action='create', schedule='35 9 * * 1-5', no_agent=True, script='trading_day_validate.py')`  
**部署状态（2026-07-18）**：已部署3轮cron job，交易日自动运行：
| 轮次 | Job ID | 时间 | 交付 |
|:----:|:-------|:----:|:----:|
| 第1轮 | `d42eee036286` | 09:35 | origin (QQ Bot) |
| 第2轮 | `aec9567e1eaa` | 13:00 | origin (QQ Bot) |
| 第3轮 | `f9d875e9702d` | 15:30 | origin (QQ Bot) |

脚本设计：
- 交易日 → 完整数值验证（涨跌家数>100、交叉验证偏差<0.5%、净值偏差<0.01）
- 非交易日 → 仅API可达性测试（不会报错）
- 使用`is_trading_day()`内置判断，无需额外配置

### 10. `_tag_freshness` 通用新鲜度标记函数

对所有数据返回统一添加新鲜度字段，让上层消费方能感知数据时效性。应在所有数据采集函数的返回路径尾部调用：

```python
def _tag_freshness(data: dict) -> dict:
    \"\"\"为数据字典添加通用新鲜度标记\"\"\"
    from datetime import datetime, timezone
    data['_fresh'] = False        # 是否新鲜\n    data['_fetch_time'] = datetime.now(timezone.utc).isoformat()  # 采集时间
    data['_is_trading_day'] = is_trading_day()  # 是否交易日
    # 如果有日期字段，检查数据新鲜度
    date_field = data.get('nav_date') or data.get('date')
    if date_field and data['_is_trading_day']:
        data['_fresh'] = str(date_field)[:10] == date.today().isoformat()
    return data
```

该函数已在 `fund_tools.py` 中实现，所有get_tencent_quote/get_fund_value等函数返回的数据都包含`_fresh/_fetch_time/_is_trading_day`这三个字段。

### 10. `_tag_freshness` 通用新鲜度标记函数

对所有数据返回统一添加新鲜度字段，让上层消费方能感知数据时效性。应在所有数据采集函数的返回路径尾部调用：

```python
def _tag_freshness(data: dict) -> dict:
    """为数据字典添加通用新鲜度标记"""
    from datetime import datetime, timezone
    data['_fresh'] = False        # 是否新鲜
    data['_fetch_time'] = datetime.now(timezone.utc).isoformat()  # 采集时间
    data['_is_trading_day'] = is_trading_day()  # 是否交易日
    # 如果有日期字段，检查数据新鲜度
    date_field = data.get('nav_date') or data.get('date')
    if date_field and data['_is_trading_day']:
        data['_fresh'] = str(date_field)[:10] == date.today().isoformat()
    return data
```

该函数已在 `fund_tools.py` 中实现，所有get_tencent_quote/get_fund_value等函数返回的数据都包含`_fresh/_fetch_time/_is_trading_day`这三个字段。

## Weibo KOL 信号采集

监控关注的财经大V（唐史主任司马迁、it精英带你养基、小浣熊1230等）的最新微博，用于信号判断和今日参考。

### 安装 weibo-cli

```bash
uv tool install kabi-weibo-cli
export PATH="$HOME/.local/bin:$PATH"
```

### 二维码登录（服务器无浏览器环境）

weibo-cli 支持 `weibo login --qrcode`，但在无头/远程服务器上无法扫描终端ASCII二维码。

**正确做法：** 用 Python 调用 passport.weibo.com API 获取二维码内容的 URL，用 `qrcode+PIL` 生成 PNG 图片，发给用户扫码。见 `references/weibo-qr-login.md`。

用户扫码登录后，凭据自动保存到 `~/.config/weibo-cli/credential.json`（7天有效，到期自动过期需重新登录）。

### 常用命令

```bash
# 获取用户最新微博
weibo weibos <UID> --count 5 --json

# 搜索微博
weibo search "keyword" --json

# 检查登录状态
weibo status

# 查看热榜
weibo hot --count 10
```

### KOL 采集流程（推荐：桌面API + 预采集脚本）

weibo weibos 和 weibo search CLI 命令使用 mobile API（m.weibo.cn），需要与桌面端不同的 cookie，在无头服务器上通常返回 ok=-100 会话过期错误。

解决方案：使用桌面 API（weibo.com）直接调用，且必须用 `feature=1` 获取最新微博：

```python
import httpx, json
from pathlib import Path

CREDENTIAL_FILE = Path.home() / '.config' / 'weibo-cli' / 'credential.json'

def get_user_weibos(uid, count=5):
    if not CREDENTIAL_FILE.exists():
        return []
    cred = json.loads(CREDENTIAL_FILE.read_text())
    # CRITICAL: feature=1 returns latest posts, feature=0 returns 6-month-old pinned posts
    r = httpx.get('https://weibo.com/ajax/statuses/mymblog',
        params={'uid': uid, 'page': '1', 'feature': '1'},  # ← MUST be 1
        cookies=cred['cookies'],
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://weibo.com/',
            'X-Requested-With': 'XMLHttpRequest',
        }, timeout=15)
    data = r.json()
    if data.get('ok') == 1:
        posts = data['data']['list'][:count]
        results = []
        for p in posts:
            text = p.get("text_raw", p.get("text", ""))
            text = re.sub(r'<[^>]+>', '', text).strip()
            # ★ 长文本检测（2026-07-18修复）：否则丢失90%+内容
            if p.get("isLongText"):
                try:
                    lt_url = f"https://weibo.com/ajax/statuses/longtext?id={p.get('id','')}"
                    lt_r = httpx.get(lt_url, cookies=cred['cookies'], headers=headers, timeout=8)
                    lt_data = lt_r.json()
                    if lt_data.get("ok") == 1:
                        full_text = lt_data.get("data", {}).get("longTextContent", "")
                        if full_text:
                            text = re.sub(r'<[^>]+>', '', full_text).strip()
                except Exception as e:
                    print(f"长文本拉取失败: {e}")
            results.append({
                'id': p.get('id', ''),
                'text': text[:2000],  # 放宽截断（旧代码text[:500]）
                'is_longtext': p.get('isLongText', False),
                'created_at': p.get('created_at', ''),
                'reposts_count': p.get('reposts_count', 0),
                'comments_count': p.get('comments_count', 0),
            })
        return results
    return []
```

提取字段：`text`（纯文本无HTML，已含长文本拉取）, `created_at`, `reposts_count`, `comments_count`, `is_longtext`。

**验证（2026-07-18）**：唐史主任司马迁 15条中10条长文本(最长570字)，小浣熊1230 15条中4条长文本(最长689字)。旧代码`text[:500]`截断了这些内容。

新KOL分析框架见 `kol_analysis.py`（4层架构：提取→验证→评分→操作建议），在 `collect_morning_data.py` 中集成。

每采集一个用户间隔 >= 1 秒。桌面API使用QR登录cookie（`~/.config/weibo-cli/credential.json`），有效期约7天。

仅对信号博文（关键词：融资仓、建仓、右侧、加仓 等）且评论数 >= 30 的帖子可拉取评论区分析。

具体微博采集细节见 `weibo-monitor` skill。

### 基金持仓分组模式

当用户持有 ETF 联接+主动基金组合时，建议按主题分组分析而非逐支分析：

```python
FUND_GROUPS = {
    '科技': ['011613', '012552', '016803', '012045'],
    '黄金': ['002963', '009477'],
    '其他': ['013209', '012879', '014280', '013403', '016298'],
}

def group_funds(fund_data):
    for group_name, codes in FUND_GROUPS.items():
        changes = []
        for code in codes:
            v = fund_data.get(code)
            if v and v.get('estimated_change'):
                changes.append(float(v['estimated_change']))
        avg = round(sum(changes) / len(changes), 2) if changes else 0
        yield (group_name, avg, len(changes))
```

同主题基金联动性强，操作上一起考虑。

## 关于 a-stock-data

GitHub: `simonlin1212/a-stock-data` — 这是一个 **28 端点 SKILL.md 文件**，不是 pip 安装包。它封装了 mootdx+腾讯+东财+同花顺+新浪+百度共 13 个数据源的代码块。

```bash
# 只需装依赖，SKILL.md 作为参考查阅
pip install mootdx requests pandas stockstats
```

28 个端点覆盖：行情层、研报层、信号层、资金面、新闻、基础数据、公告。东财接口已内置 `em_get()` 限流防封。

## 常见陷阱

1. **海外网络 → mootdx TCP可达但K线协议兼容性问题**（2026-07-18实测修正）：Oracle ARM海外服务器上通达信TCP 7709端口 **10/10服务器全部可达**（socket.create_connection通过）。但K线数据获取全部失败 `KeyError: 'datetime'` — 这是 mootdx 0.11.7 与 pandas 3.0.3 的列名兼容性问题（`to_df()` 返回的DataFrame列名不是 `datetime`，导致 `get_k_data()` 第449行 `data['datetime']` 抛KeyError）。**解决方案**：(a) 降级mootdx版本或用 `--target` 隔离pandas；(b) 直接用腾讯财经HTTP API替代K线需求。
2. **东财封IP**：每秒超5次或1分钟超200次会临时封禁，必须用`em_get()`限流
3. **基金代码C类/A类**：C类免申购费适合短期持有，A类收申购费适合长期持有
4. **腾讯返回列表索引超出**：腾讯API返回时field数量有细微差异，`split('~')`后检查长度再取值
5. **腾讯批量查询code去前缀**：`parts[2]`返回纯数字（无sh/sz前缀），需用`.endswith()`匹配你传入的完整代码。直接用`==`比较会全失败。
6. **东财涨跌家数从海外超时**：Oracle ARM海外IP调用`push2.eastmoney.com`可能SSL握手超时（~8s+）。必须加`User-Agent`和`Referer`头，且设`timeout=8`避免阻塞。
7. **指数field[35]仅在交易时段有值**：非交易时段腾讯指数返回的成交额为0，采集时需`if total > 0`条件跳过。
8. **🔴 绝不能用行业/指数收益替代单只基金净值（用户纠正，2026-07）**：分析某只基金时，必须用该基金自身的净值（`fund_open_fund_info_em` 或 `get_fund_value`），不能用对应行业指数（如"中证半导体指数-25%"）或同主题ETF的涨跌来推断该基金收益。实证错误：曾用"中证半导体指数6个月-25%"当作 `024418华夏半导体材料设备ETF联接C` 的收益，实际该基金今年 **+101%**（涨最多）。指数与基金（尤其C类联接、主动基金）收益差距巨大，且"包含关系"不能想当然（024418是半导体材料设备细分，不是宽基011613的子集）。**规则：每只基金的收益/回撤/相关性结论，都必须来自该基金自己的净值序列，禁止以指数代推。**
9. **基金净值用 AKShare `fund_open_fund_info_em(symbol=code, indicator='单位净值走势')` 实时拉**：返回 `[(日期, 单位净值)]`，按年过滤得今年收益 `(last/first-1)`，近1月用 `date(2026,6,15)` 至今，成立来用全序列首末。多只基金批量拉取时每只间隔 `time.sleep(2)` 防限流。
10. **增量改报告后必须全量事实核查再交付（用户纠正，2026-07）**：重新拉原始数据源逐数核对，不信任报告自身。核查中发现的典型错误：(a) 微博频次按"字符出现次数"算（长鑫8次）vs 按"微博条数"算（7条）口径不一致，必须标注；(b) 报告内前后矛盾（"玻璃基板应纳入候选" vs "不新增标的"）必须统一；(c) 报告改完必须重新上传 R2 的 md+html，不能只写 md。核查结论要量化（如"净值零误差，仅N处口径修正"）。
11. **`fund_open_fund_info_em` 列名子串匹配误伤（2026-07-18 发现并修复）**：该API返回列 `净值日期`, `单位净值`, `日增长率`。用子串 `"净值" in col` 匹配净值列时，`"净值" in "净值日期"` 返回 True，导致把日期列当作净值列 → `float('2026-07-17')` 抛 TypeError。正确做法：匹配净值列时必须排除日期列：`"净值" in col and "日期" not in col`。

12. **🔴 数据新鲜度 ≠ API可用率（2026-07-18新增）**：API返回200不意味着数据可用。非交易日腾讯行情和美股休市日Yahoo都静默返回旧数据但不报错。每个数据源必须用两个独立维度验证：(a) API是否可达 (b) 数据时间戳是否在当前交易日（_stale标记）。前者用track_source追踪，后者用regularMarketTime字段判断。不可替代。

13. **🔴 禁止硬编码日期和日历（用户2026-07-18明确要求）**：外盘非交易日判断用Yahoo regularMarketTime时间戳动态判断，不需要写死任何节假日列表。A股交易日判断用AKShare tool_trade_date_hist_sina() + weekday降级。任何`2026-*`硬编码日期出现在执行代码中都是Bug。

14. **海外IP → 同花顺API静默过滤（2026-07-18实测）**：`basic.10jqka.com.cn/api/stockph/hotstock/` 返回 HTTP 200 但 body 为 **0字节空响应**（3/3次全空）。主站HTML页面（data.10jqka.com.cn）可达(78KB)，但数据API被海外IP静默过滤。**不适合海外部署**。

15. **海外IP → 百度股市通API可达但数据待验证（2026-07-18实测）**：`gushitong.baidu.com/opendata` 返回 HTTP 200 (0.21s)，但 `ResultNum=0` 无数据。HTML股票页面（finance.baidu.com）完全可达(31KB)。可能因周六非交易日，需交易日再验证数据返回。保守评估：API结构可达，数据有效性待交易日确认。

16. **海外IP → 新浪财经三表完全可达✅（2026-07-18实测）**：`vip.stock.finance.sina.com.cn` 资产负债表(82KB)、利润表(59KB)、现金流量表(76KB) 全部 HTTP 200 返回完整HTML。GB2312编码需转码。零鉴权，可作为财务数据替代源。**强烈推荐**。

17. **海外IP → 巨潮公告被完全屏蔽（2026-07-18实测）**：`cninfo.com.cn/new/disclosure` → HTTP 500(6/6次)；`hisAnnouncement/query` → HTTP 200 但 totalAnnouncement=0(空数据)；`webapi.cninfo.com.cn` → HTTP 401 'code_005_ipban_notoken'。海外IP被全面封禁。**需要国内代理或VPN**。

18. **非交易日数据源测试只能验证API结构（2026-07-18经验）**：周六对5个新数据源的测试能验证TCP/HTTP可达性、响应格式和错误码，但不能验证数据准确性和完整性（百度空Result、腾讯旧数据等）。测试报告必须标注非交易日状态，结论限于"API可达性"而非"数据可用性"。

## 批量验证脚本

- `scripts/validate_funds_indices.py` — 批量基金+指数全量验证脚本。输入基金代码和指数代码字典，逐支调用 `fund_open_fund_info_em` / `stock_zh_index_daily`，检查天数、日期范围、YTD、缺口>7天(基金)、涨跌>15%(基金)/>10%(指数)异常，输出结构化JSON。批量调用间隔1.5s(基金)/0.8s(指数)防限流。已对4支基金+9个指数全量验证通过。

## 参考文件

- `references/api-endpoints.md` — 已验证的API端点汇总
- `references/weibo-qr-login.md` — 无头服务器微博二维码登录方案
- `references/fund-portfolio.md` — 基金组合持仓参考（20+支基金代码与分组）
- `references/financial-digest-format.md` — 财经简报排版规范（markdown表格格式、涨跌颜色、结构模板）
- `references/sector-etf-codes.md` — 行业ETF代码清单（已验证，含批量查询示例和陷阱）
- `references/non-trading-day-handling.md` — 非交易日API行为速查 + 数据新鲜度标记模式 + 验证铁律（2026-07-18新增）
- `references/push2-geo-block-cross-validation.md` — push2 vs push2delay海外IP交叉验证：DNS同IP、nginx vhost geo-block、7种组合全502（2026-07-18新增）
- `references/overseas-source-availability.md` — 海外服务器5个补充数据源可用性测试报告：mootdx/同花顺/百度/新浪/巨潮（2026-07-18新增）
- `references/validation-methodology.md` — 多轮验证方法论：四轮框架 + 非交易日约束 + 交易日补充项（2026-07-18新增）
- `references/trading-day-auto-validate.md` — 3轮交易日自动验证cron设置 + 验证项清单（2026-07-18新增）
- `scripts/weibo_qr_login.py` — 可复用的微博QR登录脚本（monkey-patch方式）
