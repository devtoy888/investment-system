# 数据源修复记录 (2026-07-18~19)

## 已完成修复

| # | 修复 | 文件 | 验证 |
|:-:|:-----|:-----|:----:|
| 1 | **AKShare硬编码日期** — `"2026-07-15-估算数据-估算增长率"` → 动态列名匹配 | `fund_source_akshare.py` | ✅ |
| 2 | **涨跌家数双域名** — push2 → push2delay.eastmoney.com (同一IP,不同vhost) | `fund_tools.py` | ✅ 交叉验证(502→200) |
| 3 | **北向AKShare备援** — hexin→新浪tags间插入AKShare路径 | `fund_tools.py` | ✅ |
| 4 | **Yahoo _stale标记** — 用regularMarketTime动态判断(零日历) | `fund_tools.py` | ✅ 7/7标的 |
| 5 | **新浪tags多正则** — 1种→4种模式覆盖不同文本格式 | `fund_tools.py` | ✅ |
| 6 | **`_tag_freshness`统一标记** — 所有数据返回添加新鲜度字段 | `fund_tools.py` | ✅ 边界测试24/24 |
| 7 | **`track_source`全覆盖** — 新增3个数据源追踪 | `fund_tools.py` | ✅ |
| 8 | **微博长文本API** — isLongText判断+长文本拉取+text[:2000] | `fund_tools.py` | ✅ 最长1218字完整(原被截到171字) |
| 9 | **KOL分析框架v2** — 4层(Extractor/Verifier/Mapper/format_push) | `kol_analysis.py` | ✅ 35/35 |
| 10 | **Feishu卡片→QQ Bot** — 删feishu-deps引用+3个wrapper重写 | send_morning/noon/closing + wrappers | ✅ 27/27 |
| 11 | **cron deliver local→origin** — 3个主推送直接走QQ Bot | cron jobs | ✅ |
| 12 | **交易日自动验证** — 3轮(09:35/13:00/15:30) | `trading_day_validate.py` | ✅ |

## 验证总结果

| 轮次 | 通过 | 日期 |
|:----:|:----:|:----:|
| 第1轮: 语法+引用 | 21/21 | 07-18 |
| 第2轮: 功能测试 | 15/15 | 07-18 |
| 第3轮: 残留清理 | 27/27 | 07-18 |
| 最终: 全量 | 35/35 | 07-19 |

## 旧文件删除清单

- `send_morning_cards.py` → 覆盖为`send_morning.py`
- `send_noon_cards.py` → 覆盖为`send_noon.py`
- `send_closing_cards.py` → 重命名为`send_closing.py`
- `send_morning.py` (旧版飞书HTTP路径) → 已删除

## 多轮验证脚本

- `/opt/data/scripts/trading_day_validate.py` — 交易日自动验证(no_agent=true)
- `/opt/data/scripts/verify_rename.py` — 重命名验证
