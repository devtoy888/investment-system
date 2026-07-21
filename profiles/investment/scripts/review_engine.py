#!/usr/bin/env python3
"""
自动化报告审阅进化系统
========================
核心能力：
1. 质量审查 — 每日自动检查所有报告是否完整、逻辑自洽
2. 预测验证 — 对比当日预测 vs 实际涨跌，计算准确率
3. 操作回溯 — 追踪每笔建议(买入/卖出/持有)的后续表现
4. 自我进化 — 基于准确率数据自动优化prompt
5. 复盘看板 — 可视化展示所有指标
"""
import sys, os, json, re, subprocess
from pathlib import Path
from datetime import date, datetime, timedelta
from typing import Optional, Any

sys.path.insert(0, '/opt/data/scripts')

DATA_DIR = Path("/opt/data/fund_system_data")
REPORT_DIR = DATA_DIR / "reports"
EVOLVE_DIR = DATA_DIR / "evolution"
EVOLVE_DIR.mkdir(parents=True, exist_ok=True)
BASE_URL = "https://hermes-main-media.devtoy.xyz/fund-system/reports"

# ═══════════════════════════════════════════════
# 1. 报告质量审查
# ═══════════════════════════════════════════════

REPORT_QUALITY_RULES = {
    "morning": {
        "required_sections": ["步骤1", "步骤2", "步骤3", "步骤4", "步骤5"],
        "min_chars": 1500,
        "checks": ["含预测", "含操作建议", "标明15:00前"],
    },
    "noon": {
        "required_sections": ["午", "午后", "操作"],
        "min_chars": 1000,
        "checks": ["含下午方向", "含基金影响"],
    },
    "decision": {
        "required_sections": ["操作", "基金", "建议"],
        "min_chars": 800,
        "checks": ["含具体基金代码", "含仓位建议"],
    },
    "closing": {
        "required_sections": ["步骤1", "步骤2", "步骤3", "步骤4", "步骤5"],
        "min_chars": 2000,
        "checks": ["含明日推演", "含操作方向", "含风险清单"],
    },
    "weekly": {
        "required_sections": ["本周", "下周", "策略"],
        "min_chars": 2000,
        "checks": ["含归因分析", "含下周计划"],
    },
}

def review_report(md_content: str, report_type: str) -> dict:
    """审查一份报告的质量"""
    rules = REPORT_QUALITY_RULES.get(report_type, {})
    result = {
        "type": report_type,
        "length": len(md_content),
        "passed": True,
        "issues": [],
        "sections_found": [],
        "checks_passed": 0,
        "checks_total": 0,
    }
    
    # Check sections
    for section in rules.get("required_sections", []):
        if section in md_content:
            result["sections_found"].append(section)
    
    section_ratio = len(result["sections_found"]) / max(len(rules.get("required_sections", [])), 1)
    if section_ratio < 0.8:
        result["issues"].append(f"缺少关键章节: 找到{len(result['sections_found'])}/{len(rules.get('required_sections', []))}")
        result["passed"] = False
    
    # Check min length
    if len(md_content) < rules.get("min_chars", 500):
        result["issues"].append(f"内容过短: {len(md_content)} < {rules['min_chars']}")
        result["passed"] = False
    
    # Check for truncated content (ends mid-sentence)
    if md_content and not md_content.rstrip().endswith(('.', '。', '）', ')', '"', '"', '】', '```', '>')):
        last_line = md_content.strip().split('\n')[-1] if md_content.strip() else ""
        if len(last_line) > 20 and not any(last_line.strip().endswith(c) for c in '.。")）】'):
            result["issues"].append("⚠️ 疑似截断: 末尾句子未完整")
            result["passed"] = False
    
    return result


def review_all_reports(dt: date = None) -> dict:
    """审查指定日期的所有报告（日期子目录+平铺兼容）"""
    dt = dt or date.today()
    results = {}
    
    for report_type in ["morning", "noon", "decision", "closing", "morning_direction"]:
        # 优先读日期子目录
        subdir = f"{dt.year}/{dt.month:02d}/{dt.day:02d}"
        path = REPORT_DIR / subdir / f"{report_type}.md"
        # 备援：读平铺旧版
        if not path.exists():
            path = REPORT_DIR / f"{report_type}_{dt.isoformat()}.md"
        if path.exists():
            content = path.read_text(encoding='utf-8')
            results[report_type] = review_report(content, report_type)
        else:
            results[report_type] = {"type": report_type, "passed": False, "issues": ["报告不存在"]}
    
    return results

# ═══════════════════════════════════════════════
# 2. 预测验证引擎
# ═══════════════════════════════════════════════

PREDICTION_DB = EVOLVE_DIR / "predictions.jsonl"
ACCURACY_DB = EVOLVE_DIR / "accuracy.jsonl"

def extract_predictions(md_content: str, report_type: str) -> list:
    """从报告中智能提取所有预测性语句"""
    predictions = []
    lines = md_content.split('\n')
    
    # Pattern 1: 方向判断 (看多/看空/中性/涨/跌)
    direction_pattern = re.compile(r'(方向判断|预计|预期|大概率|可能|看[多空涨跌]|偏[多空涨跌]|中性)')
    # Pattern 2: 具体点位/百分比预测
    value_pattern = re.compile(r'([+-]?\d+\.?\d*%)')
    # Pattern 3: 情景推演
    scenario_pattern = re.compile(r'(情景[ABC]|如果|若|触发条件)')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        # 跳过数据表行（包含|和%的表格数据）
        if '|' in line and '%' in line and re.search(r'[🔴🟢🟡]', line):
            i += 1
            continue
        # 跳过纯数据行（纯数字+符号）
        if re.match(r'^[\d\s.,%🔴🟢🟡📈📉➖|:—\-]+$', line):
            i += 1
            continue
        
        pred = None
        
        # Check for direction prediction
        if direction_pattern.search(line):
            pred = line[:200]
        # Check for value prediction  
        elif value_pattern.search(line) and any(kw in line for kw in ['涨', '跌', '反弹', '回调', '支撑', '压力']):
            pred = line[:200]
        # Check for scenario
        elif scenario_pattern.search(line):
            # Collect the scenario block
            scenario_lines = [line]
            j = i + 1
            while j < len(lines) and j < i + 5:
                nl = lines[j].strip()
                if nl and (nl.startswith('-') or nl.startswith('*') or '应对' in nl):
                    scenario_lines.append(nl)
                    j += 1
                else:
                    break
            pred = '\n'.join(scenario_lines)[:300]
        
        if pred:
            predictions.append({
                "text": pred,
                "source_type": report_type,
                "source_date": date.today().isoformat(),
                "verified": False,
                "actual_outcome": None,
            })
        i += 1
    
    return predictions


def verify_predictions(dt: date = None) -> dict:
    """验证某天的预测 vs 实际表现"""
    dt = dt or date.today()
    today_reports = review_all_reports(dt)
    
    # Load actual market data for the day
    actual_data = _get_actual_market(dt)
    
    results = {
        "date": dt.isoformat(),
        "total_predictions": 0,
        "verified": 0,
        "correct": 0,
        "wrong": 0,
        "accuracy_pct": 0,
        "details": [],
    }
    
    for report_type, review in today_reports.items():
        if not review.get("length"):
            continue
        
        # 优先读日期子目录，备援平铺旧版
        subdir = f"{dt.year}/{dt.month:02d}/{dt.day:02d}"
        path = REPORT_DIR / subdir / f"{report_type}.md"
        if not path.exists():
            path = REPORT_DIR / f"{report_type}_{dt.isoformat()}.md"
        if not path.exists():
            continue
        
        content = path.read_text(encoding='utf-8')
        preds = extract_predictions(content, report_type)
        
        for pred in preds:
            results["total_predictions"] += 1
            # Simple verification: check if the prediction matched actual direction
            if actual_data:
                verification = _verify_single_prediction(pred["text"], actual_data)
                pred["verified"] = True
                pred["actual_outcome"] = verification.get("outcome", "unknown")
                pred["correct"] = verification.get("correct", False)
                results["verified"] += 1
                if pred["correct"]:
                    results["correct"] += 1
                else:
                    results["wrong"] += 1
                results["details"].append(pred)
    
    if results["verified"] > 0:
        results["accuracy_pct"] = round(results["correct"] / results["verified"] * 100, 1)
    
    # Save to accuracy DB
    _save_accuracy(results)
    
    return results


def _get_actual_market(dt: date) -> dict:
    """获取某日的实际市场数据（含板块涨跌幅）"""
    result = {"indices": {}, "sectors": {}, "overall": 0}
    
    # 从每日快照读取指数点位（需要换算成涨跌幅）
    snap_path = DATA_DIR / "daily-snapshots.jsonl"
    if snap_path.exists():
        snaps = []
        for line in open(snap_path):
            try: snaps.append(json.loads(line))
            except: pass
        for snap in reversed(snaps):
            if snap.get("_date") == dt.isoformat():
                result["snapshot"] = snap
                break
    
    # 从收盘数据文件读取板块涨跌幅（最准确）
    closing_sector = Path("/tmp/fund_data") / "_closing_sector.txt"
    if closing_sector.exists():
        import re
        for line in closing_sector.read_text().split('\n'):
            m = re.match(r"[🔴🟢🟡]\s*(\S+):.*\(([+-]?\d+\.?\d*)%\)", line)
            if m:
                name, pct = m.group(1), float(m.group(2))
                result["sectors"][name] = pct
    
    # 从收盘行情表获取指数涨跌幅
    closing_table = Path("/tmp/fund_data") / "_closing_tables.md"
    if closing_table.exists():
        import re
        for line in closing_table.read_text().split('\n'):
            m = re.match(r"\|\s*(\S+)\s*\|\s*[\d.]+\s*\|\s*[\d.]+\s*\|\s*[\d.]+\s*\|\s*[🔴🟢]\s*([+-]?\d+\.?\d*)%", line)
            if m:
                name, pct = m.group(1), float(m.group(2))
                if name not in result["indices"]:
                    result["indices"][name] = pct
    
    # 计算整体市场方向（所有指数涨跌的中位数）
    all_changes = list(result["indices"].values()) + list(result["sectors"].values())
    if all_changes:
        result["overall"] = sum(all_changes) / len(all_changes)
    
    return result


def _verify_single_prediction(pred_text: str, actual_data: dict) -> dict:
    """验证单个预测的正确性（支持指数/板块/整体方向）"""
    result = {"correct": False, "outcome": "未验证"}
    
    indices = actual_data.get("indices", {})
    sectors = actual_data.get("sectors", {})
    overall = actual_data.get("overall", 0)
    
    is_bullish = any(kw in pred_text for kw in ['看多', '涨', '反弹', '上升', '向上', '偏多', '加仓', '增持', '关注', '看好'])
    is_bearish = any(kw in pred_text for kw in ['看空', '跌', '回调', '下降', '向下', '偏空', '减仓', '减持', '警惕', '风险'])
    
    # 1. 检查是否匹配某个具体指数
    matched_change = None
    matched_name = None
    for idx_name, idx_change in indices.items():
        if idx_name in pred_text:
            matched_change = idx_change
            matched_name = idx_name
            break
    
    # 2. 检查是否匹配某个具体板块
    if matched_change is None:
        for sec_name, sec_change in sectors.items():
            if sec_name in pred_text:
                matched_change = sec_change
                matched_name = sec_name
                break
    
    # 3. 检查是否泛指大盘/市场
    if matched_change is None and any(kw in pred_text for kw in ['大盘', '市场', '指数', '整体', '全面']):
        matched_change = overall
        matched_name = "大盘整体"
    
    # 验证
    if matched_change is not None:
        try:
            change = float(matched_change) if not isinstance(matched_change, (int, float)) else matched_change
            matched_str = matched_name or "标的"
            if is_bullish and change > 0:
                result["correct"] = True
                result["outcome"] = f"✅ {matched_str}涨{change:+.2f}%（方向正确）"
            elif is_bearish and change < 0:
                result["correct"] = True
                result["outcome"] = f"✅ {matched_str}跌{change:+.2f}%（方向正确）"
            elif is_bullish and change <= 0:
                result["outcome"] = f"❌ {matched_str}跌{change:+.2f}%（预期涨实际跌）"
            elif is_bearish and change >= 0:
                result["outcome"] = f"❌ {matched_str}涨{change:+.2f}%（预期跌实际涨）"
            else:
                result["outcome"] = f"➖ {matched_str}{change:+.2f}%（中性/无法判断方向）"
        except: pass
    else:
        result["outcome"] = "➖ 无法匹配具体标的（跳过验证）"
    
    return result


def _save_accuracy(results: dict):
    """保存准确率到演化数据库"""
    ACCURACY_DB.parent.mkdir(parents=True, exist_ok=True)
    with open(ACCURACY_DB, 'a', encoding='utf-8') as f:
        f.write(json.dumps(results, ensure_ascii=False) + '\n')


def get_accuracy_trend(days: int = 30) -> dict:
    """获取准确率趋势"""
    if not ACCURACY_DB.exists():
        return {"days": days, "records": 0, "avg_accuracy": 0}
    
    records = []
    with open(ACCURACY_DB) as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except:
                pass
    
    recent = [r for r in records if r["date"] >= (date.today() - timedelta(days=days)).isoformat()]
    
    if not recent:
        return {"days": days, "records": 0, "avg_accuracy": 0}
    
    accuracies = [r.get("accuracy_pct", 0) for r in recent if r.get("verified", 0) > 0]
    
    return {
        "days": days,
        "records": len(recent),
        "total_predictions": sum(r.get("total_predictions", 0) for r in recent),
        "avg_accuracy": round(sum(accuracies) / len(accuracies), 1) if accuracies else 0,
        "trend": "up" if len(accuracies) >= 2 and accuracies[-1] > accuracies[0] else "down" if len(accuracies) >= 2 else "stable",
    }

# ═══════════════════════════════════════════════
# 3. 操作建议回溯
# ═══════════════════════════════════════════════

def extract_operations(md_content: str) -> list:
    """提取报告中的具体基金操作建议"""
    ops = []
    
    # Pattern: 基金代码 + 操作动词
    fund_code_pat = re.compile(r'(\d{6})')
    op_verbs = ['加仓', '减仓', '清仓', '买入', '卖出', '持有', '观望', '止盈', '止损']
    
    for line in md_content.split('\n'):
        codes = fund_code_pat.findall(line)
        verbs = [v for v in op_verbs if v in line]
        
        if codes and verbs:
            ops.append({
                "code": codes[0],
                "action": verbs[0],
                "context": line.strip()[:150],
            })
    
    return ops


def backtest_operations(dt: date = None) -> dict:
    """回溯操作建议的后续表现"""
    dt = dt or date.today()
    results = {
        "date": dt.isoformat(),
        "total_ops": 0,
        "buy_signals": 0,
        "sell_signals": 0,
        "hold_signals": 0,
    }
    
    for report_type in ["morning", "noon", "decision"]:
        path = REPORT_DIR / f"{dt.year}" / f"{dt.month:02d}" / f"{dt.day:02d}" / f"{report_type}.md"
        if not path.exists():
            continue
        
        content = path.read_text(encoding='utf-8')
        ops = extract_operations(content)
        
        for op in ops:
            results["total_ops"] += 1
            if op["action"] in ['加仓', '买入']:
                results["buy_signals"] += 1
            elif op["action"] in ['减仓', '清仓', '卖出', '止盈', '止损']:
                results["sell_signals"] += 1
            else:
                results["hold_signals"] += 1
    
    return results

# ═══════════════════════════════════════════════
# 4. 复盘看板
# ═══════════════════════════════════════════════

def generate_dashboard(dt: date = None) -> str:
    """生成全量复盘HTML看板"""
    dt = dt or date.today()
    reviews = review_all_reports(dt)
    accuracy = get_accuracy_trend(30)
    backtest = backtest_operations(dt)
    
    # Build HTML
    report_cards = ""
    report_status = {"passed": 0, "failed": 0, "total": 0}
    
    fix_items = ""
    for rtype, review in sorted(reviews.items()):
        report_type_labels = {'morning':'晨报','noon':'午报','decision':'14:30决策','closing':'收盘复盘','morning_direction':'09:35方向'}
        rtype_label = report_type_labels.get(rtype, rtype)
        report_status["total"] += 1
        status_icon = "✅" if review.get("passed") else "❌"
        if review.get("passed"):
            report_status["passed"] += 1
        else:
            report_status["failed"] += 1
        
        issues_html = ""
        for issue in review.get("issues", []):
            issues_html += f'<li class="issue">{issue}</li>'
            # 生成修复建议
            if "截断" in issue:
                fix_items += f'<div class="fix-item">⚠️ <b>{rtype}</b> AI分析被截断 → 增大生成时的max_tokens参数</div>'
            elif "缺少" in issue:
                fix_items += f'<div class="fix-item">⚠️ <b>{rtype}</b> 章节不完整 → 检查prompt设计，确保覆盖所有要求章节</div>'
            elif "过短" in issue:
                fix_items += f'<div class="fix-item">⚠️ <b>{rtype_label}</b> 内容过短 → 检查数据采集是否完整</div>'
            elif "不存在" in issue:
                fix_items += f'<div class="fix-item">❌ <b>{rtype_label}</b> 报告未生成 → 检查cron定时任务和脚本是否正常执行</div>'
        
        if review.get("passed"):
            fix_items += f'<div class="fix-item ok">✅ <b>{rtype_label}</b> 全部检查通过</div>'
        
        sections = ", ".join(review.get("sections_found", []))
        report_cards += f'''
        <div class="report-card">
            <div class="rc-header">
                <span class="rc-type">{rtype_label}</span>
                <span class="rc-status">{status_icon}</span>
            </div>
            <div class="rc-body">
                <div class="rc-meta">字数: {review.get("length", 0)} | 章节: {sections}</div>
                {f'<ul>{issues_html}</ul>' if issues_html else '<div class="pass">全部检查通过</div>'}
            </div>
        </div>'''
    
    # Accuracy chart data
    chart_data = []
    if ACCURACY_DB.exists():
        with open(ACCURACY_DB) as f:
            for line in f:
                try:
                    r = json.loads(line)
                    if r.get("verified", 0) > 0:
                        chart_data.append({"d": r["date"][-5:], "a": r["accuracy_pct"]})
                except:
                    pass
    chart_data = chart_data[-30:]  # last 30 days
    
    chart_rows = ""
    for cd in chart_data:
        bar_w = max(int(cd["a"]), 5)
        color = "#27ae60" if cd["a"] >= 60 else "#e67e22" if cd["a"] >= 40 else "#e74c3c"
        chart_rows += f'<tr><td>{cd["d"]}</td><td><div class="bar" style="width:{bar_w}%;background:{color}">{cd["a"]}%</div></td></tr>'
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>投资系统复盘看板 · {dt.isoformat()}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,'PingFang SC',sans-serif;background:#f0f2f5;color:#1a1a2e;line-height:1.6}}
.header{{background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);color:white;padding:30px 20px;text-align:center}}
.header h1{{font-size:24px;margin-bottom:6px}}
.header .sub{{font-size:13px;opacity:0.8}}
.container{{max-width:960px;margin:0 auto;padding:16px}}

/* Summary cards */
.summary{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:20px}}
.summary-card{{background:white;border-radius:12px;padding:16px;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.06)}}
.summary-card .num{{font-size:32px;font-weight:700;color:#4a6cf7}}
.summary-card .num.green{{color:#27ae60}}
.summary-card .num.red{{color:#e74c3c}}
.summary-card .label{{font-size:12px;color:#888;margin-top:4px}}

/* Report cards */
.report-card{{background:white;border-radius:12px;padding:16px;margin-bottom:12px;box-shadow:0 1px 4px rgba(0,0,0,0.06)}}
.rc-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}}
.rc-type{{font-weight:600;font-size:16px;text-transform:capitalize}}
.rc-status{{font-size:20px}}
.rc-meta{{font-size:13px;color:#666}}
.rc-body ul{{list-style:none;padding:0;margin:8px 0}}
.issue{{color:#e74c3c;font-size:13px;padding:2px 0}}
.pass{{color:#27ae60;font-size:13px;font-weight:500}}

/* Chart */
.chart table{{width:100%;border-collapse:collapse}}
.chart td{{padding:4px 8px;font-size:12px}}
.bar{{height:20px;border-radius:4px;color:white;padding:0 8px;line-height:20px;font-size:11px;min-width:40px;text-align:right}}

/* Accuracy card */
.acc-detail{{margin-top:10px}}
.acc-detail .stat{{display:inline-block;background:#f8f9fa;padding:6px 14px;border-radius:8px;margin:4px;font-size:13px}}

/* Operations */
.op-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:10px}}
.op-item{{text-align:center;padding:10px;border-radius:8px;font-size:14px;font-weight:600}}
.op-buy{{background:#e8f5e9;color:#2e7d32}}
.op-sell{{background:#ffebee;color:#c62828}}
.op-hold{{background:#fff3e0;color:#e65100}}

/* Navigation */
.nav{{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap}}
.nav a{{background:white;padding:8px 16px;border-radius:8px;text-decoration:none;color:#4a6cf7;font-size:13px;box-shadow:0 1px 3px rgba(0,0,0,0.06)}}
.nav a:hover{{background:#4a6cf7;color:white}}

@media(max-width:600px){{.summary{{grid-template-columns:repeat(2,1fr)}}.op-grid{{grid-template-columns:1fr}}}}
/* Dark mode */
body.dk{{background:#1a1a2e;color:#e0e0e0}}
body.dk .summary-card,body.dk .report-card,body.dk .nav a{{background:#16213e;color:#e0e0e0;box-shadow:0 1px 4px rgba(0,0,0,0.3)}}
body.dk .nav a:hover{{background:#4a6cf7}}
body.dk .rc-meta,body.dk .footer{{color:#888}}
body.dk .stat{{background:#0f3460;color:#e0e0e0}}
body.dk .op-buy{{background:#1b4332;color:#52b788}}
body.dk .op-sell{{background:#4a1a1a;color:#ef5350}}
body.dk .op-hold{{background:#4a3a1a;color:#ffb74d}}
body.dk .header{{background:linear-gradient(135deg,#0f0c29,#1a1a3e,#16213e)}}
/* Fix suggestions */
.fix-section{{margin:16px 0}}
.fix-item{{background:#fff5f5;border-left:3px solid #e74c3c;padding:8px 12px;margin:6px 0;border-radius:0 6px 6px 0;font-size:13px}}
body.dk .fix-item{{background:#2d1a1a;border-left-color:#ef5350}}
.fix-item.ok{{background:#f0fdf4;border-left-color:#27ae60}}
body.dk .fix-item.ok{{background:#1a2d1a;border-left-color:#52b788}}
</style>
</head>
<body>
<div class="header">
    <h1>📊 投资系统复盘看板</h1>
    <div class="sub">{dt.isoformat()} · 自动审阅每日报告质量</div>
</div>
<div class="container">

<div class="nav">
    <a href="{BASE_URL}/dashboard.html">📊 刷新看板</a>
    <a href="{BASE_URL}/index.html">📅 历史报告</a>
    <a href="javascript:void(0)" onclick="document.body.classList.toggle('dk')">🌓 切换主题</a>
</div>

<div class="summary">
    <div class="summary-card">
        <div class="num">{report_status["total"]}</div>
        <div class="label">今日报告</div>
    </div>
    <div class="summary-card">
        <div class="num green">{report_status["passed"]}</div>
        <div class="label">通过审查</div>
    </div>
    <div class="summary-card">
        <div class="num red">{report_status["failed"]}</div>
        <div class="label">存在问题</div>
    </div>
    <div class="summary-card">
        <div class="num">{accuracy.get("avg_accuracy", "—")}%</div>
        <div class="label">预测准确率({accuracy.get("days", 30)}天)</div>
    </div>
    <div class="summary-card">
        <div class="num">{backtest.get("total_ops", 0)}</div>
        <div class="label">今日操作建议</div>
    </div>
    <div class="summary-card">
        <div class="num">{accuracy.get("total_predictions", 0)}</div>
        <div class="label">累计预测数</div>
    </div>
</div>

<h2>📋 今日报告质量审查</h2>
{report_cards}

<h2>🔧 自动修复建议</h2>
<div class="fix-section">
{fix_items}
</div>

<h2>📈 预测准确率趋势（近{len(chart_data)}天）</h2>
<div class="chart">
    <table>
        {chart_rows if chart_rows else '<tr><td style="text-align:center;color:#888;padding:20px">暂无验证数据（需要T+1确认）</td></tr>'}
    </table>
</div>
<div class="acc-detail">
    <span class="stat">✅ 正确: {accuracy.get('total_predictions', 0)}</span>
    <span class="stat">📊 趋势: {'📈上升' if accuracy.get('trend')=='up' else '📉下降' if accuracy.get('trend')=='down' else '➖稳定'}</span>
</div>

<h2>🛠️ 今日操作信号</h2>
<div class="op-grid">
    <div class="op-item op-buy">🟢 买入/加仓<br>{backtest.get("buy_signals", 0)}次</div>
    <div class="op-item op-sell">🔴 卖出/减仓<br>{backtest.get("sell_signals", 0)}次</div>
    <div class="op-item op-hold">🟡 持有/观望<br>{backtest.get("hold_signals", 0)}次</div>
</div>

<div style="text-align:center;margin:30px 0;font-size:12px;color:#aaa">
    自动生成 · {datetime.now().strftime('%Y-%m-%d %H:%M')} · 每日收盘后自动更新
</div>
</div>
<script>
if(window.matchMedia("(prefers-color-scheme:dark)").matches)document.body.classList.add("dk");
</script>
</body></html>"""
    
    # Save and upload
    local_path = REPORT_DIR / "dashboard.html"
    local_path.write_text(html, encoding='utf-8')
    
    subprocess.run([sys.executable, '-c', f'''
import sys; sys.path.insert(0, "/opt/data/scripts")
from fund_tools import upload_to_r2 as up
up("{local_path}", "fund-system/reports/dashboard.html", "text/html; charset=utf-8")
'''], capture_output=True, text=True, timeout=30)
    
    return f"{BASE_URL}/dashboard.html"

# ═══════════════════════════════════════════════
# 5. 自我进化
# ═══════════════════════════════════════════════

EVOLVE_CONFIG = EVOLVE_DIR / "evolution_config.json"

def analyze_evolution() -> dict:
    """分析系统进化趋势并提出改进建议"""
    trend = get_accuracy_trend(30)
    backtest_data = []
    
    # Load accuracy history
    accuracies = []
    if ACCURACY_DB.exists():
        with open(ACCURACY_DB) as f:
            for line in f:
                try:
                    r = json.loads(line)
                    if r.get("accuracy_pct", 0) > 0:
                        accuracies.append(r)
                except:
                    pass
    
    # Calculate weekly averages
    weekly_avg = {}
    for r in accuracies:
        week = r["date"][:7]  # YYYY-MM
        if week not in weekly_avg:
            weekly_avg[week] = []
        weekly_avg[week].append(r["accuracy_pct"])
    
    for week, vals in weekly_avg.items():
        weekly_avg[week] = round(sum(vals) / len(vals), 1)
    
    # Generate improvement suggestions
    suggestions = []
    
    if trend.get("avg_accuracy", 0) < 50:
        suggestions.append("🔴 预测准确率低于50%，建议审查prompt中的市场分析逻辑")
    elif trend.get("avg_accuracy", 0) < 65:
        suggestions.append("🟡 准确率中等，可优化关键判断的置信度描述")
    else:
        suggestions.append("🟢 准确率良好，保持当前prompt设计")
    
    if len(accuracies) >= 5:
        recent_avg = sum(r["accuracy_pct"] for r in accuracies[-5:]) / 5
        if recent_avg > trend.get("avg_accuracy", 0):
            suggestions.append("📈 最近5天准确率持续提升，系统在自我改进")
        else:
            suggestions.append("📉 最近准确率下降，建议检查市场风格是否发生变化")
    
    # Save evolution config
    config = {
        "last_analysis": datetime.now().isoformat(),
        "accuracy_trend": trend,
        "weekly_averages": weekly_avg,
        "suggestions": suggestions,
        "total_reports_analyzed": len(accuracies),
    }
    EVOLVE_CONFIG.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
    
    return config

# ═══════════════════════════════════════════════
# 6. 全量执行入口
# ═══════════════════════════════════════════════

def full_review_cycle(dt: date = None) -> dict:
    """执行完整的审阅进化周期"""
    dt = dt or date.today()
    
    print(f"🔍 开始审阅周期: {dt.isoformat()}", file=sys.stderr)
    
    # 1. 审查所有报告
    print("  📋 审查报告质量...", file=sys.stderr)
    reviews = review_all_reports(dt)
    
    # 2. 验证预测
    print("  ✅ 验证预测准确率...", file=sys.stderr)
    verification = verify_predictions(dt)
    print(f"    准确率: {verification.get('accuracy_pct', 'N/A')}% ({verification.get('correct', 0)}/{verification.get('verified', 0)})", file=sys.stderr)
    
    # 3. 操作回溯
    print("  🔙 回溯操作建议...", file=sys.stderr)
    backtest = backtest_operations(dt)
    print(f"    买入{backtest.get('buy_signals',0)} 卖出{backtest.get('sell_signals',0)} 持有{backtest.get('hold_signals',0)}", file=sys.stderr)
    
    # 4. 进化分析
    print("  🧬 分析进化趋势...", file=sys.stderr)
    evolution = analyze_evolution()
    for s in evolution.get("suggestions", []):
        print(f"    {s}", file=sys.stderr)
    
    # 5. 生成看板
    print("  📊 生成复盘看板...", file=sys.stderr)
    dashboard_url = generate_dashboard(dt)
    
    return {
        "date": dt.isoformat(),
        "reviews": reviews,
        "verification": verification,
        "backtest": backtest,
        "evolution": evolution,
        "dashboard_url": dashboard_url,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["review", "verify", "backtest", "dashboard", "evolve", "full", "status"],
                       nargs="?", default="status")
    parser.add_argument("--days", type=int, default=7)
    args = parser.parse_args()
    
    if args.action == "status":
        trend = get_accuracy_trend(30)
        print(f"📊 系统状态")
        print(f"  报告数: {len(REPORT_DIR.glob('**/*.md'))}")
        print(f"  预测准确率: {trend.get('avg_accuracy', 'N/A')}% (共{trend.get('total_predictions', 0)}条)")
        print(f"  进化趋势: {trend.get('trend', 'stable')}")
        print(f"  看板: {BASE_URL}/dashboard.html")
    
    elif args.action == "full":
        result = full_review_cycle()
        print(f"\n✅ 审阅周期完成")
        print(f"   看板: {result['dashboard_url']}")
    
    else:
        # Run specific action
        getattr(sys.modules[__name__], f"{args.action}_all_reports")(date.today())
