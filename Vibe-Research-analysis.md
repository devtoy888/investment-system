# Vibe-Research 数据源方案深度分析

> 分析时间：2026-07-18
> 仓库：https://github.com/simonlin1212/Vibe-Research
> 定位：个人 AI 投研系统（A股/美股/港股）

---

## 一、数据源全景架构

Vibe-Research 采用**三层数据源、开箱即用**的设计：三个独立数据工具包子仓库直接嵌入项目根目录，`git clone` 后无需额外下载或接线即可使用。

```
Vibe-Research/
├── a-stock-data/          ← A股全栈数据工具箱（v3.3，10层·40端点）
├── global-stock-data/     ← 美股/港股工具箱（v1.0.1，8层·18端点）
├── backend/
│   ├── astock.py          ← A股数据层（移植自 a-stock-data）
│   ├── gstock.py          ← 美股/港股层（移植自 global-stock-data）
│   ├── newsradar.py       ← 资讯雷达（移植自 investment-news）
│   ├── market.py          ← 市场情绪+板块资金+短线情绪
│   └── news_sources.json  ← 108个RSS源配置
```

---

## 二、详细数据源清单

### 2.1 A股数据源（`backend/astock.py` — 816行，10层架构）

| 层级 | 数据内容 | 数据源 | 获取方式 | 依赖级别 |
|------|---------|--------|---------|---------|
| **L1 行情** | 实时报价/PE/PB/市值/换手/涨跌停 | **腾讯财经** `qt.gtimg.cn` | `urllib` GET（纯标准库） | ⭐ 永远可用 |
| **L1 大盘指数** | 上证/深成指/创业板/沪深300 | **腾讯财经** | 同上 | ⭐ 永远可用 |
| **L2 研报** | 个股/行业研报列表+PDF链接 | **东财 reportapi** | `requests` GET | 轻量必装 |
| **L3 一致预期** | 机构预测EPS（同花顺） | **同花顺** via akshare | akshare惰性导入 | 可选 |
| **L3 新闻** | 个股新闻 | **东财** via akshare | akshare惰性导入 | 可选 |
| **L3 基本面** | 行业/股本/上市时间 | **东财** via akshare | akshare惰性导入 | 可选 |
| **L3 公告** | 巨潮公告（cninfo） | **巨潮资讯** via akshare | akshare惰性导入 | 可选 |
| **L3 公告(稳定版)** | 个股近期公告 | **东财 np-anotice** | `requests` GET | 轻量必装 |
| **L4 K线** | 日/周/月/60分钟K线 | 通达信 via **mootdx** | mootdx TCP协议 | 可选 |
| **L4 财务** | 季报财务快照(37字段) | 通达信 via **mootdx** | mootdx TCP协议 | 可选 |
| **L4 财务摘要** | 营收/净利/ROE/毛利率 | **同花顺** via akshare | akshare惰性导入 | 可选 |
| **L5 估值分位** | PE-TTM/PB历史分位(近5年) | **百度股市通** via akshare | akshare惰性导入 | 可选 |
| **L5 完整估值** | 前向PE/PEG/消化年数 | 腾讯+akshare组合 | 混合 | 可选 |
| **L6 融资融券** | 日级两融明细 | **东财 datacenter** `RPTA_WEB_RZRQ_GGMX` | `requests` GET | 轻量必装 |
| **L6 大宗交易** | 折溢价/买卖营业部 | **东财 datacenter** `RPT_DATA_BLOCKTRADE` | `requests` GET | 轻量必装 |
| **L6 股东户数** | 季度筹码集中度 | **东财 datacenter** `RPT_HOLDERNUMLATEST` | `requests` GET | 轻量必装 |
| **L6 分红** | 历史分红送转 | **东财 datacenter** `RPT_SHAREBONUS_DET` | `requests` GET | 轻量必装 |
| **L6 资金流** | 120日主力/大单/小单净流入 | **东财 push2his** | `requests` GET | 轻量必装 |
| **L6 龙虎榜** | 上榜记录+买卖席位+机构 | **东财 datacenter** 多表联查 | `requests` GET | 轻量必装 |
| **L6 限售解禁** | 历史+未来90天解禁日历 | **东财 datacenter** `RPT_LIFT_STAGE` | `requests` GET | 轻量必装 |
| **L6 概念板块** | 个股所属概念/板块归属 | **东财 push2 slist** | `requests` GET | 轻量必装 |
| **L6 热门概念** | 热门概念命中 | **东财 emappdata** | `requests` POST | 轻量必装 |
| **L6 互动易** | 投资者问答 | **巨潮 cninfo IRM** | `requests` POST | 轻量必装 |
| **L10 打板情绪** | 涨停/炸板/跌停/昨涨停池 | **东财 push2ex** `getTopicZTPool`等 | `requests` GET | 轻量必装 |
| **L10 成交额榜** | 全市场成交额TOP20 | **东财 push2 clist** | `requests` GET | 轻量必装 |
| **L10 行业排名** | 全行业涨跌幅排名 | **东财 push2 clist** | `requests` GET | 轻量必装 |
| **板块资金流** | 行业资金净流入/净流出 | **乐股网** via akshare | akshare惰性导入 | 可选 |
| **市场情绪** | 涨跌家数/涨停跌停/活跃度 | **乐股网** via akshare | akshare惰性导入 | 可选 |

### 2.2 美股/港股数据源（`backend/gstock.py` — 183行）

| 数据内容 | 数据源 | 获取方式 | 覆盖 |
|---------|--------|---------|------|
| 全球指数（道指/标普/纳指/恒生/恒生科技） | **东财 push2** `stock/get` | `requests` GET（复用astock.em_get） | 全球5大指数 |
| 美股/港股搜索 | **东财 searchapi** | `requests` GET（精确代码匹配优先） | 美股+港股+韩股 |
| 美股/港股实时行情 | **东财 push2/push2delay** | `requests` GET（push2优先→失败降级delay） | 美股+港股 |
| 关键财务指标(营收/净利/EPS/ROE/毛利率/负债率) | **东财 datacenter** `GMAININDICATOR` | `requests` GET | 美股+港股（韩股仅行情） |
| 韩股行情 | **东财 push2** MktNum=177 | `requests` GET | 含三星/SK海力士等 |

**global-stock-data 工具包**（完整版，agent可直接调用）还包含：新浪+Yahoo行情、Yahoo K线/期权/SEC EDGAR XBRL、技术指标(MA/MACD/RSI/KDJ/布林带)等。后端只移植了东财域内的合规子集。

### 2.3 资讯数据源（`backend/newsradar.py` + `news_sources.json`）

| 属性 | 详情 |
|------|------|
| **源数量** | 108个公开RSS/Atom源 |
| **赛道分类** | 12个：AI/大模型、半导体/芯片、机器人/自动化、汽车/新能源车、能源/新能源、生物医药/健康、航天/太空、网络安全、科技/互联网、消费电子/数码、财经/宏观、科学/前沿 |
| **获取方式** | Python标准库 `urllib` + `xml.etree.ElementTree`（零第三方依赖） |
| **并发策略** | `ThreadPoolExecutor(max_workers=40)` 并行抓取 |
| **每条源抓取数** | 最多6条/源 |
| **时间窗口** | 最近7天 |
| **超时** | 15秒/源 |
| **零鉴权** | 全部公开RSS，无需任何API key |

**代表性源包括**：
- AI赛道：OpenAI Blog、Google Research、HuggingFace、DeepMind、arXiv cs.AI、MIT Tech Review、量子位、机器之心等16个
- 半导体：SemiAnalysis、DIGITIMES、IEEE Spectrum、SemiWiki等9个
- 科技：TechCrunch、The Verge、Ars Technica、Hacker News、36氪、虎嗅等15个
- 宏观：CNBC、FT、WSJ、Yahoo Finance、华尔街见闻、SEC、Federal Reserve等12个

---

## 三、数据获取方式分类

### 3.1 方式一：HTTP API直连（主力方式）

**基础传输层**：纯 `urllib.request` 或 `requests`
- 腾讯行情：`urllib.request.urlopen()` → GBK解码
- 东财全系：`requests.get()` / `requests.post()`
- RSS资讯：`urllib.request.urlopen()` → XML解析

**东财统一入口** (`em_get` 函数)：
```python
def em_get(url, params=None, headers=None, timeout=15):
    # 1. 串行限流：两次请求最小间隔1秒+随机抖动(0.1~0.5s)
    # 2. 直连优先：先试直连(trust_env=False, timeout=8s)
    # 3. 失败降级：直连失败→走系统代理
    # 4. 探测结果整个进程复用
```

### 3.2 方式二：通达信TCP协议（mootdx）

- 通过 `mootdx.quotes.Quotes.factory(market="std")` 连接通达信行情服务器
- 获取K线和财务数据（37字段季报快照）
- **惰性导入**：未安装mootdx时对应端点返回`501 + 安装提示`

### 3.3 方式三：akshare封装（惰性导入）

- 一致预期EPS（同花顺）、市场情绪（乐股网）、板块资金流、个股新闻/公告/基本面等
- 作为可选项，缺失不阻塞核心功能

### 3.4 方式四：RSS/Atom Feed解析

- 纯标准库：`xml.etree.ElementTree.fromstring()`
- 同时支持RSS(`<item>`)和Atom(`<entry>`)格式
- 支持 `pubDate` / `published` / `updated` / `date` 多种时间格式

---

## 四、数据验证与错误处理机制

### 4.1 分层分级依赖——核心功能永不断

```
Level 0 (永远可用): 腾讯行情 → 仅需 urllib，零第三方依赖
Level 1 (轻量必装): 东财研报/公告/资金面/龙虎榜等 → 仅需 requests
Level 2 (可选增强): akshare/mootdx → 未安装时返回 HTTP 501 + pip install 提示
```

### 4.2 输入验证

- **A股代码**：强制6位数字校验 (`re: ^\d{6}$`)，非法输入返回 `HTTP 400`
- **美股/港股搜索**：精确代码匹配优先（`Code==q`，防止搜AAPL混入票据/ETF）；数字型港股短代码自动补零（`"700"` → `"00700"`）
- **韩股**：必须带 `.KS`/`.KQ`/`.KR` 后缀区分（韩股代码与A股同为6位数字）
- **参数范围检查**：`top`(5-50)、`pages`(1-5)、`limit`(1-50)、`category`(4/5/6/11)

### 4.3 响应数据形状校验（契约测试）

**离线测试** (`test_pure.py` + `test_api.py`)：
- 市场前缀映射测试（沪/深/北交/ETF）
- 估值计算正确性（PEG/消化年数边界）
- 腾讯行情解析正确性（≥53字段、坏行跳过）
- API参数校验（非法代码→400、缺key→400）
- 美股/港股解析失败→404（非500）

**联网冒烟测试** (`test_live.py`, `pytest -m live`)：
- 真实数据源shape校验（按代码600519测试）
- 断言偏"形状"而非"非空"（住宅IP风控/限流可能间歇为空不算失败）
- 覆盖：行情、估值、研报、公告、财务、融资融券、股东户数、分红、概念板块、行业排名、短线情绪、成交额榜、全球指数、美股港股

### 4.4 异常兜底策略

| 场景 | 处理方式 |
|------|---------|
| 行情源暂时不可达 | try/except → HTTP 502 + 异常信息 |
| 美股push2掉连 | push2优先→自动降级push2delay（延时行情），latch到可用主机 |
| 东财datacenter无数据 | 返回空列表 `[]`（不断开、不报错） |
| 一致预期缺某年数据 | 返回None占位，估值字段以null填充 |
| 腾讯行情行解析失败 | 字段不足/无引号行→安全跳过，不抛异常 |
| RSS源抓取失败 | 返回None，计入`failed_sources`统计，不阻塞其他源 |
| akshare/mootdx未安装 | 抛出`DependencyMissing`→ HTTP 501 + 安装提示 |
| 用户持仓数据迁移失败 | 打印stderr警告，不阻塞启动，旧数据原样保留 |

### 4.5 缓存策略（减少数据源压力）

| 数据类型 | 缓存时长 | 缓存范围 |
|---------|---------|---------|
| 市场情绪+板块资金流 | 5分钟 | 全站共享 |
| 短线情绪（连板梯队） | 5分钟 | 全站共享 |
| 成交额TOP20 | 5分钟 | 全站共享 |
| 全球指数 | 5分钟 | 全站共享 |
| 行业排名 | 5分钟 | 全站共享 |
| 资金流(个股120日) | 15分钟 | 按代码 |
| 公告 | 15分钟 | 按代码 |
| 互动易 | 15分钟 | 按代码 |
| 热门概念 | 15分钟 | 按代码 |
| 估值分位 | 30分钟 | 按代码 |
| 财务摘要 | 30分钟 | 按代码 |
| 融资融券/大宗交易/股东/分红/龙虎榜/解禁/板块 | 30分钟 | 按代码 |
| 持仓行情 | 30分钟 | 后台定时刷新 |

空结果不缓存：数据源故障时下次请求直接重试。

### 4.6 合规红线过滤（资讯）

`news_sources.json`内置27个`redline_keywords`过滤词（中英文）：
- 赌博相关：赌博/博彩/赌场/彩票/下注/押注/gambling/betting/casino/lottery/sportsbook
- 预测市场：预测市场/polymarket/kalshi/prediction market
- 加密货币：加密货币/虚拟货币/比特币/以太坊/稳定币/crypto/bitcoin/ethereum/stablecoin
- 色情内容：色情/porn

过滤在标题+摘要的`blob`上做关键词匹配，命中即丢弃。

---

## 五、数据源稳定性保障

### 5.1 东财反封策略

1. **内置限流**：两次东财请求最小间隔1秒 + 随机抖动0.1~0.5秒（`_EM_MIN_INTERVAL = 1.0`）
2. **直连优先模式**：自动探测网络环境——国内财经站直连，避开用户Clash/V2Ray科学上网代理挂掉国内站
3. **代理降级**：直连失败→走系统代理，探测结果整个进程复用
4. **环境变量控制**：`VR_DATA_PROXY=1`强制走代理

### 5.2 数据源冗余

- **行情**：push2(实时)→push2delay(延时) 自动降级
- **成交额榜**：push2→push2delay 降级
- **美股行情**：东财搜索无精确匹配时退回第一条（名称查询兜底）

### 5.3 惰性导入——核心服务零阻塞

- `akshare`和`mootdx`只在被调用时导入
- 未安装时抛出`DependencyMissing`异常
- API层统一捕获 → 返回`HTTP 501 + "pip install xxx"`提示
- 行情和研报功能完全不受影响

### 5.4 缓存原子写入

```python
# 资讯缓存：先写临时文件，再原子改名——防并发交错写坏
tmp = CACHE_FILE + ".tmp"
with open(tmp, "w") as f: json.dump(data, f)
os.replace(tmp, CACHE_FILE)
```

### 5.5 用户数据隔离

- 持仓/上传研报默认存 `~/.vibe-research/`（仓库外）
- 旧版 `backend/.cache/` 数据自动迁移
- 重新下载/覆盖更新项目文件夹不会丢失用户数据
- 测试环境通过 `VR_DATA_DIR` 环境变量隔离到临时目录

---

## 六、依赖层次总结

```
裸Python（标准库）: 腾讯行情 + RSS资讯雷达（108源） → 永远可用

+ requests（轻量必装）: 东财全系（研报/公告/资金面/龙虎榜/
                        解禁/板块/两融/大宗/股东/分红/互动易/
                        打板池/成交额榜/行业排名/美港股行情） 
                        → 主力功能

+ akshare（可选增强）: 一致预期/新闻/基本面/市场情绪/板块资金流/
                      历史估值分位/百度股市通
                      → 增强分析

+ mootdx（可选增强）: K线/季报财务快照
                      → 深度技术分析
```

---

## 七、数据源总表

| 序号 | 数据源名称 | 类型 | 获取方式 | 鉴权 | 市场 |
|------|-----------|------|---------|------|------|
| 1 | 腾讯财经 qt.gtimg.cn | HTTP API | urllib GET | 无 | A股 |
| 2 | 东财 reportapi | HTTP API | requests GET | 无 | A股 |
| 3 | 东财 push2/push2delay/push2ex/push2his | HTTP API | requests GET/POST | 无 | A股/美/港 |
| 4 | 东财 datacenter-web | HTTP API | requests GET | 无 | A股/美/港 |
| 5 | 东财 searchapi | HTTP API | requests GET | 无 | A股/美/港 |
| 6 | 东财 np-anotice（公告） | HTTP API | requests GET | 无 | A股 |
| 7 | 东财 emappdata（热门概念） | HTTP API | requests POST | 无 | A股 |
| 8 | 巨潮 cninfo（互动易） | HTTP API | requests POST | 无 | A股 |
| 9 | 通达信行情（mootdx） | TCP协议 | mootdx Python库 | 无 | A股 |
| 10 | 同花顺（akshare封装） | HTTP API | akshare Python库 | 无 | A股 |
| 11 | 百度股市通（akshare封装） | HTTP API | akshare Python库 | 无 | A股 |
| 12 | 乐股网（akshare封装） | HTTP API | akshare Python库 | 无 | A股 |
| 13 | 108个公开RSS/Atom源 | RSS Feed | urllib+XML解析 | 无 | 全球资讯 |

**特点**：全部零鉴权、全部公开源、无需任何API key。

---

## 八、关键工程亮点

1. **开箱即用**：数据源工具包子仓库直接嵌入，`git clone`即用
2. **分级依赖**：核心→增强，未安装增强依赖时优雅降级（501+安装提示）
3. **直连优先+代理降级**：解决科学上网用户访问国内财经站的痛点
4. **内置限流防封**：东财最小间隔1秒+随机抖动
5. **多源降级**：push2→push2delay自动切换
6. **精确代码匹配**：美股/港股搜索防止票据/ETF/窝轮混入
7. **合规红线过滤**：资讯27个关键词白名单过滤
8. **全站共享缓存**：减少数据源压力，空结果不缓存
9. **原子写入**：防止并发写坏缓存
10. **用户数据仓库外存储**：更新项目不丢持仓/研报
11. **测试分两层**：离线契约测试（快、稳）+ 联网冒烟测试（核实上游shape）
