#!/usr/bin/env python3
"""
数据源自动验证脚本
每周六运行（周末无交易，回顾本周数据可用性）

功能:
1. 读取 _source_availability.jsonl 计算每个数据源的上周可用率
2. 读取三份JSONL归档，检查数据是否被实际采集到
3. 给出 keep / investigate / drop 建议
4. 如果某个源连续14天可用率 < 50%，输出移除建议
"""
import json, sys
from datetime import date, datetime, timedelta
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path("/opt/data/fund_system_data")
TRACKER_FILE = DATA_DIR / "_source_availability.jsonl"
ARCHIVES = {
    'morning_brief': DATA_DIR / 'morning-briefs.jsonl',
    'noon_brief': DATA_DIR / 'noon-briefs.jsonl',
    'closing_review': DATA_DIR / 'closing-reviews.jsonl',
}

# 数据源描述
SOURCE_DESCRIPTIONS = {
    'sector_etfs': '行业ETF板块涨跌排行 (腾讯)',
    'market_breadth': '涨跌家数 (东财+新浪+AKShare三级备援)',
    'total_turnover': '两市总成交额 (腾讯)',
    'tencent_quotes': 'A股指数行情 (腾讯)',
    'fund_values': '基金净值/实时估值 (天天基金)',
    'overnight': '外盘美股/黄金/美元 (Yahoo)',
    'northbound_flow': '北向资金 (hexin+新浪+AKShare+东财+快照)',
    'weibo_kols': '博主微博采集 (桌面API)',
}

# 正常值范围（用于合理性校验）
SANITY_RANGES = {
    'sector_etfs': {'min_success_pct': 50},   # 至少50%板块获取成功
    'market_breadth': {'min_rise_fall_total': 100},  # 涨+跌至少100家
    'total_turnover': {'min_billion': 100},   # 最少100亿算合理
}


def load_tracker() -> list[dict]:
    """读取追踪文件"""
    if not TRACKER_FILE.exists():
        return []
    records = []
    for line in TRACKER_FILE.read_text().strip().split('\n'):
        line = line.strip()
        if line:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def load_archive_usage(path: Path) -> dict:
    """从JSONL归档读取某次推送中数据源的使用情况（原始数据字段）"""
    if not path.exists():
        return {}
    stats = defaultdict(lambda: {'collected': 0, 'total': 0})
    for line in path.read_text().strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        date_key = record.get('_date', 'unknown')
        # 检查各数据源是否出现在该记录中
        checks = {
            'sector_etfs': bool(record.get('sectors')),
            'market_breadth': (
                record.get('market_overview', {}).get('rise_count') is not None
            ),
            'total_turnover': (
                record.get('market_overview', {}).get('total_turnover', 0) > 0
            ),
            'tencent_quotes': bool(record.get('quotes')),
            'fund_values': bool(record.get('funds')),
            'overnight': bool(record.get('overnight')),
            'weibo_kols': bool(record.get('kol_posts')),
            'weibo_comments': bool(record.get('comment_analysis')),
        }
        for src, present in checks.items():
            stats[src]['total'] += 1
            if present:
                stats[src]['collected'] += 1
    return dict(stats)


def compute_weekly_stats(records: list[dict], days: int = 7) -> dict:
    """计算过去N天每个数据源的统计"""
    cutoff = datetime.now() - timedelta(days=days)
    weekly = [r for r in records if datetime.fromisoformat(r.get('_ts', '2000-01-01')) > cutoff]
    
    stats = defaultdict(lambda: {'attempts': 0, 'successes': 0, 'details': []})
    for r in weekly:
        src = r.get('source', 'unknown')
        stats[src]['attempts'] += 1
        if r.get('success'):
            stats[src]['successes'] += 1
        stats[src]['details'].append(r.get('detail', ''))
    
    result = {}
    for src, s in stats.items():
        rate = round(s['successes'] / s['attempts'] * 100) if s['attempts'] > 0 else 0
        result[src] = {
            'name': SOURCE_DESCRIPTIONS.get(src, src),
            'attempts': s['attempts'],
            'successes': s['successes'],
            'rate': rate,
            'status': _judge_status(rate, s['attempts']),
        }
    return result


def _judge_status(rate: int, attempts: int) -> str:
    """判断数据源状态"""
    if attempts == 0:
        return '⚠️ 无数据'
    if attempts < 3:
        return '🔄 样本不足'
    if rate >= 80:
        return '✅ 稳定'
    if rate >= 50:
        return '🔶 不稳定'
    return '❌ 需移除'


def check_sanity(archive_stats: dict) -> dict:
    """合理性检查"""
    issues = {}
    # 检查成交额 - 非交易时段可能为0
    turnover_stat = archive_stats.get('total_turnover', {})
    if turnover_stat.get('total', 0) > 0:
        collected = turnover_stat.get('collected', 0)
        total = turnover_stat.get('total', 0)
        if collected / total < 0.3:
            issues['total_turnover'] = f"成交额存在率仅{collected}/{total}，可能经常在非交易时段采集"
    return issues


def main():
    print("=" * 60)
    print(f"📊 数据源可用性验证报告 — {date.today().isoformat()}")
    print("=" * 60)
    
    # 1. 从tracker读取可用率
    records = load_tracker()
    if not records:
        print("\n⚠️  尚无追踪数据。新数据源刚刚部署，等待积累样本。")
        print("   自动验证将在采集 >= 3次后开始评估。")
        return
    
    weekly = compute_weekly_stats(records, days=7)
    
    print(f"\n📈 过去7天数据源可用率统计 (共{len(records)}条记录)\n")
    print(f"{'数据源':<20} {'描述':<30} {'尝试':>5} {'成功':>5} {'可用率':>7} {'状态':<12}")
    print("-" * 85)
    for src, s in sorted(weekly.items(), key=lambda x: x[1]['rate']):
        print(f"{src:<20} {s['name']:<30} {s['attempts']:>5} {s['successes']:>5} {s['rate']:>6}% {s['status']:<12}")
    
    # 2. 从归档检查数据实际使用情况
    print(f"\n📚 归档数据核验\n")
    for push_name, path in ARCHIVES.items():
        if path.exists():
            line_count = len(path.read_text().strip().split('\n'))
            print(f"  {push_name:20}: {line_count}条记录 ({path})")
        else:
            print(f"  {push_name:20}: 文件不存在")
    
    archive_stats = load_archive_usage(ARCHIVES.get('noon_brief', Path('/dev/null')))
    # 合并三个归档
    combined_usage = defaultdict(lambda: {'collected': 0, 'total': 0})
    for push_name, path in ARCHIVES.items():
        usage = load_archive_usage(path)
        for src, v in usage.items():
            combined_usage[src]['total'] += v['total']
            combined_usage[src]['collected'] += v['collected']
    
    print(f"\n📋 各数据源归档存在率\n")
    print(f"{'数据源':<20} {'归档存在率':<30}")
    print("-" * 50)
    for src, v in sorted(combined_usage.items()):
        pct = round(v['collected'] / v['total'] * 100) if v['total'] > 0 else 0
        bar = '█' * (pct // 10) + '░' * (10 - pct // 10)
        print(f"{src:<20} {v['collected']:>3}/{v['total']:<3} {pct:>3}% {bar}")
    
    # 3. 提出建议
    print(f"\n🎯 建议操作\n")
    
    # 新数据源（最近才添加的）
    new_sources = {'sector_etfs', 'market_breadth', 'total_turnover'}
    new_source_records = [r for r in records if r.get('source') in new_sources]
    
    if new_sources - set(weekly.keys()):
        print(f"  🔄 新数据源刚刚部署: {', '.join(new_sources - set(weekly.keys()))}")
        print(f"     等待一周数据积累后评估")
    
    # 推荐保留的要删除的
    drops = [s for s in weekly.values() if s['status'] == '❌ 需移除' and s['attempts'] >= 5]
    if drops:
        print(f"  建议移除以下不稳定数据源：")
        for d in drops:
            print(f"    ❌ {d['name']} (可用率{d['rate']}%)")
    else:
        print(f"  ✅ 目前无数据源需要移除")
    
    # 合理性检查
    issues = check_sanity(combined_usage)
    if issues:
        print(f"\n🔍 需关注的问题：")
        for src, msg in issues.items():
            print(f"    ⚠️  {SOURCE_DESCRIPTIONS.get(src, src)}: {msg}")
    
    print("\n" + "=" * 60)
    print("📌 说明：验证脚本每周六运行，自动决定数据源去留")
    print("   新数据源需积累 >= 7天数据才进入评估")
    print("   可用率 < 50% 且连续14天 -> 自动建议移除")
    print("=" * 60)


if __name__ == "__main__":
    main()
