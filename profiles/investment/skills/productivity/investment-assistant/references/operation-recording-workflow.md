# 操作记录工作流

> 用户要求：每次买入/卖出/调仓操作后，必须生成记录文档并存档R2，便于历史分析。

## 触发条件

用户执行任何基金买卖操作后（手动告知成交信息后），必须执行以下记录流程。

## 流程步骤

### 步骤1：获取成交净值

- 003096(中欧医疗C) — A股基金，T+1确认，15:00前买入按当日收盘净值
- 013403(华夏恒生科技C) — QDII基金，T+2确认，净值以港股/美股收盘价折算
- 其他A股基金：用 `get_fund_value(code)` 获取7/15最新净值+当日估算涨跌
- 标注"待确认"状态并注明预计确认日期

### 步骤2：生成操作记录MD

保存路径: `/opt/data/fund_system_data/operations/operation_YYYY-MM-DD.md`

模板结构:
```markdown
# 操作记录 · YYYY-MM-DD

> 操作类型: 建仓/加仓/减仓/清仓/调仓 | 方向: 买入/卖出

## 操作明细

| 时间 | 基金 | 代码 | 金额 | 买入/卖出净值 | 估算涨跌 | 预计份额 | 说明 |
|:---|:----|:---:|:----:|:-----------:|:-------:|:--------:|:----|

## 操作理由

每支基金一个表格，含：
- 择时理由（板块表现、技术面数据）
- 分批说明（首批占比、剩余批次安排）
- 逻辑支撑（主任微博引用、指数数据）
- 策略框架（主任哲学引用）
```

### 步骤3：生成自适应HTML

- 复制 `operation_YYYY-MM-DD.html` (与MD同目录)
- HTML使用marked.js渲染同名MD文件
- 深色主题、移动端自适应

### 步骤4：更新操作索引README

路径: `/opt/data/fund_system_data/operations/README.md`

格式:
```markdown
| 日期 | 操作 | 基金 | 代码 | 金额 | 详情 |
|:---|:----|:----|:---:|:----:|:----|
| MM-DD | 买入 | 基金名 | 代码 | 金额 | [查看详情](operation_YYYY-MM-DD.html) |
```

### 步骤5：更新持仓文档

- 读取当前 `portfolio-YYYY-MM-DD.md`
- 在对应分组下新增该基金行（含成本、待确认状态）
- 更新总成本合计
- 生成对应HTML

### 步骤6：全部上传R2

```python
upload_to_r2(f'/opt/data/fund_system_data/operations/operation_YYYY-MM-DD.md',
             'fund-system/operations/operation_YYYY-MM-DD.md',
             'text/markdown; charset=utf-8')
upload_to_r2(..., 'text/html; charset=utf-8')  # HTML同样上传
# 持仓也一样
```

路径约定:
| 文件 | R2路径 |
|:----|:-------|
| 操作记录MD | `fund-system/operations/operation_YYYY-MM-DD.md` |
| 操作记录HTML | `fund-system/operations/operation_YYYY-MM-DD.html` |
| 操作索引 | `fund-system/operations/README.md` |
| 持仓MD | `fund-system/data/portfolio/portfolio-YYYY-MM-DD.md` |
| 持仓HTML | `fund-system/data/portfolio/portfolio-YYYY-MM-DD.html` |

## 用户纠正记录

- 2026-07-16: 022398被误作恒生科技基金，实为债基。正确恒生科技C类代码为013403。
