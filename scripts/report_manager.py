#!/usr/bin/env python3
"""报告管理系统 — 结构化存储 + 索引 + 复盘分析"""
import sys, os, json, re, subprocess
from pathlib import Path
from datetime import date, datetime
from typing import Optional

sys.path.insert(0, '/opt/data/scripts')

DATA_DIR = Path("/opt/data/fund_system_data")
REPORT_DIR = DATA_DIR / "reports"
INDEX_PATH = REPORT_DIR / "index.json"
BASE_URL = "https://hermes-main-media.devtoy.xyz/fund-system/reports"

# ═══════════════════════════════════════════════
# 1. 标准化存储
# ═══════════════════════════════════════════════

def report_paths(report_type: str, dt: date = None) -> dict:
    """生成标准化的文件路径（按年/月/日组织）"""
    dt = dt or date.today()
    subdir = f"{dt.year}/{dt.month:02d}/{dt.day:02d}"
    local_subdir = REPORT_DIR / subdir
    local_subdir.mkdir(parents=True, exist_ok=True)
    
    return {
        "local_md": str(local_subdir / f"{report_type}.md"),
        "local_html": str(local_subdir / f"{report_type}.html"),
        "r2_md": f"fund-system/reports/{subdir}/{report_type}.md",
        "r2_html": f"fund-system/reports/{subdir}/{report_type}.html",
        "url_md": f"{BASE_URL}/{subdir}/{report_type}.md",
        "url_html": f"{BASE_URL}/{subdir}/{report_type}.html",
        "date": dt.isoformat(),
        "type": report_type,
    }

def save_and_upload(report_type: str, title: str, data_tables: str, analysis: str) -> dict:
    """标准化保存+上传报告，更新索引"""
    paths = report_paths(report_type)
    
    full_md = f"# {title}\n\n{data_tables}\n\n## 🤖 AI 深度分析\n\n{analysis}"
    
    # Save locally
    with open(paths["local_md"], 'w', encoding='utf-8') as f:
        f.write(full_md)
    
    # Upload to R2
    _upload(paths["local_md"], paths["r2_md"])
    
    # Generate and upload HTML
    html = _build_html(full_md, title)
    with open(paths["local_html"], 'w', encoding='utf-8') as f:
        f.write(html)
    _upload(paths["local_html"], paths["r2_html"], "text/html; charset=utf-8")
    
    # Update index
    _update_index(paths, title, len(analysis), data_tables[:100])
    
    return paths

def _upload(local: str, r2_key: str, ct: str = None):
    """上传文件到R2"""
    ct = ct or ("text/markdown; charset=utf-8" if r2_key.endswith('.md') else "text/html; charset=utf-8")
    subprocess.run(
        [sys.executable, '-c', f'''
import sys; sys.path.insert(0, "/opt/data/scripts")
from fund_tools import upload_to_r2 as up
up("{local}", "{r2_key}", "{ct}")
'''],
        capture_output=True, text=True, timeout=30
    )

# ═══════════════════════════════════════════════
# 2. 报告索引
# ═══════════════════════════════════════════════

def _update_index(paths: dict, title: str, analysis_len: int, snippet: str):
    """维护报告索引JSON"""
    index = {"reports": [], "last_updated": datetime.now().isoformat()}
    if INDEX_PATH.exists():
        try:
            index = json.loads(INDEX_PATH.read_text())
        except:
            pass
    
    entry = {
        "type": paths["type"],
        "date": paths["date"],
        "title": title,
        "url_md": paths["url_md"],
        "url_html": paths["url_html"],
        "size": analysis_len,
        "created": datetime.now().isoformat(),
    }
    
    # Remove old entry for same type+date
    index["reports"] = [r for r in index["reports"] 
                       if not (r["type"] == paths["type"] and r["date"] == paths["date"])]
    index["reports"].append(entry)
    index["last_updated"] = datetime.now().isoformat()
    
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
    _upload(str(INDEX_PATH), "fund-system/reports/index.json")
    
    # Also generate monthly archive page
    _generate_monthly_archive(paths["date"])

def get_index() -> list:
    """读取报告索引"""
    if INDEX_PATH.exists():
        return json.loads(INDEX_PATH.read_text()).get("reports", [])
    return []

def query_reports(report_type: str = None, days: int = 30) -> list:
    """查询报告历史"""
    all_reports = get_index()
    cutoff = date.today().isoformat()
    results = [r for r in all_reports if r["date"] >= cutoff]
    if report_type:
        results = [r for r in results if r["type"] == report_type]
    return sorted(results, key=lambda x: x["date"], reverse=True)

# ═══════════════════════════════════════════════
# 3. 复盘分析工具
# ═══════════════════════════════════════════════

def extract_predictions(md_content: str) -> list:
    """从报告中提取预测/判断"""
    predictions = []
    for line in md_content.split('\n'):
        # Match patterns like "方向判断：看多" or "预期：跌" or "判断：准确"
        match = re.search(r'(方向判断|预测|预期|判断)[：:]\s*(.+?)(?:[。，]|\n|$)', line)
        if match:
            predictions.append({
                "type": match.group(1),
                "content": match.group(2).strip(),
                "line": line.strip()[:80]
            })
    return predictions

def extract_fund_ops(md_content: str) -> list:
    """从报告中提取基金操作建议"""
    ops = []
    for line in md_content.split('\n'):
        # Match fund codes (6 digits) + operation keywords
        if re.search(r'\d{6}', line) and any(kw in line for kw in ['加仓', '减仓', '清仓', '持有', '观望', '买入', '卖出']):
            ops.append(line.strip()[:120])
    return ops

def analyze_trend(report_type: str, days: int = 30) -> dict:
    """分析某类报告的趋势数据"""
    reports = query_reports(report_type, days)
    total_predictions = 0
    buy_signals = 0
    sell_signals = 0
    hold_signals = 0
    
    for r in reports:
        try:
            md = Path(r.get("local_md", "")).read_text() if r.get("local_md") else ""
        except:
            md = ""
        
        if md:
            ops = extract_fund_ops(md)
            for op in ops:
                if '加仓' in op or '买入' in op:
                    buy_signals += 1
                elif '减仓' in op or '清仓' in op or '卖出' in op:
                    sell_signals += 1
                elif '持有' in op or '观望' in op:
                    hold_signals += 1
            total_predictions += len(extract_predictions(md))
    
    return {
        "report_type": report_type,
        "days": days,
        "report_count": len(reports),
        "total_predictions": total_predictions,
        "buy_signals": buy_signals,
        "sell_signals": sell_signals,
        "hold_signals": hold_signals,
    }

# ═══════════════════════════════════════════════
# 4. 月度归档页面
# ═══════════════════════════════════════════════

def _generate_monthly_archive(dt_str: str):
    """生成月度归档HTML"""
    dt = date.fromisoformat(dt_str)
    year, month = dt.year, dt.month
    
    reports = get_index()
    monthly = [r for r in reports if r["date"].startswith(f"{year}-{month:02d}")]
    
    if not monthly:
        return
    
    calendar = {}
    for r in monthly:
        day = r["date"].split('-')[2]
        if day not in calendar:
            calendar[day] = []
        calendar[day].append(r)
    
    rows = ""
    for day in sorted(calendar.keys(), reverse=True):
        day_reports = calendar[day]
        links = " ".join(
            f'<a href="{r["url_html"]}" class="tag-{r["type"]}">{r["type"]}</a>'
            for r in day_reports
        )
        rows += f"""
        <tr>
            <td>{year}-{month:02d}-{day}</td>
            <td>{links}</td>
            <td><small>{' · '.join(r.get('title','')[:30] for r in day_reports[:3])}</small></td>
        </tr>"""
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>报告归档 · {year}年{month}月</title>
<style>
body {{ font-family: -apple-system,'PingFang SC',sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f6fa; color: #333; }}
h1 {{ color: #1a1a2e; border-bottom: 2px solid #4a6cf7; padding-bottom: 10px; }}
table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
th, td {{ padding: 10px 14px; text-align: left; }}
th {{ background: #4a6cf7; color: white; font-size: 13px; }}
tr:nth-child(even) {{ background: #f8f9ff; }}
a {{ text-decoration: none; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin: 0 2px; }}
.tag-morning {{ background: #fff3e0; color: #e65100; }}
.tag-noon {{ background: #e3f2fd; color: #1565c0; }}
.tag-decision {{ background: #fce4ec; color: #c62828; }}
.tag-closing {{ background: #e8f5e9; color: #2e7d32; }}
.tag-weekly {{ background: #f3e5f5; color: #6a1b9a; }}
.tag-verify {{ background: #e0f2f1; color: #00695c; }}
.summary {{ display: flex; gap: 12px; margin: 16px 0; }}
.card {{ flex: 1; background: white; padding: 16px; border-radius: 12px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }}
.card .num {{ font-size: 28px; font-weight: 700; color: #4a6cf7; }}
.card .label {{ font-size: 12px; color: #888; margin-top: 4px; }}
</style>
</head>
<body>
<h1>📊 报告归档 · {year}年{month}月</h1>
<div class="summary">
    <div class="card"><div class="num">{len(monthly)}</div><div class="label">总报告数</div></div>
    <div class="card"><div class="num">{len(calendar)}</div><div class="label">交易日</div></div>
    <div class="card"><div class="num">{len(set(r['type'] for r in monthly))}</div><div class="label">报告类型</div></div>
</div>
<table>
<thead><tr><th>日期</th><th>报告列表</th><th>标题</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</body>
</html>"""
    
    local_path = REPORT_DIR / f"{year}" / f"{month:02d}" / "index.html"
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(html, encoding='utf-8')
    
    r2_key = f"fund-system/reports/{year}/{month:02d}/index.html"
    _upload(str(local_path), r2_key, "text/html; charset=utf-8")

# ═══════════════════════════════════════════════
# 5. HTML渲染（复用之前的）
# ═══════════════════════════════════════════════

def _build_html(md_content: str, title: str) -> str:
    """Markdown → 美观HTML"""
    from html import escape
    escaped = escape(md_content)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{escape(title)}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:#f0f2f5;color:#1a1a2e;line-height:1.8;font-size:15px}}
.header{{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);color:white;padding:28px 20px;text-align:center}}
.header h1{{font-size:22px;font-weight:600;margin-bottom:6px}}
.header .date{{font-size:13px;opacity:0.8}}
.container{{max-width:860px;margin:0 auto;padding:12px}}
.card{{background:white;border-radius:12px;padding:16px 18px;margin-bottom:14px;box-shadow:0 1px 3px rgba(0,0,0,0.06);overflow-x:auto}}
table{{width:100%;border-collapse:collapse;font-size:13px;min-width:480px}}
th,td{{padding:8px 10px;text-align:left;border-bottom:1px solid #eee;white-space:nowrap}}
th{{background:#f8f9fa;color:#666;font-weight:600;font-size:12px}}
tr:hover{{background:#f8f9ff}}
.up{{color:#e74c3c;font-weight:500}}
.down{{color:#27ae60;font-weight:500}}
h2{{font-size:17px;margin:20px 0 12px;padding-bottom:8px;border-bottom:2px solid #e8e8e8}}
h3{{font-size:15px;margin:14px 0 8px;color:#0f3460}}
p{{margin:6px 0}}
hr{{border:none;border-top:1px solid #e0e0e0;margin:20px 0}}
pre{{background:#f8f9fa;padding:12px;border-radius:8px;overflow-x:auto;white-space:pre-wrap;word-break:break-word;font-size:13px}}
.tag{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600}}
@media(max-width:600px){{body{{font-size:14px}}.container{{padding:8px}}table{{font-size:11px;min-width:100%}}th,td{{padding:5px 6px}}}}
</style>
</head>
<body>
<div class="header"><h1>{escape(title)}</h1><div class="date">{date.today().isoformat()}</div></div>
<div class="container"><div class="card"><pre>{escaped}</pre></div></div>
</body>
</html>"""


# ═══════════════════════════════════════════════
# 6. 复盘分析报告
# ═══════════════════════════════════════════════

def generate_review_analysis(days: int = 30) -> str:
    """生成复盘分析报告"""
    reports = get_index()
    recent = [r for r in reports if r["date"] >= (date.today().isoformat())]
    
    lines = [f"# 投资报告复盘分析 · {date.today()}", ""]
    lines.append(f"## 总览")
    lines.append(f"- 共 {len(reports)} 份报告，最近 {days} 天 {len(recent)} 份")
    lines.append("")
    
    # Per-type stats
    types = {}
    for r in recent:
        t = r["type"]
        if t not in types:
            types[t] = {"count": 0, "total_size": 0}
        types[t]["count"] += 1
        types[t]["total_size"] += r.get("size", 0)
    
    lines.append(f"## 各类报告统计")
    lines.append(f"| 类型 | 数量 | 平均字数 |")
    lines.append(f"|:----|:----:|:--------:|")
    for t, stats in sorted(types.items()):
        avg = stats["total_size"] // stats["count"] if stats["count"] > 0 else 0
        lines.append(f"| {t} | {stats['count']} | {avg} |")
    
    lines.append("")
    lines.append(f"## 操作信号趋势")
    for t in types:
        trend = analyze_trend(t, days)
        lines.append(f"### {t}")
        lines.append(f"- 买入信号: {trend['buy_signals']} | 卖出信号: {trend['sell_signals']} | 持有信号: {trend['hold_signals']}")
        lines.append("")
    
    lines.append("---")
    lines.append(f"_自动生成 · 下次运行: 每日08:00_")
    
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["save", "index", "analyze", "archive", "migrate"], nargs="?", default="index")
    parser.add_argument("--type", help="Report type")
    parser.add_argument("--days", type=int, default=30)
    args = parser.parse_args()
    
    if args.action == "index":
        idx = get_index()
        print(f"报告索引: {len(idx)} 条记录")
        for r in idx[-10:]:
            print(f"  {r['date']} {r['type']:12s} {r['url_html']}")
    
    elif args.action == "analyze":
        report = generate_review_analysis(args.days)
        print(report)
    
    elif args.action == "archive":
        # Generate archive for current month
        _generate_monthly_archive(date.today().isoformat())
        print(f"✅ 月度归档已更新")
    
    elif args.action == "migrate":
        # Migrate existing flat files to new structure
        for f in REPORT_DIR.glob("*_*.md"):
            parts = f.stem.split("_")
            if len(parts) >= 2:
                rtype = parts[0]
                try:
                    dt = date.fromisoformat(parts[1])
                    paths = report_paths(rtype, dt)
                    # Copy to new location
                    with open(f) as src:
                        content = src.read()
                    with open(paths["local_md"], 'w') as dst:
                        dst.write(content)
                    print(f"  ✅ {f.name} → {paths['r2_md']}")
                except:
                    pass
        print("迁移完成")
