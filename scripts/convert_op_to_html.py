#!/opt/data/.venv/bin/python3
"""convert_op_to_html.py — 操作记录markdown → 自适应HTML，上传R2，更新dashboard.json"""

import sys, os, json, subprocess, re

HERMES = '/opt/data'
OPS_DIR = os.path.join(HERMES, 'fund_system_data', 'operations')
DASHBOARD = os.path.join(HERMES, 'fund_system_data', 'dashboard.json')
UPLOADER = os.path.join(HERMES, 'r2_uploader.py')

R2_BASE = 'https://hermes-main-media.devtoy.xyz/fund-system'

def md_to_html(md_text):
    """极简markdown→HTML转换（不引入第三方库，覆盖操作记录格式）"""
    lines = md_text.split('\n')
    html_parts = ['<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">',
                  '<meta name="viewport" content="width=device-width,initial-scale=1.0">',
                  '<title>操作记录</title>',
                  '<style>',
                  'body{background:#111;color:#e5e5e5;font-family:-apple-system,BlinkMacSystemFont,'
                  '"Segoe UI",Roboto,sans-serif;font-size:15px;line-height:1.7;'
                  'max-width:720px;margin:0 auto;padding:16px}',
                  'h1{font-size:20px;border-bottom:1px solid #333;padding-bottom:8px;margin:0 0 16px}',
                  'h2{font-size:16px;margin:20px 0 10px;color:#60a5fa}',
                  'h3{font-size:14px;margin:16px 0 8px;color:#a78bfa}',
                  'p{margin:6px 0}',
                  'blockquote{border-left:3px solid #60a5fa;padding:8px 12px;margin:12px 0;'
                  'background:#1a1a2e;border-radius:0 6px 6px 0;color:#cbd5e1;font-size:13px}',
                  'table{width:100%;border-collapse:collapse;margin:12px 0;font-size:13px}',
                  'th,td{border:1px solid #333;padding:6px 8px;text-align:left}',
                  'th{background:#1a1a2e;color:#60a5fa;font-weight:600}',
                  'td{background:#0d0d0d;color:#d1d5db}',
                  'td:first-child{font-weight:600}',
                  'strong{color:#fbbf24}',
                  'em{color:#9ca3af}',
                  'code{background:#1a1a2e;padding:1px 4px;border-radius:3px;font-size:13px}',
                  'hr{border:none;border-top:1px solid #333;margin:16px 0}',
                  '.meta{background:#1a1a2e;border-radius:8px;padding:12px;margin:12px 0}',
                  '.meta p{margin:3px 0;font-size:13px}',
                  '.status-ok{color:#22c55e}',
                  '.status-pending{color:#eab308}',
                  '</style></head><body>']
    in_table = False
    in_blockquote = False
    for line in lines:
        stripped = line.strip()
        # 空行
        if not stripped:
            if in_table:
                html_parts.append('</tbody></table>')
                in_table = False
            if in_blockquote:
                html_parts.append('</blockquote>')
                in_blockquote = False
            continue
        # 分割线
        if stripped.startswith('---'):
            html_parts.append('<hr>')
            continue
        # 标题
        if stripped.startswith('# '):
            html_parts.append(f'<h1>{stripped[2:]}</h1>')
            continue
        if stripped.startswith('## '):
            html_parts.append(f'<h2>{stripped[3:]}</h2>')
            continue
        if stripped.startswith('### '):
            html_parts.append(f'<h3>{stripped[4:]}</h3>')
            continue
        # 表格行
        if stripped.startswith('|') and stripped.endswith('|'):
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            if not in_table:
                html_parts.append('<table><thead><tr>')
                for c in cells:
                    html_parts.append(f'<th>{c}</th>')
                html_parts.append('</tr></thead><tbody>')
                in_table = True
                continue
            if all(c in ('-'*len(c), f':{'-'*(len(c)-2)}:', f'{'-'*(len(c)-2)}:', f':{'-'*(len(c)-2)}') for c in cells):
                continue
            html_parts.append('<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>')
            continue
        # 引用
        if stripped.startswith('> '):
            if not in_blockquote:
                html_parts.append('<blockquote>')
                in_blockquote = True
            processed = stripped[2:]
            processed = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', processed)
            processed = re.sub(r'\*(.+?)\*', r'<em>\1</em>', processed)
            html_parts.append(f'<p>{processed}</p>')
            continue
        # 普通段落
        if in_table:
            html_parts.append('</tbody></table>')
            in_table = False
        if in_blockquote:
            html_parts.append('</blockquote>')
            in_blockquote = False
        processed = stripped
        processed = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', processed)
        processed = re.sub(r'\*(.+?)\*', r'<em>\1</em>', processed)
        html_parts.append(f'<p>{processed}</p>')
    if in_table:
        html_parts.append('</tbody></table>')
    html_parts.append('</body></html>')
    return '\n'.join(html_parts)


def update_dashboard_json(date_str, html_url):
    """更新dashboard.json中操作的detail_url指向HTML"""
    if not os.path.exists(DASHBOARD):
        return
    with open(DASHBOARD) as f:
        data = json.load(f)
    changed = False
    for op in data.get('operations', []):
        if op.get('date') == date_str:
            old = op.get('detail_url', '')
            if old != html_url:
                op['detail_url'] = html_url
                changed = True
    if changed:
        with open(DASHBOARD, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f'  ✅ dashboard.json 已更新')
    return changed


def main():
    if not os.path.isdir(OPS_DIR):
        print('❌ 无操作目录')
        return 1

    # 加载R2环境
    env_path = os.path.join(HERMES, 'profiles', 'investment', '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith('R2_') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k, v)

    files = sorted([f for f in os.listdir(OPS_DIR) if f.endswith('.md') and f != 'README.md'])
    ok = 0
    for fn in files:
        md_path = os.path.join(OPS_DIR, fn)
        with open(md_path) as f:
            md_content = f.read()

        # 生成HTML
        html = md_to_html(md_content)
        html_fn = fn.replace('.md', '.html')
        html_path = os.path.join(OPS_DIR, html_fn)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)

        # 上传
        key = f'fund-system/operations/{html_fn}'
        r = subprocess.run([sys.executable, UPLOADER, html_path, key, 'text/html; charset=utf-8'],
                           capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            date_match = re.search(r'operation_(\d{4}-\d{2}-\d{2})', fn)
            if date_match:
                html_url = f'{R2_BASE}/operations/{html_fn}'
                update_dashboard_json(date_match.group(1), html_url)
                print(f'  ✅ {html_fn} → R2')
                ok += 1
        else:
            print(f'  ❌ {html_fn}: {r.stderr[:100]}')

    # 重新上传整个dashboard.json（更新后的detail_url）
    if ok and os.path.exists(DASHBOARD):
        r2 = subprocess.run([sys.executable, UPLOADER, DASHBOARD, 'fund-system/dashboard.json',
                             'application/json; charset=utf-8'],
                            capture_output=True, text=True, timeout=30)
        if r2.returncode == 0:
            print(f'  ✅ dashboard.json (含HTML链接) → R2')

    print(f'\n完成: {ok}/{len(files)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
