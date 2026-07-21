# Interactive Graph Viewer (ECharts)

HTML template for embedding an interactive knowledge graph in the wiki. Uses ECharts force-directed layout.

## Usage

1. Place at `docs/concepts/graph-viewer/index.html`
2. `graph.json` must be accessible at `../../images/graph-data.json`

## Key Config

- **Colors**: Array per community (max 12, cycles after)
- **Node size**: `symbolSize: Math.max(8, 25 - nodes.length/10)` — scales with wiki size
- **Force layout**: `repulsion: 300, edgeLength: 100, gravity: 0.1`
- **Click handler**: Shows tooltip with source filename
- **Roam**: Enabled (pan + zoom)

## Standalone viewer (no MkDocs plugin needed)

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>Knowledge Graph</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<style>*{margin:0;padding:0}body{background:#0d1117;overflow:hidden}#g{width:100vw;height:100vh}</style>
</head>
<body><div id=g></div>
<script>
fetch("graph-data.json").then(r=>r.json()).then(d=>{
const C=["#f97316","#8b5cf6","#06b6d4","#10b981","#ef4444","#3b82f6","#f59e0b","#ec4899","#14b8a6","#6366f1","#84cc16","#d946ef"];
const cats=Object.entries(Object.fromEntries(d.nodes.map(n=>[n.community,n.community_name||("C"+n.community)])))
  .map(([i,n])=>({name:n,itemStyle:{color:C[i%C.length]}}));
const nds=d.nodes.map(n=>({id:n.id,name:n.label||n.id,category:n.community||0,symbolSize:20,itemStyle:{color:C[(n.community||0)%C.length]}}));
const lks=d.links.map(l=>({source:l.source,target:l.target}));
const ch=echarts.init(document.getElementById("g"));
ch.setOption({backgroundColor:"#0d1117",series:[{type:"graph",layout:"force",roam:true,data:nds,links:lks,categories:cats,force:{repulsion:300,edgeLength:100,gravity:0.1},label:{show:true,position:"right",fontSize:10,color:"#8b949e"},lineStyle:{color:"source",opacity:0.5},emphasis:{focus:"adjacency"}}]});
window.addEventListener("resize",()=>ch.resize())});
</script></body></html>
```
