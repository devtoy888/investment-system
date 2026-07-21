# 海外服务器A股数据源可用性报告

**测试时间**: 2026-07-18 周六 (非交易日)
**服务器**: Oracle ARM (overseas)
**Python**: 3.13.5, mootdx 0.11.7, pandas 3.0.3
**每源3次取平均耗时**
**测试脚本**: `/opt/data/scripts/test_overseas_v2.py`
**结果JSON**: `/opt/data/scripts/overseas_source_test_v2.json`

## 汇总

| 数据源 | 可达 | 平均耗时 | 数据返回 | 推荐 | 判定 |
|:---|---:|---:|:---|:---:|:---|
| sine_新浪财经三表 | ✅ | 0.52s | 完整HTML(GB2312) | ✅ | **完全可用** |
| baidu_百度股市通 | ✅ | 0.28s | API空(ResultNum=0) | ✅ | API可达，待交易日验证 |
| mootdx_通达信TCP | 🟡 | 18.04s | Socket可达，K线协议失败 | 🟡 | TCP可达，兼容性问题 |
| 10jqka_同花顺 | ❌ | 1.55s | HTTP 200空body(0字节) | ❌ | 海外IP静默过滤 |
| cninfo_巨潮公告 | ❌ | 0.29s | HTTP 500/401/空数据 | ❌ | 海外IP全面封禁 |

## 详细发现

### 1. mootdx 通达信TCP

- **TCP Socket**: 10/10服务器全部可达（打破"海外全超时"旧假设）
  - 119.97.185.59:7709 ~ 124.71.187.122:7709 全部通过 socket.create_connection(timeout=2)
- **K线数据**: 3/3次全部失败 `KeyError: 'datetime'`
  - 根本原因：mootdx 0.11.7 `get_k_data()` 第449行 `data['datetime']` — to_df()返回的DataFrame列名不含'datetime'
  - pandas 3.0.3 与 mootdx 0.11.7 兼容性问题
- **建议**: 用 `--target` 隔离安装低版本 pandas，或直接用腾讯HTTP API替代K线需求

### 2. 同花顺 10jqka

- **API端点**: `basic.10jqka.com.cn/api/stockph/hotstock/` → HTTP 200 + 0字节body (3/3次)
- **板块排行API**: `basic.10jqka.com.cn/api/stockph/plate/rank/` → 同上，0字节
- **HTML页面**: `data.10jqka.com.cn` → HTTP 200 + 78KB HTML (可达但不含数据API)
- **结论**: 海外IP被静默过滤，不适合海外部署

### 3. 百度股市通

- **Opendata API**: `gushitong.baidu.com/opendata?resource_id=5353` → HTTP 200 (0.21s avg)
  - 返回格式: `{"QueryID":"...","ResultCode":0,"ResultNum":0,"Result":[]}`
  - ResultNum=0 可能是周六非交易日，也可能是海外IP过滤
- **HTML股票页**: `gushitong.baidu.com/stock/ab-000001` → 302 → `finance.baidu.com/stock/ab-000001` (31KB)
- **建议**: 交易日再验证一次，确认数据返回后作为腾讯备援

### 4. 新浪财经三表 ✅

- **资产负债表**: `vip.stock.finance.sina.com.cn/.../vFD_BalanceSheet/.../600519/...` → HTTP 200, 82172字节, GB2312, has_table=True
- **利润表**: `.../vFD_ProfitStatement/.../600519/...` → HTTP 200, 59216字节
- **现金流量表**: `.../vFD_CashFlow/.../600519/...` → HTTP 200, 76319字节
- **结论**: 三表全部可达，零鉴权。可作为财务数据替代源。需解析GB2312编码HTML表格。

### 5. 巨潮公告 cninfo.com.cn

- **disclosure API**: `cninfo.com.cn/new/disclosure` → HTTP 500 (6/6次)
- **hisAnnouncement/query**: → HTTP 200 但 totalAnnouncement=0 (空数据，3/3次)
- **webapi.cninfo.com.cn**: → HTTP 401 `"code_005_ipban_notoken"`
- **结论**: 海外IP被全面封禁。需国内代理或VPN。

## 与现有数据源的对比

| 需求 | 现有源 | 海外可用性 | 新替代源 | 海外可用性 |
|:-----|:-------|:---------:|:---------|:---------:|
| K线数据 | mootdx TCP | 🟡 TCP可达,协议兼容问题 | 腾讯HTTP API | ✅ 已稳定 |
| 板块排行 | 东财 | ❌ 22.7% | 同花顺 | ❌ 海外IP过滤 |
| 查询数据 | - | - | 百度股市通 | ✅ API可达(数据待验证) |
| 财务报表 | - | - | 新浪财经三表 | ✅ 完全可用 |
| 公告 | - | - | 巨潮公告 | ❌ 海外IP封禁 |
