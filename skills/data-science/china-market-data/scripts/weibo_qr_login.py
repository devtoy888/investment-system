#!/usr/bin/env python3
"""
微博QR码登录脚本 — 在无头服务器上运行，生成二维码图片，等待扫码。
通过monkey-patch weibo-cli的_display_qr_in_terminal，用weibo-cli自身的登录逻辑，
同时将二维码保存为PNG图片（用于 MEDIA: 协议发送给用户）。

用法：
  PYTHONUNBUFFERED=1 python3 weibo_qr_login.py  # 建议用unbuffered模式

依赖：
  uv tool install kabi-weibo-cli
  pip install httpx qrcode[pil] Pillow
"""
import sys
import os

# 确保 weibo-cli 的包路径可访问
sys.path.insert(0, os.path.expanduser(
    '~/.local/share/uv/tools/kabi-weibo-cli/lib/python3.13/site-packages'
))

import qrcode
from PIL import Image

# Monkey-patch: 拦截weibo-cli的二维码显示函数，同时保存PNG
import weibo_cli.auth as auth

_original_display = auth._display_qr_in_terminal

def _patched_display(data):
    """显示二维码 + 保存为PNG图片"""
    # 保存PNG
    img = qrcode.make(data)
    img_path = '/opt/data/image_cache/weibo_qr_login.png'
    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    img.save(img_path)
    print(f'\n[QR Image saved: {img_path}]', flush=True)
    print(f'[Send to user: MEDIA:{img_path}]', flush=True)
    # 仍显示终端ASCII码作为后备
    return _original_display(data)

auth._display_qr_in_terminal = _patched_display

# 执行weibo-cli的完整QR登录流程
try:
    print('📱 正在获取微博登录二维码...', flush=True)
    cred = auth.qr_login()
    print('✅ 登录成功!', flush=True)
    
    # 验证凭据
    cookies = cred.cookies
    has_sub = 'SUB' in cookies
    print(f'✅ 凭据已保存 ({len(cookies)} cookies)', flush=True)
    print(f'✅ 含SUB cookie: {has_sub}', flush=True)
    
    if not has_sub:
        print('⚠️ 警告: 未获取到SUB cookie。可尝试访问weibo.com捕获更多cookie。', flush=True)
        
except Exception as e:
    print(f'❌ 登录失败: {e}', flush=True)
    sys.exit(1)
