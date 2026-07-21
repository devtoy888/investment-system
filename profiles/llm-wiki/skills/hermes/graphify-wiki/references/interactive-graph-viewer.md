# Interactive Graph Viewer (Graphify 原生 graph.html)

用 Graphify `export.to_html()` 生成的交互图（vis-network），**替代 ECharts**。原生含搜索框、NODE INFO 面板、社区过滤器、边置信度 tooltip（EXTRACTED/INFERRED）。

## 生成
```python
export.to_html(G, clusters, 'graphify-out/graph.html', community_labels=labels)
```

## 托管到 MkDocs
1. `cp graphify-out/graph.html docs/graph-html/graph.html`（**需 docker restart 生效**）
2. `docs/concepts/graph-viewer.md` 用 iframe：`<iframe src="/graph-html/graph.html" style="width:100%;height:80vh;border:1px solid #30363d;border-radius:8px;"></iframe>`

## 节点点击跳 wiki 页（文件级，后处理注入，不改库）
```python
html = html_path.read_text(encoding='utf-8')
if 'WIKI_JUMP_INJECTED' not in html:
    so = html.find('<script>'); sc = html.find('</script>', so)
    inject = '''
/* WIKI_JUMP_INJECTED */
network.on('click', function(params) {
  if (params.nodes && params.nodes.length) {
    var n = nodesDS.get(params.nodes[0]);
    if (n && n._source_file) window.open('/' + n._source_file.replace(/\.md/, '') + '/', '_self');
  }
});
'''
    html = html[:sc] + inject + html[sc:]
    html_path.write_text(html, encoding='utf-8')
```

## 三大坑
1. 注入必须在**第一个 `<script>` 块**内（network/nodesDS 是块级 const，跨块不可见）。
2. 变量名是 **`nodesDS`**（不是 `nodes`）。
3. 节点字段是 **`_source_file`**（带下划线前缀，非 `source_file`）。

## 验证
浏览器加载 graph.html → 确认搜索框/NODE INFO/社区过滤器/canvas；console `network.emit('click',{nodes:['<id>']})` 并 spy `window.open` 确认捕获 `/<page>/`。
