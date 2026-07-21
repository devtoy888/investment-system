#!/usr/bin/env python3
"""
r2_markdown_report.py — Convert a wiki changelog/fix-plan markdown file into a
beautiful adaptive HTML report and upload BOTH MD + HTML to R2.

WHY THIS SCRIPT EXISTS
----------------------
When the user asks for a "修复文档 / 修复对照记录 / change-log", a plain table is
not enough and a HALF-beautified page is worse than none. Lesson from a session
where only tables + hero were styled and the user had to point out that paragraphs,
lists, bold, and inline code were still raw markdown. This generator renders
EVERY markdown element type so nothing ships unstyled.

Element coverage (do NOT drop any when editing):
  - YAML frontmatter (--- ... ---) is SKIPPED
  - First H1  -> gradient Hero header with 4 auto-extracted stat cards
  - H2/H3     -> section headings (accent left-border / underline)
  - blockquote -> card with accent left border
  - hr (---)  -> divider
  - ordered list (1. )  -> <ol>
  - unordered list (- )  -> <ul>
  - task list (- [ ] / - [x]) -> <ul class=task-list> with disabled checkboxes
  - table     -> styled table with blue header; status column -> colored badge
  - **bold**  -> <strong>
  - `code`    -> <code> (monospace, accent color)
  - standalone bold line -> lead paragraph (accent emphasis)
  - everything -> dark/light adaptive via prefers-color-scheme

Usage:
  python3 r2_markdown_report.py [--md /path/to/changelog.md] [--html-key references/x.html] [--md-key references/x.md]

Requires boto3 + r2_uploader on the active venv (use /opt/hermes/.venv/bin/python3).
R2 credentials are read from environment (see cloudflare-r2 skill).
"""

import os
import sys
import re
import argparse
import datetime
import html as html_module

# ---- Defaults (override via args; env via cloudflare-r2 skill) ----
DEFAULT_MD = "/llm-wiki/docs/wiki-repair-changelog.md"
DEFAULT_MD_KEY = "references/wiki-repair/changelog.md"
DEFAULT_HTML_KEY = "references/wiki-repair/changelog.html"

STAT_LABELS = {
    "js_version": "当前 JS 版本",
    "edges": "图谱边数",
    "done": "已完成项",
    "cron": "Lint Cron ID",
}


def extract_stats(md_text):
    stats = {}
    m = re.search(r"related-pages\.v(\d+)\.js", md_text)
    stats["js_version"] = f"v{m.group(1)}" if m else "—"
    m = re.search(r"(\d+)\s*边", md_text)
    stats["edges"] = m.group(1) if m else "—"
    m = re.search(r"job_id=(\w+)", md_text)
    stats["cron"] = m.group(1) if m else "—"
    stats["done"] = len(re.findall(r"✅", md_text))
    stats["pending"] = len(re.findall(r"⏳", md_text))
    return stats


def inline(text):
    """Render inline markdown: escape HTML first, then `code` and **bold**."""
    text = html_module.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text


def badge_cell(text):
    text = text.strip()
    if "✅" in text:
        return '<span class="badge badge-done">✅ 完成</span>'
    if "⏳" in text:
        return '<span class="badge badge-pending">⏳ 待办</span>'
    if "❌" in text:
        return '<span class="badge badge-fail">❌ 失败</span>'
    return inline(text)


def md_to_html(md_text):
    lines = md_text.split("\n")
    stats = extract_stats(md_text)

    # Skip YAML frontmatter (--- ... ---)
    if lines and lines[0].strip() == "---":
        end = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end = i
                break
        if end > 0:
            lines = lines[end + 1:]

    out = []
    i = 0
    n = len(lines)
    first_h1 = True

    def flush_list(buf, ordered):
        if not buf:
            return
        tag = "ol" if ordered else "ul"
        cls = ' class="task-list"' if (not ordered and any(b.startswith("[ ]") or b.startswith("[x]") for b in buf)) else ""
        out.append(f"<{tag}{cls}>")
        for item in buf:
            m = re.match(r"^\[( |x|X)\]\s+(.*)", item)
            if m:
                checked = "checked" if m.group(1).lower() == "x" else ""
                out.append(f'<li class="task-item"><input type="checkbox" disabled {checked}> {inline(m.group(2))}</li>')
            else:
                out.append(f"<li>{inline(item)}</li>")
        out.append(f"</{tag}>")

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Table
        if stripped.startswith("|") and "|" in stripped[1:]:
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                r = lines[i].strip()
                if re.match(r"^\|[\s:|-]+\|$", r):
                    i += 1
                    continue
                rows.append([c.strip() for c in r.strip("|").split("|")])
                i += 1
            if rows:
                out.append('<div class="table-wrap"><table>')
                out.append("<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in rows[0]) + "</tr></thead>")
                out.append("<tbody>")
                for row in rows[1:]:
                    tds = ""
                    for c in row:
                        if "✅" in c or "⏳" in c or "❌" in c:
                            tds += f'<td class="status-col">{badge_cell(c)}</td>'
                        else:
                            tds += f"<td>{inline(c)}</td>"
                    out.append(f"<tr>{tds}</tr>")
                out.append("</tbody></table></div>")
            continue

        if stripped.startswith("# "):
            if first_h1:
                first_h1 = False
                out.append(f'''<header class="hero">
  <div class="hero-inner">
    <div class="hero-badge">🔧 系统修复报告</div>
    <h1>{inline(stripped[2:])}</h1>
    <p class="hero-sub">LLM Wiki 全面评估后的架构层 / 导航层 / 视觉层修复记录</p>
    <div class="stat-grid">
      <div class="stat-card"><div class="stat-num">{stats['js_version']}</div><div class="stat-label">{STAT_LABELS['js_version']}</div></div>
      <div class="stat-card"><div class="stat-num">{stats['edges']}</div><div class="stat-label">{STAT_LABELS['edges']}</div></div>
      <div class="stat-card"><div class="stat-num">{stats['done']}</div><div class="stat-label">{STAT_LABELS['done']}</div></div>
      <div class="stat-card"><div class="stat-num" style="font-size:0.75em">{stats['cron'][:8]}</div><div class="stat-label">{STAT_LABELS['cron']}</div></div>
    </div>
  </div>
</header>''')
            else:
                out.append(f'<h1 class="section-title">{inline(stripped[2:])}</h1>')
            i += 1
            continue
        if stripped.startswith("## "):
            out.append(f'<h2 class="h2">{inline(stripped[3:])}</h2>')
            i += 1
            continue
        if stripped.startswith("### "):
            out.append(f'<h3 class="h3">{inline(stripped[4:])}</h3>')
            i += 1
            continue
        if stripped.startswith("> "):
            quote = []
            while i < n and lines[i].strip().startswith("> "):
                quote.append(lines[i].strip()[2:])
                i += 1
            out.append(f'<blockquote>{"".join(inline(q) for q in quote)}</blockquote>')
            continue
        if stripped == "---":
            out.append('<hr class="divider">')
            i += 1
            continue
        if re.match(r"^- ", stripped):
            buf = []
            while i < n and re.match(r"^- ", lines[i].strip()):
                buf.append(lines[i].strip()[2:])
                i += 1
            flush_list(buf, False)
            continue
        if re.match(r"^\d+\.\s+", stripped):
            buf = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                buf.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            flush_list(buf, True)
            continue
        if stripped == "":
            i += 1
            continue
        if re.match(r"^\*\*.+\*\*$", stripped):
            out.append(f'<p class="lead">{inline(stripped)}</p>')
        else:
            out.append(f"<p>{inline(stripped)}</p>")
        i += 1

    body = "\n".join(out)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Wiki 修复对照记录</title>
<style>
:root {{
  --bg: #f4f6fb; --card: #ffffff; --text: #1a1f36; --text-light: #6b7280;
  --primary: #3949ab; --primary-dark: #1a237e; --primary-light: #e8eaf6;
  --border: #e5e7eb; --shadow: 0 2px 12px rgba(0,0,0,0.06);
  --green: #2e7d32; --green-bg: #e8f5e9; --orange: #e65100; --orange-bg: #fff3e0; --red: #c62828; --red-bg: #ffebee;
  --code-bg: #f3f4f6;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #0f1117; --card: #1a1d27; --text: #e4e7ed; --text-light: #9aa0ac;
    --primary: #5c6bc0; --primary-dark: #3949ab; --primary-light: #232838;
    --border: #2a2e3a; --shadow: 0 2px 12px rgba(0,0,0,0.3);
    --green: #66bb6a; --green-bg: #1b2e1c; --orange: #ffa726; --orange-bg: #2e2415; --red: #ef5350; --red-bg: #2e1b1b;
    --code-bg: #232838;
  }}
}}
* {{ box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif; max-width: 960px; margin: 0 auto; padding: 0 16px 60px; background: var(--bg); color: var(--text); line-height: 1.7; }}
.hero {{ margin: 24px 0 32px; border-radius: 18px; overflow: hidden; background: linear-gradient(135deg, var(--primary-dark), var(--primary)); box-shadow: 0 8px 32px rgba(57,73,171,0.25); }}
.hero-inner {{ padding: 36px 32px 32px; }}
.hero-badge {{ display: inline-block; padding: 4px 14px; border-radius: 20px; background: rgba(255,255,255,0.18); color: #fff; font-size: 0.82em; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 14px; }}
.hero h1 {{ color: #fff; font-size: 1.9em; margin: 0 0 8px; font-weight: 700; }}
.hero-sub {{ color: rgba(255,255,255,0.85); margin: 0 0 24px; font-size: 0.98em; }}
.stat-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }}
.stat-card {{ background: rgba(255,255,255,0.12); border-radius: 12px; padding: 16px 12px; text-align: center; backdrop-filter: blur(4px); }}
.stat-num {{ color: #fff; font-size: 1.5em; font-weight: 700; line-height: 1.2; }}
.stat-label {{ color: rgba(255,255,255,0.8); font-size: 0.75em; margin-top: 4px; }}
.section-title {{ color: var(--primary); font-size: 1.5em; margin: 36px 0 16px; padding-bottom: 10px; border-bottom: 2px solid var(--primary-light); }}
.h2 {{ color: var(--primary); font-size: 1.3em; margin: 28px 0 12px; padding-left: 12px; border-left: 4px solid var(--primary); }}
.h3 {{ color: var(--text); font-size: 1.1em; margin: 20px 0 10px; }}
p {{ margin: 10px 0; }}
.lead {{ font-weight: 600; color: var(--primary); margin: 18px 0 10px; font-size: 1.02em; }}
strong {{ color: var(--text); font-weight: 700; }}
code {{ background: var(--code-bg); padding: 2px 6px; border-radius: 4px; font-family: "SF Mono", "Fira Code", Consolas, monospace; font-size: 0.88em; color: var(--primary); }}
blockquote {{ background: var(--card); border-left: 4px solid var(--primary); padding: 14px 18px; margin: 16px 0; border-radius: 0 10px 10px 0; box-shadow: var(--shadow); color: var(--text-light); font-size: 0.92em; }}
ul, ol {{ margin: 12px 0; padding-left: 24px; }}
li {{ margin: 6px 0; }}
.task-list {{ list-style: none; padding-left: 4px; }}
.task-item {{ display: flex; align-items: flex-start; gap: 8px; }}
.task-item input {{ margin-top: 5px; flex-shrink: 0; accent-color: var(--primary); }}
.table-wrap {{ overflow-x: auto; margin: 18px 0; border-radius: 12px; box-shadow: var(--shadow); }}
table {{ border-collapse: collapse; width: 100%; background: var(--card); font-size: 0.88em; min-width: 520px; }}
thead th {{ background: var(--primary); color: #fff; font-weight: 600; padding: 12px 14px; text-align: left; white-space: nowrap; }}
thead th:first-child {{ border-top-left-radius: 12px; }}
thead th:last-child {{ border-top-right-radius: 12px; }}
tbody td {{ padding: 11px 14px; border-bottom: 1px solid var(--border); }}
tbody tr:last-child td {{ border-bottom: none; }}
tbody tr:hover {{ background: var(--primary-light); }}
.status-col {{ white-space: nowrap; }}
.badge {{ display: inline-block; padding: 3px 12px; border-radius: 14px; font-size: 0.82em; font-weight: 600; white-space: nowrap; }}
.badge-done {{ background: var(--green-bg); color: var(--green); }}
.badge-pending {{ background: var(--orange-bg); color: var(--orange); }}
.badge-fail {{ background: var(--red-bg); color: var(--red); }}
.divider {{ border: none; border-top: 1px solid var(--border); margin: 28px 0; }}
footer {{ text-align: center; color: var(--text-light); font-size: 0.82em; margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--border); }}
@media (max-width: 640px) {{
  .stat-grid {{ grid-template-columns: repeat(2, 1fr); }}
  .hero-inner {{ padding: 28px 20px 24px; }}
  .hero h1 {{ font-size: 1.5em; }}
  body {{ padding: 0 12px 40px; }}
}}
</style>
</head>
<body>
{body}
<footer>
  最后更新: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} · 自动生成 · DevToy Wiki 修复记录
</footer>
</body>
</html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", default=DEFAULT_MD)
    ap.add_argument("--md-key", default=DEFAULT_MD_KEY)
    ap.add_argument("--html-key", default=DEFAULT_HTML_KEY)
    args = ap.parse_args()

    for v in ("R2_ACCOUNT_ID", "R2_BUCKET", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_PUBLIC_URL"):
        if v not in os.environ:
            print(f"ERROR: env {v} not set (load cloudflare-r2 env first)")
            sys.exit(1)

    try:
        from r2_uploader import R2Uploader
    except ImportError:
        print("ERROR: r2_uploader not found")
        sys.exit(1)

    md_text = open(args.md, "r", encoding="utf-8").read()
    uploader = R2Uploader()

    url_md = uploader.upload_file(args.md, args.md_key, content_type="text/plain; charset=utf-8")
    print(f"MD uploaded: {url_md}")

    html_content = md_to_html(md_text)
    uploader.s3.put_object(
        Bucket=uploader.bucket_name,
        Key=args.html_key,
        Body=html_content.encode("utf-8"),
        ContentType="text/html; charset=utf-8",
    )
    url_html = f"{os.environ['R2_PUBLIC_URL']}/{args.html_key}"
    print(f"HTML uploaded: {url_html}")


if __name__ == "__main__":
    main()
