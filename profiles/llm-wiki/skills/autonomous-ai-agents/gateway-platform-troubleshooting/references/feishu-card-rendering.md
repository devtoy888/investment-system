# Feishu Card 2.0 消息渲染 — 修复指南

## 问题

Feishu 适配器默认使用 `post` 消息格式（`msg_type=post`）渲染 Markdown 回复。这个格式使用 `tag:"md"` 元素，**只支持极简的 Markdown 子集**（链接 + 部分粗体），不支持：

- 表格（→ 降级为纯文本，行 4474-4476）
- 代码块（→ 截断为约 2 行）
- 列表、标题、引用块（→ 渲染残缺）
- 流式回复的首块与编辑消息类型不一致（首块 `text`，编辑变 `post`）

## 根因：两个 Markdown 渲染器

| 容器 | 标签 | 能力 | 当前适配器 |
|------|------|------|:---------:|
| `post` 消息 | `tag:"md"` | 仅链接 + 部分粗体 | **✅ 当前在用** |
| **Card 2.0** (`interactive`) | **`tag:"markdown"`** | **完整 CommonMark（表格/代码块/列表/标题/引用）** | ❌ 仅审批卡片使用 |

上游 issue: [NousResearch/hermes-agent#46470](https://github.com/NousResearch/hermes-agent/issues/46470)

## 代码位置

**适配器文件**: `/opt/hermes/plugins/platforms/feishu/adapter.py`

### 需要修改的方法

#### 1. `_build_outbound_payload()` (行 4470)

```python
def _build_outbound_payload(self, content: str) -> tuple[str, str]:
    # 当前：检测到表格 → 降级为纯文本
    if _MARKDOWN_TABLE_RE.search(content):
        text_payload = {"text": content}
        return "text", json.dumps(text_payload, ensure_ascii=False)
    # 有 Markdown → 发 post（残缺渲染）
    if _MARKDOWN_HINT_RE.search(content):
        return "post", _build_markdown_post_payload(content)
    # 否则纯文本
    text_payload = {"text": content}
    return "text", json.dumps(text_payload, ensure_ascii=False)
```

**目标: 全部改用 Card 2.0**:

```python
def _build_outbound_payload(self, content: str) -> tuple[str, str]:
    return "interactive", _build_markdown_card_payload(content)
```

#### 2. 新增 `_build_markdown_card_payload()` 函数

参考已有审批卡片（行 1955-1974）的结构，构造 Card 2.0 JSON：

```python
def _build_markdown_card_payload(content: str) -> str:
    """Build a Feishu Card 2.0 payload with full CommonMark markdown support."""
    card = {
        "config": {"wide_screen_mode": True},
        "elements": [
            {"tag": "markdown", "content": content},
        ],
    }
    return json.dumps(card, ensure_ascii=False)
```

### 权限要求

发送 `interactive` 消息只需 `im:message:send` 权限——bot 本身已经有了（能发消息）。不需要额外权限。审批卡片（`send_exec_approval`、`send_update_prompt`）已经在用 Card 2.0，证明权限无问题。

### 影响范围

- 所有通过 `_send_text()` 路径发出的消息
- 流式回复：适配器会流式编辑 `msg_type=interactive` 的卡片内容
- 不影响：文件/图片/审批卡片（各自有独立发送路径）

### 上游 PR 参考

- [#6015](https://github.com/NousResearch/hermes-agent/pull/6015) — 第一版尝试（Cygra, Apr 8），将 Markdown 回复从 `post` 改为 Card 2.0，**仍处于 Open 状态**
- [#46470](https://github.com/NousResearch/hermes-agent/issues/46470) — 最新分析（wait4xx, 1mo ago），包含根因表格和完整方案

## 确认当前版本是否已修复

```bash
# 查看版本
/opt/hermes/bin/hermes --version

# 检查适配器代码是否已使用 Card 2.0
grep -n 'msg_type.*interactive' /opt/hermes/plugins/platforms/feishu/adapter.py

# 检查 _build_outbound_payload 的实现
sed -n '4470,4481p' /opt/hermes/plugins/platforms/feishu/adapter.py
# 如果返回 "post" 或 "text" 而不是 "interactive"，则尚未修复
```

## 手动打补丁方法

由于这涉及修改适配器源码，**不是配置变更**，当前版本 Hermes 没有开关可以切换。手动打补丁：

```bash
# 备份原始文件
cp /opt/hermes/plugins/platforms/feishu/adapter.py /opt/hermes/plugins/platforms/feishu/adapter.py.bak

# 方法 A：修改 _build_outbound_payload + 新增函数
```

补丁代码新增在 `_build_markdown_post_payload()` 函数附近（约行 552），修改 `_build_outbound_payload()`（行 4470）。

**注意**: 下次 `hermes update` 会覆盖修改，需要重新打补丁。
