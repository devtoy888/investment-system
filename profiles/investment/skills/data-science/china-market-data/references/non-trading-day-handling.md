# 非交易日数据新鲜度处理

> 2026-07-18 修订 | 基于两参考仓库对比 + 实测验证

## 问题陈述

腾讯API（`qt.gtimg.cn`）在非交易日**静默返回上周五收盘数据**，不报错也不做无数据标记。这与其他数据源（mootdx TCP返回空、东财返回空/502、同花顺返回null）行为不同，导致自动推送系统可能拿旧数据当成实时数据。

## 各API非交易日行为

| 数据源 | 非交易日行为 | 风险 | 对策 |
|:-------|:------------|:----:|:-----|
| **腾讯行情** | 返回上周五收盘价(price=prev_close, change_pct=昨日) | 🔴 | 加_stale标记；消费方必须检查 |
| **天天基金** | nav_date≠today，已有stale字段 | ✅ | 持续使用stale字段 |
| **东财push2** | 502（和平常一样，无法区分） | 🟡 | 不额外处理，502统一降级 |
| **新浪tags** | 返回旧新闻文本 | 🔴 | 结合交易日历判断 |
| **AKShare全量A股** | 连接重置/超时 | 🟢 | 异常就是非交易日信号 |
| **Yahoo外盘** | **美股休市日也返回旧数据（无标记）** | **🔴** | **见"外盘非交易日"节** |

## ⚠️ 外盘非交易日（2026-07-18确认：当前完全未处理）

Yahoo外盘（道琼斯/标普500/纳斯达克/恒指/韩指/KOSPI）**完全没有非交易日处理**。美股自身有13天休市日，港股约17天，韩股约12天。在这些日期Yahoo返回上周五数据，系统无感知。

**风险场景：** A股交易日 + 美股休市日 = 晨报显示"道琼斯涨X%"（实际是3天前数据）

### 2026年美股休市日

| 日期 | 假日 | A股状态 | 风险 |
|:-----|:-----|:-------|:----:|
| 2026-01-19(周一) | 马丁路德金日 | ✅交易 | 🔴 |
| 2026-02-16(周一) | 总统日 | ❌春节(同步休市) | 🟢 |
| 2026-04-03(周五) | 耶稣受难日 | ✅交易 | 🔴 |
| 2026-05-25(周一) | 阵亡将士纪念日 | ✅交易 | 🔴 |
| 2026-07-03(周五) | 独立日前 | ✅交易 | 🔴 |
| 2026-09-07(周一) | 劳动节 | ✅交易 | 🔴 |
| 2026-11-26(周四) | 感恩节 | ✅交易 | 🔴 |
| 2026-12-25(周五) | 圣诞节 | ✅交易 | 🔴 |

### 修复方案（2026-07-18实施 — 动态时间戳方案，无硬编码）

利用Yahoo返回的`regularMarketTime`时间戳动态判断数据新鲜度，**不依赖任何节假日日历**：

```python
from datetime import datetime, timezone

def _is_yahoo_data_fresh(meta: dict) -> tuple:
    """利用Yahoo自身的时间戳判断外盘数据新鲜度。
    任何市场、任何节假日自动适配，无需硬编码日历。
    """
    market_time = meta.get('regularMarketTime')
    if not market_time:
        return False, "no_timestamp"
    
    now_ts = datetime.now().timestamp()
    age_hours = (now_ts - market_time) / 3600
    
    # <24h视为新鲜（覆盖隔夜数据）
    if age_hours < 24:
        return True, None
    else:
        return False, f"data_age={age_hours:.1f}h>24h"

# 在Yahoo报价函数中：
result = {
    'price': price,
    'change_pct': change_pct,
    '_stale': not is_fresh,
    '_stale_reason': stale_reason,
    '_data_time': datetime.fromtimestamp(market_time, tz=timezone.utc).isoformat(),
    '_fetch_time': datetime.now().isoformat(),
}
```

**已验证（2026-07-18，33/33测试通过）：**
- 美股(16h前) → `_stale=False` ✅（隔夜数据合理）
- 韩股(52.5h前) → `_stale=True` ✅（周四数据，正确标记stale）
- 恒指(29.4h前) → `_stale=True` ✅（周五早盘数据）
- 7个外盘标的全部正确标记

## 数据新鲜度实现模式

### 1. 每个数据返回携带_stale标记

```python
# 在get_tencent_quote()的return中：
return {
    'price': parts[3],
    'change_pct': parts[32],
    # ... 其他字段 ...
    '_stale': not is_trading_day(),  # 非交易日标记为旧数据
    '_data_source': 'tencent',
}
```

### 2. 通用新鲜度标记函数

```python
def _tag_freshness(data: dict) -> dict:
    today_str = date.today().isoformat()
    is_trading = is_trading_day()
    
    # 从数据中提取日期字段
    data_date = None
    for key in ('nav_date', 'date', 'trade_date'):
        if key in data and data[key]:
            data_date = str(data[key])[:10]
            break
    
    if data_date is None:
        data['_fresh'] = is_trading  # 非交易日→stale
    else:
        data['_fresh'] = (data_date == today_str)
    
    data['_data_date'] = data_date or "unknown"
    data['_fetch_time'] = datetime.now().isoformat()
    data['_is_trading_day'] = is_trading
    return data
```

### 3. 消费方检查

```python
data = get_tencent_quote('sh000001')
if data and data.get('_stale', False):
    # 数据是旧数据，应标注或跳过
    print("⚠️ 非交易日数据，仅供参考")
```

## 交易日历判断

使用AKShare的交易日历API + weekday降级（双层防护）：

```python
import akshare as ak
from datetime import date

def is_trading_day(d: date = None) -> bool:
    if d is None:
        d = date.today()
    # 第一层：周末过滤
    if d.weekday() >= 5:
        return False
    # 第二层：AKShare交易日历
    try:
        df = ak.tool_trade_date_hist_sina()
        trade_dates = set(str(d.date()) for d in df['trade_date'])
        return d.isoformat() in trade_dates
    except:
        return d.weekday() < 5  # 降级到weekday判断
```

## 验证铁律（防本session错误重现）

1. **非交易日只能验证API结构和错误处理**，不能验证数值准确性
2. **数值验证必须在交易日 9:30-15:00** 执行
3. **验证报告必须标注验证时间和交易日状态**
4. **交叉验证**：腾讯 vs AKShare 偏差>1%告警

## 参考仓库对比

| 仓库 | 非交易日处理 | 对我们的启示 |
|:-----|:------------|:------------|
| **a-stock-data** (Vibe-Research) | 无主动判断，API返回空/异常就代表非交易日 | 东财/同花顺底层API天然返回空，不需要特别处理 |
| **Vibe-Trading** | 回测层面自然过滤，无数据行自动跳过；缓存用end_date<today保护 | 回测场景不需要关注，但推送系统必须处理 |
| **我们（修复后）** | 每个数据返回带_stale/_fresh标记 + is_trading_day()前置判断 | 腾讯API的静默返回旧数据特性需要主动标记 |

关键区别：两个参考库都是**取数据工具库**，不是**推送系统**。它们的API底层天然在非交易日返回空，而我们用腾讯API做主力行情源且需要自动推送，必须主动检测和标记。
