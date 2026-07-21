#!/usr/bin/env python3
"""
进化引擎 v1 — LLM分析闭环进化系统
==================================
功能:
1. 双阶段生成: 初稿 → 自审 → 打磨 → 推送
2. 预测提取: 从分析文本中解析可验证断言
3. 结果追踪: 次日验证预测准确率
4. Prompt进化: 基于历史准确率自动优化

用法:
  python3 evolution_engine.py generate     # 生成+双阶段打磨
  python3 evolution_engine.py verify       # 验证昨日预测
  python3 evolution_engine.py optimize     # 优化提示词
"""

import sys, os, json, re, time
from pathlib import Path
from datetime import date, datetime, timedelta
from typing import Optional, Any

sys.path.insert(0, '/opt/data/scripts')
sys.path.insert(0, '/opt/data')

EVOLUTION_DIR = Path("/opt/data/fund_system_data/llm_evolution")
PREDICTIONS_FILE = EVOLUTION_DIR / "predictions.jsonl"
ACCURACY_FILE = EVOLUTION_DIR / "accuracy_history.jsonl"
PROMPT_EVOLUTION_FILE = EVOLUTION_DIR / "prompt_evolution.json"
CACHE_DIR = Path("/opt/data/fund_system_data/llm_analysis_cache")

EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)

# ── DeepSeek API ──
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
if not DEEPSEEK_API_KEY:
    env_path = '/opt/data/profiles/investment/.env'
    if os.path.exists(env_path):
        for line in open(env_path):
            if line.startswith('DEEPSEEK_API_KEY='):
                DEEPSEEK_API_KEY = line.split('=', 1)[1].strip()
                os.environ['DEEPSEEK_API_KEY'] = DEEPSEEK_API_KEY

BASE_URL = os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')


def call_deepseek(system: str, user: str, max_tokens: int = 1500, temp: float = 0.3) -> Optional[str]:
    """调用DeepSeek V4 Flash"""
    if not DEEPSEEK_API_KEY:
        return None
    import requests
    try:
        resp = requests.post(
            f'{BASE_URL}/chat/completions',
            headers={'Authorization': f'Bearer {DEEPSEEK_API_KEY}', 'Content-Type': 'application/json'},
            json={'model': 'deepseek-v4-flash', 'messages': [
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': user}
            ], 'max_tokens': max_tokens, 'temperature': temp, 'stream': False},
            timeout=120
        )
        resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"  ⚠️ API: {type(e).__name__}", file=sys.stderr)
        return None


# ═══════════════════════════════════════════════
# Layer 1: 双阶段生成 (Two-pass Generation)
# ═══════════════════════════════════════════════

REVIEW_PROMPT = """你是金融AI质量审核专家。检查以下分析报告，从5个维度评分：

A. 数据准确 — 所有数字是否可追溯
B. 逻辑严密 — 推理是否自洽
C. 可验证 — 是否包含具体可验证的预测（如"明日xx板块涨"比"关注xx"好）
D. 风险意识 — 是否强调不确定性
E. 实用性 — 对决策有否实际帮助

输出JSON（不要额外文字）：
{"score": <1-10>, "issues": ["问题1", "问题2"], "improvements": ["改进1", "改进2"]}"""


def two_pass_generate(report_type: str, data: str, system_prompt: str, max_out: int = 1500) -> Optional[str]:
    """双阶段生成: 初稿 → AI自审 → 打磨稿"""
    # Pass 1: 生成初稿
    print(f"  [进化] Pass 1: 生成初稿...", file=sys.stderr)
    draft = call_deepseek(system_prompt, data, max_tokens=max_out, temp=0.3)
    if not draft:
        return None
    
    # Pass 2: 自审评分
    print(f"  [进化] Pass 2: 自我审校...", file=sys.stderr)
    review = call_deepseek(REVIEW_PROMPT, f"报告类型: {report_type}\n\n{draft}", max_tokens=600, temp=0.2)
    
    score = 0
    issues = []
    improvements = []
    if review:
        try:
            # 提取JSON
            jm = re.search(r'\{.*\}', review, re.DOTALL)
            if jm:
                parsed = json.loads(jm.group())
                score = parsed.get('score', 0)
                issues = parsed.get('issues', [])
                improvements = parsed.get('improvements', [])
        except:
            pass
    
    # Pass 3: 如果评分<7，打磨改进
    if score < 7 and improvements:
        print(f"  [进化] Pass 3: 打磨改进 (当前评分{score}/10)...", file=sys.stderr)
        polish_prompt = f"""你是A股基金投资分析师。以下分析报告评分{score}/10，问题：
{chr(10).join(f'- {i}' for i in issues)}

改进要求：
{chr(10).join(f'- {imp}' for imp in improvements)}

请基于原始数据重新撰写分析，保留好的部分，修正问题。"""
        polished = call_deepseek(polish_prompt, f"原始报告:\n{draft}\n\n数据:\n{data[:2000]}", max_tokens=max_out, temp=0.3)
        if polished:
            print(f"  [进化] 打磨完成 ✅", file=sys.stderr)
            return polished
        print(f"  [进化] 打磨失败，使用初稿", file=sys.stderr)
    
    return draft


# ═══════════════════════════════════════════════
# Layer 2: 预测提取器
# ═══════════════════════════════════════════════

PREDICTION_EXTRACT_PROMPT = """从以下财经分析中提取可验证的预测断言。包含显性预测（"预计/可能/将要"）和隐性预测（"关注xx能否企稳"暗示"当前不稳"）。

宽松判断标准：只要涉及"明日/下周/未来"某个方向的可能性判断，都提取出来。

输出JSON数组（不要额外文字）：
[
  {"target": "预测对象(指数/板块/基金)", "direction": "涨/跌/持平/震荡/不确定",
   "timeframe": "1日/1周/短期",
   "condition": "预测条件描述", 
   "confidence": <1-10>,
   "source_sentence": "原文中对应句子"}
]

如果实在没有任何预测，输出空数组: []"""


def extract_predictions(analysis_text: str, report_type: str) -> list:
    """从LLM分析文本中提取可验证的预测"""
    result = call_deepseek(PREDICTION_EXTRACT_PROMPT, 
                           f"报告类型: {report_type}\n\n{analysis_text}", 
                           max_tokens=800, temp=0.2)
    if not result:
        return []
    
    try:
        jm = re.search(r'\[.*\]', result, re.DOTALL)
        if jm:
            predictions = json.loads(jm.group())
            # 添加元数据
            today = date.today().isoformat()
            for p in predictions:
                p['report_type'] = report_type
                p['generated_date'] = today
                p['verified'] = False
                p['actual_outcome'] = None
                p['accuracy'] = None
            return predictions
    except Exception as e:
        print(f"  ⚠️ 预测解析失败: {e}", file=sys.stderr)
    
    return []


def store_predictions(predictions: list):
    """存储预测到JSONL"""
    if not predictions:
        return
    with open(PREDICTIONS_FILE, 'a', encoding='utf-8') as f:
        for p in predictions:
            f.write(json.dumps(p, ensure_ascii=False) + '\n')
    print(f"  [进化] 已存储 {len(predictions)} 条预测", file=sys.stderr)


# ═══════════════════════════════════════════════
# Layer 3: 结果追踪器
# ═══════════════════════════════════════════════

TRACKING_KEYWORDS = {
    '上证指数': 'sh000001',
    '科创50': 'sh000688', 
    '创业板指': 'sz399006',
    '沪深300': 'sh000300',
    '上证50': 'sh000016',
    '半导体': '半导体ETF',
    '通信': '通信ETF',
    '消费': '消费ETF',
    '医药': '医药ETF',
    '新能源': '新能源ETF',
    '光伏': '光伏ETF',
    '军工': '军工ETF',
}

def verify_yesterday_predictions() -> list:
    """验证昨日预测的准确性"""
    if not PREDICTIONS_FILE.exists():
        print("  [验证] 无历史预测数据", file=sys.stderr)
        return []
    
    today = date.today()
    yesterday = (today - timedelta(days=1)).isoformat()
    
    # 读取未验证的预测
    unverified = []
    all_predictions = []
    with open(PREDICTIONS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            p = json.loads(line)
            if not p.get('verified') and p.get('generated_date', '') <= yesterday:
                unverified.append(p)
            all_predictions.append(p)
    
    if not unverified:
        print(f"  [验证] 无待验证预测", file=sys.stderr)
        return []
    
    print(f"  [验证] 待验证: {len(unverified)} 条", file=sys.stderr)
    
    # 获取当前行情
    try:
        from fund_tools import get_tencent_quote
    except:
        print("  ⚠️ fund_tools不可用，跳过验证", file=sys.stderr)
        return []
    
    verified_count = 0
    results = []
    for p in unverified:
        target = p.get('target', '')
        direction = p.get('direction', '')
        
        # 尝试获取这个标的的当前行情
        quote = None
        if target:
            # 查找对应指数代码
            sym = TRACKING_KEYWORDS.get(target)
            if sym:
                q = get_tencent_quote(sym)
                if q:
                    try:
                        change = float(q.get('change_pct', 0))
                        # 判断方向是否正确
                        actual_direction = '涨' if change > 0.5 else ('跌' if change < -0.5 else '持平')
                        correct = (
                            (direction == '涨' and change > 0) or
                            (direction == '跌' and change < 0) or
                            (direction == '持平' and abs(change) < 0.5)
                        )
                        p['verified'] = True
                        p['actual_outcome'] = f"{actual_direction}({change:+.2f}%)"
                        p['accuracy'] = 'correct' if correct else 'wrong'
                        verified_count += 1
                        results.append(p)
                        print(f"  ✅ {target}: 预测{direction} → 实际{actual_direction}({change:+.2f}%) {'✅' if correct else '❌'}", file=sys.stderr)
                    except:
                        pass
        
        if not p.get('verified'):
            p['verified'] = True
            p['accuracy'] = 'unverifiable'
            p['actual_outcome'] = '无法验证'
    
    # 写回（更新验证状态）
    updated = []
    for p in all_predictions:
        for r in results:
            if id(p) == id(r):
                break
        else:
            updated.append(p)
    updated.extend(unverified)
    
    with open(PREDICTIONS_FILE, 'w', encoding='utf-8') as f:
        for p in updated:
            f.write(json.dumps(p, ensure_ascii=False) + '\n')
    
    # 记录准确率历史
    if results:
        acc_record = {
            'date': today.isoformat(),
            'verified': len(results),
            'correct': sum(1 for r in results if r.get('accuracy') == 'correct'),
            'wrong': sum(1 for r in results if r.get('accuracy') == 'wrong'),
            'unverifiable': sum(1 for r in results if r.get('accuracy') == 'unverifiable'),
        }
        with open(ACCURACY_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(acc_record, ensure_ascii=False) + '\n')
        
        rate = acc_record['correct'] / acc_record['verified'] * 100 if acc_record['verified'] > 0 else 0
        print(f"  📊 准确率: {acc_record['correct']}/{acc_record['verified']} = {rate:.1f}%", file=sys.stderr)
    
    return results


# ═══════════════════════════════════════════════
# Layer 4: 准确率看板
# ═══════════════════════════════════════════════

def accuracy_dashboard() -> str:
    """生成准确率看板"""
    if not ACCURACY_FILE.exists():
        return "暂无准确率数据"
    
    records = []
    with open(ACCURACY_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    
    if not records:
        return "暂无准确率数据"
    
    total_verified = sum(r['verified'] for r in records)
    total_correct = sum(r['correct'] for r in records)
    total_wrong = sum(r['wrong'] for r in records)
    overall_rate = total_correct / total_verified * 100 if total_verified > 0 else 0
    
    # 按报告类型统计
    predictions = []
    if PREDICTIONS_FILE.exists():
        with open(PREDICTIONS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        predictions.append(json.loads(line))
                    except:
                        pass
    
    by_type = {}
    for p in predictions:
        rt = p.get('report_type', 'unknown')
        acc = p.get('accuracy')
        if rt not in by_type:
            by_type[rt] = {'correct': 0, 'wrong': 0, 'total': 0}
        if acc == 'correct':
            by_type[rt]['correct'] += 1
        elif acc == 'wrong':
            by_type[rt]['wrong'] += 1
        by_type[rt]['total'] += 1
    
    lines = [
        "📊 **AI分析准确率看板**",
        "",
        f"| 指标 | 值 |",
        f"|:----|:---:|",
        f"| 总预测数 | {total_verified} |",
        f"| 正确 | {total_correct} |",
        f"| 错误 | {total_wrong} |",
        f"| 整体准确率 | {overall_rate:.1f}% |",
        "",
        "**按报告类型**:",
        "| 类型 | 正确 | 总预测 | 准确率 |",
        "|:---|:----:|:-----:|:-----:|",
    ]
    
    for rt, stats in sorted(by_type.items()):
        rate = stats['correct'] / stats['total'] * 100 if stats['total'] > 0 else 0
        lines.append(f"| {rt} | {stats['correct']} | {stats['total']} | {rate:.0f}% |")
    
    lines.append("")
    lines.append(f"*更新: {date.today().isoformat()}*")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════
# Layer 5: Prompt自进化
# ═══════════════════════════════════════════════

def evolve_prompts() -> dict:
    """基于历史准确率生成优化建议"""
    if not PREDICTIONS_FILE.exists() or not ACCURACY_FILE.exists():
        return {"status": "数据不足", "suggestions": []}
    
    # 读取预测数据
    predictions = []
    with open(PREDICTIONS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    predictions.append(json.loads(line))
                except:
                    pass
    
    if len(predictions) < 5:
        return {"status": "数据不足(需≥5条)", "suggestions": []}
    
    # 找出准确率高/低的模式
    correct_predictions = [p for p in predictions if p.get('accuracy') == 'correct']
    wrong_predictions = [p for p in predictions if p.get('accuracy') == 'wrong']
    
    # 用LLM分析哪些模式work
    analysis_data = {
        'total': len(predictions),
        'correct': len(correct_predictions),
        'wrong': len(wrong_predictions),
        'correct_samples': [{'target': p['target'], 'direction': p['direction'], 'source': p.get('source_sentence', '')[:100]} 
                           for p in correct_predictions[:3]],
        'wrong_samples': [{'target': p['target'], 'direction': p['direction'], 'source': p.get('source_sentence', '')[:100]} 
                         for p in wrong_predictions[:3]],
    }
    
    prompt = f"""你是AI Prompt优化专家。基于以下金融预测准确率数据，分析哪些分析模式有效、哪些无效，给出Prompt优化建议。

数据: {json.dumps(analysis_data, ensure_ascii=False)}

输出JSON:
{{
  "effective_patterns": ["有效的分析模式"],
  "ineffective_patterns": ["无效/需修正的模式"],
  "prompt_optimizations": ["具体Prompt修改建议"],
  "new_focus_areas": ["应该新增的分析维度"]
}}"""
    
    result = call_deepseek(prompt, "请分析并输出优化建议", max_tokens=1000, temp=0.3)
    
    suggestions = {"status": "已完成", "suggestions": []}
    if result:
        try:
            jm = re.search(r'\{.*\}', result, re.DOTALL)
            if jm:
                suggestions = json.loads(jm.group())
        except:
            pass
    
    # 保存进化记录
    evolution_record = {
        'date': date.today().isoformat(),
        'total_predictions': len(predictions),
        'accuracy': analysis_data['correct'] / max(analysis_data['correct'] + analysis_data['wrong'], 1),
        'suggestions': suggestions,
    }
    PROMPT_EVOLUTION_FILE.write_text(
        json.dumps(evolution_record, ensure_ascii=False, indent=2)
    )
    
    print(f"  [进化] Prompt优化建议已生成", file=sys.stderr)
    print(f"  有效模式: {suggestions.get('effective_patterns', [])}", file=sys.stderr)
    print(f"  待优化: {suggestions.get('ineffective_patterns', [])}", file=sys.stderr)
    
    return suggestions


# ═══════════════════════════════════════════════
# 完整进化流程
# ═══════════════════════════════════════════════

def full_evolution_cycle(report_type: str, data: str, system_prompt: str, max_tokens: int = 1500) -> tuple:
    """
    完整进化流程:
    1. 双阶段生成 → 2. 提取预测 → 3. 存储预测
    返回: (final_analysis, predictions)
    """
    # Step 1: 双阶段生成
    analysis = two_pass_generate(report_type, data, system_prompt, max_out=max_tokens)
    if not analysis:
        return None, []
    
    # Step 2: 提取并存储预测
    predictions = extract_predictions(analysis, report_type)
    if predictions:
        store_predictions(predictions)
    
    return analysis, predictions


# ═══════════════════════════════════════════════
# CLI 入口
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if action == "verify":
        results = verify_yesterday_predictions()
        print(f"\n{accuracy_dashboard()}")
    
    elif action == "dashboard":
        print(accuracy_dashboard())
    
    elif action == "evolve":
        suggestions = evolve_prompts()
        print(json.dumps(suggestions, ensure_ascii=False, indent=2))
    
    elif action == "status":
        print("📈 **AI进化引擎状态**")
        print(f"  预测库: {PREDICTIONS_FILE}")
        print(f"  准确率历史: {ACCURACY_FILE}")
        print(f"  Prompt进化: {PROMPT_EVOLUTION_FILE}")
        print(f"  预测数: {sum(1 for _ in open(PREDICTIONS_FILE)) if PREDICTIONS_FILE.exists() else 0}")
        
    else:
        print(f"用法: {sys.argv[0]} [verify|dashboard|evolve|status]")
