#!/usr/bin/env python3
"""
JSONL 自动去重脚本 — 每天收盘后运行
保留每天第一条有效记录，清除冗余

安全设计:
- 操作前备份原文件
- 只删明显重复（同一天的后序记录）
- 输出变更统计
"""
import json, shutil
from pathlib import Path
from collections import OrderedDict
from datetime import date, datetime

DATA_DIR = Path("/opt/data/fund_system_data")

# 不处理的文件（追加型数据）
SKIP_FILES = {"decisions.jsonl", "signals.jsonl"}

FILES = [
    ("morning-briefs.jsonl",  "date"),
    ("noon-briefs.jsonl",     "date"),
    ("closing-reviews.jsonl", "_date"),
    ("signals-resolved.jsonl","signal_date"),
]

def out(s=""):
    print(s)

def deduplicate_jsonl(path, date_key):
    """对JSONL去重：保持每天第一条有效记录"""
    if not path.exists():
        return 0, 0, None
    
    lines = path.read_text().split('\n')
    total = len(lines)
    
    seen_dates = OrderedDict()  # date -> (line_index, line_text)
    skipped = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            record = json.loads(stripped)
        except json.JSONDecodeError:
            skipped.append(i)
            continue
        
        d = record.get(date_key, "unknown")
        if d not in seen_dates:
            seen_dates[d] = (i, stripped)
        # 跳过同一天的后续记录
    
    deduped = [v[1] for v in seen_dates.values()]
    count_after = len(deduped)
    removed = total - count_after - len(skipped)
    
    if removed == 0:
        return 0, total, None
    
    # 备份原文件
    bak_path = path.with_suffix(".jsonl.bak")
    shutil.copy2(path, bak_path)
    
    # 写回去重后的内容（保留原始顺序）
    path.write_text('\n'.join(deduped) + '\n')
    
    return removed, count_after, bak_path

def main():
    today = date.today().isoformat()
    
    out("━" * 50)
    out(f"📦 JSONL 自动去重 — {today}")
    out("━" * 50)
    
    total_removed = 0
    total_kept = 0
    
    for fname, date_key in FILES:
        path = DATA_DIR / fname
        if not path.exists():
            out(f"\n🟡 {fname}: 文件不存在，跳过")
            continue
        
        removed, kept, bak = deduplicate_jsonl(path, date_key)
        total_removed += removed
        total_kept += kept
        
        if removed > 0:
            out(f"\n✅ {fname}: 移除{removed}条重复，保留{kept}条（备份: {bak.name})")
        else:
            out(f"\n✅ {fname}: {kept}条，无需去重")
    
    out(f"\n{'=' * 50}")
    out(f"合计: 移除 {total_removed} 条冗余，保留 {total_kept} 条有效记录")
    
    if total_removed > 0:
        out(f"⚠️ 原始文件已备份为 .jsonl.bak，确认无误后可删除")
        out(f"   删除命令: rm -f {DATA_DIR}/*.jsonl.bak")
    out(f"{'=' * 50}")

if __name__ == "__main__":
    main()
