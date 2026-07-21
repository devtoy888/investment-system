# R2 报告推送架构

> 2026-07-21 定型。所有LLM定时报告改为：QQ Bot推送短摘要+链接，完整MD+HTML上传R2。

## 核心文件

| 文件 | 作用 |
|:-----|:------|
| `/opt/data/scripts/push_report_r2.py` | 推送核心：保存MD→生成HTML→上传R2→短摘要推送 |
| `/opt/data/scripts/report_manager.py` | 报告管理系统：索引/归档/复盘 |
| `/opt/data/scripts/review_engine.py` | 审阅进化引擎：质量审查+预测验证+操作回溯+看板 |

## 数据流

```
预采集脚本 (collect_*.py)
       ↓
build_*_data_v2() 构建数据 → call_ds() LLM分析
       ↓
push_report(report_type, title, data_tables, analysis)
  ├── 1. 保存本地MD
  ├── 2. _build_html() → 生成美观HTML（分区块+深浅模式）
  ├── 3. upload_to_r2() MD + HTML
  └── 4. 短摘要推送到QQ Bot
```

## `push_report_r2.py` 关键函数

### `push_report(report_type, title, data_tables, analysis)`

标准入口。参数：
- `report_type`: `morning`/`noon`/`decision`/`closing`/`weekly`/`weekend`/`verify`
- `title`: 报告标题
- `data_tables`: 数据表部分的Markdown（从预采集脚本读取的文件内容）
- `analysis`: LLM生成的深度分析文本

### `_build_html(md, title)`

Markdown→HTML渲染。**不是把MD丢进`<pre>`**，而是：

1. **分割区块**：在`## 🤖 AI 深度分析`处分割为数据表区 + AI分析区
2. **数据表渲染**：`_render_table()` 将 `|` 分隔表格转为HTML `<table>`，自动跳过 `:---` 分隔行
3. **步骤卡片**：`_parse_steps()` 按`###`分离AI分析步骤，每步渲染为 `.st` 卡片（左边框颜色编码）
4. **基金操作表**：步骤5的基金表格用 `_render_fund_table()` 渲染，带优先级颜色标记
5. **内联格式**：`_fmt()` 处理 `**粗体**`→`<strong>`，`🔴`/`🟢`→`<span class="up/down">`
6. **CSS变量深浅模式**：`:root` + `.dk` class + 右上角按钮 + `window.matchMedia`系统检测

### Markdown语法支持

| 语法 | 渲染方式 |
|:-----|:---------|
| `#### H4标题` | `<h4>` 带左竖线 |
| `### H3标题` | `<h3>` |
| `**粗体**` | `_fmt()` 用re.sub转`<strong>` |
| `|表格|` | `_render_table()` 自动跳过`:---`行 |
| `> 引用` | `<blockquote>` 左竖线 |
| `- 列表` / `1. 列表` | `.li` class 左三角 |
| `🔴`/`🟢` | `.up`红色 / `.down`绿色 |
| `---` | 忽略（不渲染） |

### 深浅模式实现

```css
:root { --bg:#f0f2f5; --cd:#fff; --tx:#1a1a2e; ... }
.dk { --bg:#0d0d1a; --cd:#16162a; --tx:#e0e0e0; ... }

body { background: var(--bg); color: var(--tx); }

/* 切换按钮 */
.tg { position:fixed; top:10px; right:10px; ... }

/* 系统自动匹配 */
if(window.matchMedia("(prefers-color-scheme:dark)").matches)
  document.body.classList.add("dk");
```

**注意**：不要用 `filter: invert(1)` 粗暴反色——图片会反色。正确做法是CSS变量切换。

## `report_manager.py` 核心功能

### 路径生成 `report_paths(report_type, dt)`

```python
fund-system/reports/{year}/{month:02d}/{day:02d}/{type}.md
fund-system/reports/{year}/{month:02d}/{day:02d}/{type}.html
```

### 索引维护 `_update_index()`

- 读取/写入 `index.json`
- 自动生成月度归档 `{year}/{month:02d}/index.html`

## `review_engine.py` 核心功能

每日17:00自动运行完整审阅周期：

```python
full_review_cycle() → {
  "reviews": {每份报告的质量审查},
  "verification": {预测准确率},
  "backtest": {操作信号统计},
  "evolution": {进化建议},
  "dashboard_url": "复盘看板地址"
}
```

### 质量审查规则

| 报告类型 | 必须含章节 | 最小字数 |
|:---------|:----------|:--------:|
| morning | 步骤1-5 | 1500 |
| noon | 午/午后/操作 | 1000 |
| decision | 操作/基金/建议 | 800 |
| closing | 步骤1-5 | 2000 |

## 所有 R2 推送的任务

| 任务 | cron script 路径 | 原始推送 | 改为 |
|:-----|:-----------------|:---------|:-----|
| 早报 | `run_morning.py` | 直接call_ds | `push_report("morning", ...)` |
| 午报 | `run_noon.py` | 直接call_ds | `push_report("noon", ...)` |
| 收盘 | `run_closing.py` | generate_v2 | `push_report("closing", ...)` |
| 开盘/14:30 | `run_execute_plan.py` | execute_today_plan.py | wrapper捕获stdout→R2 |
| 周末 | `run_weekend.py` | generate_v2 | `push_report("weekend", ...)` |
| 周度 | `run_weekly_review.py` | weekly_review.py | `push_report("weekly", ...)` |
| 预测验证 | `run_evolution_verify.py` | evolution_engine | `push_report("verify", ...)` |

## Pitfalls

1. **HTML不要用`<pre>`包裹全文**— 看起来是纯文本dump。必须分区块渲染。
2. **不要用`filter: invert()`做深色模式**— 图片会反色。用CSS变量。
3. **表格`white-space:nowrap`导致水平滚动**— 设`vertical-align:top`让内容换行。
4. **`:---`分隔行必须跳过**— `_render_table()` 检查 `all(c in '|:- ' for c in s)`。
5. **`####` H4需要单独处理**— `_render_step_body` 最前面检查 `s.startswith('#### ')`。
6. **`**bold**`在HTML中不能直接显示**— 必须用`re.sub(r'\*\*(.+?)\*\*', '<strong>\\1</strong>', text)`。
