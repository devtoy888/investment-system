#!/usr/bin/env python3
"""Generate daily tech news card image with robust font handling.

FALLBACK SCRIPT — used when generate_news_card_v3.py is not available.
Takes data from inline variables; does NOT accept CLI args.
For CLI-based generation, use generate_news_card_v3.py instead.

Usage:
  uv run python3 generate_news_card_fallback.py
  
Outputs: /opt/data/daily-card.png (copy to /tmp/daily-card.png for MEDIA: delivery)

Font fallback chain:
  1. WenQuanYi Zen Hei (TTC index 0) — best CJK support
  2. Douyin Sans Bold (TTF) — preferred but may not exist
  3. DejaVu Sans Bold — ASCII only, no CJK

Known issues:
  - Pillow's textsize() is deprecated in Pillow 14; use font.getbbox() instead
  - TTC files need explicit index=0 parameter
  - /tmp is cleared on container restart; always save to persistent path
"""
from PIL import Image, ImageDraw, ImageFont
import os

W = 1080
MARGIN = 36
BG = "#0f0f23"
ACCENT = "#e94560"
WHITE = "#eaeaea"
DIM = "#8888aa"
HN_COLOR = "#ff6b6b"
GH_COLOR = "#58a6ff"
BILI_COLOR = "#00d4ff"
SUMMARY_COLOR = "#ffd700"

today = "2026-07-16"


def get_font(size):
    """Load font with CJK support, trying multiple paths and TTC indices."""
    ttc_path = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
    if os.path.exists(ttc_path):
        try:
            return ImageFont.truetype(ttc_path, size, index=0)
        except Exception:
            pass
        try:
            return ImageFont.truetype(ttc_path, size, index=1)
        except Exception:
            pass

    dy_path = "/opt/data/scripts/DouyinSansBold.ttf"
    if os.path.exists(dy_path):
        try:
            return ImageFont.truetype(dy_path, size)
        except Exception:
            pass

    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except Exception:
        return ImageFont.load_default()


font_t = lambda: get_font(36)
font_h = lambda: get_font(28)
font_b = lambda: get_font(22)
font_d = lambda: get_font(18)
font_s = lambda: get_font(15)

v2ex = [
    ("0.03 一刀 codex ，支持最新 5.6，评论送 10 刀", "196条回复"),
    ("谈一谈中医能不能治病", "126条回复"),
    ("有没有便宜点的宽带，一个月 139 真的受不了了", "119条回复"),
    ("就这，房东要告我破坏他的房子", "118条回复"),
    ("兄弟们 我好像毁了的我人生？（笑）", "113条回复"),
    ("推广一下自建最开始和朋友自用现在几十用户的一个小中转", "85条回复"),
    ("最近搬家，把客厅搞成了电竞房分享一下", "80条回复"),
    ("专升本前端毕业 1 年，从初创到大厂，我的开源项目上了 github trending", "77条回复"),
    ("有老哥买过亚朵星球深睡枕吗", "70条回复"),
]

hn = [
    ("Inkling: Our Open-Weights Model", "↑656分 · 165评论"),
    ("Stripe and Advent have made a joint offer to acquire PayPal", "↑334分 · 205评论"),
    ("Grok Build is open source", "↑243分 · 290评论"),
    ("Running Gemma 4 26B at 5 tokens/sec on a 13-year-old Xeon", "↑227分 · 150评论"),
    ("Governments should invest in free, open source AI", "↑76分 · 28评论"),
    ("SQLite should have (Rust-style) editions", "↑101分 · 38评论"),
]

gh = [
    ("xai-org/grok-build ⭐3098", "Rust · Coding agent harness and TUI"),
    ("MDX-Tom/gpt-5.6-instruct ⭐1342", "Python · Codex CLI 破甲提示词"),
    ("littledivy/mimic ⭐1021", "Python · Intercept any app, call from Python"),
    ("mereyabdenbekuly/clodex-ide ⭐810", "TypeScript · Zero-trust agentic IDE"),
    ("AlephAITech/WorkBuddyGuide ⭐804", "Python · 开源 WorkBuddy 实战蓝"),
]

bili = [
    ("孩子总把网络烂梗挂嘴边怎么办？", "978万播放"),
    ("郝 哥 连 线 勇 哥", "463万播放"),
    ("cheems小电影", "555万播放"),
    ("《崩坏：星穹铁道》姬子•启行角色PV", "393万播放"),
    ("哭着剪完这条视频…", "350万播放"),
]

summary = [
    "🤖 AI圈：xAI开源Grok Build编码代理框架（⭐3098），Codex CLI迎来gpt-5.6破甲测试包（⭐1342）。",
    "💰 金融圈：Stripe联合Advent对PayPal发起联合收购要约，获HN 334分热评。",
    "🔧 开源圈：SQLite Rust风格版本提案引发讨论，Mimic工具可拦截任意应用从Python调用。",
    "💬 V2EX热点：社区关注点多元——AI工具推广、中医讨论、宽带资费、职场话题各占热度。",
]

LINE_H = 30
META_H = 24
ITEM_GAP = 6
HEADER_H = 40
TITLE_H = 60
SEP_H = 4
SUMMARY_LINE_H = 36
FOOTER_H = 50

total_h = TITLE_H + SEP_H + MARGIN
for section_items in [v2ex, hn, gh, bili]:
    total_h += HEADER_H + SEP_H
    for item in section_items:
        total_h += LINE_H + META_H + ITEM_GAP
    total_h -= ITEM_GAP
    total_h += SEP_H
total_h += HEADER_H + SEP_H + (len(summary) * SUMMARY_LINE_H) + FOOTER_H + MARGIN
total_h = max(total_h, 1800)

img = Image.new("RGB", (W, total_h), BG)
draw = ImageDraw.Draw(img)

y = MARGIN
draw.text((MARGIN, y), f"📊 行业技术日报 · {today}", fill=ACCENT, font=font_t())
y += 55
draw.line([(MARGIN, y), (W - MARGIN, y)], fill=ACCENT, width=2)
y += 20


def draw_section(draw, title, color, items, y):
    draw.text((MARGIN, y), title, fill=color, font=font_h())
    y += HEADER_H
    for title_text, meta in items:
        draw.text((MARGIN + 12, y), f"▸ {title_text}", fill=WHITE, font=font_b())
        y += LINE_H
        if meta:
            draw.text((MARGIN + 32, y), meta, fill=DIM, font=font_d())
            y += META_H
        y += ITEM_GAP
    y += SEP_H
    return y


y = draw_section(draw, "━━━ V2EX 热搜 ━━━", ACCENT, v2ex, y)
y = draw_section(draw, "━━━ Hacker News 热门 ━━━", HN_COLOR, hn, y)
y = draw_section(draw, "━━━ GitHub Trending ━━━", GH_COLOR, gh, y)
y = draw_section(draw, "━━━ B站热门 ━━━", BILI_COLOR, bili, y)

draw.text((MARGIN, y), "━━━ 今日摘要 ━━━", fill=SUMMARY_COLOR, font=font_h())
y += HEADER_H
for line in summary:
    draw.text((MARGIN + 12, y), line, fill=WHITE, font=font_b())
    y += SUMMARY_LINE_H

y += 10
draw.text((MARGIN, y), "数据来源: V2EX · Hacker News · GitHub · Bilibili | 自动生成", fill=DIM, font=font_s())

out = "/opt/data/daily-card.png"
img.save(out, "PNG")
print(f"Image saved: {out} ({img.size[0]}x{img.size[1]})")
