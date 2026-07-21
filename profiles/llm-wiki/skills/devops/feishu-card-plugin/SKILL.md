---
name: feishu-card-plugin
description: "Feishu Card 2.0 消息卡片插件 v2 — 混合策略：含表格走 Card 2.0，纯文本/代码走 Post 格式"
version: 2.0.0
author: Hermes Agent
tags: [feishu, card, message, plugin, devops, hybrid-strategy]
---

# Feishu Card 2.0 消息卡片插件 v2

## 用途

用用户插件覆盖 Hermes 内置的 Feishu 适配器，采用**混合消息策略**：

```
消息内容
├── 含表格 ──→ Card 2.0（动态彩色标题 + 原生表格组件）
└── 不含表格 ──→ Post 格式（代码块有复制按钮 + 完整展开）
```

## v2 变更 (2026-07-13)

| 版本 | 策略 | 说明 |
|:---:|:---:|:---|
| v1 | 全部 Card 2.0 | 表格、代码块均走卡片，但代码块无复制按钮 |
| **v2** | **混合** | 代码块→Post（有复制按钮），表格→Card 2.0（正常渲染） |

## 为什么混合？

实测对比发现飞书三种消息格式各有优劣：

| 能力 | Post (`tag:"md"`) | Card 1.0 (`tag:"markdown"`) | Card 2.0 (`tag:"markdown"`) |
|:---|---:|:---:|:---:|
| 代码块复制按钮 | ✅ 有 | ❌ 无 | ❌ 无 |
| 代码完整展开 | ✅ 全部行可见 | ❌ 截断前2行 | ⚠️ 需滑动 |
| 语法高亮 | ✅ | ✅ | ✅ |
| 表格渲染 | ❌ 降级纯文本 | ❌ | ✅ GFM |
| 动态卡片标题 | ❌ | ✅ | ✅ |

**关键发现**：飞书 API 无论哪种格式都无法触发客户端原生代码块组件（右上角复制按钮）。复制按钮只出现在用户手动通过聊天框发送的代码块消息中。Post 格式的 `tag:"md"` 代码块有复制按钮、且完整展开，是最优选择。

## 插件原理

Hermes 的 `PlatformRegistry` 支持 "last writer wins" 覆盖内置适配器。用户插件注册同名 `"feishu"` 平台条目替换内置适配器。

## 文件结构

```
/opt/data/profiles/llm-wiki/plugins/feishu-card/
├── plugin.yaml        # 插件清单
└── __init__.py        # CardFeishuAdapter 实现
```

## 核心实现：混合策略

### `_build_outbound_payload()`

```python
def _build_outbound_payload(self, content: str) -> tuple[str, str]:
    # Hybrid strategy:
    # - Content with tables → Card 2.0 (table rendering + dynamic header)
    # - Content without tables → Post format (copy button + full code block)
    if _MARKDOWN_TABLE_RE.search(content):
        return self._build_card_with_tables(content, *_detect_header_style(content))
    return super()._build_outbound_payload(content)
```

### 带表格的 Card 2.0 结构

当内容含表格时，调用 `_build_card_with_tables()` 将 Markdown 表格解析为 CardKit 2.0 原生 `table` 组件：

```json
{
  "schema": "2.0",
  "header": {"title": {"tag": "plain_text", "content": "📊 数据"}, "template": "turquoise"},
  "body": {
    "elements": [
      {"tag": "markdown", "content": "说明文字"},
      {
        "tag": "table",
        "page_size": 100,
        "columns": [
          {"name": "col_0", "display_name": "列名", "data_type": "text", "horizontal_align": "left"}
        ],
        "rows": [{"col_0": "值"}]
      }
    ]
  }
}
```

### 无表格时走 Post 格式

调用父类 `FeishuAdapter._build_outbound_payload()`，它返回 `msg_type="post"` 的 `tag:"md"` 格式。该格式下代码块有复制按钮、完整展开。

### Markdown 表格解析

`_parse_markdown_table()` 将标准 Markdown 表格转为 columns + rows：

```
| Name | Value |     →     columns: [{name: "col_0", display_name: "Name"}, ...]
|------|-------|          rows: [{col_0: "foo", col_1: "1"}, ...]
| foo  | 1     |
```

### 混排内容分割

`_split_content_blocks()` 将消息分成文段和表格的交替序列，保持原有顺序。

## 动态卡片样式规则

`_detect_header_style(content)` 按优先级匹配（仅含表格时生效）：

| 优先级 | 内容特征 | 标题 | 颜色 |
|--------|---------|------|:----:|
| 1 | 首个 Markdown 标题 `## xxx` | 标题内容 | 后续规则定 |
| 2 | error/fail/exception/❌ | ⚠️ 错误 | 🔴 red |
| 3 | warning/⚠️ | ⚠️ 警告 | 🟠 orange |
| 4 | Markdown 表格 | 📊 数据 | 🟢 turquoise |
| 5 | 代码块 ``` | 🛠 技术 | 🟣 indigo |
| 6 | 编号列表/无序列表 | 📋 清单 | 🟢 green |
| 7 | vs/对比/比较 | ⚖️ 对比 | 🟣 purple |
| 8 | 加粗文本 `**` | ℹ️ 信息 | ⚪ grey |
| 9 | 其他 | ℹ️ 信息 | 🔵 blue |

## 部署步骤

### 1. 创建/更新插件文件

```bash
mkdir -p /opt/data/profiles/llm-wiki/plugins/feishu-card/
```

写入 `plugin.yaml` 和 `__init__.py`。

### 2. 启用插件

```bash
hermes config set plugins.enabled '[feishu-platform, feishu-card]'
```

验证 YAML 格式——必须是列表，不是 JSON 字符串：
```yaml
plugins:
  enabled:
    - feishu-platform
    - feishu-card
```

### 3. 重启 Gateway

Gateway 进程对 SIGTERM/SIGINT 免疫，必须用 `kill -9`：

```bash
# 清除缓存 + 重启
find /opt/data/profiles/llm-wiki/plugins/feishu-card -name "__pycache__" -type d -exec rm -rf {} +
ps aux | grep "llm-wiki.*gateway" | grep -v grep | awk '{print $2}' | xargs kill -9
# s6-supervise 会自动重启
```

## 验证

### 发送测试消息

| 测试 | 内容 | 预期路由 | 检查点 |
|:---:|:---|:---:|:---|
| 1 | 纯代码块（多行 Python 函数） | → Post | 有复制按钮、完整展开、语法高亮 |
| 2 | 纯表格（Markdown 表格） | → Card 2.0 | 表格渲染正常、有彩色卡片标题 |
| 3 | 代码块+表格混合 | → Card 2.0 | 表格优先，两者都正常 |

## 已知陷阱

### 1. `__pycache__` 缓存

Python 会缓存编译后的字节码。插件代码更新后，如果 `__pycache__` 未清除，Gateway 加载的仍是旧代码。

**解决**：每次更新后删除 pycache：
```bash
find /opt/data/profiles/llm-wiki/plugins/feishu-card -name "__pycache__" -type d -exec rm -rf {} +
```

### 2. Gateway 进程信号免疫

`s6-supervise` 管理的 Gateway 进程对 SIGTERM、SIGINT、SIGABRT 均不作退出响应。`s6-svc -r/-d/-t` 也无效。唯一可靠重启方式：`kill -9`。

### 3. Post 格式 API 拒绝降级

Post 格式发送时可能被飞书 API 拒绝（`_POST_CONTENT_INVALID_RE` 匹配），自动降级为纯文本。降级后代码块无高亮和复制按钮。

### 4. YAML 字符串陷阱

`hermes config set plugins.enabled '["a","b"]'` 会写入 JSON 字符串而非 YAML 列表：
```yaml
# ❌ 错误
plugins:
  enabled: '["feishu-platform", "feishu-card"]'

# ✅ 正确
plugins:
  enabled:
    - feishu-platform
    - feishu-card
```

## 参考文件

- `references/card-payload-examples.md` — Card 1.0 / CardKit 2.0 JSON 负载示例
- [[queries/飞书代码块渲染对比-验证记录]] — Post vs Card 2.0 验证记录

## 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 插件未加载 | `plugins.enabled` 是字符串而非列表 | 检查 YAML 格式，改为列表 |
| 卡片未出现 | Gateway 未重启或缓存未清 | 清除 pycache + `kill -9` |
| 代码块无复制按钮 | 走了 Card 2.0 路径（含表格） | 这是 CardKit 限制，无法解决 |
| 认证失败 | 飞书 App 权限不足 | 检查 `im:message:send` 权限 |
