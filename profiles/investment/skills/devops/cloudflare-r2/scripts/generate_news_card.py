"""
Generate news briefing card image and upload to Cloudflare R2
Called by cron job with JSON data via stdin
Usage: echo '{"date":"2026-06-23","weekday":"星期二","news":[...]}' | python3 generate_news_card.py
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw, ImageFont
from r2_uploader import R2Uploader


def get_font(size):
    """Get a Chinese-supporting font, falling back to default."""
    font_paths = [
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/usr/share/fonts/truetype/arphic/uming.ttc',
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Light.ttc',
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def wrap_text(text, font, max_width):
    """Wrap text to fit within max_width pixels."""
    lines = []
    current = ""
    for ch in text:
        test = current + ch
        bbox = font.getbbox(test)
        if (bbox[2] - bbox[0]) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


def create_news_card(news_items, date_str, weekday, width=1200, height=2400):
    """Create a beautiful news card image from structured data."""
    img = Image.new('RGB', (width, height), color=(248, 244, 238))
    draw = ImageDraw.Draw(img)

    font_title = get_font(48)
    font_date = get_font(28)
    font_section = get_font(32)
    font_news = get_font(24)
    font_num = get_font(18)
    font_footer = get_font(18)

    # Top decorative bar
    draw.rectangle([0, 0, width, 10], fill=(180, 140, 80))

    # Header
    draw.text((60, 40), "📰 每日简报", font=font_title, fill=(80, 60, 30))
    draw.text((60, 100), f"{date_str} · {weekday}", font=font_date, fill=(120, 120, 120))

    # Separator
    y = 150
    draw.line([(60, y), (width - 60, y)], fill=(200, 180, 140), width=2)

    # Section definitions
    section_colors = [
        ('🔴 V2EX 热议', (200, 80, 80)),
        ('🟠 Hacker News', (220, 160, 60)),
        ('🟢 GitHub 热门', (80, 160, 80)),
        ('🔵 B站热门', (60, 120, 200)),
    ]

    y = 190
    for section_idx, (section_name, section_color) in enumerate(section_colors):
        if section_idx < len(news_items):
            items = news_items[section_idx]
            if items:
                # Section title
                draw.text((60, y), section_name, font=font_section, fill=section_color)
                y += 50

                # Items
                for i, item in enumerate(items):
                    # Number circle
                    cx, cy_pos = 90, y + 14
                    draw.ellipse([cx - 12, cy_pos - 12, cx + 12, cy_pos + 12], fill=(200, 170, 110))
                    draw.text((cx - 5, cy_pos - 8), str(i + 1), font=font_num, fill=(255, 255, 255))

                    # Item text with wrapping
                    tx = 120
                    max_w = width - tx - 60
                    for line in wrap_text(item, font_news, max_w):
                        draw.text((tx, y), line, font=font_news, fill=(50, 50, 50))
                        y += 32

                y += 20  # spacing between sections

    # Bottom separator
    y += 20
    draw.line([(60, y), (width - 60, y)], fill=(200, 180, 140), width=2)

    # Footer
    fy = height - 80
    draw.text((60, fy), f"自动生成于 {date_str}", font=font_footer, fill=(160, 160, 160))
    draw.text((width - 350, fy), "Powered by Hermes Agent", font=font_footer, fill=(160, 160, 160))

    return img


def main():
    # Read news data from stdin (JSON format)
    data = sys.stdin.read()
    news_data = eval(data)  # Simple eval for cron job context

    date_str = news_data.get('date', datetime.now().strftime('%Y-%m-%d'))
    weekday = news_data.get('weekday', '')
    news_items = news_data.get('news', [])

    # Generate image
    img = create_news_card(news_items, date_str, weekday)
    output_path = f"/tmp/news-card-{date_str}.png"
    img.save(output_path, 'PNG')
    print(f'✅ Image saved: {output_path} ({img.size})')

    # Upload to R2
    uploader = R2Uploader(
        account_id='a14f5ae92b9406c186b0f7f796fb7c50',
        bucket_name='hermes-main',
        access_key_id='e3498c2d01404128aa9199a887f568c7',
        secret_access_key='4855275a8e6b96fe31c2c19adea28f4eff60cd0cf17f36152ce798bbd5770742',
        public_url='https://hermes-main-media.devtoy.xyz'
    )

    key = f"daily-news/{date_str[:7]}/{date_str}_briefing.png"
    url = uploader.upload_file(output_path, key, 'image/png')
    print(f'✅ Uploaded: {url}')
    print(f'IMAGE_URL={url}')

    # Cleanup
    try:
        os.remove(output_path)
    except Exception:
        pass


if __name__ == '__main__':
    main()
