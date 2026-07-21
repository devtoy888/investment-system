#!/usr/bin/env python3
"""
14:30决策推送 — 规则引擎+AI解释 → QQ(待办清单) + R2(完整报告)
数据管线:
  execute_today_plan.py → 规则引擎输出(板块代理估算+策略标签)
  llm_analysis_v2.py → AI深度分析(基于完整数据+策略信号)
  自校验 → 交叉验证数据/策略/覆盖率
"""
import subprocess, sys, os, re, io
from datetime import date, datetime, timedelta
from pathlib import Path

os.chdir('/opt/data')
sys.path.insert(0, '/opt/data/scripts')

# ══════════════════════════════════════════
# 1. 规则引擎 → 操作建议
# ══════════════════════════════════════════
r = subprocess.run([sys.executable, '/opt/data/scripts/execute_today_plan.py'],
                   capture_output=True, text=True, timeout=300)
for l in (r.stderr or '').strip().split('\n'):
    if l.strip() and not l.startswith('['):
        print(l, file=sys.stderr)

# Stdout: 校验行 + 操作建议
stdout = r.stdout.strip()
advice_lines = [l for l in stdout.split('\n') if not l.startswith('[')]
advice = '\n'.join(advice_lines).strip()
if not advice:
    print("⚠️ 规则引擎未输出", file=sys.stderr); sys.exit(1)

# ══════════════════════════════════════════
# 2. AI深度分析
# ══════════════════════════════════════════
today = date.today()
analysis = ""

try:
    # 构建包含板块代理数据的完整上下文
    summary_dir = "/tmp/fund_data"
    ctx_parts = []
    for fname in ['_noon_market.txt', '_noon_sector.txt', '_noon_volume.txt',
                  '_noon_northbound.txt', '_noon_overview.txt', '_noon_rss.txt']:
        fp = f"{summary_dir}/{fname}"
        if os.path.exists(fp):
            c = open(fp).read().strip()
            if c: ctx_parts.append(f"【{fname.replace('_noon_','').replace('.txt','')}】\n{c[:800]}")

    # 从操作建议提取策略决策依据
    strategy_section = []
    for l in advice.split('\n'):
        if '[' in l and ']' in l and ('回撤' in l or '建仓' in l or '科技' in l or '安全' in l or '趋势' in l):
            strategy_section.append(l.strip())

    from llm_analysis_v2 import call_ds

    prompt = f"""你是一位A股基金首席分析师。现在是14:30，用户的基金经理需要理解今日操作策略。

基于以下市场数据和策略引擎输出的操作建议，用结构化分析解释：
1.【市场定性】今日行情一句话定性
2.【核心策略】为什么今日主要操作是「持有观望」？策略依据是什么？
3.【操作解读】逐条解释每支基金的操作逻辑（3-5条核心的，不用全列）
4.【风险提示】明日最需要注意的1-2个风险

要求：专业、简洁、有数据支撑。不要列清单，要讲逻辑。

【今日市场】
{chr(10).join(ctx_parts)[:2000]}

【策略引擎输出（带策略标签）】
{chr(10).join(strategy_section)}"""

    ai_text = call_ds(prompt, "", max_tokens=2000, temp=0.3)
    if ai_text:
        analysis = ai_text.replace('<br>', '\n').replace('<br/>', '\n')
except Exception as e:
    print(f"[AI] {type(e).__name__}", file=sys.stderr)

# ══════════════════════════════════════════
# 3. 构建输出
# ══════════════════════════════════════════
from push_report_r2 import push_report
from send_qqbot import _output

report_type = "decision"
title = f"基金决策 · 14:30 · {today}"

# ── R2完整报告（数据+操作表+AI分析）──
data_sections = []
for fname in ['_noon_market.txt', '_noon_sector.txt', '_noon_volume.txt',
              '_noon_northbound.txt', '_noon_overview.txt']:
    fp = f"{summary_dir}/{fname}"
    if os.path.exists(fp):
        c = open(fp).read().strip()
        label = fname.replace('_noon_','').replace('.txt','')
        label_map = {'market':'盘中行情','sector':'板块表现','volume':'量价分析','northbound':'北向资金','overview':'市场总览','rss':'市场新闻'}
        label = label_map.get(label, label)
        if c: data_sections.append(f"## {label}\n{c}")

data_tables = '\n\n'.join(data_sections)
full_report = data_tables + '\n\n## 操作建议（策略引擎）\n\n' + advice
if analysis:
    full_report += '\n\n## AI 策略解读\n\n' + analysis

# 静默上传
old_stdout = sys.stdout
sys.stdout = io.StringIO()
try:
    md, html = push_report(report_type, title, data_tables + '\n\n## 操作建议\n\n' + advice, analysis)
finally:
    sys.stdout = old_stdout

# ── QQ待办清单 ──
qq = [f"📊 {today.strftime('%m/%d')} 14:30 决策"]

# 市场快照（从advice中提取）
for l in advice.split('\n'):
    if l.startswith(('📊', '🔥', '🌊')):
        qq.append(l)

# 操作表（精简：只取有动作的+建仓的）
qq.append("")
qq.append("🎯 操作清单")
for l in advice.split('\n'):
    s = l.strip()
    if s.startswith('|') and ('📉' in s or '📈' in s):
        cells = [c.strip() for c in s.split('|')]
        if len(cells) >= 5:
            qq.append(f"• {cells[1][:14]} → {cells[3][:14]}")
    elif s.startswith('|') and '建仓双轨' in s:
        cells = [c.strip() for c in s.split('|')]
        if len(cells) >= 5:
            qq.append(f"• {cells[1][:14]} → {cells[3][:14]}(建仓)")

# 策略一句话
qq.append("")
qq.append("📌 回撤阶梯优先: 深套>25%不割，等待反弹")

# AI一句话
if analysis:
    first = analysis.split('\n\n')[0].replace('**','').replace('##','').replace('\n',' ').strip()[:150]
    qq.append(f"")
    qq.append(f"💡 {first}")

# 链接
qq.append("")
qq.append(f"📄 {md}")
qq.append(f"🌐 {html}")

_output('\n'.join(qq))
