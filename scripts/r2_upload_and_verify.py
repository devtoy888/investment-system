#!/usr/bin/env python3
"""
R2 上传验证工具

用法:
  python3 r2_upload_and_verify.py local.md [remote-key]
  python3 r2_upload_and_verify.py --verify-only <url>

功能:
  1. 上传文件到 R2（带正确 Content-Type）
  2. 自动检测文件编码
  3. 验证 Content-Type 头
  4. 验证中文可读性
  5. 输出验证报告
"""

import os, sys, urllib.request, mimetypes

CONTENT_TYPE_MAP = {
    '.md': 'text/plain; charset=utf-8',
    '.html': 'text/html; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
    '.gif': 'image/gif', '.pdf': 'application/pdf',
    '.txt': 'text/plain; charset=utf-8',
    '.yaml': 'text/plain; charset=utf-8', '.yml': 'text/plain; charset=utf-8',
}

CHINESE_KEYWORDS = {
    '.md': ['方案', '架构', '部署', '配置', '分析', '知识图谱'],
    '.html': ['方案', '架构', '部署'],
}


def verify_url(url, expected_ct=None, check_chinese=True, filepath=None):
    """验证远程文件的 Content-Type + 编码 + 中文可读性"""
    results = []

    req = urllib.request.Request(url)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36')
    try:
        resp = urllib.request.urlopen(req, timeout=30)
    except Exception as e:
        results.append({'check': 'HTTP 请求', 'status': '❌', 'detail': str(e)})
        return results

    actual_ct = resp.headers.get('Content-Type', '')
    code = resp.status
    results.append({'check': 'HTTP 状态码', 'status': '✅' if code == 200 else '❌',
                    'detail': str(code)})
    results.append({'check': f'Content-Type (期望: {expected_ct})',
                    'status': '✅' if expected_ct and expected_ct in actual_ct else '⚠️',
                    'detail': actual_ct})

    if not check_chinese:
        return results
    try:
        body = resp.read()
    except Exception as e:
        results.append({'check': '内容下载', 'status': '⚠️', 'detail': str(e)})
        return results

    try:
        text = body.decode('utf-8')
        charset = 'utf-8'
    except UnicodeDecodeError:
        text = body.decode('gbk', errors='replace')
        charset = 'gbk (fallback)'

    results.append({'check': '编码检测',
                    'status': '✅' if charset == 'utf-8' else '⚠️',
                    'detail': charset})

    if filepath:
        ext = os.path.splitext(filepath)[1].lower()
        keywords = CHINESE_KEYWORDS.get(ext, ['方案', '配置', '分析', '知识'])
        found = [kw for kw in keywords if kw in text]
        not_found = [kw for kw in keywords if kw not in text]
        if found:
            results.append({
                'check': f'中文可读性 (找到: {found[:3]})',
                'status': '✅' if not not_found else '⚠️',
                'detail': f'找到{len(found)}个{"，缺"+str(not_found) if not_found else ""}'
            })
        else:
            results.append({'check': '中文可读性', 'status': '❌',
                            'detail': '未找到任何中文字符，可能编码问题！'})

    results.append({'check': '内容长度', 'status': '✅',
                    'detail': f'{len(body)} bytes / {len(text)} chars'})
    return results


def upload_and_verify(local_path, remote_key=None):
    """上传文件并自动验证"""
    from r2_uploader import R2Uploader

    if not os.path.exists(local_path):
        print(f'❌ 文件不存在: {local_path}')
        return False

    if not remote_key:
        remote_key = os.path.basename(local_path)

    ext = os.path.splitext(local_path)[1].lower()
    content_type = CONTENT_TYPE_MAP.get(ext)
    if not content_type:
        content_type, _ = mimetypes.guess_type(local_path) or ('application/octet-stream', None)

    with open(local_path, 'rb') as f:
        raw = f.read(8192)
    if raw[:3] == b'\xef\xbb\xbf':
        encoding = 'utf-8-bom (有 BOM)'
    else:
        try:
            raw.decode('utf-8')
            encoding = 'utf-8'
        except UnicodeDecodeError:
            encoding = 'gbk (⚠️ 需要转 UTF-8)'

    print(f'\n═══ 上传 ═══')
    print(f'  本地: {local_path} ({encoding})')
    print(f'  远程: {remote_key}')
    print(f'  Content-Type: {content_type}')

    if 'gbk' in encoding:
        print(f'  ⚠️ GBK 编码！浏览器中文乱码风险')
        print(f'  建议: iconv -f gbk -t utf-8 {local_path} > {local_path}.utf8')

    uploader = R2Uploader()
    url = uploader.upload_file(local_path, remote_key, content_type=content_type)
    print(f'  上传完成: {url}')

    print(f'\n═══ 验证 ═══')
    results = verify_url(url, expected_ct=content_type, check_chinese=True, filepath=local_path)
    all_pass = True
    for r in results:
        print(f'  {r["check"]}: {r["status"]}  {r["detail"]}')
        if '❌' in r['status']:
            all_pass = False

    print(f'\n{"✅ 全部通过" if all_pass else "⚠️ 有问题"} → {url}')
    return all_pass


def verify_only(url):
    """只验证已有 URL"""
    print(f'\n═══ 验证远程文件 ═══')
    ext = os.path.splitext(url.split('?')[0])[1].lower()
    expected_ct = CONTENT_TYPE_MAP.get(ext, 'unknown')
    results = verify_url(url, expected_ct=expected_ct, check_chinese=True, filepath=url)
    for r in results:
        print(f'  {r["check"]}: {r["status"]}  {r["detail"]}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'用法:\n  python3 {sys.argv[0]} local.md [remote-key]\n  python3 {sys.argv[0]} --verify-only <url>')
        sys.exit(1)
    if sys.argv[1] == '--verify-only':
        verify_only(sys.argv[2])
    else:
        upload_and_verify(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
