# Serving Markdown as HTML via R2 (Client-Side Rendering)

When you need to share `.md` content from R2 in a browser-friendly format, a `text/plain` Content-Type shows raw text without formatting. This reference covers converting MD→HTML for browser consumption.

## Approaches

### Approach 1: Client-Side `marked.js` (Recommended)

Embed the raw Markdown as a JS string in an HTML wrapper, then use the `marked.js` library (from CDN) to render in the browser:

```
Template:
  <!DOCTYPE html>
  <html lang="zh-CN">
  <head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page Title</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/15.0.7/marked.min.js"></script>
  <style>
    /* responsive styles */
    body { font-family: -apple-system, "Noto Sans SC", sans-serif; padding: 12px; }
    #content { max-width: 860px; margin: 0 auto; }
    /* ... (see full template below) */
  </style>
  </head>
  <body>
  <div id="content">Loading...</div>
  <script>
  const md = `...markdown content here (escaped)...`;
  marked.setOptions({breaks:true, gfm: true});
  document.getElementById('content').innerHTML = marked.parse(md);
  </script>
  </body>
  </html>
```

**Key advantages:**
- Handles ALL markdown edge cases (code blocks in blockquotes, mixed indentation, nested lists) — marked.js is battle-tested
- Content is always up-to-date (no pre-rendering needed)
- Self-contained single file, no external dependencies beyond CDN JS
- Supports GFM (tables, task lists, strikethrough, auto-links)

**Required escaping for JS string (Python):**
```python
md_escaped = md.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
```

### Approach 2: Server-Side Python `markdown` Library

Use the Python `markdown` library to pre-render before upload:

```python
import markdown
html_body = markdown.markdown(md, extensions=[
    'markdown.extensions.tables',
    'markdown.extensions.fenced_code',
    'markdown.extensions.codehilite',
    'markdown.extensions.nl2br',
])
# Then wrap in HTML template and upload
```

**Limitations:**
- Code blocks inside blockquotes (`> ```bash`) may be rendered as headings instead of code
- No syntax highlighting in code blocks without extra CSS
- Need to rebuild and re-upload when content changes

## Recommended: Full `marked.js` Template

```python
import json

with open('doc.md', 'r') as f:
    md = f.read()

# JS-safe escaping
md_escaped = md.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Page Title</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/15.0.7/marked.min.js"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
    font-size: 16px; line-height: 1.8; color: #1a1a2e; background: #f5f5f5; padding: 12px;
  }}
  #content {{
    max-width: 860px; margin: 0 auto; background: #fff; border-radius: 10px;
    padding: 28px 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }}
  #content h1 {{ font-size:1.65em; margin:.6em 0 .3em; color:#0d47a1; border-bottom:2px solid #1565c0; padding-bottom:.3em; }}
  #content h2 {{ font-size:1.35em; margin:1.3em 0 .4em; color:#1565c0; border-left:4px solid #1565c0; padding-left:12px; }}
  #content pre {{ background:#1e1e2e; color:#cdd6f4; padding:16px; border-radius:8px; overflow-x:auto; font-size:.82em; }}
  #content pre code {{ background:none; padding:0; }}
  #content table {{ width:100%; border-collapse:collapse; display:block; overflow-x:auto; }}
  #content th, #content td {{ border:1px solid #dee2e6; padding:8px 12px; }}
  #content th {{ background:#e3f2fd; }}
  #content blockquote {{ border-left:4px solid #90caf9; background:#e3f2fd; padding:10px 16px; margin:.8em 0; border-radius:0 8px 8px 0; }}
  @media (max-width:600px) {{
    body {{ padding:6px; font-size:15px; }}
    #content {{ padding:16px 12px; }}
    #content pre {{ font-size:.72em; padding:12px; }}
  }}
  @media (prefers-color-scheme:dark) {{
    body {{ background:#0d0d1a; color:#e0e0e0; }}
    #content {{ background:#16162a; }}
    #content h1 {{ color:#64b5f6; border-bottom-color:#64b5f6; }}
    #content h2 {{ color:#64b5f6; border-left-color:#64b5f6; }}
    #content th {{ background:#1a237e; color:#e3f2fd; }}
    #content td {{ border-color:#37474f; }}
    #content code {{ background:#2a2a4a; }}
  }}
</style>
</head>
<body>
<div id="content">Loading...</div>
<script>
marked.setOptions({{breaks:true, gfm: true}});
document.getElementById('content').innerHTML = marked.parse(`{md_escaped}`);
</script>
</body>
</html>'''

with open('/tmp/output.html', 'w') as f:
    f.write(html)
```

## Upload to R2

```python
uploader = R2Uploader()
url = uploader.upload_file(
    '/tmp/output.html',
    'path/doc.html',
    content_type='text/html; charset=utf-8'
)
```

## Common Pitfalls

| Issue | Fix |
|-------|-----|
| Chinese text in JS template literal | Ensure Python `.replace('\\${', '\\\\${')` to avoid f-string interference |
| Template literal backtick in MD content | `.replace('`', '\\`')` in the Markdown content |
| Large files >50KB | `marked.js` handles large content fine, but mobile rendering may lag — consider breaking into multiple HTML files |
| CDN availability | `marked.js` is served by Cloudflare CDN (cdnjs) — highly reliable in China |
| Dark mode | Use `prefers-color-scheme: dark` media query for auto-switching |
