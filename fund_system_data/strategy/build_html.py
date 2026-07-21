#!/usr/bin/env python3
"""Convert MD assessment report to self-contained HTML (no JS/CDN)"""
import re, os

md_path = '/opt/data/fund_system_data/strategy/DATA_SOURCE_ASSESSMENT.md'
html_path = '/opt/data/fund_system_data/strategy/DATA_SOURCE_ASSESSMENT.html'

with open(md_path, 'r') as f:
    md = f.read()

def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def inline(t):
    """Process inline markdown"""
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    return t

def render_table(rows):
    """Convert markdown table rows to HTML table"""
    parts = ['<div class="table-wrap"><table>']
    for idx, row in enumerate(rows):
        if idx == 1:  # skip alignment row
            continue
        cells = [c.strip() for c in row.split('|')]
        if cells and cells[0] == '':
            cells = cells[1:]
        if cells and cells[-1] == '':
            cells = cells[:-1]
        tag = 'th' if idx == 0 else 'td'
        parts.append('<tr>')
        for c in cells:
            parts.append(f'<{tag}>{inline(c)}</{tag}>')
        parts.append('</tr>')
    parts.append('</table></div>')
    return '\n'.join(parts)

# Parse markdown
lines = md.split('\n')
out = []
in_code = False
code_buf = []
in_tbl = False
tbl_buf = []

for i, line in enumerate(lines):
    # Code block
    if line.startswith('```'):
        if not in_code:
            in_code = True
            code_buf = []
        else:
            in_code = False
            code_html = esc('\n'.join(code_buf))
            out.append(f'<pre><code>{code_html}\n</code></pre>')
        continue
    
    if in_code:
        code_buf.append(line)
        continue
    
    # Horizontal rule
    if re.match(r'^---+$', line.strip()):
        if in_tbl:
            out.append(render_table(tbl_buf))
            in_tbl = False; tbl_buf = []
        out.append('<hr>')
        continue
    
    # Empty line
    if not line.strip():
        if in_tbl:
            out.append(render_table(tbl_buf))
            in_tbl = False; tbl_buf = []
        out.append('')
        continue
    
    # Table row
    if line.strip().startswith('|') and line.strip().endswith('|'):
        if not in_tbl:
            in_tbl = True; tbl_buf = []
        tbl_buf.append(line.strip())
        continue
    
    if in_tbl:
        out.append(render_table(tbl_buf))
        in_tbl = False; tbl_buf = []
    
    # Headings
    m = re.match(r'^(#{1,6})\s+(.+)$', line)
    if m:
        level = len(m.group(1))
        out.append(f'<h{level}>{inline(m.group(2))}</h{level}>')
        continue
    
    # Blockquote
    if line.startswith('> '):
        out.append(f'<blockquote><p>{inline(line[2:])}</p></blockquote>')
        continue
    
    # List items
    if re.match(r'^[\-\*]\s+', line):
        out.append(f'<li>{inline(re.sub(r"^[\-\*]\s+", "", line))}</li>')
        continue
    if re.match(r'^\d+\.\s+', line):
        out.append(f'<li>{inline(re.sub(r"^\d+\.\s+", "", line))}</li>')
        continue
    
    # Paragraph
    if line.strip():
        out.append(f'<p>{inline(line)}</p>')

if in_tbl and tbl_buf:
    out.append(render_table(tbl_buf))

body = '\n'.join(out)

# Add badge spans to table cells
for pattern, replacement in [
    (r'<td>(\u2705[^<]*)</td>', r'<td><span class="badge badge-ok">\1</span></td>'),
    (r'<td>(\u274c[^<]*)</td>', r'<td><span class="badge badge-err">\1</span></td>'),
]:
    body = re.sub(pattern, replacement, body)

# CSS
css = '''
:root{--bg:#0d1117;--bg-card:#161b22;--border:#30363d;--text:#e6edf3;--text-muted:#8b949e;--accent:#58a6ff;--green:#3fb950;--red:#f85149;--yellow:#d29922}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC',sans-serif;background:var(--bg);color:var(--text);line-height:1.7;padding:0;-webkit-font-smoothing:antialiased}
.header{background:linear-gradient(135deg,#1a2332 0%,#0d1117 100%);border-bottom:1px solid var(--border);padding:32px 16px 24px;text-align:center}
.header h1{font-size:1.5em;color:#fff;margin-bottom:6px}
.header .subtitle{color:var(--text-muted);font-size:.9em}
#content{max-width:900px;margin:0 auto;padding:20px 16px 60px}
#md-content h1{font-size:1.6em;margin:32px 0 16px;padding-bottom:8px;border-bottom:1px solid var(--border)}
#md-content h2{font-size:1.3em;margin:28px 0 12px}
#md-content h3{font-size:1.1em;margin:24px 0 10px;color:var(--accent)}
#md-content p{margin:12px 0}
#md-content a{color:var(--accent);text-decoration:none}
#md-content a:hover{text-decoration:underline}
#md-content strong{color:#f0f6fc}
#md-content table{width:100%;border-collapse:collapse;margin:16px 0;font-size:.85em;overflow-x:auto;display:block}
#md-content th,#md-content td{padding:6px 10px;border:1px solid var(--border);text-align:left;white-space:nowrap}
#md-content th{background:#1c2333;font-weight:600;color:var(--text-muted);font-size:.85em;text-transform:uppercase;letter-spacing:.5px}
#md-content tr:nth-child(even){background:#0d1117}
#md-content tr:hover{background:#1c2333}
#md-content code{background:#1c2333;padding:2px 6px;border-radius:4px;font-size:.85em;font-family:'JetBrains Mono','Fira Code',monospace;color:#ffa657}
#md-content pre{background:#161b22;border:1px solid var(--border);border-radius:8px;padding:16px;overflow-x:auto;margin:16px 0}
#md-content pre code{background:0 0;padding:0;color:var(--text);font-size:.8em;white-space:pre}
#md-content blockquote{border-left:3px solid var(--accent);padding:8px 16px;margin:16px 0;background:#0d1117;color:var(--text-muted)}
#md-content ul,#md-content ol{padding-left:24px;margin:12px 0}
#md-content li{margin:4px 0}
#md-content hr{border:none;border-top:1px solid var(--border);margin:32px 0}
.table-wrap{overflow-x:auto}
.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:.75em;font-weight:600}
.badge-ok{background:rgba(63,185,80,0.15);color:var(--green)}
.badge-warn{background:rgba(210,153,34,0.15);color:var(--yellow)}
.badge-err{background:rgba(248,81,73,0.15);color:var(--red)}
@media(max-width:600px){.header h1{font-size:1.2em}#md-content table{font-size:.75em}#md-content th,#md-content td{padding:4px 6px}#content{padding:12px 10px 40px}}
'''

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>📊 数据源全量评估与稳健化方案</title>
<style>{css}</style>
</head>
<body>
<div class="header">
<h1>📊 A股基金数据源全量评估与稳健化方案</h1>
<div class="subtitle">评估日期: 2026-07-18 · 数据源追踪: 560条记录</div>
</div>
<div id="content">
<div id="md-content">
{body}
</div>
<div style="margin-top:32px;padding-top:16px;border-top:1px solid var(--border);text-align:center;color:var(--text-muted);font-size:.8em">
📅 报告生成: 2026-07-18 · 数据来源: _source_availability.jsonl (560条) + 实时实测
</div>
</div>
</body>
</html>'''

with open(html_path, 'w') as f:
    f.write(html)

print(f'HTML: {len(html)} bytes')
print(f'Body: {len(body)} chars')
print(f'Badge ok: {body.count("badge-ok")}')
print(f'Badge err: {body.count("badge-err")}')
print(f'undefined count: {body.count("undefined")}')
print(f'Tables: {body.count("<table")}')
print(f'Code blocks: {body.count("<pre><code")}')
print('OK')
