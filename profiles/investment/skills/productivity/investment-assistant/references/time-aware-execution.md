# 时间感知执行脚本 — 交易时段判定 + 防假实时数据

> 来源: 2026-07-16 用户纠正"今天还没开盘，你只是参考昨天的数据吧"。
> 核心: 执行/决策脚本必须区分交易时段，绝不能用昨日过期估值充当"今日实时"。

## 一、致命陷阱：非交易时段跑出假实时指令

`get_fund_value(code)` 在非交易时段返回的是**上一交易日的官方净值**，
`estimated_change` 字段却仍是**昨天盘中**的旧估算（接口未刷新）。
例如 7/16 盘前跑，返回 `nav_date: 2026-07-14, estimated_change: 5.68`（7/15盘中旧值）。
若脚本直接 print 这个 5.68% 并说"今日医疗+5.68%不买"，就是**虚假实时指令**。

**判定规则**：
- `nav_date == 今日` 且当前为交易时段(9:30-15:00) → 估值有效
- 否则 → 该估值不可作为"今日实时"，只能用于回顾

## 二、时间感知骨架（直接复用）

```python
from datetime import datetime, timedelta

def is_trading_time():
    """北京 9:30-15:00，排除午休(11:30-13:00)"""
    now = datetime.now() + timedelta(hours=8)   # 容器内UTC→BJT
    bjt = now.hour * 60 + now.minute
    if 570 <= bjt <= 690:   # 9:30-11:30
        return True
    if 780 <= bjt <= 900:   # 13:00-15:00
        return True
    return False

# 主流程
if not is_trading_time():
    # 盘前/盘后：只回看近几日K线(腾讯kline)，给预案，不产假实时指令
    print("⚠️ 非交易时段，等待开盘/14:30重跑")
    return
# 交易时段：拉真实盘中估值
kcb50 = get_index_change("sh000688")   # 腾讯 qt.gtimg.cn
med = get_realtime_fund("003096")      # 天天基金 fundgz
```

## 三、实时数据接口

```python
# 指数实时涨跌%（腾讯 qt.gtimg.cn，字段~32是涨跌幅百分点）
import requests
r = requests.get(f"https://qt.gtimg.cn/q=sh000688", timeout=8,
                 headers={"User-Agent": "Mozilla/5.0"})
fields = r.text.split('"')[1].split('~')
kcb50_chg = float(fields[32]) if len(fields) > 32 else None

# 基金实时估值%（天天基金 fundgz，estimated_change 字段）
from fund_tools import get_fund_value
v = get_fund_value(code)
chg = float(v.get('estimated_change', '0'))   # 仅交易时段有效
nav_date = v.get('nav_date', '')              # 校验是否今日
```

## 四、双时点 cron 模式（已落地 2026-07-16）

执行/决策脚本配两个定时任务，均 `no_agent=true` + `deliver=origin`：
- **09:35** 开盘后：拉真实盘中数据，给开盘后建议
- **14:30** 决策点：结合当日实时 + 近几日K线趋势，给最终决策

脚本位置: `/opt/data/scripts/execute_today_plan.py`（同时软链/复制到
`~/.hermes/scripts/` 供 cron 以相对名调用）。

## 五、近几日走势回顾数据源

非交易时段需展示"近几日走势"时用腾讯K线（容器可连通）：
```
https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={sym},day,2026-06-15,2026-07-15,250,qfq
# 返回 data[sym].day = [[日期,开,收,高,低,量],...]，close 在 index 2
```
注意：该接口从 `hermes-main` 容器连续请求会被限流，单条 `docker exec curl` + 间隔2-5秒。
若限流，退路是 AKShare `stock_zh_index_daily`（场内指数更稳）。
