# LLM Wiki 媒体文件上传到 R2 的工作流

## 用途
Hermes Agent 在创建 LLM Wiki 内容时，遇到图片/PDF 等文件需要上传到 R2，然后在 Markdown 中通过 URL 引用。

## 架构
```
本地 Markdown（git 跟踪）       R2（远程存储）
├── docs/entities/ai.md         wiki-media/
│   └── ![架构图](R2_URL)       ├── images/2026-07/ai-arch.png
├── docs/concepts/              ├── pdfs/2026-07/
└── docs/raw/                   └── icons/
```

## R2 存储结构
```
wiki-media/
├── images/YYYY-MM/      ← 图片（按月分目录）
├── pdfs/YYYY-MM/        ← PDF
└── icons/               ← 可复用的图标
```

## 上传脚本 `wiki_upload.py`
放在 `~/llm-wiki/scripts/wiki_upload.py`，基于 r2_uploader.py：

```python
"""Upload LLM Wiki media files to R2."""
import sys, os
sys.path.insert(0, '/opt/data')
from r2_uploader import R2Uploader
from datetime import datetime

PREFIX = 'wiki-media'

def upload(file_path, category='images'):
    """上传文件到 R2 wiki-media 目录，返回公网 URL。"""
    ext = file_path.rsplit('.', 1)[-1].lower()
    month = datetime.now().strftime('%Y-%m')
    key = f'{PREFIX}/{category}/{month}/{os.path.basename(file_path)}'
    
    r2 = R2Uploader()
    url = r2.upload_file(file_path, key)
    print(url)
    return url

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 wiki_upload.py <file_path> [category]')
        sys.exit(1)
    upload(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'images')
```

## 在 Hermes Agent 中的工作流
当 Agent 需要给 wiki 内容添加图片时：

1. 生成/下载图片到 `/tmp/wiki-upload/`
2. 调用上传脚本：
   ```bash
   cd /opt/data && /opt/hermes/.venv/bin/python3 /opt/data/llm-wiki/scripts/wiki_upload.py /tmp/wiki-upload/chart.png images
   ```
3. 获取返回的 URL
4. 在 Markdown 中写入：
   ```markdown
   ![图表描述](https://hermes-main-media.devtoy.xyz/wiki-media/images/2026-07/chart.png)
   ```

## 渲染兼容性
- ✅ MkDocs Material: 原生支持网络图片 URL
- ✅ Obsidian: 原生支持 `![alt](URL)` 语法
- ✅ 所有 Markdown 渲染器通用

## 注意事项
- 图片先存本地临时目录，上传后**不需要保留本地副本**
- Markdown 文件本身不存储图片二进制内容，只存 URL
- R2 免费额度：10GB 存储，每月 1000 万次读取 — 图片文件足够
- 分类参数：`images`（默认）、`pdfs`、`icons`
