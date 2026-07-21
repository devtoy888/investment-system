# Risk Warning 连跌检测按日期去重

> 2026-07-15 修复。`fund-daily-trend.jsonl` 在同一天内多次追加导致误报。

## 问题现象

推送内容显示三条相同的日期但不同的数值：
```
🔴 华夏科创50ETF联接C(011613) 连跌3天: 
  2026-07-15(-2.69%), 2026-07-15(-2.79%), 2026-07-15(-4.03%), 累计-9.51%
```

用户质疑数据准确性，因为三条都是同一天。

## 根因

`risk_warning.py` 每次运行（08:00/11:35/14:30/16:00）都会追加一条记录。一天产生4-8条同日期记录。

**旧代码（bug）：**
```python
hist = defaultdict(list)
for rec in trend:
    d = rec.get("_date", "")
    for code, chg in rec.get("changes", {}).items():
        hist[code].append((d, chg))        # 全部追加

for code, values in hist.items():
    recent = values[-3:]                    # 最后3条记录 → 全是同一天！
```

**修复：**
```python
hist = defaultdict(dict)
for rec in trend:
    d = rec.get("_date", "")
    for code, chg in rec.get("changes", {}).items():
        hist[code][d] = chg                # 同日期后来的覆盖前面的

for code, date_changes in hist.items():
    recent = sorted(date_changes.keys())[-3:]
    last3 = [(d, date_changes[d]) for d in recent]
```

## 关键改动

| 旧 | 新 |
|:--|:--|
| `defaultdict(list)` | `defaultdict(dict)` |
| `.append()` | `[d] = chg`（按日期去重） |
| `values[-3:]`（记录索引） | `sorted(keys)[-3:]`（日期排序） |

## 防复发

涉及 `fund-daily-trend.jsonl` 读取的代码修改必须检查按日期去重逻辑。
