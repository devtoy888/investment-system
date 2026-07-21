#!/usr/bin/env python3
"""报告推送工具 — 生成MD/HTML + 上传R2 + 短摘要推送"""
import sys, os, json, re, subprocess
from pathlib import Path
from datetime import date, datetime
from html import escape

sys.path.insert(0, '/opt/data/scripts')
from send_qqbot import _output

DATA_DIR = Path("/opt/data/fund_system_data")
REPORT_DIR = DATA_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
BASE_URL = "https://hermes-main-media.devtoy.xyz/fund-system/reports"

def upload_to_r2(local: str, r2_key: str, ct: str = None):
    ct = ct or ("text/markdown; charset=utf-8" if r2_key.endswith('.md') else "text/html; charset=utf-8")
    subprocess.run([sys.executable, '-c',
        'import sys; sys.path.insert(0,"/opt/data/scripts"); from fund_tools import upload_to_r2 as up; up("%s","%s","%s")' % (local, r2_key, ct)
    ], capture_output=True, text=True, timeout=30)

def push_report(report_type: str, title: str, data_tables: str, analysis: str):
    """生成报告 → 日期目录 → R2推送 → 短摘要"""
    t = date.today()
    today = t.isoformat()
    subdir = f"{t.year}/{t.month:02d}/{t.day:02d}"
    full_md = "# " + title + "\n\n" + data_tables + "\n\n## 🤖 AI 深度分析\n\n" + analysis
    
    # 本地保存到日期子目录
    local_dir = REPORT_DIR / subdir
    local_dir.mkdir(parents=True, exist_ok=True)
    md_path = str(local_dir / f"{report_type}.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(full_md)
    
    html_path = str(local_dir / f"{report_type}.html")
    html_content = _build_html(full_md, title)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # R2路径带日期目录 + 兼容旧版平铺路径
    md_key = f"fund-system/reports/{subdir}/{report_type}.md"
    html_key = f"fund-system/reports/{subdir}/{report_type}.html"
    md_key_flat = f"fund-system/reports/{report_type}_{today}.md"
    html_key_flat = f"fund-system/reports/{report_type}_{today}.html"
    upload_to_r2(md_path, md_key)
    upload_to_r2(html_path, html_key, "text/html; charset=utf-8")
    # 同时上传扁平路径版（兼容已分享的旧链接）
    upload_to_r2(md_path, md_key_flat)
    upload_to_r2(html_path, html_key_flat, "text/html; charset=utf-8")
    
    md_link = f"{BASE_URL}/{subdir}/{report_type}.md"
    html_link = f"{BASE_URL}/{subdir}/{report_type}.html"
    
    summary = (
        "📊 " + title + "\n\n"
        "🤖 AI分析完成（" + str(len(analysis)) + "字）\n\n"
        "📄 " + md_link + "\n"
        "🌐 " + html_link + "\n"
    )
    
    _output(summary)
    return md_link, html_link

# ═══════════════════════════════════════════
# HTML 构建
# ═══════════════════════════════════════════

def _build_html(md: str, title: str) -> str:
    """Markdown → 美观分区块HTML，支持深浅模式"""
    lines = md.split('\n')
    
    # Split into data section and AI analysis section
    ai_idx = None
    for i, l in enumerate(lines):
        if 'AI 深度分析' in l or ('深度分析' in l and '##' in l):
            ai_idx = i
            break
    
    data_lines = lines[:ai_idx] if ai_idx else []
    ai_lines = lines[ai_idx+1:] if ai_idx else []
    
    # Render data tables
    data_html = ""
    i = 0
    while i < len(data_lines):
        l = data_lines[i]
        s = l.strip()
        # Skip H1 title (already in HTML header)
        if s.startswith('# ') and i == 0:
            i += 1
            continue
        if s.startswith('|') and s.endswith('|'):
            tbl = []
            while i < len(data_lines) and data_lines[i].strip().startswith('|'):
                tbl.append(data_lines[i])
                i += 1
            data_html += _render_table(tbl)
        elif s.startswith('## '):
            h2 = s[3:]
            icon = "\U0001f4ca"
            if '\U0001f319' in h2 or '外盘' in h2: icon = '\U0001f319'
            elif 'A股' in h2 or '昨收' in h2: icon = '\U0001f4c8'
            elif '量价' in h2: icon = '\U0001f4c9'
            elif '板块' in h2: icon = '\U0001f525'
            elif '持仓' in h2: icon = '\U0001f4b0'
            data_html += f'<h3 class="sh">{icon} {escape(h2)}</h3>'
        elif s.startswith('**') or (s and '---' not in s):
            cls = ''
            if any(c in s for c in ['\U0001f534', '\U0001f4c8', '\U0001f525']):
                cls = ' up'
            elif any(c in s for c in ['\U0001f7e2', '\U0001f4c9', '\U0001f4a7']):
                cls = ' down'
            if cls:
                data_html += f'<p class="{cls}">{_fmt(s)}</p>'
            elif s.startswith('**') and s.endswith('**'):
                data_html += f'<p class="bl">{_fmt(s.strip("*"))}</p>'
            else:
                data_html += f'<p>{_fmt(s)}</p>'
        i += 1
    
    # Render AI analysis
    ai_html = ""
    steps = _parse_steps(ai_lines)
    for title_text, body in steps:
        ai_html += _step_card(title_text, body)
    
    # Handle step 5 fund table specially
    ai_html = ai_html.replace('<FUND_TABLE>', '<div class="ft-wrap">')
    ai_html = ai_html.replace('</FUND_TABLE>', '</div>')
    
    et = escape(title)
    d = date.today().isoformat()
    now = datetime.now().strftime('%H:%M')
    
    return (
        '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n'
        '<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width,initial-scale=1.0">\n'
        '<title>' + et + '</title>\n<style>\n'
        
        # CSS variables for theme
        ':root{--bg:#f0f2f5;--cd:#fff;--tx:#1a1a2e;--t2:#666;--bd:#eee;--ac:#4a6cf7;'
        '--up:#e74c3c;--dn:#27ae60;--rk:#fff5f5;--hdr:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460)}\n'
        '.dk{--bg:#0d0d1a;--cd:#16162a;--tx:#e0e0e0;--t2:#888;--bd:#2a2a3e;'
        '--ac:#6b8cff;--up:#ff6b6b;--dn:#51cf66;--rk:#2a1515;--hdr:linear-gradient(135deg,#0a0a1a,#1a1a2e,#0f3460)}\n'
        
        # Base
        '*{margin:0;padding:0;box-sizing:border-box}\n'
        'body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;'
        'background:var(--bg);color:var(--tx);line-height:1.7;font-size:15px;transition:.2s}\n'
        
        # Header
        '.hd{background:var(--hdr);color:#fff;padding:24px 16px;text-align:center;position:relative}\n'
        '.hd h1{font-size:18px;font-weight:600}\n'
        '.hd .m{font-size:12px;opacity:.7;margin-top:3px}\n'
        '.tg{position:fixed;top:10px;right:10px;z-index:99;'
        'background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);'
        'color:#fff;padding:5px 12px;border-radius:16px;font-size:11px;cursor:pointer;backdrop-filter:blur(6px)}\n'
        '.tg:hover{background:rgba(255,255,255,.2)}\n'
        
        # Container
        '.c{max-width:860px;margin:0 auto;padding:8px}\n'
        
        # Data section
        '.ds{background:var(--cd);border-radius:10px;padding:10px 12px;margin-bottom:10px;'
        'box-shadow:0 1px 3px rgba(0,0,0,.05);border:1px solid var(--bd)}\n'
        '.sh{font-size:14px;font-weight:600;margin:12px 0 6px;padding-bottom:4px;'
        'border-bottom:1px solid var(--bd);color:var(--ac)}\n'
        
        # Tables - no nowrap, scrollable
        '.tw{overflow-x:auto;margin:6px 0;border-radius:6px;border:1px solid var(--bd)}\n'
        'table{width:100%;border-collapse:collapse;font-size:12px}\n'
        'th,td{padding:5px 7px;text-align:left;border-bottom:1px solid var(--bd);vertical-align:top}\n'
        'th{background:rgba(74,108,247,.04);color:var(--t2);font-weight:600;font-size:11px;position:sticky;top:0}\n'
        '.up{color:var(--up);font-weight:500}\n'
        '.down{color:var(--dn);font-weight:500}\n'
        
        # Step cards
        '.st{background:var(--cd);border-radius:10px;padding:12px 14px;margin-bottom:10px;'
        'box-shadow:0 1px 3px rgba(0,0,0,.05);border-left:4px solid var(--ac)}\n'
        '.stt{font-size:14px;font-weight:600;color:var(--ac);margin-bottom:8px;padding-bottom:4px;'
        'border-bottom:1px solid var(--bd)}\n'
        '.stb p{margin:4px 0;font-size:13px}\n'
        '.sp{height:6px}\n'
        '.bl{font-weight:600;padding:3px 0;font-size:13px}\n'
        '.li{padding:2px 0 2px 14px;position:relative;font-size:12px}\n'
        '.li::before{content:"\u25b8";position:absolute;left:2px;color:var(--ac)}\n'
        '.rc{background:var(--rk);border:1px solid rgba(231,76,60,.2);border-radius:6px;padding:8px 10px;margin:6px 0;font-size:12px}\n'
        
        # Fund operation table (Step 5)
        '.ft{width:100%;border-collapse:collapse;font-size:12px;margin:8px 0}\n'
        '.ft th{background:var(--ac);color:#fff;padding:6px 8px;text-align:left;font-size:11px}\n'
        '.ft td{padding:6px 8px;border-bottom:1px solid var(--bd);vertical-align:top;font-size:11px}\n'
        '.ft .ph{color:var(--up);font-weight:600}\n'
        '.ft .pm{color:#e67e22;font-weight:600}\n'
        '.ft .ab{color:var(--dn);font-weight:600}\n'
        '.ft .as{color:var(--up);font-weight:600}\n'
        '.ft .ah{color:#e67e22;font-weight:600}\n'
        
        # Mobile
        '@media(max-width:600px){'
        'body{font-size:14px}.c{padding:4px}'
        '.ds,.st{padding:8px 10px}'
        'th,td{padding:3px 5px;font-size:11px}'
        '.ft td{font-size:10px;padding:3px 5px}'
        '.ft th{font-size:10px;padding:3px 5px}'
        '.hd h1{font-size:16px}}\n'
        
        '</style>\n</head>\n<body>\n'
        '<div class="hd"><h1>' + et + '</h1>'
        '<div class="m">' + d + ' \U0001f916 AI生成 ' + now + '</div>'
        '<button class="tg" onclick="document.body.classList.toggle(\'dk\')">\U0001f313 主题</button></div>\n'
        '<div class="c">\n'
        '<div class="ds">' + data_html + '</div>\n'
        '<h3 style="font-size:15px;font-weight:600;margin:14px 0 8px;color:var(--ac)">\U0001f916 AI 深度分析</h3>\n'
        + ai_html + '\n'
        '<div style="text-align:center;margin:20px 0;font-size:11px;color:var(--t2)">\U0001f916 AI生成 \u00b7 不构成投资建议</div>\n'
        '</div>\n'
        '<script>\n'
        'if(window.matchMedia("(prefers-color-scheme:dark)").matches)document.body.classList.add("dk");\n'
        'document.querySelector(".tg").onclick=function(){document.body.classList.toggle("dk")};\n'
        '</script>\n'
        '</body>\n</html>'
    )

def _fmt(text: str) -> str:
    """Inline markdown formatting to HTML — 先替换再escape"""
    t = text
    # Bold ** → <strong> (do BEFORE escape so ** isn't escaped)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    # Escape remaining HTML entities
    t = escape(t)
    # Re-preserve our generated <strong> tags
    t = t.replace('&lt;strong&gt;', '<strong>').replace('&lt;/strong&gt;', '</strong>')
    # Color emoji markers
    t = t.replace('🔴', '<span class="up">🔴</span>')
    t = t.replace('🟢', '<span class="down">🟢</span>')
    t = t.replace('📈', '<span class="up">📈</span>')
    t = t.replace('📉', '<span class="down">📉</span>')
    return t

def _render_table(rows: list) -> str:
    """Render markdown table to HTML, skip separator rows"""
    data = []
    for r in rows:
        s = r.strip()
        # Skip separator rows like |:---|:---:|
        if all(c in '|:- ' for c in s):
            continue
        cells = [c.strip() for c in s.split('|')[1:-1]]
        if cells and not all(c in ':- ' for c in ''.join(cells)):
            data.append(cells)
    if len(data) < 2:
        return ""
    
    thead = '<thead><tr>' + ''.join(f'<th>{_fmt(c)}</th>' for c in data[0]) + '</tr></thead>'
    tbody = ""
    for row in data[1:]:
        tbody += '<tr>' + ''.join(f'<td>{_fmt(c)}</td>' for c in row) + '</tr>'
    
    return '<div class="tw">' + (table := '<table>' + thead + '<tbody>' + tbody + '</tbody></table>') + '</div>'

def _parse_steps(lines: list) -> list:
    """解析AI分析步骤"""
    steps = []
    current_title = ""
    current_body = []
    
    for l in lines:
        s = l.strip()
        if s.startswith('### ') or s.startswith('## '):
            if current_title:
                steps.append((current_title, '\n'.join(current_body)))
            current_title = s.replace('### ', '').replace('## ', '').replace('**', '')
            current_body = []
        elif s == '---' or s.startswith('---'):
            continue
        else:
            current_body.append(l)
    
    if current_title:
        steps.append((current_title, '\n'.join(current_body)))
    
    return steps

def _step_card(title_text: str, body: str) -> str:
    """步骤卡片渲染"""
    icon = "\U0001f4ca"
    if '\u6b65\u9aa41' in title_text or '\u9694\u591c' in title_text: icon = "\U0001f319"
    elif '\u6b65\u9aa42' in title_text or '\u590d\u76d8' in title_text: icon = "\U0001f441\ufe0f"
    elif '\u6b65\u9aa43' in title_text or '\u4f5c\u6218' in title_text: icon = "\U0001f5fa\ufe0f"
    elif '\u6b65\u9aa44' in title_text or '\u98ce\u9669' in title_text: icon = "\u26a0\ufe0f"
    elif '\u6b65\u9aa45' in title_text or '\u4f18\u5148\u7ea7' in title_text or '\u57fa\u91d1' in title_text: icon = "\U0001f3af"
    
    body_html = _render_step_body(body, title_text)
    return (
        '<div class="st">'
        '<div class="stt">' + icon + ' ' + escape(title_text) + '</div>'
        '<div class="stb">' + body_html + '</div>'
        '</div>'
    )

def _render_step_body(body: str, title: str) -> str:
    """步骤主体渲染 - 完整markdown解析"""
    lines = body.split('\n')
    
    html = ""
    i = 0
    while i < len(lines):
        l = lines[i]
        s = l.strip()
        
        if not s:
            html += '<div class="sp"></div>'
            i += 1
            continue
        
        # H4 headers (####)
        if s.startswith('#### '):
            html += '<h4 style="font-size:13px;font-weight:600;margin:10px 0 6px;color:var(--ac)">' + _fmt(s[5:]) + '</h4>'
            i += 1
            continue
        
        # H3 headers
        if s.startswith('### '):
            html += '<h3 style="font-size:14px;font-weight:600;margin:10px 0 6px">' + _fmt(s[4:]) + '</h3>'
            i += 1
            continue
        
        # Tables
        if s.startswith('|') and s.endswith('|'):
            # Check if this is a separator row
            if all(c in '|:- ' for c in s):
                i += 1
                continue
            tbl = []
            while i < len(lines):
                cl = lines[i].strip()
                if cl.startswith('|') and cl.endswith('|'):
                    # Skip separator rows
                    if not all(c in '|:- ' for c in cl):
                        tbl.append(lines[i])
                    i += 1
                else:
                    break
            if tbl:
                html += _render_table(tbl)
            continue
        
        # Horizontal rule
        if s.startswith('---') or s == '---':
            i += 1
            continue
        
        # Blockquote
        if s.startswith('> '):
            html += '<blockquote style="background:var(--rk);border-left:3px solid var(--ac);padding:6px 10px;margin:6px 0;border-radius:4px;font-size:12px">' + _fmt(s[2:]) + '</blockquote>'
            i += 1
            continue
        
        # Risk items
        if '\u26a0' in s or '\u6700\u6015' in s or ('\u98ce\u9669' in s and len(s) < 60):
            html += '<div class="rc"><p>' + _fmt(s) + '</p></div>'
            i += 1
            continue
        
        # List items
        if (s.startswith('- ') or s.startswith('* ')) and not s.startswith('**'):
            txt = s[2:]
            html += '<p class="li">' + _fmt(txt) + '</p>'
            i += 1
            continue
        
        # Numbered list items
        if s and s[0].isdigit() and '. ' in s[:4]:
            html += '<p class="li">' + _fmt(s) + '</p>'
            i += 1
            continue
        
        # Bold line (starts and ends with **)
        if s.startswith('**') and s.endswith('**'):
            html += '<p class="bl">' + _fmt(s.strip('*')) + '</p>'
            i += 1
            continue
        
        # Regular paragraph with formatting
        html += '<p>' + _fmt(s) + '</p>'
        i += 1
    
    return html

def _render_fund_table(lines: list) -> str:
    """基金操作建议表渲染（Step 5）"""
    data = []
    for l in lines:
        s = l.strip()
        if s.startswith('|') and s.endswith('|'):
            cells = [c.strip() for c in s.split('|')[1:-1]]
            if cells:
                data.append(cells)
    
    if len(data) < 2:
        return _render_table(lines)  # fallback
    
    # Find header row (not separator)
    header_idx = 0
    for i, row in enumerate(data):
        if not all(c in '|:- ' for c in ''.join(row)):
            header_idx = i
            break
    
    header = data[header_idx] if header_idx < len(data) else data[0]
    rows = [r for r in data[header_idx+1:] if not all(c in '|:- ' for c in ''.join(r))]
    
    thead = '<thead><tr>' + ''.join(f'<th>{_fmt(h)}</th>' for h in header) + '</tr></thead>'
    tbody = ""
    
    for row in rows:
        if len(row) < 5:
            continue
        pri = row[0].replace('**', '')
        name = row[1].replace('**', '')
        val = row[2].replace('**', '').replace('*', '') if len(row) > 2 else ''
        chg = row[3].replace('**', '') if len(row) > 3 else ''
        act = row[4].replace('**', '').replace('(', '').replace(')', '') if len(row) > 4 else ''
        reason = row[5].replace('**', '')[:60] if len(row) > 5 else ''
        
        pc = 'ph' if '\u6700\u9ad8' in pri else 'pm'
        ac = 'ab' if '\u52a0\u4ed3' in act or '\u4e70\u5165' in act else 'as' if '\u51cf\u4ed3' in act or '\u5356\u51fa' in act else 'ah'
        
        tbody += (
            '<tr>'
            '<td class="' + pc + '">' + _fmt(pri[:6]) + '</td>'
            '<td><strong>' + _fmt(name[:20]) + '</strong><br><span style="font-size:10px;color:var(--t2)">' + _fmt(chg) + '</span></td>'
            '<td>' + _fmt(val[:8]) + '</td>'
            '<td class="' + ac + '">' + _fmt(act[:12]) + '</td>'
            '<td style="font-size:10px">' + _fmt(reason) + '</td>'
            '</tr>'
        )
    
    return '<table class="ft">' + thead + '<tbody>' + tbody + '</tbody></table>'


if __name__ == "__main__":
    print("R2 report pusher loaded. Use push_report()")
