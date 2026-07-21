# 已验证API端点汇总

## 腾讯财经实时行情

**URL:** `https://qt.gtimg.cn/q={code}`

**返回格式:** `v_{code}="…~…~…";` 用 `~` 分隔的字段列表

**关键字段索引:**
| 索引 | 含义 | 类型 |
|------|------|------|
| 1 | 股票名称 | str |
| 2 | 代码（纯数字，无sh/sz前缀） | str |
| 3 | 当前价 | str |
| 4 | 昨收 | str |
| 5 | 开盘价 | str |
| 6 | 成交量 | str |
| 7 | 成交额(元，ETF有效，指数为0) | str |
| 31 | 涨跌额 | str |
| 32 | 涨跌幅% | str |
| 33 | 最高价 | str |
| 34 | 最低价 | str |
| 35 | 指数独占：`price/volume/turnover`（三段式，第三段=成交额元） | str |
| 37 | 换手率% | str |
| 39 | 动态市盈率 | str |
| 44 | 流通市值 | str |
| 45 | 总市值 | str |
| 46 | 市净率 | str |

**代码前缀规则:** 6/9开头→`sh`，8开头→`bj`，其他(0/3开头)→`sz`

**指数成交额提取（field[35]技巧）：** 腾讯对指数的field[35]格式为 `price/volume/turnover`，第三段是成交额(元)。上证A股用 `sh000002`（A股指数），深证用 `sz399001`（深证成指）。非交易时段返回0。

**已验证可用的代码:**
- `sh000001` 上证指数
- `sh000002` A股指数（上证总成交额用）
- `sz399001` 深证成指（深证总成交额用）
- `sz399006` 创业板指
- `sh000688` 科创50
- `sh000300` 沪深300
- `sh000016` 上证50
- `sz159934` 黄金ETF(易方达) 
- `sh518880` 黄金ETF(华安)

---

## 天天基金净值/实时估值

**URL:** `https://fundgz.1234567.com.cn/js/{fund_code}.js`

**Referer:** `https://fund.eastmoney.com/`

**返回格式:** `jsonpgz({"fundcode":"...","name":"...","jzrq":"2026-06-25","dwjz":"2.7842","gsz":"2.7965","gszzl":"0.44",...});`

**关键字段:**
- `dwjz` — 昨日净值
- `gsz` — 实时估算净值
- `gszzl` — 估算涨幅%
- `jzrq` — 净值日期

---

## 东财市场总览（涨跌家数）

**URL:** `https://push2.eastmoney.com/api/qt/stock/get?secid=1.000001&fields=f57,f58,f169,f170,f171`

**请求头:** 必须加 `Referer: https://quote.eastmoney.com/` + User-Agent

**返回字段:**
- `f169` — 上涨家数（上证主板）
- `f170` — 下跌家数
- `f171` — 平盘家数

**注意事项：**
- 只返回上证主板（约900+支），非全市场
- Oracle ARM海外IP可能SSL握手超时(~8s)，需设timeout=8
- 同花顺也有涨跌家数API？已验证的只有东财push2这一条

---

## 同花顺北向资金

**URL:** `https://data.hexin.cn/market/hsgtApi/method/dayChart/`

**请求头:** 必须加 `Host: data.hexin.cn` + `Referer: https://data.hexin.cn/` + User-Agent

**返回格式:** JSON `{"time":["09:10",...,"15:00"],"hgt":[0,...,-9.28],"sgt":[0,...,-31.1]}`

**字段:**
- `time` — 262个时间点（09:10-15:00，分钟级）
- `hgt` — 沪股通累计净买入（亿元）
- `sgt` — 深股通累计净买入（亿元）

**注意事项:**
- 从09:10到15:00共262个点，09:10一般为0
- 取最后一个非None有效值作为当日最新值
- 非交易时段返回前一日最后一个有效时间点的数据
- Oracle ARM海外IP可用，不封IP

---

## Yahoo Finance 外盘

**URL:** `https://query1.finance.yahoo.com/v8/finance/chart/{url_encoded_symbol}`

**已验证Symbol:**
| 品种 | Symbol | URL编码 |
|------|--------|---------|
| 道琼斯 | `^DJI` | `%5EDJI` |
| 标普500 | `^GSPC` | `%5EGSPC` |
| 纳斯达克 | `^IXIC` | `%5EIXIC` |
| 黄金期货 | `GC=F` | `GC%3DF` |
| 美元指数 | `DX-Y.NYB` | `DX-Y.NYB` |
| 恒生指数 | `^HSI` | `%5EHSI` |
| 恒生国企 | `^HSCE` | `%5EHSCE` |

**注意:** `^HSTECH`（恒生科技）返回Not Found，不能用Yahoo获取。可用腾讯ETF `sz159740`（恒生科技ETF大成）替代。

---

## mootdx 通达信TCP

**TCP端口:** 7709

**已验证可用服务器 (2026-06测试):**
- 119.97.185.59:7709
- 124.70.133.119:7709
- 116.205.183.150:7709
- 123.60.73.44:7709
- 121.36.225.169:7709

**bars() 参数:**
- `frequency`: 9=日线, 5=周线, 6=月线
- 注意：指数代码需传6位数字(不带前缀)
- 在Oracle ARM Docker环境下已验证TCP可达

**已知问题:**
- 海外IP基本全部超时（TCP 7709被墙）
- 0.11.x裸`Quotes.factory()`抛BESTIP ValueError，需用`tdx_client()` helper
