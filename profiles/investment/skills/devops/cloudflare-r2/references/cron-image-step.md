# Cron Prompt: Image Generation Step (Step 3)

**v3 (recommended):** `/opt/data/generate_news_card_v3.py` — dynamic height, all 4 sources + summary, 8 items/section, compact layout.
**v2:** `/opt/data/generate_news_card_v2.py` — fixed 1200×2400, V2EX+GitHub only, 5 items/section, wasted whitespace. Deprecated.

Copy-paste this block after your data-collection and text-report-generation steps in any cron prompt that needs a picture card.

## Minimal Copy-Paste Block

```
## 步骤3：生成图片简报并上传至 R2

数据收集完毕后，必须同时生成图片版本简报并推送。

注意：使用 `/opt/hermes/.venv/bin/python3` 而非系统 `python3`，因为 boto3 在 venv 中。

执行以下命令生成图片简报并上传到 R2：

```bash
cd /opt/data && \
  /opt/hermes/.venv/bin/python3 generate_news_card_v3.py \
    --date=$(TZ=Asia/Shanghai date +%Y-%m-%d) \
    --time="$(TZ=Asia/Shanghai date '+%H:%M') 北京时间" \
    --v2ex "标题1" "标题2" "标题3" "标题4" "标题5" \
    --hn "标题1" "标题2" "标题3" "标题4" "标题5" \
    --github "仓库1" "仓库2" "仓库3" "仓库4" "仓库5" \
    --summary "摘要1" "摘要2" "摘要3" "摘要4" "摘要5" \
    --upload
```

从脚本输出中提取 `URL=https://...` 地址。

如果图片生成成功，最终输出必须包含：
1. **图片 Markdown 链接**：`![日报图片](R2_URL)`
2. **完整文本日报**

如果图片生成失败（字体缺失、Pillow 未安装、R2 配置问题等），跳过图片步骤，只输出纯文本日报。
```

## Production-Grade Block (with Python inline fallback for complex data)

When the agent needs to pass 5+ items per section (argparse can fail on too many `--v2ex` args), use a Python inline script that reads the saved data files:

```bash
cd /opt/data && /opt/hermes/.venv/bin/python3 -c "
import json, subprocess, datetime

# Load data from /tmp/ (files saved during step 1)
v2ex = json.load(open('/tmp/_v2ex.json'))
gh = json.load(open('/tmp/_gh.json'))

# Extract titles — max 5 per section
v2ex_titles = [t['title'] for t in v2ex[:5]]
gh_names = [r['full_name'] for r in gh.get('items', [])[:5]]

# Build command
cmd = [
    '/opt/hermes/.venv/bin/python3', 'generate_news_card_v3.py',
    '--date=' + datetime.datetime.now().strftime('%Y-%m-%d'),
    '--v2ex'] + v2ex_titles + ['--github'] + gh_names + ['--upload']

result = subprocess.run(cmd, capture_output=True, text=True)
# Print URL line for agent to capture
for line in result.stdout.splitlines():
    if line.startswith('URL='):
        print(line)
"
```

## Required Conditions

- **boto3** must be installed in the Hermes venv: `uv pip install boto3`
- **Pillow** must be installed in the Hermes venv (pre-included)
- **R2 credentials** must be in `r2_uploader.py` or available via env vars
- **Font** `/tmp/DouyinSansBold.otf` must exist (downloaded from 60s-static-host repo)

## Common Failures & Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| `boto3 not found` | System python used instead of venv | Prefix with `/opt/hermes/.venv/bin/` |
| `data["date"] referenced before assignment` | Script bug (v2, fixed) | Use script with `args.date` patch applied |
| `Notification failed: name 'args' is not defined` | Stale push code in create_daily_card() | Remove the notify_service block |
| `HTTP 401: 无效的令牌` | Cron job provider set to `"custom"` not `"custom:provider_name"` | Set `provider: "custom:agnes"` |
| `DingTalk not configured` | config.yaml missing `dingtalk:` section | Add platform config section |
