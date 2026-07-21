# LLM Wiki 前端修复核查清单

当用户反馈 wiki 前端有问题（404、链接不可点击、[[wikilinks]] 纯文本等），按此清单逐一排查修复。

## 第一步：问题诊断

### 检查项 1 — 子目录 404

```bash
curl -s -o /dev/null -w "%{http_code}" https://wiki.devtoy.xyz/entities/
curl -s -o /dev/null -w "%{http_code}" https://wiki.devtoy.xyz/concepts/
curl -s -o /dev/null -w "%{http_code}" https://wiki.devtoy.xyz/comparisons/
curl -s -o /dev/null -w "%{http_code}" https://wiki.devtoy.xyz/queries/
```

全部应为 200。任何 404 = 缺少 index.md。

### 检查项 2 — [[wikilinks]] 是否可点击

在浏览器打开任意概念页（如 `/concepts/vibe-trading/项目总览/`），看底部交叉引用区域。若显示纯文本 `[[concepts/vibe-trading/技术架构]]` 而非蓝色链接 = wikilinks 插件缺失。

```bash
docker exec llm-wiki pip list 2>/dev/null | grep -iE "roamlinks|obsidian-bridge"
```

### 检查项 3 — 裸 URL 是否自动链接

打开 setup-guide 页，看"相关文档"表格中的 `https://...` 是否可点击。若不可点击 = magiclink 扩展未启用。

```bash
grep -q "magiclink" /llm-wiki/mkdocs.yml && echo "已配置" || echo "未配置"
```

### 检查项 4 — 原始来源文档不可见

```bash
[ -f /llm-wiki/docs/raw/index.md ] && echo "有 index" || echo "缺少 raw/index.md"
```

## 第二步：修复

### 修复 404 — 创建 index.md

需要 index.md 的目录：

| 目录 | 必须性 |
|------|--------|
| `entities/` | nav 或首页链接引用时必需 |
| `concepts/` | nav 引用 `concepts/` 时必需 |
| `concepts/*/` | nav 引用子目录时必需 |
| `comparisons/` | nav 引用时必需 |
| `queries/` | nav 引用时必需 |
| `raw/` | 如需从网站浏览原始文档 |

每个 index.md 格式：

```markdown
---
title: 目录索引
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: index
tags: [index]
---

# 目录名

- [页面标题](页面文件名.md)
```

### 修复 wikilinks — 安装 roamlinks 插件

```bash
# 选项 1（推荐，持久）：改 compose command + entrypoint
# llm-wiki:
#   image: squidfunk/mkdocs-material:latest
#   entrypoint: ["/sbin/tini", "--", "sh", "-c"]
#   command: ["pip install -q mkdocs-roamlinks-plugin && exec mkdocs serve --dev-addr 0.0.0.0:8456 --dirty"]
#
# ⚠️ command 必须用 YAML JSON 列表格式，字符串会被拆分导致失败

# 选项 2（一次安装，容器重建后丢失）：
docker exec llm-wiki pip install mkdocs-roamlinks-plugin

# 选项 3（自定义镜像，彻底持久）：
# Dockerfile: FROM squidfunk/mkdocs-material:latest
#             RUN pip install --no-cache-dir mkdocs-roamlinks-plugin
# 构建: docker build -t llm-wiki:latest ~/llm-wiki/
```

然后在 mkdocs.yml plugins 中添加：

```yaml
plugins:
  - search
  - roamlinks
```

### 修复 nav 目录引用警告

mkdocs.yml 的 nav 中引用目录路径（如 `concepts/网络安全等级保护/`）会产生 WARNING。改为引用 index.md：

```yaml
nav:
  - 概念:
    - 等保 2.0: concepts/网络安全等级保护/index.md    # 不是 concepts/网络安全等级保护/
    - Vibe-Trading: concepts/vibe-trading/index.md
  - 对比分析: comparisons/index.md
  - 查询归档: queries/index.md
```

### 修复 index.md 相对目录链接 INFO

首页 `[entities](entities/)` 这类链接产生 INFO，改为 `[entities](entities/index.md)`。

### 修复 roamlinks 插件误报

`mkdocs-roamlinks-plugin` 会把任何 `[[word]]` 模式（包括代码块和标题中）当作 wikilink 处理。
SCHEMA.md、log.md、setup-guide.md 中如果写了 `[[wikilinks]]` 这种文字描述，会产生 WARNING。
修复：改为纯文字描述，避免 `[[...]]` 包围。

### 修复 OCR 文本链接路径

等保标准页面（`concepts/网络安全等级保护/` 下）的 `[OCR文本](raw/papers/...)` 是相对路径，
MkDocs 会从当前页目录解析导致 404。改为绝对路径 `[OCR文本](/raw/papers/...)` 或
相对路径 `[OCR文本](../../raw/papers/...)`。

### 修复裸 URL — 启用 magiclink

在 mkdocs.yml markdown_extensions 中添加：

```yaml
markdown_extensions:
  - pymdownx.magiclink
```

注意：`pymdown-extensions` 已在官方镜像中，**无需 pip install**。

### 修复 setup-guide 过时内容

对比 docker-compose.yml 实际配置 vs setup-guide.md 中记录的：

| 项目 | 检查点 |
|------|--------|
| volume 映射路径 | `/docs` 还是 `/llm-wiki` |
| 端口 | 8000 还是 8456 |
| 网络名 | `hermes-network` 还是 `hermes_hermes-network` |
| command 参数 | 是否含 `--dirty` |

## 第三步：重启与验证

```bash
# 重启容器
docker restart llm-wiki

# 查看启动日志，确认无 WARNING（nav 引用、roamlinks 误报等已消除）
sleep 5 && docker logs llm-wiki --tail 20
# 理想输出：只有 INFO 级消息，无 WARNING 行

# 验证子目录 200
curl -s -o /dev/null -w "%{http_code}\\n" https://wiki.devtoy.xyz/entities/
curl -s -o /dev/null -w "%{http_code}\\n" https://wiki.devtoy.xyz/concepts/
curl -s -o /dev/null -w "%{http_code}\\n" https://wiki.devtoy.xyz/comparisons/
curl -s -o /dev/null -w "%{http_code}\\n" https://wiki.devtoy.xyz/queries/

# 浏览器手动验证
# 1. 打开任意等保页面 → 底部 [[wikilinks]] 应为蓝色可点击
# 2. 打开 setup-guide → "相关文档" 表格中的 URL 应为超链接
# 3. 点击 nav 中"对比分析"→ 应跳转至 comparisons/index.md

# Agent 侧无法直接访问 docker，以上命令需宿主机执行
```
