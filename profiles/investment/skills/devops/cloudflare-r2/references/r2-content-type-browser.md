# R2 文件 Content-Type：浏览器正确显示中文

## 核心规则

| 文件类型 | 推荐的 Content-Type | 说明 |
|---------|-------------------|------|
| .md | `text/plain; charset=utf-8` | ❌ 不要用 text/markdown（浏览器不识别）|
| .html | `text/html; charset=utf-8` | 浏览器原生支持 |
| .json | `application/json; charset=utf-8` | API 消费时用 |

## 为什么 text/markdown 不行？

`text/markdown` 这个 MIME 类型在 RFC 中定义但主流浏览器（Chrome、Safari、Firefox）并不原生支持。
浏览器会：
1. 不认识该类型 → 当成 `application/octet-stream` 下载
2. 或尝试渲染但编码不正确（中文乱码）

## 自动验证工具

上传后自动检查 Content-Type 和中文可读性：

```bash
python3 /opt/data/scripts/r2_upload_and_verify.py local.md remote-key.md
```

验证项：
- HTTP 状态码 200
- Content-Type 正确
- UTF-8 编码
- 中文关键词可读

## HTML 包装方案

对于需要在浏览器中美观展示的 Markdown 文档，更好的方式是用 marked.js 做客户端渲染：

```python
import markdown
html = f'''<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/15.0.7/marked.min.js"></script>
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 860px; margin: auto; padding: 16px; line-height: 1.8; }}
  @media (prefers-color-scheme: dark) {{ body {{ background: #1a1a2e; color: #e0e0e0; }} }}
</style>
</head><body>
<div id="content">加载中...</div>
<script>
document.getElementById('content').innerHTML = marked.parse(`MD_CONTENT`);
</script>
</body></html>'''
```
