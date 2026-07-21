# Source File Index Pages for LLM Wiki

为 LLM Wiki 的 `raw/` 和 `sources/` 目录创建结构化索引页，使原始材料在 MkDocs 前端中可浏览且可导航到处理后的概念页面。

## Overview

`raw/` (原始文档) 和 `sources/` (外部来源,如YouTube) 这两个目录通常不放 在 nav 中，但创建一个结构化的 `index.md` 能让这些资料在前端被发现。关键设计：**用表格将原始文件映射到对应的概念页面**，让读者知道"这个原始文档产生了哪些 wiki 页面"。

## 目录索引通用要求

MkDocs 要求每个子目录必须有 `index.md` 才能渲染该路径。详见主 skill 的"目录索引要求"部分。

## raw/index.md 模式

### 结构

```markdown
---
title: "📄 原始文档"
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: index
tags: [raw, sources]
---

# 📄 原始文档

> 一句话描述此目录用途

## 目录结构

用代码块展示目录树，让读者一目了然：

```text
raw/
├── articles/        ← 网页文章源文件（待导入）
├── papers/
│   └── topic-name/
│       ├── doc1-raw.md
│       └── core-standards/
│           ├── doc2-raw.md
│           └── ocr/
│               └── doc3-ocr.md
└── transcripts/     ← 音视频转录（待导入）
```

### 文件→概念映射表

每个子类目用一个表格，将原始文件映射到对应的概念页面：

| 原始文件 | 对应概念页面 |
|---------|-------------|
| 基本要求-raw.md | [[concepts/topic/doc-name]] |
| 测评要求-raw.md | [[concepts/topic/doc-name]] |

**关键**：使用 `[[wikilinks]]` 格式，obsidian-bridge/roamlinks 插件会将其转为可点击链接。

### 关联页面

```markdown
## 关联页面

- [[entities/entity-a]] — 描述
- [[entities/entity-b]] — 描述
- [[sources/youtube/]] — 其他源文件目录
```

## sources/youtube/index.md 模式

```markdown
---
title: "📁 YouTube 源文件"
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: index
tags: [youtube, sources]
---

# 📁 YouTube 源文件

此目录存放从 YouTube 视频/播放列表导入的源文件。

## 投喂工作流

1. **提取内容**：使用 `web_extract` 工具获取 YouTube 页面内容
2. **生成 Wiki 页面**：将提取内容传入投喂脚本
3. **更新图谱**：执行 trigger-rebuild.sh

## 已投喂视频

| 视频 | 时长 | 上传者 | 日期 |
|------|------|--------|------|
| [标题](video-page.md) | 09:50 | 作者 | YYYY-MM-DD |
```

注意：视频页面用标准 Markdown 链接 `[title](filename.md)`，因为这不是概念/实体目录，而是源文件目录。

## 更新 nav

在 `mkdocs.yml` 中添加一个新的顶级 nav 条目：

```yaml
nav:
  # ... 现有条目 ...
  - 📁 源文件:
    - 📄 原始文档: raw/index.md
    - 🎥 YouTube 源文件: sources/youtube/index.md
  # ... 后续条目 ...
```

### 放置原则

- 在"❓ 查询归档"之后、"搭建方案"之前——源文件属于参考材料，优先级介于内容和基础设施之间
- 使用 emoji 前缀保持视觉一致性：`📁` 文件夹，`📄` 文档，`🎥` 视频
- 缩进：顶层 2 空格，子项 4 空格

## Session-Specific Details from wiki.devtoy.xyz

### 原始文档结构

`raw/index.md` 为 wiki.devtoy.xyz 创建时的内容：

- 三个映射表：核心标准（4项）、OCR扫描件（3项）、数据安全专项（2项）
- 每个表将原始文件路径名映射到 `[[concepts/网络安全等级保护/...]]` wikilink
- 底部"关联页面"链接到 4 个 entities 页面和 sources/youtube/

### 目录结构展示

```text
raw/
├── articles/        ← 网页文章源文件（待导入）
├── assets/          ← 媒体资源文件
├── papers/          ← PDF/学术论文源文件
│   └── 网络安全等级保护/
│       ├── 数据安全基本要求-raw.md
│       ├── 数据安全测评要求-raw.md
│       ├── 测评机构能力要求-raw.md
│       └── 核心标准/
│           ├── 基本要求-raw.md
│           ├── 测评要求-raw.md
│           ├── 测评过程指南-raw.md
│           ├── 认证技术规范-raw.md
│           └── ocr/
│               ├── 定级指南-ocr.md
│               ├── 实施指南-ocr.md
│               └── 测评机构能力要求2018-ocr.md
└── transcripts/     ← 音视频转录文本（待导入）
```

### 陷阱

- **`[[wikilinks]]` 在表格中使用时**：确保插件（obsidian-bridge 或 roamlinks）已安装，否则渲染为纯文本
- **nav 缩进**：mkdocs.yml 的缩进必须是 2 空格层级（顶层 2 格，子项 4 格），不能用 Tab
- **文件路径不存在**：如果引用了 `sources/youtube/index.md` 但文件不存在，build/serve 会报 WARNING，但仍可启动
- **重启生效**：修改 mkdocs.yml 后必须重启容器（docker restart llm-wiki），MkDocs serve 模式不会自动检测 yml 变更
