# SVG Image Lightbox for MkDocs

Self-contained HTML+JS lightbox for large images/SVGs in MkDocs pages.
Includes zoom (+/- buttons + mouse wheel), pan (drag), and reset.
Click overlay background or ✕ button to close.

## Usage

Replace a markdown image `![alt](path)` with this HTML block in your `.md` file:

```html
<div style="text-align:center;margin:20px 0">
  <a href="javascript:void(0)" onclick="openLightbox()" style="cursor:zoom-in">
    <img src="/images/knowledge-graph.svg" alt="描述" style="max-width:100%;border:1px solid #30363d;border-radius:8px;transition:opacity .2s" onmouseover="this.style.opacity=.85" onmouseout="this.style.opacity=1">
  </a>
  <div style="margin-top:6px;font-size:13px;color:#8b949e">🖲️ 点击放大查看</div>
</div>

<div id="lb-overlay" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.85);z-index:9999;overflow:hidden">
  <div style="position:fixed;top:16px;right:16px;z-index:99999;display:flex;gap:8px">
    <button onclick="lbZoomIn()" title="放大" style="width:36px;height:36px;border-radius:8px;border:none;background:#2d333b;color:#c9d1d9;font-size:20px;cursor:pointer">+</button>
    <button onclick="lbZoomOut()" title="缩小" style="width:36px;height:36px;border-radius:8px;border:none;background:#2d333b;color:#c9d1d9;font-size:20px;cursor:pointer">−</button>
    <button onclick="lbReset()" title="重置" style="width:36px;height:36px;border-radius:8px;border:none;background:#2d333b;color:#c9d1d9;font-size:16px;cursor:pointer">↺</button>
    <button onclick="closeLightbox()" title="关闭" style="width:36px;height:36px;border-radius:8px;border:none;background:#da3633;color:#fff;font-size:18px;cursor:pointer">✕</button>
  </div>
  <div id="lb-container" style="position:fixed;top:0;left:0;width:100%;height:100%;display:flex;align-items:center;justify-content:center;cursor:grab" onclick="closeLightbox(event)">
    <div style="position:relative;display:inline-block" onclick="event.stopPropagation()">
      <img id="lb-img" src="/images/knowledge-graph.svg" alt="描述" style="display:block;max-width:100vw;max-height:100vh">
    </div>
  </div>
</div>

<script>
var Z=1,X=0,Y=0,D=false,SX,SY,PX,PY;
function openLightbox(){document.getElementById('lb-overlay').style.display='block';document.body.style.overflow='hidden';Z=1;X=0;Y=0;U();}
function closeLightbox(e){if(e&&e.target!==document.getElementById('lb-container')&&e.target!==document.getElementById('lb-overlay'))return;document.getElementById('lb-overlay').style.display='none';document.body.style.overflow='auto';}
function U(){var i=document.getElementById('lb-img');i.style.transform='translate('+X+'px,'+Y+'px) scale('+Z+')';i.style.transformOrigin='center center';}
function lbZoomIn(){Z=Math.min(Z*1.3,10);U();}
function lbZoomOut(){Z=Math.max(Z/1.3,0.2);U();}
function lbReset(){Z=1;X=0;Y=0;U();}
document.getElementById('lb-container').addEventListener('wheel',function(e){e.preventDefault();e.stopPropagation();Z=Math.min(Math.max(Z*(e.deltaY<0?1.2:1/1.2),0.2),10);U();},{passive:false});
document.getElementById('lb-container').addEventListener('mousedown',function(e){D=true;SX=e.clientX;SY=e.clientY;PX=X;PY=Y;this.style.cursor='grabbing';});
document.addEventListener('mousemove',function(e){if(!D)return;X=PX+(e.clientX-SX);Y=PY+(e.clientY-SY);U();});
document.addEventListener('mouseup',function(){if(D){D=false;var c=document.getElementById('lb-container');if(c)c.style.cursor='grab';}});
document.addEventListener('keydown',function(e){if(document.getElementById('lb-overlay').style.display!=='block')return;if(e.key==='Escape')closeLightbox({target:document.getElementById('lb-overlay')});if(e.key==='='||e.key==='+')lbZoomIn();if(e.key==='-')lbZoomOut();if(e.key==='0')lbReset();});
</script>
```

## Key Details

- **Use absolute paths**: `src="/images/foo.svg"` not `src="../images/foo.svg"`. MkDocs rewrites markdown image paths relative to the markdown file, but **raw HTML paths resolve relative to the page URL**. A page at `/concepts/knowledge-graph/` with `../images/foo.svg` becomes `/concepts/images/foo.svg` — wrong.
- **`passive:false`** on the wheel listener prevents the background page from scrolling while zooming.
- **`transform-origin: center center`** ensures scale applies from the image center.
- **Keyboard shortcuts**: Esc (close), +/- (zoom), 0 (reset).
- The minified JS at the bottom avoids name collisions with other scripts on the page.
