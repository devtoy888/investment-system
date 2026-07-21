#!/usr/bin/env python3
"""
KOL信号因子验证 — 验证博主预测方向 vs 实际市场走势

读取 signals.jsonl 的历史信号，对比实际指数/板块涨跌，输出:
  - 各KOL准确率（整体/方向/板块）
  - IC/IR 信息系数
  - 最佳/最差预测案例
"""
import sys, os, json, re
sys.path.insert(0, '/opt/data/scripts')
# numpy/pandas 通过 akshare-deps 加载
_DEPS = "/opt/data/akshare-deps"
if os.path.isdir(_DEPS) and _DEPS not in sys.path:
    sys.path.insert(0, _DEPS)
from pathlib import Path
from datetime import datetime, date
from collections import defaultdict
import numpy as np

DATA_DIR = Path("/opt/data/fund_system_data")
SIGNALS_FILE = DATA_DIR / "signals.jsonl"
NOON_FILE = DATA_DIR / "noon-briefs.jsonl"
SNAPSHOTS_FILE = DATA_DIR / "daily-snapshots.jsonl"

# ── 板块到指数的映射（用于验证方向预测）──
SECTOR_INDEX_MAP = {
    "大盘": "上证指数",
    "科创50": "科创50",
    "半导体": "科创50",
    "科技": "科创50",
    "消费": "消费",
    "医药": "医药",
    "新能源": "新能源",
    "光伏": "光伏",
    "军工": "军工",
    "金融": "券商",
    "资源": "有色金属",
    "周期": "有色金属",
}

def load_signals() -> list[dict]:
    """加载所有信号"""
    if not SIGNALS_FILE.exists():
        return []
    lines = [l.strip() for l in SIGNALS_FILE.read_text().split('\n') if l.strip()]
    return [json.loads(l) for l in lines]

def load_noon_data() -> dict[str, dict]:
    """按日期索引午盘数据"""
    if not NOON_FILE.exists():
        return {}
    lines = [l.strip() for l in NOON_FILE.read_text().split('\n') if l.strip()]
    result = {}
    for l in lines:
        try:
            d = json.loads(l)
            result[d.get("date", "")] = d
        except:
            pass
    return result

def get_index_change(signal: dict, noon_data: dict[str, dict]) -> float | None:
    """获取信号对应板块的实际涨跌幅"""
    date_str = signal.get("date", "")
    sector = signal.get("predicted_sector", "大盘")
    index_name = SECTOR_INDEX_MAP.get(sector, "上证指数")
    
    # 从午盘数据获取
    noon = noon_data.get(date_str, {})
    quotes = noon.get("quotes", {})
    if index_name in quotes:
        val = quotes[index_name].get("change_pct")
        if val is not None:
            return float(str(val).replace("%", ""))
    
    # 从 snapshots 获取
    return None

def verify_signal(signal: dict, noon_data: dict[str, dict]) -> dict:
    """验证单条信号：预测方向 vs 实际走势"""
    actual_change = get_index_change(signal, noon_data)
    pred_dir = signal.get("predicted_direction", "neutral")
    
    result = {
        "date": signal.get("date"),
        "kol": signal.get("kol_name"),
        "sector": signal.get("predicted_sector"),
        "direction": pred_dir,
        "actual_change": actual_change,
        "correct": None,
        "resolved": False,
    }
    
    if actual_change is None:
        return result
    
    result["resolved"] = True
    
    # 判断是否正确
    if pred_dir == "bullish":
        result["correct"] = actual_change > 0
    elif pred_dir == "bearish":
        result["correct"] = actual_change < 0
    else:  # neutral 不参与准确率统计
        result["correct"] = None
    
    return result

def _spearman_rank(x: np.ndarray, y: np.ndarray) -> float:
    """手动计算Spearman秩相关系数（避免依赖scipy）"""
    n = len(x)
    if n < 3:
        return 0.0
    # 排名（从1开始）
    x_rank = np.argsort(np.argsort(x)).astype(float) + 1
    y_rank = np.argsort(np.argsort(y)).astype(float) + 1
    d = x_rank - y_rank
    rho = 1 - (6 * np.sum(d ** 2)) / (n * (n ** 2 - 1))
    return rho if not np.isnan(rho) else 0.0

def calc_ic(signals: list[dict], noon_data: dict[str, dict]) -> dict:
    """计算信息系数（IC）"""
    verified = []
    for s in signals:
        r = verify_signal(s, noon_data)
        if r["correct"] is not None and r["resolved"]:
            # 方向映射: bullish=1, bearish=-1
            pred_val = 1 if r["direction"] == "bullish" else -1
            act_val = 1 if r["actual_change"] > 0 else -1
            verified.append({"pred": pred_val, "act": act_val})
    
    if len(verified) < 5:
        return {"ic": 0, "ir": 0, "n": len(verified)}
    
    preds = np.array([v["pred"] for v in verified])
    acts = np.array([v["act"] for v in verified])
    
    # Spearman rank IC
    rho = _spearman_rank(preds, acts)
    ic_val = rho if not np.isnan(rho) else 0
    
    # Rank IC 序列（按日期分组）
    # 简单IR = mean(IC) / std(IC)
    ir_val = ic_val / np.std(preds - acts) if np.std(preds - acts) > 1e-10 else 0
    
    return {"ic": round(ic_val, 4), "ir": round(ir_val, 4), "n": len(verified)}

def build_report() -> str:
    """生成KOL因子验证报告"""
    signals = load_signals()
    noon_data = load_noon_data()
    
    if not signals:
        return "⚠️ 暂无信号数据，需要运行午盘/早盘采集后重新验证"
    
    total = len(signals)
    lines = [f"# 📊 KOL信号因子验证报告", f"> 生成时间: {datetime.now().isoformat()}", f"> 总信号数: {total}", ""]
    
    # ── 1. 各KOL准确率 ──
    lines.append("## 一、KOL准确率")
    lines.append("")
    lines.append("| KOL | 信号数 | 已验证 | 看多 | 看空 | 准确率 |")
    lines.append("|:----|:-----:|:-----:|:----:|:----:|:-----:|")
    
    kol_stats = defaultdict(lambda: {"total": 0, "verified": 0, "bullish": 0, "bearish": 0, "correct": 0})
    
    for s in signals:
        kol = s.get("kol_name", "未知")
        kol_stats[kol]["total"] += 1
        r = verify_signal(s, noon_data)
        if r["resolved"]:
            kol_stats[kol]["verified"] += 1
            if r["direction"] == "bullish":
                kol_stats[kol]["bullish"] += 1
            elif r["direction"] == "bearish":
                kol_stats[kol]["bearish"] += 1
            if r["correct"]:
                kol_stats[kol]["correct"] += 1
    
    for kol, st in sorted(kol_stats.items()):
        acc = st["correct"] / st["verified"] * 100 if st["verified"] > 0 else 0
        bar = "█" * int(acc / 5) + "░" * (20 - int(acc / 5))
        lines.append(f"| {kol} | {st['total']} | {st['verified']} | {st['bullish']} | {st['bearish']} | {bar} {acc:.1f}% |")
    
    # ── 2. 方向细分 ──
    lines.append("")
    lines.append("## 二、方向预测细分类")
    lines.append("")
    lines.append("| KOL | 看多准确率 | 看空准确率 | 中性占比 |")
    lines.append("|:----|:--------:|:--------:|:--------:|")
    
    for kol, st in sorted(kol_stats.items()):
        bull_correct = 0
        bear_correct = 0
        neutral_count = 0
        for s in signals:
            if s.get("kol_name") != kol:
                continue
            r = verify_signal(s, noon_data)
            if not r["resolved"]:
                continue
            if r["direction"] == "neutral":
                neutral_count += 1
            elif r["direction"] == "bullish" and r["correct"]:
                bull_correct += 1
            elif r["direction"] == "bearish" and r["correct"]:
                bear_correct += 1
        
        bull_acc = bull_correct / st["bullish"] * 100 if st["bullish"] > 0 else 0
        bear_acc = bear_correct / st["bearish"] * 100 if st["bearish"] > 0 else 0
        neut_pct = neutral_count / st["verified"] * 100 if st["verified"] > 0 else 0
        lines.append(f"| {kol} | {bull_acc:.1f}% | {bear_acc:.1f}% | {neut_pct:.1f}% |")
    
    # ── 3. IC 信息系数 ──
    lines.append("")
    lines.append("## 三、信息系数")
    lines.append("")
    ic_data = calc_ic(signals, noon_data)
    lines.append(f"- **IC（信息系数）**: {ic_data['ic']:.4f} ({'有效' if abs(ic_data['ic']) > 0.05 else '微弱' if abs(ic_data['ic']) > 0 else '无效'})")
    lines.append(f"- **IR（信息比率）**: {ic_data['ir']:.4f}")
    lines.append(f"- **样本量**: {ic_data['n']} 条可验证信号")
    if ic_data['ic'] > 0:
        lines.append("- ✅ 信号方向与市场走势正相关（方向对了）")
    elif ic_data['ic'] < 0:
        lines.append("- ⚠️ 信号方向与市场走势负相关（反向指标）")
    
    # ── 4. 板块命中率 ──
    lines.append("")
    lines.append("## 四、板块命中率")
    lines.append("")
    lines.append("| 板块 | 信号数 | 准确率 |")
    lines.append("|:----|:-----:|:-----:|")
    
    sector_stats = defaultdict(lambda: {"count": 0, "correct": 0})
    for s in signals:
        sec = s.get("predicted_sector", "大盘")
        r = verify_signal(s, noon_data)
        if r["resolved"] and r["correct"] is not None:
            sector_stats[sec]["count"] += 1
            if r["correct"]:
                sector_stats[sec]["correct"] += 1
    
    for sec, st in sorted(sector_stats.items(), key=lambda x: -x[1]["count"]):
        acc = st["correct"] / st["count"] * 100 if st["count"] > 0 else 0
        lines.append(f"| {sec} | {st['count']} | {acc:.1f}% |")
    
    # ── 5. 最佳/最差预测 ──
    lines.append("")
    lines.append("## 五、典型案例")
    lines.append("")
    
    # 排序：看多且涨最多 / 看多且跌最多
    best = []
    worst = []
    for s in signals:
        r = verify_signal(s, noon_data)
        if r["resolved"] and r["correct"] is not None and r["actual_change"] is not None:
            imp = abs(r["actual_change"])
            item = (imp, r["kol"], r["sector"], r["direction"], r["actual_change"], s.get("text_snippet", "")[:60])
            if r["correct"]:
                best.append(item)
            else:
                worst.append(item)
    
    best.sort(key=lambda x: -x[0])
    worst.sort(key=lambda x: -x[0])
    
    lines.append("### 最准判断（涨幅最大看多 / 跌幅最大看空）")
    for imp, kol, sec, dr, chg, txt in best[:3]:
        lines.append(f"- **{kol}** 看{dr} {sec}: 实际{chg:+.2f}% → ✅ \"{txt}...\"")
    
    lines.append("")
    lines.append("### 最差判断（看多反跌 / 看空反涨）")
    for imp, kol, sec, dr, chg, txt in worst[:3]:
        lines.append(f"- **{kol}** 看{dr} {sec}: 实际{chg:+.2f}% → ❌ \"{txt}...\"")
    
    return "\n".join(lines)

def main():
    report = build_report()
    print(report)
    
    # 存入 R2
    report_path = DATA_DIR / "reports" / f"kol-verify-{date.today().isoformat()}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)
    
    from fund_tools import upload_to_r2
    r2_url = upload_to_r2(str(report_path), f"fund-system/reports/kol-verify-{date.today().isoformat()}.md", "text/markdown; charset=utf-8")
    print(f"\n📄 报告已上传: {r2_url}")

if __name__ == "__main__":
    main()
