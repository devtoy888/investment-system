# AKShare 指数历史数据拉取

> 2026-07-15 整理。用于板块轮动分析、全年收益对比、近期趋势判断。

## 可用API

AKShare `stock_zh_index_daily()` 返回完整日K线数据（含日期、开高低收、成交量）。

```python
import os
os.environ['TQDM_DISABLE'] = '1'
import akshare as ak

df = ak.stock_zh_index_daily(symbol="sh000688")  # 全部历史数据
```

**注意：** date 列类型是 `datetime.date`，不是字符串。筛选时用 `df['date'] >= date(2026, 1, 1)`。

## 指数代码大全

| 指数 | 代码 | 用途 |
|:----|:----|:------|
| 科创50 | sh000688 | 科技/AI核心，全年涨幅判断 |
| 沪深300 | sh000300 | 大盘基准 |
| 中证医疗 | sz399989 | 医药板块轮动 |
| 中证消费 | sz399932 | 消费板块 |
| 中证白酒 | sz399997 | 白酒细分 |
| 中证半导体 | sz399967 | 半导体细分 |
| 创业板指 | sz399006 | 成长板块 |

## 三阶段分析法

### 阶段1：全年（YTD）

```python
from datetime import date
df = ak.stock_zh_index_daily(symbol="sh000688")
df_ytd = df[df['date'] >= date(2026, 1, 1)]
first_close = float(df_ytd.iloc[0]['close'])
last_close = float(df_ytd.iloc[-1]['close'])
ytd = (last_close / first_close - 1) * 100
```

**判断基准：** YTD > +5% = 全年强势 | -5% ~ +5% = 横盘 | < -5% = 全年弱势

### 阶段2：近20天

```python
recent = df_ytd.iloc[-20:]
if len(recent) >= 20:
    mtd = (float(recent.iloc[-1]['close']) / float(recent.iloc[0]['close']) - 1) * 100
```

**判断近期资金流向：** 近20天 vs YTD 方向一致 = 趋势延续 | 方向相反 = 正在反转

### 阶段3：每日涨跌矩阵

```python
indices = {'sh000688': '科创50', 'sz399989': '中证医疗', 'sz399967': '中证半导体'}
data = {}
for sym, name in indices.items():
    df = ak.stock_zh_index_daily(symbol=sym)
    df = df[df['date'] >= date(2026, 6, 15)]  # 近1个月
    data[name] = df

for dt in sorted(all_dates)[-15:]:
    for name in indices.values():
        row = data[name][data[name]['date'] == dt]
        if not row.empty:
            chg = close / prev_close - 1
            print(f"{'🟢' if chg>0 else '🔴'}{chg:+.2f}%")
```

## 实战案例（2026-07-15 分析结果）

```python
# 3周板块资金流向排序
医药:            +8.07%   🚀 最强流入
消费:            +6.55%   🚀
沪深300:         -1.07%   ➖
科创50:          -3.00%   📉
中证半导体:      -12.76%  🔻 最强流出
新能源/光伏:     -15.6%   🔻 最惨
```

## 腾讯API的局限性

| API | 可用性 | 说明 |
|:----|:------:|:------|
| `qt.gtimg.cn/q=sh000300` | ✅ 实时 | **不支持历史K线** |
| `web.ifzq.gtimg.cn/.../fqkline` | ❌ 关停 | 返回`bad params`/302跳转 |
| `push2.eastmoney.com/.../kline` | ❌ 502 | 常返回502 Bad Gateway |

**结论：** AKShare `stock_zh_index_daily()` 是目前唯一稳定可用的全年历史数据源。

## Pitfall

1. **TQDM进度条干扰** — 必须设置 `os.environ['TQDM_DISABLE'] = '1'`，否则前几个API调用会打印进度条到stdout
2. **date列类型** — 不是字符串，用 `df['date'] >= date(2026,1,1)` 不是 `df['date'] >= '2026-01-01'`
3. **指数代码格式** — `sh000688`（上证用sh前缀），`sz399989`（深证用sz前缀）
4. **首次调用较慢** — 约1-3秒，后续调用缓存后<1秒
