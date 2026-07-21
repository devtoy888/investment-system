#!/usr/bin/env python3
"""Upload v2_report_corrected.html to R2"""
import sys
sys.path.insert(0, '/opt/data')
from r2_uploader import R2Uploader
from pathlib import Path

u = R2Uploader()
base = 'fund-system/llm-validation'
md = Path('fund_system_data/llm_validation/v2_report_corrected.md').read_text(encoding='utf-8')

escaped = md.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>v2全量验证报告(修正版)</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;max-width:800px;margin:0 auto;padding:20px;background:#0d1117;color:#c9d1d9;line-height:1.6}
table{border-collapse:collapse;width:100%;margin:15px 0} th,td{border:1px solid #30363d;padding:8px 12px;text-align:left}
th{background:#161b22} code{background:#161b22;padding:2px 6px;border-radius:3px}
pre{background:#161b22;padding:15px;border-radius:6px;overflow-x:auto}
h1,h2,h3{color:#58a6ff} a{color:#58a6ff}
</style>
</head>
<body>
<div id="content">加载中...</div>
<script>
const md = `''' + escaped + '''`;
document.getElementById('content').innerHTML = marked.parse(md);
</script>
</body>
</html>'''

u.upload_bytes(html.encode('utf-8'), base + '/v2_report_corrected.html', 'text/html; charset=utf-8')
print('✅ v2_report_corrected.html uploaded')
