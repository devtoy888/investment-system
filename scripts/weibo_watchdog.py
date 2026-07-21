#!/usr/bin/env python3
"""
微博 Cookie 过期间自动检测 + 修复（no_agent 模式）
每天早间运行：
- 凭证有效 → 静默退出（无输出 = 不推送）
- 凭证过期 → 生成二维码，推送到聊天窗口提醒用户扫码
"""
import sys, json, time, os, threading, queue, subprocess
from pathlib import Path

sys.path.insert(0, '/opt/data/scripts')
from fund_tools import get_user_weibos, CREDENTIAL_FILE

# ── 第一步：检测凭证有效性 ──
def check_credentials() -> bool:
    """返回 True 表示凭证有效"""
    if not CREDENTIAL_FILE.exists():
        return False
    # 先用真实API验证，不做文件年龄假设
    posts = get_user_weibos('2014433131', count=1)
    if not posts:
        return False
    # API验证通过后，检查文件年龄作为预警提示（不阻塞）
    age = time.time() - CREDENTIAL_FILE.stat().st_mtime
    if age > 12 * 86400:  # 12天预警（Weibo凭证约14-30天有效）
        print(f"⚠️ 微博凭证已 {age/86400:.0f} 天，接近到期，建议近期扫码续期")
    return True

if check_credentials():
    sys.exit(0)  # 凭证有效 → 静默退出

# ── 第二步：凭证过期，启动扫码修复 ──
print("🔴 微博凭证已过期/失效，正在生成登录二维码...")

# 生成二维码图片所在路径
QR_PATH = '/opt/data/image_cache/weibo_qr_login.png'

# 启动登录脚本作为后台子进程
proc = subprocess.Popen(
    ['python3', '/opt/data/scripts/weibo_login_direct.py'],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    text=True, bufsize=1
)

# 异步读取子进程输出
q = queue.Queue()
def enqueue_output(out, queue_obj):
    for line in iter(out.readline, ''):
        queue_obj.put(line)
    out.close()

t = threading.Thread(target=enqueue_output, args=(proc.stdout, q))
t.daemon = True
t.start()

# 等候 QR 生成（最多10秒）
qr_ready = False
start_ts = time.time()
while time.time() - start_ts < 10:
    try:
        line = q.get(timeout=0.5)
        line_s = line.strip()
        if 'QRID=' in line_s:
            pass  # 知道QRID，继续
        elif 'QR_READY' in line_s:
            qr_ready = True
            break
    except queue.Empty:
        break

if not qr_ready:
    print("❌ 二维码生成失败，请手动运行: python3 /opt/data/scripts/weibo_login_direct.py")
    sys.exit(1)

# 确认二维码图片存在
if not os.path.exists(QR_PATH):
    print(f"❌ 二维码图片未找到: {QR_PATH}")
    sys.exit(1)

# ── 第三步：输出扫码提醒（子进程继续在后台轮询登录） ──
print()
print("📱 **微博凭证已过期，请扫码续期**")
print()
print(f"MEDIA:{QR_PATH}")
print()
print("⏱️ 使用微博App扫描上方二维码，有效期约4分钟")
print("✅ 扫码后自动续期，无需额外操作")
print()
print("💡 若二维码过期，请回复「微博续期」重新生成")

# 子进程继续在后台运行，检测到扫码后自动保存凭证
# 不等待子进程结束——用户可能晚点才扫，让它在后台等满4分钟
