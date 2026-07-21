# 基金系统 · 决策验证与进化闭环设计

> 创建日期：2026-07-15 | 基于用户对"如何验证建议有效性"的讨论

## 一、现状问题

| 问题 | 影响 | 状态 |
|:----|:----|:----:|
| JSONL严重重复（同一天采集N次） | 无法直接查询"某天唯一快照" | ❌ 待修 |
| 无决策日志 | 不知道系统推荐了什么操作 | ❌ 待建 |
| 信号归因`correct`字段全为null | KOL周报无法生成 | 🟡 待修 |
| KOL准确率周报无cron调用 | `generate_signal_report()`函数存在但从未运行 | ❌ 待建 |

## 二、闭环架构

```
每日推送（含操作建议）
  → 收盘后记录 decisions.jsonl（结构化存下每条建议）
  → 3天后回溯验证（比较建议方向 vs 实际走势）
  → 周末生成周报（系统准确率 + KOL排行榜）
  → 月度进化报告（调权重、改阈值）
```

## 三、数据格式设计

### 3.1 决策日志 `decisions.jsonl`

```json
{
  "_date": "2026-07-15",
  "market_direction_accuracy": "6/6正确",
  "group_recommendations": [
    {"group": "科技/AI", "recommendation": "持有", "reason": "科创新高延续"},
    {"group": "黄金", "recommendation": "不加仓", "reason": "占比26%>20%目标"},
    {"group": "新能源", "recommendation": "观察", "reason": ""}
  ],
  "kol_signals": [
    {"kol": "唐史主任", "text": "开融资仓吸点", "direction": "看多"}
  ],
  "price_snapshot": {
    "上证": 4094.40, "科创50": 2207.86, "黄金ETF": 8.750
  },
  "verification_3d": "pending"
}
```

3天后回溯时比较 `price_snapshot` 与3天后对应指数收盘价，判断每条建议对错。

### 3.2 每日快照 `daily-snapshots.jsonl`

```json
{
  "_date": "2026-07-15",
  "indices": {"上证": 4094.40, "科创50": 2207.86, "创业板": 4342.71},
  "overnight": {"道琼斯": 52182.74, "纳指": 25820.14, "黄金期货": 4030.5},
  "turnover": 153032596,
  "breadth": {"rise": 1200, "fall": 2800},
  "northbound": -65.56,
  "funds_summary": {"科技/AI": -2.64, "黄金": -0.96, "新能源": -3.56}
}
```

从现有JSONL中提取每天1条有效记录。

## 四、待建脚本清单

| 脚本 | 功能 | 优先级 |
|:----|:----|:------:|
| `log_daily_decisions.py` | 收盘后记录决策日志+价格快照 | P0 |
| `deduplicate_archives.py` | 从morning-briefs/closing-reviews等JSONL去重生成daily-snapshots | P0 |
| 修复 `resolve_past_signals()` | 让correct字段正确赋值（当前全部为null） | P0 |
| `generate_weekly_report.py` | 周度复盘（含KOL准确率周报） | P1 |

## 五、Cron注册坑点

⚠️ **关键**：cronjob的`script`参数不支持绝对路径和symlink。必须把脚本放在 `~/profiles/<profile>/scripts/` 目录下，以wrapper形式调用：

```python
# run_xxx.py (wrapper pattern)
import subprocess, sys
r = subprocess.run([sys.executable, '/opt/data/scripts/actual_script.py'],
    capture_output=True, text=True, timeout=120)
if r.stdout.strip(): print(r.stdout.strip())
```

## 六、存储方案

| 层级 | 路径 | 用途 |
|:----|:----|:-----|
| 本地JSONL | `/opt/data/fund_system_data/` | 日常追加 |
| R2 | `fund-system/data/` | 每天同步（已有`upload_to_r2()`函数） |
| QQ | 推送通道 | 周报/月报推送 |

JSONL格式足够（每天1行，一年365行），无需引入数据库。
