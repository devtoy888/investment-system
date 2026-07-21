# Feishu 消息渲染 — 混合策略 (v2)

> 会话验证：2026-07-14 | 相关 skill：`feishu-card-plugin` (v2.0.0) | 验证记录：[[queries/飞书代码块渲染对比-验证记录]]

## 背景

Hermes 内置的 Feishu 适配器用 `post` + `tag:"md"` 渲染 Markdown，但该渲染器只支持链接和部分粗体。需要用户插件覆盖内置适配器，启用更好的渲染方案。

## 核心发现：飞书有三个消息格式

| 格式 | 消息类型 | 代码块复制按钮 | 代码块完整展开 | 表格渲染 | 卡片标题 |
|:---|---:|:---:|:---:|:---:|:---:|
| 纯文本 `text` | `msg_type=text` | ❌ | ❌ | ❌ | ❌ |
| Post `tag:"md"` | `msg_type=post` | ✅ 有 | ✅ 全部行可见 | ❌ 不渲染 | ❌ |
| Card 2.0 `tag:"markdown"` | `msg_type=interactive` | ❌ 无 | ⚠️ 需滑动 | ✅ GFM | ✅ 彩色动态 |

**关键**：飞书 API 无法触发客户端原生代码块组件（右上角复制按钮）。该按钮仅出现在用户手动通过聊天框发送的代码块消息中。

## 混合策略（v2 方案）

代码块有复制按钮 → Post 格式；表格必须渲染 → Card 2.0。两者不可兼得，按内容动态选择：

```
消息内容
├── 含表格 ──→ Card 2.0（动态彩色标题 + 原生表格组件）
└── 不含表格 ──→ Post 格式（代码块有复制按钮 + 完整展开）
```

## 插件架构变化（v1 → v2）

### v1（已废弃）

全部走 Card 2.0：`"schema": "2.0"` + `"body": {"elements": [...]}`。

**问题**：
- 代码块无复制按钮
- 表格中的 `native table` 组件不支持列对齐（API 返回 ErrCode 200621）
- 非表格内容也走卡片，浪费

### v2（当前）

```python
def _build_outbound_payload(self, content: str) -> tuple[str, str]:
    if 含表格:
        return Card 2.0 (native table + dynamic header)
    # 不含表格 → 父类的 post/text 格式
    return super()._build_outbound_payload(content)
```

## 动态卡片标题（仅 Card 2.0 路径）

`_detect_header_style(content)` 按优先级：

| 优先级 | 内容特征 | 标题 | 颜色 |
|--------|---------|------|:----:|
| 1 | 首个 `#`/`##`/`###` 标题 | 标题内容 | 后续规则定 |
| 2 | error/fail/exception/❌ | ⚠️ 错误 | `red` |
| 3 | warning/⚠️ | ⚠️ 警告 | `orange` |
| 4 | Markdown 表格 | 📊 数据 | `turquoise` |
| 5 | ``` 代码块 | 🛠 技术 | `indigo` |
| 6 | 编号/无序列表 | 📋 清单 | `green` |
| 7 | vs/对比/比较 | ⚖️ 对比 | `purple` |
| 8 | **加粗** | ℹ️ 信息 | `grey` |
| 9 | 其他 | ℹ️ 信息 | `blue` |

## Card JSON 2.0 结构（必须 `"schema": "2.0"`）

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
        "columns": [{"name": "col_0", "display_name": "列名", "data_type": "text", "horizontal_align": "left"}],
        "rows": [{"col_0": "值"}]
      }
    ]
  }
}
```

⚠️ `"schema": "2.0"` 不可省略，否则 Card 1.0 的 `tag:"markdown"` 只支持 Markdown 子集，**代码块会被截断为前 ~2 行**。

## 当前完整插件代码

见 skill [`feishu-card-plugin` v2.0.0](skill:devops/feishu-card-plugin)。

## 已知陷阱

### 1. `__pycache__` 缓存

Python 会缓存编译字节码。插件代码更新后，如果 `__pycache__` 未清除，Gateway 加载的仍是旧代码。

**解决**：每次更新后：
```bash
find /opt/data/profiles/llm-wiki/plugins/feishu-card -name "__pycache__" -type d -exec rm -rf {} +
```

### 2. Gateway 进程信号免疫

`s6-supervise` 管理的 Gateway 进程对 SIGTERM、SIGINT、SIGABRT 均不作退出响应。`s6-svc -r/-d/-t` 无效。

**唯一可靠重启**：
```bash
ps aux | grep "llm-wiki.*gateway" | grep -v grep | awk '{print $2}' | xargs kill -9
# s6 自动重启
```

### 3. Post 格式 API 拒绝降级

Post 格式发送时可能被飞书 API 拒绝（`_POST_CONTENT_INVALID_RE` 匹配），父类自动降级为纯文本。降级后代码块无高亮和复制按钮。

### 4. 原生表格组件不支持对齐

CardKit 2.0 原生 `tag:"table"` 不接受 `horizontal_align` 参数（API 返回 ErrCode 200621）。**改用 `tag:"markdown"` 中嵌入 GFM 表格可实现对齐**。

### 5. YAML 字符串 vs 列表

```yaml
# ❌ 错误 — 字符串
plugins:
  enabled: '["feishu-platform", "feishu-card"]'

# ✅ 正确 — 列表
plugins:
  enabled:
    - feishu-platform
    - feishu-card
```

## 验证方法

| 测试 | 内容 | 预期路由 | 检查点 |
|:---:|:---|:---:|:---|
| 1 | 纯多行代码块 | → Post | 有复制按钮、完整展开、语法高亮 |
| 2 | 纯 Markdown 表格 | → Card 2.0 | 表格渲染正常、有彩色卡片标题 |
| 3 | 代码块 + 表格混合 | → Card 2.0 | 表格优先，两者都正常 |
