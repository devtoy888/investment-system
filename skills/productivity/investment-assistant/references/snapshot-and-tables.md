# 收盘快照 & 脚本生成表格架构

## 数据流

```
收盘复盘 (16:00 CST, closing_review.py)
  │
  ├─ 实时采集收盘数据 (quotes, sectors, overview, northbound, funds)
  │
  ├─ 步骤10: 生成 _closing_tables.md (81行, 全部表格预格式化)
  │   → LLM 原样输出 + 添加推演
  │
  └─ 步骤11: 保存 _yesterday_snapshot.json (收盘快照)
       → collect_morning_data.py 优先读取 (次日08:30)
       → 无快照时回退实时API (首次部署/新环境)
```

## 快照字段

_yesterday_snapshot.json:
```json
{
  "date": "2026-07-01",
  "quotes": { /* 6指数: price/open/prev_close/change_pct */ },
  "sectors": { /* 10ETF: price/open/prev_close/change_pct */ },
  "market_overview": { /* 涨跌家数+两市成交 */ },
  "northbound": { /* 沪/深/合计/time */ },
  "funds": { /* 17支基金: nav/estimated_nav/estimated_change */ },
  "fund_groups": { /* 分组: 黄金/科技AI/资源周期/新能源/通航 */ }
}
```

## 各推送表格格式

| 数据 | 财经早餐 | 收盘复盘 |
|:----|:--------|:--------|
| 隔夜外盘/外盘 | 3列(指数/收盘/涨跌) | (收盘无外盘) |
| A股行情 | 3列(指数/点位/涨跌) | 6列(指数/昨收/今开/收盘/涨跌/开方向) |
| 行业板块 | 3列(板块/今开→收盘/涨跌) | 3列(板块/今开→收盘/涨跌) |
| 两市成交+北向 | 行内: 成交X亿 \| 北向X亿 | 行内: 成交X亿；行内: 北向X亿 |
| 持仓基金 | **3列**(基金/前日净值/昨日涨跌) | **4列**(基金/昨收净值/估算净值/涨跌) |
| 早盘预测验证 | (早报无验证) | 4列(指数/开方向预测/收盘实际/验证) |
| 推演 | AI添加 | AI添加 |

**关键差异：** 早报只做参考展示，去掉"估算净值"列；收盘复盘需展示估算细节。

## 实现位置

| 功能 | 文件 | 行号参考 |
|:----|:----|:--------|
| 收盘表格生成 (十) | `/opt/data/scripts/closing_review.py` | ~225-350 |
| 收盘快照保存 (十一) | `/opt/data/scripts/closing_review.py` | ~352-365 |
| 早报快照读取 (二) | `/opt/data/scripts/collect_morning_data.py` | ~32-42 |
| 早报表格生成 (八) | `/opt/data/scripts/collect_morning_data.py` | ~195-270 |

## 盘中速递待跟进

三个推送中收盘复盘和财经早餐已使用脚本生成表格模式，盘中速递 (collect_noon_data.py) 仍由LLM排版。下次用户报告盘中速递格式问题时，应用同样方案。
