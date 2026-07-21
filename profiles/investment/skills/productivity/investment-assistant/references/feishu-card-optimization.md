# Feishu Card 2.0 组件优化分析

基于2026-07-13对飞书开放平台文档的调研，产出以下可用组件和优化方案。

## 官方组件清单

以下组件均经 `lark_oapi` SDK + Hermes adapter 代码验证为飞书官方支持的 Card 2.0 元素：

| tag | 官方支持来源 | 当前使用 | 用途 |
|:----|:-----------|:--------|:----|
| `markdown` | adapter.py 第1047行、1961行 | ✅ | 文字/富文本 |
| `table` | adapter.py 第1050行确认 | ✅ | 原生表格（列定义+数据行） |
| `hr` / `divider` | adapter.py 第757行处理逻辑 | ✅ Phase 1 | 分割线，替代 markdown `---` |
| `column_set` | adapter.py 第1050行支持列表 | ⚠️ 可用但大盘走势弃用 | 多列布局，手机端阅读优化 |
| `button` | adapter.py 第1946、2003行生成按钮 | ✅ Phase 2 | 交互按钮/链接跳转 |
| `note` | adapter.py 第1048行支持列表 | ✅ Phase 1 | 底部注释角标 |
| `action` | adapter.py 第1965行动作容器 | ✅ Phase 2 | 按钮组容器 |
| `img` | lark_oapi SDK 通用元素 | ❌ 未用 | 内嵌图片 |
| `config.wide_screen_mode` | adapter.py 第1954行 | ✅ | 宽屏 |
| `header.template` | adapter.py 第1956行 | ✅ Phase 2 | 卡片颜色（blue/red/green等） |

## 已确认的 msg_type

| msg_type | 用途 | 当前使用 |
|:---------|:-----|:--------|
| `text` | 纯文本 | adapter fallback |
| `post` | 富文本（tag:md） | adapter 默认（**不**渲染表格） |
| `interactive` | 卡片（Card 2.0） | ✅ send_feishu_cards.py 直连API |
| `image` | 图片消息 | adapter 支持 |
| `file` | 文件消息 | adapter 支持 |

## 分阶段实施方法论

每一阶段遵循：**实现 → 推送测试 → 解释预期效果 → 用户确认 → 下一阶段**

### 通知用户的话术模板

推送测试消息前必须说明：
1. **修改了哪些文件** — 如「修改了 sitecustomize.py，新增 _is_hr_line() 等函数」
2. **预期结构变化** — 如「之前 x个元素，现在 x个中包含 N个 hr + M个 note」
3. **预期视觉效果** — 如「hr=灰色分割横线，note=灰色小字脚注」
4. **请求确认** — 「你看飞书上效果对吗？」

---

## Phase 1: hr + note（2026-07-13 已实施 ✅）

### 修改文件

`/opt/data/.feishu-deps/sitecustomize.py` → `_build_card_from_content()`

### 新增函数

- `_is_hr_line(line)` — 检测 `---`, `***`, `___` 行（全由 `-*/_` 组成，>=3个字符）
- `_is_note_line(text)` — 检测脚注/说明行
- `_flush_md_block(elements, md_lines)` — 按空白行拆分子块，逐块判断 note 或 markdown

### _is_note_line 检测规则

| 条件 | 匹配示例 |
|:----|:--------|
| 不含 `**`，方向标注如 `↑=` | `开方向↑=高于昨收, ↓=低于昨收` |
| 含免责词 | `仅供参考，不构成投资建议` |
| 一行内特殊emoji开头+短句（不含📊📋等标题emoji） | `✅ 再平衡检查通过` |

### 预期视觉表现

| 组件 | 飞书上显示样式 |
|:----|:-------------|
| `hr` | 一条细细的灰色分割横线，视觉分隔两个内容块 |
| `note` | 灰色小字，比正文更小更淡，在卡片底部作附属说明 |

### 当前卡片结构变化

**大盘走势卡片：**
```
之前: heading→table→md(开方向↑=...)→md(成交)→heading→table
现在: heading→table→note(开方向↑=...)→md(成交)→heading→table
       ↑ 变为灰色小字脚注
```

**操作评估卡片：**
```
之前: heading→table→heading→table→md(再平衡检查)
现在: heading→table→heading→table→note(再平衡检查)
       ↑ 变为灰色小字脚注
```

---

## Phase 2: column_set(弃用) + button + 颜色方案（2026-07-13 已实施 ✅）

### 修改文件

| 文件 | 改动 |
|:----|:-----|
| `/opt/data/.feishu-deps/sitecustomize.py` | 新增 `_is_quote_table()`、`_build_quote_columns()` 函数(后弃用) |
| `/opt/data/.feishu-deps/sitecustomize.py` | 移除 column_set 特殊处理，大盘走势改回原生table |
| `/opt/data/scripts/send_feishu_cards.py` | 新增 `send_card_with_button()` 函数 |

### 2a: column_set 多列布局 → ❌ 大盘走势弃用

#### 尝试历程

| 版本 | 方案 | 用户反馈 | 结论 |
|:----|:----|:--------|:----|
| v1 | column_set，每行独立markdown元素 | 行对不齐，像散落文本 | ❌ |
| v2 | 每列一个markdown块，用`\n\n`分隔 | 行数不对(左2行vs右3行/条) | ❌ |
| v3 | 每列一个markdown块，每行1行 | 内容不对应(一行塞太多) | ❌ |
| **最终** | **原生 table 组件** | **✅ 有表头、列对齐、数据明确** | ✅ |

#### 结论：大盘走势的6列数据（指数/昨收/今开/收盘/涨跌/开方向）**必须用原生 Feishu table**，不要用 column_set。

```python
# sitecustomize.py _build_card_from_content() 2026-07-13 最终版本：
# 移除 _is_quote_table() 特殊判断，所有表格统一走 _parse_table_block()
# 即：table_json = _parse_table_block(raw_table)  # 不再判断是否quote表
```

#### column_set 的适用场景

column_set 仍然可用，但适合**非表格数据**的多列展示（如 地址+电话+邮箱 的三列联系方式）。对于**结构化表格数据**，原生 table 永远更好。

#### ⚠️ column_set Pitfall：每行独立 markdown 元素 → 行对不齐

**不要**每行一个独立的 `{"tag": "markdown", "content": "..."}` 元素。每个独立的 markdown 块在飞书上会按独立的段落渲染，导致左列的第N行和右列的第N行**视觉上不对齐**，看起来像散开的文本块而不是表格。

✅ **如果要用 column_set：每列只用一个 markdown 元素**，所有行通过 `\n` 或 `\n\n` 放在一个字符串里。

### 2b: button 跳转按钮

#### 新增函数

`send_feishu_cards.py` → `send_card_with_button(title, content, button_text, button_url, template)`

```python
def send_card_with_button(title, content, button_text, button_url, template="blue"):
    """Send markdown card + hr divider + action button with URL link."""
```

#### 输出结构

```json
{
  "header": {"title": "KOL按钮测试", "template": "wathet"},
  "elements": [
    {"tag": "markdown", "content": "KOL分析文本..."},
    {"tag": "hr"},
    {
      "tag": "action",
      "actions": [{
        "tag": "button",
        "text": {"tag": "plain_text", "content": "🔗 查看原文"},
        "type": "default",
        "multi_url": {"url": "https://weibo.com/u/2014433131", ...}
      }]
    }
  ]
}
```

按钮在飞书客户端内打开内置浏览器跳转。

#### 应用场景

- KOL 观点卡片 → "🔗 查看原文" 链接到 KOL 微博主页
- 新闻卡片 → 链接到 RSS 原文
- 数据来源链接等

### 2c: template 颜色方案

`send_feishu_cards.py` 中 `send_card()`/`send_card_with_tables()` 的 `template` 参数统一：

| 卡片类型 | template | 含义 |
|:--------|:---------|:----|
| 指数行情/外盘 | `blue` 🔵 | 中性信息 |
| 板块热度/排行 | `red` 🔴 | 关注/警示 |
| 持仓表现 | `green` 🟢 | 个人资产 |
| 操作建议/评估 | `purple` 🟣 | 决策信息 |
| KOL观点 | `wathet` 🌀 | 第三方参考 |
| 新闻/辅助信息 | `grey` ⚫ | 辅助信息 |

**已在 `send_closing_cards.py` 和 `send_morning_cards.py` 中应用。**

---

## Phase 3: send_structured_card — 非表格结构化卡片（2026-07-14 新增 ✅）

### 动机

`send_card()` 和 `send_card_with_tables()` 只能处理纯 markdown 或 markdown 含表格的场景。对于**需要视觉层次**的内容（KOL 观点、新闻汇总），需要在一个卡片内组合 markdown、divider、note 等元素。

### 新增函数

`send_morning_cards.py` → `send_structured_card(title, sections, template)`

```python
def send_structured_card(title, sections, template="blue"):
    """Send a card with multiple structured elements.
    sections: list of dicts with 'type' ('markdown'|'divider'|'note') and 'content'.
    """
```

### sections 参数格式

```python
sections = [
    {"type": "markdown", "content": "**汇总内容**\n- 点1\n- 点2"},
    {"type": "divider"},           # → <hr> 灰色分隔线
    {"type": "markdown", "content": "📝 详细内容..."},
    {"type": "note", "content": "脚注说明文字"},  # → 灰色小字
]
```

### 输出 JSON 结构

```json
{
  "config": {"wide_screen_mode": true},
  "header": {"title": {"content": "卡片标题", "tag": "plain_text"}, "template": "blue"},
  "elements": [
    {"tag": "markdown", "content": "**汇总内容**..."},
    {"tag": "hr"},
    {"tag": "markdown", "content": "📝 详细内容..."},
    {"tag": "note", "elements": [{"tag": "plain_text", "content": "脚注说明"}]}
  ]
}
```

### 与 send_card 的区别

| 特性 | send_card | send_structured_card |
|:----|:---------|:-------------------|
| 元素数 | 固定 1 个 markdown | 任意多个元素组合 |
| divider 支持 | ❌ | ✅ `{"type": "divider"}` |
| note 支持 | ❌ | ✅ `{"type": "note"}` |
| 大卡片回退 | 截断 content 到 4000 字 | 截断 markdown 元素到 3000 字 |
| ⚠️ token 导入 | 直接引用模块变量 | **必须用模块引用**（见 pitfall） |

### ⚠️ Python import pitfall：模块变量 vs 直接导入

`send_structured_card` 使用 `sfc._token`、`sfc._chat_id`，**不是** `from send_feishu_cards import _token`。

**原因**：`from module import variable` 在 Python 中是**值拷贝**（导入时的值）。当 `send_feishu_cards` 的其他函数（如 `send_card_with_tables`）在运行时修改了模块的 `_token` 变量，通过 `from ... import` 导入的引用**看不到修改**，仍然持有旧值（`None`）。

**正确做法**：
```python
# ✅ 正确：模块引用，始终看到最新值
import send_feishu_cards as sfc
sfc._ensure_auth()
token = sfc._token

# ❌ 错误：值拷贝，永远 None
from send_feishu_cards import _ensure_auth, _token
_ensure_auth()  # 设置了 send_feishu_cards._token
_token          # 仍然是 None ！
```

### 应用场景

| 卡片类型 | 结构 | 示例 |
|:--------|:----|:----|
| KOL共识 | markdown + note | 赛道共识 + "基于关键词分析" |
| KOL观点 | markdown + divider + markdown(前5条) + note | 汇总段 + 分割线 + 明细 + 脚注 |
| RSS新闻 | markdown + note | 新闻列表 + "英文标题已自动翻译" |

---

## 官方文档可访问性

飞书开放平台文档URL格式：
- 飞书(CN): `https://open.feishu.cn/document/<path>.md` -> AI友好的纯Markdown版本（需要客户端渲染生效）
- Lark(国际): `https://open.larksuite.com/document/<path>.md` -> 同上
- 文档页面HTML中标记 `<link rel="alternate" type="text/markdown" href="...md" tip="pure markdown version, better for ai" />`
- 文档系统为 React SPA，需 JavaScript 渲染；直接 curl `*.md` 返回 "This document is not found"
- CardKit 可视化编辑器需登录飞书账号后访问 `https://open.feishu.cn/cardkit`

## 验证方法

所有组件通过飞书 Open API `/open-apis/im/v1/messages?receive_id_type=chat_id` 发送 `msg_type=interactive` 验证。

错误码可在 [API Explorer](https://open.feishu.cn/api-explorer) 查证。

自动化验证：构建card JSON后检查 `elements` 中 `tag` 类型的种类和顺序是否符合预期。
