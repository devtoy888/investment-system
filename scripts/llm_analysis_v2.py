#!/usr/bin/env python3
"""
LLM分析模块 v2 — 充分发挥DeepSeek金融分析能力
=============================================
设计原则:
1. 不限输出字数 — 深度比简洁重要
2. 传完整数据 — 不截断数据源
3. 多步推理链 — 分步思考而非一次性输出
4. 跨任务上下文 — 知道之前分析了什么
5. 持仓深度感知 — 知道每支基金的成本/天数/盈亏
6. KOL+数据双源交叉验证
7. ✅ T+1基金操作规则 + 金融理论框架驱动分析
"""

# 共同金融约束框架 — 注入每个系统提示词
# ═══════════════════════════════════════════════

T1_FRAMEWORK = """## 【共同约束：基金操作规则 — 按收盘净值成交】
你管理的所有14支基金都是场外基金，与股票/ETF有本质区别，必须深刻理解以下操作约束：

### ⏰ 时间约束
- **15:00前下单** → 按**今日收盘净值**成交（净值在收盘后公布，下单时不知道确切成交价）
- **15:00后下单** → 按**下一个交易日收盘净值**成交
- 估算净值（盘中实时估算）≠ 实际成交净值，仅作方向参考

### 📋 买卖到账规则
- **买入**：今日买入（15:00前）→ 按今日净值 → 份额明天（T+1）到账
- **卖出**：今日卖出（15:00前）→ 按今日净值 → 资金T+2左右到账
- 卖出后资金不会马上可用，需要2-3个交易日到账

### 🏗️ 建仓期保护
003096（中欧医疗C）和013403（华夏恒生科技C）处于建仓期，**仅允许"持有"或"可加仓"**，不允许减仓。

### ⚡ 15:00决策窗口的意义
- 你看到的估算净值、实时走势、板块涨跌都是**决策参考**，不是成交价
- 你是在"盲操作"——你知道今天大盘涨跌方向，但不知道每支基金的精确成交净值
- 14:30-15:00是最关键的决策窗口，因为这是今日最后的操作机会
- 所有操作建议必须明确指出：是在15:00前操作，还是仅为明日计划"""


FINANCIAL_THEORY_FRAMEWORK = """## 【共同约束：金融投资理论框架】
你的分析应基于以下投资理论原则进行分析判断，但**不要死套具体数字**，而是结合实际数据做独立判断：

### 1️⃣ 趋势跟踪
- 单日波动 ≠ 趋势：不因一天大涨看多、一天大跌看空
- 判断趋势需要结合量价关系、振幅变化确认方向
- 加速/减速/反转的信号由你基于数据自行判断

### 2️⃣ 风险控制
- 持仓组合需要分散风险，避免单一赛道过度集中
- 当市场出现明确的风险信号时，及时降低风险敞口
- 建仓期基金(003096/013403)永远不受减仓操作影响

### 3️⃣ 仓位管理
- 避免在市场不明朗时满仓操作
- 新建仓建议分批进行，不要一次性投入全部资金
- 考虑总仓位与现金储备的平衡

### 4️⃣ 再平衡
- 组合中各赛道有大致的目标配比作为参考方向
- 当某个赛道占比偏离过大时，考虑调整
- 再平衡优先用增量资金，其次调整存量

### 5️⃣ 组合监控
- 每日关注各赛道占比和整体风险水平
- 定期复盘持仓基金的表现和操作记录
- 避免频繁交易增加成本
"""

import sys, os, json, requests, time, re
from pathlib import Path
from datetime import date, datetime, timedelta
from typing import Optional, Any

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
SUMMARY_DIR = Path("/tmp/fund_data")
DATA_DIR = Path("/opt/data/fund_system_data")
OPS_DIR = DATA_DIR / "operations"
CACHE_DIR = Path("/opt/data/fund_system_data/llm_analysis_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# 从.env加载API key
if not DEEPSEEK_API_KEY:
    env_path = '/opt/data/profiles/investment/.env'
    if os.path.exists(env_path):
        for line in open(env_path):
            if line.startswith('DEEPSEEK_API_KEY='):
                DEEPSEEK_API_KEY = line.split('=', 1)[1].strip()
                os.environ['DEEPSEEK_API_KEY'] = DEEPSEEK_API_KEY

# ── 定义用户持有的14支基金（写死不用每次都查）──
ALL_FUNDS = [
    # 科技/AI — 7支
    ('011613', '华夏科创50ETF联接C', '科技/AI'),
    ('024418', '华夏半导体材料ETF联接C', '科技/AI'),
    ('014871', '大摩科技领先混合C', '科技/AI'),
    ('017103', '大摩数字经济混合C', '科技/AI'),
    ('011712', '大摩万众创新混合C', '科技/AI'),
    ('020233', '大摩景气智选混合C', '科技/AI'),
    ('026449', '大摩沪港深科技混合C', '科技/AI'),
    # 黄金 — 1支
    ('009478', '中银上海金ETF联接C', '黄金'),
    # 资源/周期 — 2支
    ('163302', '大摩资源优选混合(LOF)', '资源/周期'),
    ('025857', '华夏中证电网设备ETF联接C', '资源/周期'),
    # 新能源 — 2支
    ('012329', '天弘中证新能源指数增强C', '新能源'),
    ('011103', '天弘中证光伏C', '新能源'),
    # 建仓期 — 2支
    ('003096', '中欧医疗健康混合C', '医药'),
    ('013403', '华夏恒生科技ETF联接C', '恒生科技'),
]

BUILDING_FUNDS = {'003096', '013403'}


# DeepSeek API 调用
# ═══════════════════════════════════════════════

def call_ds(system: str, user: str, max_tokens: int = 2000, temp: float = 0.3) -> Optional[str]:
    """调用DeepSeek V4 Flash"""
    if not DEEPSEEK_API_KEY:
        return None
    try:
        resp = requests.post(
            f'{DEEPSEEK_BASE_URL}/chat/completions',
            headers={'Authorization': f'Bearer {DEEPSEEK_API_KEY}', 'Content-Type': 'application/json'},
            json={
                'model': 'deepseek-v4-flash',
                'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
                'max_tokens': max_tokens, 'temperature': temp, 'stream': False
            },
            timeout=120
        )
        resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"  ⚠️ DS API: {type(e).__name__}: {str(e)[:100]}", file=sys.stderr)
        return None


def _cache_key(rt: str) -> str:
    return f"{rt}_{date.today().isoformat()}"

def _cache_read(rt: str) -> Optional[str]:
    f = CACHE_DIR / f"{_cache_key(rt)}.txt"
    return f.read_text(encoding='utf-8').strip() if f.exists() else None

def _cache_write(rt: str, content: str):
    (CACHE_DIR / f"{_cache_key(rt)}.txt").write_text(content, encoding='utf-8')


# 数据加载 — 完整数据不截断
# ═══════════════════════════════════════════════

def read_tmp(name: str) -> str:
    f = SUMMARY_DIR / name
    return f.read_text(encoding='utf-8').strip() if f.exists() else ""

def load_json_tmp(name: str) -> dict:
    f = SUMMARY_DIR / name
    try: return json.loads(f.read_text()) if f.exists() else {}
    except: return {}

def load_jsonl(path: Path, n: int = 5) -> list:
    if not path.exists(): return []
    lines = [l.strip() for l in path.read_text().split('\n') if l.strip()]
    records = []
    for l in lines[-n:]:
        try: records.append(json.loads(l))
        except: pass
    return records

def get_portfolio_summary() -> str:
    """读取完整持仓数据"""
    # 从操作记录构建
    portfolio = {}
    if OPS_DIR.exists():
        for fpath in sorted(OPS_DIR.glob('operation_*.md')):
            text = fpath.read_text(encoding='utf-8')
            rows = re.findall(
                r'\|?\s*(\d{1,2}/\d{1,2})?\s*\|?\s*([^|]+?)\s*\|?\s*(\d{6})\s*\|?\s*(\d+)\s*\|?',
                text
            )
            for row in rows:
                date_str, fname, code, amount = row
                amount = float(amount)
                if code not in portfolio:
                    portfolio[code] = {'name': fname.strip(), 'total_cost': 0, 'batches': []}
                portfolio[code]['total_cost'] += amount
                portfolio[code]['batches'].append({'date': date_str, 'amount': amount})
    
    if not portfolio:
        return "持仓数据暂缺"
    
    lines = ["📊 完整持仓:"]
    for code, info in portfolio.items():
        fund_info = next((f for f in ALL_FUNDS if f[0] == code), None)
        sector = fund_info[2] if fund_info else "未知"
        status = "🏗️建仓期" if code in BUILDING_FUNDS else ""
        days_held = ""
        if info['batches']:
            first_date = info['batches'][0]['date']
            try:
                fd = datetime.strptime(first_date, '%m/%d')
                today = datetime.now()
                d = (today - fd.replace(year=today.year)).days
                days_held = f"持有{d}天"
            except:
                pass
        
        batch_detail = "; ".join([f"{b['date']}入{b['amount']:.0f}元" for b in info['batches']])
        lines.append(f"  {code} {info['name']} [{sector}] {status}")
        lines.append(f"    总成本{info['total_cost']:.0f}元 {days_held}")
        lines.append(f"    明细: {batch_detail}")
    
    # 分类汇总
    by_sector = {}
    for code, info in portfolio.items():
        fund_info = next((f for f in ALL_FUNDS if f[0] == code), None)
        sector = fund_info[2] if fund_info else "未知"
        if sector not in by_sector:
            by_sector[sector] = {'count': 0, 'cost': 0}
        by_sector[sector]['count'] += 1
        by_sector[sector]['cost'] += info['total_cost']
    
    lines.append("")
    lines.append("📊 赛道分布:")
    for sector, sdata in sorted(by_sector.items(), key=lambda x: -x[1]['cost']):
        pct = sdata['cost'] / sum(s['cost'] for s in by_sector.values()) * 100
        lines.append(f"  {sector}: {sdata['count']}支 {sdata['cost']:.0f}元 ({pct:.0f}%)")
    
    return "\n".join(lines)


def get_previous_predictions() -> str:
    """读取昨天的预测及验证结果"""
    pred_file = DATA_DIR / "llm_evolution" / "predictions.jsonl"
    if not pred_file.exists():
        return "无历史预测数据"
    
    predictions = []
    with open(pred_file) as pf:
        for line in pf:
            try: predictions.append(json.loads(line))
            except: pass
    
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    yesterday_preds = [p for p in predictions if p.get('generated_date') == yesterday]
    
    if not yesterday_preds:
        return "无昨日预测数据"
    
    lines = ["📋 昨日预测回顾:"]
    for p in yesterday_preds:
        acc = p.get('accuracy', '待验证')
        emoji = '✅' if acc == 'correct' else ('❌' if acc == 'wrong' else '⏳')
        lines.append(f"  {emoji} {p.get('target','?')} → {p.get('direction','?')} (置信度{p.get('confidence','?')})")
        if p.get('actual_outcome'):
            lines.append(f"     实际: {p['actual_outcome']}")
    
    return "\n".join(lines)


def get_kol_today() -> str:
    """获取今日KOL观点"""
    kol_text = read_tmp("_kol_summary.txt")
    noon_kol = read_tmp("_noon_kol.txt")
    
    parts = []
    if kol_text:
        parts.append("=== 早盘KOL ===")
        parts.append(kol_text[:2000])
    if noon_kol:
        parts.append("=== 盘中KOL ===")
        parts.append(noon_kol[:2000])
    
    return "\n".join(parts) if parts else ""


# 系统提示词 v2 — 发挥DeepSeek深度分析能力
# ═══════════════════════════════════════════════
# 核心变化: 不限字数 + 多步推理 + 持仓深度感知 + 预测回溯

CLOSING_PROMPT_V2 = T1_FRAMEWORK + "\n" + FINANCIAL_THEORY_FRAMEWORK + "\n" + """你是一位拥有15年经验的A股基金首席分析师，专精于多因子市场分析和T+1基金组合管理。

请按以下步骤分析今日收盘数据：

【步骤1：市场全景定性】
基于指数涨跌、成交量、涨跌家数，用一个精炼的判断定性今日市场（如 "大强小弱的修复日" / "系统性杀跌" / "震荡分化" 等）。解释为什么是这个定性。

【步骤2：板块轮动深度解构】
- 最强3个板块及驱动逻辑（是超跌反弹、避险驱动、还是趋势加速？）
- 最弱3个板块及下跌原因（是获利了结、基本面恶化、还是情绪扩散？）
- 当日是否出现风格切换信号？（从成长→价值？大盘→小盘？科技→消费？）

【步骤3：组合影响分析 — 分赛道逐基诊断】
对用户持有的每个赛道，分析今日表现及对组合的影响：
a) 科技/AI（7支）：哪个跌幅最大？哪个相对抗跌？半导体材料vs科创50的分化
b) 黄金（1支）：避险属性是否体现
c) 资源/周期（2支）：有色金属/电网设备的表现
d) 新能源（2支）：持续性还是企稳信号
e) 医药和恒生科技（建仓期）：今日是否适合加仓？

⚠️ 【持仓状态约束 — 必须遵守】
用户持仓14支基金，当前大部分处于深套状态（从高点回撤超过20%），且科技板块占比高达84%，严重超配。
**对于回撤超过20%的基金，严禁建议"止盈/减仓/卖出"**。只允许建议：
- "持有等待反弹至-15%以内再评估"
- 或"继续持有，观望" 
对于回撤超过25%的基金，只允许「持有不动」。

⚠️ **超配约束（与深套约束同等重要）**：
科技占比84%已远超合理范围（55-65%），处于严重超配状态。
**在此超配状态下，严禁建议加仓任何科技类基金（包括024418、011613等）。**
正确的策略是：
- 科技基金：持有不动，等待反弹至-15%以内，再考虑减仓至合理比例
- 非科技基金（黄金/资源/新能源/医药）：可以继续观察，但也不建议大幅加仓
- 建仓期基金（003096/013403）：维持小额定投节奏，不追涨

【步骤4：关键信号识别】
从量价关系、北向资金、市场广度、异常波动等维度，识别当前最重要的2-3个信号。解释这些信号意味着什么。

【步骤5：明日推演】
基于今日数据，给出明日最可能的3种情景及概率判断（如：情景A 科技反弹 40% / 情景B 继续分化 35% / 情景C 全面转弱 25%）。对每种情景，说明判断依据和应该如何应对。

【步骤6：明日基金操作方向参考】
基于今日收盘，给出明日的基金操作方向参考：
- 每个赛道明日总方向（偏多/偏空/中性）
- 具体到基金：哪些明日可关注加仓、哪些需警惕风险
- 所以所有操作建议必须明确指出：是在15:00前操作，还是仅为明日计划
"""


MORNING_PROMPT_V2 = T1_FRAMEWORK + "\n" + FINANCIAL_THEORY_FRAMEWORK + "\n" + """你是一位A股基金首席分析师。现在是早上开盘前，请基于隔夜外盘数据和昨日收盘情况，分析今日A股各赛道的预期走势和应对策略。

请按步骤分析：

【步骤1：隔夜信号传导链】
逐一分析外盘（美股/中概/黄金/美元/恒生/原油）对A股各板块的传导路径。用"外盘XX → A股XX板块"的格式列出3-5条关键传导链，并标注影响强度（强/中/弱）。

【步骤2：昨日复盘与预测验证】
- 昨日市场关键特征
- 如果昨天有预测，验证准确率（从已给的预测数据中提取）
- 昨天的判断是否需要修正

【步骤3：今日作战地图】
列出今日需要重点观察的3条主线，每条包含：
a) 方向判断（看多/看空/中性）
b) 关键观察指标（什么信号出现时才确认方向）
c) 对持仓基金的具体影响

【步骤4：风险清单】
开盘后最怕出现的3件事，以及应对预案。

【步骤5：今日基金关注优先级】
基于隔夜数据和昨日收盘，对以下持仓基金给出今日优先级排序：
a) **最值得关注（3支）** — 今日可能有操作机会的基金及理由
b) **最需要警惕（3支）** — 今日需要注意风险的基金及理由
- 所以所有操作建议必须明确指出：是在15:00前操作，还是仅为明日计划
"""


NOON_PROMPT_V2 = T1_FRAMEWORK + "\n" + FINANCIAL_THEORY_FRAMEWORK + "\n" + """你是一位A股基金首席分析师。现在是午盘休市期间，请基于上午走势数据，分析下午可能的方向及操作策略。

分析步骤：

【步骤1：上午走势定位 vs 昨日预测】
上午实际走势与昨日收盘分析中的"明日推演"是否一致？验证昨日预测。

【步骤2：半日板块轮动】
上午领涨/领跌板块与昨日全天的对比 — 风格在延续还是切换？
- 上午最强和最弱的逻辑
- 上午出现了什么意外信号（如果有）

【步骤3：量价深度分析】
- 上午成交量vs昨日同期 → 放量/缩量程度
- 北向资金半日流向 → 与昨日对比
- 市场宽度（涨跌家数比）→ 是普涨还是结构性行情

【步骤4：午后策略调整】
基于上午数据，中午到14:30应该关注什么？
- 哪些赛道的判断需要调整？
- 下午可能出现的变盘点
- 对持仓基金的影响评估

【步骤5：午后基金操作方向】
基于上午实际走势，给出午后对各持仓基金的初步判断（简版）：
- 每个赛道给出午后方向（偏多/偏空/中性）
- 所以所有操作建议必须明确指出：是在15:00前操作，还是仅为明日计划
"""


DECISION_PROMPT_V2 = T1_FRAMEWORK + "\n" + FINANCIAL_THEORY_FRAMEWORK + "\n" + """你是一位拥有15年经验的A股基金首席分析师。现在是14:30关键时刻，请基于今日完整数据和持仓情况，做出是否操作的最终决策判断。

你的用户持有14支基金，总成本约6426元，其中2支（003096中欧医疗C、013403华夏恒生科技C）处于建仓期。

你已获得以下数据：
1. 今日行情数据（指数、板块、量价、北向资金）
2. 完整持仓明细（每支基金的成本、持有天数、赛道分布）
3. 多日趋势数据（5日指数变化）
4. 实时持仓盈亏（总成本、市值、盈亏率）
5. 最新市场新闻（来自财经RSS源）
6. KOL今日观点（主任和小浣熊微博）
7. 昨日预测回顾
8. 最近操作记录和决策日志

请严格按照以下步骤分析（每一步都必须完成）：

【第一步：全市场画像 — 今日是什么日子？】
基于全天（开盘至14:30）的数据，定性今日行情。**同时结合5日指数趋势**（判断今日是趋势延续还是转折）和**市场新闻**（是否有事件驱动）：
- 市场风格（大盘/小盘/成长/价值？）
- 主线板块（资金集中在哪？）
- 量能特征（放量/缩量/平量？）
- 情绪温度（狂热/活跃/平淡/恐慌？）
- 5日趋势定位（趋势加速/减速/反转？）
- 新闻驱动（今日新闻是否解释了板块异动？）

【第二步：分赛道多空诊断 — 逐赛道给出判断】
结合今日行情、**多日趋势**、**KOL观点**、**市场新闻**，对用户持有的每个赛道从以下维度给出判断：
a) 赛道名称 + 当日多空方向（明确看多/看空/中性）
b) 判断依据（基于今日数据的具体数字）
c) 趋势性质（单日反弹 vs 趋势反转 vs 持续下跌 vs 横盘）
d) 置信度（1-10，基于数据的充分程度）

【第三步：逐基金评分+操作建议 — 每支基金独立评估】
结合**最新持仓盈亏**（总成本+当前市值+盈亏率），对用户持有的全部14支基金逐一进行评估。每支基金输出格式：
```
| 代码 | 简称 | 赛道 | 技术分 | 资金分 | 趋势分 | 总分 | 操作 | 理由 | 置信度 |
```
评分维度说明：
- **技术分**(1-10)：当日涨跌、量价关系、位置（高位/低位）
- **资金分**(1-10)：北向资金对该赛道的态度、成交额变化
- **趋势分**(1-10)：多日趋势（是趋势延续还是反转？3日累计方向）
- **总分** = (技术+资金+趋势)/3

操作方向由你基于数据和市场判断自行决定，以下为方向选择参考：
- **清仓（完全卖出）** — 当判断基金逻辑已坏、或市场风险极高时
- **减仓/减仓观察** — 当判断趋势走坏、需要降低敞口时，给出减仓比例
- **暂不加/持有观望** — 方向不明时
- **可加仓** — 当判断趋势向上、当前相对低位时，给出加仓金额
- **持有（不变）** — 一切正常时

建仓基金（003096/013403）仅允许"持有"或"可加仓"。
注意：所有加仓/减仓建议应说明**仓位比例建议**，让用户知道具体操作规模。

【第四步：风险检查清单】
逐项检查以下风险是否适用今日，基于你的判断给出预警级别（高/中/低）：
- □ 持仓过于集中在某个赛道
- □ 持仓基金出现连续下跌不见企稳
- □ 北向资金方向与持仓方向相反
- □ 市场出现系统性信号（如放量破位）
- □ **持仓盈亏预警** — 结合最新持仓盈亏数据，判断哪些基金已达需要调整的风险阈值
- □ **基金数量冗余** — 科技/AI持有7支是否过多？是否有表现相近的可以合并或淘汰？

约束：
- 严格基于数据，不要虚构数字
- 所有判断要有明确的数据依据
- 所以所有操作建议必须明确指出：是在15:00前操作，还是仅为明日计划
"""


WEEKLY_PROMPT_V2 = T1_FRAMEWORK + "\n" + FINANCIAL_THEORY_FRAMEWORK + "\n" + """你是一位A股基金首席分析师。请基于本周每日数据和KOL观点，进行周度复盘和下周策略规划。

分析步骤：

【步骤1：本周市场全景 — 完整的周度叙事】
- 本周行情的驱动力是什么？（宏观事件/政策变化/外资流动/情绪周期？）
- 周初vs周末的风格变化
- 关键转折点在哪一天？发生了什么？

【步骤2：组合归因分析 — 赚钱/亏钱在哪？】
基于每日快照数据，分析组合各赛道的周度表现：
- 每个赛道对总组合的收益贡献（用快照净值变化）
- 哪个赛道拖累最大？哪个提供了保护？
- 当前配比与目标配比的偏离度

【步骤3：KOL信号聚合 — 谁看得准？】
对唐史主任司马迁和小浣熊1230本周的观点做准确率评估：
- 每人本周的核心论点
- 哪些判断已验证（✅）、哪些错误（❌）、哪些待验证（⏳）
- 下周应该重点关注谁的观点

【步骤4：下周策略 — 具体到持仓调整】
|- 下周赛道配比建议（哪些赛道加仓/减仓/维持/清仓）
|- 具体的基金调整方向（哪些基金该加仓、哪些该减仓、哪些该清仓、哪些换仓）
|- **基金组合优化**：科技/AI持有7支是否冗余？同赛道基金对比分析：
  - 华夏科创50 vs 半导体材料 → 持仓重叠度判断
  - 大摩4支科技基金(014871/017103/011712/020233) → 表现分化评估，是否有重复持仓的可合并
  - 如有冗余基金，给出合并/淘汰建议（如：保留表现最好的2-3支，清仓最差的）
|- 每种调整的仓位幅度建议（如：科技/AI减至30%等）
|- 每周累计盈亏复核：基于最新数据判断哪些基金已达需要调整的阈值
- 下周最重要的3个观察点
- 所以所有操作建议必须明确指出：是在15:00前操作，还是仅为明日计划
"""




# 数据构建 v2 — 完整数据传递
# ═══════════════════════════════════════════════

def build_closing_data_v2() -> str:
    """收盘分析 — 完整数据"""
    tables = read_tmp("_closing_tables.md")
    eval_text = read_tmp("_operation_eval.txt")
    snap = load_json_tmp("_yesterday_snapshot.json")
    
    # 昨日预测
    predictions = get_previous_predictions()
    
    # 基金详细数据（AKShare实时估算+昨日净值基线）
    fund_details = "基金明细（收盘估算，待晚间确认）:\n"
    # 获取实时估算
    fund_realtime = {}
    try:
        import akshare as ak; import pandas as pd
        df = ak.fund_value_estimation_em()
        est_col = [c for c in df.columns if '估算增长率' in c]
        if est_col:
            for _, row in df.iterrows():
                code = str(row['基金代码'])
                if code in getattr(__import__('fund_tools', fromlist=['']), 'FUND_CODES', {}):
                    try:
                        val = str(row.get(est_col[0], '0')).replace('%', '').strip()
                        fund_realtime[code] = float(val) if val and val != '---' else 0.0
                    except: pass
    except: pass
    
    from fund_tools import FUND_CODES
    portfolio_summary = get_portfolio_summary()
    
    fund_details = "基金明细（收盘估算，含回撤状态）:\n"
    for code, name in sorted(FUND_CODES.items()):
        yest_nav = snap.get('funds', {}).get(code, {}).get('nav', '?')
        today_est = fund_realtime.get(code, 0)
        emoji = "🔴" if today_est > 0 else "🟢"
        
        # 估算净值（fix None issue）
        try:
            yest_nav_f = float(yest_nav) if yest_nav != '?' else 0
            est_nav = round(yest_nav_f * (1 + today_est/100), 4) if yest_nav_f > 0 else "N/A"
        except:
            est_nav = "N/A"
        
        fund_details += f"  {code} {name}: 昨收{yest_nav} 估算{emoji}{today_est:+.2f}%"
        if est_nav != "N/A":
            fund_details += f" 估算净值≈{est_nav}"
        fund_details += "\n"
    
    parts = [
        f"📅 {date.today().isoformat()} 收盘数据",
        "",
        "━━━ 完整行情表 ━━━",
        tables,
        "",
        "━━━ 操作评估 ━━━",
        eval_text or "(无)",
        "",
        fund_details if fund_details else "",
        "",
        predictions,
        "",
        "━━━ 持仓全貌 ━━━",
        get_portfolio_summary(),
        "",
        "━━━ 多日趋势(5日) ━━━",
        get_multi_day_trend(5),
        "",
        "━━━ 持仓盈亏 ━━━",
        get_portfolio_pnl(),
        "",
        "━━━ 最新市场新闻 ━━━",
        get_news_headlines(6),
    ]
    return "\n".join(parts)


def build_morning_data_v2() -> str:
    """早盘分析 — 完整数据"""
    overnight = read_tmp("_overnight_summary.txt")
    market = read_tmp("_market_summary.txt")
    sector = read_tmp("_sector_summary.txt")
    overview = read_tmp("_market_overview_summary.txt")
    northbound = read_tmp("_northbound_summary.txt")
    fund = read_tmp("_fund_summary.txt")
    kol = read_tmp("_kol_summary.txt") or read_tmp("_kol_consensus.txt")
    
    # 昨日预测
    predictions = get_previous_predictions()
    
    parts = [
        f"📅 {date.today().isoformat()} 早盘数据",
        "",
        "━━━ 隔夜外盘 ━━━",
        overnight or "无数据",
        "",
        "━━━ A股昨收 ━━━",
        market or "无数据",
        "",
        "━━━ 板块昨收 ━━━",
        sector or "无数据",
        "",
        "━━━ 市场总览 ━━━",
        overview or "无数据",
        "",
        "━━━ 北向资金 ━━━",
        northbound or "无数据",
        "",
        "━━━ 基金昨收 ━━━",
        fund or "无数据",
        "",
        "━━━ 昨日预测回顾 ━━━",
        predictions,
        "",
        "━━━ 持仓全貌 ━━━",
        get_portfolio_summary(),
        "",
        "━━━ KOL观点（部分） ━━━",
        (kol[:1500] if kol else "无数据"),
        "",
        "━━━ 多日趋势(5日) ━━━",
        get_multi_day_trend(5),
        "",
        "━━━ 持仓盈亏 ━━━",
        get_portfolio_pnl(),
        "",
        "━━━ 最新市场新闻 ━━━",
        get_news_headlines(6),
    ]
    return "\n".join(parts)


def build_noon_data_v2() -> str:
    """午盘分析 — 完整数据"""
    market = read_tmp("_noon_market.txt")
    sector = read_tmp("_noon_sector.txt")
    volume = read_tmp("_noon_volume.txt")
    overview = read_tmp("_noon_overview.txt")
    northbound = read_tmp("_noon_northbound.txt")
    fund = read_tmp("_noon_fund.txt")
    group = read_tmp("_noon_group.txt")
    kol = read_tmp("_noon_kol.txt")
    
    # 昨日收盘板块（对比用）
    yesterday_sector = read_tmp("_sector_summary.txt")
    
    # 昨日预测
    predictions = get_previous_predictions()
    
    parts = [
        f"📅 {date.today().isoformat()} 午盘数据",
        "",
        "━━━ 上午行情 ━━━",
        market or "无数据",
        "",
        "━━━ 上午板块 ━━━",
        sector or "无数据",
        "",
        "━━━ 量价分析 ━━━",
        volume or "无数据",
        "",
        "━━━ 市场总览 ━━━",
        overview or "无数据",
        "",
        "━━━ 北向 ━━━",
        northbound or "无数据",
        "",
        "━━━ 昨日板块(对比) ━━━",
        yesterday_sector or "无数据",
        "",
        "━━━ 基金估算 ━━━",
        fund or "无数据",
        "",
        "━━━ 分组表现 ━━━",
        group or "无数据",
        "",
        "━━━ 昨日预测回顾 ━━━",
        predictions,
        "",
        "━━━ 持仓全貌 ━━━",
        get_portfolio_summary(),
        "",
        "━━━ 盘中KOL ━━━",
        (kol[:1500] if kol else "无数据"),
        "",
        "━━━ 多日趋势(5日) ━━━",
        get_multi_day_trend(5),
        "",
        "━━━ 持仓盈亏 ━━━",
        get_portfolio_pnl(),
        "",
        "━━━ 最新市场新闻 ━━━",
        get_news_headlines(6),
    ]
    return "\n".join(parts)


def build_decision_data_v2() -> str:
    """14:30决策 — 完整持仓+完整市场+KOL+预测回溯"""
    noon_market = read_tmp("_noon_market.txt")
    noon_sector = read_tmp("_noon_sector.txt")
    noon_volume = read_tmp("_noon_volume.txt") 
    noon_nb = read_tmp("_noon_northbound.txt")
    noon_overview = read_tmp("_noon_overview.txt")
    
    # 昨日快照（基准）
    snap = load_json_tmp("_yesterday_snapshot.json")
    yesterday_quotes = ""
    if snap.get('quotes'):
        for k, v in snap['quotes'].items():
            if v:
                yesterday_quotes += f"  {k}: {v.get('price')} ({v.get('change_pct')})\n"
    
    # 基金实时估算
    fund_real_time = ""
    if snap.get('funds'):
        fund_real_time = "基金估算净值:\n"
        for code, fd in snap['funds'].items():
            name = fd.get('name', code)
            nav = fd.get('nav', '?')
            chg = fd.get('estimated_change', '?')
            fund_real_time += f"  {code} {name}: NAV={nav} 估算{chg}%\n"
    
    predictions = get_previous_predictions()
    kol = get_kol_today()
    
    ops_text = ""
    if OPS_DIR.exists():
        ops_files = sorted(OPS_DIR.glob("operation_*.md"))
        if ops_files:
            ops_text = ops_files[-1].read_text(encoding='utf-8')[:800]
    
    trade_log = DATA_DIR / "trade_decisions.jsonl"
    trade_data = ""
    if trade_log.exists():
        lines = [l.strip() for l in trade_log.read_text().split('\n') if l.strip()]
        trade_data = "\n".join(lines[-5:])
    
    parts = [
        f"📅 {date.today().isoformat()} 14:30决策数据",
        "",
        "━━━ 昨日收盘（基准） ━━━",
        yesterday_quotes or "无数据",
        "",
        "━━━ 今日行情（截至14:30） ━━━",
        noon_market or "无数据",
        "",
        "━━━ 今日板块 ━━━",
        noon_sector or "无数据",
        "",
        "━━━ 量价分析 ━━━",
        noon_volume or "无数据",
        "",
        "━━━ 北向资金 ━━━",
        noon_nb or "无数据",
        "",
        "━━━ 市场总览 ━━━",
        noon_overview or "无数据",
        "",
        fund_real_time if fund_real_time else "",
        "",
        "━━━ 昨日预测回顾 ━━━",
        predictions,
        "",
        "━━━ 完整持仓 ━━━",
        get_portfolio_summary(),
        "",
        "━━━ 今日KOL观点 ━━━",
        kol[:2000] if kol else "无数据",
        "",
        "━━━ 最近操作 ━━━",
        ops_text or "无",
        "",
        "━━━ 最近决策日志 ━━━",
        trade_data or "无",
        "",
        "━━━ 多日趋势(5日) ━━━",
        get_multi_day_trend(5),
        "",
        "━━━ 持仓盈亏 ━━━",
        get_portfolio_pnl(),
        "",
        "━━━ 最新市场新闻 ━━━",
        get_news_headlines(6),
    ]
    return "\n".join(parts)


def build_weekly_data_v2() -> str:
    """周度复盘 — 完整周数据"""
    closing_records = load_jsonl(DATA_DIR / "closing-reviews.jsonl", n=10)
    signals = load_jsonl(DATA_DIR / "signals.jsonl", n=30)
    snaps = load_jsonl(DATA_DIR / "daily-snapshots.jsonl", n=10)
    
    ops_text = ""
    if OPS_DIR.exists():
        for f in sorted(OPS_DIR.glob("operation_*.md"))[-5:]:
            ops_text += f"\n--- {f.name} ---\n"
            ops_text += f.read_text(encoding='utf-8')[:300] + "\n"
    
    kol_text = read_tmp("_kol_summary.txt") or "无"
    
    trade_log = DATA_DIR / "trade_decisions.jsonl"
    trade_data = ""
    if trade_log.exists():
        lines = [l.strip() for l in trade_log.read_text().split('\n') if l.strip()]
        trade_data = "\n".join(lines[-15:])
    
    sig_text = ""
    for s in signals[-15:]:
        sig_text += f"  [{s.get('date','?')}] {s.get('kol_name','?')}: {s.get('text','?')[:80]} → {'✅' if s.get('verified') else '⏳'}\n"
    
    snap_text = ""
    for s in snaps[-7:]:
        d = s.get('_date', s.get('date', '?'))
        idx = s.get('indices', {})
        snap_text += f"  {d}: 上证={idx.get('上证指数','?')} 科创50={idx.get('科创50','?')} 黄金={idx.get('黄金ETF市场价','?')}\n"
    
    predictions = get_previous_predictions()
    
    parts = [
        f"📅 周度复盘: 截至{date.today().isoformat()}",
        "",
        "━━━ 每日指数快照 ━━━",
        snap_text or "无数据",
        "",
        "━━━ 本周信号 ━━━",
        sig_text or "无数据",
        "",
        "━━━ 本周操作 ━━━",
        ops_text[:1500] or "无",
        "",
        "━━━ 完整持仓 ━━━",
        get_portfolio_summary(),
        "",
        "━━━ 本周决策日志 ━━━",
        trade_data[:1500] or "无",
        "",
        "━━━ 近期预测 ━━━",
        predictions,
        "",
        "━━━ KOL观点 ━━━",
        kol_text[:2000] if kol_text else "无",
        "",
        "━━━ 多日趋势(5日) ━━━",
        get_multi_day_trend(5),
        "",
        "━━━ 持仓盈亏 ━━━",
        get_portfolio_pnl(),
        "",
        "━━━ 本周市场新闻 ━━━",
        get_news_headlines(8),
    ]
    return "\n".join(parts)


# 公开接口 v2
# ═══════════════════════════════════════════════

def generate_v2(report_type: str, use_cache: bool = True) -> Optional[str]:
    """通用v2生成器 — 基于report_type自动选择prompt+data builder"""
    config = {
        'closing': (CLOSING_PROMPT_V2, build_closing_data_v2, 5500),
        'morning': (MORNING_PROMPT_V2, build_morning_data_v2, 2500),
        'noon': (NOON_PROMPT_V2, build_noon_data_v2, 2000),
        'decision': (DECISION_PROMPT_V2, build_decision_data_v2, 2500),
        'weekly': (WEEKLY_PROMPT_V2, build_weekly_data_v2, 3000),
        'weekend': (WEEKEND_PROMPT_V2, build_weekend_data_v2, 2500),
    }
    
    if report_type not in config:
        print(f"  ⚠️ 未知报告类型: {report_type}", file=sys.stderr)
        return None
    
    prompt, builder, max_tok = config[report_type]
    
    if use_cache:
        cached = _cache_read(report_type)
        if cached:
            return cached
    
    data = builder()
    if not data or "(无数据)" in data[:100]:
        print(f"  ⚠️ {report_type} 数据不足", file=sys.stderr)
        return None
    
    # 尝试进化引擎双阶段生成
    try:
        sys.path.insert(0, '/opt/data/scripts')
        from evolution_engine import full_evolution_cycle
        analysis, preds = full_evolution_cycle(report_type, data, prompt, max_tokens=max_tok)
        if analysis:
            _cache_write(report_type, analysis)
            # 预测提取已完成并存储
            return analysis
    except Exception as e:
        print(f"  ⚠️ 进化引擎: {type(e).__name__}", file=sys.stderr)
    
    # 回退单次调用
    analysis = call_ds(prompt, data, max_tokens=max_tok, temp=0.3)
    if analysis:
        _cache_write(report_type, analysis)
    return analysis


def format_block(title: str, content: str) -> str:
    """格式化推送块"""
    if not content:
        return ""
    return f"\n## 📌 {title}\n\n{content}\n"


# Weekend 支持
# ═══════════════════════════════════════════════

WEEKEND_PROMPT_V2 = T1_FRAMEWORK + "\n" + FINANCIAL_THEORY_FRAMEWORK + "\n" + """你是一位A股基金首席分析师。现在是周末，请基于最新外盘数据（美股/黄金/美元/恒生）和KOL最新观点，分析对A股各赛道的传导影响，给出周一开盘前的作战预案。

请按以下步骤分析：

【步骤1：全球市场全景】
逐一分析各外盘品种的最新走势及其联动逻辑：
- 美股（纳斯达克/标普/道琼斯）→ A股科技/AI板块的传导方向
- 黄金 → 黄金赛道的影响
- 美元指数 → 资源/周期板块的反向传导
- 恒生指数 → 港股科技ETF联动
用"外盘XX走势 → A股XX板块"的格式列出关键传导链

【步骤2：持仓赛道影响评估】
分析以下赛道可能受到的外盘影响：
a) 科技/AI（7支基金）：纳指是利好还是利空？幅度如何？
b) 黄金（1支）：金价走势对黄金基金的方向指引
c) 资源/周期（2支）：美元+商品价格的综合影响
d) 新能源（2支）：美股新能源是否跟随纳指波动？
e) 恒生科技（建仓期）：恒指走势对013403的直接影响

【步骤3：KOL信号聚合】
基于博主最新微博判断其对下周的倾向性（偏多/偏空/中性）

【步骤4：周一开盘策略】
- 开盘最可能出现的3种情景及概率
- 每种情景下的应对预案（哪些基金该加仓/减仓/持有）
- 所以所有操作建议必须明确指出：是在15:00前操作，还是仅为明日计划
"""

def build_weekend_data_v2() -> str:
    """构造周末分析数据 — 实时采集外盘+持仓+KOL"""
    try:
        sys.path.insert(0, '/opt/data/scripts')
        import fund_tools as ft
        
        overnight = ft.get_overnight_quotes()
        quotes_str = ""
        for name, q in overnight.items():
            if q:
                emoji = '🔴' if q['change_pct'] > 0 else '🟢' if q['change_pct'] < 0 else '🟡'
                quotes_str += f"  {emoji} {name}: {q['price']} ({q['change_pct']:+.2f}%)\n"
        
        kol_str = ""
        for uid, name in ft.KOLS.items():
            try:
                posts = ft.get_user_weibos(uid, count=5)
                if posts:
                    kol_str += f"\n--- {name} ---\n"
                    for p in posts[:3]:
                        txt = p.get('text','')[:150].replace('\n',' ')
                        kol_str += f"  {txt}\n"
                        interp = ft.interpret_weibo(p.get('text',''), name)
                        if interp:
                            kol_str += f"  解读: {interp}\n"
            except:
                pass
        
        parts = [
            f"📅 周末外盘数据 ({date.today().isoformat()})",
            "",
            "━━━ 外盘收盘 ━━━",
            quotes_str or "无数据",
            "",
            "━━━ 完整持仓 ━━━",
            get_portfolio_summary(),
            "",
            "━━━ KOL最新观点 ━━━",
            kol_str or "无",
            "",
            "━━━ 上周预测回顾 ━━━",
            get_previous_predictions(),
            "",
            "━━━ 多日趋势(5日) ━━━",
            get_multi_day_trend(5),
            "",
            "━━━ 持仓盈亏 ━━━",
            get_portfolio_pnl(),
            "",
            "━━━ 最新市场新闻 ━━━",
            get_news_headlines(8),
        ]
        return "\n".join(parts)
    except Exception as e:
        return f"周末数据采集失败: {e}"


def generate_weekend_v2(use_cache: bool = True) -> Optional[str]:
    """生成周末深度分析"""
    if use_cache:
        cached = _cache_read("weekend")
        if cached:
            return cached
    
    data = build_weekend_data_v2()
    if not data or "全部获取失败" in data[:100]:
        return None
    
    try:
        from evolution_engine import full_evolution_cycle
        analysis, preds = full_evolution_cycle("weekend", data, WEEKEND_PROMPT_V2, max_tokens=2500)
        if analysis:
            _cache_write("weekend", analysis)
        return analysis
    except:
        pass
    
    analysis = call_ds(WEEKEND_PROMPT_V2, data, max_tokens=2500, temp=0.3)
    if analysis:
        _cache_write("weekend", analysis)
    return analysis


_config_extra = {
    'weekend': (WEEKEND_PROMPT_V2, build_weekend_data_v2, 2500),
}

# 覆写原config
_orig_config = None
def _patch_config():
    global _orig_config
    # 延迟打补丁到调用时
    pass


# 命令行
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    rt = sys.argv[1] if len(sys.argv) > 1 else "closing"
    result = generate_v2(rt, use_cache=False)
    if result:
        print(f"📊 {rt.upper()} v2 分析完成:")
        print("=" * 50)
        print(result[:2000])
        print(f"\n... (共{len(result)}字符)")
        print("=" * 50)
    else:
        print(f"  ⚠️ {rt} 分析生成失败", file=sys.stderr)


# ⬇️ 以下为新增函数：多日趋势 + 持仓盈亏 + 市场新闻
# ═══════════════════════════════════════════════

def get_multi_day_trend(days: int = 5) -> str:
    """从 daily-snapshots.jsonl 读取最近N天指数趋势"""
    fpath = DATA_DIR / "daily-snapshots.jsonl"
    if not fpath.exists():
        return "无历史趋势数据"
    
    records = []
    for line in fpath.read_text().split('\n'):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except:
            pass
    
    by_date = {}
    for r in records:
        d = r.get('_date', '')
        by_date[d] = r
    
    sorted_dates = sorted(by_date.keys())[-days:]
    if not sorted_dates:
        return "无历史趋势数据"
    
    lines = ["📈 **多日指数趋势**"]
    lines.append(f"| 日期 | 上证 | 科创50 | 沪深300 | 创业板 | 上证50 | 黄金 |")
    lines.append(f"|:---:|:---:|:-----:|:------:|:-----:|:-----:|:---:|")
    
    for d in sorted_dates:
        r = by_date[d]
        idx = r.get('indices', {})
        lines.append(f"| {d[-5:]} | {idx.get('上证指数','?')} | {idx.get('科创50','?')} | {idx.get('沪深300','?')} | {idx.get('创业板指','?')} | {idx.get('上证50','?')} | {idx.get('黄金ETF市场价','?')} |")
    
    return "\n".join(lines)


def get_portfolio_pnl() -> str:
    """读取最新的持仓盈亏数据"""
    fpath = DATA_DIR / "daily-snapshots.jsonl"
    if not fpath.exists():
        return ""
    
    last_record = None
    for line in reversed(fpath.read_text().split('\n')):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
            if r.get('portfolio_value') and r.get('portfolio_cost'):
                last_record = r
                break
        except:
            pass
    
    if not last_record:
        return ""
    
    pv = last_record['portfolio_value']
    pc = last_record['portfolio_cost']
    pnl = last_record.get('portfolio_pnl', pv - pc)
    pnl_pct = last_record.get('portfolio_pnl_pct', (pnl/pc*100) if pc else 0)
    fee = last_record.get('portfolio_fee_estimate', 0)
    
    return (f"💰 **实时持仓盈亏**\n"
            f"  总成本: {pc:.0f}元\n"
            f"  当前市值: {pv:.0f}元\n"
            f"  盈亏: {pnl:+.0f}元 ({pnl_pct:+.2f}%)\n"
            f"  估算手续费: {fee:.2f}元")


def get_news_headlines(max_items: int = 5) -> str:
    """从 news_sources.json RSS源采集最新财经新闻"""
    import xml.etree.ElementTree as ET
    
    news_file = Path("/opt/data/scripts/news_sources.json")
    if not news_file.exists():
        return "无新闻数据源配置"
    
    try:
        sources = json.loads(news_file.read_text())
    except:
        return "新闻配置解析失败"
    
    all_news = []
    feed_urls = []
    for s in sources.get('sources', []):
        if s.get('type') == 'rss' and s.get('url'):
            feed_urls.append(s)
    
    for src in feed_urls[:6]:
        try:
            resp = requests.get(src['url'], timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code != 200:
                continue
            root = ET.fromstring(resp.content)
            for item in root.iter('item'):
                title = item.findtext('title', '')
                link = item.findtext('link', '')
                pubdate = item.findtext('pubDate', '')
                if title and len(title) > 5:
                    all_news.append({
                        'title': title.strip(),
                        'source': src['name'],
                        'hint': src.get('hint', ''),
                        'date': pubdate[:16] if pubdate else '',
                    })
                    if len(all_news) >= max_items:
                        break
            if len(all_news) >= max_items:
                break
        except Exception as e:
            continue
    
    if not all_news:
        return "无最新新闻"
    
    lines = ["📰 **最新市场新闻**"]
    for n in all_news[:max_items]:
        label = {'ai_semi':'🤖','energy':'⚡','macro':'🏛️','gold':'🥇'}.get(n.get('hint',''), '📌')
        lines.append(f"  {label} [{n['source']}] {n['title']}")
    
    return "\n".join(lines)
