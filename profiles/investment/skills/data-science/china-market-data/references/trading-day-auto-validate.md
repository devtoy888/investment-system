# 交易日自动验证（2026-07-18）

## 3轮验证时间线

| 轮次 | 时间 | 触发 | 验证内容 |
|:----:|:----:|:-----|:---------|
| 第1轮 | 交易日 09:35 | cronjob | 各源是否正常开盘、_stale标记是否=False |
| 第2轮 | 交易日 13:00 | cronjob | 交叉验证(腾讯vsAKShare偏差<0.5%)、涨跌三源对比 |
| 第3轮 | 交易日 15:30 | cronjob | 收盘数据准确性(涨跌家数>100)、归档完整性 |

## 脚本

`/opt/data/scripts/trading_day_validate.py` (no_agent模式)

脚本自动行为:
- **交易日** → 完整数值验证（涨跌家数>100、交叉验证偏差<0.5%、净值偏差<0.01）
- **非交易日** → 仅API可达性测试（不报错）
- 自检测`is_trading_day()`，无需配置

## 部署命令

```python
cronjob(action='create', name='🔬 第1轮验证-开盘(09:35)',
    schedule='35 9 * * 1-5', no_agent=True, script='trading_day_validate.py')
cronjob(action='create', name='🔬 第2轮验证-盘中(13:00)',
    schedule='0 13 * * 1-5', no_agent=True, script='trading_day_validate.py')
cronjob(action='create', name='🔬 第3轮验证-收盘(15:30)',
    schedule='30 15 * * 1-5', no_agent=True, script='trading_day_validate.py')
```

## 验证项清单

### 第1轮(09:35)
- `is_trading_day()` 返回True
- `get_tencent_quote('sh000001')` → _stale=False
- `get_fund_value('017103')` → nav_date=今日
- `get_market_overview()` → rise+fall > 100
- `get_sector_quotes()` → 50%以上板块有数据
- `get_overnight_quotes()` → _stale字段类型正确

### 第2轮(13:00)
- 腾讯vsAKShare上证涨跌偏差<0.5%
- 天天基金vsAKShare同日期净值偏差<0.01
- 涨跌家数AKShare vs 东财偏差<500
- track_source今日有记录

### 第3轮(15:30)
- 同第1轮，收盘数据应更稳定
- 归档文件存在和有内容
