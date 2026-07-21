#!/usr/bin/env python3
"""
Pre-collect data for the daily tech report (v3 - all 4 sources).
Runs before the cron agent so data is ready.
Outputs: parsed summary files to /tmp/_*_summary.txt
And: Generates briefing image via generate_news_card_v3.py
"""
import subprocess, json, os, re, sys, datetime, random, urllib.request

DATA_DIR = '/tmp'

def weixin_warmup():
    """Send a silent getConfig request to WeChat iLink to refresh the session."""
    token = os.environ.get('WEIXIN_TOKEN', '')
    base_url = os.environ.get('WEIXIN_BASE_URL', 'https://ilinkai.weixin.qq.com').rstrip('/')
    if not token:
        return
    body = json.dumps({"base_info": {"channel_version": "0.1.25"}})
    headers = {
        "Content-Type": "application/json",
        "AuthorizationType": "ilink_bot_token",
        "Authorization": f"Bearer {token}",
        "X-WECHAT-UIN": str(random.randint(1000000000, 9999999999)),
        "iLink-App-Id": "wx_bot_sdk",
        "iLink-App-ClientVersion": "0.1.25",
    }
    try:
        req = urllib.request.Request(
            f"{base_url}/ilink/bot/getconfig",
            data=body.encode('utf-8'),
            headers=headers,
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
        print(f"  WeChat session warmup: {result.get('ret', 'ok')}")
    except Exception as e:
        print(f"  WeChat warmup skipped: {e}")

# ── WeChat session warmup ──
weixin_warmup()

def fetch(url, output_file, headers=None):
    cmd = ['curl', '-sL', url, '-o', output_file]
    if headers:
        for h in headers:
            cmd.extend(['-H', h])
    subprocess.run(cmd, timeout=20)

# 1. V2EX
fetch('https://www.v2ex.com/api/topics/hot.json', f'{DATA_DIR}/_v2ex.json')
try:
    v2ex = json.load(open(f'{DATA_DIR}/_v2ex.json'))
    with open(f'{DATA_DIR}/_v2ex_summary.txt', 'w') as f:
        for t in v2ex[:10]:
            tid = t.get('id', '')
            f.write(f'{t["title"]}|https://www.v2ex.com/t/{tid}|{t.get("node",{}).get("title","?")}|{t.get("replies",0)}条回复\n')
except: pass

# 2. Hacker News
fetch('https://news.ycombinator.com/', f'{DATA_DIR}/_hn.html',
      headers=['User-Agent: Mozilla/5.0'])
try:
    with open(f'{DATA_DIR}/_hn.html') as f:
        content = f.read()
    ids = re.findall(r'class="athing submission" id="(\d+)"', content)
    with open(f'{DATA_DIR}/_hn_summary.txt', 'w') as f:
        for mid in ids[:10]:
            tm = re.search(rf'id="{mid}".*?<span class="titleline"><a[^>]*>([^<]+)</a>', content, re.DOTALL)
            title = tm.group(1).replace('&#x27;',"'").replace('&amp;','&') if tm else 'N/A'
            sc = re.search(rf'score_{mid}">(\d+)', content)
            score = sc.group(1) if sc else '?'
            cm = re.search(rf'item\?id={mid}">(\d+)&nbsp;', content)
            comments = cm.group(1) if cm else 'discuss'
            f.write(f'{title}|https://news.ycombinator.com/item?id={mid}|↑{score}分|{comments}条评论\n')
except: pass

# 3. GitHub trending
fetch('https://api.github.com/search/repositories?q=created:>' +
      (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d') +
      '&sort=stars&order=desc&per_page=10',
      f'{DATA_DIR}/_gh.json',
      headers=['Accept: application/vnd.github+json', 'User-Agent: curl-agent'])
try:
    gh = json.load(open(f'{DATA_DIR}/_gh.json'))
    with open(f'{DATA_DIR}/_gh_summary.txt', 'w') as f:
        for r in gh.get('items', [])[:10]:
            lang = r.get('language') or '?'
            desc = (r.get('description') or '')[:100]
            f.write(f'{r["full_name"]}|https://github.com/{r["full_name"]}|⭐{r["stargazers_count"]}|{lang}|{desc}\n')
except: pass

# 4. Bilibili
fetch('https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all',
      f'{DATA_DIR}/_bili.json',
      headers=['User-Agent: agent-reach/1.0', 'Referer: https://www.bilibili.com'])
try:
    bili = json.load(open(f'{DATA_DIR}/_bili.json'))
    with open(f'{DATA_DIR}/_bili_summary.txt', 'w') as f:
        for v in bili.get('data', {}).get('list', [])[:10]:
            bvid = v.get("bvid", "")
            f.write(f'{v.get("title","N/A").strip()}|{v.get("owner",{}).get("name","?")}|{v.get("stat",{}).get("view",0)}播放|{bvid}\n')
except: pass

# 5. Generate image card (v3 - all 4 sources)
try:
    v2ex = json.load(open(f'{DATA_DIR}/_v2ex.json'))
    gh = json.load(open(f'{DATA_DIR}/_gh.json'))
    bili = json.load(open(f'{DATA_DIR}/_bili.json'))

    v2ex_titles = [t['title'] for t in v2ex[:8]]
    gh_names = [r['full_name'] + ' — ⭐' + str(r['stargazers_count']) for r in gh.get('items', [])[:8]]

    hn_titles = []
    try:
        with open(f'{DATA_DIR}/_hn_summary.txt') as f:
            for line in f.readlines()[:8]:
                parts = line.strip().split('|')
                hn_titles.append(parts[0] if parts else '')
    except: pass

    bili_titles = []
    try:
        with open(f'{DATA_DIR}/_bili_summary.txt') as f:
            for line in f.readlines()[:8]:
                parts = line.strip().split('|')
                bili_titles.append(parts[0] if parts else '')
    except: pass

    summaries = []
    if v2ex_titles:
        summaries.append(f'V2EX: {v2ex[0]["title"][:40]}…等{v2ex[0].get("replies",0)}条回复')
    if hn_titles:
        summaries.append(f'HN: {hn_titles[0][:40]}')
    if gh_names:
        summaries.append(f'GitHub: {gh["items"][0]["full_name"]} ⭐{gh["items"][0]["stargazers_count"]}')

    cmd = ['/opt/hermes/.venv/bin/python3', '/opt/data/skills/devops/cloudflare-r2/scripts/generate_news_card.py',
           '--date=' + datetime.datetime.now().strftime('%Y-%m-%d'),
           '--v2ex'] + v2ex_titles
    if hn_titles:
        cmd += ['--hn'] + hn_titles
    if gh_names:
        cmd += ['--github'] + gh_names
    if bili_titles:
        cmd += ['--bilibili'] + bili_titles
    if summaries:
        cmd += ['--summary'] + summaries
    cmd += ['--upload']

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    for line in result.stdout.splitlines():
        if line.startswith('URL='):
            url = line.split('=', 1)[1]
            print(f'R2_URL={url}')
            with open(f'{DATA_DIR}/_r2_url.txt', 'w') as f:
                f.write(url)
    local_path = '/tmp/daily-card.png'
    if os.path.exists(local_path):
        with open(f'{DATA_DIR}/_image_path.txt', 'w') as f:
            f.write(local_path)
except Exception as e:
    print(f'Image generation skipped: {e}', file=sys.stderr)

print('Data collection complete.')

# ---------------------------------------------------------------------------
# 生成 Markdown 报告并直发 QQ（绕过 Hermes deliver=qqbot 的 markdown 降级路径）
# 复用已采集好的 _*_summary.txt，纯脚本拼报告，不依赖 Agent。
# ---------------------------------------------------------------------------
def _read_summary(name):
    path = f'{DATA_DIR}/{name}'
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [ln.strip() for ln in f if ln.strip()]


def build_report_md():
    """从 _*_summary.txt 拼出 ≤3800 字符的 Markdown 报告。"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    blocks = [f'# 📰 行业技术日报 · {today}', '']

    sources = [
        ('V2EX', '_v2ex_summary.txt', '▸ V2EX 热帖'),
        ('Hacker News', '_hn_summary.txt', '▸ Hacker News 热门'),
        ('GitHub', '_gh_summary.txt', '▸ GitHub 趋势'),
        ('Bilibili', '_bili_summary.txt', '▸ Bilibili 热门'),
    ]
    for label, fname, header in sources:
        rows = _read_summary(fname)[:8]
        if not rows:
            continue
        blocks.append(f'## {header}')
        for row in rows:
            parts = [p.strip() for p in row.split('|')]
            if len(parts) < 2:
                continue
            title = parts[0]
            url = parts[1] if len(parts) > 1 else ''
            tail = ' | '.join(parts[2:]) if len(parts) > 2 else ''
            if url.startswith('http'):
                line = f'- [{title}]({url})'
            else:
                line = f'- {title}'
            if tail:
                line += f' | {tail}'
            blocks.append(line)
        blocks.append('')

    # 今日摘要（从 _r2_url 之外的 summary 聚合，这里用各源首条做轻量摘要）
    blocks.append('## ▸ 今日摘要')
    for label, fname, _ in sources:
        rows = _read_summary(fname)[:3]
        for row in rows:
            parts = [p.strip() for p in row.split('|')]
            if parts:
                blocks.append(f'- {label}：{parts[0][:30]}')
    blocks.append('')

    md = '\n'.join(blocks)
    # 硬截断到 3800，避免 QQ 切分破坏 markdown
    if len(md) > 3800:
        md = md[:3800].rsplit('\n', 1)[0]
    return md


def send_report():
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import qq_markdown_send as q
        md = build_report_md()
        if not md.strip():
            print('[qq] 报告为空，跳过发送', file=sys.stderr)
            return
        n = q.send_markdown_to_default_qq(md)
        print(f'[qq] 已发送 {n} 条行业技术日报到 QQ')
    except Exception as e:
        print(f'[qq] 发送失败：{e}', file=sys.stderr)


send_report()
