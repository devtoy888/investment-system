#!/usr/bin/env python3
"""
v2全量验证 — 测试全部7个报告类型，自动评估并上传R2
"""
import sys, os, json, re, time
from pathlib import Path
from datetime import date, datetime

sys.path.insert(0, '/opt/data/scripts')
sys.path.insert(0, '/opt/data')

# 加载API key
env_path = '/opt/data/profiles/investment/.env'
if os.path.exists(env_path):
    for line in open(env_path):
        if line.startswith('DEEPSEEK_API_KEY='):
            os.environ['DEEPSEEK_API_KEY'] = line.split('=', 1)[1].strip()

from llm_analysis_v2 import generate_v2, call_ds
from r2_uploader import R2Uploader

VALIDATION_DIR = Path("/opt/data/fund_system_data/llm_validation")
VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
today = date.today().isoformat()

REPORT_TYPES = ['closing', 'morning', 'noon', 'decision', 'weekly', 'weekend']

EVAL_PROMPT = """评估以下A股分析报告的质量，输出JSON（不要额外文字）：
{"data_accuracy":<1-10>,"logic":<1-10>,"practicality":<1-10>,"conciseness":<1-10>,"risk":<1-10>,"total":<平均分>,"comment":"<短评>","improvement":"<改进建议>"}

报告：
"""

def evaluate(report_type, text):
    """评估报告质量 — 解析5维度评分，总分取平均"""
    prompt = f"""分析报告类型: {report_type}

请对以下报告从5个维度每项评1-10分，按此格式输出(不要多余文字)：
数据准确性=8 逻辑一致性=7 实用性=8 简洁性=9 风险意识=7 评语=XXX

报告内容：
{text[:2000]}"""
    result = call_ds("你是一位评分严格的金融AI质量审核专家，请按格式输出评分。", prompt, max_tokens=400, temp=0.2)
    
    scores = {'data_accuracy': 0, 'logic': 0, 'practicality': 0, 'conciseness': 0, 'risk': 0}
    comment = ""
    
    if result:
        for m in re.finditer(r'(数据准确性|逻辑一致性|实用性|简洁性|风险意识)=(\d+)', result):
            km = {'数据准确性':'data_accuracy','逻辑一致性':'logic','实用性':'practicality','简洁性':'conciseness','风险意识':'risk'}
            scores[km[m.group(1)]] = int(m.group(2))
        cm = re.search(r'评语=([^\n]+)', result)
        if cm:
            comment = cm.group(1).strip()
    
    # 总分 = 5维度平均分，四舍五入到一位小数
    vals = [scores[k] for k in scores]
    avg = sum(vals) / max(len([v for v in vals if v > 0]), 1)
    total = round(avg, 1)
    
    return {**scores, "total": total, "comment": comment}

# ── 运行验证 ──
results = []
for rt in REPORT_TYPES:
    print(f"\n=== 测试 {rt} v2 ===", flush=True)
    analysis = generate_v2(rt, use_cache=False)
    if analysis:
        print(f"  ✅ 长度: {len(analysis)} 字符", flush=True)
        eval_result = evaluate(rt, analysis)
        score = eval_result.get('total', 0)
        print(f"  📊 评分: {score}/10 | {eval_result.get('comment','')[:60]}", flush=True)
        results.append({
            'type': rt,
            'length': len(analysis),
            'score': score,
            'eval': eval_result,
            'text': analysis,
        })
    else:
        print(f"  ❌ 生成失败", flush=True)
        results.append({'type': rt, 'length': 0, 'score': 0, 'error': '生成失败'})

# ── 统计 ──
valid = [r for r in results if r.get('score', 0) > 0]
avg = sum(r['score'] for r in valid) / len(valid) if valid else 0
print(f"\n{'='*50}")
print(f"📊 v2全量验证完成")
for r in results:
    s = f"✅ {r['score']}/10" if r.get('score', 0) >= 6 else f"❌ {r.get('score', 0)}/10"
    print(f"  {r['type']}: {s} ({r.get('length',0)}字符)")
print(f"平均分: {avg:.2f}/10")

# ── 生成报告 ──
md_lines = [
    f"# LLM分析v2 全量验证报告",
    f"",
    f"**日期**: {today}",
    f"**模型**: DeepSeek V4 Flash",
    f"**引擎**: llm_analysis_v2.py (多步推理+完整数据)",
    f"",
    f"---",
    f"",
    f"## 综合统计",
    f"",
    f"| 指标 | 值 |",
    f"|:----|:---:|",
    f"| 报告类型数 | {len(valid)}/{len(REPORT_TYPES)} |",
    f"| 平均分 | {avg:.2f}/10 |",
    f"",
    f"---",
    f"",
]
for r in results:
    rt = r['type']
    if r.get('error'):
        md_lines.append(f"## ❌ {rt} — {r['error']}")
        md_lines.append("")
        continue
    sc = r.get('score', 0)
    ev = r.get('eval', {})
    md_lines.append(f"## 📊 {rt} — {sc}/10")
    md_lines.append("")
    md_lines.append(f"| 维度 | 分数 |")
    md_lines.append(f"|:---|:---:|")
    md_lines.append(f"| 数据准确性 | {ev.get('data_accuracy','?')}/10 |")
    md_lines.append(f"| 逻辑一致性 | {ev.get('logic','?')}/10 |")
    md_lines.append(f"| 实用性 | {ev.get('practicality','?')}/10 |")
    md_lines.append(f"| 简洁性 | {ev.get('conciseness','?')}/10 |")
    md_lines.append(f"| 风险意识 | {ev.get('risk','?')}/10 |")
    md_lines.append(f"| **总分** | **{sc}/10** |")
    md_lines.append("")
    md_lines.append(f"**长度**: {r['length']} 字符")
    md_lines.append("")
    md_lines.append(f"**评语**: {ev.get('comment','')}")
    if ev.get('improvement'):
        md_lines.append(f"**改进**: {ev.get('improvement','')}")
    md_lines.append("")
    md_lines.append(f"### 分析原文")
    md_lines.append("")
    md_lines.append(f"> {r['text'].replace(chr(10), chr(10)+'> ')}")
    md_lines.append("")

md_content = "\n".join(md_lines)

# ── 保存+上传 ──
fname = f"v2_validation_{today}"
md_path = VALIDATION_DIR / f"{fname}.md"
md_path.write_text(md_content, encoding='utf-8')

# HTML内嵌
escaped = md_content.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>v2全量验证报告</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,sans-serif;max-width:800px;margin:0 auto;padding:20px;background:#0d1117;color:#c9d1d9;line-height:1.6}}
table{{border-collapse:collapse;width:100%;margin:15px 0}} th,td{{border:1px solid #30363d;padding:8px 12px}}
th{{background:#161b22}} code{{background:#161b22;padding:2px 6px;border-radius:3px}}
pre{{background:#161b22;padding:15px;border-radius:6px;overflow-x:auto}}
h1,h2,h3{{color:#58a6ff}} a{{color:#58a6ff}}
blockquote{{border-left:3px solid #30363d;margin:10px 0;padding:0 15px;color:#8b949e}}
</style></head>
<body><div id="content">加载中...</div>
<script>const md = `{escaped}`; document.getElementById('content').innerHTML = marked.parse(md);</script>
</body></html>'''
html_path = md_path.with_suffix('.html')
html_path.write_text(html, encoding='utf-8')

u = R2Uploader()
base = "fund-system/llm-validation"
for f in [md_path, html_path]:
    ct = 'text/markdown; charset=utf-8' if f.suffix == '.md' else 'text/html; charset=utf-8'
    u.upload_file(str(f), f'{base}/{f.name}', ct)
    print(f"  ☁️ R2: {base}/{f.name}")

print(f"\n📊 平均分: {avg:.2f}/10")
print(f"📄 报告: {md_path}")
