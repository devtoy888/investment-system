#!/usr/bin/env python3
"""
只清理 cron 自动生成的 session 日志（source='cron'），保留用户真实对话。
默认删除 7 天前的 cron 日志。

用法:
  python prune_cron_sessions.py --days 7 --dry-run   # 只统计不删除
  python prune_cron_sessions.py --days 7             # 执行删除

必须放在 ~/.hermes/scripts/ 下（cronjob 只接受该目录内的相对路径）。
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.expanduser("~/.hermes/hermes-agent")) if os.path.exists(
    os.path.expanduser("~/.hermes/hermes-agent")) else None
import hermes_state


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=7,
                   help="删除 N 天前的 cron 日志（source='cron'）")
    p.add_argument("--dry-run", action="store_true", help="只统计不删除")
    p.add_argument("--hermes-home",
                   default=os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
    args = p.parse_args()

    db = hermes_state.SessionDB()

    # 先统计将要删除的（仅用于展示，实际删除数由 prune_sessions 返回）
    before = db.list_sessions_rich(source="cron", limit=100000, order_by_last_active=True)
    cutoff_ts = time.time() - args.days * 86400
    to_delete = [s["id"] for s in before
                 if (s.get("last_active_ts") or s.get("updated_at") or 0) < cutoff_ts]

    print(f"[prune_cron] 当前 cron session 总数: {len(before)}")
    print(f"[prune_cron] 将删除 {args.days} 天前的: {len(to_delete)} 条 (dry-run 预估值)")

    if args.dry_run:
        for sid in to_delete[:20]:
            print(f"  (dry) {sid}")
        if len(to_delete) > 20:
            print(f"  ... 还有 {len(to_delete) - 20} 条")
        print("[prune_cron] DRY-RUN 完成，未删除")
        return

    if to_delete:
        # 实际删除数由 prune_sessions 返回；可能与上面预估值不同（时间戳字段差异）
        n = db.prune_sessions(older_than_days=args.days, source="cron")
        print(f"[prune_cron] 已删除 {n} 条 cron session (prune_sessions 实返回值)")
    else:
        print("[prune_cron] 没有符合条件的 cron session")


if __name__ == "__main__":
    main()
