# 飞书消息格式与表格渲染 (2026-07-13 最终确认)

## 结论表

| 消息类型 | msg_type | GFM表格渲染 | 适用场景 | 验证方法 |
|:--------|:--------:|:-----------:|:--------|:--------|
| 纯文本 | text | ❌ | 简单通知 | ❌ |
| 富文本 | post (`tag:md`) | ❌ 不渲染 | 带格式的文字 | 测试 → 普通文字形式 |
| 消息卡片 | interactive (`tag:markdown`) | ❌ 不渲染 | 带格式的文字 | 测试 → 不是表格形式 |
| 卡片原生table | interactive (`tag:table`) | ✅ 仅此方案 | **唯一可行的表格式** | 测试 → 是表格 |

## 唯一可行方案：Card 2.0 原生 `table` 组件

结构：
```json
{
  "tag": "table",
  "page_size": 5,
  "columns": [
    {"name": "col_0", "display_name": "指数", "data_type": "text"},
    {"name": "col_1", "display_name": "收盘", "data_type": "text"},
    {"name": "col_2", "display_name": "涨跌", "data_type": "text"}
  ],
  "rows": [
    {"col_0": "科创50", "col_1": "2064.98", "col_2": "-5.53%"},
    {"col_0": "上证指数", "col_1": "3996.16", "col_2": "-1.00%"}
  ]
}
```

## 发送方式

### 方式A：直接API调用（推荐，绕过adapter）

使用 `send_feishu_cards.py` 工具：
```python
from send_feishu_cards import send_card, send_card_with_tables

# 纯markdown（无表格）：
send_card("卡片标题", "**markdown内容**", "blue")

# 含GFM表格（自动转为原生table组件）：
send_card_with_tables("卡片标题", "| H1 | H2 |\n|---|---|\n| A | B |", "red")
```

### 方式B：sitecustomize.py 补丁（有bug，谨慎使用）

通过 `PYTHONPATH=/opt/data/.feishu-deps` 加载 `sitecustomize.py`，该补丁在 `FeishuAdapter._build_outbound_payload()` 中检测 `_MARKDOWN_TABLE_RE`，自动将含表格的内容转为 `msg_type: interactive` 卡片。

**已知bug：** `_make_patched_send()` 的fallback路径在卡片发送失败时调用 `original_send(self, chunk, ...)`，但 `original_send` 内部调用的 `_build_outbound_payload` 已经是打过补丁的版本，导致重新进入卡片发送路径形成**无限循环**。

**修复：** fallback时应传递 `_strip_markdown_to_plain_text(chunk)` 而非 `chunk`。

### ⚠️ 补丁目标类名确认 (2026-07-13)

`sitecustomize.py` 中 `TARGET_CLASS = "FeishuAdapter"` 是正确的。适配器类名是 `FeishuAdapter` (文件 `/opt/hermes/plugins/platforms/feishu/adapter.py` 第1410行 `class FeishuAdapter(BasePlatformAdapter):`)，不是 `FeishuPlatformAdapter`。之前写错的 `FeishuPlatformAdapter` 导致补丁静默不生效。

## 多卡片拆分策略（重要）

**不要把所有内容塞进一张卡片**。按逻辑章节拆分：

| 推送 | 卡片数 | 每张内容 | 颜色 |
|:----|:-----:|:--------|:----:|
| 早报 | 7张 | 外盘/A股·量价·板块·持仓·操作·KOL·新闻 | 蓝·靛蓝·红·绿·紫·青·灰 |
| 盘中 | 3张 | 行情+量价·板块+北向+持仓·分析 | 靛蓝·红·靛蓝 |
| 收盘 | 5张 | 大盘·板块·持仓·预测验证·操作评估 | 蓝·红·绿·靛蓝·紫 |

## 卡片颜色规范

| 颜色 | template | 适用 |
|:----|:--------:|:----|
| 蓝色 | blue | 行情数据（外盘/指数） |
| 靛蓝 | indigo | 分析、量价 |
| 红色 | red | 板块排行、风险 |
| 绿色 | green | 持仓、收益 |
| 紫色 | purple | 操作建议、评估 |
| 青色 | wathet | KOL观点 |
| 灰色 | grey | 新闻、参考信息 |

## Emoji 规范（2026-07-13 用户明确要求）

所有涨跌方向相关的位置统一使用：
- 🔴 = 涨/正值
- 🟢 = 跌/负值
- 🟡 = 持平

应用范围：大盘涨跌、基金涨幅、板块排行、北向资金、分组趋势、操作评估、持仓估算。
不适用范围：量价分析信号emoji（🔥放量上攻、📈温和放量、💧放量下跌等 — 描述量价形态）。
代码模式：`emoji = '🔴' if val > 0 else '🟢' if val < 0 else '🟡'`
