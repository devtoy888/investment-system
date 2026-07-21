# AKShare实时估算全量API（2026-07-21确认可用）

## 调用方式（主线程，一次性）

```python
import akshare as ak
import pandas as pd

df = ak.fund_value_estimation_em()  # ~20秒, 返回20000+基金
est_col = [c for c in df.columns if '估算增长率' in c]
name_col = [c for c in df.columns if '基金名称' in c]

for _, row in df.iterrows():
    code = str(row['基金代码'])
    if code in our_codes:
        name = row.get(name_col[0], '') if name_col else ''
        val = str(row.get(est_col[0], '0')).replace('%', '').strip()
        est_change = float(val) if val and val != '---' else 0.0
        print(f"  {code} {name}: {est_change}%")
```

## 为什么之前没用这个API

`fund_source_akshare.get_fund_realtime()` 包装了这个API但加了 `signal.alarm(10)` 超时。信号量机制在子线程中抛 `ValueError: signal only works in main thread`。主线程直接调用 `ak.fund_value_estimation_em()` 正常工作。

## 精度对比（2026-07-21实测）

### 板块代理 vs AKShare实时

| 基金代码 | 基金名称 | 板块代理 | AKShare实时 |
|:--------|:---------|:--------:|:-----------:|
| 024418 | 华夏上证科创板半导体材料设备 | +8.3% | **+15.8%** |
| 011712 | 大摩万众创新混合C | +6.2% | **+11.5%** |
| 011613 | 华夏科创50ETF联接C | +6.9% | **+10.7%** |
| 026449 | 大摩沪港深科技混合C | +1.4% | **+7.2%** |
| 020233 | 大摩景气智选混合C | +8.3% | **+7.0%** |
| 011103 | 天弘中证光伏C | +2.6% | **+3.8%** |
| 003096 | 中欧医疗健康混合C | -0.3% | **+1.1%** |
| 009478 | 中银上海金ETF联接C | +1.0% | **+0.0%** |

结论：板块代理在细分指数上严重低估（024418差7.5%），部分基金方向判断相反（003096估-0.3%实+1.1%）。**AKShare实时估算优于板块代理。**

## 集成到 execute_today_plan.py

在 `build_portfolio()` 开头、读取seed/ops之后，主线程一次性获取：

```python
fund_realtime = {}
try:
    import akshare as ak
    df = ak.fund_value_estimation_em()
    est_col = [c for c in df.columns if '估算增长率' in c]
    if est_col:
        for _, row in df.iterrows():
            code = str(row['基金代码'])
            if code in merged:
                val = str(row.get(est_col[0], '0')).replace('%', '').strip()
                fund_realtime[code] = float(val) if val and val != '---' else 0.0
    print(f"  ✅ AKShare实时估算: {len(fund_realtime)}支基金", file=sys.stderr)
except Exception as e:
    print(f"  ⚠️ AKShare全量估值: {e}", file=sys.stderr)

# 然后在循环中：
if code in fund_realtime:
    est_change = fund_realtime[code]
    est_source = "AKShare"
else:
    # 降级到板块代理
    est_change = sectors.get(proxy_sector, 0.0)
    est_source = "板块代理"
```

## 避免的坑

1. **不能放子线程/ThreadPoolExecutor** — 直接 `ak.fund_value_estimation_em()` 在主线程正常，但如果在 `get_all_funds()` 的线程池中调用（通过信号量包装），会崩溃。
2. **一次性调用** — ~20秒全量获取，不要改为每次查1只（会触发20000次网络请求）。
3. **列名动态匹配** — AKShare列名含日期（如 `"2026-07-21-估算数据-估算增长率"`），用 `[c for c in df.columns if '估算增长率' in c]` 动态匹配。
