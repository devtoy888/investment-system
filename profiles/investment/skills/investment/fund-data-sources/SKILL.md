---
name: fund-data-sources
title: A股基金数据源架构与稳健化
description: >
  多源冗余设计、降级链配置、数据新鲜度标记、交易日/非交易日处理、
  海外IP适配(新加坡Oracle ARM)、多轮验证流程、微博KOL信号采集与分析。
  覆盖：fundgz失效修复、AKShare全量实时API、基金数据交叉验证、报告管线同步。
tags: [china-market, data-source, stability, fallback, redundancy, trade-day, overseas, akshare, report-pipeline]
triggers:
  - 数据源又出问题了 / 数据不准 / 这个接口挂了
  - 微博内容拉不全 / KOL分析不到位
  - 非交易日数据怎么搞 / 外盘数据过期了
  - push2 502 / push2delay / 东财502 / 海外超时
  - 为什么没有数据 / 数据源评估
  - 持仓快照失真 / 市值不对 / portfolio snapshot
  - 净值计算 / 1月不对 / 1周没算
  - 上传R2预览 / HTML打不开 / 乱码
  - 报告管线数据同步 / report pipeline / closing_review.py / send_closing.py
  - 东财接口实测 / verify API / test endpoint
  - 基金估算全为0% / fundgz失效
  - AKShare实时估算接入 / fund_value_estimation_em
  - 报告索引自动生成 / index.html历史报告
  - QQ格式：概览 vs R2格式：翔实
---

# 基金数据源架构

## 🚨 必须先读的参考文件

**在计算基金净值指标前，必须先读 `references/nav-calculation-methodology.md`**。该文档记录了一次严重数据错误（1m错报-1.8%实际-6.4%）的根因分析和修正方法。

| 参考文件 | 何时读 |
|:---------|:-------|
| `references/nav-calculation-methodology.md` | **每次计算基金NAV涨跌幅前** |
| `references/r2-upload-standards.md` | **每次向R2上传文件时** |
| `references/eastmoney-push2delay-verified-2026-07-21.md` | **每次排查东财接口问题时** |
| `references/qq-bot-format.md` | 每次生成推送文本时 |

## 核心原则

1. **数据层修复自动继承** — 修复底层函数后所有调用自动受益
2. **降级链 ≥3级** — 主源→备源→快照
3. **新鲜度标记** — `_stale`/`_fresh`/`_fetch_time`
4. **多轮验证** — 语法→功能→集成

## 降级链设计

```python
'基金净值': fundgz(已失效→404) → AKShare历史净值(线程池get_all_funds) → 板块代理估算 → 昨日快照
'涨跌家数': push2delay(2026-07-21实测100%) → push2(Oracle ARM通常502) → 新浪tags(4正则) → AKShare → 昨日快照
'北向资金': push2delay kamt.kline(2026-07实测100%) → push2 kamt.kline(**也与clist不同路由,实测100%**) → hexin(48%) → 快照
'指数资金流': push2delay stock/get指数字段(f135-f146,主力/超大单净额)
'外盘': Yahoo(+_stale标记) — 零日历维护
'板块资金流': push2delay clist(50行业,实测100%) — 新增能力
'板块涨跌排行': push2delay clist(50行业,实测100%) — 新增能力
```

## 关键数据源状态 (Oracle ARM新加坡)

| 数据源 | 海外IP状态 | 备注 |
|:-------|:----------:|:------|
| 腾讯财经(qt.gtimg.cn) | ✅ ~99% | 主力行情源 |
| push2delay.eastmoney.com | ✅ 100%(2026-07-21实测) | **优先使用** — 涨跌家数+板块资金流+板块排行 |
| push2.eastmoney.com | ❌ 多数502 | Oracle ARM CDN节点拦截，降级到push2delay |
| 天天基金(fundgz) | ❌ 已失效(2026-07-21起301→404) | 自动降级到AKShare |
| Yahoo Finance | ✅ ~100% | 外盘(+_stale标记) |
| AKShare fund_value_estimation_em | ✅ 主线程调用 | **最佳实时估算源**(~20秒全量20000+) |
| AKShare fund_open_fund_info_em | ✅ | 历史净值/趋势/回撤 |
| mootdx(通达信TCP) | ⚠️ TCP可达但库有bug | AKShare替代 |

## ⚠️ fundgz API失效链式修复（2026-07-21）

### 问题传播路径

```
fundgz.1234567.com.cn 301→404 (返回HTML非JSONP)
  → get_fund_value() 检查'jsonpgz('失败
    → 旧代码：不抛异常、不触备援、静默return None
      → 所有基金estimated_change=0.0%
        → execute_today_plan.py决策建议失真
        → closing_review.py持仓表全空
        → llm_analysis_v2.py AI分析基于错误数据
```

### 修复1: get_fund_value() AKShare备援移出except块

```python
# 旧：备援仅在except块内（fundgz返回200时被跳过）
# 新：不论fundgz返回什么，都执行AKShare备援
except Exception as e:
    if _retry: return get_fund_value(code, _retry=False)
# 函数末尾无条件执行AKShare备援
try:
    ak_data = get_fund_realtime(code)
    if ak_data: return {...change_source:'akshare'}
except: pass
return None
```

### 修复2: 全量AKShare实时估算（主线程一次性，精度最高）

`ak.fund_value_estimation_em()` 在主线程直接调用可获取20000+基金实时估算(~20秒)，精度远超板块代理。

```python
import akshare as ak
df = ak.fund_value_estimation_em()
est_col = [c for c in df.columns if '估算增长率' in c]
for _, row in df.iterrows():
    code = str(row['基金代码'])
    if code in FUND_CODES:
        val = str(row.get(est_col[0], '0')).replace('%', '').strip()
        fund_realtime[code] = float(val) if val and val != '---' else 0.0
```

### 已接入脚本清单

| 脚本 | 接入点 | 日期 |
|:-----|:-------|:----:|
| `execute_today_plan.py` | `build_portfolio()` AKShare覆盖 | ✅ 2026-07-21 |
| `closing_review.py` | `funds_now = get_all_funds()` 后覆盖 | ✅ 2026-07-21 |
| `llm_analysis_v2.py` | `build_closing_data_v2()`, `build_decision_data_v2()` | ✅ 2026-07-21 |
| `collect_noon_data.py` | 午报采集 — 未接入 | ⏳ TODO |
| `collect_morning_data.py` | 早报采集 — 未接入 | ⏳ TODO |

**接入模式**：主线程一次性调用→过滤FUND_CODES→无条件覆盖旧数据。不放在ThreadPoolExecutor。

### AKShare线程冲突陷阱

`get_all_funds()` 用5线程并行内部 `signal.SIGALRM` 超时仅主线程可用，子线程抛异常降级到历史API。正确模式是主线程 `ak.fund_value_estimation_em()`。

### fund_source_akshare.py stdout污染

多处 `print()` 走stdout污染报告输出。已修stderr + wrapper过滤双重保障。

## 微博KOL分析框架 v2

### 长文本处理
```python
if p.get("isLongText"):
    # /ajax/statuses/longtext?id={id} 获取完整内容
```

### 分析框架四层
1. Extractor → 结构化断言{sector, direction, timeframe, claim, confidence}
2. Verifier → 赛道→行情映射(SECTOR_DATA_MAP)，对比实际涨跌幅
3. Mapper → 信号→基金操作(SECTOR_TO_FUNDS)
4. format_push → QQ Bot纯文字

## Cron脚本路径陷阱

profiles目录不要用symlink（cron安全机制拒绝）。用wrapper脚本替代。

## 数据源验证纪律（2026-07-21确立）

**在推荐任何新数据源/API到生产环境前，必须从用户实际服务器实测。**

### 错误做法（曾被用户纠正）
```
看到README说某个API可用 → 直接推荐 → 用户发现不通 → 信任损失
```

### 正确流程
```
1. 编写测试脚本，从服务器sshd/terminal实际运行
2. 用urllib标准库（不依赖第三方包）测试连通性
3. 连续测5-10次统计可用率
4. 验证返回数据格式是否符合需求字段
5. 区分CDN节点问题 vs 真正的API不可用
6. 将验证结果写成references文档供后续查阅
```

### 本次验证发现的关键模式（Eastmoney from Oracle ARM）

| 现象 | 结论 |
|------|------|
| push2.eastmoney.com 502, 但首页200 | 不是IP被封，是特定CDN节点限制 |
| push2delay.eastmoney.com 200 | 不同CDN节点，全部可用 |
| clist/get 502, 但 stock/get 200 | 不同API端点走不同CDN路由 |
| 非交易时段数据一直不变 | push2delay返回最后一帧快照，正常行为 |

### 推荐的验证工具

```python
# 最小化验证脚本 - 不依赖requests/akshare
import urllib.request, json, time, random
UA = 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36'
REF = 'https://quote.eastmoney.com/'

def test_url(label, url):
    start = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent":UA, "Referer":REF})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        elapsed = time.time() - start
        print(f"[OK] {label}: {elapsed:.1f}s")
        return True
    except Exception as e:
        print(f"[FAIL] {label}: {e}")
        return False
```

## 板块资金流数据（2026-07-21新增能力）

两个新增函数已加入 `fund_tools.py`：

| 函数 | 功能 | 数据量 | 可用率 |
|------|------|--------|--------|
| `get_sector_fund_flow_em()` | 50个行业主力净流入排名 | 50行业 | 100% |
| `get_sector_rankings_em()` | 50个行业涨跌排行 | 50行业 | 100% |

### get_sector_fund_flow_em() 代码

```python
def get_sector_fund_flow_em() -> dict:
    \"\"\"获取行业板块资金流排名(东财push2delay)\"\"\"
    result = {}
    try:
        import urllib.request, urllib.parse, json
        UA = 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36'
        REF = 'https://quote.eastmoney.com/'
        p = {"pn":1,"pz":50,"po":1,"np":1,"fltt":2,"invt":2,"fid":"f62",
             "fs":"m:90+t:2","fields":"f12,f14,f2,f3,f4,f62,f184,f15,f16"}
        url = "https://push2delay.eastmoney.com/api/qt/clist/get?" + urllib.parse.urlencode(p)
        req = urllib.request.Request(url, headers={"User-Agent":UA, "Referer":REF})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        diff = data.get("data", {}).get("diff", [])
        for i, item in enumerate(diff):
            name = item.get('f14', '')
            if not name:
                continue
            net_inflow = item.get('f62') or 0
            result[name] = {
                'rank': i + 1,
                'change_pct': round(item.get('f3') or 0, 2),
                'net_inflow_wan': int(net_inflow),
                'net_inflow_yi': round(net_inflow / 100000000, 2),
                'price': item.get('f2'),
                'high': item.get('f15'),
                'low': item.get('f16'),
                'turnover_rate': item.get('f184'),
            }
    except Exception as e:
        print(f"get_sector_fund_flow_em: {e}")
    return result  # 返回50个行业数据
```

### get_sector_rankings_em() 代码

```python
def get_sector_rankings_em() -> dict:
    \"\"\"获取行业板块涨跌排行(东财push2delay)\"\"\"
    result = {}
    try:
        import urllib.request, urllib.parse, json
        UA = 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36'
        REF = 'https://quote.eastmoney.com/'
        p = {"pn":1,"pz":50,"po":1,"np":1,"fltt":2,"invt":2,"fid":"f3",
             "fs":"m:90+t:2","fields":"f12,f14,f2,f3,f4,f15,f16,f17,f18"}
        url = "https://push2delay.eastmoney.com/api/qt/clist/get?" + urllib.parse.urlencode(p)
        req = urllib.request.Request(url, headers={"User-Agent":UA, "Referer":REF})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        diff = data.get("data", {}).get("diff", [])
        for item in diff:
            name = item.get('f14', '')
            if not name:
                continue
            result[name] = {
                'change_pct': round(item.get('f3') or 0, 2),
                'price': item.get('f2'),
                'high': item.get('f15'),
                'low': item.get('f16'),
                'open': item.get('f17'),
                'prev_close': item.get('f18'),
            }
    except Exception as e:
        print(f"get_sector_rankings_em: {e}")
    return result  # 返回50个行业数据
```

### 关键API参数

1. `fid="f62"` → 按主力净流入排序，`fid="f3"` → 按涨跌幅排序
2. `fs="m:90+t:2"` → 东财行业板块分类（非申万分类）
3. `push2delay` 返回延迟约3秒数据，看板场景完全可接受
4. 全部使用标准库urllib，零外部依赖
| `get_sector_fund_flow_em()` | 2026-07-21 | 50行业资金流排名 |
| `get_sector_rankings_em()` | 2026-07-21 | 50行业涨跌排名 |
| `get_northbound_em()` | 待实现 | 北向资金(kamt.kline, push2/push2delay皆通) |
| `get_index_fundflow()` | 待实现 | 指数资金流字段(f135-f146) |

## ⚠️ 基金投资者需要市场数据（2026-07-21用户纠正）

**基金投资者也需要行情/板块/资金流/行业排名数据**，因为：
- 基金底层是股票，板块表现直接影响基金净值
- 板块资金流帮助判断赛道冷热（如半导体净流入166亿→基金可加仓）
- 行业排名辅助KOL信号交叉验证（唐主任说"存"→半导体板块确实涨+9.85%）
- 涨跌家数判断全市场系统性风险

**不要因为"用户买基金"就认为"不需要股票数据"。**

## 多轮验证流程

1. 语法+引用 → `py_compile.compile()` + 文件存在检查
2. 功能 → 实际数据拉取+输出格式
3. 集成 → cron链路验证+旧文件清理
4. 交易日验证 → 自动3轮(09:35/13:00/15:30)

## ⚠️ 报告路径不匹配：review_engine vs push_report（2026-07-21发现）

**问题**：`review_engine.py` 按 `reports/YYYY/MM/DD/report_type.md` 查找报告，但 `push_report_r2.py` 按 `reports/report_type_YYYY-MM-DD.md` 存储。路径不匹配导致 review_engine 报告3/4\"不存在\"，预测准确率恒为0%。

| 系统 | 期望路径 | 实际路径 | 状态 |
|:-----|:---------|:---------|:----:|
| push_report | `reports/closing_2026-07-21.md` | ✅ 扁平前缀 | 在线 |
| review_engine | `reports/2026/07/21/closing.md` | ❌ 日期子目录 | 404 |

**修复方案**：二选一
- 方案A：统一 push_report 按日期子目录格式存储
- 方案B：统一 review_engine 按扁平前缀格式查找
- 方案C：push_report 同时写两份（兼容已有链接）

## ⚠️ 估算净值 None 修复（2026-07-21）

**问题**：持仓表的"估算净值"列显示 None，因 get_fund_value() 返回 dict 不含 estimated_nav。

**修复**：在生成表格前手动计算 → `fd['estimated_nav'] = round(nav * (1 + ec/100), 4)`
已在 `closing_review.py`（持仓表）和 `llm_analysis_v2.py`（AI数据）中应用。

## QQ Bot Markdown链接失效（2026-07-21修复）

**问题**：`push_report_r2.py` 输出 `[Markdown报告](url)` 格式，QQ Bot不支持Markdown链接语法，点击时括号被当作URL一部分→404。

**修复**：改为纯文本URL：
```python
"📄 " + md_link + "\\n"
"🌐 " + html_link + "\\n"
```

## 报告R2存储架构：日期子目录（2026-07-21实现）

### 目录结构

```
旧（平铺）:                   新（日期目录）:
reports/                      reports/
├── closing_2026-07-21.md      ├── 2026/
├── decision_2026-07-21.md     │   └── 07/
├── noon_2026-07-21.md         │       └── 21/
├── morning.md                  │           ├── closing.md
├── dashboard.html             │           ├── closing.html
└── index.html                 │           ├── decision.md
                               │           ├── decision.html
                               │           ├── noon.md / noon.html
                               │           ├── morning.md / morning.html
                               ├── dashboard.html
                               ├── index.html
                               └── index.json
```

### push_report_r2.py 改动

```python
t = date.today()
subdir = f"{t.year}/{t.month:02d}/{t.day:02d}"
local_dir = REPORT_DIR / subdir
local_dir.mkdir(parents=True, exist_ok=True)
md_path = str(local_dir / f"{report_type}.md")
# ... 写文件 ...
# R2上传：同时写日期目录版 + 扁平兼容版
md_key = f"fund-system/reports/{subdir}/{report_type}.md"
md_key_flat = f"fund-system/reports/{report_type}_{today}.md"
upload_to_r2(md_path, md_key)
upload_to_r2(md_path, md_key_flat)  # 兼容已分享的旧链接
# 返回新格式链接
md_link = f"{BASE_URL}/{subdir}/{report_type}.md"
```

### review_engine.py 读取兼容

```python
# 优先读日期子目录，备援读平铺旧版
subdir = f"{dt.year}/{dt.month:02d}/{dt.day:02d}"
path = REPORT_DIR / subdir / f"{report_type}.md"
if not path.exists():
    path = REPORT_DIR / f"{report_type}_{dt.isoformat()}.md"
```

### run_review.py 索引扫描兼容

```python
# 扫描日期子目录
for sub in REPORT_DIR.glob("[0-9][0-9][0-9][0-9]/*/*/"):
    rdate = f"{sub.parent.parent.name}-{sub.parent.name}-{sub.name}"
    for f in sub.glob("*.md"):
        reports.setdefault(rdate, {})[f.stem] = rdate
# 扫描平铺旧版
for f in REPORT_DIR.glob("*_*-*-*.md"):
    parts = name.split("_", 1)
    if len(parts) == 2:
        rtype, rdate = parts
        reports.setdefault(rdate, {})[rtype] = name
```

### 索引链接生成

旧版链接: `{BASE_URL}/{rtype}_{rdate}.md`  
新版链接: `{BASE_URL}/{year}/{month}/{day}/{rtype}.md`

## 报告索引自动生成（2026-07-21实现）

每日17:00审阅cron（`run_review.py`）在完成审阅后自动扫描reports目录生成index.html并上传R2。

- 扫描日期子目录 + 平铺旧版两种格式
- 识别6种报告类型：晨报/午报/09:35方向/14:30决策/收盘复盘/周报/外盘
- 按日期倒序排列，彩色标签+MD/HTML双链接
- 深色模式支持（跟随系统+手动切换）
- 上传至 `fund-system/reports/index.html`

当周日/周报/外盘报告生成后，下次审阅周期自动收录。

## ⚠️ R2报告上传后必须验证CDN（2026-07-21会话核心纠正）

每次修改→上传→通知用户链路中，必须加一步CDN验证：

**正确流程（修复后）：**
```
修改代码 → 生成本地文件 → 上传R2 → curl验证线上（非web_extract）
→ 检查 last-modified 头部 → 确认无"报告不存在"等占位符
→ 确认每个字段渲染正确 → 通知用户
```

**常见错误（多次触发用户不满）：**
```
修改代码 → 直接通知用户 "修好了" ❌
→ 用户读的是CDN缓存旧版 → "根本没好" 
→ 反复重试 → 信任损失
```

## ⚠️ group_funds() 基金名称为空（2026-07-21）

**问题**：group_funds() 返回的 dict 不含 code 字段，下游取名用 f.get('name','?') 但 name 为空。

**修复**：在 group_funds() 循环内注入 `v['code'] = code`。
下游显示格式：`{fcode} {FUND_CODES.get(fcode, fname)[:20]}`。
涉及文件：closing_review.py（持仓表）、send_closing.py（推送）。
