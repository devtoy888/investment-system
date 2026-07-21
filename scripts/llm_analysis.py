#!/usr/bin/env python3
"""
LLM分析模块 — 调用DeepSeek V4 Flash对A股基金市场数据进行深度分析
充分发挥DeepSeek在金融领域的分析能力：多因子合成、趋势识别、风险评估

用法: 各报告脚本先采集数据写/tmp/fund_data/，然后调用本模块生成分析文本
"""

import os, sys, json, requests, time
from pathlib import Path
from datetime import date, datetime
from typing import Optional, Any

# ── 密钥配置 ──
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
SUMMARY_DIR = Path("/tmp/fund_data")
LLM_CACHE_DIR = Path("/opt/data/fund_system_data/llm_analysis_cache")
LLM_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════
# DeepSeek API 调用
# ═══════════════════════════════════════════════

def call_deepseek(
    system_prompt: str,
    user_data: str,
    max_tokens: int = 1500,
    temperature: float = 0.3,
    model: str = "deepseek-v4-flash",
) -> Optional[str]:
    """调用DeepSeek V4 Flash API"""
    if not DEEPSEEK_API_KEY:
        print("  ⚠️ DEEPSEEK_API_KEY 未设置，跳过LLM分析", file=sys.stderr)
        return None
    
    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_data}
        ],
        'max_tokens': max_tokens,
        'temperature': temperature,
        'stream': False
    }
    
    try:
        resp = requests.post(
            f'{DEEPSEEK_BASE_URL}/chat/completions',
            headers=headers, json=payload, timeout=90
        )
        resp.raise_for_status()
        result = resp.json()['choices'][0]['message']['content']
        return result
    except requests.exceptions.Timeout:
        print(f"  ⚠️ DeepSeek API 超时(90s)", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  ⚠️ DeepSeek API 调用失败: {type(e).__name__}: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"    响应: {e.response.text[:500]}", file=sys.stderr)
        return None


# ═══════════════════════════════════════════════
# 缓存管理（防重复调用）
# ═══════════════════════════════════════════════

def _cache_key(report_type: str) -> str:
    """生成当日缓存key"""
    today = date.today().isoformat()
    return f"{report_type}_{today}"

def _read_cache(report_type: str) -> Optional[str]:
    """读取当日缓存"""
    key = _cache_key(report_type)
    cache_file = LLM_CACHE_DIR / f"{key}.txt"
    if cache_file.exists():
        content = cache_file.read_text(encoding='utf-8').strip()
        if content:
            print(f"  📦 读取LLM分析缓存: {key}", file=sys.stderr)
            return content
    return None

def _write_cache(report_type: str, content: str):
    """写入当日缓存"""
    key = _cache_key(report_type)
    cache_file = LLM_CACHE_DIR / f"{key}.txt"
    cache_file.write_text(content, encoding='utf-8')
    print(f"  💾 LLM分析已缓存: {key}", file=sys.stderr)


# ═══════════════════════════════════════════════
# 数据加载工具
# ═══════════════════════════════════════════════

def read_tmp_file(name: str) -> str:
    """读取/tmp/fund_data/下的文件"""
    f = SUMMARY_DIR / name
    return f.read_text(encoding='utf-8').strip() if f.exists() else ""

def load_json_tmp(name: str) -> dict:
    """加载JSON文件"""
    f = SUMMARY_DIR / name
    if f.exists():
        try:
            return json.loads(f.read_text())
        except:
            pass
    return {}

def load_jsonl(path: Path, last_n: int = 5) -> list:
    """加载JSONL最后N条记录"""
    if not path.exists():
        return []
    lines = [l.strip() for l in path.read_text().split('\n') if l.strip()]
    records = []
    for l in lines[-last_n:]:
        try:
            records.append(json.loads(l))
        except:
            continue
    return records


# ═══════════════════════════════════════════════
# 系统提示词 — 针对DeepSeek金融分析能力设计
# ═══════════════════════════════════════════════

CLOSING_ANALYSIS_PROMPT = """你是一位专业的A股基金投资分析师，拥有10年经验。你的任务是分析今日收盘数据，生成一段精炼的日度复盘分析。

分析要求：
1. 今日行情总览 — 用1-2句话概括今日市场走势的核心特征（风格、领跌/领涨、量能变化）
2. 板块轮动解读 — 识别今日最强和最弱板块，分析轮动逻辑（是避险驱动、超跌反弹还是趋势延续）
3. 持仓影响 — 从用户持有的科技/AI、黄金、资源/周期、新能源、医药等赛道角度，说明今日涨跌对组合的影响程度
4. 关键信号 — 识别需要关注的异常信号（放量/缩量、突破/破位、北向资金异动等）
5. 明日关注 — 2-3个明日需要重点观察的维度

约束：
- 严格基于数据说话，不凭空推测
- 不给出具体买卖建议
- 数据已标注涨跌方向，直接引用即可
- 输出控制在300字以内，简洁有力
- 使用中文，自然口语化"""

MORNING_ANALYSIS_PROMPT = """你是一位专业的A股基金投资分析师。你的任务是分析早盘数据（隔夜外盘 + 昨日A股收盘），为今日交易做准备。

分析要求：
1. 隔夜信号解读 — 外盘走势的A股传导逻辑（美股/黄金/美元/恒生→A股哪些板块）
2. 昨日复盘要点 — 昨日放量下跌/上涨是否延续，关键位置得失
3. 今日关注 — 开盘后重点观察的3个维度（板块/资金/事件）
4. 风险提示 — 今日潜在的风险点（外盘期货异动、宏观事件等）

约束：
- 数据驱动，不猜测
- 与A股30分钟开盘（9:30）的时间点匹配
- 输出控制在250字以内"""

NOON_ANALYSIS_PROMPT = """你是一位专业的A股基金投资分析师。你的任务是分析上午盘面数据，给出午后策略参考。

分析要求：
1. 上午走势定性 — 上午是延续昨日方向、反转还是震荡？（用半日数据说话）
2. 板块轮动识别 — 上午领涨/领跌板块与昨日的对比，是否有风格切换信号
3. 量价关系评估 — 上午成交量相对昨日的放缩情况，买卖力量对比
4. 午后策略参考 — 基于上午趋势给出午后关注方向

约束：
- 不给出具体买卖指令
- 输出控制在200字以内"""

DECISION_ANALYSIS_PROMPT = """你是一位专业的A股基金投资分析师，专长于T+1基金波段操作。你的任务是分析当日14:30的市场数据，给出基金操作参考。

分析要求：
1. 当日趋势定性 — 今日是反弹日、继续下跌还是震荡？与过去3天的趋势对比
2. 各赛道状态判断 — 用户持有科技/AI、黄金、资源/周期、新能源、医药赛道，分析各赛道当前的多空格局
3. 基金操作参考 — 基于以下框架给出方向参考：
   - 连续下跌后缩量企稳 → 可观察是否加仓窗口
   - 放量破位下跌 → 暂不加仓，观望
   - 大涨后放量滞涨 → 注意回调风险
   - 横盘整理 → 持有观望
4. 风险提醒 — 需要警惕的异常信号

约束：
- 已经是14:30，要在15:00收盘前给出参考
- T+1基金交易需要提前布局，考虑次日可能的延续性
- 建仓基金(003096中欧医疗C、013403华夏恒生科技C)仍处于建仓期，仅考虑加仓不考虑减仓
- 输出控制在250字以内"""

WEEKLY_ANALYSIS_PROMPT = """你是一位专业的A股基金投资分析师，专长于周度组合诊断。你的任务是分析本周的完整数据，生成周度复盘。

分析要求：
1. 本周行情总览 — 本周市场核心特征（风格、主线、成交量变化）
2. 赛道表现归因 — 用户持有的科技/AI、黄金、资源/周期、新能源、医药各赛道本周表现及归因
3. 组合健康度评估 — 各赛道配比是否合理，需要关注哪些偏离
4. KOL观点聚合 — 两位关注博主(唐史主任司马迁、小浣熊1230)本周的核心观点一致性，哪些判断已验证
5. 下周策略方向 — 基于当前趋势的下周关注重点

约束：
- 数据详实，每个判断都要有数据支撑
- 不承诺收益，不推荐具体买卖点
- 重点关注趋势延续性而非单日波动
- 输出控制在400字以内"""


# ═══════════════════════════════════════════════
# 各报告的分析数据构建函数
# ═══════════════════════════════════════════════

def build_closing_data() -> str:
    """构造收盘分析输入数据"""
    tables = read_tmp_file("_closing_tables.md")
    eval_text = read_tmp_file("_operation_eval.txt")
    
    # 快照数据补充
    snap = load_json_tmp("_yesterday_snapshot.json")
    nb = snap.get('northbound', {})
    nb_total = nb.get('total', 0) if nb else 0
    
    parts = [
        f"📅 日期: {date.today().isoformat()}",
        "",
        "━━━ 收盘数据 ━━━",
        tables[:2000] if len(tables) > 2000 else tables,
        "",
        "━━━ 操作评估 ━━━",
        eval_text[:800] if eval_text else "(无)",
        "",
        f"北向资金: {nb_total:+.2f}亿" if nb_total else "(北向数据暂缺)",
    ]
    return "\n".join(parts)


def build_morning_data() -> str:
    """构造早盘分析输入数据"""
    overnight = read_tmp_file("_overnight_summary.txt")
    market = read_tmp_file("_market_summary.txt")
    sector = read_tmp_file("_sector_summary.txt")
    overview = read_tmp_file("_market_overview_summary.txt")
    northbound = read_tmp_file("_northbound_summary.txt")
    fund = read_tmp_file("_fund_summary.txt")
    
    parts = [
        f"📅 日期: {date.today().isoformat()}",
        "",
        "━━━ 隔夜外盘 ━━━" if overnight else "━━━ 隔夜外盘(无数据)━━━",
        overnight[:500] if overnight else "无数据",
        "",
        "━━━ A股昨收行情 ━━━",
        market[:500] if market else "无数据",
        "",
        "━━━ 板块昨收 ━━━",
        sector[:500] if sector else "无数据",
        "",
        "━━━ 市场总览 ━━━",
        overview[:300] if overview else "无数据",
        "",
        "━━━ 北向资金 ━━━" if northbound else "",
        northbound[:200] if northbound else "",
        "",
        "━━━ 基金昨收 ━━━" if fund else "",
        fund[:500] if fund else "",
    ]
    return "\n".join(parts)


def build_noon_data() -> str:
    """构造午盘分析输入数据"""
    market = read_tmp_file("_noon_market.txt")
    sector = read_tmp_file("_noon_sector.txt")
    volume = read_tmp_file("_noon_volume.txt")
    overview = read_tmp_file("_noon_overview.txt")
    northbound = read_tmp_file("_noon_northbound.txt")
    fund = read_tmp_file("_noon_fund.txt")
    group = read_tmp_file("_noon_group.txt")
    
    # 昨日收盘数据用于对比
    yesterday_sector = read_tmp_file("_sector_summary.txt")
    
    parts = [
        f"📅 日期: {date.today().isoformat()}",
        "",
        "━━━ 上午收盘行情 ━━━",
        market[:300] if market else "无数据",
        "",
        "━━━ 上午板块表现 ━━━",
        sector[:500] if sector else "无数据",
        "",
        "━━━ 量价分析 ━━━",
        volume[:800] if volume else "无数据",
        "",
        "━━━ 市场总览 ━━━",
        overview[:300] if overview else "无数据",
        "",
        "━━━ 北向资金 ━━━" if northbound else "",
        northbound[:200] if northbound else "",
        "",
        "━━━ 昨日收盘板块(对比用) ━━━",
        yesterday_sector[:400] if yesterday_sector else "无数据",
        "",
        "━━━ 基金估算盈亏 ━━━" if fund else "",
        fund[:400] if fund else "",
        "",
        "━━━ 持仓分组表现 ━━━" if group else "",
        group[:300] if group else "",
    ]
    return "\n".join(parts)


def build_decision_data() -> str:
    """构造14:30决策分析输入数据"""
    # 读取收盘快照（昨日数据）
    snap = load_json_tmp("_yesterday_snapshot.json")
    
    # 读取今天的盘中数据
    noon_market = read_tmp_file("_noon_market.txt")
    noon_sector = read_tmp_file("_noon_sector.txt")
    noon_volume = read_tmp_file("_noon_volume.txt")
    noon_nb = read_tmp_file("_noon_northbound.txt")
    
    # 读取操作记录
    ops_dir = Path("/opt/data/fund_system_data/operations")
    ops_text = ""
    if ops_dir.exists():
        ops_files = sorted(ops_dir.glob("operation_*.md"))
        if ops_files:
            ops_text = ops_files[-1].read_text(encoding='utf-8')[:500]
    
    # 读取trade_decisions
    trade_log = Path("/opt/data/fund_system_data/trade_decisions.jsonl")
    trade_data = ""
    if trade_log.exists():
        lines = [l.strip() for l in trade_log.read_text().split('\n') if l.strip()]
        trade_data = "\n".join(lines[-5:])
    
    # 构建昨日指数数据
    yesterday_quotes = ""
    if snap.get('quotes'):
        for k, v in snap['quotes'].items():
            if v:
                yesterday_quotes += f"{k}: {v.get('price')} ({v.get('change_pct')})\n"
    
    parts = [
        f"📅 日期: {date.today().isoformat()}",
        "",
        "━━━ 昨日收盘行情(基准) ━━━",
        yesterday_quotes[:400] if yesterday_quotes else "无数据",
        "",
        "━━━ 今日盘中行情(14:30前) ━━━",
        noon_market[:300] if noon_market else "无数据",
        "",
        "━━━ 今日板块表现 ━━━",
        noon_sector[:500] if noon_sector else "无数据",
        "",
        "━━━ 今日量价分析 ━━━",
        noon_volume[:800] if noon_volume else "无数据",
        "",
        "━━━ 今日北向资金 ━━━" if noon_nb else "",
        noon_nb[:200] if noon_nb else "",
        "",
        "━━━ 最近操作记录 ━━━" if ops_text else "",
        ops_text if ops_text else "",
        "",
        "━━━ 最近决策记录 ━━━" if trade_data else "",
        trade_data if trade_data else "",
    ]
    return "\n".join(parts)


def build_weekly_data() -> str:
    """构造周度复盘分析输入数据"""
    DATA_DIR = Path("/opt/data/fund_system_data")
    
    # 本周收盘数据
    closing_records = load_jsonl(DATA_DIR / "closing-reviews.jsonl", last_n=10)
    # 本周信号
    signals = load_jsonl(DATA_DIR / "signals.jsonl", last_n=20)
    # 每日快照
    snaps = load_jsonl(DATA_DIR / "daily-snapshots.jsonl", last_n=10)
    # 操作记录
    ops_dir = DATA_DIR / "operations"
    ops_text = ""
    if ops_dir.exists():
        for f in sorted(ops_dir.glob("operation_*.md"))[-5:]:
            ops_text += f"\n--- {f.name} ---\n"
            ops_text += f.read_text(encoding='utf-8')[:300] + "\n"
    
    # 本周KOL数据
    kol_summary = read_tmp_file("_kol_summary.txt")
    
    # 近期决策记录
    trade_log = DATA_DIR / "trade_decisions.jsonl"
    trade_data = ""
    if trade_log.exists():
        lines = [l.strip() for l in trade_log.read_text().split('\n') if l.strip()]
        trade_data = "\n".join(lines[-10:])
    
    # 格式化信号
    sig_text = ""
    for s in signals[-10:]:
        sig_text += f"  [{s.get('date','?')}] {s.get('kol_name','?')}: {s.get('text','?')[:80]} → {'✅' if s.get('verified') else '⏳'}\n"
    
    parts = [
        f"📅 周度报告: 截至 {date.today().isoformat()}",
        "",
        "━━━ 本周收盘记录(最近) ━━━",
        "\n".join([f"  {r.get('date','?')}: quotes={len(r.get('quotes',{}))} sectors={len(r.get('sectors',{}))}" for r in closing_records[-5:]]) if closing_records else "无数据",
        "",
        "━━━ 本周信号记录 ━━━" if sig_text else "",
        sig_text[:800] if sig_text else "",
        "",
        "━━━ 本周操作记录 ━━━" if ops_text else "",
        ops_text[:1000] if ops_text else "",
        "",
        "━━━ KOL观点汇总 ━━━" if kol_summary else "",
        kol_summary[:1500] if kol_summary else "",
        "",
        "━━━ 最近决策记录 ━━━" if trade_data else "",
        trade_data[:800] if trade_data else "",
    ]
    return "\n".join(parts)


# ═══════════════════════════════════════════════
# 公开接口
# ═══════════════════════════════════════════════

def generate_closing_analysis(use_cache: bool = True, use_evolution: bool = True) -> Optional[str]:
    """生成收盘复盘LLM分析"""
    if use_cache:
        cached = _read_cache("closing")
        if cached:
            return cached
    
    data = build_closing_data()
    if not data.strip() or "(无数据)" in data:
        return None
    
    if use_evolution:
        try:
            from evolution_engine import full_evolution_cycle
            analysis, preds = full_evolution_cycle("closing", data, CLOSING_ANALYSIS_PROMPT)
            if analysis:
                _write_cache("closing", analysis)
            return analysis
        except Exception as e:
            print(f"  ⚠️ 进化引擎异常,回退普通模式: {type(e).__name__}", file=sys.stderr)
    
    analysis = call_deepseek(CLOSING_ANALYSIS_PROMPT, data, max_tokens=1000)
    if analysis:
        _write_cache("closing", analysis)
    return analysis


def generate_morning_analysis(use_cache: bool = True) -> Optional[str]:
    """生成早报LLM分析"""
    if use_cache:
        cached = _read_cache("morning")
        if cached:
            return cached
    
    data = build_morning_data()
    if not data.strip() or "(无数据)" in data:
        return None
    
    analysis = call_deepseek(MORNING_ANALYSIS_PROMPT, data, max_tokens=1000)
    if analysis:
        _write_cache("morning", analysis)
    return analysis


def generate_noon_analysis(use_cache: bool = True) -> Optional[str]:
    """生成午报LLM分析"""
    if use_cache:
        cached = _read_cache("noon")
        if cached:
            return cached
    
    data = build_noon_data()
    if not data.strip() or "(无数据)" in data:
        return None
    
    analysis = call_deepseek(NOON_ANALYSIS_PROMPT, data, max_tokens=1000)
    if analysis:
        _write_cache("noon", analysis)
    return analysis


def generate_decision_analysis(use_cache: bool = True) -> Optional[str]:
    """生成14:30决策LLM分析"""
    if use_cache:
        cached = _read_cache("decision")
        if cached:
            return cached
    
    data = build_decision_data()
    if not data.strip() or "(无数据)" in data:
        return None
    
    analysis = call_deepseek(DECISION_ANALYSIS_PROMPT, data, max_tokens=1200)
    if analysis:
        _write_cache("decision", analysis)
    return analysis


def generate_weekly_analysis(use_cache: bool = True) -> Optional[str]:
    """生成周度复盘LLM分析"""
    if use_cache:
        cached = _read_cache("weekly")
        if cached:
            return cached
    
    data = build_weekly_data()
    if not data.strip() or "(无数据)" in data:
        return None
    
    analysis = call_deepseek(WEEKLY_ANALYSIS_PROMPT, data, max_tokens=1200)
    if analysis:
        _write_cache("weekly", analysis)
    return analysis


def format_analysis_block(title: str, analysis: str) -> str:
    """将LLM分析格式化成推送块（兼容send_qqbot的## 标题格式）"""
    return f"\n## 📌 {title}\n\n{analysis}\n"


# ═══════════════════════════════════════════════
# 命令行入口（用于测试）
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    report_type = sys.argv[1] if len(sys.argv) > 1 else "closing"
    use_cache = sys.argv[2] != "--no-cache" if len(sys.argv) > 2 else True
    
    generators = {
        "closing": generate_closing_analysis,
        "morning": generate_morning_analysis,
        "noon": generate_noon_analysis,
        "decision": generate_decision_analysis,
        "weekly": generate_weekly_analysis,
    }
    
    gen = generators.get(report_type)
    if not gen:
        print(f"未知报告类型: {report_type}，可选: {list(generators.keys())}")
        sys.exit(1)
    
    result = gen(use_cache=use_cache)
    if result:
        print("=" * 40)
        print(f"📊 {report_type.upper()} LLM分析结果:")
        print("=" * 40)
        print(result)
        print("=" * 40)
    else:
        print(f"❌ {report_type} 分析生成失败（数据不足或API错误）")
