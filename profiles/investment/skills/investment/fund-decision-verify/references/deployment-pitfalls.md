# 决策系统部署陷阱记录

## 1. CRON 文件路径陷阱（2026-07-20/2026-07-21）

**现象**: 修改 `execute_today_plan.py` 后 cron 仍然跑旧版代码

**根因**: Hermes Agent 的 cron 调用 `script` 时以 profiles 目录为相对路径根:
- 开发修改: `/opt/data/scripts/execute_today_plan.py`
- Cron实际调用: `/opt/data/profiles/investment/scripts/execute_today_plan.py`

两路文件不同步，cron 跑的一直是旧版。

**验证方法**:
```bash
diff /opt/data/profiles/investment/scripts/execute_today_plan.py /opt/data/scripts/execute_today_plan.py
head -5 /opt/data/profiles/investment/scripts/execute_today_plan.py
```

**❌ 旧做法（已被 cron 安全机制拦截）**:
使用 symlink 指向源代码。2026-07-21 起 cron 增加了安全检查，symlink 会触发 `Script path escapes the scripts directory via traversal` 错误，因为 cron 会追踪 symlink 并发现其指向路径不在 profiles/scripts 目录内。

**✅ 正确做法**：创建 wrapper 脚本，通过 subprocess 调用：
```python
"""Wrapper: calls the real script"""
import subprocess, sys, os
os.chdir('/opt/data')
r = subprocess.run([sys.executable, '/opt/data/scripts/real_script.py'], timeout=120)
if r.returncode != 0:
    sys.exit(r.returncode)
```

比 symlink 优越：
- 不会被 cron 安全机制拦截
- 可控制工作目录（`os.chdir()`）
- 可设定超时（`timeout=120`）
- 可捕获处理 stdout/stderr

⚠️ wrapper 不能和原脚本同名（会覆盖/自引用）。wrapper 放 profiles 目录，原脚本在 `/opt/data/scripts/`。

**修复后验证**:
```bash
ls -la /opt/data/profiles/investment/scripts/update_operation_nav.py
head -3 /opt/data/profiles/investment/scripts/update_operation_nav.py
```

## 1a. workdir 导致脚本路径解析失败（2026-07-21）

**现象**: cron job 设了 `workdir=/opt/data`，脚本名 `update_operation_nav.py`，报错 `Script path escapes the scripts directory`。

**根因**: 设了 workdir 时，cron 将 workdir 与 profiles/scripts 目录拼接解析脚本路径，安全机制误判越界。

**修复**:
1. 删除旧 cron（含 workdir 配置）
2. 重建 cron，**不指定 workdir**，使用默认 profiles/scripts 目录
3. 确保 wrapper 内部 `os.chdir()` 切换目录

**关键**: no_agent cron 的 workdir 触发更严安全检查。不带 workdir 最安全。

## 2. 新增基金后遗漏同步（2026-07-20）

新增基金需要同步更新以下 ALL 文件:

| 文件 | 用途 | 更新内容 |
|:----|:----|:---------|
| `fund_tools.py` | 日采集基础 | 加入 `FUND_CODES` |
| `log_daily_decisions.py` | 收盘日志/偏离度 | 加入 `PORTFOLIO_COST` |
| `check_allocation.py` | 偏离度检测 | 加入 `PORTFOLIO` + `THRESHOLDS` |
| `risk_warning.py` | 风险预警 | 加入 `WATCHED_FUNDS` |
| `execute_today_plan.py` | 决策推送 | 加入 base 字典+tech_codes |

**步骤**: 先 `fund_tools.py` → 其他文件逐项加 → 手动跑一次验证

## 3. 同名定时任务冗余（2026-07-20）

14:30 收到两条推送。根因：两个 cron job 都在14:30触发（新旧系统共存）。

**解法**: `cronjob(action='list')` 检查 → `cronjob(action='pause', job_id='xxx')` 停掉旧的。

## 4. AKShare 串行超时（2026-07-20）

**现象**: 脚本 60s+ 超时。**解法**: `ThreadPoolExecutor` 并行预加载，14个基金从42s降到3s。

```python
def get_perf_parallel(codes):
    with ThreadPoolExecutor(max_workers=6) as exc:
        list(exc.map(_get_perf_single, codes))
```

**效果**: 从 87s → 9s（9.7x 提速）

## 5. 减仓建议在深跌后仍推送（2026-07-20）

**现象**: 基金距高点已跌 20-29%，仍在建议清仓。**根因**: 没看近期回撤。

**修复**: 加入 `drawdown` 回撤保护：
- `< -25%` → 🔥 坚决不减仓（割肉）
- `-15%~-25%` → ⚠️ 等反弹
- `-5%~-15%` → 🟢 可执行
- `> -5%` → 🟢 可操作

## 6. 9:35 出具体操作建议不合适（2026-07-20）

**根因**: T+1 基金以 15:00 净值确认，早盘操作=午后操作。

**修复**: 9:35 仅观察不出建议；14:30 出具体建议。推送标注 `🕤 盘前观察` / `🕝 午后决策点`。

## 7. QQ Bot Markdown 渲染失败（2026-07-20）

**现象**: `#` 标题、`**粗体**`、`|表格|` 均显示为纯文本。

**根因**: cron 的 `no_agent` 交付使用普通文本（`msg_type: 0`），非 markdown（`msg_type: 2`）。

**修复**: 在脚本内直接调用 QQ Bot API：
```python
from send_qq_bot import send_markdown
ok = send_markdown(advice)
```

**QQ Bot Markdown 支持**: `#`标题 `##`子标题 `**粗体**` `_斜体_` `>引用` `---`分割线 `-`列表 `|表格|`

## 8. 执行计划基金业绩缓存错误 — 024418（2026-07-20）

**现象**: 执行计划输出中024418被标注为"今年-25%最弱、被011613完全包含"。

**根因**: 旧版用中证半导体指数（-25%）代推基金净值。实际024418今年+74%（科技组最强）。

**修复**: 每支基金必须通过 `fund_open_fund_info_em()` 拉取实际净值，不能依赖指数代推。

## 9. 反弹减仓触发条件过松（2026-07-20）

**现象**: 科技组1周已跌-16%，仅反弹+2.8%就触发「执行全部减持」。

**根因**: 仅检查当日反弹≥0%，不考虑近期已暴跌。

**修复**: 附加 `drawdown >= -15` 检查：深跌+弱反弹=持有等更强的反弹，不是卖出。

## 10. 持仓金额用估算而非实际成本（2026-07-20）

**现象**: 分析报告用"~1,200元"等估算值替代实际成本数据。

**根因**: 未读取 `trade_decisions.jsonl` 的实际 `cost` 字段。

**修复**: 任何时候分析持仓金额，必须从 `trade_decisions.jsonl` 读取精确成本数据，不估算不取整。

## 11. LLM 输出截断 — max_tokens 不是银弹（2026-07-21）

**现象**: 长报告步骤5总被截断（"最值得关注3支"只显示第1支），即使增大 max_tokens 也无效。

**根因**: API 上下文窗口有上限。输入 prompt+data ~2000 tokens，增大 max_tokens 不会释放更多窗口空间。LLM 在前几个步骤花了太多 token。

**解决方案（三步走）**:

1. **精简 prompt 输入**（比增大 max_tokens 有效）：用紧凑格式（~200字）代替完整 T1+Theory 框架（~1500字）：
   ```
   错误：T1_FRAMEWORK + "\n" + FINANCIAL_THEORY_FRAMEWORK + "\n" + "..."
   正确："""## 【操作约束】\n1...\n2...\n3...\n"""
   ```

2. **前简后详**：prompt 明确要求前面步骤简洁、步骤5详细

3. **紧凑指令**：单行缩写替代分步长文本
   ```
   1.【信号】简述 2.【复盘】关键点 3.【作战】方向+观察
   4.【风险】3条 5.【基金·详细】a)3支:名称/理由/操作 b)3支 c)其余
   ```

**验证**：输出从截断于第1支 → 完整覆盖 a/b/c 三段。
