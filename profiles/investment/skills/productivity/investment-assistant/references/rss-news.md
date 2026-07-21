# RSS 赛道新闻系统 (2026-07-06)

## 数据源

30 个公开 RSS 源，分 4 个投资赛道，配置在 `/opt/data/scripts/news_sources.json`。

| 赛道 | 源数 | 关键词 | 对应持仓组 |
|------|:----:|--------|-----------|
| AI / 半导体/芯片 | 11 | OpenAI, Google AI, 量子位, 机器之心, TechCrunch, The Verge, EETimes, 36氪AI, Anthropic, SemiInsights, HuggingFace | 科技/AI |
| 能源 / 新能源 | 6 | PV Magazine, Reuters Energy, Bloomberg NEF, 光伏头条, 北极星储能, OFweek | 新能源 |
| 财经 / 宏观 | 6 | 华尔街见闻, 财新网, FT中文网, Reuters, Bloomberg, WSJ | 通用 |
| 黄金 / 贵金属 | 5 | Kitco, Gold.org, Mining.com, Reuters Commodities, 黄金网 | 黄金 |

## 采集函数

```python
from fund_tools import fetch_rss_news, format_rss_news

news = fetch_rss_news(max_per_source=3, timeout=10)
# 返回: {"AI / 半导体/芯片": [("title", "url", "source"), ...], ...}

text = format_rss_news(news)
# 返回: markdown 格式的字符串
```

## 集成点

- `collect_morning_data.py` 第 8.5 节：RSS 采集输出到 `/tmp/fund_data/_rss_news.txt`
- 早报 prompt 的 step 2 需要 `cat /tmp/fund_data/_rss_news.txt` 才能让 LLM 读到

## 实现细节

- 纯 stdlib (`urllib.request` + `xml.etree.ElementTree`)，零第三方依赖
- 8 个并发 workers，每源超时 10 秒
- 支持 RSS 2.0 和 Atom 两种格式
- 自动去重
- 每赛道最多 5 条

## 英文标题自动翻译（2026-07-14 新增）

### 问题

RSS 源包含大量英文媒体（OpenAI, Google AI, TechCrunch, The Verge, Reuters, Bloomberg, WSJ, Kitco, PV Magazine 等），标题为英文，中文读者阅读不便。

### 方案

利用 Google Translate 免费 API（无需 API Key），在 `format_rss_news()` 中自动检测并翻译英文标题。

### 关键函数

```python
from fund_tools import translate_text

def translate_text(text: str, target: str = "zh-CN") -> str:
    """调用 Google 免费翻译 API 将文本翻译为中文。带内存缓存。"""
    # 使用 https://translate.googleapis.com/translate_a/single
    # 参数: client=gtx, sl=auto, tl=zh-CN, dt=t, q=text
    # 返回: response.json()[0][0][0] 为译文
```

### 语言检测

```python
def is_mostly_english(text: str) -> bool:
    """判断文本是否以英文字符为主（>50% 英文字母）"""
    # 只翻译英文字母占比 > 40% 的标题
    # 纯中文标题（如华尔街见闻、财新网）保持原样
```

### 缓存策略

- 内存字典 `_TRANSLATE_CACHE`，key 为 text[:200]
- 同一个标题在单次运行中只请求一次
- 不持久化到磁盘（每日新闻标题不同，无意义）

### 集成点

- `fund_tools.py::format_rss_news()` — 调用 `is_mostly_english()` 过滤，英文标题过 `translate_text()` 再输出
- 输出文件 `/tmp/fund_data/_rss_news.txt` 格式不变（markdown），只标题从英文变为中文
