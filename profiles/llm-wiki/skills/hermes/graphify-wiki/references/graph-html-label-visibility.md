# graph.html 节点标签可见性 + 响应式优化（实战调试链）

来源：2026-07 session — 用户反馈"节点遮挡、密密麻麻、移动端看不清"。

## 根因链（按出现顺序）

Graphify `export.to_html()` 默认节点 `font:{size:0}`（无标签）。要显示标签必须后处理强制，但有一串隐藏坑：

1. **graphify 不导出 `value`(degree) 字段** — vis 的 `scaling.label.drawThreshold` 基于 `value` 判定，全 0 → 所有标签被阈值过滤不画。即使设 `font.size=14` 也白搭。
2. **在 `G.nodes` 注入 `value=degree` 不生效** — `to_html` 序列化只取特定字段忽略 `value`。必须在**运行时**从 `network.body.data.edges` 算 degree 再 `nodes.update({value:d})`。
3. **`scaling.label.enabled` 必须关掉** — 开启时字号由 scaling 计算、`font.size` 被忽略；关掉后 `font.size` 直接控制（degree≥3 设 15、<3 设 0 隐藏小节点）。
4. **update 时机** — graphify stabilization 在 VIS_OPT 注册 `network.once('stabilizationIterationsDone')` **之前**已完成 → `once` 永不触发。必须用 `setTimeout(postStable, 3000)` + `(postStable, 6000)` 兜底，且 resize 重跑 applyOpts。
5. **console 验证技巧** — 手动 `window.__nds.update([{id:'setup_guide', font:{size:30,strokeColor:'#f00'}}])` 截图确认 vis 渲染层响应 `font.size`（渲染 OK → 问题在 update 时机/被覆盖）。

## 调试钩子

`const network` 是块级 const，console 全局访问不到。在 VIS_OPT 开头加：
```js
window.__net = network;
window.__nds = network.body.data.nodes;
```
之后 console 可读 `window.__nds.get()` 确认 font/size/value。

## 完整 postStable 模板（桌面端示标签 + 移动端隐藏）

```js
function postStable(){
  if (network.body && network.body.data && network.body.data.nodes) {
    var all = network.body.data.nodes.get();
    var deg = {}; var eds = network.body.data.edges.get();
    for (var e=0;e<eds.length;e++){ deg[eds[e].from]=(deg[eds[e].from]||0)+1; deg[eds[e].to]=(deg[eds[e].to]||0)+1; }
    var upd = [];
    for (var i=0;i<all.length;i++){
      var n=all[i]; var d=deg[n.id]||0;
      var mobile = window.innerWidth < 768;
      if (mobile) {
        upd.push({ id:n.id, value:d, font:{size:0}, size:Math.min(n.size||6,13) });
      } else {
        upd.push({ id:n.id, value:d, font:{size: d>=3?15:0, strokeWidth:4, strokeColor:'#fff'} });
      }
    }
    network.body.data.nodes.update(upd);
    if (mobile) {
      network.on('hoverNode', function(p){ network.body.data.nodes.update([{id:p.node, font:{size:13}}]); });
      network.on('blurNode',  function(p){ network.body.data.nodes.update([{id:p.node, font:{size:0}}]); });
    }
  }
  try {
    var boxes = document.querySelectorAll('#communities-panel input[type=checkbox]');
    var changed=false;
    for (var b=0;b<boxes.length;b++){
      var cb=boxes[b]; var cid=cb.getAttribute('data-community-id');
      if (cid && typeof communitySize==='function' && communitySize(cid)>0 && communitySize(cid)<6){ if(cb.checked){cb.checked=false;changed=true;} }
    }
    if (changed && typeof applyCommunityFilter==='function') applyCommunityFilter();
  } catch(e){}
}
network.once('stabilizationIterationsDone', postStable);
setTimeout(postStable, 3000); setTimeout(postStable, 6000);
```

## applyOpts setOptions（物理 + 响应式）

```js
network.setOptions({
  physics: { enabled:true, solver:'barnesHut',
    barnesHut:{ gravitationalConstant:-12000, centralGravity:0.15, springLength:160, springConstant:0.04, damping:0.5, avoidOverlap:0.9 },
    stabilization:{ iterations:300, fit:true } },
  nodes: { shape:'dot', size: mobile?6:12,
    font:{ size: mobile?0:14, face:'sans-serif', strokeWidth:3, strokeColor:'#fff' },
    scaling:{ min: mobile?3:7, max: mobile?16:28, label:{ enabled:false } }, hidden:false },
  edges: { smooth:{enabled:true,type:'continuous'}, color:{opacity: mobile?0.18:0.4}, width: mobile?0.4:0.8 },
  interaction: { hover:true, tooltipDelay:120, navigationButtons:true, multiselect:true, zoomView:true, dragNodes:true, dragView:true }
});
```

## 关联质量：INFERRED → LIKELY（跨主题误连修复）

`enrich-graph.py` 原逻辑"同目录任意两文件都连边"会把 `entities/` 根目录的"等保标准实体"与"投资组合/AI Agent 实体"硬连（跨主题）。

修复：弱关联降级为 `LIKELY`（confidence_score 0.4），且**只连精确子目录（目录深度≥2）**，根目录（entities/、concepts/）不互连。实测跨主题误连清零：`等保↔投资/hermes=0`、`6dim↔font/graph=0`。

前端 `related-pages.js` 用 `LIKELY` 排在 EXTRACTED/INFERRED 之后，折叠为"展开弱关联"按钮。

## wiki_title 注入（中文标签）

Graphify 节点 `label` 是 slug（如 `hermes-agent.md`），非中文。在 `build-graph.py` 的 `export.to_json` 前，遍历 `result['nodes']` 从源文件 H1 提取 `wiki_title`，并**同步到 `G.nodes`**（to_json 读 G 不读 result）：
```python
def _get_h1(p):
    for line in open(p, encoding='utf-8'):
        m = re.match(r'^#\s+(.+?)\s*$', line)
        if m: return m.group(1).strip()
_title_map = {n['id']: _get_h1(_docs/n['source_file']) for n in result['nodes'] if ...}
for _gn in G.nodes():
    if _gn in _title_map: G.nodes[_gn]['wiki_title'] = _title_map[_gn]
```
前端 `related-pages.js` 的 `id2label` / `getLabelForNode` 优先读 `wiki_title`。

## ⚠️ 最终结论（2026-07 后续验证，覆盖上方 postStable 路径）

上方 postStable 批量 `nodes.update({font:{size:15}})` 路径**实测不可靠**：
- 数据层确认 `font.size=15` 已写入（console 读 `window.__nds` 验证 183 节点有标签），
  但 canvas 仍不画——graphify 在该页**禁用了 vis 原生标签层**（用独立 canvas overlay
  只画社区圈，不画普通节点标签）。手动单节点 `font:{size:30}` 偶发显示属巧合/时序。

**唯一确定可行的方案 = canvas overlay 画标签**（绕过 vis 标签层）：
在 VIS_OPT 注入段加 `network.on('afterDrawing', drawLabels)`，遍历节点用
`ctx.fillText` 在节点下方画中文标签（节点坐标用 `network.getPositions([id])`）。

```js
function drawLabels(ctx) {
  try {
    var nodes = network.body.data.nodes.get();
    var sc = network.getScale ? network.getScale() : 1;
    ctx.save(); ctx.font = '12px sans-serif';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    for (var i=0;i<nodes.length;i++) {
      var n = nodes[i]; if (n.hidden) continue;
      var lbl = (n.label || '').toString();
      if (!lbl || lbl.length === 0) continue;
      var pos = network.getPositions([n.id])[n.id]; if (!pos) continue;
      var short = lbl.length > 14 ? lbl.slice(0,13)+'\u2026' : lbl;
      var w = ctx.measureText(short).width + 6;
      var y = pos.y + (n.size ? n.size*sc : 6) + 8;
      ctx.fillStyle = 'rgba(15,15,26,0.72)';
      ctx.fillRect(pos.x - w/2, y - 8, w, 16);
      ctx.fillStyle = '#fff'; ctx.fillText(short, pos.x, y);
    }
    ctx.restore();
  } catch(e) {}
}
if (network && network.on) network.on('afterDrawing', drawLabels);
```

⚠️ **drawLabels 实现陷阱**：函数内变量名必须一致。若写 `var lbl = ...` 却在
`if (!lbl || lbl.length===0) continue;` 里误打成 `!lbl`（少一个 l），该条件永远为真 →
所有标签被 `continue` 跳过 → 标签仍不显示，且 try/catch 静默吞掉（无报错）。
**写完后务必 grep 确认函数内变量名统一**（如 `lbl` 出现 3 次：定义、判断、slice）。

## ⚠️ 库源码改动的致命陷阱（f-string）
若直接改 `exporters/html.py`，JS 里的 `{ size: 14 }` 在 `f"""` 模板里被当成 Python 表达式
→ `name 'size' is not defined` → `export.to_html()` 抛异常、静默失败。正确写法 `{{ size: 14 }}`。
**推荐**：不要改库，全部用 build-graph.py 后处理字符串替换，避免 f-string 崩溃。

## wiki_title 注入必须双写（否则无效）
Graphify `to_html` 只序列化 G.nodes 的 `label` 字段（非 `wiki_title`）。注入中文标题时：
`G.nodes[_gn]['wiki_title'] = title`（JS fallback 用）**且** `G.nodes[_gn]['label'] = title`
（Graphify 导出用）。只写 `wiki_title` → RAW_NODES JSON 无该字段 → 回退 slug。

## CF 缓存验证坑
curl `https://wiki.devtoy.xyz/graph-html/graph.html` 无 `?v=` 命中 Cloudflare 边缘旧版
→ grep 验证会误判"改动未上线"。验证线上真实内容加随机 query 回源：
`curl -s "...graph.html?cb=$(date +%s)"`。

## ⚠️ Browserbase 浏览器验证陷阱（本 session 新增）
Browserbase 浏览器工具与 `curl` 走**不同的 CF 边缘/缓存层**：浏览器会话持续命中
旧版 graph.html（无论换新文件名 graph.v3/v4/v5、加 `?nocache=`、按 F5 硬刷新，
console 探测 `drawLabels:false` 但 curl 明文拿到含 drawLabels 的新版）。
**结论：用浏览器截图验证静态 HTML 改动不可信**。验证优先级：
1. 数据层：Python 解析 `RAW_NODES` JSON 确认 `label` 为中文。
2. 代码层：`node -e "const fs=require('fs');const h=fs.readFileSync('docs/graph-html/graph.html','utf8');const m=h.match(/function drawLabels[\s\S]*?\n  }/);try{new Function(m[0]);console.log('OK');}catch(e){console.log('ERR',e.message);}"` —— 提交注入的 JS 前必跑，捕捉 `!lbl` 类 typo（被 try/catch 静默吞掉）。
3. 源站层：`curl` 明文确认 `drawLabels` 存在（cf-cache-status: DYNAMIC，源站不缓存）。
4. 真机层：请用户用自己的浏览器访问确认（DYNAMIC 缓存，首次访问即最新）。

