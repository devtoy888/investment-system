#!/usr/bin/env python3
"""Upload evolution MD docs + generate HTML versions to R2"""
import sys
sys.path.insert(0, '/opt/data')
from r2_uploader import R2Uploader
from pathlib import Path

u = R2Uploader()
base = 'fund-system/llm-evolution'

for fname in ['EVOLUTION_ARCH.md', 'ROADMAP.md']:
    fp = Path(f'fund_system_data/llm_evolution/{fname}')
    md = fp.read_text(encoding='utf-8')
    
    # Upload MD
    u.upload_bytes(md.encode('utf-8'), f'{base}/{fname}', 'text/markdown; charset=utf-8')
    print(f'  MD: {base}/{fname}')
    
    # Generate HTML with embedded markdown
    escaped = md.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{fname.replace('.md','').replace('_',' ')}</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         max-width: 800px; margin: 0 auto; padding: 20px;
         background: #0d1117; color: #c9d1d9; line-height: 1.6; }}
  table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
  th, td {{ border: 1px solid #30363d; padding: 8px 12px; text-align: left; }}
  th {{ background: #161b22; }}
  code {{ background: #161b22; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
  pre {{ background: #161b22; padding: 15px; border-radius: 6px; overflow-x: auto; }}
  h1, h2, h3 {{ color: #58a6ff; }}
  a {{ color: #58a6ff; }}
</style>
</head>
<body>
<div id="content">加载中...</div>
<script>
const mdContent = `{escaped}`;
document.getElementById('content').innerHTML = marked.parse(mdContent);
</script>
</body>
</html>'''
    
    htmlname = fname.replace('.md', '.html')
    u.upload_bytes(html.encode('utf-8'), f'{base}/{htmlname}', 'text/html; charset=utf-8')
    print(f'  HTML: {base}/{htmlname}')

print('\n✅ 全部上传完成')
