# 2026-07-15 Session: KOL分析重构 + 数据降级 + 消息合并

## KOL 分析策略变更

### 原问题
- 每条微博都做黑话破译 → 信息过载，用户不需要每条都分析
- 显示互动数（转发/评论/点赞）→ 无用噪音
- 评论分析提取板块讨论 → 权重过高且低价值
- 无事实核查 → 博主说的数值断言未验证

### 修正后

| 方面 | 旧行为 | 新行为 |
|:---|:---|:---|
| 黑话分析 | 每条微博跑 `interpret_weibo()` | **仅今日信号帖**（含 `SIGNAL_TRIGGERS` 关键词） |
| 历史帖子 | 全部深度分析 | 仅做赛道情绪统计（趋势一致性参考） |
| 互动数 | `🔄x 💬y ❤️z` | **彻底移除** |
| 评论分析 | 拉20条，分析板块讨论，出5条热评 | **仅主任回复**（最多3条），低权重 |
| 事实核查 | 无 | `fact_check_kol_claims()` 交叉验证数值断言 |
| 深度解读 | `generate_kol_deep_analysis()` 生成大段黑话 | **移除**（不再调用） |

### 触发逻辑
```python
SIGNAL_TRIGGERS = ['加仓','减仓','清仓','抄底','反弹','底部','泡沫','风险',
                   'ICU','KTV','IPO','放量','缩量','格局','右侧','机会','警惕',
                   '止损','触底','泡沫','过热','扫货','建仓','离场','逃顶']

p['is_signal'] = any(kw in p['text'] for kw in SIGNAL_TRIGGERS) and _is_today_post(p)
```

### `fact_check_kol_claims()` 函数
位置: `fund_tools.py` (紧接在 `interpret_weibo()` 之后)

支持3类验证:
1. **指数/板块涨跌幅**: 匹配 `"名称 + 涨/跌 + 数字%"` 模式，三级偏差: ✅<0.3% / ⚠️<1.0% / ❌≥1.0%
2. **成交额**: 匹配 `"成交X万亿"` 或 `"成交量X亿"`(仅千亿以上)，对照 `market_overview.total_turnover`
3. **北向资金**: 匹配 `"北向流出/流入X亿"`，对照 `northbound.total`

盘中运行时，行情数据从 `prev_close` 获取昨收价，涨跌幅无法从腾讯API实时数据获取（API只给今日涨跌幅）。

## 行情数据源 3级降级

`collect_morning_data.py` 昨日数据采集优先级:

```
① _yesterday_snapshot.json  (收盘快照) → 最完整
② morning-briefs.jsonl       (存档恢复) → 有涨跌幅和成交额
③ 腾讯API prev_close         (盘中保底) → 昨收价正确,涨跌幅暂缺
```

### 盘中自动检测
```python
in_market = (now_hour == 9 and now_min >= 30) or (10 <= now_hour <= 10) or \
            (now_hour == 11) or (13 <= now_hour <= 14)
```
检测到盘中 + 无①② → 用 `prev_close` 替代 `price` 作为昨日收盘价，`change_pct` 标 0.00。

### 腾讯API限制
- ✅ `prev_close` (parts[4]) = 昨日收盘价，盘中也可获取
- ❌ 昨日涨跌幅 = 无法从实时API推导（需要对比前日收盘，API没有该字段）
- ❌ k-line API (`ifzq.gtimg.cn`) 从该服务器无法连通

## QQ消息合并推送

### 修改前
`send_qq_bot.py` 的 `send_markdown_in_chunks()` 按 `═══` 分隔符切分内容，每个card独立成一条消息 → 8-12条

### 修改后
所有内容合并为连续Markdown，**仅按QQ 3800字符限制**切分:
- 标题 `## 📚 {title}` 只加一次
- 多段时自动加 `_(📎 接上条)_` / `_(📎 续下条)_` 标记
- 自动过滤脚本状态行（`OK `, `FAIL `, `All done`, `Morning cards done`）

结果: 6435字符早报 → **2条消息**（原8条）

## Bug修复
- `fund_tools.py:1715`: `raw.get()` → `raw_data.get()` (变量名错误导致 `run_sanity_checks` 崩溃)
