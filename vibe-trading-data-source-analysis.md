# Vibe-Trading 数据源架构与错误处理策略分析

> 分析目标: https://github.com/HKUDS/Vibe-Trading (22.9k Stars)
> 核心代码路径: `agent/backtest/loaders/`, `agent/backtest/runner.py`, `agent/backtest/validation.py`

---

## 一、数据源体系架构

### 1.1 整体架构: Protocol + Registry + Fallback Chain

Vibe-Trading 采用 **三层架构** 管理数据源:

```
┌──────────────────────────────────────────────┐
│  Runner (fetch_data_map / _fetch_auto)       │  ← 统一入口，含运行时降级
├──────────────────────────────────────────────┤
│  Registry (LOADER_REGISTRY + FALLBACK_CHAINS)│  ← 中央注册表 + 市场级降级链
├──────────────────────────────────────────────┤
│  DataLoaderProtocol (base.py)                │  ← 接口协议
├──────────────────────────────────────────────┤
│  21个具体 Loader 实现                         │  ← 各数据源适配器
└──────────────────────────────────────────────┘
```

**核心接口** (`agent/backtest/loaders/base.py:583-609`):

```python
@runtime_checkable
class DataLoaderProtocol(Protocol):
    name: str           # 数据源名称，如 "tushare", "eastmoney"
    markets: set[str]   # 服务的市场类型，如 {"a_share", "us_equity"}
    requires_auth: bool # 是否需要认证

    def is_available(self) -> bool: ...
    def fetch(self, codes, start_date, end_date, *, interval, fields) -> dict[str, DataFrame]: ...
```

### 1.2 注册机制 — Decorator + Lazy Import

所有 loader 通过 `@register` 装饰器自注册 (`agent/backtest/loaders/registry.py:59-65`):

```python
def register(cls):
    LOADER_REGISTRY[cls.name] = cls
    return cls
```

`_ensure_registered()` 惰性导入所有 loader 模块，依赖缺失的模块（如 `akshare` 未安装）静默跳过:
```python
for mod in _loader_modules:
    try:
        importlib.import_module(mod)
    except Exception:
        pass  # 缺失依赖不阻塞
```

### 1.3 21个数据源全面覆盖

| 数据源 | 市场覆盖 | 认证 | 位置 |
|--------|---------|------|------|
| `tushare` | A股/期货/基金 | 需要token | `loaders/tushare.py` |
| `eastmoney` | A股/港股/美股 | 无需认证(免费) | `loaders/eastmoney_loader.py` |
| `yahoo` | 美股/港股/印度 | 无需认证(免费) | `loaders/yahoo_loader.py` |
| `yfinance` | 美股/港股/印度/加密货币 | 无需认证 | `loaders/yfinance_loader.py` |
| `okx` | 加密货币 | 无需认证(公开API) | `loaders/okx.py` |
| `ccxt` | 加密货币(100+交易所) | 无需认证 | `loaders/ccxt_loader.py` |
| `akshare` | A股/期货/基金/外汇/宏观 | 无需认证 | `loaders/akshare_loader.py` |
| `baostock` | A股 | 无需认证 | `loaders/baostock_loader.py` |
| `tencent` | A股 | 无需认证 | `loaders/tencent_loader.py` |
| `mootdx` | A股 | 无需认证 | `loaders/mootdx_loader.py` |
| `futu` | 港股 | 需要连接 | `loaders/futu.py` |
| `sina` | A股/美股 | 无需认证 | `loaders/sina_loader.py` |
| `stooq` | 美股 | 无需认证 | `loaders/stooq_loader.py` |
| `finnhub` | 美股 | 需要API Key | `loaders/finnhub_loader.py` |
| `alphavantage` | 美股 | 需要API Key | `loaders/alphavantage_loader.py` |
| `tiingo` | 美股 | 需要API Key | `loaders/tiingo_loader.py` |
| `fmp` | 美股 | 需要API Key | `loaders/fmp_loader.py` |
| `qveris` | 多市场 | 需要配置 | `loaders/qveris_loader.py` |
| `india_broker` | 印度股票 | 需要连接 | `loaders/india_broker_loader.py` |
| `longbridge` | 美股/港股 | 需要连接 | `loaders/longbridge.py` |
| `local` | 全市场 | 本地CSV文件 | `loaders/local_loader.py` |

---

## 二、降级(Fallback)策略 — 多层递进

### 2.1 市场级 Fallback Chain（核心降级机制）

每个市场类型都有预定义的降级链 (`registry.py:130-140`)，按 **IP封禁风险低→高、数据质量高→低** 排列:

```python
FALLBACK_CHAINS = {
    "a_share":   ["tencent", "mootdx", "eastmoney", "baostock", "akshare", "tushare", "local"],
    "us_equity": ["yahoo", "stooq", "sina", "eastmoney", "yfinance", "tiingo", "fmp",
                  "finnhub", "alphavantage", "longbridge", "akshare", "local"],
    "hk_equity": ["eastmoney", "yahoo", "futu", "yfinance", "akshare", "longbridge", "local"],
    "crypto":    ["okx", "ccxt", "yfinance", "local"],
    "futures":   ["tushare", "akshare", "local"],
    "forex":     ["akshare", "yfinance", "local"],
    ...
}
```

**设计原则** (代码注释原文, line 125-129):
> Chains are ordered by IP-ban risk first (lighter, throttle-tolerant public endpoints lead; key-gated REST and rate-limit-prone sources trail), then by data quality.

### 2.2 三层降级机制

#### Layer 1: 注册表解析降级 (`resolve_loader`)

```python
def resolve_loader(market):
    chain = FALLBACK_CHAINS.get(market, [])
    for name in chain:
        try:
            loader = LOADER_REGISTRY[name]()
        except Exception:
            continue  # 构造函数失败（如缺token），继续尝试下一个
        if loader.is_available():
            return loader
    raise NoAvailableSourceError(f"No available data source for market '{market}'")
```

#### Layer 2: 显式源不可用降级 (`get_loader_cls_with_fallback`)

当用户显式指定某个 source 但不可用时:
- 先尝试实例化 → `is_available()` → 通过同一市场的 fallback chain 查找替代
- **关键保护**: `local` 和 `qveris` 永远不会降级到网络源 (`_NO_NETWORK_FALLBACK_SOURCES`)
- 降级时记录 `logger.warning("... is unavailable, falling back to ...")`

#### Layer 3: 运行时数据空返回降级 (`fetch_data_map` 和 `_fetch_auto`)

在 loader 返回空数据时（非异常，而是无数据），尝试同 market 的其他来源:

```python
# runner.py:1126-1146
if not data_map and codes:
    market = _detect_market(codes[0])
    for fallback_source in FALLBACK_CHAINS.get(market, []):
        if fallback_source == source:
            continue
        fallback_loader = LOADER_REGISTRY[fallback_source]()
        if not fallback_loader.is_available():
            continue
        data_map = fallback_loader.fetch(...)
        if data_map:
            logger.info("Runtime fallback: %s -> %s", source, fallback_source)
            break
```

### 2.3 应用层降级: Tushare Fallback Adapter

`agent/src/tools/tushare_fallbacks.py` 实现了更高层的工具降级:
- 主数据源: 东方财富免费公开 API
- 备选数据源: Tushare Pro (需要token)
- 降级语义: 当东方财富不可用时，Tushare 恢复相同的**资金流向/龙虎榜/北向资金/两融**研究工作流
- 异常类型: `TushareFallbackUnavailable` (token未配置、导入失败、日期格式错误)

---

## 三、错误处理机制

### 3.1 分级异常处理策略

| 层级 | 策略 | 代码位置 |
|------|------|----------|
| **Loader构造函数错误** | 捕获并跳过，继续尝试fallback chain下一个 | `registry.py:168-172` |
| **单symbol失败** | 记录warning，不中断batch，返回已有数据 | 每个loader的`fetch()`方法 |
| **永久代(perp)失败** | 立即raise（不吞没），确保关键数据失败可见 | `ccxt_loader.py:195-197` |
| **非瞬态异常** | 立即传播，不重试 | `base.py:retry_with_budget` |
| **Loader依赖缺失** | 静默跳过，不阻塞其他loader | `registry.py:_ensure_registered` |
| **不可降级源失败** | 抛出明确错误，指示用户检查配置 | `registry.py:211-217` |

### 3.2 核心模式: Batch中单symbol隔离

所有 loader 的 `fetch()` 方法都遵循同一模式——单个 symbol 失败不中断整个批次:

```python
# 典型模式 (eastmoney_loader.py:94-109, yahoo_loader.py:200-218, okx.py:92-109)
for code in codes:
    try:
        df = cached_loader_fetch(...)
        if df is not None and not df.empty:
            result[code] = df
    except Exception as exc:
        logger.warning("eastmoney failed for %s: %s", code, exc)
return result  # 返回成功获取的symbol数据
```

### 3.3 Bounded Retry with Budget（有界重试+预算）

`base.py:165-217` 实现了重试核心机制 `retry_with_budget`:

```python
def retry_with_budget(fn, *, transient, deadline, label, max_retries=3, backoff=(0.5, 1.5, 4.0)):
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except transient as exc:
            remaining = deadline - time.monotonic()
            if attempt == max_retries or remaining <= 0:
                raise TimeoutError(f"{label} failed after {attempt+1} attempt(s): {exc}") from exc
            time.sleep(min(backoff[attempt], max(0.0, remaining)))
```

**关键设计决策**:
- **默认退避**: `(0.5s, 1.5s, 4.0s)` — 渐进式退避
- **默认最大重试**: 3次（总共4次尝试）
- **预算感知睡眠**: `sleep(min(backoff[attempt], remaining_budget))` — 剩余预算不足时不花完整个退避时间
- **非瞬态异常不重试**: 只对显式声明的 `transient` 异常类重试
- **原始异常保留**: 最终 `TimeoutError` 的 `__cause__` 保留原始异常供诊断

**实际使用场景**:

| Loader | 瞬态异常类型 | 超时/budget | 代码 |
|--------|------------|------------|------|
| CCXT | `ccxt.NetworkError` | 60s per fetch | `ccxt_loader.py:254-259` |
| OKX | `requests.RequestException` | 60s per fetch | `okx.py:149-154` |

### 3.4 分页预算检查 (`check_budget`)

`base.py:144-159` — 用于分页fetch中每个页面间的预算检查:

```python
def check_budget(deadline, label, budget_s=None):
    if time.monotonic() > deadline:
        raise TimeoutError(f"{label} exceeded {budget_s:.0f}s budget")
```

CCXT loader 在每个分页循环中使用: `check_budget(deadline, label, budget_s=60.0)` — 一旦超过60秒，立即终止分页。

### 3.5 Yahoo Cookie/Crumb 401 自动刷新

`yahoo_client.py:274-291` — Yahoo Finance quoteSummary API 需要 cookie+crumb 握手:

```python
def _quote_summary_request(yahoo_symbol, modules_param, *, force_refresh):
    crumb, cookies = _CRUMB_STORE.get(force_refresh=force_refresh)
    response = throttled_get(...)
    if response.status_code == 401 and not force_refresh:
        logger.info("Yahoo quoteSummary 401 for %s; refreshing crumb", yahoo_symbol)
        return _quote_summary_request(yahoo_symbol, modules_param, force_refresh=True)
    response.raise_for_status()
    return response.json()
```

401 时自动刷新 crumb 并重试一次，第二次 401 直接传播。

---

## 四、数据缓存方案

### 4.1 缓存架构

缓存位于 `base.py:220-581`，是一个**显式opt-in的本地文件缓存**:

```
特征:
- 环境变量控制: VIBE_TRADING_DATA_CACHE="1"/"true"/"yes"/"on"
- 存储后端: DuckDB → Parquet 文件
- 存储路径: ~/.vibe-trading/cache/loaders/{source}/{sha256}.parquet
- 键: SHA256(content-addressed, 基于 source+symbol+timeframe+date+fields)
- 版本化: 当前版本=3，改变键格式时自动失效旧条目
```

### 4.2 缓存维度隔离

缓存键涵盖**所有维度**，任何一个维度不同即产生不同缓存:

```python
# base.py:407-424
def _loader_cache_payload(*, source, symbol, timeframe, start_date, end_date, fields):
    return {
        "version": 3,
        "source": source,       # "tushare", "yfinance", etc.
        "symbol": symbol,       # "000001.SZ", "AAPL.US"
        "timeframe": timeframe,  # "1D", "1H", "5m"
        "start_date": start_date, # 归一化为 YYYY-MM-DD
        "end_date": end_date,
        "fields": fields,       # ["pe"], None, etc.
    }
```

测试验证了7个维度的完整隔离 (`test_loader_cache_key_partitions_source_symbol_timeframe_date_and_fields`)。

### 4.3 未完结范围保护

**关键设计**：缓存只在 `end_date < today` 时才启用 (`loader_cache_range_is_final`):

```python
def loader_cache_range_is_final(end_date):
    end = pd.Timestamp(end_date).normalize().date()
    return end < dt.date.today()
```

原因: 键是内容寻址的（基于end_date），不基于wall-clock时间，如果缓存一个当日/未来结束的范围，会把未成形的bar固定住。测试验证了当日范围永远不会被缓存。

### 4.4 缓存读写原子性

写入使用 **临时文件 + os.replace** 保证原子性:

```python
# base.py:503-527
unique = f"{os.getpid()}.{uuid.uuid4().hex}"
tmp_path = cache_path.with_name(f"{cache_path.name}.{unique}.tmp")
# ... write to tmp_path ...
os.replace(tmp_path, cache_path)  # 原子swap
```

**并发安全**: pid + uuid 确保两个并发写入同一键的进程使用不同临时路径，`os.replace` 保证每个文件原子交换。

### 4.5 缓存层在Loader中的集成

所有 loader 通过 `cached_loader_fetch` 统一使用缓存:

```python
# base.py:366-404
def cached_loader_fetch(*, source, symbol, ..., fetch):
    cached = loader_cache_get(...)  # 尝试读缓存（miss=非致命，返回None）
    if cached is not None:
        return cached
    frame = fetch()                 # 回退到live provider
    loader_cache_put(..., frame=frame)  # 写入缓存（失败=非致命，静默忽略）
    return frame
```

**测试验证**:
- 禁用时绕过缓存 (`test_loader_cache_disabled_by_default_bypasses_home`)
- 损坏条目回退到live fetch (`test_loader_cache_corrupt_entry_falls_back_to_live_fetch`)
- 第二次fetch从缓存服务 (`test_yfinance_loader_serves_second_fetch_from_cache`)
- 真实DuckDB round-trip保持字节一致性 (`test_loader_cache_real_duckdb_round_trip`)

---

## 五、数据验证与准确性保证机制

### 5.1 OHLC 不变式校验 (结构正确性)

`base.py:50-100` 实现了 `validate_ohlc`，检查每个bar是否违反OHLC基本约束:

```python
def validate_ohlc(frame, *, strategy="drop"):
    invalid = (
        (high < low)           # 最高价 < 最低价
        | (high < open_)       # 最高价 < 开盘价
        | (high < close)       # 最高价 < 收盘价
        | (low > open_)        # 最低价 > 开盘价
        | (low > close)        # 最低价 > 收盘价
        | (open_ <= 0)         # 非正价格
        | (high <= 0)
        | (low <= 0)
        | (close <= 0)
    )
```

三种策略:
- **`drop`** (默认): 删除无效行，记录warning
- **`warn`**: 保留但记录warning  
- **`raise`**: 抛出 `ValueError`

### 5.2 中央边界守卫 (Catch-All)

**所有数据在进入回测前必须经过 `_sanitize_data_map`** (`runner.py:1161-1178`):

```python
def _sanitize_data_map(data_map):
    return {code: validate_ohlc(frame) for code, frame in data_map.items()}
```

这是**单一聚合点**: 无论数据来自 auto/single-source/runtime-fallback/未来新loader，都统一经过此检查。代码注释明确说明:

> Each loader only drops NaN rows, so a bar that violates the OHLC invariants can still reach the backtest... Applying validate_ohlc here — the single point every fetched map converges through — guards every source uniformly.

测试验证: 即使 local loader 的CSV包含 `high < low` 的bar，也会被此边界守卫删除。

### 5.3 Loader内部的NaN处理

每个 loader 在生成 DataFrame 时都会:
1. `pd.to_numeric(..., errors="coerce")` — 将非数值转为 NaN
2. `.dropna(subset=["open", "high", "low", "close"])` — 删除OHLC不完全的行

典型模式 (eastmoney_loader.py:168-176):
```python
for column in _OHLCV_COLUMNS:
    df[column] = pd.to_numeric(df[column], errors="coerce").astype(float)
df = df[_OHLCV_COLUMNS].dropna(subset=["open", "high", "low", "close"])
```

### 5.4 日期范围验证

`base.py:31-47` — 所有 loader 入口统一调用:

```python
def validate_date_range(start_date, end_date):
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    if start > end:
        raise ValueError(f"start_date > end_date")
```

### 5.5 统计验证套件 (回测结果验证)

`backtest/validation.py` 提供三种独立的统计验证:
1. **蒙特卡洛置换检验**: shuffle trade PnL 顺序，检验策略是否显著优于随机
2. **Bootstrap Sharpe CI**: 重采样日收益，估计夏普率置信区间
3. **Walk-Forward分析**: 将回测分割为顺序窗口，检查性能一致性

### 5.6 配置端验证

`BacktestConfigSchema` (runner.py:68-100) 使用 Pydantic v2 验证:
- `codes`: 非空列表，无空字符串
- `start_date`/`end_date`: 必须是可解析日期
- `initial_cash`: 必须是正数 (gt=0)，禁止 inf/NaN
- `source`: 必须是 `VALID_SOURCES` 成员（与 loader 注册表保持同步）

### 5.7 Tushare Fallback 的数据规范化

`tushare_fallbacks.py` 实现了数据规范化以确保 fallback 数据与主源兼容:
- 金额单位转换: Tushare 万CNY → 东方财富 CNY (`* 10_000`)
- 日期格式统一: `YYYYMMDD` → `YYYY-MM-DD`
- 符号格式统一: 6位纯数字 → `code.SH/SZ/BJ`

---

## 六、HTTP 层 — 通用限速与会话复用

### 6.1 Per-Host Throttle (`_http.py`)

```python
class HostThrottle:
    """进程级最小间隔门控，按任意host bucket分组"""
    def wait(self, bucket, min_interval):
        # 记录每个bucket的最后请求时间
        # 使用threading.Lock保证线程安全
        # 添加jitter (0-0.4s) 防止并发调用者同步
```

**设计特点**:
- 进程级共享门控 (`_THROTTLE = HostThrottle()`)
- 不同bucket互不阻塞（锁仅用于记账算术，不跨sleep持有）
- jitter + 预留fire时间 → 确保连续请求至少间隔 `min_interval`

### 6.2 Per-Bucket Session 复用

```python
_SESSIONS: dict[str, requests.Session] = {}  # 按bucket复用TCP/TLS连接
```

### 6.3 各Provider的限速配置

| Provider | Bucket | 默认间隔 | 环境变量覆盖 |
|----------|--------|---------|-------------|
| Yahoo Finance | `yahoo` | 0.6s | `VIBE_TRADING_YAHOO_MIN_INTERVAL` |
| Eastmoney | `eastmoney` | Client层控制 | `VIBE_TRADING_EASTMONEY_MIN_INTERVAL` |
| Finnhub | `finnhub` | 0.4s | `VIBE_TRADING_FINNHUB_MIN_INTERVAL` |

### 6.4 超时配置

所有HTTP请求都有超时保护:
- 默认: 15秒 (`throttled_get` timeout=15.0)
- CCXT: `CCXT_TIMEOUT_MS` 默认 15000ms
- OKX: `OKX_TIMEOUT_S` 默认 15s

---

## 七、自动路由 (Auto Mode)

### 7.1 符号→市场分类

`_market_hooks.py:25-46` 的 `_MARKET_PATTERNS` 定义了14个正则表达式来分类符号:

```python
_MARKET_PATTERNS = [
    (r"^\d{6}\.(SZ|SH|BJ)$", "a_share"),    # 600519.SH
    (r"^[A-Z]+\.US$", "us_equity"),          # AAPL.US
    (r"^\d{3,5}\.HK$", "hk_equity"),         # 00700.HK
    (r"^[A-Z]+-USDT$", "crypto"),            # BTC-USDT
    (r"^[A-Za-z]{1,2}\d{3,4}\.(ZCE|DCE|...)$", "futures"),  # IF2406.CFFEX
    (r"^[A-Z]{3}/[A-Z]{3}$", "forex"),       # EUR/USD
    ...
]
```

### 7.2 自动路由流程 (`_fetch_auto`)

当 `source="auto"` 时:
1. 按市场分组代码 → 每个市场组通过 `resolve_loader(market)` 获取最优可用loader
2. 若 fallback chain 全部失败 → 降级到 legacy source mapping
3. 若 loader 返回空数据 → 运行时尝试同市场其他loader
4. 所有结果 merge → 通过 `_sanitize_data_map` 统一清洗

---

## 八、总结: 架构优势

| 维度 | 实现方式 | 关键文件 |
|------|---------|---------|
| **源多样性** | 21个loader覆盖全球8个市场类型 | `loaders/registry.py` |
| **多层降级** | 注册表→显式源→运行时空数据，三层降级 | `registry.py` + `runner.py` |
| **精确重试** | 区分瞬态/非瞬态异常，有budget约束 | `base.py:165-217` |
| **请求限速** | Per-host throttle + jitter + session复用 | `_http.py` |
| **数据缓存** | SHA256内容寻址，DuckDB+Parquet后端，原子写入 | `base.py:220-581` |
| **数据校验** | 中央OHLC边界守卫 + 日期范围 + 配置schema | `base.py:50-100` + `runner.py:1161-1178` |
| **单元隔离** | 单symbol失败不中断batch | 每个loader的`fetch()` |
| **自动路由** | 14个正则模式将符号自动分发到最优loader | `_market_hooks.py` |
| **应用层降级** | Tushare fallback adapter恢复东方财富研究流 | `tools/tushare_fallbacks.py` |
| **Cookie管理** | Yahoo 401自动刷新crumb/cookie | `yahoo_client.py:274-291` |

**最值得借鉴的设计**:
1. **Fallback Chain排序策略**: 按IP封禁风险排列，免费公开端点在前，key-gated在后——兼顾可靠性和成本
2. **`_sanitize_data_map` 中央守卫**: 无论数据走什么路径进入，都经过统一校验——绝不让脏数据进入回测
3. **`retry_with_budget`**: 结合退避+wall-clock预算+瞬态异常分类——比简单的"重试N次"更精确
4. **缓存原子性+未完结保护**: 并发安全+当日范围不缓存——避免固定未成形数据
