# Monitor Report Format Rules (2026-07-06)

## Multi-Iteration Optimization (4+ revisions from user feedback)

### Core Rule: Structure Only, Never Trim Content

When converting no_agent script output from plain text to structured format:
1. Count data items PER DIMENSION in original output
2. Verify new version has same count or more
3. User explicitly rejected truncated D3 (组内表现), D4 (关联标的), and shortened signal lists

### [4] 逐基诊断表格式 (2026-07-06 紧迫度列回归)

| 代码 | 名称 | 组别 | 估值 | 评分 | 紧迫度 | 建议 |
|:----|:----|:----:|:----:|:---:|:-----:|:----:|
| 017103 | 大摩数字经济混合C | 科技/AI | -2.59% | -2.0 | 🔴高 | 🔴 减仓观望 |

**关键规则：**
- 紧迫度列在"评分"与"建议"之间，显示为 `🔴高`/`🟢低`/`🟡中`
- 建议列使用 `rec` 自身的 emoji（如 `🔴 减仓观望`），**不加额外的紧迫度 emoji 前缀** — `rec` 字段已内置 emoji（来自 score_group_action 的返回值如 `🔴 减仓观望`、`🟡 持有`）
- 紧迫度 emoji 仅用于紧迫度列自身，不重复作用于建议列（避免出现 `🔴🔴` 双重 emoji）
- 排序：高→中→低，同紧迫度按评分降序

### 表格宽度规则（适用于QQ渲染）

- 7列（含紧迫度）已接近QQ markdown最大宽度，列名尽量精简
- 名称列截断至16字符（`name[:16]`），组别截断至6字符
- 如需更窄，可将"名称"列移至表尾或缩短代码列

### Per-Fund Detail Section Format (Final)

```
📌 017103 大摩数字经济混合C 🔴

今日: 大跌-2.59%

趋势: 近3日均跌-0.69% — 弱势下行 | 连跌3日

组内: 🚩 落后组均-1.52% (排名7/7) | 组均值-1.07% | 最佳=华夏科创50ETF联接C(+1.04%)

关联: 🟢 科创50: +1.04% — 偏强

量价: 📈 半导体: 温和放量(振幅6.4%) | 📈 科创50: 温和放量(振幅5.5%)

信号: 📉 今日大跌 | 🚩 组内落后(排名7/7)
```

### DO Maintain:
- Each dimension on its own line: 今日/趋势/组内/关联/量价/信号
- Blank line between dimensions for readability
- Group average (组均值) AND best fund (最佳=)
- Multiple volume signals from different related sectors
- All signal items (no 3-item limit)

### DON'T:
- Merge dimensions onto one line (user rejected compact 1-line format)
- Remove D3 (组内表现) or D4 (关联标的) detail
- Limit signal list to N items
- Add emoji prefixes to dimension labels (use bare 今日:/趋势:/组内:/关联:/量价:/信号:)

### Summary Section Format

| Direction counts | `| 方向 | 数量 |` table |
| Group ranking | `| 组别 | 评分 | 建议 |` table |
| Watch-list alerts | `| 代码 | 名称 | 估值 | 建议 |` table |

### Table Width Rule (for QQ rendering)
- Max 4-5 columns per table
- Tables wider than 5 columns wrap badly on QQ
- Group summary table: 5 columns (组别/支/均值/评分/建议)
- Fund diagnostics table: 4 columns (代码/名称/估值/建议) - 6 columns wraps badly
