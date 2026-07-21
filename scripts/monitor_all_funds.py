#!/usr/bin/env python3
"""
=== 基金全盘监控分析系统 ===
monitor_all_funds.py — 覆盖全部13只基金的实时分析与操作建议

分析框架（6个维度）：
  1. 市场全景 — 大盘指数、涨跌家数、北向资金、外盘
  2. 板块热度 — 10个行业ETF涨跌排行与振幅
  3. 组别趋势 — 4个持仓组的N日趋势与操作评分
  4. 逐基诊断 — 每只基金的估值、趋势、量价信号、操作建议
  5. 组合平衡 — 权重偏离检查、再平衡建议
  6. 量价信号 — 放量/缩量异常信号汇总

使用方法：
  python3 /opt/data/scripts/monitor_all_funds.py              # 完整分析
  python3 /opt/data/scripts/monitor_all_funds.py --json       # JSON输出
  python3 /opt/data/scripts/monitor_all_funds.py --funds-only  # 仅基金诊断
  python3 /opt/data/scripts/monitor_all_funds.py --groups-only # 仅组别分析
"""

import sys
import os
import json
from datetime import datetime, date, timedelta
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# 确保 fund_tools.py 在路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ''))
import fund_tools as ft


# ══════════════════════════════════════════════
# 分析框架核心
# ══════════════════════════════════════════════

class FundAnalyzer:
    """基金全盘分析器"""

    def __init__(self):
        self.today = date.today()
        self.today_str = self.today.isoformat()
        self.collected = {}          # 所有采集数据
        self.errors = []             # 采集错误
        self.warnings = []           # 分析警告
        self.fund_analyses = []      # 逐基分析结果
        self.group_analyses = []     # 组别分析结果

    # ── 数据采集 ──────────────────────────────

    def collect_all(self, fast: bool = False, quiet: bool = False):
        """采集所有数据源（并行）"""
        out = open(os.devnull, 'w') if quiet else sys.stderr
        print("=" * 60, file=out)
        print(f"📡 数据采集开始 — {self.today_str}", file=out)
        print("=" * 60, file=out)

        results = {}

        # 阶段1: 基金净值 + 大盘指数（并行）
        print("\n📊 阶段1: 基金净值 + 大盘指数", file=out)
        with ThreadPoolExecutor(max_workers=8) as exc:
            futures = {}

            # 所有基金净值
            for code, name in ft.FUND_CODES.items():
                futures[exc.submit(ft.get_fund_value, code)] = ('fund', code, name)

            # 大盘指数
            for idx_name, idx_code in ft.QUOTES.items():
                futures[exc.submit(ft.get_tencent_quote, idx_code)] = ('quote', idx_name, idx_code)

            # 收集结果
            fund_data = {}
            quote_data = {}
            for f in as_completed(futures):
                kind, key, meta = futures[f]
                try:
                    val = f.result()
                except Exception as e:
                    self.errors.append(f"{kind}:{key}:{e}")
                    val = None

                if kind == 'fund':
                    fund_data[key] = val
                    if val:
                        print(f"  ✅ [{val['name']}] 净值={val['nav']}  估算涨跌={val.get('estimated_change', '?')}%", file=out)
                    else:
                        print(f"  ❌ [{meta}] 获取失败", file=out)
                        self.errors.append(f"基金{key}:{meta}:无数据")
                elif kind == 'quote':
                    quote_data[key] = val
                    if val:
                        print(f"  ✅ {key}: {val['price']} ({val['change_pct']}%)", file=out)
                    else:
                        print(f"  ❌ {key}: 获取失败", file=out)
                        self.errors.append(f"指数{key}:无数据")

        results['funds'] = fund_data
        results['quotes'] = quote_data

        # 阶段2: 板块 + 市场总览 + 北向 + 外盘（全部并行）
        if not fast:
            print("\n📊 阶段2: 板块 + 市场总览 + 北向资金 + 外盘", file=out)
            with ThreadPoolExecutor(max_workers=4) as exc:
                f_sector = exc.submit(ft.get_sector_quotes)
                f_market = exc.submit(ft.get_market_overview)
                f_north = exc.submit(ft.get_northbound_flow)
                f_overnight = exc.submit(ft.get_overnight_quotes)

                results['sectors'] = f_sector.result()
                results['market_overview'] = f_market.result()
                results['northbound'] = f_north.result()
                results['overnight'] = f_overnight.result()
        else:
            results['sectors'] = {}
            results['market_overview'] = {}
            results['northbound'] = {}
            results['overnight'] = {}

        self.collected = results
        return results

    # ── 逐基诊断（框架核心）──────────────────

    def analyze_individual_fund(self, code: str, name: str, fund_val: dict,
                                 group_name: str, group_trend: list,
                                 quotes: dict, sectors: dict,
                                 volume_signals: list) -> dict:
        """
        对单只基金进行多维度诊断，生成操作建议。

        诊断维度：
          D1 — 今日估值变化
          D2 — 近3日组别趋势
          D3 — 组内相对表现（vs组平均）
          D4 — 关联板块/指数表现
          D5 — 量价信号
          D6 — 综合操作建议
        """
        analysis = {
            'code': code,
            'name': name,
            'group': group_name,
            'nav': fund_val.get('nav', '?'),
            'estimated_nav': fund_val.get('estimated_nav', '?'),
            'estimated_change': fund_val.get('estimated_change', '0'),
            'nav_date': fund_val.get('nav_date', ''),
            'dimensions': {},
            'signals': [],
            'recommendation': '持有',
            'urgency': '低',
            'score': 0,
        }

        try:
            change_pct = float(analysis['estimated_change'] or 0)
        except (ValueError, TypeError):
            change_pct = 0

        # 修正黄金联接基金（009478）无实时估算的问题：用黄金ETF市价替代
        # 仅在API确认为0.00%（且非刚开盘时）才触发
        if code == '009478' and abs(change_pct) < 0.005 and quotes:
            # 先检查是否交易时段刚开盘（9:30-10:00），此时API可能延迟
            now = datetime.now()
            bj_min = (now.hour + 8) % 24 * 60 + now.minute
            if 565 <= bj_min <= 600:  # 9:25-10:00 BJT，延迟正常，等下次刷新
                gold_etf = quotes.get('黄金ETF市场价')
                if gold_etf:
                    try:
                        g_change = float(gold_etf.get('change_pct', 0) or 0)
                        if abs(g_change) >= 0.005:  # 黄金ETF确实有变动
                            change_pct = g_change
                            analysis['estimated_change'] = str(g_change)
                            analysis['dimensions']['D1_今日估值'] = f"黄金ETF{g_change:+.2f}%（替代基金估算）"
                    except (ValueError, TypeError):
                        pass
            else:
                # 非开盘初期，gszzl=0.00说明确实无估算，用黄金ETF替代
                gold_etf = quotes.get('黄金ETF市场价')
                if gold_etf:
                    try:
                        change_pct = float(gold_etf.get('change_pct', 0) or 0)
                        analysis['estimated_change'] = str(change_pct)
                        analysis['dimensions']['D1_今日估值'] = f"黄金ETF{change_pct:+.2f}%（替代基金估算）"
                    except (ValueError, TypeError):
                        pass
        if change_pct > 2.0:
            d1 = f"大涨{change_pct:+.2f}%"
            analysis['signals'].append('📈 今日大涨')
            analysis['score'] += 1
        elif change_pct > 0.5:
            d1 = f"上涨{change_pct:+.2f}%"
            analysis['signals'].append('📈 温和上涨')
        elif change_pct < -2.0:
            d1 = f"大跌{change_pct:+.2f}%"
            analysis['signals'].append('📉 今日大跌')
            analysis['score'] -= 1
        elif change_pct < -0.5:
            d1 = f"下跌{change_pct:+.2f}%"
            analysis['signals'].append('📉 温和下跌')
        else:
            d1 = f"微幅波动{change_pct:+.2f}%"
        analysis['dimensions']['D1_今日估值'] = d1

        # D2: 组别趋势（近3日）
        if group_trend and len(group_trend) >= 2:
            recent = [c for _, c in group_trend[-3:]]
            avg_recent = sum(recent) / len(recent)
            streak = self._trend_streak(group_trend)
            if avg_recent > 1.5:
                d2 = f"近3日均涨{avg_recent:+.2f}% — 强势上升"
                analysis['signals'].append(f'🔥 {streak}')
                analysis['score'] += 1
            elif avg_recent > 0.5:
                d2 = f"近3日均涨{avg_recent:+.2f}% — 温和上行"
            elif avg_recent < -1.5:
                d2 = f"近3日均跌{avg_recent:+.2f}% — 持续回调"
                analysis['signals'].append(f'💧 {streak}')
                analysis['score'] -= 1
            elif avg_recent < -0.5:
                d2 = f"近3日均跌{avg_recent:+.2f}% — 弱势下行"
                analysis['score'] -= 0.5
            else:
                d2 = f"近3日均{avg_recent:+.2f}% — 震荡整理"
            d2 += f" | {streak}"
        else:
            d2 = "趋势数据不足"
        analysis['dimensions']['D2_组别趋势'] = d2

        # D3: 组内相对表现
        analysis['dimensions']['D3_组内表现'] = self._relative_performance(
            code, group_name, change_pct, analysis)

        # D4: 关联板块/指数
        analysis['dimensions']['D4_关联标的'] = self._related_market(
            group_name, quotes, sectors, analysis)

        # D5: 量价信号
        analysis['dimensions']['D5_量价信号'] = self._volume_signal(
            group_name, code, volume_signals, analysis)

        # D6: 综合判定
        analysis = self._final_recommendation(analysis, change_pct)

        return analysis

    def _trend_streak(self, trend_data: list) -> str:
        """计算连续涨跌天数（自动去重同一天多次快照，保留最新）"""
        # 按日期去重，保留每天最新一条
        deduped = {}
        for d, c in trend_data:
            deduped[d] = c  # 后出现的覆盖前面的（最新快照）
        changes = [c for d, c in sorted(deduped.items())]
        if not changes:
            return "无趋势数据"
        streak = 0
        direction = 'up' if changes[-1] > 0 else 'down'
        for c in reversed(changes):
            if (direction == 'up' and c > 0) or (direction == 'down' and c < 0):
                streak += 1
            else:
                break
        if direction == 'up':
            return f"连涨{streak}日" if streak >= 2 else "近日收涨"
        else:
            return f"连跌{streak}日" if streak >= 2 else "近日收跌"

    def _relative_performance(self, code: str, group_name: str,
                               change_pct: float, analysis: dict) -> str:
        """计算基金在组内的相对表现（基于组平均）"""
        # 从已采集的基金数据中计算组平均
        fund_data = self.collected.get('funds', {})
        group_codes = ft.GROUPS.get(group_name, [])
        if not group_codes:
            return "无组数据"

        total = 0.0
        count = 0
        best_change = -999
        worst_change = 999
        best_code = ''
        worst_code = ''

        for gc in group_codes:
            fv = fund_data.get(gc)
            if not fv:
                continue
            try:
                gc_pct = float(fv.get('estimated_change', 0) or 0)
            except (ValueError, TypeError):
                continue
            total += gc_pct
            count += 1
            if gc_pct > best_change:
                best_change, best_code = gc_pct, gc
            if gc_pct < worst_change:
                worst_change, worst_code = gc_pct, gc

        if count == 0:
            return "无组数据"

        avg = total / count
        diff = change_pct - avg

        # 排名
        all_changes = []
        for gc in group_codes:
            fv = fund_data.get(gc)
            if fv:
                try:
                    all_changes.append((gc, float(fv.get('estimated_change', 0) or 0)))
                except (ValueError, TypeError):
                    pass
        all_changes.sort(key=lambda x: x[1], reverse=True)
        rank = next((i+1 for i, (c, _) in enumerate(all_changes) if c == code), count)

        if diff > 1.0:
            perf = f"🏅 超组均{diff:+.2f}% (排名{rank}/{count})"
            analysis['signals'].append(f'🏅 组内领先(排名{rank}/{count})')
            analysis['score'] += 0.5
        elif diff > 0:
            perf = f"📈 略超组均{diff:+.2f}% (排名{rank}/{count})"
        elif diff > -1.0:
            perf = f"📉 略低于组均{diff:+.2f}% (排名{rank}/{count})"
        else:
            perf = f"🚩 落后组均{diff:+.2f}% (排名{rank}/{count})"
            analysis['signals'].append(f'🚩 组内落后(排名{rank}/{count})')
            analysis['score'] -= 0.5

        return f"{perf} | 组均值{avg:+.2f}% | 最佳={ft.FUND_CODES.get(best_code, best_code)}({best_change:+.2f}%)"

    def _related_market(self, group_name: str, quotes: dict,
                         sectors: dict, analysis: dict) -> str:
        """查找关联板块/指数表现"""
        mapping = {
            '黄金':     ('黄金ETF市场价', 'quotes'),
            '科技/AI':  ('科创50', 'quotes'),
            '资源/周期': ('有色金属', 'sectors'),
            '新能源':   ('新能源', 'sectors'),
        }

        info = mapping.get(group_name)
        if not info:
            return "无关联标的"

        key, source = info
        data_source = quotes if source == 'quotes' else sectors
        q = data_source.get(key) if data_source else None

        if not q:
            # 尝试 sector 回退
            if source == 'quotes':
                q = sectors.get(key)
            elif source == 'sectors':
                q = quotes.get(key)

        if not q:
            return f"{key}: 数据缺失"

        try:
            cp = float(q['change_pct'])
            name = q.get('name', key)
        except (ValueError, TypeError):
            return f"{key}: 数据异常"

        if cp > 1.5:
            r = f"🔴 {key}: {cp:+.2f}% — 强势"
            analysis['signals'].append(f'🔴 关联{key}走强({cp:+.2f}%)')
            analysis['score'] += 0.5
        elif cp > 0:
            r = f"🟢 {key}: {cp:+.2f}% — 偏强"
        elif cp < -1.5:
            r = f"🟢 {key}: {cp:+.2f}% — 弱势"
            analysis['signals'].append(f'🟢 关联{key}走弱({cp:+.2f}%)')
            analysis['score'] -= 0.5
        elif cp < 0:
            r = f"🟢 {key}: {cp:+.2f}% — 偏弱"
        else:
            r = f"🟡 {key}: {cp:+.2f}% — 平盘"

        return r

    def _volume_signal(self, group_name: str, code: str,
                        volume_signals: list, analysis: dict) -> str:
        """从量价信号中查找相关信号"""
        if not volume_signals:
            return "无量价数据"

        # 查找组相关指数/板块的量价信号
        mapping = {
            '黄金':     ['黄金ETF市场价'],
            '科技/AI':  ['科创50', '半导体'],
            '资源/周期': ['有色金属', '上证指数'],
            '新能源':   ['新能源', '光伏'],
        }
        keys = mapping.get(group_name, [])

        relevant = []
        for vs in volume_signals:
            if vs['name'] in keys:
                relevant.append(vs)

        if not relevant:
            # 找最接近的
            for vs in volume_signals:
                if '黄金' in vs['name'] or '科创' in vs['name'] or \
                   '有色' in vs['name'] or '新能源' in vs['name'] or \
                   '光伏' in vs['name'] or '半导体' in vs['name']:
                    relevant.append(vs)
                if len(relevant) >= 1:
                    break

        if not relevant:
            return "无关联量价信号"

        parts = []
        for vs in relevant[:2]:
            emoji = vs.get('emoji', '➖')
            sig = vs.get('signal', '')
            amp = vs.get('amplitude', 0)
            parts.append(f"{emoji} {vs['name']}: {sig}(振幅{amp}%)")

            if '上攻' in sig or '反弹' in sig:
                analysis['signals'].append(f'📊 量价:{vs["name"]}{sig}')
                analysis['score'] += 0.5
            elif '下跌' in sig or '阴跌' in sig:
                analysis['signals'].append(f'📊 量价:{vs["name"]}{sig}')
                analysis['score'] -= 0.5

        return ' | '.join(parts)

    def _final_recommendation(self, analysis: dict, change_pct: float) -> dict:
        """综合所有维度生成最终操作建议"""

        score = analysis['score']

        # 调整阈值
        if score >= 3:
            analysis['recommendation'] = '🟢 增持'
            analysis['urgency'] = '高'
        elif score >= 1.5:
            analysis['recommendation'] = '🟢 关注'
            analysis['urgency'] = '中'
        elif score >= 0.5:
            analysis['recommendation'] = '🟡 持有偏多'
            analysis['urgency'] = '低'
        elif score >= -0.5:
            analysis['recommendation'] = '🟡 持有'
            analysis['urgency'] = '低'
        elif score >= -1.5:
            analysis['recommendation'] = '🟠 观望'
            analysis['urgency'] = '中'
        elif score >= -3:
            analysis['recommendation'] = '🔴 减仓观望'
            analysis['urgency'] = '高'
        else:
            analysis['recommendation'] = '🔴 减持'
            analysis['urgency'] = '高'

        # 单日极端涨跌的特殊处理
        if change_pct >= 5:
            analysis['recommendation'] = '🔴 大涨减仓'
            analysis['urgency'] = '高'
            analysis['signals'].append('⚠️ 单日涨幅≥5%，注意短期回调风险')
        elif change_pct <= -5:
            analysis['recommendation'] = '🟢 大跌关注'
            analysis['urgency'] = '高'
            analysis['signals'].append('⚠️ 单日跌幅≥5%，可能超跌反弹机会')

        return analysis

    # ── 全量分析 ──────────────────────────────

    def run_full_analysis(self):
        """运行完整分析流程"""
        results = self.collected
        if not results:
            self.collect_all()

        fund_data = results.get('funds', {})
        quotes = results.get('quotes', {})
        sectors = results.get('sectors', {})
        market = results.get('market_overview', {})

        # 量价分析
        volume_analysis = ft.get_volume_analysis(quotes, sectors)
        volume_signals = volume_analysis.get('volume_signals', [])

        # 组别聚合
        groups = ft.group_funds(fund_data)
        # print(f"\n📊 组别聚合: {len([g for g in groups if groups[g]['count'] > 0])}个活跃组")

        # 从日志加载前日建议（供稳定性逻辑）
        prev_actions = {}
        try:
            log_path = '/tmp/fund_data/_suggestion_log.json'
            if os.path.exists(log_path):
                with open(log_path) as f:
                    slog = json.load(f)
                dates = sorted(slog.keys())
                if dates and dates[-1] != self.today_str:
                    prev = slog[dates[-1]]
                elif len(dates) >= 2:
                    prev = slog[dates[-2]]
                else:
                    prev = None
                if prev:
                    for gname, gd in prev.get('groups', {}).items():
                        prev_actions[gname] = gd.get('action', '持有')
        except Exception:
            pass

        # 逐组分析
        group_scores = {}
        for gname, gdata in groups.items():
            if gdata['count'] == 0:
                continue
            trend = ft.get_group_trend(gname, days=5)
            score_result = ft.score_group_action(gname, quotes, sectors, [], trend,
                                                  prev_action=prev_actions.get(gname))
            group_scores[gname] = score_result

            ga = {
                'group': gname,
                'avg_change': gdata['avg_change'],
                'count': gdata['count'],
                'trend': trend,
                'score': score_result['score'],
                'action': score_result['action'],
                'urgency': score_result['urgency'],
                'reasons': score_result['reasons'],
                'funds': gdata['funds'],
            }
            self.group_analyses.append(ga)

        # 逐基诊断
        for code, name in ft.FUND_CODES.items():
            fv = fund_data.get(code)
            if not fv:
                self.warnings.append(f"基金{code}无数据，跳过诊断")
                continue

            # 确定组别
            group_name = '未分组'
            for gn, codes in ft.GROUPS.items():
                if code in codes:
                    group_name = gn
                    break

            group_trend = ft.get_group_trend(group_name, days=5) if group_name != '未分组' else []

            fa = self.analyze_individual_fund(
                code, name, fv, group_name, group_trend,
                quotes, sectors, volume_signals
            )
            self.fund_analyses.append(fa)

        # 再平衡检查
        self.rebalance_alerts = ft.check_rebalance(fund_data)

        return {
            'fund_analyses': self.fund_analyses,
            'group_analyses': self.group_analyses,
            'rebalance_alerts': self.rebalance_alerts,
            'volume_analysis': volume_analysis,
        }

    # ── 格式化输出 ────────────────────────────

    def print_report(self):
        """打印完整的分析报告"""
        print("\n")
        print("=" * 72)
        print(f"  📊 基金全盘监控分析报告")
        print(f"  📅 {self.today_str} ({self._weekday_cn()})  |  {datetime.now().strftime('%H:%M:%S')}")
        print(f"  📋 覆盖: 13只基金 | 4个组别")
        print("=" * 72)

        self._print_market_overview()
        self._print_sector_heatmap()
        self._print_group_summary()
        self._print_fund_diagnostics()
        self._print_rebalance()
        self._print_volume_summary()
        self._verify_previous_suggestions()  # 验证前日建议
        self._print_summary()
        self._save_suggestion_log()          # 保存今日建议供明日验证

    def _weekday_cn(self):
        wd = ['周一','周二','周三','周四','周五','周六','周日']
        return wd[self.today.weekday()]

    def _fmt_pct(self, val):
        try:
            p = float(val)
            return f"{p:+.2f}%"
        except (ValueError, TypeError):
            return str(val)

    def _print_market_overview(self):
        """市场全景（表格版）"""
        quotes = self.collected.get('quotes', {})
        market = self.collected.get('market_overview', {})
        north = self.collected.get('northbound', {})
        overnight = self.collected.get('overnight', {})

        print("\n【1】市场全景")

        # 指数表格
        print("\n📈 主要指数:")
        print("| 指数 | 点位 | 涨跌 |")
        print("|:----|:---:|:----:|")
        for name in ['上证指数', '创业板指', '科创50', '沪深300', '上证50', '黄金ETF市场价']:
            q = quotes.get(name)
            if q:
                cp = float(q['change_pct'])
                emoji = '🔴' if cp > 0 else '🟢' if cp < 0 else '🟡'
                print(f"| {name} | {q['price']} | {emoji} {q['change_pct']}% |")
            else:
                print(f"| {name} | — | 无数据 |")

        # 涨跌家数 + 成交额
        if market:
            rc = market.get('rise_count')
            fc = market.get('fall_count')
            lu = market.get('limit_up')
            ld = market.get('limit_down')
            tt = market.get('total_turnover', 0)

            print()
            if rc is not None:
                sentiment = ft.grade_market_sentiment(rc, fc, lu, ld)
                print(f"  📊 市场情绪: {sentiment}")
            if tt:
                print(f"  💰 两市成交: {tt/1e8:.0f}亿")
            if lu is not None or ld is not None:
                print(f"  📈 涨停{lu or '?'}家 / 跌停{ld or '?'}家")
        else:
            print(f"  ⚠️ 市场总览数据缺失")

        # 北向
        if north.get('total') is not None:
            emoji = '🔴' if north['total'] > 0 else '🟢' if north['total'] < 0 else '🟡'
            stale_flag = ' ⚠️(缓存)' if north.get('stale') else ''
            print(f"  {emoji} 北向: {north['total']:+.2f}亿 (沪{north.get('hgt', 0):+.2f} 深{north.get('sgt', 0):+.2f}){stale_flag}")

        # 外盘表格
        if overnight:
            print("\n🌙 隔夜外盘:")
            print("| 品种 | 收盘 | 涨跌 |")
            print("|:----|:---:|:----:|")
            for name in ['道琼斯', '标普500', '纳斯达克', '黄金期货', '美元指数', '恒生指数', '韩国KOSPI']:
                q = overnight.get(name)
                if q:
                    emoji = '🔴' if q['change_pct'] > 0 else '🟢' if q['change_pct'] < 0 else '🟡'
                    print(f"| {name} | {q['price']} | {emoji} {q['change_pct']:+.2f}% |")

    def _print_sector_heatmap(self):
        """板块热度（表格版）"""
        sectors = self.collected.get('sectors', {})
        if not sectors:
            return

        print("\n【2】板块热度排行")
        sorted_sectors = sorted(
            [(k, v) for k, v in sectors.items() if v],
            key=lambda x: -x[1]['change_pct']
        )

        print("\n| 板块 | 涨跌 | 振幅 | 量价信号 |")
        print("|:----|:----:|:----:|:--------:|")
        for name, q in sorted_sectors:
            cp = q['change_pct']
            emoji = '🔴' if cp > 0 else '🟢' if cp < 0 else '🟡'
            amp = q.get('amplitude', 0)
            amp_str = f"{amp:.1f}%" if amp else '—'
            # 热度条
            abs_pct = min(abs(cp), 5)
            filled = int(abs_pct / 5 * 10)
            bar = '█' * filled + '░' * (10 - filled)
            vol_signal = '放量' if amp > 3 else '温和' if amp > 1.5 else '缩量'
            direction = '📈' if cp > 0 else '📉'
            print(f"| {emoji} {name} | {cp:+.2f}%{bar} | {amp_str} | {vol_signal} {direction} |")

    def _heat_bar(self, pct, width=20):
        """热度条"""
        abs_pct = min(abs(pct), 5)
        filled = int(abs_pct / 5 * width)
        if pct > 0:
            return '█' * filled + '░' * (width - filled)
        else:
            return '░' * (width - filled) + '█' * filled

    def _print_group_summary(self):
        """组别总结（表格版）"""
        if not self.group_analyses:
            return

        # 计算真实持仓权重
        fund_data = self.collected.get('funds', {})
        actual_weights = ft.calc_group_actual_weights(fund_data) if fund_data else {}
        has_actual = bool(actual_weights)

        print("\n【3】组别趋势与操作评分")

        # 汇总表
        print("\n| 组别 | 支 | 均值 | 评分 | 建议 | 权重 |")
        print("|:----|:--:|:----:|:---:|:----:|:----:|")
        for ga in sorted(self.group_analyses, key=lambda x: -x['score']):
            gname = ga['group']
            avg = ga['avg_change']
            score = ga['score']
            action = ga['action']
            action_emoji = {'增持': '🟢', '关注': '🟢', '持有': '🟡', '观望': '🔴', '减持': '🔴'}.get(action, '🟡')
            # 显示实际权重(如果有) 或 目标权重
            if has_actual and gname in actual_weights:
                w = f"{actual_weights[gname]['pct']}%"
            else:
                w = f"{ft.PORTFOLIO_WEIGHTS.get(gname, {}).get('weight', '?')}%"
            print(f"| {gname} | {ga['count']} | {avg:+.2f}% | {score:+d} | {action_emoji}{action} | {w} |")

        # 各组详情（趋势+前3基金）
        for ga in sorted(self.group_analyses, key=lambda x: -x['score']):
            gname = ga['group']
            avg = ga['avg_change']
            score = ga['score']
            action = ga['action']

            print(f"\n📁 {gname} 评分{score:+d} {action}  (均值{avg:+.2f}%)")

            # 趋势
            trend = ga.get('trend', [])
            if trend:
                vals = [c for _, c in trend[-5:]]
                trend_str = ' → '.join(f"{c:+.2f}%" for c in vals)
                print(f"  趋势: {trend_str}")

            # 组内基金
            funds = ga.get('funds', [])
            if funds:
                for f in sorted(funds, key=lambda x: -(float(x.get('estimated_change', 0) or 0))):
                    chg = self._fmt_pct(f.get('estimated_change', 0))
                    print(f"  {f['code']} {f['name'][:18]} {chg}")

            # 评分理由
            reasons = ga.get('reasons', [])
            if reasons:
                for r in reasons:
                    print(f"  📝 {r}")

    def _print_fund_diagnostics(self):
        """逐基诊断"""
        if not self.fund_analyses:
            print("\n  ⚠️ 无基金诊断数据")
            return

        print("\n【4】逐基诊断（按操作建议排序）\n")

        # 按紧迫度 + 评分排序
        urgency_order = {'高': 0, '中': 1, '低': 2}
        sorted_fa = sorted(self.fund_analyses,
                          key=lambda x: (urgency_order.get(x['urgency'], 9), -x['score']))

        print("| 代码 | 名称 | 组别 | 估值 | 评分 | 紧迫度 | 建议 |")
        print("|:----|:----|:----:|:----:|:---:|:-----:|:----:|")
        for fa in sorted_fa:
            code = fa['code']
            name = fa['name'][:16]
            group = fa['group'][:6]
            chg = self._fmt_pct(fa['estimated_change'])
            score = f"{fa['score']:+.1f}"
            rec = fa['recommendation']
            urg = fa['urgency']
            urg_icon = {'高': '🔴', '中': '🟡', '低': '🟢'}.get(urg, '')
            print(f"| {code} | {name} | {group} | {chg} | {score} | {urg_icon}{urg} | {rec} |")

        # 详细信号（完整数据+格式美观）
        has_signals = any(fa['signals'] for fa in sorted_fa)
        if has_signals:
            print("\n" + "─" * 40)
            print("📌 关键信号详情")
            print("─" * 40)
            for fa in sorted_fa:
                if fa['signals']:
                    d1 = fa['dimensions'].get('D1_今日估值', '?')
                    d2 = fa['dimensions'].get('D2_组别趋势', '?')
                    d3 = fa['dimensions'].get('D3_组内表现', '?')
                    d4 = fa['dimensions'].get('D4_关联标的', '?')
                    d5 = fa['dimensions'].get('D5_量价信号', '?')
                    sigs = ' | '.join(fa['signals'])
                    urg_icon = {'高': '🔴', '中': '🟡', '低': '🟢'}.get(fa['urgency'], '')
                    print(f"\n📌 {fa['code']} {fa['name'][:18]}")
                    print(f"\n今日: {d1}")
                    print(f"\n趋势: {d2}")
                    print(f"\n组内: {d3}")
                    print(f"\n关联: {d4}")
                    print(f"\n量价: {d5}")
                    if sigs:
                        print(f"\n信号: {sigs}")

    def _print_rebalance(self):
        """再平衡"""
        alerts = getattr(self, 'rebalance_alerts', [])
        if not alerts:
            return

        print("\n" + "─" * 72)
        print("【5】组合再平衡预警")
        print("─" * 72)

        for a in alerts:
            icon = '🔴' if a['type'] == 'overweight' else '🟢'
            print(f"\n  {icon} {a['group']} — {a['type']} (紧迫度: {a['urgency']})")
            print(f"     当前估算占比: {a.get('current_est', '?')}%")
            print(f"     {a['suggestion']}")

    def _print_volume_summary(self):
        """量价汇总"""
        va = self.collected.get('_volume_analysis', {})
        # Actually use the volume_analysis from results
        quotes = self.collected.get('quotes', {})
        sectors = self.collected.get('sectors', {})

        if not quotes and not sectors:
            return

        va = ft.get_volume_analysis(quotes, sectors)
        if not va or not va.get('volume_signals'):
            return

        print("\n【6】量价异常信号")

        print(f"\n📊 总体: {va.get('total_signal', '—')}")
        amp_sum = va.get('amplitude_summary', '')
        if amp_sum:
            print(f"📊 {amp_sum}")

        # 只显示异常信号
        abnormal = [vs for vs in va['volume_signals']
                    if vs['signal'] not in ('正常波动',)]
        if abnormal:
            print(f"\n  异常品种 ({len(abnormal)}个):")
            print("| 品种 | 涨跌 | 振幅 | 成交 | 量价信号 |")
            print("|:----|:----:|:----:|:----:|:--------:|")
            for vs in abnormal[:15]:
                vol_str = vs.get('volume', '—')
                print(f"| {vs['emoji']} {vs['name']:<14} | {vs['change_pct']:>+6.2f}% | {vs['amplitude']:>5.1f}% | {vol_str:<8} | {vs['signal']} |")

    # ── 操作建议跟踪验证 ──────────────────────
    SUGGESTION_LOG = '/tmp/fund_data/_suggestion_log.json'

    def _save_suggestion_log(self):
        """保存当日操作建议供次日验证"""
        entry = {
            'date': self.today_str,
            'groups': {},
            'funds': {},
        }
        for ga in self.group_analyses:
            entry['groups'][ga['group']] = {
                'score': ga['score'],
                'action': ga['action'],
                'avg_change': ga.get('avg_change', 0),
            }
        for fa in self.fund_analyses:
            entry['funds'][fa['code']] = {
                'name': fa['name'],
                'recommendation': fa['recommendation'],
                'urgency': fa['urgency'],
                'score': fa['score'],
                'estimated_change': fa['estimated_change'],
            }
        try:
            os.makedirs(os.path.dirname(self.SUGGESTION_LOG), exist_ok=True)
            log = {}
            if os.path.exists(self.SUGGESTION_LOG):
                with open(self.SUGGESTION_LOG, 'r') as f:
                    log = json.load(f)
            log[self.today_str] = entry
            # 只保留最近30天
            dates = sorted(log.keys())
            for d in dates[:-30]:
                del log[d]
            with open(self.SUGGESTION_LOG, 'w') as f:
                json.dump(log, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.warnings.append(f"建议日志保存失败: {e}")

    def _verify_previous_suggestions(self):
        """对比前一日操作建议与今日实际表现"""
        try:
            if not os.path.exists(self.SUGGESTION_LOG):
                return
            with open(self.SUGGESTION_LOG, 'r') as f:
                log = json.load(f)

            # 找前一个交易日
            all_dates = sorted(log.keys())
            if len(all_dates) < 2:
                return
            prev_key = all_dates[-1]
            # 如果今天已经保存过了且是最后一天，往前取一天
            if prev_key == self.today_str and len(all_dates) >= 2:
                prev_key = all_dates[-2]
            if prev_key == self.today_str:
                return

            prev = log[prev_key]
            prev_groups = prev.get('groups', {})
            prev_funds = prev.get('funds', {})

            # 用今日已分析的组别数据（self.group_analyses + self.fund_analyses）
            today_groups = {ga['group']: ga for ga in self.group_analyses}
            today_funds = {fa['code']: fa for fa in self.fund_analyses}

            results = []
            correct_count = 0
            total_count = 0

            # ── 验证组别建议 ──
            for gname, gprev in prev_groups.items():
                tga = today_groups.get(gname)
                if not tga:
                    continue
                today_change = tga.get('avg_change', 0) or 0

                action = gprev['action']
                score = gprev['score']
                is_bearish = action in ('观望', '减持')
                is_bullish = action in ('增持', '关注')
                is_neutral = action == '持有'

                verdict = '🟡'
                label = '中性'
                if is_bearish and today_change < -0.3:
                    verdict = '✅'
                    label = '正确'
                    correct_count += 1
                elif is_bullish and today_change > 0.3:
                    verdict = '✅'
                    label = '正确'
                    correct_count += 1
                elif is_neutral:
                    verdict = '🟡'
                    label = '中性'
                else:
                    verdict = '❌'
                    label = '偏差'

                if not is_neutral:
                    total_count += 1

                results.append({
                    'type': 'group',
                    'name': gname,
                    'previous': f"{action}(评分{score:+d})",
                    'actual': f"{today_change:+.2f}%",
                    'verdict': verdict,
                    'label': label,
                })

            # ── 验证基金建议 ──
            for code, fprev in prev_funds.items():
                tfa = today_funds.get(code)
                if not tfa:
                    continue
                try:
                    today_chg = float(tfa.get('estimated_change', 0) or 0)
                except (ValueError, TypeError):
                    continue

                rec = fprev['recommendation']
                urgency = fprev['urgency']
                is_bearish = any(kw in rec for kw in ['减仓', '减持', '观望'])
                is_bullish = any(kw in rec for kw in ['增持', '关注', '大涨减仓', '大跌关注'])
                is_neutral = '持有' in rec and not is_bullish and not is_bearish

                verdict = '🟡'
                label = '中性'
                if (is_bearish or urgency == '高') and today_chg < -0.5:
                    verdict = '✅'
                    label = '正确'
                    correct_count += 1
                elif is_bullish and today_chg > 0.5:
                    verdict = '✅'
                    label = '正确'
                    correct_count += 1
                elif is_neutral:
                    verdict = '🟡'
                    label = '中性'
                else:
                    verdict = '❌'
                    label = '偏差'

                if not is_neutral:
                    total_count += 1

                results.append({
                    'type': 'fund',
                    'name': fprev['name'],
                    'code': code,
                    'previous': rec[:12],
                    'actual': f"{today_chg:+.2f}%",
                    'verdict': verdict,
                    'label': label,
                })

            if not results:
                return

            # ── 输出验证报告 ──
            accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
            print(f"\n{'─' * 50}")
            print(f"📋 操作建议验证（{prev_key} → {self.today_str}）")
            print(f"{'─' * 50}")

            # 组别验证
            group_results = [r for r in results if r['type'] == 'group']
            if group_results:
                print(f"\n📁 组别操作验证:")
                print(f"| 组别 | 前日建议 | 今日实际 | 判定 |")
                print(f"|:----|:--------|:--------:|:----:|")
                for r in group_results:
                    print(f"| {r['name']} | {r['previous']} | {r['actual']} | {r['verdict']} {r['label']} |")

            # 基金验证（只显示有明确信号的）
            fund_results = [r for r in results if r['type'] == 'fund' and r['label'] != '中性']
            if fund_results:
                print(f"\n💰 基金信号验证:")
                print(f"| 代码 | 名称 | 前日信号 | 今日实际 | 判定 |")
                print(f"|:----|:----|:--------|:--------:|:----:|")
                for r in fund_results[:10]:
                    print(f"| {r['code']} | {r['name'][:10]} | {r['previous']} | {r['actual']} | {r['verdict']} {r['label']} |")
                if len(fund_results) > 10:
                    print(f"  ... 还有{len(fund_results)-10}条")

            if total_count > 0:
                print(f"\n📊 准确率: {accuracy:.0f}% ({correct_count}/{total_count})")
            print(f"{'─' * 50}")

        except Exception as e:
            self.warnings.append(f"建议验证失败: {e}")

    def _print_summary(self):
        """总结"""
        # 统计
        total = len(self.fund_analyses)
        bullish = sum(1 for fa in self.fund_analyses
                     if any(kw in fa['recommendation'] for kw in ['增持', '关注', '偏多', '大跌关注']))
        neutral = sum(1 for fa in self.fund_analyses
                     if '持有' in fa['recommendation']
                     and not any(kw in fa['recommendation'] for kw in ['偏多', '减持', '减仓', '观望', '增持', '关注']))
        cautious = sum(1 for fa in self.fund_analyses
                      if any(kw in fa['recommendation'] for kw in ['观望', '减仓', '减持', '大涨减仓']))

        print("\n" + "═" * 56)
        print("📋 分析总结")
        print("═" * 56)

        # 统计诊断分布
        print("| 方向 | 数量 |")
        print("|:---|:----:|")
        print(f"| 🟢 偏多 | {bullish} |")
        print(f"| 🟡 中性 | {neutral} |")
        print(f"| 🔴 偏空 | {cautious} |")

        if self.group_analyses:
            print(f"\n📁 组别排名:")
            print("| 组别 | 评分 | 建议 |")
            print("|:----|:---:|:----:|")
            for ga in sorted(self.group_analyses, key=lambda x: -x['score']):
                action_emoji = {'增持': '🟢', '关注': '🟢', '持有': '🟡', '观望': '🔴', '减持': '🔴'}.get(ga['action'], '🟡')
                print(f"| {ga['group']} | {ga['score']:+d} | {action_emoji}{ga['action']} |")

        # 重点关注
        high_urgency = [fa for fa in self.fund_analyses if fa['urgency'] == '高']
        if high_urgency:
            print(f"\n⚠️ 需关注 ({len(high_urgency)}只):")
            print("| 代码 | 名称 | 估值 | 建议 |")
            print("|:----|:----|:----:|:----:|")
            for fa in high_urgency:
                chg = self._fmt_pct(fa['estimated_change'])
                print(f"| {fa['code']} | {fa['name'][:14]} | {chg} | {fa['recommendation']} |")

        # 错误/警告
        if self.errors:
            print(f"\n  ❌ 采集错误 ({len(self.errors)}):")
            for e in self.errors[:5]:
                print(f"     {e}")
            if len(self.errors) > 5:
                print(f"     ... 共{len(self.errors)}条")

        if self.warnings:
            print(f"\n  ⚠️ 分析警告 ({len(self.warnings)}):")
            for w in self.warnings[:5]:
                print(f"     {w}")

        print(f"\n  ✅ 报告生成完成 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 72)


# ══════════════════════════════════════════════
# CLI 入口
# ══════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description='基金全盘监控分析系统')
    parser.add_argument('--json', action='store_true', help='以JSON格式输出')
    parser.add_argument('--funds-only', action='store_true', help='仅输出基金诊断')
    parser.add_argument('--groups-only', action='store_true', help='仅输出组别分析')
    parser.add_argument('--fast', action='store_true', help='快速模式（仅基金+指数）')
    args = parser.parse_args()

    analyzer = FundAnalyzer()

    # In --json / --funds-only / --groups-only modes, suppress fund_tools stdout prints
    if args.json or args.funds_only or args.groups_only:
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            analyzer.collect_all(fast=args.fast)
        finally:
            sys.stdout = old_stdout
    else:
        analyzer.collect_all(fast=args.fast)
    analysis = analyzer.run_full_analysis()

    if args.json:
        output = {
            'date': analyzer.today_str,
            'generated_at': datetime.now().isoformat(),
            'market_overview': {
                'quotes': {k: {'price': v['price'], 'change_pct': v['change_pct']}
                           for k, v in (analyzer.collected.get('quotes', {}) or {}).items() if v} if analyzer.collected.get('quotes') else {},
                'breadth': analyzer.collected.get('market_overview', {}),
                'northbound': analyzer.collected.get('northbound', {}),
                'overnight': {k: {'price': v['price'], 'change_pct': v['change_pct']}
                             for k, v in (analyzer.collected.get('overnight', {}) or {}).items() if v} if analyzer.collected.get('overnight') else {},
            },
            'group_analyses': analysis['group_analyses'],
            'fund_analyses': analysis['fund_analyses'],
            'rebalance_alerts': analysis['rebalance_alerts'],
            'errors': analyzer.errors,
            'warnings': analyzer.warnings,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2, default=str))
    elif args.funds_only:
        print(json.dumps(analysis['fund_analyses'], ensure_ascii=False, indent=2, default=str))
    elif args.groups_only:
        print(json.dumps(analysis['group_analyses'], ensure_ascii=False, indent=2, default=str))
    else:
        analyzer.print_report()


if __name__ == '__main__':
    main()
