# 基金持仓数据获取（免费，无需token）

天天基金 `fundf10` 子域名提供基金持仓TOP10数据，免费、无token。

⚠️ **限流实测**：连续请求会被限流（本会话实测曾连续224秒全部失败，返回空或限流页）。逐支间隔5秒+重试可缓解但仍不稳定。东财限流时前十大个股持仓无法获取，改用 `ak.fund_portfolio_industry_allocation_em`（行业配置）做近似重叠分析。完整应对方案与可用替代API见 `references/data-source-resilience.md`。

## API 地址

```
https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={基金代码}&topline=10&year=&month=
```

返回：`var apidata={ content:"<HTML表格>" }` 的JavaScript包裹格式。

## 使用方法（Python）

```python
import re, json
from urllib.request import urlopen

code = "011613"
url = f"https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}&topline=10"
resp = urlopen(url)
data = resp.read().decode('utf-8')
m = re.search(r'content:"(.*?)",', data, re.DOTALL)
if m:
    html = m.group(1).replace('\\r','').replace('\\n','\n')
    # 然后用 HTMLParser 解析 table 获取持仓
```

## 表格列顺序

| 序号 | 股票代码 | 股票名称 | 最新价 | 涨跌幅 | 占净值比例(%) | 持股数(股) |

注意：对于主动管理基金（非ETF联接），第6列可能显示为"市值(元)"而非百分比。

## 适用场景

- 基金持仓重叠分析（多支基金是否持有同一股票）
- 判断基金经理是否风格漂移
- 行业集中度评估
- 季度调仓跟踪
