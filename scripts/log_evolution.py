#!/usr/bin/env python3
"""
进化日志脚本 — 每次系统变更后手动/自动执行
1. 在 EVOLUTION_LOG.md 追加记录
2. 生成 SYSTEM_DESIGN_v{N}.md 新版本快照
3. 上传到 R2

用法:
  python3 log_evolution.py "v4" "新增周末外盘速报" --changes 新增cron:周六09:00 新增cron:数据源验证 新增cron:加仓信号监控
"""
import argparse, json, os, sys, subprocess
from pathlib import Path
from datetime import date, datetime

DATA_DIR = Path("/opt/data/fund_system_data")
SCRIPTS_DIR = Path("/opt/data/scripts")
EVOLUTION_DIR = DATA_DIR / "evolution"
STRATEGY_DIR = DATA_DIR / "strategy"  # local cache
R2_BASE = "fund-system"

FUND_SYSTEM_PREFIX = os.environ.get("FUND_SYSTEM_PREFIX", "fund-system")

def parse_args():
    parser = argparse.ArgumentParser(description="记录系统进化并上传R2")
    parser.add_argument("version", help="版本号，如 v4")
    parser.add_argument("title", help="本次进化标题")
    parser.add_argument("--changes", action="append", default=[], help="变更明细（可重复）")
    parser.add_argument("--issues", action="append", default=[], help="自检发现（可重复）")
    parser.add_argument("--pending", action="append", default=[], help="待办事项（可重复）")
    return parser.parse_args()

def upload_file(local_path, r2_key, content_type="text/markdown"):
    """上传文件到R2，复用 fund_tools.py 的 upload_to_r2"""
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        from fund_tools import upload_to_r2
        url = upload_to_r2(str(local_path), r2_key, content_type)
        return url
    except Exception as e:
        print(f"  ⚠️ R2上传失败: {e}")
        return None

def update_evolution_log(args):
    """更新 EVOLUTION_LOG.md"""
    log_path = EVOLUTION_DIR / "EVOLUTION_LOG.md"
    EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
    
    today = date.today().isoformat()
    entry = [
        f"\n## {args.version} → 下一版 ({today})",
        f"### 变更：{args.title}",
    ]
    
    if args.changes:
        entry.append("")
        for c in args.changes:
            entry.append(f"- {c}")
    
    if args.issues:
        entry.append("")
        entry.append("### 自检发现")
        for i in args.issues:
            entry.append(f"- {i}")
    
    if args.pending:
        entry.append("")
        entry.append("### 待办")
        for p in args.pending:
            entry.append(f"- [ ] {p}")
    
    entry.append("")
    
    if log_path.exists():
        content = log_path.read_text()
        # 在第一个"---" 之后插入新记录，或追加到最后
        content += "\n".join(entry)
    else:
        content = [
            "# 系统进化日志",
            "",
            f"> 首次创建: {today}",
            "> 每次系统变更自动追加记录",
            "---",
        ]
        content.extend(entry)
        content = "\n".join(content)
    
    log_path.write_text(content)
    
    # 上传到R2
    r2_key = f"{FUND_SYSTEM_PREFIX}/evolution/EVOLUTION_LOG.md"
    url = upload_file(log_path, r2_key)
    return url

def snapshot_strategy_docs(args):
    """生成当前策略文档快照并上传"""
    today = date.today().isoformat()
    snapshot_name = f"SYSTEM_DESIGN_{args.version}.md"
    local_path = DATA_DIR / "strategy" / snapshot_name
    STRATEGY_DIR.mkdir(parents=True, exist_ok=True)
    
    # 生成新版本快照
    doc = [
        f"# 系统设计 {args.version}",
        f"> 生成日期: {today}",
        f"> 进化: {args.title}",
        "---",
        "",
        "## 本次变更",
    ]
    
    if args.changes:
        for c in args.changes:
            doc.append(f"- {c}")
    
    doc.append("")
    doc.append("## 自检问题")
    if args.issues:
        for i in args.issues:
            doc.append(f"- {i}")
    else:
        doc.append("- 无严重问题")
    
    doc.append("")
    doc.append("## 待办")
    if args.pending:
        for p in args.pending:
            doc.append(f"- [ ] {p}")
    else:
        doc.append("- 无")
    
    doc.append("")
    doc.append("---")
    doc.append(f"*参考：R2 {FUND_SYSTEM_PREFIX}/strategy/SYSTEM_DESIGN_v*")
    
    local_path.write_text("\n".join(doc))
    
    r2_key = f"{FUND_SYSTEM_PREFIX}/strategy/{snapshot_name}"
    url = upload_file(local_path, r2_key)
    return url, snapshot_name

def main():
    args = parse_args()
    
    print(f"━" * 50)
    print(f"📝 记录系统进化: {args.version} — {args.title}")
    print(f"━" * 50)
    
    # 1. 更新进化日志
    print(f"\n📋 更新进化日志...")
    log_url = update_evolution_log(args)
    print(f"   EVOLUTION_LOG.md -> {'✅ ' + log_url if log_url else '⚠️ 上传失败'}")
    
    # 2. 生成快照
    print(f"\n📸 生成策略快照...")
    snap_url, snap_name = snapshot_strategy_docs(args)
    print(f"   {snap_name} -> {'✅ ' + snap_url if snap_url else '⚠️ 上传失败'}")
    
    # 3. 输出R2路径
    print(f"\n📎 R2 存档路径")
    print(f"   进化日志: {FUND_SYSTEM_PREFIX}/evolution/EVOLUTION_LOG.md")
    print(f"   设计快照: {FUND_SYSTEM_PREFIX}/strategy/{snap_name}")
    
    print(f"\n✅ 进化记录完成")

if __name__ == "__main__":
    main()
