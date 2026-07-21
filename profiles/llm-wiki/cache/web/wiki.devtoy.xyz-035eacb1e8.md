[跳转至](https://wiki.devtoy.xyz/queries/%E9%A3%9E%E4%B9%A6%E4%BB%A3%E7%A0%81%E5%9D%97%E6%B8%B2%E6%9F%93%E5%AF%B9%E6%AF%94-%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/#post-vs-card-20)

# 飞书消息代码块渲染对比 — Post vs Card 2.0 [¶](https://wiki.devtoy.xyz/queries/%E9%A3%9E%E4%B9%A6%E4%BB%A3%E7%A0%81%E5%9D%97%E6%B8%B2%E6%9F%93%E5%AF%B9%E6%AF%94-%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/\#post-vs-card-20 "Permanent link")

## 背景 [¶](https://wiki.devtoy.xyz/queries/%E9%A3%9E%E4%B9%A6%E4%BB%A3%E7%A0%81%E5%9D%97%E6%B8%B2%E6%9F%93%E5%AF%B9%E6%AF%94-%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/\#_1 "Permanent link")

Hermes Feishu 适配器的消息渲染有两个选择：`post` 格式（`tag:"md）和 Card 2.0 格式（`tag:"markdown 在 Card JSON 2.0 body 中）。需要确定哪种格式对代码块渲染效果更好。

## 测试方法 [¶](https://wiki.devtoy.xyz/queries/%E9%A3%9E%E4%B9%A6%E4%BB%A3%E7%A0%81%E5%9D%97%E6%B8%B2%E6%9F%93%E5%AF%B9%E6%AF%94-%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/\#_2 "Permanent link")

1. 修改 `CardFeishuAdapter._build_outbound_payload()`，暂时切换至纯 Post 格式
2. 发送带多行代码块的消息
3. 观察复制按钮、展开行为、语法高亮
4. 恢复 Card 2.0 格式，发送同一条消息对比

## 对比结果 [¶](https://wiki.devtoy.xyz/queries/%E9%A3%9E%E4%B9%A6%E4%BB%A3%E7%A0%81%E5%9D%97%E6%B8%B2%E6%9F%93%E5%AF%B9%E6%AF%94-%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/\#_3 "Permanent link")

### Post 格式（\`tag:"md） [¶](https://wiki.devtoy.xyz/queries/%E9%A3%9E%E4%B9%A6%E4%BB%A3%E7%A0%81%E5%9D%97%E6%B8%B2%E6%9F%93%E5%AF%B9%E6%AF%94-%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/\#post-tagmd "Permanent link")

| 能力 | 结果 |
| --- | --- |
| 代码块复制按钮 | ✅ **有**（右上角 📋 图标） |
| 完整展开 | ✅ 全部行直接可见，无需滚动 |
| 语法高亮 | ✅ 支持 |
| 表格渲染 | ❌ 不渲染，降级为纯文本 |
| 流式编辑兼容性 | ❌ 首次 chunk 为 `text`，后续改为 `post` 导致飞书拒收 |

### Card 2.0（\`tag:"markdown 在 Card JSON 2.0 body 内） [¶](https://wiki.devtoy.xyz/queries/%E9%A3%9E%E4%B9%A6%E4%BB%A3%E7%A0%81%E5%9D%97%E6%B8%B2%E6%9F%93%E5%AF%B9%E6%AF%94-%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/\#card-20tagmarkdown-card-json-20-body "Permanent link")

| 能力 | 结果 |
| --- | --- |
| 代码块复制按钮 | ❌ 无（CardKit 纯展示组件无交互） |
| 完整展开 | ⚠️ 固定高度，需滑动查看全部行 |
| 语法高亮 | ✅ 支持 |
| 表格渲染 | ✅ 完整 GFM 表格支持 |
| 流式编辑兼容性 | ✅ 始终 `interactive` 类型，一致 |

**关键发现**：飞书 API 无论通过 `post` 还是 `card` 格式，都无法触发飞书客户端的原生代码块组件（有复制按钮的那个）。复制按钮只在用户手动通过聊天输入框发送代码块时出现。

## 根因分析 [¶](https://wiki.devtoy.xyz/queries/%E9%A3%9E%E4%B9%A6%E4%BB%A3%E7%A0%81%E5%9D%97%E6%B8%B2%E6%9F%93%E5%AF%B9%E6%AF%94-%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/\#_4 "Permanent link")

飞书有两个 Markdown 渲染器（来自 [concepts/vibe-trading/项目总览](https://wiki.devtoy.xyz/concepts/vibe-trading/%E9%A1%B9%E7%9B%AE%E6%80%BB%E8%A7%88/) 扩展）：

| 容器 | 元素 | 能力 |
| --- | --- | --- |
| `post` 消息 | \`tag:"md | 仅链接 \+ 部分粗体（官方文档描述） |
| Card 2.0 body | \`tag:"markdown | 完整 CommonMark（代码块、表格、列表、标题） |

但实际测试发现 `post` \+ \`tag:"md 的代码块渲染 **比官方描述更好**——有语法高亮、完整展开、甚至有复制按钮。而 Card 2.0 的代码块渲染虽然正确，但没有复制按钮。

## 最终策略：混合方案 [¶](https://wiki.devtoy.xyz/queries/%E9%A3%9E%E4%B9%A6%E4%BB%A3%E7%A0%81%E5%9D%97%E6%B8%B2%E6%9F%93%E5%AF%B9%E6%AF%94-%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/\#_5 "Permanent link")

```
def _build_outbound_payload(self, content):
    if _MARKDOWN_TABLE_RE.search(content):
        # 含表格 → Card 2.0（表格必须用卡片渲染）
        return self._build_card_with_tables(content, title, template)
    # 不含表格 → Post 格式（代码块有复制按钮 + 完整展开）
    return super()._build_outbound_payload(content)
```

### 路由规则 [¶](https://wiki.devtoy.xyz/queries/%E9%A3%9E%E4%B9%A6%E4%BB%A3%E7%A0%81%E5%9D%97%E6%B8%B2%E6%9F%93%E5%AF%B9%E6%AF%94-%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/\#_6 "Permanent link")

```
消息内容
├── 含表格 ──→ Card 2.0（动态彩色标题 + 原生表格组件）
└── 不含表格 ──→ Post 格式（代码块有复制按钮 + 完整展开）
```

### 验证结果 [¶](https://wiki.devtoy.xyz/queries/%E9%A3%9E%E4%B9%A6%E4%BB%A3%E7%A0%81%E5%9D%97%E6%B8%B2%E6%9F%93%E5%AF%B9%E6%AF%94-%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/\#_7 "Permanent link")

| 测试 | 内容 | 路由 | 结果 |
| --- | --- | --- | --- |
| Test 1 | 纯代码块 | → Post | ✅ 有复制按钮、完整展开、语法高亮 |
| Test 2 | 纯表格 | → Card 2.0 | ✅ 表格正常渲染、卡片蓝色标题 |
| Test 3 | 代码块+表格混合 | → Card 2.0 | ✅ 表格优先，两者都正常 |

## 已知限制 [¶](https://wiki.devtoy.xyz/queries/%E9%A3%9E%E4%B9%A6%E4%BB%A3%E7%A0%81%E5%9D%97%E6%B8%B2%E6%9F%93%E5%AF%B9%E6%AF%94-%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/\#_8 "Permanent link")

- Post 格式的 `tag:"md 含代码块的消息可能被飞书 API 拒绝（`\_POST\_CONTENT\_INVALID\_RE\`），导致降级为纯文本
- `__pycache__` 缓存会导致插件代码更新后未生效，需清理后重启
- Gateway 进程（s6 管理）对 SIGTERM/SIGINT 免疫，需 `kill -9` 强制重启

* * *

## 📊 图谱关联 [¶](https://wiki.devtoy.xyz/queries/%E9%A3%9E%E4%B9%A6%E4%BB%A3%E7%A0%81%E5%9D%97%E6%B8%B2%E6%9F%93%E5%AF%B9%E6%AF%94-%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95/\#_9 "Permanent link")

由 Graphify 知识图谱自动计算的相关页面：

- [首页](https://wiki.devtoy.xyz/)
- [查询归档](https://wiki.devtoy.xyz/)

回到页面顶部