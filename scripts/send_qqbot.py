"""
QQ Bot Markdown 输出模块 — 替代飞书卡片推送。
所有函数直接 print Markdown 到 stdout，由 cron 的 deliver=qqbot 自动投递。
"""
import sys

# 每条消息最大字符数（防止QQ截断）
MAX_MSG_LEN = 4000
_need_separator = False


def _sep():
    """打印段落分隔线"""
    global _need_separator
    if _need_separator:
        print("\n═══════════════════════════════════\n")
    _need_separator = True


def send_card(title, content, template=None):
    """发送纯 Markdown 段落"""
    _sep()
    rendered = f"## {title}\n\n{content}"
    _output(rendered)
    return True


def send_card_with_tables(title, content, template=None):
    """发送带表格的 Markdown 段落（直接输出原始Markdown表格，不转飞书table组件）"""
    _sep()
    rendered = f"## {title}\n\n{content}"
    _output(rendered)
    return True


def send_card_with_button(title, content, button_text, button_url, template=None):
    """发送带链接的 Markdown（QQ不支持按钮，改为文字链接）"""
    _sep()
    rendered = f"## {title}\n\n{content}\n\n🔗 [{button_text}]({button_url})"
    _output(rendered)
    return True


def send_structured_card(title, sections, template=None):
    """发送结构化卡片（sections: list of dict with type='markdown'|'divider'|'note'）"""
    _sep()
    parts = [f"## {title}"]
    for sec in sections:
        t = sec.get('type', '')
        c = sec.get('content', '')
        if t in ('markdown', 'note'):
            parts.append(c)
        elif t == 'divider':
            parts.append('---')
    rendered = "\n\n".join(parts)
    _output(rendered)
    return True


def _output(text):
    """带截断保护的输出"""
    if len(text) > MAX_MSG_LEN:
        # 尝试在段落边界截断
        cut = text[:MAX_MSG_LEN]
        last_para = cut.rfind("\n\n")
        if last_para > MAX_MSG_LEN // 2:
            text = text[:last_para] + "\n\n...（内容过长已截断）"
        else:
            text = cut + "\n\n...（内容过长已截断）"
    print(text)
