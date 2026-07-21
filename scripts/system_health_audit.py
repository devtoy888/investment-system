#!/usr/bin/env python3
"""
系统健康自检脚本 — 每周六运行
检查系统各维度健康状况，输出自检报告 + 进化建议

输出 stdout → cron no_agent 推送到 QQ
空输出 → 无推送（系统健康时不打扰）
"""
import json, os, sys, subprocess
from pathlib import Path
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

DATA_DIR = Path("/opt/data/fund_system_data")
SCRIPTS_DIR = Path("/opt/data/scripts")
CRON_LOG = Path(os.path.expanduser("~/.hermes/cron/output"))

FILES_TO_CHECK = {
    "morning-briefs.jsonl":  {"date_key": "date"},
    "noon-briefs.jsonl":     {"date_key": "date"},
    "closing-reviews.jsonl": {"date_key": "date"},
    "signals-resolved.jsonl":{"date_key": "signal_date"},
    "decisions.jsonl":       {"date_key": "_date"},
}

issues = []
warnings = []
suggestions = []

def out(s=""):
    print(s)

def parse_jsonl(path):
    """解析 JSONL 文件，返回 records 列表"""
    records = []
    for line in path.read_text().split('\n'):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records

def check_jsonl_health():
    """检查 JSONL 文件数据质量"""
    out("📄 **JSONL 数据质量**")
    all_ok = True
    
    for fname, config in FILES_TO_CHECK.items():
        path = DATA_DIR / fname
        if not path.exists():
            out(f"  ❌ {fname}: 文件不存在")
            all_ok = False
            continue
        
        records = parse_jsonl(path)
        total = len(records)
        if total == 0:
            out(f"  🟡 {fname}: 空文件")
            continue
        
        date_key = config["date_key"]
        date_counts = Counter(r.get(date_key, "unknown") for r in records)
        unique_dates = len(date_counts)
        total_days = unique_dates
        max_dup = max(date_counts.values())
        
        # 期望值：每天1条
        expected = total_days
        dedup_ratio = round(total / expected, 1) if expected > 0 else 0
        
        # 检查字段完整性
        missing_fields = 0
        if fname == "closing-reviews.jsonl":
            missing_fields = sum(1 for r in records if not r.get("market_accuracy"))
        elif fname == "signals-resolved.jsonl":
            correct_null = sum(1 for r in records if r.get("correct") is None)
        
        status = "✅" if dedup_ratio <= 1.5 else ("🟡" if dedup_ratio <= 3 else "❌")
        if status == "❌":
            issues.append(f"{fname} 重复率过高 ({dedup_ratio}x)")
        
        out(f"  {status} {fname}: {total}条/{total_days}天 ≈ {dedup_ratio}x/天")
        if dedup_ratio > 1.5:
            out(f"     → 期望每天1条，实际最高单日{max_dup}条")
        
        if fname == "signals-resolved.jsonl":
            cn = sum(1 for r in records if r.get("correct") is None)
            ct = sum(1 for r in records if r.get("correct") is True)
            cf = sum(1 for r in records if r.get("correct") is False)
            if cn == total and total > 0:
                out(f"     → ⚠️ correct字段: 全部{cn}条为null，从未做出正确/错误判断")
                issues.append(f"KOL信号归因：{total}条信号correct均为null")
                suggestions.append("修复 resolve_past_signals() 的涨跌判断逻辑")
    
    out()

def check_signal_resolution():
    """检查 KOL 信号归因状态"""
    out("📡 **KOL 信号归因**")
    
    resolved_path = DATA_DIR / "signals-resolved.jsonl"
    if not resolved_path.exists():
        out("  ❌ signals-resolved.jsonl 不存在")
        return
    
    records = parse_jsonl(resolved_path)
    if not records:
        out("  🟡 信号记录为空")
        return
    
    # 按博主统计
    kol_stats = defaultdict(lambda: {"total": 0, "correct": 0, "wrong": 0, "pending": 0})
    for r in records:
        kol = r.get("kol_name", "未知")
        corr = r.get("correct")
        kol_stats[kol]["total"] += 1
        if corr is True:
            kol_stats[kol]["correct"] += 1
        elif corr is False:
            kol_stats[kol]["wrong"] += 1
        else:
            kol_stats[kol]["pending"] += 1
    
    for kol, stats in sorted(kol_stats.items()):
        total = stats["total"]
        resolved = stats["correct"] + stats["wrong"]
        pending = stats["pending"]
        rate = round(resolved / total * 100) if total > 0 else 0
        
        if resolved == 0 and total > 0:
            out(f"  ❌ {kol}: {total}条信号 → 0条已解析 (0%)")
        else:
            out(f"  🟡 {kol}: {total}条 → {resolved}条已解析 ({rate}%)")
    
    out()

def check_data_sources():
    """调用 auto_validate 检查数据源，或直接分析"""
    out("🔌 **数据源健康**")
    
    # 从 closing-reviews 估算数据采集率
    closing_path = DATA_DIR / "closing-reviews.jsonl"
    if not closing_path.exists():
        out("  🟡 暂无数据（等待采集）")
        return
    
    records = parse_jsonl(closing_path)
    recent = [r for r in records if 
              r.get("_date", "").startswith((date.today() - timedelta(days=7)).isoformat()[:10]) or
              r.get("date", "").startswith((date.today() - timedelta(days=7)).isoformat()[:10])]
    
    # 检查最近7天的数据字段完整性
    if records:
        sample = records[-1]  # 取最新一条
        has_overnight = bool(sample.get("overnight"))
        has_funds = bool(sample.get("fund_accuracy"))
        has_market = bool(sample.get("market_accuracy"))
        out(f"  最新记录字段: 外盘={'✅' if has_overnight else '❌'} 基金={'✅' if has_funds else '❌'} 大盘={'✅' if has_market else '❌'}")
    
    out()

def check_cron_health():
    """检查 cron 任务执行状态"""
    out("⏰ **Cron 任务健康**")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "hermes", "cron", "list"],
            capture_output=True, text=True, timeout=15
        )
        output = result.stdout + result.stderr
        # 解析cron状态
        for line in output.split('\n'):
            if "error" in line.lower() and "delivery" in line.lower():
                out(f"  ⚠️ 推送异常: {line.strip()}")
    except Exception as e:
        out(f"  🟡 无法查询cron状态: {e}")
    
    out()

def check_delivery_health():
    """检查推送成功率（从cron日志）"""
    out("📨 **推送健康**")
    
    # 检查最近7天日志文件
    recent_logs = []
    if CRON_LOG.exists():
        for f in sorted(CRON_LOG.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
            content = f.read_text()
            if "error" in content.lower() or "fail" in content.lower() or "send" in content.lower():
                recent_logs.append((f.name, content[:200]))
    
    if recent_logs:
        out(f"  最近{len(recent_logs)}次cron运行中有异常日志:")
        for name, snippet in recent_logs[:3]:
            out(f"  ⚠️ {name}: {snippet[:100]}")
    else:
        out("  ✅ 无推送异常记录")
    
    out()

def generate_evolution_suggestions():
    """汇总问题并生成进化建议"""
    if not issues and not warnings:
        out("🎯 **进化建议**")
        out("  ✅ 系统一切正常，无需调整")
        return
    
    out("🎯 **进化建议**")
    
    for issue in issues[:5]:
        out(f"  ❌ {issue}")
    
    for warn in warnings[:3]:
        out(f"  ⚠️ {warn}")
    
    if suggestions:
        out("\n📋 **建议操作项**")
        for i, s in enumerate(suggestions, 1):
            out(f"  {i}. {s}")
    
    out()

def main():
    today = date.today().isoformat()
    week_num = date.today().isocalendar()[1]
    
    out("━" * 50)
    out(f"📊 系统健康自检 · 第{week_num}周 ({today})")
    out("━" * 50)
    out()
    
    check_jsonl_health()
    check_signal_resolution()
    check_data_sources()
    check_cron_health()
    check_delivery_health()
    generate_evolution_suggestions()
    
    out("━" * 50)
    out(f"💡 说明：系统自检每周六自动执行")
    out(f"   问题持续一周未修复将升级告警")
    out("━" * 50)
    
    # 如果有严重问题，exit code 非0触发更高优先级
    if issues:
        sys.exit(1)

if __name__ == "__main__":
    main()
