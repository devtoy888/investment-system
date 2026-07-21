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
