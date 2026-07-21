#!/usr/bin/env python3
"""
KOL分析框架v2 — 当日可操作 + 事实核查闭环

设计:
  1. 信号提取层(Extractor)     → 从博文提取: 赛道/方向/断言/时效(今天/本周/长期)
  2. 事实核查层(Verifier)      → 开盘前: 核查昨日预测准确率
                               → 收盘后: 重新验证当天信号
  3. 操作映射层(Mapper)        → 当日操作建议(具体到基金+方向)
  4. 量化验证层(Tracker)       → 回测: 取未来数据验证，含时序对齐

赛道→基金映射（可操作闭环的关键）:
  科技/AI → 科创50/半导体相关基金
  黄金    → 黄金ETF
  新能源  → 新能源/光伏基金
  ...
"""
import json, re, os
from datetime import date, datetime, timedelta
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path('/opt/data/fund_system_data')
KOL_TRACK_FILE = DATA_DIR / 'kol_track_record.jsonl'

# ─── 赛道 → 对应指数/基金映射（操作建议的桥梁）───
SECTOR_TO_QUOTES = {
    '科技/AI': ['科创50', '半导体', '通信', 'AI', '科技', '人工智能', '算力', '芯片', '大模型', '机器人', 'deepseek', '智能体'],
    '黄金': ['黄金ETF'],
    '资源/周期': ['有色金属', '资源'],
    '新能源': ['新能源', '光伏'],
    '医药': ['医药'],
    '消费': ['消费'],
    '市场整体': ['上证指数', '沪深300', '创业板指'],
}

SECTOR_TO_FUNDS = {
    '科技/AI': [
        ('华夏科创50ETF联接C', '011613', '科创50'),
        ('大摩数字经济混合C', '017103', '科技'),
    ],
    '黄金': [
        ('中银上海金ETF联接C', '009477', '黄金'),
    ],
    '资源/周期': [
        ('大摩资源优选混合(LOF)', '163302', '资源'),
        ('华夏中证电网设备主题ETF联接C', '021448', '电网'),
    ],
    '新能源': [
        ('天弘中证新能源指数增强C', '012895', '新能源'),
        ('天弘中证光伏产业指数C', '013589', '光伏'),
    ],
    '科技/AI(北交所)': [
        ('华夏北证50成份指数C', '017526', '北交所'),
    ],
}

DIRECTION_KEYWORDS = {
    'bullish': ['加仓','补仓','右侧','反弹','抄底','建仓','看多','看好','确定性',
                '吃肉','弹性','格局','扫货','拿住','定投','不慌','机会','突破','启动','反转'],
    'bearish': ['减仓','清仓','风险','警惕','回调','泡沫','过热','出货','砸盘',
                '逃顶','止损','谨慎','离场','回避','空仓','别追','小心','等待','观望','止盈','下行','崩'],
}

TIMEFRAME_KEYWORDS = {
    'today': ['今天','日内','今日','马上','立刻','即将','开盘'],
    'soon': ['本周','明天','短期','近期','近几日','下周','短线'],
    'medium': ['本月','季度','趋势','中线','阶段性'],
    'long': ['长期','年底','明年','下半年','布局'],
}


class Extractor:
    """信号提取 — 不仅看关键词，还提取断言的事实基础"""

    @staticmethod
    def extract(text: str, kol_name: str = "") -> list[dict]:
        signals = []
        text_lower = text.lower()

        for sector, sector_kws in SECTOR_TO_QUOTES.items():
            # 赛道检测：用扩展关键词
            all_kws = sector_kws + {
                '科技/AI': ['AI','人工智能','算力','芯片','半导体','大模型','机器人','deepseek','智能体'],
                '黄金': ['黄金','金价','贵金属','Au'],
                '资源/周期': ['资源','周期','铜','铝','锂','稀土','煤炭','钢铁'],
                '新能源': ['新能源','光伏','锂电','电池','储能','电车'],
                '医药': ['医药','医疗','创新药','CXO'],
                '消费': ['消费','白酒','食品','零售'],
                '市场整体': ['大盘','指数','行情','市场','A股','创业板','科创板','流动性','资金','政策'],
            }.get(sector, sector_kws)

            matched = [kw for kw in all_kws if kw.lower() in text_lower]
            if not matched:
                continue

            # 方向
            direction = 'neutral'
            for d, kws in DIRECTION_KEYWORDS.items():
                if any(kw.lower() in text_lower for kw in kws):
                    direction = d
                    break

            # 时效（区分"今天操作" vs "长期趋势"）
            timeframe = 'soon'
            for tf, kws in TIMEFRAME_KEYWORDS.items():
                if any(kw.lower() in text_lower for kw in kws):
                    timeframe = tf
                    break

            # 置信度
            confidence = min(len(matched) * 10 + (30 if direction != 'neutral' else 0), 95)

            # 提取断言原文
            claim = Extractor._claim_sentence(text, matched)

            signals.append({
                'sector': sector,
                'direction': direction,
                'timeframe': timeframe,
                'claim': claim or text[:120],
                'confidence': confidence,
                'matched': matched,
                'kol': kol_name,
            })

        return signals

    @staticmethod
    def _claim_sentence(text, keywords):
        """提取含关键词的断言句（找最像观点的句子）"""
        sents = re.split(r'[。！？\n]', text)
        # 优先找同时含方向词的句子
        for sent in sents:
            has_kw = any(kw.lower() in sent.lower() for kw in keywords)
            has_dir = any(d for d_kws in DIRECTION_KEYWORDS.values() for d in d_kws if d.lower() in sent.lower())
            if has_kw and has_dir:
                return sent.strip()[:150]
        # 回退：只要有赛道关键词
        for sent in sents:
            if any(kw.lower() in sent.lower() for kw in keywords):
                return sent.strip()[:150]
        return text[:150]


class Verifier:
    """事实核查 — 对齐市场数据做验证"""

    # 赛道→可能的数据key映射（从腾讯回调数据里匹配）
    SECTOR_DATA_MAP = {
        '科技/AI': ['科创50', '半导体', '通信', '创业板指'],
        '黄金': ['黄金ETF市场价', '黄金ETF'],
        '资源/周期': ['有色金属'],
        '新能源': ['新能源', '光伏'],
        '医药': ['医药'],
        '消费': ['消费'],
        '市场整体': ['上证指数', '沪深300'],
    }

    @staticmethod
    def verify_signal(signal: dict, quotes: dict) -> dict:
        """验证单条信号（使用当日实际行情数据）"""
        # 找匹配的行情key
        candidates = Verifier.SECTOR_DATA_MAP.get(signal['sector'], [])
        best_key = None
        best_change = 0
        for c in candidates:
            for qkey, qdata in quotes.items():
                if c.lower() in qkey.lower():
                    change = float(qdata.get('change_pct', 0))
                    if abs(change) > abs(best_change):
                        best_change = change
                        best_key = qkey

        if best_key is None:
            return {'verified': False, 'reason': f'无行情数据匹配{signal["sector"]}'}

        actual_dir = 'bullish' if best_change > 0 else ('bearish' if best_change < 0 else 'neutral')
        predicted_dir = signal['direction']
        correct = (predicted_dir == actual_dir) if predicted_dir != 'neutral' else None

        return {
            'verified': True,
            'correct': correct,
            'predicted': predicted_dir,
            'actual': actual_dir,
            'actual_change': best_change,
            'matched_quote': best_key,
        }

    @staticmethod
    def fact_check_all(signals: list[dict], quotes: dict) -> list[dict]:
        """批量核查 + 统计"""
        results = []
        for s in signals:
            r = Verifier.verify_signal(s, quotes)
            results.append({**s, 'verification': r})
        return results

    @staticmethod
    def verify_from_file(date_str: str = None):
        """从历史记录重新核查（收盘后/次日用真实数据）"""
        if date_str is None:
            date_str = (date.today() - timedelta(days=1)).isoformat()

        if not KOL_TRACK_FILE.exists():
            return []

        records = []
        with open(KOL_TRACK_FILE) as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    if r.get('date') == date_str:
                        records.append(r)

        return records


class Mapper:
    """操作映射 — 信号→具体基金操作建议"""

    @staticmethod
    def to_actions(signals: list[dict]) -> list[dict]:
        """将当日信号转为可执行操作"""
        # 清理：只保留"today"或高置信度的信号
        today_signals = [s for s in signals
                        if s.get('timeframe') in ('today', 'soon')
                        and s['direction'] != 'neutral'
                        and s['confidence'] >= 30]

        if not today_signals:
            return []

        # 按赛道聚合净方向
        sector_net = defaultdict(int)
        sector_conf = defaultdict(list)
        for s in today_signals:
            net = 1 if s['direction'] == 'bullish' else -1
            sector_net[s['sector']] += net
            sector_conf[s['sector']].append(s['confidence'])

        actions = []
        for sector, net in sorted(sector_net.items(), key=lambda x: -abs(x[1])):
            avg_conf = sum(sector_conf[sector]) / len(sector_conf[sector])

            # 确定操作方向
            if net >= 2:
                action = '加仓'
                direction = 'buy'
            elif net >= 1:
                action = '增持'
                direction = 'buy'
            elif net <= -2:
                action = '减仓'
                direction = 'sell'
            elif net <= -1:
                action = '减持'
                direction = 'sell'
            else:
                continue  # 分歧太大，不出操作

            # 映射到具体基金
            target_funds = SECTOR_TO_FUNDS.get(sector, [])
            fund_details = []
            for fname, fcode, ftag in target_funds:
                fund_details.append({
                    'name': fname,
                    'code': fcode,
                    'tag': ftag,
                    'suggested_action': direction,
                    'suggested_pct': '5%' if abs(net) >= 2 else '3%',  # 力度
                })

            actions.append({
                'sector': sector,
                'action': action,
                'direction': direction,
                'net_sentiment': net,
                'confidence': round(avg_conf),
                'signal_count': len(sector_conf[sector]),
                'reason': Mapper._reason(sector, net, direction, avg_conf),
                'funds': fund_details,
                'source_kols': list(set(s['kol'] for s in today_signals if s['sector'] == sector)),
            })

        return actions

    @staticmethod
    def _reason(sector, net, direction, confidence):
        if direction == 'buy':
            return f"多KOL看多{sector}(净{net:+d}, 置信度{confidence}%), 可关注增持"
        else:
            return f"多KOL看空{sector}(净{net:+d}, 置信度{confidence}%), 注意减仓风险"


def analyze(texts: list[str], quotes: dict = None, kol_name: str = "KOL") -> dict:
    """完整分析入口"""
    if quotes is None:
        quotes = {}

    all_signals = []
    for text in texts:
        sigs = Extractor.extract(text, kol_name)
        all_signals.extend(sigs)

    # 事实核查（如果有行情数据）
    if quotes:
        verified = Verifier.fact_check_all(all_signals, quotes)
    else:
        verified = all_signals

    # 操作建议
    actions = Mapper.to_actions(verified)

    return {
        'signals': verified,
        'actions': actions,
        'signal_count': len(verified),
        'action_count': len(actions),
    }


def analyze_from_kol_data(kol_data: dict, quotes: dict = None) -> dict:
    """从KOL采集数据运行完整分析"""
    if quotes is None:
        quotes = {}

    all_signals = []
    for uid, info in kol_data.items():
        name = info.get('name', '未知')
        posts = info.get('posts', [])
        for p in posts:
            sigs = Extractor.extract(p.get('text', ''), name)
            for s in sigs:
                s['post_id'] = p.get('id', '')
                s['post_time'] = p.get('created_at', '')
            all_signals.extend(sigs)

    # 事实核查
    verified = Verifier.fact_check_all(all_signals, quotes)

    # 操作建议
    actions = Mapper.to_actions(verified)

    return {
        'signals': verified,
        'actions': actions,
        'signal_count': len(verified),
        'action_count': len(actions),
        'analysis_time': datetime.now().isoformat(),
    }


def format_push(analysis: dict) -> str:
    """格式化推送（含操作建议+事实核查）"""
    lines = []

    # === 操作建议（最前面）===
    if analysis['actions']:
        lines.append("📋 **KOL信号 → 今日操作建议**")
        lines.append("| 赛道 | 建议 | 置信度 | 涉及基金 |")
        lines.append("|:----|:----:|:------:|:---------|")
        for a in analysis['actions']:
            emoji = '🔴' if a['direction'] == 'buy' else '🟢'
            funds_str = '、'.join(f"{f['code']}({f['suggested_pct']})" for f in a['funds'][:3])
            lines.append(f"| {a['sector']} | {emoji}{a['action']} | {a['confidence']}% | {funds_str} |")
        lines.append("")

    # === 信号摘要 ===
    non_neutral = [s for s in analysis['signals'] if s['direction'] != 'neutral']
    if non_neutral:
        lines.append("🔍 **当日信号摘要**")
        for s in non_neutral[:8]:
            d = '📈' if s['direction'] == 'bullish' else '📉'
            v = s.get('verification', {})
            v_tag = ''
            if v.get('verified'):
                if v.get('correct') == True:
                    v_tag = ' ✅'
                elif v.get('correct') == False:
                    v_tag = ' ❌'
                elif v.get('correct') is None:
                    v_tag = ' ➖'
            lines.append(f"  [{s['kol']}]{d} {s['sector']}({s['timeframe']}){v_tag}")
            lines.append(f"    {s['claim'][:80]}")
        lines.append("")

    # === 统计 ===
    lines.append("📊 **今日KOL统计**")
    lines.append(f"  信号总数: {analysis['signal_count']}")
    lines.append(f"  含方向信号: {len(non_neutral)}")
    lines.append(f"  可操作建议: {analysis['action_count']}")
    lines.append(f"  分析时间: {analysis.get('analysis_time', '')[:19]}")
    lines.append("")

    return '\n'.join(lines)
