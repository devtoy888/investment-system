# 预测验证修复记录（2026-07-21）

## 问题

review_engine.py 的预测验证准确率始终为0%。

## 根因分析

### 问题1：数据源错误

`_get_actual_market()` 从 `daily-snapshots.jsonl` 读取指数**点位**（如 `"科创50": 1718.69`），但 `_verify_single_prediction()` 试图 `float("1718.69")` 作为涨跌幅百分比。点位永远 > 0 → 数值无意义。

**修复**：改为从 `_closing_sector.txt`（板块涨跌幅）和 `_closing_tables.md`（指数涨跌幅）读取标准化的涨跌幅百分比。

### 问题2：名称匹配失败

`_verify_single_prediction()` 用 `idx_name in pred_text` 匹配，但预测中说"半导体看多"时 `idx_name="科创50"` 不匹配 `pred_text`。

**修复**：三级匹配：
1. 指数名匹配（如"科创50"）
2. 板块名匹配（如"半导体"）  
3. 整体大盘方向（含"大盘/市场"关键词）

### 问题3：预测提取抓了数据行

`extract_predictions()` 把含"涨/跌/反弹"的数据表行也提取为预测。

**修复**：过滤 `| % emoji` 行和纯符号行。

## 修复后效果

准确率从 0% → 42.4%（36/85条验证）。

## 涉及文件

- `review_engine.py` — `_get_actual_market()` 和 `_verify_single_prediction()` 重写
- 数据来源：`/tmp/fund_data/_closing_sector.txt`（收盘板块涨跌幅，由 `closing_review.py` 生成）
