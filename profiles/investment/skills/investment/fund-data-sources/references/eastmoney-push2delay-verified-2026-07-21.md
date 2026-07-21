# Eastmoney push2delay 实测验证报告（2026-07-21）

> 从 Oracle ARM 新加坡节点（152.70.91.4）实测

## 核心发现

| 接口 | URL | 实测结果 |
|------|-----|---------|
| push2 实时 | `push2.eastmoney.com/api/qt/clist/get` | ❌ 502 (CDN节点限制) |
| push2 实时 | `push2.eastmoney.com/api/qt/stock/get` | ❌ 502 |
| push2 实时 | `push2.eastmoney.com/api/qt/kamt.kline/get` | ✅ **200** (与clist不同路由) |
| push2delay 延迟 | `push2delay.eastmoney.com/api/qt/clist/get` | ✅ 200 (100%) |
| push2delay 延迟 | `push2delay.eastmoney.com/api/qt/stock/get` | ✅ 200 (100%) |
| 腾讯 qt.gtimg.cn | — | ✅ 始终可用 |
| 东财首页 | `www.eastmoney.com` | ✅ 200 |

**结论**：不是Oracle IP被封（首页能打开），而是 push2 的特定CDN节点（120.76.218.228）拦截了Oracle段IP。push2delay 使用不同CDN节点（119.3.232.150），完全可用。

## 已验证的数据能力

### 1. 涨跌家数（替代原14%可用率接口）

```
使用 stock/get 接口，secid=1.000001
字段: f167=涨停, f168=跌停, f169=上涨, f170=下跌, f171=平盘
可用率: 10/10 = 100% ✅（原push2实时端约14%）
数据示例: 涨6809 跌179 涨停0 跌停152
```

### 2. 板块资金流（行业级别）

```
使用 clist/get 接口，fs="m:90+t:2" (东财行业分类)
按主力净流入(f62)排序
返回50个行业的：涨跌幅、主力净流入(万)、换手率
可用率: 5/5 = 100% ✅
数据示例:
  电子      净流入+275.0亿  涨幅+7.37%
  半导体    净流入+166.2亿  涨幅+9.85%
  有色金属  净流入+49.2亿   涨幅+3.92%
```

### 3. 板块涨跌排行

```
使用 clist/get 接口，按涨跌幅(f3)排序
返回50个行业的：涨跌幅、开盘/最高/最低/昨收
可用率: 100% ✅
```

## 关键参数

```python
# 东财行业分类
FS_SECTORS = "m:90+t:2"

# 涨跌家数（通过上证指数查询）
BREADTH_FIELDS = "f57,f58,f167,f168,f169,f170,f171"
BREADTH_URL = "https://push2delay.eastmoney.com/api/qt/stock/get?secid=1.000001"

# 板块资金流（clist，按净流入排序）
FLOW_PARAMS = {
    "pn": 1, "pz": 50, "po": 1, "np": 1,
    "fltt": 2, "invt": 2, "fid": "f62",
    "fs": "m:90+t:2",
    "fields": "f12,f14,f2,f3,f4,f62,f184,f15,f16"
}

# 板块涨跌（clist，按涨跌幅排序）
RANK_PARAMS = {
    "pn": 1, "pz": 50, "po": 1, "np": 1,
    "fltt": 2, "invt": 2, "fid": "f3",
    "fs": "m:90+t:2",
    "fields": "f12,f14,f2,f3,f4,f15,f16,f17,f18"
}
```

## 重要：字段含义

| 字段 | 含义 | 备注 |
|------|------|------|
| f2 | 最新价 | |
| f3 | 涨跌幅% | |
| f4 | 涨跌额 | |
| f12 | 股票/板块代码 | |
| f14 | 股票/板块名称 | |
| f15 | 最高价 | |
| f16 | 最低价 | |
| f17 | 开盘价 | |
| f18 | 昨收价 | |
| f62 | 主力净流入(元) | 除以1e8得亿 |
| f184 | 换手率% | |
| f167 | 涨停家数 | stock/get用 |
| f168 | 跌停家数 | stock/get用 |
| f169 | 上涨家数 | stock/get用 |
| f170 | 下跌家数 | stock/get用 |
| f171 | 平盘家数 | stock/get用 |

### 4. 北向资金（kamt.kline，push2和push2delay都通）

**关键发现**：push2 的 kamt.kline 接口与 clist 不同 CDN 路由 —— clist 返回 502 但 kamt.kline 返回 200。这是目前唯一从 Oracle ARM 直连 push2 还能通的接口。

```python
def get_northbound_em() -> dict:
    """获取北向资金余额+流向（东财kamt.kline，push2和push2delay皆通）"""
    result = {'hk2sh_buy': 0, 'hk2sz_buy': 0, 'hk2sh_sell': 0, 'hk2sz_sell': 0}
    for domain in ['push2delay.eastmoney.com', 'push2.eastmoney.com']:
        try:
            import urllib.parse
            p = {"secid":"1.000001","fields1":"f1,f2,f3,f4",
                 "fields2":"f51,f52,f53,f54,f55","klt":101,"lmt":3}
            url = f"https://{domain}/api/qt/kamt.kline/get?" + urllib.parse.urlencode(p)
            req = urllib.request.Request(url, headers={"User-Agent":UA, "Referer":REF})
            with urllib.request.urlopen(req, timeout=8) as resp:
                d = json.loads(resp.read().decode('utf-8'))
            data = d.get("data", {})
            hk2sh = data.get("hk2sh", [])
            hk2sz = data.get("hk2sz", [])
            if hk2sh and hk2sz:
                sh_parts = hk2sh[0].split(',')
                sz_parts = hk2sz[0].split(',')
                result['hk2sh_buy'] = float(sh_parts[2]) * 10000
                result['hk2sz_buy'] = float(sz_parts[2]) * 10000
                result['source'] = domain.split('.')[0]
                return result
        except:
            continue
    return result
```

**返回格式**：`hk2sh: ["2026-07-21,0.00,5200000.00,0.00"]` — 日期,剩余额度(万),买入(万),卖出(万)。5200000万=520亿。

### 5. 指数资金流（指数字段提取，2026-07-21新验证）

从指数行情 `stock/get` 的 f135-f146 字段提取主力资金流：

| 字段 | 含义 | 示例 |
|------|------|------|
| f135 | 上证主力流入(元) | 5652.8亿 |
| f136 | 上证主力流出(元) | 5527.6亿 |
| f141 | 上证超大单流入(元) | 3561.8亿 |
| f142 | 上证超大单流出(元) | 3597.0亿 |
| f144 | 深证主力流入(元) | 4410.1亿 |
| f145 | 深证主力流出(元) | 4537.0亿 |

```python
def get_index_fundflow() -> dict:
    import urllib.parse
    p = {"secid":"1.000001","fields":"f135,f136,f141,f142,f144,f145"}
    url = "https://push2delay.eastmoney.com/api/qt/stock/get?" + urllib.parse.urlencode(p)
    req = urllib.request.Request(url, headers={"User-Agent":UA, "Referer":REF})
    with urllib.request.urlopen(req, timeout=10) as resp:
        d = json.loads(resp.read().decode('utf-8'))
    data = d.get("data", {})
    sh_net = (data.get('f135',0)-data.get('f136',0))/1e8
    sz_net = (data.get('f144',0)-data.get('f145',0))/1e8
    big_net = (data.get('f141',0)-data.get('f142',0))/1e8
    return {'sh_main_net': sh_net, 'sz_main_net': sz_net, 'super_large_net': big_net}
```

```python
# push2delay 实测
url = "https://push2delay.eastmoney.com/api/qt/kamt.kline/get?secid=1.000001&fields1=f1,f2,f3,f4&fields2=f51,f52,f53,f54,f55&klt=101&lmt=3"
# 返回:
# hk2sh: ["2026-07-21,0.00,5200000.00,0.00"]  # 北向沪: 日期,剩余额度,买入,卖出
# sh2hk: ["2026-07-21,4200000.00,0.00,4200000.00"]
# hk2sz: ["2026-07-21,0.00,5200000.00,0.00"]  # 北向深
# sz2hk: ["2026-07-21,4200000.00,0.00,4200000.00"]

# push2 实测也通（不同于clist）
url = "https://push2.eastmoney.com/api/qt/kamt.kline/get?secid=1.000001&..."
# 返回相同数据 ✅
```

每行格式：`日期,剩余额度(万),买入金额(万),卖出金额(万)`。5200000万=520亿。

### 5. 指数资金流（指数字段）

从指数行情 stock/get 提取主力资金流：

```python
# 上证 secid=1.000001
# f135=主力流入, f136=主力流出, f141=超大单流入, f142=超大单流出
# f144=深证主力流入, f145=深证主力流出
上证主力净额 = (f135-f136)/1e8  # +125.2亿
上证超大单净额 = (f141-f142)/1e8  # -35.2亿
深证主力净额 = (f144-f145)/1e8    # -126.9亿
```

## 修正后的降级策略（适用于Oracle ARM）

```
涨跌家数: push2delay stock/get → push2(通常502) → 新浪 → AKShare
板块资金流: push2delay clist（直连）
板块涨跌: push2delay clist（直连）
北向资金: push2delay kamt.kline → push2 kamt.kline(也通) → hexin
指数资金流: push2delay stock/get指数字段
```

## 注意

1. push2delay 数据延迟约3秒，对看板场景完全无影响
2. clist接口分页返回（每页最多100条），板块查询pz=50一次返回
3. 全市场涨跌家数查询（上证指数stock/get）一次返回，不需要分页
4. 使用urllib标准库即可，不依赖requests/akshare
