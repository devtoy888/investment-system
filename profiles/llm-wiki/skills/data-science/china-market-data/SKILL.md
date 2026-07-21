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
| 3 | **mootdx(通达信)** | TCP 7709 | **不封** | K线/五档/财务(海外IP可能超时) |
| 4 | 东财(限流) | HTTP | 有风控 | 龙虎榜/北向/资金流/研报(已内置限流) |
| 5 | 同花顺 | HTTP | 极低 | 热点题材/北向资金 |

> **核心原则：** 能用腾讯/天天就不用东财。腾讯接口实测不封IP。

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

### 5. 东财市场总览（涨跌家数）

`push2.eastmoney.com` 提供A股涨跌家数API，无需限流（低频查询即可）。**注意：从Oracle ARM海外IP可能SSL握手超时**，需加 User-Agent + Referer 头。

```python
import requests

def get_market_breadth():
    \"\"\"获取A股涨跌家数 (上证主板)
    返回: {'rise_count': int, 'fall_count': int, 'flat_count': int}
    字段: f169=涨家数, f170=跌家数, f171=平盘家数
    \"\"\"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': 'https://quote.eastmoney.com/',
    }
    r = requests.get(
        'https://push2.eastmoney.com/api/qt/stock/get?secid=1.000001&fields=f57,f58,f169,f170,f171',
        timeout=8, headers=headers)
    data = r.json().get('data', {})
    return {
        'rise_count': int(data.get('f169', 0)),
        'fall_count': int(data.get('f170', 0)),
        'flat_count': int(data.get('f171', 0)),
    }
# 返回示例: {'rise_count': 823, 'fall_count': 20, 'flat_count': 74}
```

> 注意：此API只返回上证主板的涨跌家数（约900+支股票），并非全市场。如需深证+创业板+科创板的需额外调用。

### 6. 同花顺北向资金（不封IP）

同花顺 hexin 数据中心提供沪深股通实时分钟级北向资金数据，262个时间点（09:10-15:00），**Oracle ARM海外IP可用**。

```python
import requests

_NORTHBOUND_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/117.0.0.0 Safari/537.36',
    'Host': 'data.hexin.cn',
    'Referer': 'https://data.hexin.cn/',
}

def get_northbound_flow() -> dict:
    \"\"\"获取北向资金当日实时累计净流入
    返回: {'hgt': 沪股通亿, 'sgt': 深股通亿, 'total': 合计亿, 'time': 最新时间点}\"\"\"
    r = requests.get(
        'https://data.hexin.cn/market/hsgtApi/method/dayChart/',
        headers=_NORTHBOUND_HEADERS, timeout=10)
    d = r.json()
    times = d.get('time', [])
    hgt = d.get('hgt', [])
    sgt = d.get('sgt', [])
    for i in range(len(times) - 1, -1, -1):
        if times[i] and hgt[i] is not None and sgt[i] is not None:
            return {
                'hgt': hgt[i], 'sgt': sgt[i],
                'total': (hgt[i] or 0) + (sgt[i] or 0),
                'time': times[i],
            }
    return {'hgt': None, 'sgt': None, 'total': None, 'time': None}
```

**数据源说明：** a-stock-data（simonlin1212/a-stock-data）项目中验证了此接口的可用性。原东财push2北向API在海外IP超时。同花顺此接口稳定且无IP封禁风险。东财kamt.kline接口返回数据格式不明确（清零/结构混乱）。

### 7. 数据源自动验证模式

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

非交易时段处理：成交额等字段在非交易时段返回0，采集脚本应加 `if total > 0` 条件跳过空数据。

## 涨跌颜色约定（A股惯例）

推送给用户时，用 emoji 标注涨跌必须符合 A股/国内习惯：
- **🔴 = 上涨**（红色代表涨）
- **🟢 = 下跌**（绿色代表跌）
- **🟡 = 持平**

这是 A 股惯例（与美股相反），用户会纠正你。所有行情展示、基金分组、持仓概览都必须遵守。

## 外盘行情（Yahoo Finance）

非A股数据（美股指数、黄金期货、美元等）使用 Yahoo Finance API，零配置：

```python
import requests

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
        result[name] = {'price': price, 'change_pct': change_pct}
        time.sleep(0.3)
    return result
```

注意：Yahoo Finance 接口对 A 股/港股不准确（盘后数据延迟），只用于美股和大宗商品。

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
        return data['data']['list'][:count]
    return []
```

提取字段：`text_raw`（纯文本无HTML）, `created_at`, `reposts_count`, `comments_count`, `attitudes_count`。

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

1. **海外网络 → mootdx不可达**：通达信TCP 7709在海外基本全超时，回退到腾讯财经API
2. **东财封IP**：每秒超5次或1分钟超200次会临时封禁，必须用`em_get()`限流
3. **基金代码C类/A类**：C类免申购费适合短期持有，A类收申购费适合长期持有
4. **腾讯返回列表索引超出**：腾讯API返回时field数量有细微差异，`split('~')`后检查长度再取值
5. **腾讯批量查询code去前缀**：`parts[2]`返回纯数字（无sh/sz前缀），需用`.endswith()`匹配你传入的完整代码。直接用`==`比较会全失败。
6. **东财涨跌家数从海外超时**：Oracle ARM海外IP调用`push2.eastmoney.com`可能SSL握手超时（~8s+）。必须加`User-Agent`和`Referer`头，且设`timeout=8`避免阻塞。
7. **指数field[35]仅在交易时段有值**：非交易时段腾讯指数返回的成交额为0，采集时需`if total > 0`条件跳过。

## 参考文件

- `references/api-endpoints.md` — 已验证的API端点汇总
- `references/weibo-qr-login.md` — 无头服务器微博二维码登录方案
- `references/fund-portfolio.md` — 基金组合持仓参考（20+支基金代码与分组）
- `references/financial-digest-format.md` — 财经简报排版规范（markdown表格格式、涨跌颜色、结构模板）
- `references/sector-etf-codes.md` — 行业ETF代码清单（已验证，含批量查询示例和陷阱）
- `scripts/weibo_qr_login.py` — 可复用的微博QR登录脚本（monkey-patch方式）
