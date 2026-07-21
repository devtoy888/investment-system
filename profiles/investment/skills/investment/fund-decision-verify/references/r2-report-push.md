# R2 报告推送方案（2026-07-21）

## 问题

QQ Bot 推文上限 4000 字符，长报告（早报 5000+、收盘 8000+）被截断，后半部分关键内容丢失。用户要求改为推送短摘要 + 链接。

## 方案

推送短摘要（含 R2 链接），完整报告以 MD + HTML 形式上传 R2。

## 使用方式

```python
from push_report_r2 import push_report

md_link, html_link = push_report(
    report_type="morning",          # 唯一标识，用于文件名
    title="财经早餐 · 2026-07-21",  # 报告标题
    data_tables=tables_text,        # 数据表（Markdown格式）
    analysis=analysis               # LLM分析内容（Markdown格式）
)
```

`push_report()` 内部流程：
1. 合并 data_tables + analysis → 完整 MD 文件存本地
2. 调用 `build_html()` → 自适应 HTML 文件
3. `upload_to_r2()` → 上传到 `fund-system/reports/` 目录
4. `_output()` → 推送短摘要到 QQ Bot（含 MD 链接 + HTML 预览链接）

## QQ Bot 推送内容格式

不再推送完整分析，改为：

```
📊 **财经早餐 · 基金参考 · 2026-07-21**

🤖 AI分析完成（4719字）

📄 [Markdown报告](https://hermes-main-media.devtoy.xyz/...)
🌐 [HTML预览](https://hermes-main-media.devtoy.xyz/...)

📌 核心要点：
> (前几行摘要)
```

## 核心函数：`build_html()`

不要用 `<pre>` 简单包裹 MD 文本。设计要点：

- **深色渐变 header**（`#1a1a2e → #0f3460`）
- **白色卡片 body**（`border-radius: 12px, box-shadow`）
- **表格颜色标记**（🔴 = `.up { color: #e74c3c }`，🟢 = `.down { color: #27ae60 }`）
- **手机自适应**（`@media max-width: 600px`）
- **section 头标 emoji**（🌙步骤1/👁️步骤2/🗺️步骤3/⚠️步骤4/🎯步骤5）
- **基金卡片**（带左侧 4px 彩色边框，`.fund-card` 类）
- **风险框**（红色边框，`.risk-box`）
- **标签**（`.tag-buy` 绿色 / `.tag-sell` 红色 / `.tag-hold` 橙色）

## 已改造的任务

| 任务 | 文件 | 推送方式 |
|:----|:----|:---------|
| 🍳 早报 09:00 | `run_morning.py` | R2 |
| ☕ 午报 11:35 | `run_noon.py` | R2 |
| 📝 收盘 16:00 | `run_closing.py` | R2 |
| 📈 开盘 09:35 | `run_execute_plan.py` | R2（wrapper） |
| 📋 14:30决策 | `run_execute_plan.py` | R2（wrapper） |
| 🌍 周末外盘 周六 | `run_weekend.py` | R2 |
| 📚 周度复盘 周日 | `run_weekly_review.py` | R2 |
| 🔄 AI进化验证 10:00 | `run_evolution_verify.py` | R2 |

## 完整源代码

见 `/opt/data/scripts/push_report_r2.py`
