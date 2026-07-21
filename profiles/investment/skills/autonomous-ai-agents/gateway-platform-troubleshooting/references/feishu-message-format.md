# Feishu 消息格式与 Markdown 渲染

## 飞书消息类型

| 类型 | msg_type | 表格支持 | Markdown | 适用场景 |
|:----|:--------:|:--------:|:--------:|:---------|
| 纯文本 | `text` | ❌ | 仅 `<b>` `<i>` `<u>` `<s>` 标签 | 短文本、通知 |
| 富文本 | `post` | ✅ GFM 语法 | ✅ tag:md 原生渲染 | 财经报表、结构化消息 |
| 卡片 | `interactive` | ✅ | ✅ 需 JSON 结构 | 交互式、高美观需求 |

**关键发现：** 飞书富文本 `post` + `tag:md` **原生支持 GFM 表格**（`| col1 | col2 |\n| --- | --- |`），无需特殊处理。

## Hermes 适配器的表格 Bug

### 问题根因

`/opt/hermes/plugins/platforms/feishu/adapter.py` 中的 `_build_outbound_payload` 方法（4470行）：

```python
def _build_outbound_payload(self, content: str) -> tuple[str, str]:
    # 这段注释是错的：飞书 tag:md 实际支持表格
    if _MARKDOWN_TABLE_RE.search(content):
        return "text", ...  # ❌ 强制降级为纯文本
    if _MARKDOWN_HINT_RE.search(content):
        return "post", ...  # ✅ 走富文本
    return "text", ...
```

### 修复方案

该文件是 root 只读的（容器部署），通过猴子补丁修复：

**补丁位置：** `/opt/data/.feishu-deps/lark_oapi/ws/__init__.py`

**选择理由：** `lark_oapi.ws` 是适配器**确实导入且可写**的模块。`lark_oapi.channel` 虽可写但从未被导入，放那是无效的。

**补丁逻辑：** 当适配器导入 `lark_oapi.ws` 时触发（此时 `FeishuAdapter` 类已定义），替换 `_build_outbound_payload` 方法：

```python
# lark_oapi.ws.__init__.py 末尾追加
try:
    import sys as _sys
    _mod = _sys.modules.get("plugins.platforms.feishu.adapter")
    if _mod is not None:
        _adapter = _mod
        _hint = _adapter._MARKDOWN_HINT_RE
        _table = _adapter._MARKDOWN_TABLE_RE
        _build_post = _adapter._build_markdown_post_payload

        def _patched(self, content: str):
            if _hint.search(content) or _table.search(content):
                return "post", _build_post(content)
            import json
            return "text", json.dumps({"text": content}, ensure_ascii=False)

        _adapter.FeishuAdapter._build_outbound_payload = _patched
except Exception:
    pass
```

### 飞书运行时 Python 路径

| 路径 | 权限 | 用途 |
|:----|:----:|:-----|
| `/opt/hermes/` | root:root 只读 | Hermes 源代码（容器内置） |
| `/opt/data/.feishu-deps/` | hermes 可写 | 额外 Python 包（uv pip --target） |
| `/opt/data/feishu-venv/` | hermes 可写 | 备用 venv，部分 lark_oapi 组件 |
| `/opt/data/.feishu-deps` 在 sys.path 首位 | — | 运行时优先加载 |

### 调试方法

```bash
# 检查补丁是否加载
PYTHONPATH="" /opt/hermes/.venv/bin/python3 -c "
from plugins.platforms.feishu.adapter import FeishuAdapter
import types
fn = FeishuAdapter._build_outbound_payload
print(f'方法已替换: {fn.__name__ != \"_build_outbound_payload\"}')
if fn.__name__ != '_build_outbound_payload':
    print(f'当前方法: {fn.__name__}')
"

# 测试表格路由
PYTHONPATH="" /opt/hermes/.venv/bin/python3 -c "
from plugins.platforms.feishu.adapter import FeishuAdapter
test = '**表格**\n| a | b |\n| --- | --- |'
t, p = FeishuAdapter._build_outbound_payload(FeishuAdapter, test)
print(f'msg_type={t}')  # 应为 post
"

# 发送测试消息
/opt/hermes/.venv/bin/hermes send -t "feishu:CHAT_ID" -s "测试标题" "| a | b |\n| --- | --- |"
```

### 注意事项

- `hermes send` 走独立发送通道，同样受 `_build_outbound_payload` 影响
- 若 post 消息被飞书 API 拒绝（`content format of the post type is incorrect`），适配器会自动降级为纯文本（`send` 方法 1862-1871 行）
- 表格需要 `\n\n` 前后分隔（GFM 标准要求）
- 修改后需重启网关：`kill PID && sleep 5`（s6 自动重启）
