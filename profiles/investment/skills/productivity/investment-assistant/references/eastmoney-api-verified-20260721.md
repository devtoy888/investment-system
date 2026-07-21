# 东财API实测验证记录（2026-07-21）

> 测试环境：Oracle ARM 新加坡 (152.70.91.4)  
> 测试方式：urllib标准库 + push2delay优先降级

## 总览

| 接口域名 | clist/get | stock/get | kamt.kline/get | ulist.np/get |
|----------|-----------|-----------|----------------|---------------|
| `push2.eastmoney.com` | ❌ 502 | ❌ 502 | ✅ 200 | ✅ 200 |
| `push2delay.eastmoney.com` | ✅ 200 | ✅ 200 | ✅ 200 | ✅ 200 |

结论：push2delay 全部可用，push2 仅 clist/stock 被拦（不同CDN节点）。

## 已验证可用的数据

### 1. 板块资金流（50个行业）

```
GET https://push2delay.eastmoney.com/api/qt/clist/get
  pn=1, pz=50, po=1, np=1, fltt=2, invt=2, fid=f62
  fs=m:90+t:2
  fields=f12,f14,f2,f3,f4,f62,f184,f15,f16

返回: data.diff[] 每项含:
  f14 = 行业名
  f3  = 涨跌幅%
  f62 = 主力净流入(元)
  f184 = 换手率
```

### 2. 板块涨跌排名（50个行业）

```
GET https://push2delay.eastmoney.com/api/qt/clist/get
  pn=1, pz=50, po=1, np=1, fltt=2, invt=2, fid=f3
  fs=m:90+t:2
  fields=f12,f14,f2,f3,f4,f15,f16,f17,f18

返回: data.diff[] 每项含:
  f14 = 行业名, f2 = 最新价, f3 = 涨跌幅%
  f15 = 最高, f16 = 最低, f17 = 开盘, f18 = 昨收
```

### 3. 全市场涨跌家数

```
GET https://push2delay.eastmoney.com/api/qt/stock/get
  secid=1.000001
  fields=f57,f58,f167,f168,f169,f170,f171

返回: 
  f167 = 涨停数
  f168 = 跌停数
  f169 = 上涨家数
  f170 = 下跌家数
  f171 = 平盘家数
```

（之前的数据中心涨跌家数只有14%可用率，push2delay路径100%可用）

### 4. 北向资金余额+流向（push2和push2delay都通）

```
GET https://push2.eastmoney.com/api/qt/kamt.kline/get
  secid=1.000001
  fields1=f1,f2,f3,f4
  fields2=f51,f52,f53,f54,f55
  klt=101 (日线), lmt=3

返回: data:
  hk2sh = ["2026-07-21,remaining_quota,buy_amount,sell_amount"]  (北向沪)
  sh2hk = ["2026-07-21,remaining_quota,buy_amount,sell_amount"]  (南向沪)
  hk2sz = ["2026-07-21,remaining_quota,buy_amount,sell_amount"]  (北向深)
  sz2hk = ["2026-07-21,remaining_quota,buy_amount,sell_amount"]  (南向深)
```

金额单位推测为万元（5200000 = 520亿，与沪股通日额度一致）。

### 5. 指数主力资金流（指数字段提取）

```
GET https://push2delay.eastmoney.com/api/qt/stock/get
  secid=1.000001
  fields=f57,f58,f135,f136,f137,f138,f139,f140,f141,f142,f143,f144,f145,f146

返回:
  f135 = 沪主力流入(元)
  f136 = 沪主力流出(元)
  f137 = f135 - f136 (净额)
  f141 = 沪超大单流入
  f142 = 沪超大单流出
  f143 = f141 - f142 (净额)
  f144 = 深主力流入
  f145 = 深主力流出
  f146 = f144 - f145 (净额)
```

### 6. 腾讯指数行情（已有，不改）

```
GET https://qt.gtimg.cn/q=sh000001,sh000688,sh000300,sz399001,sz399006
编码: gbk
返回: 每行由~分隔，索引3=现价，32=涨跌幅%
```

## 不可用的接口

| 接口 | 原因 | 替代方案 |
|------|------|---------|
| `push2.eastmoney.com/api/qt/clist/get` | CDN 502 | push2delay |
| `push2.eastmoney.com/api/qt/stock/get` | CDN 502 | push2delay |
| `datacenter-web.eastmoney.com/api/data/v1/get` `RPT_MUTUAL_DEAL_STOCK` | 报表名已失效 | kamt.kline |
| `search-api-web.eastmoney.com` | 参数格式变化 | 暂不修复 |
| `reportapi.eastmoney.com` | 参数格式变化 | 暂不修复 |
