# graph-viewer.md UX 修复实录（用户四项反馈）

来源：用户对 graph.html / graph-viewer 页的四点反馈及修复。沉淀为可复用 checklist。

## 用户反馈 → 根因 → 修复

| # | 反馈 | 根因 | 修复位置 |
|---|------|------|----------|
| 1 | 点击节点不跳转 | 多层叠加：(a) 旧跳转 `window.open('/'+source_file.replace(/\\.md/,'')+'/')` 丢子目录前缀（→`/setup-guide/` 404）；(b) **`.md` 正则转义坑**（Python 注入使 `/\\.md$/` 变字面 `\\\\.md`，永不匹配 → `.md` 去不掉 → `/setup-guide.md/` 404）；(c) **source_file 丢目录**（graphify 只存 `setup-guide.md`，需 build 时从 docs 归一化重建完整路径）；(d) **iframe 导航陷阱（最终根因）**：graph.html 经 `<iframe>` 嵌入 wiki 页，handler 写 `window.location.href=url` 只改 iframe 自身 src、父页面不动，用户感知"点不动"。(a)(b)(c) 修完 curl/grep 全过，真实点击仍不跳，直到改 `window.top.location.href=url` 才真修好 | build-graph.py 注入 `wikiUrlOf()`（`slice(-3)==='.md'` 去后缀避正则、保留 `dirname`、source_file 从 docs 映射补全 → `/setup/setup-guide/`）；点击 handler 用 `window.top.location.href` 顶层跳转 |
| 2 | PC 端容器太小、显示不够 | iframe `height:80vh` + graph.html `body{height:100vh}` 被 mkdocs 父容器限制 | graph-viewer.md iframe 改 `height:100vh`；graph.html 本身已 `100vh` 就绪 |
| 3 | 右侧搜索/Communities 面板不能折叠 | graphify 模板 `#sidebar` 无折叠逻辑 | 注入 `#sb-toggle` 绝对定位按钮，`sb.style.display='none'` 折叠，图谱 `#graph{flex:1}` 自动铺满 |
| 4 | Communities 显示 concepts/log 无意义 | `community_labels` 用节点 id 前缀（如 `concepts30`），且 build 时 labels 计算失效（空 `{}`） | labels = 社区内最高 degree 节点的中文 `wiki_title` + 节点数，如 `GB/T 28449-2018 信息安全技术... (41)` |

## 关键验证点（部署后必查）

1. **跳页 URL 回归**：抽 `source_file` 含子目录的节点（如 `setup/setup-guide.md`），用 `wikiUrlOf` 推导路由，确认 == MkDocs 实际路由（`/setup/setup-guide/`），非缺前缀的 `/setup-guide/`。
   ```bash
   /llm-wiki/scripts/.graphify-venv/bin/python3 -c "
   import json
   d=json.load(open('/llm-wiki/graphify-out/graph.json'))
   for n in d['nodes'][:200]:
       sf=n.get('source_file','')
       if '/' in sf:
           base=sf[:-3].rsplit('/',1)
           print(sf, '->', '/' + base[0] + '/' + base[1] + '/')
   " | head
   ```
2. **LEGEND 中文名回归**：解析线上 graph.html 的 `const LEGEND = [...]` 确认社区名是中文 wiki_title + 节点数，非 `concepts30`/`log21` 之类前缀。
3. **iframe 高度**：graph-viewer.md 的 iframe `style` 含 `height:100vh`。
4. **sb-toggle**：`grep -c sb-toggle docs/graph-html/graph.html` >= 1。

## 不要做的事

- 不要用 Browserbase 浏览器截图验证 graph.html 改动（CF 会话缓存隔离，见 SKILL.md CF 坑）。改用 **本地 playwright + chromium 加载 file:// 副本** 跑真实 JS（见 SKILL.md「自动化浏览器验证」），或 curl `?cb=` + node 语法检查 + 请用户浏览器肉眼验收。
- 不要在 `_nodes_raw` 定义之前计算 `labels`（NameError）。
- 不要在 drawLabels 里写 `!lbl`（少一个 l，静默吞错）。
- **不要把节点 label 覆盖成文件 H1**：一个 md 被 graphify 拆成多个语义节点，全写成文件标题 → 790 节点塌缩成 70 个同名 label（用户截图实锤）。节点 label 用语义化 id，wiki_title 只给社区名/跳转。
- **不要只靠 curl/grep 声称 graph.html 修复完成**：本次两次 curl/grep 通过却线上仍炸（同名、不跳）。用户硬性要求真实浏览器自动化测试。每次改注入 JS 后必跑 `scripts/graph-html-e2e-test.js`。
