# R2报告推送模式

## 问题背景

QQ Bot每条消息有4000字符上限（`MAX_MSG_LEN = 4000` in `send_qqbot.py`）。LLM深度分析动辄5000-6000字，被截断后后半部分丢失。

## 解决方案

**之前**：完整报告内容逐表推送 → QQ Bot截断，用户看不到完整分析 ❌

**现在**：MD+HTML上传R2 → 推送短摘要+链接 ✅

## 关键文件

| 文件 | 路径 | 说明 |
|:----|:----|:-----|
| 推送模块 | `/opt/data/scripts/push_report_r2.py` | 生成MD/HTML → 上传R2 → 推送短摘要 |
| 数据目录 | `/opt/data/fund_system_data/reports/` | 本地MD/HTML存档 |
| R2基础URL | `https://hermes-main-media.devtoy.xyz/fund-system/reports/` | 公开访问 |

## R2推送流程（push_report_r2.py内部逻辑）

```
push_report(report_type, title, data_tables, analysis)
  ├── ① 拼接完整MD: f"# {title}\n\n{data_tables}\n\n## 🤖 AI 深度分析\n\n{analysis}"
  ├── ② 保存本地MD → fund_system_data/reports/{type}_{date}.md
  ├── ③ 生成自适应HTML → fund_system_data/reports/{type}_{date}.html
  │     ├── 自动检测viewport，手机/电脑自适应
  │     ├── 蓝色主题表格样式
  │     └── pre标签包裹保持格式
  ├── ④ upload_to_r2() → MD和HTML上传到R2
  ├── ⑤ 推送短摘要（标题 + R2链接 + 分析的200字开头）
  └── 返回 (md_link, html_link)
```

## v2脚本改造模板（run_morning.py / run_closing.py）

```python
# 改动前：直接print完整分析 → QQ Bot截断
from llm_analysis_v2 import generate_v2, format_block
analysis = generate_v2("closing", use_cache=False)
if analysis:
    print(format_block("收盘 AI 深度分析", analysis))

# 改动后：R2推送 → 短摘要+链接
from llm_analysis_v2 import build_closing_data_v2, CLOSING_PROMPT_V2, call_ds
from push_report_r2 import push_report

analysis = call_ds(CLOSING_PROMPT_V2, data, max_tokens=2500, temp=0.3)
if analysis:
    analysis = analysis.replace("<br>", "\n").replace("<br/>", "\n")
    push_report(
        report_type="closing",
        title=f"收盘复盘 · {date.today().isoformat()}",
        data_tables=tables_text,
        analysis=analysis
    )
```

## HTML生成说明

`push_report_r2.py` 的 `build_html()` 使用 `html.escape()` 包裹完整MD内容到`<pre>`标签中：

- 不适合正式发布页，但作为**快速预览**足够
- 自动添加移动端 viewport meta
- 表格/代码着色通过CSS处理
- 如需更精美版本，可升级到Markdown→HTML渲染器（如mistune）

## 注意事项

1. `upload_to_r2()` 调用 `fund_tools` 中的函数，需要 `sys.path.insert(0, '/opt/data/scripts')`
2. R2 key命名规则：`fund-system/reports/{type}_{date}.{ext}`
3. 已改造的文件：`run_morning.py`, `run_closing.py`
4. 未改造的文件（仍走QQ Bot原生推送）：`run_noon.py`（午报较短，暂不改造）
