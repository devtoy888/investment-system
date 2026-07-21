# 数据源弹性获取（限流应对）

东财（`fundf10` / `fund_portfolio_hold_em`）在连续请求时会被限流（实测曾连续224秒全部失败）。
以下为实测可用的替代方案，按优先级排列。所有方案均已在容器内 `docker exec hermes-main` 验证。

## 1. 指数历史K线 → 腾讯API（稳定，首选）
```
https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=CODE,day,START,END,250,qfq
```
- 返回 JSON：`data.CODE.day = [[日期, 开, 收, 高, 低, 量], ...]`
- **收盘价在第3列 `x[2]`**（不是第1列）
- 实测：循环逐支拉取 + 每支间隔 2~3 秒，6 个指数全部成功（119 个交易日/指数）
- 指数 CODE 映射：
  - `sh000688` 科创50 | `sz399967` 中证半导体 | `sz399989` 中证医疗
  - `sz399997` 中证白酒 | `sz399932` 中证消费 | `sh000300` 沪深300
- 解析技巧：递归遍历 `data` 找含 `'day'` 键的 dict，避免硬编码层级

## 2. 基金净值历史 → AKShare（稳定）
```python
import akshare as ak
df = ak.fund_open_fund_info_em(symbol=CODE, indicator='单位净值走势')
# 过滤 date >= cutoff，输出写文件再读，避免 print(json) 被截断
```
- 逐支拉取 + 间隔 4 秒防限流
- 日期列可能是 `datetime.date` 或 `str`，比较前统一类型

## 3. 基金行业配置 → AKShare（东财限流时可用）
```python
ak.fund_portfolio_industry_allocation_em(symbol=CODE, date='2026')
```
- 即使 `fund_portfolio_hold_em` 报 `Can not decode value starting with character ';'`
  也能正常返回（行业类别 / 占净值比例 / 市值 / 截止时间）
- 用于基金间行业重叠的近似分析（替代无法获取的前十大个股持仓）

## 4. 基金前十大个股持仓 → 易限流（无可靠免费替代）
- `fundf10` API 与 `ak.fund_portfolio_hold_em` 均连东财，限流时无法获取
- 腾讯无公开基金持仓接口（试过 `web.ifzq.gtimg.cn/fund/fund/jjcc/` 返回 dispatch 错误）
- 应对：用方法 3 的行业配置做近似重叠判断

## 5. 基金实时估值 → 腾讯 `qt.gtimg.cn`（偶发限流）
```
http://qt.gtimg.cn/q=f_CODE  →  v_f_CODE="代码~名称~净值~...~涨跌"
```
- 第 5 列净值、第 7 列涨跌（`~` 分隔）
- 限流时返回 `v_pv_none_match="1"`，需重试或放弃

## 用户分析铁律（来自会话要求）
- 必须实时拉取真实 API 数据，**禁止占位/虚构**（如报告中写"数据待补"会被打回）
- 评估需数据 + 理论（如马科维茨均值-方差）双重支撑
- 时间跨度 **≥ 6 个月**，不用短期快照下结论
- 报告要详尽完整，覆盖结构/轮动/重叠/对比/路径/风险各维度
