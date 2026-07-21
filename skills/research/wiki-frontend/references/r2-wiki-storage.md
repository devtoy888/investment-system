# R2 Cold Storage for Wiki Large Files

## Problem
40GB server disk. Markdown is space-efficient (~1-3MB/100 pages), but:
- Images (screenshots, diagrams): 50-500KB each, adds up
- PDFs (papers, reports): 1-10MB each
- Git with binaries: history balloons

## Strategy
```yaml
Local disk (~/wiki/):
  - Markdown text (full content for instant Agent access)
  - Small images (<1MB)
  - Agent tool-accessible paths

R2 (Cloudflare):
  - Images >1MB
  - PDFs >5MB  
  - Audio, video, other large attachments
  - Referenced via URL in markdown: ![](https://r2-bucket.dev/path/file.png)
```

## Integration in Ingest Workflow

When Agent ingests a file into the wiki:

```python
from r2_uploader import R2Uploader
import os

uploader = R2Uploader()  # Reads credentials from .env

def ingest_file(path, key_prefix="wiki-assets"):
    size = os.path.getsize(path)
    threshold = 1 * 1024 * 1024  # 1MB
    
    if size > threshold:
        url = uploader.upload_file(path, f"{key_prefix}/{os.path.basename(path)}")
        os.remove(path)  # Free local disk
        return url  # Store this URL in markdown
    return None  # Keep locally
```

## Frontend Impact

| Scenario | Latency | Impact |
|----------|---------|--------|
| Agent reads markdown | 0ms (local) | None |
| Page load in MkDocs | 0ms (local HTML) | None |
| Image load (R2) | 50-200ms (CF CDN edge) | First load only; cached after |
| PDF download | ~1s with CDN | Acceptable; link opens in new tab |

## Disk Budget

```
Total:       40GB
Reserved:    30GB (Hermes venv, sessions, logs, OS, breathing room)
Available:   ~10GB for wiki content

Space needed (3-year estimate):
  Markdown:  2-5GB  ✅
  Small imgs: 1-2GB ✅
  Git hist:   2-3GB  ✅ (if .gitignore excludes binaries)
  Total:     5-10GB ✅ Fits in budget
```

## Implementation

Existing R2Uploader class at `/opt/data/r2_uploader.py` (or equivalent) already configured with credentials from `.env`. No additional setup needed — integrate at Agent ingest time.
