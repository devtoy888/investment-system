#!/usr/bin/env python3
"""Reconstruct llm_analysis_v2.py from the corrupted file by extracting clean parts and adding fixes."""

ORIG = '/opt/data/scripts/llm_analysis_v2.py'
OUT = '/opt/data/scripts/llm_analysis_v2.py'

# Read original corrupted file
with open(ORIG, 'r') as f:
    lines = f.readlines()

CORRUPTION = '所以所有操作建议必须明确指出'

# Step 1: Filter out ALL corruption lines and their trailing artifacts
clean = []
i = 0
while i < len(lines):
    line = lines[i]
    
    if CORRUPTION in line:
        i += 1
        # Skip the """ \n \n FINANCIAL_THEORY_FRAMEWORK trailing pattern
        if i < len(lines) and lines[i].strip() == '"""':
            i += 1
        if i < len(lines) and lines[i].strip() == '':
            i += 1
            if i < len(lines) and lines[i].strip() == '':
                i += 1
        if i < len(lines) and lines[i].strip() == 'FINANCIAL_THEORY_FRAMEWORK':
            i += 1
        continue
    
    # Also skip standalone FINANCIAL_THEORY_FRAMEWORK artifacts
    if lines[i].strip() == 'FINANCIAL_THEORY_FRAMEWORK':
        # Check if it's an artifact (preceded by blank, not part of a string)
        if i > 0 and lines[i-1].strip() == '':
            i += 1
            continue
    
    clean.append(line)
    i += 1

# Join and apply targeted fixes
text = ''.join(clean)

# Fix 1: T1_FRAMEWORK and FINANCIAL_THEORY_FRAMEWORK were merged
# The original had T1 closing """ followed by FINANCIAL_THEORY_FRAMEWORK = """
# In the corrupted file, the T1 string swallows the FINANCIAL content
# We need to split them

# The T1_FRAMEWORK string ends after "还是仅为明日计划"
# Then FINANCIAL_THEORY_FRAMEWORK starts with "## 【共同约束：金融理论框架】"
# But in the corrupted file, they're merged

# Pattern: the T1_FRAMEWORK last content line is about "15:00截时点的特殊意义"
# followed directly by FINANCIAL content "你的分析应基于以下投资理论框架："

# Fix: split the merged string
old_merged = '''- 如果14:30预判今日是底部，决定加仓 → 按今日收盘净值买入（抄的是今天的底，不是明天的）

你的分析应基于以下投资理论框架：'''

new_split = '''- 如果14:30预判今日是底部，决定加仓 → 按今日收盘净值买入（抄的是今天的底，不是明天的）
- 所以所有操作建议必须明确指出：是在15:00前操作，还是仅为明日计划
"""


FINANCIAL_THEORY_FRAMEWORK = """## 【共同约束：金融理论框架】
你的分析应基于以下投资理论框架：'''

if old_merged in text:
    text = text.replace(old_merged, new_split)
else:
    print("WARNING: Could not find T1/FINANCIAL merge point")
    print("Looking for alternative merge pattern...")
    # Try without the blank line
    alt = '按今日收盘净值买入（抄的是今天的底，不是明天的）\n\n\n你的分析应基于以下投资理论框架：'
    if alt in text:
        text = text.replace(alt, new_split.split('\n\n\n')[0] + '\n"""\n\n\nFINANCIAL_THEORY_FRAMEWORK = """## 【共同约束：金融理论框架】\n你的分析应基于以下投资理论框架：')
        print("Fixed using alt pattern")

# Fix 2: Add BUILDING_FUNDS definition after ALL_FUNDS
# Pattern: ALL_FUNDS ends with ], then blank line, then comment "# DeepSeek API"
old_build = ']\n\n\n# DeepSeek API 调用'
if old_build in text:
    text = text.replace(old_build, "]\n\nBUILDING_FUNDS = {'003096', '013403'}\n\n\n# DeepSeek API 调用")
else:
    print("WARNING: Could not find BUILDING_FUNDS insertion point")

# Fix 3: Add _cache_key function definition before _cache_read
# Pattern: the call_ds function's except clause is missing return None
# and _cache_key function is missing entirely

# Fix call_ds except block - add return None
old_call_ds_except = '        print(f"  ⚠️ DS API: {type(e).__name__}: {str(e)[:100]}", file=sys.stderr)\n\n\n    return'
new_call_ds_except = '        print(f"  ⚠️ DS API: {type(e).__name__}: {str(e)[:100]}", file=sys.stderr)\n        return None\n\n\ndef _cache_key(rt: str) -> str:\n    return'
text = text.replace(old_call_ds_except, new_call_ds_except)

# Fix 4: _cache_write body
text = text.replace(
    'def _cache_write(rt: str, content: str):\n\n\n# 数据加载',
    'def _cache_write(rt: str, content: str):\n    (CACHE_DIR / f"{_cache_key(rt)}.txt").write_text(content, encoding=\'utf-8\')\n\n\n# 数据加载'
)

# Fix 5: get_portfolio_summary return
text = text.replace(
    '        lines.append(f"  {sector}: {sdata[\'count\']}支 {sdata[\'cost\']:.0f}元 ({pct:.0f}%)")\n    \n\n    """读取昨天的预测及验证结果"""',
    '        lines.append(f"  {sector}: {sdata[\'count\']}支 {sdata[\'cost\']:.0f}元 ({pct:.0f}%)")\n    \n    return "\\n".join(lines)\n\n\ndef get_previous_predictions() -> str:\n    """读取昨天的预测及验证结果"""'
)

# Fix 6: get_previous_predictions return
text = text.replace(
    '            lines.append(f"     实际: {p[\'actual_outcome\']}")\n    \n\n    """获取今日KOL观点"""',
    '            lines.append(f"     实际: {p[\'actual_outcome\']}")\n    \n    return "\\n".join(lines)\n\n\ndef get_kol_today() -> str:\n    """获取今日KOL观点"""'
)

# Fix 7: get_kol_today return
text = text.replace(
    '        parts.append(noon_kol[:2000])\n    \n\n# 系统提示词 v2',
    '        parts.append(noon_kol[:2000])\n    \n    return "\\n".join(parts) if parts else ""\n\n\n# 系统提示词 v2'
)

# Fix 8: All 5 prompt constants got merged. We need to split them.
# The prompts all follow the pattern:
#   XXX_PROMPT_V2 = T1_FRAMEWORK + "\n" + FINANCIAL_THEORY_FRAMEWORK + "\n" + """..."""
# In the corrupted file they all got smushed into one big string.

# Find the prompt section boundaries
# CLOSING_PROMPT_V2 ends with: 哪些明日可关注加仓、哪些需警惕风险\n\n\n
# MORNING_PROMPT_V2 starts with: 请按步骤分析：
# Actually, looking at the filtered output, the prompts are concatenated.
# Let me fix them by splitting on known boundaries.

# The CLOSING_PROMPT_V2 originally ends at "还是仅为明日计划" then """
# Then MORNING_PROMPT_V2 = T1_FRAMEWORK + ... starts
# In the corrupted file, the """ closing and the next prompt def are gone

# Strategy: Split each prompt at the last line before the next prompt content starts.

# CLOSING_PROMPT_V2: ends with "哪些需警惕风险\n" and last line has the T+1 rule
# MORNING_PROMPT_V2: starts with empty line then "请按步骤分析："
# NOON_PROMPT_V2: starts with "分析步骤："
# DECISION_PROMPT_V2: starts with "你的用户持有14支基金"
# WEEKLY_PROMPT_V2: starts with "分析步骤：" (but different content)

# Let's split and reconstruct each prompt properly

# First, identify the merged prompt block
# It starts at: CLOSING_PROMPT_V2 = T1_FRAMEWORK + ...
# And runs until: # 数据构建 v2

# Split on known boundaries within the merged section

# Find where CLOSING_PROMPT_V2 ends and next begins
# Boundary: end of closing prompt (before "请按步骤分析：")
closing_end = '哪些需警惕风险\n\n\n请按步骤分析：'
if closing_end in text:
    parts = text.split(closing_end, 1)
    text = (parts[0] + 
            '哪些需警惕风险\n- 所以所有操作建议必须明确指出：是在15:00前操作，还是仅为明日计划\n"""\n\n\n' +
            'MORNING_PROMPT_V2 = T1_FRAMEWORK + "\\n" + FINANCIAL_THEORY_FRAMEWORK + "\\n" + """你是一位A股基金首席分析师。现在是早上开盘前，请基于隔夜外盘数据和昨日收盘情况，分析今日A股各赛道的预期走势和应对策略。\n\n' +
            '请按步骤分析：' +
            parts[1])
    print("Fixed CLOSING/MORNING prompt boundary")
else:
    print("WARNING: Could not find CLOSING/MORNING boundary")

# MORNING ends with T+1 rule, NOON starts with "分析步骤："
morning_end = '哪些需要注意风险的基金及理由\n\n\n分析步骤：'
if morning_end in text:
    parts = text.split(morning_end, 1)
    text = (parts[0] +
            '哪些需要注意风险的基金及理由\n- 所以所有操作建议必须明确指出：是在15:00前操作，还是仅为明日计划\n"""\n\n\n' +
            'NOON_PROMPT_V2 = T1_FRAMEWORK + "\\n" + FINANCIAL_THEORY_FRAMEWORK + "\\n" + """你是一位A股基金首席分析师。现在是午盘休市期间，请基于上午走势数据，分析下午可能的方向及操作策略。\n\n' +
            '分析步骤：' +
            parts[1])
    print("Fixed MORNING/NOON prompt boundary")
else:
    print("WARNING: Could not find MORNING/NOON boundary")

# NOON ends, DECISION starts with "你的用户持有14支基金"
noon_end = '- 每个赛道给出午后方向（偏多/偏空/中性）\n\n\n你的用户持有14支基金'
if noon_end in text:
    parts = text.split(noon_end, 1)
    text = (parts[0] +
            '- 每个赛道给出午后方向（偏多/偏空/中性）\n- 所以所有操作建议必须明确指出：是在15:00前操作，还是仅为明日计划\n"""\n\n\n' +
            'DECISION_PROMPT_V2 = T1_FRAMEWORK + "\\n" + FINANCIAL_THEORY_FRAMEWORK + "\\n" + """你是一位拥有15年经验的A股基金首席分析师。现在是14:30关键时刻，请基于今日完整数据和持仓情况，做出是否操作的最终决策判断。\n\n' +
            '你的用户持有14支基金' +
            parts[1])
    print("Fixed NOON/DECISION prompt boundary")
else:
    print("WARNING: Could not find NOON/DECISION boundary")

# DECISION ends, WEEKLY starts with "分析步骤："
decision_end = '- 所有判断要有明确的数据依据\n\n\n分析步骤：'
if decision_end in text:
    parts = text.split(decision_end, 1)
    text = (parts[0] +
            '- 所有判断要有明确的数据依据\n- 所以所有操作建议必须明确指出：是在15:00前操作，还是仅为明日计划\n"""\n\n\n' +
            'WEEKLY_PROMPT_V2 = T1_FRAMEWORK + "\\n" + FINANCIAL_THEORY_FRAMEWORK + "\\n" + """你是一位A股基金首席分析师。请基于本周每日数据和KOL观点，进行周度复盘和下周策略规划。\n\n' +
            '分析步骤：' +
            parts[1])
    print("Fixed DECISION/WEEKLY prompt boundary")
else:
    print("WARNING: Could not find DECISION/WEEKLY boundary")

# WEEKLY ends with T+1 rule, section comment "# 数据构建 v2" follows
weekly_end = '- 下周最重要的3个观察点\n\n\n# 数据构建 v2'
if weekly_end in text:
    parts = text.split(weekly_end, 1)
    text = (parts[0] +
            '- 下周最重要的3个观察点\n- 所以所有操作建议必须明确指出：是在15:00前操作，还是仅为明日计划\n"""\n\n\n' +
            '# 数据构建 v2' +
            parts[1])
    print("Fixed WEEKLY prompt end")
else:
    # Try alternative boundary
    weekly_end2 = '- 下周最重要的3个观察点\n\n\n\n# 数据构建 v2'
    if weekly_end2 in text:
        parts = text.split(weekly_end2, 1)
        text = (parts[0] +
                '- 下周最重要的3个观察点\n- 所以所有操作建议必须明确指出：是在15:00前操作，还是仅为明日计划\n"""\n\n\n' +
                '# 数据构建 v2' +
                parts[1])
        print("Fixed WEEKLY prompt end (alt)")
    else:
        print("WARNING: Could not find WEEKLY prompt end")

# Fix 9: build_closing_data_v2 return
text = text.replace(
    '        get_news_headlines(6),\n    ]\n\n\n    """早盘分析 — 完整数据"""',
    '        get_news_headlines(6),\n    ]\n    return "\\n".join(parts)\n\n\ndef build_morning_data_v2() -> str:\n    """早盘分析 — 完整数据"""'
)

# Fix 10: build_morning_data_v2 return
text = text.replace(
    '        get_news_headlines(6),\n    ]\n\n\n    """午盘分析 — 完整数据"""',
    '        get_news_headlines(6),\n    ]\n    return "\\n".join(parts)\n\n\ndef build_noon_data_v2() -> str:\n    """午盘分析 — 完整数据"""'
)

# Fix 11: build_noon_data_v2 return
text = text.replace(
    '        get_news_headlines(6),\n    ]\n\n\n    """14:30决策 — 完整持仓+完整市场+KOL+预测回溯"""',
    '        get_news_headlines(6),\n    ]\n    return "\\n".join(parts)\n\n\ndef build_decision_data_v2() -> str:\n    """14:30决策 — 完整持仓+完整市场+KOL+预测回溯"""'
)

# Fix 12: build_decision_data_v2 return
text = text.replace(
    '        get_news_headlines(6),\n    ]\n\n\n    """周度复盘 — 完整周数据"""',
    '        get_news_headlines(6),\n    ]\n    return "\\n".join(parts)\n\n\ndef build_weekly_data_v2() -> str:\n    """周度复盘 — 完整周数据"""'
)

# Fix 13: build_weekly_data_v2 return
text = text.replace(
    '        get_news_headlines(8),\n    ]\n\n\n# 公开接口 v2',
    '        get_news_headlines(8),\n    ]\n    return "\\n".join(parts)\n\n\n# 公开接口 v2'
)

# Fix 14: generate_v2 return
text = text.replace(
    '        _cache_write(report_type, analysis)\n\n\n    """格式化推送块"""',
    '        _cache_write(report_type, analysis)\n    return analysis\n\n\ndef format_block(text: str, max_len: int = 500) -> str:\n    """格式化推送块"""\n    if not text:\n        return ""\n    return text[:max_len]'
)

# Fix 15: build_weekend_data_v2 function definition
text = text.replace(
    'WEEKEND_PROMPT_V2 = T1_FRAMEWORK + "\\n" + FINANCIAL_THEORY_FRAMEWORK + "\\n" + """你是一位A股基金首席分析师。现在是周末，请基于最新外盘数据（美股/黄金/美元/恒生）和KOL最新观点，分析对A股各赛道的传导影响，给出周一开盘前的作战预案。',
    'WEEKEND_PROMPT_V2 = T1_FRAMEWORK + "\\n" + FINANCIAL_THEORY_FRAMEWORK + "\\n" + """你是一位A股基金首席分析师。现在是周末，请基于最新外盘数据（美股/黄金/美元/恒生）和KOL最新观点，分析对A股各赛道的传导影响，给出周一开盘前的作战预案。'
)

# Actually the above won't help. Let me fix the weekend prompt close and build_weekend_data_v2 def
text = text.replace(
    '- 每种情景下的应对预案（哪些基金该加仓/减仓/持有）\n\n\n    """构造周末分析数据',
    '- 每种情景下的应对预案（哪些基金该加仓/减仓/持有）\n- 所以所有操作建议必须明确指出：是在15:00前操作，还是仅为明日计划\n"""\n\n\ndef build_weekend_data_v2() -> str:\n    """构造周末分析数据'
)

# Fix 16: build_weekend_data_v2 exception return
text = text.replace(
    '        return "\\n".join(parts)\n    except Exception as e:\n\n\n    """生成周末深度分析"""',
    '        return "\\n".join(parts)\n    except Exception as e:\n        return f"周末数据采集失败: {e}"\n\n\ndef generate_weekend_v2(use_cache: bool = True) -> Optional[str]:\n    """生成周末深度分析"""'
)

# Fix 17: generate_weekend_v2 return
text = text.replace(
    '        _cache_write("weekend", analysis)\n\n\n_config_extra',
    '        _cache_write("weekend", analysis)\n    return analysis\n\n\n_config_extra'
)

# Fix 18: _patch_config
text = text.replace(
    'def _patch_config():\n    global _orig_config\n    # 延迟打补丁到调用时\n\n\n# 命令行',
    'def _patch_config():\n    global _orig_config\n    # 延迟打补丁到调用时\n    pass\n\n\n# 命令行'
)

# Fix 19: __main__ else branch
text = text.replace(
    '        print("=" * 50)\n    else:\n\n\n# ⬇️ 以下为新增函数',
    '        print("=" * 50)\n    else:\n        print(f"  ⚠️ {rt} 分析生成失败", file=sys.stderr)\n\n\n# ⬇️ 以下为新增函数'
)

# Fix 20: get_multi_day_trend return
text = text.replace(
    "        lines.append(f\"| {d[-5:]} | {idx.get('上证指数','?')} | {idx.get('科创50','?')} | {idx.get('沪深300','?')} | {idx.get('创业板指','?')} | {idx.get('上证50','?')} | {idx.get('黄金ETF市场价','?')} |\")\n    \n\n    \"\"\"读取最新的持仓盈亏数据\"\"\"",
    "        lines.append(f\"| {d[-5:]} | {idx.get('上证指数','?')} | {idx.get('科创50','?')} | {idx.get('沪深300','?')} | {idx.get('创业板指','?')} | {idx.get('上证50','?')} | {idx.get('黄金ETF市场价','?')} |\")\n    \n    return \"\\n\".join(lines)\n\n\ndef get_portfolio_pnl() -> str:\n    \"\"\"读取最新的持仓盈亏数据\"\"\""
)

# Fix 21: get_portfolio_pnl return
text = text.replace(
    '            f"  估算手续费: {fee:.2f}元\\n"\n\n\n    """从 news_sources.json RSS源采集最新财经新闻"""',
    '            f"  估算手续费: {fee:.2f}元")\n\n\ndef get_news_headlines(max_items: int = 5) -> str:\n    """从 news_sources.json RSS源采集最新财经新闻"""'
)

# Fix 22: get_news_headlines needs return at end
# The file ends with get_news_headlines body, let's add the return
last_line = text.rstrip().rsplit('\n', 1)[-1]
if 'lines.append(f"  {label}' in text:
    text = text.rstrip() + '\n    \n    return "\\n".join(lines)\n'

# Write output
with open(OUT, 'w') as f:
    f.write(text)

print(f"Written {len(text)} bytes to {OUT}")
print(f"Lines: {len(text.splitlines())}")

# Verify syntax
import ast
try:
    ast.parse(text)
    print("✅ Python syntax check: PASSED")
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")
    # Show context around error
    error_line = e.lineno
    all_lines = text.split('\n')
    start = max(0, error_line - 5)
    end = min(len(all_lines), error_line + 3)
    print(f"\nContext around line {error_line}:")
    for i in range(start, end):
        marker = '>>>' if i == error_line - 1 else '   '
        print(f"{marker} {i+1}: {all_lines[i]}")
