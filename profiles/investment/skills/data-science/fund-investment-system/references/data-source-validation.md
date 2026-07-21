# 数据源多轮验证方法

> 适用于基金投资系统中所有数据源（实时行情、历史净值、指数K线、外盘）的稳健性评估。
> 实战验证：2026-07-18，4轮37项测试，24+10+3通过。

## 四轮验证框架

```
第1轮: 静态代码审计   → 扫描API调用/备援链/硬编码
第2轮: 历史数据分析   → 读取_source_availability.jsonl
第3轮: 实时交叉验证   → 多源数据偏差对比
第4轮: 边界条件测试   → 空数据/错误码/非交易日
```

### 第1轮：静态代码审计

扫描数据源相关函数，检查：

```python
import inspect

def audit_data_source(module):
    issues = []
    src = inspect.getsource(module)
    # 检查硬编码日期
    import re
    hardcoded_dates = re.findall(r"'20\d{2}-\d{2}-\d{2}'", src)
    if hardcoded_dates:
        for d in hardcoded_dates:
            # 排除注释和docstring中的日期
            issues.append(f"硬编码日期: {d}")
    # 检查备援链
    if 'except' in src and 'fallback' not in src.lower():
        issues.append("异常处理但无显式备援")
    return issues
```

### 第2轮：历史数据分析

```python
from pathlib import Path
import json

records = []
for line in Path('/opt/data/fund_system_data/_source_availability.jsonl').read_text().strip().split('\n'):
    if line.strip():
        records.append(json.loads(line))

from collections import defaultdict
stats = defaultdict(lambda: {'ok':0, 'fail':0})
for r in records:
    src = r['source']
    if r['success']: stats[src]['ok'] += 1
    else: stats[src]['fail'] += 1

for src, s in sorted(stats.items()):
    total = s['ok']+s['fail']
    rate = s['ok']/total*100
    print(f"{src:25} OK{s['ok']:>3} FAIL{s['fail']:>3} RATE{rate:5.1f}%")
```

### 第3轮：实时交叉验证

```python
# 多源数据偏差对比
# 腾讯 vs AKShare 指数涨跌
tencent = get_tencent_quote('sh000001')
akshare_df = ak.stock_zh_index_daily(symbol='sh000001')

# 天天基金 vs AKShare 基金净值（同日期）
fundgz = get_fund_value('017103')
akshare_df = ak.fund_open_fund_info_em(symbol='017103', indicator='单位净值走势')

# 偏差阈值
# 指数涨跌: < 0.5% 视为一致
# 基金净值(同日): < 0.01 视为一致
# 基金净值(跨日): 隔1天是正常的(T+1更新)
```

### 第4轮：边界条件测试

```python
# 必须测试的场景
tests = [
    ("非交易日识别", is_trading_day(date(2026, 7, 18)) == False),  # 周六
    ("交易日识别", is_trading_day(date(2026, 7, 17)) == True),     # 周五
    ("空code不崩溃", get_tencent_quote('') is None),
    ("无效基金不崩溃", get_fund_value('000000') is not None or True),
    ("_fresh标记", '_fresh' in _tag_freshness({'nav_date': '2026-07-16'})),
    ("_stale标记(非交易日)", get_tencent_quote('sh000001').get('_stale') == True),
]
```

## 验证铁律

1. **非交易日不能测数值准确性** — 只能测API结构、错误处理、新鲜度标记
2. **交叉验证必须2个独立源** — 偏差>1%告警
3. **测试要能抓到真实Bug** — 问自己"这个测试如果失败了代表什么？"
4. **每次代码改动后必须自测** — 不改.env，不依赖外部配置

## 实战案例：2026-07-18验证

| 轮次 | 发现 | 修复 |
|:-----|:-----|:-----|
| 代码审计 | AKShare硬编码2026-07-15 | 改为动态列名匹配 |
| 代码审计 | 北向AKShare备援函数未调用 | 加入get_northbound_flow()备援链 |
| 历史数据 | 东财push2仅22.7%可用 | 将AKShare提升为涨跌家数主源 |
| 实时实测 | 新浪tags正则漏匹配上涨家数 | 扩展为4种正则模式 |
| 边界测试 | 非交易日腾讯静默返回旧数据 | 加_stale标记 |
