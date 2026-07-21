# Card 2.0 消息负载示例

该文件记录 Feishu Card 2.0 插件生成的消息负载 JSON，供开发和调试参考。

## 1. 纯文本 → Card 1.0（无表格时）

```json
{
  "config": {
    "wide_screen_mode": true
  },
  "header": {
    "title": {"tag": "plain_text", "content": "ℹ️ 信息"},
    "template": "blue"
  },
  "elements": [
    {"tag": "markdown", "content": "这是普通文本消息"}
  ]
}
```

- `msg_type`: "interactive"
- `content`: 上述 JSON 序列化字符串

## 2. 含表格 → CardKit 2.0

```json
{
  "schema": "2.0",
  "header": {
    "title": {"tag": "plain_text", "content": "📊 数据"},
    "template": "turquoise"
  },
  "body": {
    "elements": [
      {
        "tag": "table",
        "page_size": 100,
        "columns": [
          {"name": "col_0", "display_name": "项目", "data_type": "text", "horizontal_align": "left"},
          {"name": "col_1", "display_name": "数值", "data_type": "text", "horizontal_align": "left"}
        ],
        "rows": [
          {"col_0": "CPU", "col_1": "45%"},
          {"col_0": "内存", "col_1": "72%"}
        ]
      }
    ]
  }
}
```

- `msg_type`: "interactive"
- `schema: "2.0"` 是关键——缺少此项则飞书不识别为 CardKit
- `header` 在顶层，不在 `config` 内（与 Card 1.0 不同）

## 3. 混排（Markdown + 表格）

```json
{
  "schema": "2.0",
  "header": {
    "title": {"tag": "plain_text", "content": "## 标题"},
    "template": "blue"
  },
  "body": {
    "elements": [
      {"tag": "markdown", "content": "## 标题\n\n说明文字"},
      {
        "tag": "table",
        "page_size": 100,
        "columns": [
          {"name": "col_0", "display_name": "A", "data_type": "text", "horizontal_align": "left"}
        ],
        "rows": [
          {"col_0": "1"}
        ]
      },
      {"tag": "markdown", "content": "结尾文字"}
    ]
  }
}
```

- `body.elements` 中 `markdown` 与 `table` 交错排列，按原文顺序
- `markdown` 元素使用普通 Markdown 渲染（包括标题、列表、代码块）
- `table` 元素使用飞书原生表格组件

## 4. 动态标题匹配示例

| 内容片段 | 匹配规则 | 标题 | 颜色 |
|---------|---------|------|------|
| `Error:` 或 `失败` | error 规则 | ⚠️ 错误 | red |
| `Warning:` 或 `⚠️` | warning 规则 | ⚠️ 警告 | orange |
| Markdown 表格 | table 规则 | 📊 数据 | turquoise |
| `\`\`\`python` | code block 规则 | 🛠 技术 | indigo |
| `- 步骤一` 或 `1. 步骤` | list 规则 | 📋 清单 | green |
| `A vs B` 或 `对比` | comparison 规则 | ⚖️ 对比 | purple |
| `**加粗**` | bold 规则 | ℹ️ 信息 | grey |
| `## 用户标题` | heading 提取 | 标题内容 | 后续规则定 |
