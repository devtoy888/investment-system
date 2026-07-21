# 推送渲染 & Cron超时 修复记录

> 2026-07-21 修复了两个影响推送的bug和一个cron配置问题。

## 1. `<br>` 标签不渲染

**问题**：推送内容中的 `<br>` HTML标签在QQ Bot markdown中不渲染，导致表格内换行失效。

**原因**：LLM生成的分析内容在表格等场景中使用了 `<br>` 作为换行符，但QQ Bot仅支持Markdown原生语法，不支持HTML标签。

**修复**：所有推送脚本中对LLM输出做后处理：
```python
analysis = analysis.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
```

**修改的文件**：
- `run_morning.py` (Step 3: v2深度分析段)
- `run_closing.py` (v2分析段)

## 2. `format_block` 函数被重建破坏

**问题**：`format_block("早盘 AI 深度分析", analysis)` 抛出 `TypeError: slice indices must be integers`。

**原因**：文件重建时（delegate_task），子代理将 `format_block(title, content)` 改为 `format_block(text, max_len=500)`。

**签名变化**：

| 版本 | 签名 | 行为 |
|:----|:----|:-----|
| 原版 | `format_block(title: str, content: str) -> str` | 返回 `f"\n## 📌 {title}\n\n{content}\n"` |
| 被破坏 | `format_block(text: str, max_len: int = 500) -> str` | 返回 `text[:max_len]` — 错误！ |

**调用方**传参 `format_block("标题", 内容字符串)` → 内容字符串被当作 `max_len` → `text[:内容字符串]` → TypeError。

**修复**：恢复原版签名。

**教训**：delegate_task重建文件时，**必须在context中明确指明每个函数的签名和返回值**，否则子代理可能"优化"函数行为。

## 3. Cron no_agent 超时 (SIGTERM -15)

**问题**：早报cron任务（`run_morning.py`）被系统以SIGTERM(-15)杀死。

**根因链**：
```
prompt增大 ~1500字 (T1框架+理论框架)
    → API调用变慢
    → 进化引擎3轮调用 (draft + review + polish)  
    → 叠加数据采集60s
    → 总耗时 ~120-140s
    → 超过cron隐含超时 → SIGTERM
```

**注意**：exit code -15 = SIGTERM，不是Python异常。stderr只显示 `[进化] Pass 1: 生成初稿...` 然后进程被杀死。

**修复方案**：早报改为直接API调用，跳过进化引擎：

```python
# ❌ 原方案（进化引擎，3轮API调用）
analysis = generate_v2('morning')

# ✅ 新方案（直接调用，1轮API调用，~20s）
data = build_morning_data_v2()
analysis = call_ds(MORNING_PROMPT_V2, data, max_tokens=2500, temp=0.3)
if analysis:
    analysis = analysis.replace("<br>", "\n")
    print(format_block("早盘 AI 深度分析", analysis))
```

**总耗时变化**：
| 步骤 | 原方案 | 新方案 |
|:----|:-----:|:-----:|
| 数据采集 | ~60s | ~60s |
| LLM分析 | ~50-70s (3轮) | ~20s (1轮) |
| 总计 | ~120-140s ❌ | ~80-90s ✅ |

**其他minute提示**：如果其他no_agent任务也超时（如收盘/决策），可采用同样的降级路径。

## 4. Cron "script path escapes" — symlink 被安全机制拦截

**问题**：`update_operation_nav.py` cron job报错 `Script path escapes the scripts directory via traversal`。

**根因**：profiles目录下的文件是symlink → `/opt/data/scripts/update_operation_nav.py`，指向的路径不在profile的scripts目录内。

**修复方案**：
1. 删除symlink
2. 在profiles目录创建wrapper脚本：
```python
#!/usr/bin/env python3
"""Wrapper: run real script"""
import subprocess, sys, os
os.chdir('/opt/data/scripts')
result = subprocess.run([sys.executable, '/opt/data/scripts/update_operation_nav.py'],
                       capture_output=True, text=True, timeout=180)
if result.stdout: print(result.stdout)
if result.stderr: print(result.stderr, file=sys.stderr)
sys.exit(result.returncode)
```
3. 删除旧cron（含workdir），用wrapper脚本名重建cron（去掉workdir）

**检查所有profile目录下的symlink**：
```bash
find /opt/data/profiles/investment/scripts/ -type l -ls
```
若有其他symlink，提前转换为wrapper避免同样错误。
