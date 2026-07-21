\-\-\-
name: a-stock-data
description: 当任务需要写代码实际获取A股数据时使用——拉取行情/K线(mootdx+腾讯+百度)、研报(东财+同花顺+iwencai)、信号(热点/北向/龙虎榜/解禁/行业)、资金面(融资融券/大宗/股东户数/分红/资金流)、新闻、财务三表/F10、公告(巨潮)、打板(涨停池/连板/炸板率)、ETF期权(T型报价/希腊字母/IV)、舆情互动(互动易/热榜/人气榜)等真实数据。十层数据源·43端点(含3官方备胎)·内嵌全部可运行代码，自包含零依赖外部文件；优先用通达信(mootdx)/腾讯(不封IP)，东财接口已内置限流防封，主源被封可查「备用源速查」降级。仅在需要调用数据接口取数时使用：A股概念解释、投资观点讨论、策略问答等无需取数的话题不要加载本skill。
origin: custom
version: 3.4.0
\-\-\-

\> 📦 项目主页：https://github.com/simonlin1212/a-stock-data — 更新、反馈、支持作者
>
\> 作者：Simon 林 · 抖音「Simon林」· 公众号「硅基世纪」

\# A股全栈数据工具包 V3.4.0

十层数据架构，43 个端点实测可用（40 主端点 + 3 官方备胎，2026-07 验证），覆盖主板/中小板/科创板/ST。每类数据在「备用源速查」列有独立备胎，主源被封时可降级。

\> \*\*V3.4.0（接口质量 + 备用源韧性，2026-07-11）：\*\*
\> \- \*\*§5.2 财联社快讯复活\*\*：旧 nodeapi 2026-05 下线后，改走官方 \`v1/roll/get\_roll\_list\` + 本地签名（\`sign=md5(sha1(排序query))\`，零 key），V3.2 移除的全市场电报能力恢复，与东财 7×24 互为独立备份。实测 errno=0。
\> \- \\*\\*新增「备用源速查 & 降级策略」章节\\*\\*：十层主源→独立备胎速查表（不同域名/不同风控面）\+ 3 个实测备胎函数——\`dragon\_tiger\_backup()\`（沪深交易所官方龙虎榜，含营业部席位）、\`fund\_flow\_backup()\`（新浪日度资金流）、\`announcements\_backup()\`（深市深交所官方/沪市东财公告+PDF）。端点 40 → 43，数据源 13 → 15（新增沪深交易所官方）。
\> \- \*\*§3.6 解禁字段修复\*\*：东财 \`RPT\_LIFT\_STAGE\` 改列名致 \`type\`/\`shares\` 恒空 → 改 \`FREE\_SHARES\_TYPE\`/\`FREE\_SHARES\`，并新增 \`able\_shares\`（实际可流通股数，更贴近真实抛压）。
\> \- \*\*§3.7 行业排名排序修复\*\*：clist 请求补 \`fid=f3\`，\`top\`/\`bottom\` 现按涨跌幅真实排序（此前缺排序字段，切片结果非涨幅序）。
\> \- \*\*§3.2 深股通标注\*\*：北向盘中披露收紧后 sgt 分钟序列不可靠（hgt 可用），权威北向用 HKEX 官方日统计（见备用源速查）。
\> \- \*\*体验\*\*：顶部新增「端点路由速查」总表（§→函数→用途→源，可按需局部读取）；FAQ 新增东财被封对策 / 财联社复活 / mootdx 库烂尾说明。
>
\> \*\*V3.2.3（行业研报新增）：\*\*
\> \- \*\*§2.1 东财行业研报 \`eastmoney\_industry\_reports()\`\*\*：研报层补上行业研报端点（此前只有个股研报）。与个股研报\*\*同端点\*\* \`reportapi.eastmoney.com/report/list\`，仅 \`qType=1\`；\`industry\_code="\*"\` 拉全行业、传东财行业码（如 \`1238\`=IT服务Ⅱ）精确过滤，PDF 复用 \`download\_pdf()\`，走 \`em\_get\` 限流。端点数 27 → 28。
\> \- 实测（2026-06-20）：全行业 \`hits=47928\`、按行业码 \`1238\` 过滤 \`hits=1863\`，首篇 PDF \`H3\_{infoCode}\_1.pdf\` 下载成功（2.5MB，\`%PDF\` 头）；行业码表端点（\`bxpa\` 等）404 不存在，用 \`"\*"\` 拉取后从结果反查行业码。

\> \*\*V3.2.2（失效接口替换 + 隐藏 Bug 修复）：\*\*
\> \- \*\*§3.3 概念板块归属（#18）\*\*：百度 PAE \`getrelatedblock\` 失效（\`ResultCode 10003\` + 空数组）→ 改用东财 \`slist\`（\`spt=3\`）\`eastmoney\_concept\_blocks()\`，一次请求拿全个股所属板块（行业/概念/地域 + BK码 + 涨跌幅 + 龙头股），零鉴权走 \`em\_get\` 限流。
\> \- \*\*§7.1 巨潮公告 orgId（#19）\*\*：硬编码 \`gssx0{code}\` 致大量 601xxx 股票 \`totalAnnouncement=0\` → 新增 \`\_cninfo\_orgid()\` 动态查官方映射表 \`szse\_stock.json\`（6198 只股，模块级缓存），硬编码降为 fallback。
\> \- \*\*综合示例修复\*\*：示例仍调用 v3.1 已删的 \`baidu\_fund\_flow\_history\` → 改 \`eastmoney\_fund\_flow\_minute\`。
\> \- \*\*§4.5/§5.1 风控说明\*\*：部分大陆住宅 IP 被东财间歇风控（\`HTTP 000\`/空）非代码 Bug，加重试/换网络提示。
\> \- 新代码原样 exec smoke test 实测：板块归属 茅台27/五粮液28/绿的谐波21；公告 平安601318/工行601398 原失效股恢复。
>
\> \*\*V3.2.1（Bug 修复）：\*\* 修复两个内嵌函数的解析逻辑（预先存在，非 V3.2 引入）——
\> \- \*\*§5.1 东财个股新闻\*\*：东财实际返回里 \`result.cmsArticleWebOld\` 直接就是文章列表，旧写法对 list 调 \`.get("list")\` 触发 AttributeError / 返回空 → 改为遍历 \`cmsArticleWebOld\` 列表本身。
\> \- \*\*§6.4 新浪财报三表\*\*：新浪实际结构是 \`result.data.report\_list\`（按报告期为键的 dict，每期 \`data\` 才是行项列表），旧写法取 \`result.data.{lrb}\` 永久返回空 → 改为遍历 \`report\_list\` 期次、从每期 \`data\` 按 \`item\_title\` 提取。
\> \- 两函数均用茅台 600519 公开 API（零 key）实测返回非空、字段正确。
>
\> \*\*V3.2（防封 + 失效修复）：\*\*
\> \- \\*\\*数据源优先级 \+ 东财防封\*\*：明确「通达信(mootdx)/腾讯不封IP 优先用，东财仅用于其独有数据」原则；新增统一节流入口 \`em\_get()\`，所有东财接口内置串行限流（间隔≥1s+随机抖动）+ 会话复用，AI 抄代码即自带防封。详见「数据源优先级 & 东财防封」章节。
\> \- \*\*财联社快讯下线（#14）\*\*：\`cls.cn\` 旧 API 全面 404，标注弃用并改用东财全球资讯。
>
\> \*\*V3.1 修复：\*\* 替换 4 个失效接口（百度 PAE 资金流→东财 push2、大宗交易 RPT 报表名更新、机构席位改用 BUY/SELL 明细筛选）+ 修复东财全球资讯 req\_trace 参数 + 修复巨潮公告 orgId 格式。
>
\> \*\*V3.0 Breaking Change\*\*：彻底移除 akshare 依赖，所有数据源改为直连 HTTP API（零第三方数据依赖，仅 mootdx 保留 TCP）。

\\*\\*使用方式：\\*\\* 将本文件放入 \`~/.claude/skills/a-stock-data/SKILL.md\`，Claude Code 会自动识别并在 A 股相关对话中激活。

\`\`\`
行情层（实时，不封IP）
├── mootdx → K线 + 五档盘口 + 逐笔成交 (TCP 7709)
├── 腾讯财经 API → PE/PB/市值/换手率/涨跌停/指数/ETF (HTTP)
└── 百度股市通 → K线带MA5/10/20 (V3.0 新增，HTTP)

研报层
├── 东财 reportapi → 个股研报 + 行业研报 + PDF下载 + 评级 + 三年EPS
├── 同花顺 THS → 一致预期EPS (直连 basic.10jqka.com.cn)
└── iwencai → NL语义搜索研报 (唯一能力，需X-Claw)

信号层
├── 同花顺热点 → 当日强势股 \+ 题材归因 reason tags (零鉴权 73ms)
├── 同花顺北向 → hgt/sgt 分钟资金流向 + 本地自缓存历史
├── 东财 slist → 个股所属板块/概念归属 (V3.2.2 替换百度PAE)
├── 东财 push2 → 个股资金流向 分钟级 (V3.1 替换百度PAE)
├── 龙虎榜席位 → 上榜记录 \+ 买卖席位 TOP5 + 机构动向 (datacenter-web)
├── 全市场龙虎榜 → 每日全市场上榜股票 \+ 净买额排名 (datacenter-web)
├── 限售解禁日历 → 历史解禁 \+ 未来90天待解禁 (datacenter-web)
└── 行业板块排名 → 东财行业涨跌/上涨下跌家数 (V3.0 替换同花顺)

资金面 / 筹码层
├── 融资融券明细 → 日级融资余额/买入/偿还 \+ 融券 (datacenter-web)
├── 大宗交易 → 成交价/量 \+ 买卖方营业部 (datacenter-web)
├── 股东户数变化 → 季度股东户数 \+ 环比变化 (datacenter-web)
├── 分红送转 → 历史每股派息/送股/转增 (datacenter-web)
└── 个股资金流120日 → 主力/大单/中单/小单 日级净流入 (push2his)

新闻层
├── 东财个股新闻 → 个股相关新闻 (search-api-web JSONP)
├── 财联社快讯 → 全市场实时电报 (v1 API+本地签名零key，✅V3.4 复活)
└── 东财全球资讯 → 7×24 财经快讯 (np-weblist，与财联社互备)

基础数据层
├── mootdx finance → 季报快照 (37字段, EPS/ROE/净利)
├── mootdx F10 → 公司资料 (9大类文本)
├── 东财个股信息 → 行业/总股本/流通股/市值/上市日期 (push2)
└── 新浪财报三表 → 资产负债表/利润表/现金流量表 (quotes.sina.cn)

公告层
├── 巨潮 cninfo → 公告全文检索+下载 (cninfo.com.cn)
└── mootdx F10 → 最新公告摘要

打板层 (V3.3 新增)
├── 东财涨停池 → 连板数/几天几板/封板资金/炸板次数/行业 (push2ex)
├── 东财炸板池 → 涨停后开板 \+ 振幅/涨速 (push2ex)
├── 东财跌停池 → 封单资金/连续跌停/开板次数 (push2ex)
├── 东财昨涨停池 → 昨涨停今表现，算晋级率/赚钱效应 (push2ex)
└── 同花顺涨停揭秘 → 涨停原因题材/封板成功率/板型 (10jqka)

ETF期权层 (V3.3 新增)
├── 合约清单 → 50ETF/300ETF/科创50/500ETF 各月认购认沽 (新浪)
├── T型报价 → 买卖五档/持仓量/行权价/最新价 (新浪)
└── 希腊字母+IV → Delta/Gamma/Theta/Vega/隐含波动率 (新浪)

舆情互动层 (V3.3 新增)
├── 互动易问答 → 投资者提问+公司回复 (巨潮，AI问答独家)
├── 同花顺热榜 → 人气值/概念标签/排名变化 (10jqka)
├── 东财人气榜 → 排名+排名变化+名称价格 (emappdata)
└── 东财概念命中 → 个股被归到哪些概念在炒+热度 (emappdata)
\`\`\`

\## 端点路由速查（按需定位，不必通读全文）

只需一类数据时，按下表定位章节（§）局部读取。除 iwencai 需 API Key 外全部零 key。

\| § \| 函数 \| 拿什么 \| 源 \|
\|---\|------\|--------\|----\|
\| 1.1 \| \`tdx\_client()\` → \`.bars()\` / \`.quotes()\` / \`.transaction()\` \| K线(多周期,不复权) / 五档盘口 / 逐笔成交 \| 通达信 \|
\| 1.2 \| \`tencent\_quote(codes)\` \| 实时价/PE/PB/市值/换手/涨跌停/指数/ETF \| 腾讯 \|
\| 1.3 \| \`baidu\_kline\_with\_ma(code)\` \| 日K线带 MA5/10/20 \| 百度 \|
\| 2.1 \| \`eastmoney\_reports(code)\` / \`download\_pdf(rec)\` \| 个股研报+评级+三年EPS / 研报PDF \| 东财 \|
\| 2.1 \| \`eastmoney\_industry\_reports(industry\_code)\` \| 行业研报 \| 东财 \|
\| 2.2 \| \`ths\_eps\_forecast(code)\` \| 机构一致预期 EPS \| 同花顺 \|
\| 2.3 \| \`iwencai\_search(query)\` / \`iwencai\_query(query)\` \| NL 语义搜研报/选股（需 Key） \| iwencai \|
\| 3.1 \| \`ths\_hot\_reason()\` \| 当日强势股+题材归因 \| 同花顺 \|
\| 3.2 \| \`hsgt\_realtime()\` \| 北向分钟流向（hgt 可用 / sgt 仅参考） \| 同花顺 \|
\| 3.3 \| \`eastmoney\_concept\_blocks(code)\` \| 个股所属板块/概念归属 \| 东财 \|
\| 3.4 \| \`eastmoney\_fund\_flow\_minute(code)\` \| 个股资金流（分钟级） \| 东财 \|
\| 3.5 \| \`dragon\_tiger\_board(code, date)\` \| 个股龙虎榜+买卖席位 TOP5 \| 东财 \|
\| 3.6 \| \`lockup\_expiry(code, date)\` \| 解禁历史+未来90天待解禁 \| 东财 \|
\| 3.7 \| \`industry\_comparison()\` \| 行业板块涨跌排名 \| 东财 \|
\| 3.8 \| \`daily\_dragon\_tiger(date)\` \| 全市场龙虎榜+净买额排名 \| 东财 \|
\| 4.1 \| \`margin\_trading(code)\` \| 融资融券明细 \| 东财 \|
\| 4.2 \| \`block\_trade(code)\` \| 大宗交易+营业部 \| 东财 \|
\| 4.3 \| \`holder\_num\_change(code)\` \| 股东户数变化 \| 东财 \|
\| 4.4 \| \`dividend\_history(code)\` \| 分红送转历史 \| 东财 \|
\| 4.5 \| \`stock\_fund\_flow\_120d(code)\` \| 个股资金流（120日，日级） \| 东财 \|
\| 5.1 \| \`eastmoney\_stock\_news(code)\` \| 个股新闻 \| 东财 \|
\| 5.2 \| \`cls\_telegraph()\` \| 财联社电报（7×24，本地签名零key） \| 财联社 \|
\| 5.3 \| \`eastmoney\_global\_news()\` \| 全球资讯（7×24） \| 东财 \|
\| 6.1 \| \`client.finance(symbol)\` \| 季报快照 37 字段 \| 通达信 \|
\| 6.2 \| \`client.F10(symbol, name)\` \| 公司资料 9 大类文本 \| 通达信 \|
\| 6.3 \| \`eastmoney\_stock\_info(code)\` \| 行业/股本/市值/上市日期 \| 东财 \|
\| 6.4 \| \`sina\_financial\_report(code, type)\` \| 财报三表 \| 新浪 \|
\| 7.1 \| \`cninfo\_announcements(code)\` \| 公告检索+PDF 下载 \| 巨潮 \|
\| 7.2 \| \`client.F10(symbol, name='最新提示')\` \| 最新公告摘要 \| 通达信 \|
\| 8.1 \| \`em\_zt\_pool\` / \`em\_zb\_pool\` / \`em\_dt\_pool\` / \`em\_yzt\_pool\` \| 涨停/炸板/跌停/昨涨停四池 \| 东财 \|
\| 8.2 \| \`ths\_limit\_up\_pool(date)\` \| 涨停原因题材+封板成功率+板型 \| 同花顺 \|
\| 8.3 \| \`limit\_up\_sentiment(date)\` \| 炸板率/连板高度/连板梯队 \| 东财(四池组合) \|
\| 9.1 \| \`sina\_option\_codes\` / \`sina\_option\_tquote\` / \`sina\_option\_greeks\` \| ETF期权合约清单 / T型报价 / 希腊字母+IV \| 新浪 \|
\| 10.1 \| \`cninfo\_irm(code)\` \| 互动易问答（提问+公司回复） \| 巨潮 \|
\| 10.2 \| \`ths\_hot\_list()\` / \`em\_hot\_rank()\` / \`em\_hot\_concept(code)\` \| 热榜/人气榜/概念命中 \| 同花顺+东财 \|
\| 备用源速查 \| \`dragon\_tiger\_backup\` / \`fund\_flow\_backup\` / \`announcements\_backup\` \| 龙虎榜/资金流/公告官方备胎（主源被封时降级） \| 交易所官方+新浪+东财(沪市公告) \|
\| 估值公式 \| \`forward\_pe\` / \`pe\_digestion\` / \`calc\_peg\` / \`full\_valuation(code)\` \| 前向PE / PE消化时间 / PEG / 单票估值全景 \| 本地计算 \|

\## 数据源优先级 & 东财防封（重要，先读）

\### 优先级原则：能用通达信/腾讯，就别用东财

\| 优先级 \| 数据源 \| 协议 \| 封 IP 风险 \| 覆盖 \|
\|--------\|--------\|------\|-----------\|------\|
\| \*\*1（首选）\*\* \| \*\*mootdx（通达信）\*\* \| TCP 7709 二进制 \| \*\*不封 IP\*\* \| K线、五档盘口、逐笔成交、财务快照、F10 \|
\| \*\*2\*\* \| \*\*腾讯财经\*\* \| HTTP GBK \| \*\*不封 IP\*\* \| 实时价、PE/PB/市值/换手率/涨跌停、指数、ETF \|
\| \*\*3\*\* \| 新浪 / 巨潮 / 同花顺 \| HTTP \| 低 \| 财报三表、公告、一致预期/热点 \|
\| \*\*4（仅独有数据才用）\*\* \| \*\*东财 eastmoney\*\* \| HTTP \| \*\*有风控，会封 IP\*\* \| 见下 \|

\*\*凡是行情 / K线 / 实时价 / 市值 / 财务三表能从 mootdx 或腾讯拿到的，一律走它们\*\*——TCP 协议和腾讯接口实测不封 IP，可放心高频调用。

\### 东财只用于它「独有、别处拿不到」的数据

下列数据\*\*只有东财有\*\*，通达信/腾讯/新浪都没有，必须用东财（但要限流）：

\> 龙虎榜席位 · 全市场龙虎榜 · 限售解禁日历 · 融资融券 · 大宗交易 · 股东户数 · 分红送转 · 个股资金流向（分钟/日级）· 行业板块排名 · 研报列表/PDF · 个股新闻 · 全球资讯

\### 东财风控阈值（社区实测，2026-05）

\| 行为 \| 触发封禁的阈值 \| 风险 \|
\|------\|---------------\|------\|
\| 每秒请求数 \| \> 5 次/秒 \| 高 \|
\| 单 IP 并发连接 \| ≥ 10 \| 高 \|
\| 1 分钟请求总数 \| ≥ 200 次 \| 中高 \|
\| 5 分钟请求总数 \| ≥ 300 次 \| 触发封禁 \|
\| User-Agent \| 空 UA / 无浏览器特征 \| 中 \|

被封表现：连续请求后 \`403\` / \`429\` / 连接超时 / 返回空数据。临时封禁通常几分钟到几小时。

\### 防封铁律（调用东财时必须遵守）

1\. \*\*串行，不并发\*\*——绝不对东财开多线程/协程并发请求
2\. \*\*每次间隔 ≥ 1 秒 + 随机抖动\*\*（QPS ≤ 2），批量筛选时调大到 1.5~2 秒
3\. \*\*复用 HTTP 会话\*\*（Keep-Alive），不要每次新建连接
4\. \*\*带正常 UA + Referer\*\*（本 SKILL 各端点已配好）
5\. \*\*批量场景每只股票之间 sleep\*\*——AI 跑批量循环（如筛选 100 只股逐个拉龙虎榜/资金流）是被封的头号元凶

\### 已内置限流：所有东财请求走 \`em\_get()\`

本 SKILL 提供统一的节流入口 \`em\_get()\`（定义见下方「东财数据中心统一查询（共用 helper）」），它自动做到：串行限流（最小间隔 \`EM\_MIN\_INTERVAL=1.0s\` + 随机抖动）+ 复用 \`EM\_SESSION\`（Keep-Alive）+ 默认 UA。\*\*所有 \`eastmoney.com\` 端点的代码块都已改用 \`em\_get\` 而非裸 \`requests.get\`\*\*，AI 直接抄代码即自带防封。批量任务把 \`EM\_MIN\_INTERVAL\` 调大即可进一步降速。

\> 注：\`em\_get\` / \`EM\_SESSION\` / \`EM\_MIN\_INTERVAL\` 是所有东财代码块共用的前置定义，使用任一东财端点前需先执行「共用 helper」代码块。

\-\-\-

\## When to Activate

\- 用户要查 A 股个股估值（一致预期 / PE / PEG / PE消化）
\- 用户要拉实时行情（价格 / 五档盘口 / K线 / 涨跌停价）
\- 用户要搜研报（按主题 / 按标的 / 按行业 / 下载PDF）
\- 用户要看\\*\\*当日强势股 / 题材归因 / 概念热点\\*\\*
\- 用户要看\\*\\*北向资金动向\\*\\*（沪股通/深股通分钟流向）
\- 用户要看\\*\\*概念板块归属\\*\\*（行业/概念/地域）
\- 用户要看\\*\\*个股资金流向\\*\\*（主力/散户/超大单/大单分钟级）
\- 用户要看\\*\\*龙虎榜席位\\*\\*（营业部 \+ 机构买卖）
\- 用户要看\\*\\*全市场龙虎榜\\*\\*（当日所有上榜股票 \+ 净买额排名）
\- 用户要看\\*\\*限售解禁日历\\*\\*（历史解禁 \+ 未来待解禁）
\- 用户要做\\*\\*行业横向对比\\*\\*（涨跌排名 / 资金流入 / 领涨股）
\- 用户要看\\*\\*融资融券 / 两融数据\\*\\*（融资余额 \+ 融券余额）
\- 用户要看\\*\\*大宗交易\\*\\*（成交价/量 \+ 买卖方营业部）
\- 用户要看\\*\\*股东户数变化\\*\\*（筹码集中度）
\- 用户要看\\*\\*分红送转历史\\*\\*（每股派息 \+ 送股 \+ 转增）
\- 用户要看\*\*指数/ETF行情\*\*（上证指数 / 沪深300 / 创业板指 / ETF）
\- 用户要看\\*\\*涨停 / 打板情绪\\*\\*（涨停池 / 连板梯队 / 炸板率 / 跌停 / 涨停原因题材）
\- 用户要看\*\*ETF 期权\*\*（T型报价 / 希腊字母 Delta·Gamma·Theta·Vega / 隐含波动率 IV）
\- 用户要看\\*\\*投资者互动问答\\*\\*（公司如何回应某传闻/利好 · 互动易）
\- 用户要看\\*\\*市场热度 / 人气榜\\*\\*（同花顺热榜 / 东财人气榜 / 个股概念命中）
\- 用户要看新闻资讯（个股新闻 / 财联社快讯 / 全球资讯）
\- 用户要查公告（巨潮公告全文）
\- 用户要做产业链调研 / 批量横向对比
\- 关键词：估值、一致预期、机构预测、市盈率、PEG、市值、研报、产业链、行业研究、K线、盘口、公告、新闻、\*\*强势股、题材、热点、概念归因、北向资金、沪股通、深股通、概念板块、资金流向、主力、龙虎榜、席位、营业部、全市场龙虎榜、净买入、解禁、限售、行业对比、行业轮动、融资融券、两融、大宗交易、股东户数、筹码集中、分红、派息、送股、指数、ETF、涨停、打板、连板、炸板、跌停、涨停原因、封板、晋级率、ETF期权、希腊字母、隐含波动率、互动易、投资者关系、热榜、人气榜、市场热度\*\*

\-\-\-

\## Prerequisites

\`\`\`bash
pip install mootdx requests pandas stockstats
\`\`\`

\| 依赖 \| 版本要求 \| 用途 \|
\|------\|---------\|------\|
\| mootdx \| >= 0.10 \| TCP行情+财务+F10（唯一非HTTP依赖）；0.11.x 用 \`tdx\_client()\` 规避 BESTIP bug，见上节 \|
\| requests \| any \| 所有HTTP API直连 \|
\| pandas \| any \| 数据处理+HTML表格解析 \|
\| stockstats \| any \| 技术指标计算（RSI/MACD/BOLL等） \|

\> \*\*V3.0 架构：\*\* 除 mootdx（TCP 二进制协议）外，所有数据源均为直连 HTTP API，零第三方数据封装依赖。每个端点的底层 URL/参数完全暴露，方便调试和定制。

\### iwencai API Key（仅语义搜索需要）

\`\`\`bash
\# 环境变量方式
export IWENCAI\_API\_KEY="your\_key\_here"
export IWENCAI\_BASE\_URL="https://openapi.iwencai.com"

\# 申请地址: https://www.iwencai.com/skillhub
\# 注册后安装 SkillHub CLI，再安装 report-search 技能即可获得 Key
\`\`\`

其他数据源（mootdx / 腾讯 / 东财 / 同花顺 / 百度股市通 / 新浪 / 巨潮）全部免费，无需 key。

\### mootdx 客户端（必读，规避 0.11.x BESTIP 空串 bug）

\> \*\*已知 bug（mootdx 0.11.x）：\*\* 全新安装后 \`Quotes.factory(market='std')\` 裸调用可能抛 \`ValueError: not enough values to unpack (expected 2, got 0)\`。
\> 根因：\`~/.mootdx/config.json\` 的 \`BESTIP.HQ\` 初始是空字符串 \`""\`（不是缺失键），mootdx 用 \`dict.get(key, default)\` 取不到 default，拆包失败。\*\*老用户（config 曾填充过 IP）不会触发，所以容易漏测。\*\*
\> \\*\\*不要靠锁版本解决：\\*\\* 锁 \`mootdx==0.10.12\` 在部分环境（如干净的 Python 3.9）下 \`import mootdx\` 会因 numpy/pandas 二进制不兼容直接崩。正确做法是用下面的 \`tdx\_client()\`——显式传 server 绕过 BESTIP，对 0.10 / 0.11 都适用。

\*\*统一用以下 helper 创建客户端（所有 mootdx 调用都走它）：\*\*

\`\`\`python
import socket
from mootdx.quotes import Quotes

\# 实测可用的备选服务器（按延迟排序，2026-06 验证）
\_TDX\_SERVERS = \[\
 ('119.97.185.59', 7709), ('124.70.133.119', 7709), ('116.205.183.150', 7709),\
 ('123.60.73.44', 7709), ('116.205.163.254', 7709), ('121.36.225.169', 7709),\
 ('123.60.70.228', 7709), ('124.71.9.153', 7709), ('110.41.147.114', 7709),\
 ('124.71.187.122', 7709),\
\]

def \_probe(ip, port, timeout=2.0):
 """TCP 握手探测，判断服务器是否可达"""
 try:
 with socket.create\_connection((ip, port), timeout=timeout):
 return True
 except Exception:
 return False

def tdx\_client(market='std'):
 """
 创建 mootdx 客户端，规避 0.11.x BESTIP.HQ 空串 bug。
 顺序兜底，保证 IP 列表老化/换网时仍能工作：
 1) 顺序探测 \_TDX\_SERVERS，用第一个 TCP 可达的显式 server；
 2) 全部不可达 → 回退 mootdx 自带 bestip 测速选优；
 3) 再不行 → 回退裸 factory（老用户 config 已有可用 BESTIP 时成立）；
 4) 仍失败 → 抛 RuntimeError，明确报错而非死等。
 """
 for ip, port in \_TDX\_SERVERS:
 if \_probe(ip, port):
 return Quotes.factory(market=market, server=(ip, port))
 try:
 return Quotes.factory(market=market, bestip=True) # fallback 1
 except Exception:
 pass
 try:
 return Quotes.factory(market=market) # fallback 2
 except Exception as e:
 raise RuntimeError(
 "所有 mootdx 服务器均不可达。海外网络通常全部超时（TCP 7709），"
 "请走国内代理或更新 \_TDX\_SERVERS 列表。原始错误：%s" % e
 )

\# 用法：client = tdx\_client() # 替代所有 Quotes.factory(market='std')
\`\`\`

\> \*\*海外 IP 用户：\*\* mootdx 走通达信 TCP 7709，海外环境通常全部超时。\`tdx\_client()\` 会快速失败给出明确报错，而非死等。

\### 市场前缀规则（全局通用）

\`\`\`python
def get\_prefix(code: str) -> str:
 """6位代码 → 市场前缀"""
 if code.startswith(("6", "9")):
 return "sh"
 elif code.startswith("8"):
 return "bj"
 else:
 return "sz"
\`\`\`

\### Ticker 格式归一化

所有接口统一支持多种输入格式，内部归一化为纯 6 位数字：

\| 输入 \| 归一化结果 \|
\|------\|-----------\|
\| \`688017\` \| \`688017\` \|
\| \`SH688017\` / \`sh688017\` \| \`688017\` \|
\| \`688017.SH\` / \`688017.sh\` \| \`688017\` \|
\| \`SZ000001\` \| \`000001\` \|
\| \`BJ832000\` \| \`832000\` \|

\### 东财数据中心统一查询（共用 helper）

龙虎榜/解禁/融资融券/大宗交易/股东户数/分红 共用同一 base URL：

\`\`\`python
import time
import random
import requests

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10\_15\_7) AppleWebKit/537.36"
DATACENTER\_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"

\# ── 东财防封：全局节流 + 会话复用 ────────────────────────────────────
\# 东财系 HTTP 接口（push2 / datacenter / reportapi / search / np-weblist）有风控：
\# 每秒 >5 次 / 单 IP 并发 ≥10 / 1 分钟 ≥200 次 → 临时封 IP。
\# 所有 eastmoney.com 请求一律走 em\_get()：串行限流（最小间隔 + 随机抖动）+ 复用
\# Keep-Alive 会话，批量调用时自动降速，避免被封。详见「数据源优先级 & 东财防封」章节。
EM\_SESSION = requests.Session()
EM\_SESSION.headers.update({"User-Agent": UA})
\# 连接级自动重试：瞬态连接错误 / 429 / 5xx 指数退避重试（住宅IP偶发风控更稳）。
\# 注意：403 不重试（东财风控信号，重试无益反而加重；按下方 EM\_MIN\_INTERVAL 降频应对）。
try:
 from requests.adapters import HTTPAdapter
 from urllib3.util.retry import Retry
 \_em\_adapter = HTTPAdapter(max\_retries=Retry(
 total=3, connect=3, backoff\_factor=0.6,
 status\_forcelist=\[429, 500, 502, 503, 504\], allowed\_methods=\["GET"\]))
 EM\_SESSION.mount("https://", \_em\_adapter)
 EM\_SESSION.mount("http://", \_em\_adapter)
except Exception:
 pass # 老版本 urllib3 缺 allowed\_methods 等参数时降级为无重试，不影响主流程
EM\_MIN\_INTERVAL = 1.0 # 两次东财请求最小间隔(秒)；批量筛选建议调大到 1.5~2
\_em\_last\_call = \[0.0\] # 模块级上次请求时间戳

def em\_get(url: str, params: dict \| None = None, headers: dict \| None = None,
 timeout: int = 15, \*\*kwargs):
 """东财统一请求入口：自动节流 \+ 复用 session + 默认 UA。
 所有 eastmoney.com 接口都应通过它请求，避免高频被封 IP。"""
 wait = EM\_MIN\_INTERVAL - (time.time() - \_em\_last\_call\[0\])
 if wait > 0:
 time.sleep(wait + random.uniform(0.1, 0.5))
 try:
 return EM\_SESSION.get(url, params=params, headers=headers, timeout=timeout, \*\*kwargs)
 finally:
 \_em\_last\_call\[0\] = time.time()

def eastmoney\_datacenter(report\_name: str, columns: str = "ALL",
 filter\_str: str = "", page\_size: int = 50,
 sort\_columns: str = "", sort\_types: str = "-1") -> list\[dict\]:
 """东财数据中心统一查询 — 龙虎榜/解禁/融资融券/大宗交易/股东户数/分红 共用（已内置限流）"""
 params = {
 "reportName": report\_name, "columns": columns,
 "filter": filter\_str, "pageNumber": "1", "pageSize": str(page\_size),
 "sortColumns": sort\_columns, "sortTypes": sort\_types,
 "source": "WEB", "client": "WEB",
 }
 r = em\_get(DATACENTER\_URL, params=params, timeout=15)
 d = r.json()
 if d.get("result") and d\["result"\].get("data"):
 return d\["result"\]\["data"\]
 return \[\]
\`\`\`

\-\-\-

\## Layer 1: 行情层（实时，不封IP）

\### 1.1 mootdx — K线 + 五档盘口 + 逐笔成交

TCP 二进制协议，连通达信服务器(7709)，无需注册，不封IP。

\`\`\`python
from mootdx.quotes import Quotes

client = tdx\_client() # 见 Prerequisites 的 tdx\_client() helper（规避 0.11.x BESTIP bug；等价 Quotes.factory(market='std')）

\# === K线数据 ===
\# ⚠️ 参数名是 frequency（不是 category！传 category 会被 \*\*kwargs 静默吞掉，
\# 永远退化成默认 frequency=9 日线，拿不到分钟数据）。
\# mootdx 0.11.7 实测频率值表：
\# 0=5分钟 1=15分钟 2=30分钟 3=60分钟(1小时) 4=日线 5=周线 6=月线
\# 8=1分钟 9=日线(默认) 10=季线 11=年线 （7=1分钟除权口径,少用）
klines = client.bars(symbol='688017', frequency=9, offset=10) # 日线
min1 = client.bars(symbol='688017', frequency=8, offset=240) # 1分钟（一个交易日≈240根）
min5 = client.bars(symbol='688017', frequency=0, offset=48) # 5分钟
\# 返回: open, close, high, low, vol, amount, datetime
\# ⚠️ 复权：bars 返回【不复权】原始价（通达信原始数据，无 adjust 参数）。
\# 跨除权除息日做估值/回测前需自行复权，或改用带前复权的日K数据源（腾讯财经）。

\# === 实时报价 ===
quotes = client.quotes(symbol=\['688017', '300476'\])
\# 返回 46 个字段:
\# price(现价), open, high, low, last\_close(昨收)
\# bid1~bid5, ask1~ask5, bid\_vol1~bid\_vol5, ask\_vol1~ask\_vol5
\# vol(成交量), amount(成交额), servertime

\# === 逐笔成交（非交易时间返回空）===
trades = client.transaction(symbol='688017', date='20260502')
\# 返回: time, price, vol, num, buyorsell(0买/1卖/2中性)
\`\`\`

\*\*mootdx 不提供 PE / PB / 市值 / 换手率 / 涨跌停价\*\* — 这些走腾讯财经。

\### 1.2 腾讯财经 API — PE/PB/市值/换手率/涨跌停/指数/ETF

HTTP GET，GBK 编码，\`~\` 分隔 88 个字段，不封IP。

\`\`\`python
import urllib.request

def tencent\_quote(codes: list\[str\]) -> dict\[str, dict\]:
 """
 批量拉取腾讯财经实时行情。
 codes: \["688017", "300476", "002463"\]
 也支持指数: \["000001", "000300", "399006"\]
 也支持ETF: \["510050", "510300"\]
 返回: {code: {name, price, pe\_ttm, pb, mcap, ...}}
 """
 prefixed = \[\]
 for c in codes:
 if c.startswith(("6", "9")):
 prefixed.append(f"sh{c}")
 elif c.startswith("8"):
 prefixed.append(f"bj{c}")
 else:
 prefixed.append(f"sz{c}")

 url = "https://qt.gtimg.cn/q=" + ",".join(prefixed)
 req = urllib.request.Request(url)
 req.add\_header("User-Agent", "Mozilla/5.0")
 resp = urllib.request.urlopen(req, timeout=10)
 data = resp.read().decode("gbk")

 result = {}
 for line in data.strip().split(";"):
 if not line.strip() or "=" not in line or '"' not in line:
 continue
 key = line.split("=")\[0\].split("\_")\[-1\]
 vals = line.split('"')\[1\].split("~")
 if len(vals) < 53:
 continue
 code = key\[2:\]
 result\[code\] = {
 "name": vals\[1\],
 "price": float(vals\[3\]) if vals\[3\] else 0,
 "last\_close": float(vals\[4\]) if vals\[4\] else 0,
 "open": float(vals\[5\]) if vals\[5\] else 0,
 "change\_amt": float(vals\[31\]) if vals\[31\] else 0,
 "change\_pct": float(vals\[32\]) if vals\[32\] else 0,
 "high": float(vals\[33\]) if vals\[33\] else 0,
 "low": float(vals\[34\]) if vals\[34\] else 0,
 "amount\_wan": float(vals\[37\]) if vals\[37\] else 0,
 "turnover\_pct": float(vals\[38\]) if vals\[38\] else 0,
 "pe\_ttm": float(vals\[39\]) if vals\[39\] else 0,
 "amplitude\_pct":float(vals\[43\]) if vals\[43\] else 0,
 "mcap\_yi": float(vals\[44\]) if vals\[44\] else 0,
 "float\_mcap\_yi":float(vals\[45\]) if vals\[45\] else 0,
 "pb": float(vals\[46\]) if vals\[46\] else 0,
 "limit\_up": float(vals\[47\]) if vals\[47\] else 0,
 "limit\_down": float(vals\[48\]) if vals\[48\] else 0,
 "vol\_ratio": float(vals\[49\]) if vals\[49\] else 0,
 "pe\_static": float(vals\[52\]) if vals\[52\] else 0,
 }
 return result

\# 用法: 个股
quotes = tencent\_quote(\["688017", "300476", "002463"\])
for code, q in quotes.items():
 print(f"{q\['name'\]}({code}): {q\['price'\]}元 PE={q\['pe\_ttm'\]} PB={q\['pb'\]} 市值={q\['mcap\_yi'\]}亿")

\# 用法: 指数 — sh000001=上证指数, sh000300=沪深300, sz399006=创业板指
index\_quotes = tencent\_quote(\["000001", "000300", "399006"\])

\# 用法: ETF — sh510050=上证50ETF, sh510300=沪深300ETF
etf\_quotes = tencent\_quote(\["510050", "510300"\])
\`\`\`

\#### 腾讯财经字段索引速查（实测校准 2026-05-03）

\| 索引 \| 含义 \| 示例 \|
\|------\|------\|------\|
\| 1 \| 名称 \| 绿的谐波 \|
\| 3 \| 当前价 \| 224.12 \|
\| 4 \| 昨收 \| 215.01 \|
\| 5 \| 今开 \| 214.10 \|
\| 9-18 \| 买一~买五(价+量) \| \|
\| 19-28 \| 卖一~卖五(价+量) \| \|
\| 31 \| 涨跌额 \| 9.11 \|
\| 32 \| 涨跌幅% \| 4.24 \|
\| 33 \| 最高 \| 229.62 \|
\| 34 \| 最低 \| 214.10 \|
\| 37 \| 成交额(万) \| 187040 \|
\| 38 \| 换手率% \| 4.55 \|
\| \*\*39\*\* \| \*\*PE(TTM)\*\* \| 300.45 \|
\| \*\*43\*\* \| \*\*振幅%（不是PB！）\*\* \| 7.22 \|
\| \*\*44\*\* \| \*\*总市值(亿)\*\* \| 410.88 \|
\| \*\*45\*\* \| \*\*流通市值(亿)\*\* \| 410.88 \|
\| \*\*46\*\* \| \*\*PB(市净率)\*\* \| 11.51 \|
\| \*\*47\*\* \| \*\*涨停价\*\* \| 258.01 \|
\| \*\*48\*\* \| \*\*跌停价\*\* \| 172.01 \|
\| 49 \| 量比 \| 1.20 \|
\| \*\*52\*\* \| \*\*PE(静)\*\* \| 314.76 \|

\> \\*\\*踩坑提醒：\\*\\* 网上很多教程把索引 43 写成 PB，实测是振幅%。PB 在索引 46。

\### 1.3 百度股市通 K线 — 带MA5/MA10/MA20（V3.0 新增）

\\*\\*核心价值：\\*\\* 返回时自带均线数据，无需本地计算。

\`\`\`python
import requests

def baidu\_kline\_with\_ma(code: str, start\_time: str = "") -> dict:
 """百度股市通K线 — 独有能力: 返回时自带 ma5/ma10/ma20 均价"""
 url = "https://finance.pae.baidu.com/selfselect/getstockquotation"
 params = {
 "all": "1", "isIndex": "false", "isBk": "false", "isBlock": "false",
 "isFutures": "false", "isStock": "true", "newFormat": "1",
 "group": "quotation\_kline\_ab", "finClientType": "pc",
 "code": code, "start\_time": start\_time, "ktype": "1",
 }
 headers = {
 "User-Agent": "Mozilla/5.0",
 "Accept": "application/vnd.finance-web.v1+json",
 "Origin": "https://gushitong.baidu.com",
 "Referer": "https://gushitong.baidu.com/",
 }
 r = requests.get(url, params=params, headers=headers, timeout=10)
 d = r.json()
 result = d.get("Result", {})
 md = result.get("newMarketData", {})
 keys = md.get("keys", \[\]) # includes: ma5avgprice, ma10avgprice, ma20avgprice
 rows = md.get("marketData", "").split(";")
 return {"keys": keys, "rows": rows}

\# 用法
data = baidu\_kline\_with\_ma("600519")
print("字段:", data\["keys"\]\[:10\])
print("最近5根K线:", data\["rows"\]\[-5:\])
\# keys 包含: time, open, close, high, low, volume, amount, ma5avgprice, ma10avgprice, ma20avgprice 等
\`\`\`

\-\-\-

\## Layer 2: 研报层

\### 2.1 东财研报 API — 研报列表 + PDF下载（主力）

A级接口（公开JSON API），reportapi.eastmoney.com，免费无key。

\`\`\`python
import requests
import re
import time
from pathlib import Path

REPORT\_API = "https://reportapi.eastmoney.com/report/list"
PDF\_TPL = "https://pdf.dfcfw.com/pdf/H3\_{info\_code}\_1.pdf"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10\_15\_7) AppleWebKit/537.36"

def eastmoney\_reports(code: str, max\_pages: int = 5) -> list\[dict\]:
 """拉取指定股票的研报列表"""
 all\_records = \[\]
 for page in range(1, max\_pages + 1):
 params = {
 "industryCode": "\*", "pageSize": "100", "industry": "\*",
 "rating": "\*", "ratingChange": "\*",
 "beginTime": "2000-01-01", "endTime": "2030-01-01",
 "pageNo": str(page), "fields": "", "qType": "0",
 "orgCode": "", "code": code, "rcode": "",
 "p": str(page), "pageNum": str(page), "pageNumber": str(page),
 }
 r = em\_get(REPORT\_API, params=params,
 headers={"Referer": "https://data.eastmoney.com/"}, timeout=30) # 已内置限流
 d = r.json()
 rows = d.get("data") or \[\]
 if not rows:
 break
 all\_records.extend(rows)
 if page >= (d.get("TotalPage", 1) or 1):
 break
 return all\_records

def download\_pdf(record: dict, target\_dir: str = "./reports") -> str \| None:
 """下载单份研报PDF，返回保存路径或None"""
 info\_code = record.get("infoCode", "")
 if not info\_code:
 return None
 date = (record.get("publishDate") or "")\[:10\]
 org = re.sub(r'\[\\\/:\*?"<>\|\]', "\_", record.get("orgSName") or "未知")\[:40\]
 title = re.sub(r'\[\\\/:\*?"<>\|\]', "\_", record.get("title", ""))\[:80\]
 fname = f"{date}\_{org}\_{title}.pdf"
 target = Path(target\_dir) / fname
 if target.exists():
 return str(target)
 url = PDF\_TPL.format(info\_code=info\_code)
 r = em\_get(url, headers={"Referer": "https://data.eastmoney.com/"}, timeout=60)
 if r.status\_code == 200 and len(r.content) >= 1024:
 target.parent.mkdir(parents=True, exist\_ok=True)
 target.write\_bytes(r.content)
 return str(target)
 return None

\# 用法
reports = eastmoney\_reports("688017")
print(f"共 {len(reports)} 篇研报")
for r in reports\[:5\]:
 print(f" {r.get('publishDate','')\[:10\]} \| {r.get('orgSName')} \| {r.get('title','')\[:60\]}")
\`\`\`

\#### 研报 record 关键字段

\| 字段 \| 含义 \|
\|------\|------\|
\| title \| 研报标题 \|
\| publishDate \| 发布日期 \|
\| orgSName \| 机构简称 \|
\| infoCode \| 用于拼 PDF URL \|
\| predictThisYearEps \| 今年EPS预测 \|
\| predictNextYearEps \| 明年EPS预测 \|
\| predictNextTwoYearEps \| 后年EPS预测 \|
\| emRatingName \| 评级(买入/增持/...) \|
\| indvInduName \| 行业分类 \|

\#### 行业研报列表（qType=1）

与个股研报\*\*同一端点\*\*（\`reportapi.eastmoney.com/report/list\`），仅 \`qType\` 不同：\`qType=0\` 个股研报，\`qType=1\` 行业研报。返回 record 可直接喂给上面的 \`download\_pdf()\`（PDF 模板通用）。

\`\`\`python
def eastmoney\_industry\_reports(industry\_code: str = "\*", max\_pages: int = 5,
 begin: str = "2024-01-01") -> list\[dict\]:
 """拉取行业研报列表（qType=1）。
 industry\_code="\*" = 全行业；传东财行业码（如 "1238"=IT服务Ⅱ）= 单行业。
 行业名 / 行业码在每条 record 的 industryName / industryCode 字段。"""
 all\_records = \[\]
 for page in range(1, max\_pages + 1):
 params = {
 "industryCode": industry\_code, "pageSize": "100", "industry": "\*",
 "rating": "\*", "ratingChange": "\*",
 "beginTime": begin, "endTime": "2030-01-01",
 "pageNo": str(page), "fields": "", "qType": "1",
 }
 r = em\_get(REPORT\_API, params=params,
 headers={"Referer": "https://data.eastmoney.com/"}, timeout=30) # 已内置限流
 d = r.json()
 rows = d.get("data") or \[\]
 if not rows:
 break
 all\_records.extend(rows)
 if page >= (d.get("TotalPage", 1) or 1):
 break
 return all\_records

\# 用法
\# 1) 全行业最新研报
reports = eastmoney\_industry\_reports("\*", max\_pages=2)
print(f"共 {len(reports)} 篇行业研报")
for r in reports\[:5\]:
 print(f" {r.get('publishDate','')\[:10\]} \| {r.get('industryName')} \| {r.get('orgSName')} \| {r.get('title','')\[:50\]}")

\# 2) 单行业（IT服务Ⅱ，行业码 1238）+ 下载首篇 PDF（复用 2.1 的 download\_pdf）
it = eastmoney\_industry\_reports("1238", max\_pages=1)
if it:
 download\_pdf(it\[0\])
\`\`\`

行业研报特有/常用字段（其余字段同 2.1 个股研报）：

\| 字段 \| 含义 \|
\|------\|------\|
\| industryName \| 行业名称（如 IT服务Ⅱ、风电设备、光伏设备） \|
\| industryCode \| 东财行业代码（用于 \`industry\_code\` 精确过滤） \|
\| emRatingName \| 行业评级（买入/增持/中性/...） \|
\| reportType \| 报告类型 \|
\| attachPages / attachSize \| PDF 页数 / 大小(KB) \|
\| infoCode \| 喂给 \`download\_pdf()\` 拼 PDF URL \|

\> \\*\\*行业码怎么拿：\\*\\* 东财行业码不是通用记忆码，没有公开的码表端点（\`bxpa\` 等已 404）。常用做法：先用 \`industry\_code="\*"\` 拉一批，从结果的 \`industryName\`/\`industryCode\` 找到目标行业的码，再用该码精确过滤。

\### 2.2 同花顺一致预期EPS（直连 basic.10jqka.com.cn）

\`\`\`python
import requests
import pandas as pd
from io import StringIO

def ths\_eps\_forecast(code: str) -> pd.DataFrame:
 """
 同花顺机构一致预期EPS。
 直连 basic.10jqka.com.cn，解析HTML表格。
 返回 DataFrame: 年度, 预测机构数, 最小值, 均值, 最大值
 "均值" = 机构一致预期EPS
 """
 url = f"https://basic.10jqka.com.cn/new/{code}/worth.html"
 headers = {
 "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10\_15\_7) AppleWebKit/537.36",
 "Referer": "https://basic.10jqka.com.cn/",
 }
 r = requests.get(url, headers=headers, timeout=15)
 r.encoding = "gbk"
 dfs = pd.read\_html(StringIO(r.text))
 # 找含"每股收益"的表格
 for df in dfs:
 cols = \[str(c) for c in df.columns\]
 if any("每股收益" in c or "均值" in c for c in cols):
 return df
 # fallback: 返回第一个表
 return dfs\[0\] if dfs else pd.DataFrame()

\# 用法
df = ths\_eps\_forecast("688017")
print(df)
\# "预测机构数" < 3 的要谨慎
\`\`\`

\### 2.3 iwencai — NL语义搜索研报（唯一能力）

需要 API Key + X-Claw Headers（SkillHub 2.0 强制要求）。

\`\`\`python
import os
import json
import secrets
import requests

IWENCAI\_BASE = os.environ.get("IWENCAI\_BASE\_URL", "https://openapi.iwencai.com")
IWENCAI\_KEY = os.environ.get("IWENCAI\_API\_KEY", "")

def \_claw\_headers(call\_type: str = "normal") -> dict:
 """SkillHub 2.0 必须的 X-Claw 鉴权头"""
 return {
 "X-Claw-Call-Type": call\_type,
 "X-Claw-Skill-Id": "report-search",
 "X-Claw-Skill-Version": "2.0.0",
 "X-Claw-Plugin-Id": "none",
 "X-Claw-Plugin-Version": "none",
 "X-Claw-Trace-Id": secrets.token\_hex(32),
 }

def iwencai\_search(query: str, channel: str = "report", size: int = 50) -> list\[dict\]:
 """
 iwencai 语义搜索。
 channel: "report"(研报) / "announcement"(公告) / "news"(新闻)
 size: 默认10, 实测可调到50（隐藏参数）
 """
 headers = {
 "Authorization": f"Bearer {IWENCAI\_KEY}",
 "Content-Type": "application/json",
 \*\*\_claw\_headers(),
 }
 payload = {
 "channels": \[channel\],
 "app\_id": "AIME\_SKILL",
 "query": query,
 "size": size,
 }
 r = requests.post(
 f"{IWENCAI\_BASE}/v1/comprehensive/search",
 json=payload, headers=headers, timeout=30,
 )
 if r.status\_code != 200:
 raise RuntimeError(f"iwencai HTTP {r.status\_code}: {r.text\[:200\]}")
 data = r.json()
 if data.get("status\_code", 0) != 0:
 raise RuntimeError(f"iwencai error: {data.get('status\_msg', '')}")
 return data.get("data") or \[\]

def iwencai\_query(query: str, page: int = 1, limit: int = 50) -> list\[dict\]:
 """
 iwencai NL数据查询（结构化字段）。
 例: "贵州茅台 ROE" → DataFrame-like rows
 """
 headers = {
 "Authorization": f"Bearer {IWENCAI\_KEY}",
 "Content-Type": "application/json",
 \*\*\_claw\_headers(),
 }
 payload = {
 "query": query,
 "page": str(page),
 "limit": str(limit),
 "is\_cache": "1",
 "expand\_index": "true",
 }
 r = requests.post(
 f"{IWENCAI\_BASE}/v1/query2data",
 json=payload, headers=headers, timeout=30,
 )
 if r.status\_code != 200:
 raise RuntimeError(f"iwencai HTTP {r.status\_code}: {r.text\[:200\]}")
 data = r.json()
 if data.get("status\_code", 0) != 0:
 raise RuntimeError(f"iwencai error: {data.get('status\_msg', '')}")
 return data.get("datas") or \[\]

def dedup\_articles(articles: list\[dict\]) -> list\[dict\]:
 """同一uid仅保留score最高的段落"""
 best = {}
 for a in articles:
 uid = a.get("uid", "") or f"{a.get('title','')}\|{a.get('publish\_date','')}"
 score = float(a.get("score", 0))
 if uid not in best or score > float(best\[uid\].get("score", 0)):
 best\[uid\] = a
 return sorted(best.values(), key=lambda x: x.get("publish\_date", ""), reverse=True)

\# 用法: NL语义搜索研报
articles = iwencai\_search("人形机器人 行星滚柱丝杠 2026", channel="report", size=50)
articles = dedup\_articles(articles)
for a in articles\[:5\]:
 extra = a.get("extra") or {}
 if isinstance(extra, str):
 extra = json.loads(extra)
 print(f"{a.get('publish\_date','')\[:10\]} \| {extra.get('organization','')} \| {a.get('title','')\[:60\]}")
\`\`\`

\*\*iwencai 的唯一价值：\*\* NL 主题搜索。"人形机器人 行星滚柱丝杠" 这种跨主题检索只有 iwencai 能做。按标的搜研报走东财 reportapi 更稳定。

\-\-\-

\## Layer 3: 信号层

\### 3.1 同花顺热点 — 当日强势股 + 题材归因 reason tags（独家）

\\*\\*核心价值：\\*\\* 不只告诉你"哪些走强"，还告诉你\\*\\*"为什么走强"\\*\\* —— 同花顺编辑部人工运营的题材标签。

\`\`\`python
import requests
import pandas as pd

def ths\_hot\_reason(date: str = None) -> pd.DataFrame:
 """
 同花顺当日强势股归因。
 date: 'YYYY-MM-DD' 格式，None=今天
 返回 DataFrame，含每只股票的题材标签 (reason)。

 实测: 73ms 拿到 ~125 只 + 完整字段
 """
 from datetime import date as \_date
 if date is None:
 date = \_date.today().strftime("%Y-%m-%d")

 url = (
 f"http://zx.10jqka.com.cn/event/api/getharden/"
 f"date/{date}/orderby/date/orderway/desc/charset/GBK/"
 )
 headers = {
 "User-Agent": (
 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
 "Chrome/117.0.0.0 Safari/537.36"
 )
 }
 r = requests.get(url, headers=headers, timeout=10)
 data = r.json()
 if data.get("errocode", 0) != 0:
 raise RuntimeError(f"同花顺热点错误: {data.get('errormsg', '')}")

 rows = data.get("data") or \[\]
 df = pd.DataFrame(rows)
 if df.empty:
 return df

 # 字段重命名（中文友好）
 rename\_map = {
 "name": "名称", "code": "代码", "reason": "题材归因",
 "close": "收盘价", "zhangdie": "涨跌额", "zhangfu": "涨幅%",
 "huanshou": "换手率%", "chengjiaoe": "成交额",
 "chengjiaoliang": "成交量", "ddejingliang": "大单净量",
 "market": "市场",
 }
 df = df.rename(columns=rename\_map)
 return df

\# 用法
df = ths\_hot\_reason("2026-05-09")
print(f"当日强势股: {len(df)} 只")
print(df\[\["代码", "名称", "涨幅%", "题材归因"\]\].head(10))
\`\`\`

\#### 同花顺热点字段速查

\| 原字段 \| 中文 \| 说明 \|
\|---\|---\|---\|
\| code \| 代码 \| 6 位股票代码 \|
\| name \| 名称 \| 简称 \|
\| \*\*reason\*\* \| \*\*题材归因\*\* \| \*\*核心字段，人工运营 tags，如"算力租赁+Token工厂+AI政务"\*\* \|
\| zhangfu \| 涨幅% \| 当日涨幅 \|
\| huanshou \| 换手率% \| 当日换手 \|
\| chengjiaoe \| 成交额 \| 元 \|
\| chengjiaoliang \| 成交量 \| 股 \|
\| ddejingliang \| 大单净量 \| 主力净流入指标 \|
\| close \| 收盘价 \| 元 \|
\| zhangdie \| 涨跌额 \| 元 \|
\| market \| 市场 \| 沪/深/北 \|

\### 3.2 同花顺北向资金 — hsgtApi 实时分钟流向 + 本地自缓存历史

\> \*\*⚠️ 深股通实时流向近期不可靠（2026-07 实测）：\*\* 沪股通(hgt)分钟序列完整，但深股通(sgt)
\> 常只回传零星几个点、末值量级异常。根因是北向自 2024-08 起收紧盘中实时披露，非本代码问题。
\> 结论：\*\*hgt 可用于当日情绪，sgt 仅供参考\*\*；要权威北向数据用 HKEX 官方日统计
\> （\`hkex.com.hk/chi/csm/DailyStat/data\_tab\_daily\_YYYYMMDDc.js\`，见文末「备用源速查」）。

\> \\*\\*已知行业性问题：\\*\\* eastmoney 全系北向数据自 2024-08 后净买额字段返回 NaN/0，属上游断供。已改为\*\*本地 CSV 自缓存模式\*\*——每次拉实时数据后自动写入本地 CSV，历史越跑越丰富。

\`\`\`python
import requests
import pandas as pd
from pathlib import Path

HSGT\_HEADERS = {
 "User-Agent": (
 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
 "Chrome/117.0.0.0 Safari/537.36"
 ),
 "Host": "data.hexin.cn",
 "Referer": "https://data.hexin.cn/",
}

def hsgt\_realtime() -> pd.DataFrame:
 """
 沪深股通当日实时分钟流向（含集合竞价 09:10–15:00，262 个时间点）。
 返回字段: time, hgt(沪股通累计净买入), sgt(深股通累计净买入)
 单位: 亿元
 """
 url = "https://data.hexin.cn/market/hsgtApi/method/dayChart/"
 r = requests.get(url, headers=HSGT\_HEADERS, timeout=10)
 d = r.json()
 times = d.get("time", \[\])
 hgt = d.get("hgt", \[\])
 sgt = d.get("sgt", \[\])

 n = len(times)
 return pd.DataFrame({
 "time": times,
 "hgt\_yi": hgt\[:n\] + \[None\] \* (n - len(hgt)),
 "sgt\_yi": sgt\[:n\] + \[None\] \* (n - len(sgt)),
 })

\# === 自缓存辅助函数 ===

def \_northbound\_cache\_path() -> Path:
 """北向资金本地 CSV 缓存路径"""
 p = Path.home() / ".tradingagents" / "cache" / "northbound\_daily.csv"
 p.parent.mkdir(parents=True, exist\_ok=True)
 return p

def \_save\_northbound\_snapshot(date: str, hgt: float, sgt: float):
 """写入/更新当天北向收盘数据到 CSV"""
 path = \_northbound\_cache\_path()
 rows = {}
 if path.exists():
 for line in path.read\_text().strip().split("\\n")\[1:\]:
 parts = line.split(",")
 if len(parts) == 3:
 rows\[parts\[0\]\] = line
 rows\[date\] = f"{date},{hgt},{sgt}"
 with open(path, "w") as f:
 f.write("date,hgt,sgt\\n")
 for d in sorted(rows.keys()):
 f.write(rows\[d\] + "\\n")

def \_load\_northbound\_history(n: int = 20) -> pd.DataFrame:
 """读取最近 N 天北向历史"""
 path = \_northbound\_cache\_path()
 if not path.exists():
 return pd.DataFrame()
 df = pd.read\_csv(path)
 return df.tail(n)

\# 用法 1: 实时分钟流向
df = hsgt\_realtime()
print(f"分钟点数: {len(df)}")
print(df.tail(5))

\# 用法 2: 自动缓存今日收盘数据
if not df.empty:
 last = df.dropna().iloc\[-1\]
 \_save\_northbound\_snapshot("2026-05-17", last\["hgt\_yi"\], last\["sgt\_yi"\])

\# 用法 3: 读取历史
hist = \_load\_northbound\_history(20)
print(hist)
\`\`\`

\### 3.3 东财 slist — 个股所属板块/概念归属（V3.2.2 替换百度）

\\*\\*核心价值：\\*\\* 一次调用拿到个股所属的全部板块（行业 \+ 概念 \+ 地域混合），含板块代码（BK码）、当日涨跌幅、板块龙头股。题材归因、板块联动分析必备。

\> \*\*V3.2.2 替换说明：\*\* 百度 PAE \`getrelatedblock\` 接口已失效（实测返回 \`ResultCode 10003\` + 空数组，#18），改用东财 \`slist\` 个股所属板块接口（\`spt=3\`，一次请求拿全，零鉴权）。东财把行业/概念/地域混在\*\*一个列表\*\*里返回，板块名本身已自解释（如「食品饮料」是行业、「贵州板块」是地域、「酿酒概念」是概念），AI 直接用板块名做题材归因即可。

\`\`\`python
def eastmoney\_concept\_blocks(code: str) -> dict:
 """
 个股所属板块/概念归属（东财 slist，一次请求拿全，已内置限流）。
 返回: {total, boards: \[{name, code(BK码), change\_pct, lead\_stock}\], concept\_tags: \[板块名...\]}
 boards 混合 行业/概念/地域，板块名自解释；concept\_tags 是所有板块名的便捷列表。
 """
 market\_code = 1 if code.startswith("6") else 0
 params = {
 "fltt": "2", "invt": "2",
 "secid": f"{market\_code}.{code}",
 "spt": "3", "pi": "0", "pz": "200", "po": "1",
 "fields": "f12,f14,f3,f128",
 }
 headers = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
 try:
 r = em\_get("https://push2.eastmoney.com/api/qt/slist/get",
 params=params, headers=headers, timeout=15)
 d = r.json()
 except Exception as e:
 print(f"\[WARN\] 东财板块归属请求失败: {e}")
 return {"total": 0, "boards": \[\], "concept\_tags": \[\]}

 diff = (d.get("data") or {}).get("diff") or {}
 items = diff.values() if isinstance(diff, dict) else diff
 boards = \[\]
 for it in items:
 boards.append({
 "name": it.get("f14", ""), # 板块名
 "code": it.get("f12", ""), # BK 板块代码
 "change\_pct": it.get("f3", ""), # 板块当日涨跌幅
 "lead\_stock": it.get("f128", ""), # 板块龙头股
 })
 return {
 "total": len(boards),
 "boards": boards,
 "concept\_tags": \[b\["name"\] for b in boards\],
 }

\# 用法
blocks = eastmoney\_concept\_blocks("600519")
print(f"共 {blocks\['total'\]} 个板块")
print("板块归属:", blocks\["concept\_tags"\])
\# → \['食品饮料', '白酒Ⅲ', '白酒Ⅱ', '贵州板块', '酿酒概念', 'HS300\_', ...\]
\`\`\`

\> \\*\\*注意：\\*\\* 东财不区分行业/概念/地域类型（混在一个列表返回）。如需精确分类可按板块名判断，或另查全市场板块清单（\`clist\` + \`m:90+t:1/2/3\`）——但后者每次需多发请求、大页易触发风控，不推荐在批量场景用。

\### 3.4 东财 push2 — 个股资金流向（分钟级）

盘中实时分钟级资金流（主力/大单/中单/小单/超大单净流入）。

\> \*\*V3.1 替换说明：\*\* 百度 PAE \`fundflow\` 和 \`fundsortlist\` 接口已于 2026-05 下线（返回 null），改用东财 push2 资金流 API。日级资金流见 Layer 4.5 \`stock\_fund\_flow\_120d()\`。

\`\`\`python
import requests

def eastmoney\_fund\_flow\_minute(code: str) -> list\[dict\]:
 """
 个股资金流向（分钟级，当日盘中）。
 code: 6位股票代码
 返回: \[{time, main\_net, small\_net, mid\_net, large\_net, super\_net}, ...\]
 单位: 元
 """
 secid = f"1.{code}" if code.startswith("6") else f"0.{code}"
 url = "https://push2.eastmoney.com/api/qt/stock/fflow/kline/get"
 params = {
 "secid": secid, "klt": 1,
 "fields1": "f1,f2,f3,f7",
 "fields2": "f51,f52,f53,f54,f55,f56,f57",
 }
 headers = {
 "User-Agent": UA,
 "Referer": "https://quote.eastmoney.com/",
 "Origin": "https://quote.eastmoney.com",
 }
 try:
 r = em\_get(url, params=params, headers=headers, timeout=10)
 d = r.json()
 except Exception as e:
 print(f"\[WARN\] push2 资金流请求失败: {e}")
 return \[\]

 rows = \[\]
 for line in d.get("data", {}).get("klines", \[\]):
 parts = line.split(",")
 if len(parts) >= 6:
 rows.append({
 "time": parts\[0\],
 "main\_net": float(parts\[1\]),
 "small\_net": float(parts\[2\]),
 "mid\_net": float(parts\[3\]),
 "large\_net": float(parts\[4\]),
 "super\_net": float(parts\[5\]),
 })
 return rows

\# 用法: 分钟级实时资金流
realtime = eastmoney\_fund\_flow\_minute("000858")
if realtime:
 last = realtime\[-1\]
 signal = "bullish" if last\["main\_net"\] > 0 else "bearish"
 print(f"主力净流入: {last\['main\_net'\]:.0f}元 → {signal}")
 # 统计全天主力净流入
 total = sum(r\["main\_net"\] for r in realtime)
 print(f"全天主力累计: {total/1e4:.0f}万元")
\`\`\`

\> \\*\\*注意：\\*\\* push2 资金流金额单位是\*\*元\*\*（非万元），使用时注意换算。\`klt=1\` 分钟级，\`klt=101\` 日级。

\### 3.5 龙虎榜席位 — 个股上榜记录 + 买卖席位 TOP5 + 机构动向

直连东财 datacenter API，不依赖第三方封装。

\`\`\`python
import requests
from datetime import datetime, timedelta

def dragon\_tiger\_board(code: str, trade\_date: str, look\_back: int = 30) -> dict:
 """
 龙虎榜数据聚合。
 trade\_date: YYYY-MM-DD
 look\_back: 回看天数
 返回: {records: \[...\], seats: {buy: \[...\], sell: \[...\]}, institution: {...}}
 """
 start = datetime.strptime(trade\_date, "%Y-%m-%d") - timedelta(days=look\_back)
 start\_str = start.strftime("%Y-%m-%d")

 # 1\. 上榜记录
 records = \[\]
 data = eastmoney\_datacenter(
 "RPT\_DAILYBILLBOARD\_DETAILSNEW",
 filter\_str=f"(TRADE\_DATE>='{start\_str}')(TRADE\_DATE<='{trade\_date}')(SECURITY\_CODE=\\"{code}\\")",
 page\_size=50,
 sort\_columns="TRADE\_DATE", sort\_types="-1",
 )
 for row in data:
 records.append({
 "date": str(row.get("TRADE\_DATE", ""))\[:10\],
 "reason": row.get("EXPLANATION", ""),
 "net\_buy": round((row.get("BILLBOARD\_NET\_AMT") or 0) / 10000, 1),
 "turnover": round(float(row.get("TURNOVERRATE") or 0), 2),
 })

 # 2\. 最近上榜的买卖席位
 seats = {"buy": \[\], "sell": \[\]}
 if records:
 latest\_date = records\[0\]\["date"\]
 # 买入席位
 buy\_data = eastmoney\_datacenter(
 "RPT\_BILLBOARD\_DAILYDETAILSBUY",
 filter\_str=f"(TRADE\_DATE='{latest\_date}')(SECURITY\_CODE=\\"{code}\\")",
 page\_size=10,
 sort\_columns="BUY", sort\_types="-1",
 )
 for row in buy\_data\[:5\]:
 seats\["buy"\].append({
 "name": row.get("OPERATEDEPT\_NAME", ""),
 "buy\_amt": round((row.get("BUY") or 0) / 10000, 1),
 "sell\_amt": round((row.get("SELL") or 0) / 10000, 1),
 "net": round((row.get("NET") or 0) / 10000, 1),
 })
 # 卖出席位
 sell\_data = eastmoney\_datacenter(
 "RPT\_BILLBOARD\_DAILYDETAILSSELL",
 filter\_str=f"(TRADE\_DATE='{latest\_date}')(SECURITY\_CODE=\\"{code}\\")",
 page\_size=10,
 sort\_columns="SELL", sort\_types="-1",
 )
 for row in sell\_data\[:5\]:
 seats\["sell"\].append({
 "name": row.get("OPERATEDEPT\_NAME", ""),
 "buy\_amt": round((row.get("BUY") or 0) / 10000, 1),
 "sell\_amt": round((row.get("SELL") or 0) / 10000, 1),
 "net": round((row.get("NET") or 0) / 10000, 1),
 })

 # 3\. 机构买卖统计（从买卖席位明细中筛选 OPERATEDEPT\_CODE="0" 即机构专用席位）
 institution = {"buy\_amt": 0, "sell\_amt": 0, "net\_amt": 0}
 for detail\_data, side in \[(buy\_data, "buy"), (sell\_data, "sell")\]:
 for row in detail\_data:
 if str(row.get("OPERATEDEPT\_CODE", "")) == "0":
 amt = (row.get("BUY") or 0) if side == "buy" else (row.get("SELL") or 0)
 if side == "buy":
 institution\["buy\_amt"\] += amt
 else:
 institution\["sell\_amt"\] += amt
 institution\["buy\_amt"\] = round(institution\["buy\_amt"\] / 10000, 1)
 institution\["sell\_amt"\] = round(institution\["sell\_amt"\] / 10000, 1)
 institution\["net\_amt"\] = round(institution\["buy\_amt"\] - institution\["sell\_amt"\], 1)

 return {"records": records, "seats": seats, "institution": institution}

\# 用法
data = dragon\_tiger\_board("002475", "2026-05-17")
print(f"近30日上榜 {len(data\['records'\])} 次")
for r in data\["records"\]:
 print(f" {r\['date'\]}: {r\['reason'\]}")
if data\["seats"\]\["buy"\]:
 print("买入席位 TOP5:")
 for s in data\["seats"\]\["buy"\]:
 print(f" {s\['name'\]}: 买{s\['buy\_amt'\]}万 卖{s\['sell\_amt'\]}万 净{s\['net'\]}万")
\`\`\`

\> \*\*ST 股注意：\*\* 5% 涨跌停更容易触发龙虎榜（"连续三日偏离值累计达12%"），科创板 20% 涨跌停则较少触发。

\### 3.6 限售解禁日历 — 历史解禁 + 未来 90 天待解禁

\`\`\`python
from datetime import datetime, timedelta

def lockup\_expiry(code: str, trade\_date: str, forward\_days: int = 90) -> dict:
 """
 限售解禁日历。
 返回: {history: \[...\], upcoming: \[...\]}
 """
 # 1\. 历史解禁记录
 history\_data = eastmoney\_datacenter(
 "RPT\_LIFT\_STAGE",
 filter\_str=f"(SECURITY\_CODE=\\"{code}\\")",
 page\_size=15,
 sort\_columns="FREE\_DATE", sort\_types="-1",
 )
 history = \[\]
 for row in history\_data:
 history.append({
 "date": str(row.get("FREE\_DATE", ""))\[:10\],
 "type": row.get("FREE\_SHARES\_TYPE", ""), # 解禁类型(东财2026改列名, 旧LIMITED\_STOCK\_TYPE已废)
 "shares": row.get("FREE\_SHARES", 0), # 本次解禁股数(万股)
 "able\_shares": row.get("ABLE\_FREE\_SHARES", 0), # 实际可流通股数(万股, 更贴近真实抛压)
 "ratio": row.get("FREE\_RATIO", 0), # 占总股本比(小数, ×100 得百分比)
 })

 # 2\. 未来待解禁
 end\_date = datetime.strptime(trade\_date, "%Y-%m-%d") + timedelta(days=forward\_days)
 end\_str = end\_date.strftime("%Y-%m-%d")
 upcoming\_data = eastmoney\_datacenter(
 "RPT\_LIFT\_STAGE",
 filter\_str=f"(SECURITY\_CODE=\\"{code}\\")(FREE\_DATE>='{trade\_date}')(FREE\_DATE<='{end\_str}')",
 page\_size=20,
 sort\_columns="FREE\_DATE", sort\_types="1",
 )
 upcoming = \[\]
 for row in upcoming\_data:
 upcoming.append({
 "date": str(row.get("FREE\_DATE", ""))\[:10\],
 "type": row.get("FREE\_SHARES\_TYPE", ""), # 解禁类型(东财2026改列名, 旧LIMITED\_STOCK\_TYPE已废)
 "shares": row.get("FREE\_SHARES", 0), # 本次解禁股数(万股)
 "able\_shares": row.get("ABLE\_FREE\_SHARES", 0), # 实际可流通股数(万股, 更贴近真实抛压)
 "ratio": row.get("FREE\_RATIO", 0), # 占总股本比(小数, ×100 得百分比)
 })

 return {"history": history, "upcoming": upcoming}

\# 用法
data = lockup\_expiry("002475", "2026-05-17")
print(f"历史解禁 {len(data\['history'\])} 批")
for h in data\["history"\]\[:5\]:
 print(f" {h\['date'\]}: {h\['type'\]} 数量={h\['shares'\]}")
if data\["upcoming"\]:
 print(f"未来90天待解禁 {len(data\['upcoming'\])} 批")
else:
 print("未来90天无待解禁")
\`\`\`

\\*\\*限售股类型参考：\\*\\*
\- 首发原股东限售股份（IPO 后 1-3 年）
\- 首发机构配售股份（IPO 战略配售）
\- 定向增发机构配售股份（6-18 个月）
\- 股权激励限售股份

\### 3.7 行业板块排名（V3.0 改用东财 — 同花顺加了反爬401）

东财行业板块涨跌幅排名，一次调用看全市场行业轮动。

\`\`\`python
import requests

def industry\_comparison(top\_n: int = 20) -> dict:
 """
 全行业涨跌幅排名（东财行业板块，~100 个行业）。
 返回: {top: \[...\], bottom: \[...\], total: int}
 """
 url = "https://push2.eastmoney.com/api/qt/clist/get"
 params = {
 "pn": "1", "pz": "100", "po": "1", "np": "1",
 "fltt": "2", "invt": "2", "fid": "f3", # fid=f3 + po=1：按涨跌幅降序（缺 fid 时 top/bottom 切片非按涨幅排）
 "fs": "m:90+t:2",
 "fields": "f2,f3,f4,f12,f13,f14,f104,f105,f128,f136,f140,f141,f207",
 }
 headers = {"User-Agent": UA}
 r = em\_get(url, params=params, headers=headers, timeout=15)
 d = r.json()
 items = d.get("data", {}).get("diff", \[\])
 if not items:
 return {"top": \[\], "bottom": \[\], "total": 0}

 rows = \[\]
 for i, item in enumerate(items):
 rows.append({
 "rank": i + 1,
 "name": item.get("f14", ""),
 "change\_pct": item.get("f3", 0),
 "code": item.get("f12", ""),
 "up\_count": item.get("f104", 0),
 "down\_count": item.get("f105", 0),
 "leader": item.get("f140", ""),
 "leader\_change": item.get("f136", 0),
 })

 return {
 "top": rows\[:top\_n\],
 "bottom": rows\[-top\_n:\],
 "total": len(rows),
 }

\# 用法
data = industry\_comparison(20)
print(f"共 {data\['total'\]} 个行业")
print("\\nTOP 10 涨幅:")
for r in data\["top"\]\[:10\]:
 print(f" {r\['rank'\]}. {r\['name'\]}: {r\['change\_pct'\]}% 涨{r\['up\_count'\]}跌{r\['down\_count'\]} 领涨{r\['leader'\]}")
print("\\nBOTTOM 5 跌幅:")
for r in data\["bottom"\]\[-5:\]:
 print(f" {r\['rank'\]}. {r\['name'\]}: {r\['change\_pct'\]}%")
\`\`\`

\### 3.8 全市场龙虎榜

每日全市场龙虎榜汇总——当日所有触发龙虎榜的股票 \+ 上榜原因 \+ 买卖净额 \+ 换手率。

\`\`\`python
from datetime import datetime

def daily\_dragon\_tiger(trade\_date: str = None, min\_net\_buy: float = None) -> dict:
 """
 全市场龙虎榜。
 trade\_date: YYYY-MM-DD（默认当日）
 min\_net\_buy: 净买入下限（万元），None 不过滤
 返回: {date, total\_records, stocks: \[{code, name, reason, close, change\_pct,\
 net\_buy\_wan, buy\_wan, sell\_wan, turnover\_pct}\]}
 """
 if trade\_date is None:
 trade\_date = datetime.now().strftime("%Y-%m-%d")

 data = eastmoney\_datacenter(
 "RPT\_DAILYBILLBOARD\_DETAILSNEW",
 filter\_str=f"(TRADE\_DATE>='{trade\_date}')(TRADE\_DATE<='{trade\_date}')",
 page\_size=500,
 sort\_columns="BILLBOARD\_NET\_AMT", sort\_types="-1",
 )
 if not data:
 return {"date": trade\_date, "total\_records": 0, "stocks": \[\],
 "note": "无数据（非交易日或盘后未更新）"}

 actual\_date = str(data\[0\].get("TRADE\_DATE", ""))\[:10\] if data else trade\_date
 stocks = \[\]
 for row in data:
 net\_buy = (row.get("BILLBOARD\_NET\_AMT") or 0) / 10000
 if min\_net\_buy is not None and net\_buy < min\_net\_buy:
 continue
 stocks.append({
 "code": row.get("SECURITY\_CODE", ""),
 "name": row.get("SECURITY\_NAME\_ABBR", ""),
 "reason": row.get("EXPLANATION", ""),
 "close": row.get("CLOSE\_PRICE") or 0,
 "change\_pct": round(float(row.get("CHANGE\_RATE") or 0), 2),
 "net\_buy\_wan": round(net\_buy, 1),
 "buy\_wan": round((row.get("BILLBOARD\_BUY\_AMT") or 0) / 10000, 1),
 "sell\_wan": round((row.get("BILLBOARD\_SELL\_AMT") or 0) / 10000, 1),
 "turnover\_pct": round(float(row.get("TURNOVERRATE") or 0), 2),
 })
 return {"date": actual\_date, "total\_records": len(stocks), "stocks": stocks}

\# 用法
data = daily\_dragon\_tiger("2026-05-16")
print(f"{data\['date'\]} 龙虎榜共 {data\['total\_records'\]} 条记录")
for s in data\["stocks"\]\[:10\]:
 print(f" {s\['code'\]} {s\['name'\]}: {s\['reason'\]} \| 净买{s\['net\_buy\_wan'\]}万 涨跌{s\['change\_pct'\]}%")

\# 只看净买入 \> 5000 万的
data = daily\_dragon\_tiger("2026-05-16", min\_net\_buy=5000)
print(f"\\n净买入 > 5000万: {data\['total\_records'\]} 条")
\`\`\`

\### 3.9 信号层组合用法：题材热度 + 资金验证

\`\`\`python
\# 拉当日强势股 reason
df\_hot = ths\_hot\_reason()

\# 词频统计 reason 列里的题材关键词
from collections import Counter
all\_tags = \[\]
for r in df\_hot\["题材归因"\].dropna():
 tags = \[t.strip() for t in str(r).split("+") if t.strip()\]
 all\_tags.extend(tags)

cnt = Counter(all\_tags)
print("当日 TOP 10 题材热度:")
for tag, n in cnt.most\_common(10):
 print(f" {tag}: {n} 只")

\# 同时拉北向当日流向，看资金流方向是否对应题材
df\_north = hsgt\_realtime()
hgt\_close = df\_north\["hgt\_yi"\].dropna().iloc\[-1\] if not df\_north.empty else 0
sgt\_close = df\_north\["sgt\_yi"\].dropna().iloc\[-1\] if not df\_north.empty else 0
print(f"\\n北向收盘累计: 沪股通 {hgt\_close} 亿 / 深股通 {sgt\_close} 亿")

\# V3.0: 叠加行业对比，看哪些行业资金在流入
comp = industry\_comparison(10)
print("\\n行业涨幅 TOP 5:")
for r in comp\["top"\]\[:5\]:
 print(f" {r\['name'\]}: {r\['change\_pct'\]}% 涨{r\['up\_count'\]}跌{r\['down\_count'\]}")
\`\`\`

\-\-\-

\## Layer 4: 资金面 / 筹码层（V3.0 新增）

\### 4.1 融资融券明细

\`\`\`python
def margin\_trading(code: str, page\_size: int = 30) -> list\[dict\]:
 """
 融资融券明细（日级）。
 返回: \[{date, rzye(融资余额), rzmre(融资买入), rqye(融券余额), ...}\]
 """
 data = eastmoney\_datacenter(
 "RPTA\_WEB\_RZRQ\_GGMX",
 filter\_str=f'(SCODE="{code}")',
 page\_size=page\_size,
 sort\_columns="DATE", sort\_types="-1",
 )
 rows = \[\]
 for row in data:
 rows.append({
 "date": str(row.get("DATE", ""))\[:10\],
 "rzye": row.get("RZYE", 0), # 融资余额(元)
 "rzmre": row.get("RZMRE", 0), # 融资买入额
 "rzche": row.get("RZCHE", 0), # 融资偿还额
 "rqye": row.get("RQYE", 0), # 融券余额(元)
 "rqmcl": row.get("RQMCL", 0), # 融券卖出量
 "rqchl": row.get("RQCHL", 0), # 融券偿还量
 "rzrqye": row.get("RZRQYE", 0), # 融资融券余额合计
 })
 return rows

\# 用法
data = margin\_trading("600519")
for d in data\[:5\]:
 print(f"{d\['date'\]}: 融资余额={d\['rzye'\]/1e8:.2f}亿 融券余额={d\['rqye'\]/1e8:.2f}亿")
\`\`\`

\### 4.2 大宗交易

\`\`\`python
def block\_trade(code: str, page\_size: int = 20) -> list\[dict\]:
 """
 大宗交易记录。
 返回: \[{date, price, vol, amount, buyer, seller, premium\_pct}\]
 """
 data = eastmoney\_datacenter(
 "RPT\_DATA\_BLOCKTRADE",
 filter\_str=f'(SECURITY\_CODE="{code}")',
 page\_size=page\_size,
 sort\_columns="TRADE\_DATE", sort\_types="-1",
 )
 rows = \[\]
 for row in data:
 close = row.get("CLOSE\_PRICE") or 0
 deal\_price = row.get("DEAL\_PRICE") or 0
 premium = ((deal\_price / close - 1) \* 100) if close else 0
 rows.append({
 "date": str(row.get("TRADE\_DATE", ""))\[:10\],
 "price": deal\_price,
 "close": close,
 "premium\_pct": round(premium, 2),
 "vol": row.get("DEAL\_VOLUME", 0),
 "amount": row.get("DEAL\_AMT", 0),
 "buyer": row.get("BUYER\_NAME", ""),
 "seller": row.get("SELLER\_NAME", ""),
 })
 return rows

\# 用法
data = block\_trade("600519")
for d in data\[:5\]:
 print(f"{d\['date'\]}: 价格={d\['price'\]} 溢价={d\['premium\_pct'\]}% 买方={d\['buyer'\]}")
\`\`\`

\### 4.3 股东户数变化

\`\`\`python
def holder\_num\_change(code: str, page\_size: int = 10) -> list\[dict\]:
 """
 股东户数变化（季度级）。
 返回: \[{date, holder\_num, change\_num, change\_ratio, avg\_shares}\]
 """
 data = eastmoney\_datacenter(
 "RPT\_HOLDERNUMLATEST",
 filter\_str=f'(SECURITY\_CODE="{code}")',
 page\_size=page\_size,
 sort\_columns="END\_DATE", sort\_types="-1",
 )
 rows = \[\]
 for row in data:
 rows.append({
 "date": str(row.get("END\_DATE", ""))\[:10\],
 "holder\_num": row.get("HOLDER\_NUM", 0),
 "change\_num": row.get("HOLDER\_NUM\_CHANGE", 0),
 "change\_ratio": row.get("HOLDER\_NUM\_RATIO", 0), # 环比%
 "avg\_shares": row.get("AVG\_FREE\_SHARES", 0), # 户均持股
 })
 return rows

\# 用法
data = holder\_num\_change("600519")
for d in data\[:5\]:
 print(f"{d\['date'\]}: 股东数={d\['holder\_num'\]} 变化={d\['change\_ratio'\]}% 户均={d\['avg\_shares'\]}")
\# 股东户数持续减少 = 筹码集中 = 主力吸筹信号
\`\`\`

\### 4.4 分红送转历史

\`\`\`python
def dividend\_history(code: str, page\_size: int = 20) -> list\[dict\]:
 """
 分红送转历史。
 返回: \[{date, bonus\_rmb(每股派息), transfer\_ratio(转增比例), bonus\_ratio(送股比例)}\]
 """
 data = eastmoney\_datacenter(
 "RPT\_SHAREBONUS\_DET",
 filter\_str=f'(SECURITY\_CODE="{code}")',
 page\_size=page\_size,
 sort\_columns="EX\_DIVIDEND\_DATE", sort\_types="-1",
 )
 rows = \[\]
 for row in data:
 rows.append({
 "date": str(row.get("EX\_DIVIDEND\_DATE", ""))\[:10\],
 "bonus\_rmb": row.get("PRETAX\_BONUS\_RMB", 0), # 每股派息(税前)
 "transfer\_ratio": row.get("TRANSFER\_RATIO", 0), # 每10股转增
 "bonus\_ratio": row.get("BONUS\_RATIO", 0), # 每10股送股
 "plan": row.get("ASSIGN\_PROGRESS", ""), # 进度
 })
 return rows

\# 用法
data = dividend\_history("600519")
for d in data\[:5\]:
 print(f"{d\['date'\]}: 每股派息={d\['bonus\_rmb'\]}元 转增={d\['transfer\_ratio'\]} 送={d\['bonus\_ratio'\]}")
\`\`\`

\### 4.5 个股资金流（120日，日级）

\`\`\`python
import requests

def stock\_fund\_flow\_120d(code: str) -> list\[dict\]:
 """
 个股资金流（日级，最近120个交易日）。
 返回: \[{date, main\_net(主力净流入), small\_net, mid\_net, large\_net, super\_net}\]
 单位: 元
 """
 market\_code = 1 if code.startswith("6") else 0
 url = "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
 params = {
 "secid": f"{market\_code}.{code}",
 "fields1": "f1,f2,f3,f7",
 "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65",
 "lmt": "120",
 }
 headers = {
 "User-Agent": UA,
 "Referer": "https://quote.eastmoney.com/",
 "Origin": "https://quote.eastmoney.com",
 }
 try:
 r = em\_get(url, params=params, headers=headers, timeout=15)
 d = r.json()
 except Exception as e:
 print(f"\[WARN\] push2 资金流请求失败: {e}")
 return \[\]
 klines = d.get("data", {}).get("klines", \[\])

 rows = \[\]
 for line in klines:
 parts = line.split(",")
 if len(parts) >= 7:
 rows.append({
 "date": parts\[0\],
 "main\_net": float(parts\[1\]) if parts\[1\] != "-" else 0,
 "small\_net": float(parts\[2\]) if parts\[2\] != "-" else 0,
 "mid\_net": float(parts\[3\]) if parts\[3\] != "-" else 0,
 "large\_net": float(parts\[4\]) if parts\[4\] != "-" else 0,
 "super\_net": float(parts\[5\]) if parts\[5\] != "-" else 0,
 })
 return rows

\# 用法
data = stock\_fund\_flow\_120d("600519")
for d in data\[-5:\]:
 print(f"{d\['date'\]}: 主力净流入={d\['main\_net'\]/1e4:.0f}万 超大单={d\['super\_net'\]/1e4:.0f}万")

\# 统计近20日主力净流入
recent\_20 = data\[-20:\]
total\_main = sum(d\["main\_net"\] for d in recent\_20)
print(f"\\n近20日主力累计净流入: {total\_main/1e8:.2f}亿")
\`\`\`

\> \*\*⚠️ 大陆住宅 IP 间歇封锁（#18）：\*\* push2/push2his 系列对\*\*部分大陆住宅宽带 IP\*\* 有连接级风控，表现为偶发 \`HTTP 000\`（连接被拒/超时）或返回空——\*\*这不是代码问题\*\*（同一代码在其他网络/时段实测正常）。遇到时：① 隔几分钟重试；② 换网络环境（如手机热点）；③ 降低请求频率（调大 \`EM\_MIN\_INTERVAL\`）。日级资金流务实替代：仍可用 mootdx 算量价，或换时段重试。

\-\-\-

\## Layer 5: 新闻层

\### 5.1 东财个股新闻（直连 search-api-web）

\`\`\`python
import requests
import re
import json

def eastmoney\_stock\_news(code: str, page\_size: int = 20) -> list\[dict\]:
 """
 东财个股新闻（JSONP 接口）。
 返回: \[{title, content, time, source, url}\]
 """
 # 构造 JSONP 参数
 cb = "jQuery\_news"
 url = "https://search-api-web.eastmoney.com/search/jsonp"
 inner\_params = json.dumps({
 "uid": "",
 "keyword": code,
 "type": \["cmsArticleWebOld"\],
 "client": "web",
 "clientType": "web",
 "clientVersion": "curr",
 "param": {"cmsArticleWebOld": {"searchScope": "default", "sort": "default",
 "pageIndex": 1, "pageSize": page\_size, "preTag": "", "postTag": ""}},
 }, separators=(',', ':'))
 params = {"cb": cb, "param": inner\_params}
 headers = {"User-Agent": UA, "Referer": "https://so.eastmoney.com/"}
 r = em\_get(url, params=params, headers=headers, timeout=15)

 # 解析 JSONP
 text = r.text
 json\_str = text\[text.index("(") + 1 : text.rindex(")")\]
 d = json.loads(json\_str)

 rows = \[\]
 # 东财实际返回里 result.cmsArticleWebOld 直接就是文章列表（非 {list:\[...\]} 嵌套）
 articles = d.get("result", {}).get("cmsArticleWebOld", \[\]) or \[\]
 for a in articles:
 rows.append({
 "title": re.sub(r'<\[^>\]+>', '', a.get("title", "")),
 "content": re.sub(r'<\[^>\]+>', '', a.get("content", ""))\[:200\],
 "time": a.get("date", ""),
 "source": a.get("mediaName", ""),
 "url": a.get("url", ""),
 })
 return rows

\# 用法
news = eastmoney\_stock\_news("688017")
for n in news\[:5\]:
 print(f" {n\['time'\]} \| {n\['source'\]} \| {n\['title'\]}")
\`\`\`

\> \*\*⚠️ 间歇性返回空（#18）：\*\* 部分大陆住宅 IP 调本接口会只拿到 \`passportWeb\`（股民资料）而无 \`cmsArticleWebOld\`（文章列表）——这是东财对该 IP 的间歇风控，非代码问题。代码已对空结果安全返回 \`\[\]\`；遇到时隔几分钟或换网络重试即可。

\### 5.2 财联社快讯（直连 cls.cn，v1 API + 本地签名）✅ 已复活（2026-07）

\> \*\*✅ 2026-07 复活：\*\* 旧接口 \`cls.cn/nodeapi/telegraphList\` 2026-05 下线（站点改
\> Next.js，旧址返回 HTML 而非 JSON，#14）。现走新版 \`cls.cn/v1/roll/get\_roll\_list\`——它
\> 强制校验 \`sign\`，但签名\*\*纯本地计算、无需任何 key\*\*：\`sign = md5(sha1(按 key 字典序
\> 拼接的 query 串))\`。财联社快讯偏 A 股财经、时效强，与 §5.3 东财 7×24 \*\*互为独立备份\*\*
\> （两条不同源、不同风控面，一条被封另一条仍在）。2026-07-11 实测 errno=0 正常返回。

\`\`\`python
import requests
import hashlib
from datetime import datetime

def cls\_telegraph(page\_size: int = 50) -> list\[dict\]:
 """
 财联社电报（全市场实时快讯）。v1 API + 本地签名，零 key。
 返回: \[{title, content, time}\] time 已转为 'YYYY-MM-DD HH:MM:SS'
 """
 params = {"appName": "CailianpressWeb", "os": "web", "sv": "7.7.5",
 "last\_time": "", "refresh\_type": "1", "rn": str(page\_size)}
 # 签名：md5(sha1(按 key 字典序拼接的 query 串))，纯本地算、无需 key
 qs = "&".join(f"{k}={params\[k\]}" for k in sorted(params))
 sign = hashlib.md5(hashlib.sha1(qs.encode()).hexdigest().encode()).hexdigest()
 url = f"https://www.cls.cn/v1/roll/get\_roll\_list?{qs}&sign={sign}"
 headers = {"User-Agent": UA, "Referer": "https://www.cls.cn/"}
 r = requests.get(url, headers=headers, timeout=10)
 d = r.json()

 rows = \[\]
 for item in d.get("data", {}).get("roll\_data", \[\]) or \[\]:
 ts = item.get("ctime")
 t = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else ""
 rows.append({
 "title": item.get("title", "") or item.get("brief", ""),
 "content": item.get("content", "") or item.get("brief", ""),
 "time": t,
 })
 return rows

\# 用法
news = cls\_telegraph()
for n in news\[:10\]:
 print(f" {n\['time'\]} \| {n\['title'\]\[:60\]}")
\`\`\`

\### 5.3 东财全球资讯（7x24）

\`\`\`python
import requests

import uuid

def eastmoney\_global\_news(page\_size: int = 50) -> list\[dict\]:
 """
 东方财富全球财经资讯（7x24 滚动）。
 返回: \[{title, summary, time}\]
 """
 url = "https://np-weblist.eastmoney.com/comm/web/getFastNewsList"
 params = {
 "client": "web", "biz": "web\_724",
 "fastColumn": "102", "sortEnd": "",
 "pageSize": str(page\_size),
 "req\_trace": str(uuid.uuid4()),
 }
 headers = {"User-Agent": UA, "Referer": "https://kuaixun.eastmoney.com/"}
 r = em\_get(url, params=params, headers=headers, timeout=10)
 d = r.json()

 rows = \[\]
 for item in d.get("data", {}).get("fastNewsList", \[\]):
 rows.append({
 "title": item.get("title", ""),
 "summary": item.get("summary", "")\[:200\],
 "time": item.get("showTime", ""),
 })
 return rows

\# 用法
news = eastmoney\_global\_news()
for n in news\[:10\]:
 print(f" {n\['time'\]} \| {n\['title'\]}")
\`\`\`

\-\-\-

\## Layer 6: 基础数据层

\### 6.1 mootdx 财务快照（37字段季报数据）

\`\`\`python
from mootdx.quotes import Quotes

client = tdx\_client() # 见 Prerequisites 的 tdx\_client() helper（规避 0.11.x BESTIP bug；等价 Quotes.factory(market='std')）

\# market: 0=深圳, 1=上海
fin = client.finance(symbol='688017')
\# 返回 37 个字段的季报快照:
\# liutongguben(流通股本), zongguben(总股本)
\# eps(每股收益), bvps(每股净资产), roe(净资产收益率%)
\# profit(净利润), income(主营收入)
\# meigujingzichan(每股净资产), meigugongjijin(每股公积金)
\# meiguweifeipeili(每股未分配利润)
\# 等37个季报财务字段
\`\`\`

\### 6.2 mootdx F10（公司文本资料）

\`\`\`python
from mootdx.quotes import Quotes

client = tdx\_client() # 见 Prerequisites 的 tdx\_client() helper（规避 0.11.x BESTIP bug；等价 Quotes.factory(market='std')）

\# 9 大类文本数据:
categories = \[\
 "最新提示", "公司概况", "财务分析",\
 "股东研究", "股本结构", "资本运作",\
 "业内点评", "行业分析", "公司大事",\
\]
for cat in categories:
 text = client.F10(symbol='688017', name=cat)
 print(f"=== {cat} ===")
 print(text\[:200\] if text else "(空)")
\`\`\`

\> \\*\\*优化提示：\\*\\* "股东研究" 中的【4.股东变化】章节含大量历史十大股东列表，实测 16000+ chars。建议只保留最新一期（-70% token）。

\### 6.3 东财个股基本面（直连 push2 API）

\`\`\`python
import requests

def eastmoney\_stock\_info(code: str) -> dict:
 """
 东财个股基本面信息。
 返回: {code, name, industry, total\_shares, float\_shares, mcap, float\_mcap, list\_date}
 """
 market\_code = 1 if code.startswith("6") else 0
 url = "https://push2.eastmoney.com/api/qt/stock/get"
 params = {
 "fltt": "2", "invt": "2",
 "fields": "f57,f58,f84,f85,f127,f116,f117,f189,f43",
 "secid": f"{market\_code}.{code}",
 }
 headers = {"User-Agent": UA}
 r = em\_get(url, params=params, headers=headers, timeout=10)
 d = r.json().get("data", {})
 return {
 "code": d.get("f57", ""),
 "name": d.get("f58", ""),
 "industry": d.get("f127", ""),
 "total\_shares": d.get("f84", 0), # 总股本(股)
 "float\_shares": d.get("f85", 0), # 流通股(股)
 "mcap": d.get("f116", 0), # 总市值(元)
 "float\_mcap": d.get("f117", 0), # 流通市值(元)
 "list\_date": str(d.get("f189", "")), # 上市日期 YYYYMMDD
 "price": d.get("f43", 0),
 }

\# 用法
info = eastmoney\_stock\_info("688017")
print(f"{info\['name'\]}({info\['code'\]}): 行业={info\['industry'\]} 总市值={info\['mcap'\]/1e8:.0f}亿 上市={info\['list\_date'\]}")
\`\`\`

\### 6.4 新浪财报三表（资产负债表/利润表/现金流量表）

\`\`\`python
import requests

def sina\_financial\_report(code: str, report\_type: str = "lrb", num: int = 8) -> list\[dict\]:
 """
 新浪财报三表。
 code: 6位代码
 report\_type: "fzb"(资产负债表) / "lrb"(利润表) / "llb"(现金流量表)
 num: 取最近 N 期（默认 8 期）
 返回: 按报告期倒序的记录列表，每期一条 dict：
 {"报告期": "2026-03-31", "<科目>": "<值>", "<科目>\_同比": <同比>, ...}
 （item\_value 为新浪原始字符串数值，仅在有同比时附 "\_同比" 键）
 """
 prefix = "sh" if code.startswith("6") else "sz"
 paper\_code = f"{prefix}{code}"
 url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
 params = {
 "paperCode": paper\_code,
 "source": report\_type,
 "type": "0",
 "page": "1",
 "num": str(num),
 }
 headers = {"User-Agent": UA}
 r = requests.get(url, params=params, headers=headers, timeout=15)
 # 新浪实际结构: result.data.report\_list 是「按报告期(如 '20260331')为键」的 dict,
 # 每期对象的 data 字段才是行项列表 \[{item\_title, item\_value, item\_tongbi}\]。
 report\_list = r.json().get("result", {}).get("data", {}).get("report\_list", {}) or {}

 rows = \[\]
 for period in sorted(report\_list.keys(), reverse=True)\[:num\]:
 obj = report\_list\[period\]
 rec = {"报告期": f"{period\[:4\]}-{period\[4:6\]}-{period\[6:8\]}"}
 for it in obj.get("data", \[\]) or \[\]:
 title = it.get("item\_title", "")
 if not title or it.get("item\_value") is None:
 continue
 rec\[title\] = it.get("item\_value")
 tongbi = it.get("item\_tongbi")
 if tongbi not in (None, ""):
 rec\[title + "\_同比"\] = tongbi
 rows.append(rec)
 return rows

\# 用法: 利润表
lrb = sina\_financial\_report("600519", "lrb")
for item in lrb\[:3\]:
 print(f"报告期: {item.get('报告期', '')} 净利润: {item.get('净利润', '')}")

\# 用法: 资产负债表
fzb = sina\_financial\_report("600519", "fzb")

\# 用法: 现金流量表
llb = sina\_financial\_report("600519", "llb")
\`\`\`

\-\-\-

\## Layer 7: 公告层

\### 7.1 巨潮公告（直连 cninfo.com.cn）

\`\`\`python
import requests
from datetime import datetime

def \_cninfo\_ts\_to\_date(ts):
 """巨潮 announcementTime 返回 Unix 毫秒整数，需转换为日期字符串。"""
 if isinstance(ts, (int, float)):
 return datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
 return str(ts)\[:10\] if ts else ""

\# 巨潮 股票→orgId 映射（模块级缓存，首次调用时拉取一次，全程复用）
\_CNINFO\_ORGID\_MAP = {}

def \_cninfo\_orgid(code: str) -> str:
 """查股票真实 orgId。巨潮 orgId 并非统一 \`gssx0{code}\` 格式（如 601318→9900002221、
 601398→jjxt0000019、688017→9900041602），硬编码会导致大量股票（尤其 601xxx 段）
 返回 totalAnnouncement=0、查不到公告（#19）。优先动态查官方映射表，查不到再回退硬编码。"""
 global \_CNINFO\_ORGID\_MAP
 if not \_CNINFO\_ORGID\_MAP:
 try:
 r = requests.get("http://www.cninfo.com.cn/new/data/szse\_stock.json",
 headers={"User-Agent": UA}, timeout=15)
 \_CNINFO\_ORGID\_MAP = {s\["code"\]: s\["orgId"\]
 for s in r.json().get("stockList", \[\])}
 except Exception as e:
 print(f"\[WARN\] 巨潮 orgId 映射表拉取失败，回退硬编码规则: {e}")
 org = \_CNINFO\_ORGID\_MAP.get(code)
 if org:
 return org
 # fallback：老格式（仅部分老股票如 600519/600036 适用）
 if code.startswith("6"):
 return f"gssh0{code}"
 elif code.startswith("8") or code.startswith("4"):
 return f"gsbj0{code}"
 return f"gssz0{code}"

def cninfo\_announcements(code: str, page\_size: int = 30) -> list\[dict\]:
 """
 巨潮公告全文检索。
 返回: \[{title, type, date, url}\]
 """
 url = "https://www.cninfo.com.cn/new/hisAnnouncement/query"
 org\_id = \_cninfo\_orgid(code) # 动态查真实 orgId（#19 修复，自带硬编码 fallback）

 payload = {
 "stock": f"{code},{org\_id}",
 "tabName": "fulltext",
 "pageSize": str(page\_size),
 "pageNum": "1",
 "column": "",
 "category": "",
 "plate": "",
 "seDate": "",
 "searchkey": "",
 "secid": "",
 "sortName": "",
 "sortType": "",
 "isHLtitle": "true",
 }
 headers = {
 "User-Agent": UA,
 "Content-Type": "application/x-www-form-urlencoded",
 "Referer": "https://www.cninfo.com.cn/new/disclosure",
 "Origin": "https://www.cninfo.com.cn",
 }
 r = requests.post(url, data=payload, headers=headers, timeout=15)
 d = r.json()

 rows = \[\]
 for item in d.get("announcements", \[\]) or \[\]:
 rows.append({
 "title": item.get("announcementTitle", ""),
 "type": item.get("announcementTypeName", ""),
 "date": \_cninfo\_ts\_to\_date(item.get("announcementTime")),
 "url": f"https://www.cninfo.com.cn/new/disclosure/detail?annoId={item.get('announcementId', '')}",
 })
 return rows

\# 用法
anns = cninfo\_announcements("688017")
for a in anns\[:10\]:
 print(f" {a\['date'\]} \| {a\['type'\]} \| {a\['title'\]}")
\`\`\`

\### 7.2 mootdx F10 公告摘要

\`\`\`python
from mootdx.quotes import Quotes
client = tdx\_client() # 见 Prerequisites 的 tdx\_client() helper（规避 0.11.x BESTIP bug；等价 Quotes.factory(market='std')）
text = client.F10(symbol='688017', name='最新提示')
\# 包含最近的公告/分红/股东大会决议等摘要
\`\`\`

\-\-\-

\## Layer 8: 打板层（涨停 / 炸板 / 跌停 / 题材情绪，V3.3.0 新增）

\> 连板梯队、炸板率、晋级率、涨停原因题材——打板与题材跟踪的高频需求（#23 / #15）。东财四池走 \`push2ex.eastmoney.com\`（与现有 push2 同源，已纳入 \`em\_get()\` 限流）；涨停原因题材增强用同花顺。\*\*全部免登录、零鉴权。\*\*

\### 8.1 东财涨停板池 — 涨停 / 炸板 / 跌停 / 昨日涨停

\`\`\`python
import requests

ZTB\_UT = "7eea3edcaed734bea9cbfc24409ed989"

def \_fmt\_zt\_time(t) -> str:
 """涨停板时间整数 → HH:MM:SS（92500 → 09:25:00）。"""
 s = str(t).zfill(6)
 return f"{s\[0:2\]}:{s\[2:4\]}:{s\[4:6\]}"

def \_em\_zt\_api(endpoint: str, sort: str, date: str) -> list\[dict\]:
 """东财涨停板行情中心通用请求（push2ex，走 em\_get 限流）。
 endpoint: getTopicZTPool / getTopicZBPool / getTopicDTPool / getYesterdayZTPool
 返回 data.pool 原始列表（data 为 null = 非交易日 / 参数错）。"""
 url = f"https://push2ex.eastmoney.com/{endpoint}"
 params = {"ut": ZTB\_UT, "dpt": "wz.ztzt", "Pageindex": 0,
 "pagesize": 10000, "sort": sort, "date": date}
 headers = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
 try:
 r = em\_get(url, params=params, headers=headers, timeout=10)
 return (r.json().get("data") or {}).get("pool") or \[\]
 except Exception as e:
 print(f"\[WARN\] 涨停板池 {endpoint} 请求失败: {e}")
 return \[\]

def em\_zt\_pool(date: str) -> list\[dict\]:
 """涨停池。date=YYYYMMDD（交易日）。
 返回每只: code/name/price/pct/amount/float\_cap/turnover/limit\_days(连板数)/
 first\_seal/last\_seal(封板时间)/seal\_fund(封板资金,元)/break\_times(炸板次数)/
 industry/zt\_stat(N天M板)"""
 out = \[\]
 for p in \_em\_zt\_api("getTopicZTPool", "fbt:asc", date):
 out.append({"code": p\["c"\], "name": p\["n"\], "price": p\["p"\] / 1000,
 "pct": round(p\["zdp"\], 2), "amount": p\["amount"\], "float\_cap": p\["ltsz"\],
 "turnover": round(p\["hs"\], 2), "limit\_days": p\["lbc"\],
 "first\_seal": \_fmt\_zt\_time(p\["fbt"\]), "last\_seal": \_fmt\_zt\_time(p\["lbt"\]),
 "seal\_fund": p\["fund"\], "break\_times": p\["zbc"\], "industry": p.get("hybk", ""),
 "zt\_stat": f'{(p.get("zttj") or {}).get("days","?")}天{(p.get("zttj") or {}).get("ct","?")}板'})
 return out

def em\_zb\_pool(date: str) -> list\[dict\]:
 """炸板池（涨停后开板）。返回 code/name/price/limit\_price(涨停价)/pct/turnover/
 first\_seal/break\_times/amplitude(振幅)/speed(涨速)/industry/zt\_stat"""
 out = \[\]
 for p in \_em\_zt\_api("getTopicZBPool", "fbt:asc", date):
 out.append({"code": p\["c"\], "name": p\["n"\], "price": p\["p"\] / 1000,
 "limit\_price": p\["ztp"\] / 1000, "pct": round(p\["zdp"\], 2),
 "turnover": round(p\["hs"\], 2), "first\_seal": \_fmt\_zt\_time(p\["fbt"\]),
 "break\_times": p\["zbc"\], "amplitude": round(p\["zf"\], 2),
 "speed": round(p\["zs"\], 2), "industry": p.get("hybk", ""),
 "zt\_stat": f'{(p.get("zttj") or {}).get("days","?")}天{(p.get("zttj") or {}).get("ct","?")}板'})
 return out

def em\_dt\_pool(date: str) -> list\[dict\]:
 """跌停池。返回 code/name/price/pct/turnover/pe/seal\_fund(封单资金)/last\_seal/
 board\_amount(板上成交额)/dt\_days(连续跌停)/open\_times(开板次数)/industry"""
 out = \[\]
 for p in \_em\_zt\_api("getTopicDTPool", "fund:asc", date):
 out.append({"code": p\["c"\], "name": p\["n"\], "price": p\["p"\] / 1000,
 "pct": round(p\["zdp"\], 2), "turnover": round(p\["hs"\], 2), "pe": p.get("pe"),
 "seal\_fund": p\["fund"\], "last\_seal": \_fmt\_zt\_time(p\["lbt"\]),
 "board\_amount": p.get("fba"), "dt\_days": p.get("days"),
 "open\_times": p.get("oc"), "industry": p.get("hybk", "")})
 return out

def em\_yzt\_pool(date: str) -> list\[dict\]:
 """昨日涨停池（昨涨停今表现，算晋级率/赚钱效应）。返回 code/name/price/
 pct(今日涨幅)/turnover/amplitude/speed/y\_first\_seal(昨封板时间)/
 y\_limit\_days(昨连板)/industry/zt\_stat"""
 out = \[\]
 for p in \_em\_zt\_api("getYesterdayZTPool", "zs:desc", date):
 out.append({"code": p\["c"\], "name": p\["n"\], "price": p\["p"\] / 1000,
 "pct": round(p\["zdp"\], 2), "turnover": round(p\["hs"\], 2),
 "amplitude": round(p\["zf"\], 2), "speed": round(p\["zs"\], 2),
 "y\_first\_seal": \_fmt\_zt\_time(p\["yfbt"\]), "y\_limit\_days": p\["ylbc"\],
 "industry": p.get("hybk", ""), "zt\_stat": f'{(p.get("zttj") or {}).get("days","?")}天{(p.get("zttj") or {}).get("ct","?")}板'})
 return out

\# 用法
zt = em\_zt\_pool("20260626")
print(f"今日涨停 {len(zt)} 只")
for s in zt\[:3\]:
 print(f" {s\['name'\]} {s\['zt\_stat'\]} 封板{s\['seal\_fund'\]/1e8:.2f}亿 {s\['industry'\]}")
\`\`\`

\> \\*\\*坑：\\*\\* ① 价格字段 \`price\`/\`limit\_price\` 已 ÷1000（原始值是 ×1000 整数）。② 四池只有 \`sort\` 不同（涨停/炸板=\`fbt:asc\`、跌停=\`fund:asc\`、昨涨停=\`zs:desc\`），\`dpt\` 都是 \`wz.ztzt\`。③ \`date\` 必须传交易日，非交易日 \`data\` 返回 null。④ 金额单位均为\*\*元\*\*。

\### 8.2 同花顺涨停揭秘 — 涨停原因题材 + 封板成功率 + 板型

\`\`\`python
from datetime import datetime

def ths\_limit\_up\_pool(date: str) -> list\[dict\]:
 """同花顺涨停揭秘（涨停原因 \+ 封板质量增强源）。date=YYYYMMDD。
 返回每只: code/name/price/pct/reason(涨停原因题材)/board\_type(换手板/一字板/T字板)/
 seal\_rate(封板成功率,0~1)/break\_times(炸板次数)/seal\_amount(封单额,元)/
 high\_days(几天几板)/first\_time(首次涨停时间)/is\_again(是否回封 0/1)"""
 url = "https://data.10jqka.com.cn/dataapi/limit\_up/limit\_up\_pool"
 params = {"page": 1, "limit": 200,
 "field": "199112,10,9001,330323,330324,330325,9002,330329,133971,133970,1968584,3475914,9003,9004",
 "filter": "HS,GEM2STAR", "order\_field": "330324", "order\_type": "0", "date": date}
 try:
 r = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=10)
 info = (r.json().get("data") or {}).get("info", \[\])
 except Exception as e:
 print(f"\[WARN\] 同花顺涨停揭秘请求失败: {e}")
 return \[\]
 out = \[\]
 for it in info:
 ft = it.get("first\_limit\_up\_time")
 out.append({"code": it.get("code"), "name": it.get("name"),
 "price": it.get("latest"), "pct": it.get("change\_rate"),
 "reason": it.get("reason\_type", ""), "board\_type": it.get("limit\_up\_type", ""),
 "seal\_rate": it.get("limit\_up\_suc\_rate"), "break\_times": it.get("open\_num") or 0,
 "seal\_amount": it.get("order\_amount"), "high\_days": it.get("high\_days", ""),
 "first\_time": datetime.fromtimestamp(int(ft)).strftime("%H:%M:%S") if ft else "",
 "is\_again": it.get("is\_again\_limit")})
 return out

\# 用法: 涨停原因题材归因
for s in ths\_limit\_up\_pool("20260626")\[:5\]:
 print(f" {s\['name'\]} {s\['high\_days'\]} \| {s\['reason'\]} \| 封板率{s\['seal\_rate'\]}")
\`\`\`

\> \\*\\*坑：\\*\\* \`first\_limit\_up\_time\` 是 \*\*Unix 秒时间戳\*\*（要 \`datetime.fromtimestamp\`），不是 HHMMSS。\`field\` 那串是同花顺内部字段 ID，照抄即可。\`filter=HS,GEM2STAR\` 控制板块范围（沪深主板 + 创业板 + 科创板）。

\### 8.3 打板情绪速算 — 炸板率 / 连板高度 / 连板梯队

\`\`\`python
def limit\_up\_sentiment(date: str) -> dict:
 """打板情绪温度计：连板梯队 \+ 炸板率 \+ 涨跌停对比。"""
 zt, zb, dt = em\_zt\_pool(date), em\_zb\_pool(date), em\_dt\_pool(date)
 ladder = {}
 for s in zt:
 ladder\[s\["limit\_days"\]\] = ladder.get(s\["limit\_days"\], 0) + 1
 zt\_n, zb\_n = len(zt), len(zb)
 return {"date": date, "zt\_count": zt\_n, "zb\_count": zb\_n, "dt\_count": len(dt),
 "break\_rate": round(zb\_n / (zt\_n + zb\_n) \* 100, 1) if (zt\_n + zb\_n) else 0, # 炸板率%
 "max\_height": max((s\["limit\_days"\] for s in zt), default=0), # 最高连板
 "ladder": dict(sorted(ladder.items()))} # 连板梯队 {板数:家数}

\# 用法
s = limit\_up\_sentiment("20260626")
print(f"涨停{s\['zt\_count'\]} 炸板{s\['zb\_count'\]}(炸板率{s\['break\_rate'\]}%) "
 f"跌停{s\['dt\_count'\]} 最高{s\['max\_height'\]}连板")
print(f"连板梯队: {s\['ladder'\]}")
\`\`\`

\> 晋级率（昨涨停今仍涨停 / 昨涨停总数）可用 \`em\_yzt\_pool()\` 的 \`pct >= 9.8\` 计数除以总数自算。

\-\-\-

\## Layer 9: ETF 期权层（T型报价 + 希腊字母 + IV，V3.3.0 新增）

\> 50ETF / 300ETF / 科创50ETF / 500ETF 期权（#13）。走新浪源——\*\*T型报价、希腊字母、隐含波动率均由交易所/新浪预先算好，无需本地算 BSM\*\*。免费直连，唯一注意带 \`Referer\`。

\### 9.1 合约清单 + T型报价 + 希腊字母

\`\`\`python
import requests

SINA\_OPT\_HDR = {"Referer": "https://stock.finance.sina.com.cn/", "User-Agent": UA}

def \_opt\_f(x):
 try: return float(x)
 except Exception: return x

def \_sina\_opt\_list(param: str) -> list:
 """新浪 hq.sinajs.cn 取值（GBK，逗号分隔，去 var hq\_str\_XXX="..." 壳）。"""
 r = requests.get(f"https://hq.sinajs.cn/list={param}", headers=SINA\_OPT\_HDR, timeout=10)
 r.encoding = "gbk"
 t = r.text
 return t.split('"')\[1\].split(",") if '"' in t else \[\]

def sina\_option\_codes(underlying: str = "510050", call: bool = True) -> dict:
 """ETF期权合约清单。underlying: 510050/510300/588000/510500。call=True认购/False认沽。
 返回 {月份YYMM: \[合约代码,...\]}，第一个 key 即近月。"""
 cate = {"510050": "50ETF", "510300": "300ETF",
 "588000": "科创50ETF", "510500": "500ETF"}.get(underlying, "50ETF")
 url = ("https://stock.finance.sina.com.cn/futures/api/openapi.php/"
 f"StockOptionService.getStockName?exchange=null&cate={cate}")
 try:
 months = requests.get(url, headers=SINA\_OPT\_HDR, timeout=10).json()\["result"\]\["data"\]\["contractMonth"\]
 except Exception as e:
 print(f"\[WARN\] 期权月份获取失败: {e}")
 return {}
 months = \[m.replace("-", "")\[2:\] for m in months\[1:\]\] # 丢首个，转 YYMM
 flag = "OP\_UP\_" if call else "OP\_DOWN\_"
 out = {}
 for m in months:
 codes = \[c.replace("CON\_OP\_", "") for c in \_sina\_opt\_list(f"{flag}{underlying}{m}")\
 if c.startswith("CON\_OP\_")\]
 if codes:
 out\[m\] = codes
 return out

def sina\_option\_tquote(code: str) -> dict:
 """期权T型报价。返回 bid\_vol/bid/last/ask/ask\_vol/open\_interest(持仓量)/pct/
 strike(行权价)/prev\_close/open/limit\_up/limit\_down/name/amplitude/high/low/volume/amount。"""
 v = \_sina\_opt\_list(f"CON\_OP\_{code}")
 if len(v) < 43:
 return {}
 return {"bid\_vol": \_opt\_f(v\[0\]), "bid": \_opt\_f(v\[1\]), "last": \_opt\_f(v\[2\]),
 "ask": \_opt\_f(v\[3\]), "ask\_vol": \_opt\_f(v\[4\]), "open\_interest": \_opt\_f(v\[5\]),
 "pct": \_opt\_f(v\[6\]), "strike": \_opt\_f(v\[7\]), "prev\_close": \_opt\_f(v\[8\]),
 "open": \_opt\_f(v\[9\]), "limit\_up": \_opt\_f(v\[10\]), "limit\_down": \_opt\_f(v\[11\]),
 "name": v\[37\], "amplitude": \_opt\_f(v\[38\]), "high": \_opt\_f(v\[39\]),
 "low": \_opt\_f(v\[40\]), "volume": \_opt\_f(v\[41\]), "amount": \_opt\_f(v\[42\])}

def sina\_option\_greeks(code: str) -> dict:
 """期权希腊字母 \+ 隐含波动率。返回 name/volume/delta/gamma/theta/vega/
 iv(隐含波动率,小数)/high/low/trade\_code/strike/last/theory(理论价值)。"""
 raw = \_sina\_opt\_list(f"CON\_SO\_{code}")
 if len(raw) < 16:
 return {}
 v = \[raw\[0\]\] + raw\[4:\] # ⚠️ raw\[1:4\] 是 3 个空串，必须跳过否则字段错位
 return {"name": v\[0\], "volume": \_opt\_f(v\[1\]), "delta": \_opt\_f(v\[2\]),
 "gamma": \_opt\_f(v\[3\]), "theta": \_opt\_f(v\[4\]), "vega": \_opt\_f(v\[5\]),
 "iv": \_opt\_f(v\[6\]), "high": \_opt\_f(v\[7\]), "low": \_opt\_f(v\[8\]),
 "trade\_code": v\[9\], "strike": \_opt\_f(v\[10\]), "last": \_opt\_f(v\[11\]), "theory": \_opt\_f(v\[12\])}

\# 用法: 取 50ETF 近月平值附近一档的 T型报价 + 希腊字母
codes = sina\_option\_codes("510050", call=True)
near = list(codes)\[0\] # 近月
c = codes\[near\]\[len(codes\[near\]) // 2\] # 中间档≈平值附近
q, g = sina\_option\_tquote(c), sina\_option\_greeks(c)
print(f"{q\['name'\]} 行权价{q\['strike'\]} 最新{q\['last'\]} 持仓{q\['open\_interest'\]:.0f}")
print(f" Delta={g\['delta'\]} Gamma={g\['gamma'\]} Theta={g\['theta'\]} Vega={g\['vega'\]} IV={g\['iv'\]:.2%}")
\`\`\`

\> \\*\\*坑：\\*\\* ① 新浪源 \*\*GBK 编码\*\*、\*\*逗号分隔\*\*、需去 \`var hq\_str\_XXX="..."\` 壳。② 必带 \`Referer: https://stock.finance.sina.com.cn/\`，否则 403。③ 希腊字母解析 \*\*\`\[raw\[0\]\] + raw\[4:\]\`\*\*——\`raw\[1:4\]\` 是 3 个空串，不跳过则 Delta/IV 全错位。④ \`iv\` 是小数（0.1735 = 17.35%）。⑤ 300ETF(510300)、科创50ETF(588000) 同理，换 \`underlying\` 即可。

\-\-\-

\## Layer 10: 舆情互动层（互动易问答 + 热榜 + 人气榜，V3.3.0 新增）

\> 投资者互动问答 \+ 市场热度——AI 问答与选题的独家信源。\*\*互动易\*\*（巨潮）能答"公司怎么回应某传闻/利好"，别处拿不到；\*\*同花顺热榜 / 东财人气榜\*\*给"当下最热个股 + 被归到什么概念在炒"。全部免登录、零鉴权。

\### 10.1 互动易问答（巨潮 — 投资者提问 + 公司回复）

\`\`\`python
import requests
from datetime import datetime

def cninfo\_irm(code: str, page\_size: int = 30, page\_num: int = 1) -> list\[dict\]:
 """互动易问答（深沪统一走巨潮）。code: 6位代码。
 返回每条: code/company/question(投资者提问)/answer(公司回复,None=未回复)/
 answerer(回答方)/ask\_time。"""
 try:
 r1 = requests.post("https://irm.cninfo.com.cn/newircs/index/queryKeyboardInfo",
 data={"keyWord": code}, headers={"User-Agent": UA}, timeout=10)
 d1 = r1.json().get("data") or \[\]
 if not d1:
 return \[\]
 org\_id = d1\[0\].get("secid")
 # ⚠️ 第二步参数必须放 query string（POST 但 body 空），否则 HTTP 400
 params = {"\_t": 1, "stockcode": code, "orgId": org\_id, "pageSize": page\_size,
 "pageNum": page\_num, "keyWord": "", "startDay": "", "endDay": ""}
 r2 = requests.post("https://irm.cninfo.com.cn/newircs/company/question",
 params=params, headers={"User-Agent": UA}, timeout=10)
 rows = r2.json().get("rows") or \[\]
 except Exception as e:
 print(f"\[WARN\] 互动易请求失败: {e}")
 return \[\]
 out = \[\]
 for it in rows:
 pd = it.get("pubDate")
 out.append({"code": it.get("stockCode"), "company": it.get("companyShortName"),
 "question": it.get("mainContent"), "answer": it.get("attachedContent"),
 "answerer": it.get("attachedAuthor"),
 "ask\_time": datetime.fromtimestamp(pd / 1000).strftime("%Y-%m-%d %H:%M") if pd else ""})
 return out

\# 用法: 看公司怎么回应投资者关切
for q in cninfo\_irm("002594", page\_size=30):
 if q\["answer"\]:
 print(f" Q: {q\['question'\]\[:30\]}\\n A\[{q\['answerer'\]}\]: {q\['answer'\]\[:50\]}")
\`\`\`

\> \\*\\*坑：\\*\\* ① 第二步参数放 \*\*query string\*\*（不是 body），否则 400。② \`orgId\` 取自第一步的 \`secid\`（即便前缀是 \`gshk\`，靠 \`stockcode\` 过滤照样拿 A 股问答）。③ 最新提问常未回复（\`answer=None\`），回复率因公司而异（实测立讯精密 002475 回复多、京东方 000725 几乎不回）。④ 时间是毫秒时间戳。

\### 10.2 同花顺热榜 + 东财人气榜（市场热度 + 概念命中）

\`\`\`python
EM\_HOT\_BODY = {"appId": "appId01", "globalId": "786e4c21-70dc-435a-93bb-38"}

def ths\_hot\_list(period: str = "hour") -> list\[dict\]:
 """同花顺热榜（单接口拿名称+人气+概念标签+排名变化）。period: hour/day。
 返回每只: rank/code/name/heat(人气值)/pct/rank\_chg(排名变化)/concepts(概念标签)/tag。"""
 try:
 r = requests.get("https://dq.10jqka.com.cn/fuyao/hot\_list\_data/out/hot\_list/v1/stock",
 params={"stock\_type": "a", "type": period, "list\_type": "normal"},
 headers={"User-Agent": UA}, timeout=10)
 lst = (r.json().get("data") or {}).get("stock\_list") or \[\]
 except Exception as e:
 print(f"\[WARN\] 同花顺热榜失败: {e}")
 return \[\]
 out = \[\]
 for it in lst:
 tag = it.get("tag") or {}
 out.append({"rank": it.get("order"), "code": it.get("code"), "name": it.get("name"),
 "heat": it.get("rate"), "pct": it.get("rise\_and\_fall"), "rank\_chg": it.get("hot\_rank\_chg"),
 "concepts": tag.get("concept\_tag") or \[\], "tag": tag.get("popularity\_tag", "")})
 return out

def em\_hot\_rank(top: int = 50) -> list\[dict\]:
 """东财人气榜（排名 \+ 排名变化 \+ 名称/价格）。返回 rank/code/name/price/pct/rank\_chg。"""
 try:
 r = requests.post("https://emappdata.eastmoney.com/stockrank/getAllCurrentList",
 json={\*\*EM\_HOT\_BODY, "marketType": "", "pageNo": 1, "pageSize": top},
 headers={"User-Agent": UA}, timeout=10)
 data = r.json().get("data") or \[\]
 if not data:
 return \[\]
 # 人气榜只给带前缀代码，用 push2 ulist.np 批量补名称/价格
 secids = \[("0." if it\["sc"\].startswith("SZ") else "1.") + it\["sc"\]\[2:\] for it in data\]
 u = requests.get("https://push2.eastmoney.com/api/qt/ulist.np/get",
 params={"ut": "f057cbcbce2a86e2866ab8877db1d059", "fltt": 2, "invt": 2,
 "fields": "f14,f3,f12,f2", "secids": ",".join(secids)},
 headers={"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}, timeout=10)
 diff = (u.json().get("data") or {}).get("diff") or \[\]
 if isinstance(diff, dict): # push2 的 diff 有时是 dict
 diff = list(diff.values())
 nm = {x\["f12"\]: (x.get("f14"), x.get("f2"), x.get("f3")) for x in diff}
 except Exception as e:
 print(f"\[WARN\] 东财人气榜失败: {e}")
 return \[\]
 out = \[\]
 for it in data:
 code = it\["sc"\]\[2:\]
 name, price, pct = nm.get(code, ("", None, None))
 out.append({"rank": it\["rk"\], "code": code, "name": name,
 "price": price, "pct": pct, "rank\_chg": it.get("hisRc")})
 return out

def em\_hot\_concept(code: str) -> list\[dict\]:
 """东财个股热门概念命中（这只票当下被市场归到哪些概念在炒）。
 返回 \[{concept, bk, hit(命中热度)}, ...\]，按热度降序。"""
 try:
 prefix = "SH" if code.startswith("6") else "SZ"
 r = requests.post("https://emappdata.eastmoney.com/stockrank/getHotStockRankList",
 json={\*\*EM\_HOT\_BODY, "srcSecurityCode": prefix + code},
 headers={"User-Agent": UA}, timeout=10)
 data = r.json().get("data") or \[\]
 except Exception as e:
 print(f"\[WARN\] 东财个股概念失败: {e}")
 return \[\]
 return \[{"concept": x.get("conceptName"), "bk": x.get("conceptId"),\
 "hit": x.get("hitCount")} for x in data\]

\# 用法
for s in ths\_hot\_list()\[:5\]:
 print(f" #{s\['rank'\]} {s\['name'\]} 热度{s\['heat'\]} {s\['concepts'\]} {s\['tag'\]}")
hot = em\_hot\_rank(10) # 东财人气榜 TOP10
print("人气第一:", hot\[0\]\["name"\], "概念命中:", em\_hot\_concept(hot\[0\]\["code"\])\[:3\])
\`\`\`

\> \\*\\*坑：\\*\\* ① 东财人气榜 \`getAllCurrentList\` 只返回带前缀代码（SZ/SH），名称要再走 \`ulist.np\` 补（\`SZ\`→\`0.\`、\`SH\`→\`1.\`）。② \`ulist.np\` 的 \`diff\` 偶尔是 dict（按序号为键），已做 \`list(values())\` 归一化。③ 同花顺热榜 \`type\` 可选 \`hour\`/\`day\`。

\-\-\-

\## 估值计算公式

\### 前向PE

\`\`\`python
def forward\_pe(price: float, eps\_forecast: float) -> float:
 """前向PE = 当前股价 / 未来年度一致预期EPS"""
 if eps\_forecast <= 0:
 return float("inf")
 return price / eps\_forecast
\`\`\`

\### PE消化时间

\`\`\`python
import math

def pe\_digestion(current\_pe: float, cagr: float, target\_pe: float = 30) -> float:
 """
 当前PE消化到目标PE需要多少年。
 target\_pe 固定30x（A股成长股合理估值锚点）。
 cagr: 用 下一年EPS / 当年EPS - 1
 """
 if current\_pe <= target\_pe:
 return 0.0
 if cagr <= 0:
 return float("inf")
 return math.log(current\_pe / target\_pe) / math.log(1 + cagr)
\`\`\`

\### PEG

\`\`\`python
def calc\_peg(pe: float, cagr: float) -> float:
 """
 PEG = 前向PE / (CAGR \* 100)
 PEG < 1 → 便宜
 PEG 1-1.5 → 合理
 PEG > 1.5 → 贵
 """
 if cagr <= 0:
 return float("inf")
 return pe / (cagr \* 100)
\`\`\`

\### 投资框架速查

\`\`\`
壁垒 → 增速 → PE消化 → PEG校验

1\. 有壁垒吗？(tech\_moat / capacity\_moat) → 没有则排除
2\. 增速多少？(CAGR > 30% 才有意义)
3\. PE多久消化到30x？(< 2年合理, > 4年太贵)
4\. PEG多少？(< 1 便宜, 1-1.5 合理, > 1.5 贵)

30x PE 锚点: A股成长股的合理估值重力线，所有行业统一用30x。
期权定价例外: PEG > 3 但壁垒极深时，本质是看涨期权，不适用PEG框架。
\`\`\`

\-\-\-

\## 完整调研流程

\### 流程 A: 单票完整估值（30秒）

\`\`\`python
import requests
import urllib.request
import math
import pandas as pd

def full\_valuation(code: str) -> dict:
 """单票完整估值分析"""
 # 1\. 腾讯实时行情
 prefix = "sh" if code.startswith(("6","9")) else ("bj" if code.startswith("8") else "sz")
 url = f"https://qt.gtimg.cn/q={prefix}{code}"
 req = urllib.request.Request(url)
 req.add\_header("User-Agent", "Mozilla/5.0")
 resp = urllib.request.urlopen(req, timeout=10)
 data = resp.read().decode("gbk")
 vals = data.split('"')\[1\].split("~")
 price = float(vals\[3\])
 mcap = float(vals\[44\])
 pe\_ttm = float(vals\[39\]) if vals\[39\] else 0
 pb = float(vals\[46\]) if vals\[46\] else 0

 # 2\. 机构一致预期（直连同花顺）
 df = ths\_eps\_forecast(code)
 eps\_cur = eps\_next = None
 analyst\_count = 0
 if not df.empty and len(df.columns) >= 3:
 # 按列名取「均值」=机构一致预期EPS（见 ths\_eps\_forecast 文档）。
 # 不按 iloc 位置取——同花顺表格列序会变；且旧版误用 iloc\[2\]＝「最小值」
 # 当成一致预期，导致 pe\_forward/PEG 系统性偏差，此处一并修正。
 def \_pick(row, name):
 for c in df.columns:
 if name in str(c):
 return row.get(c)
 return None
 try:
 r0 = df.iloc\[0\]
 v = \_pick(r0, "均值"); eps\_cur = float(v) if pd.notna(v) else None
 cnt = \_pick(r0, "预测机构数"); analyst\_count = int(cnt) if pd.notna(cnt) else 0
 if len(df) >= 2:
 vn = \_pick(df.iloc\[1\], "均值"); eps\_next = float(vn) if pd.notna(vn) else None
 except (ValueError, TypeError) as e:
 print(f"\[WARN\] full\_valuation EPS 解析失败({e})，估值可能不完整")

 # 3\. 估值指标
 pe\_fwd = price / eps\_cur if eps\_cur else float("inf")
 cagr = (eps\_next / eps\_cur - 1) if (eps\_cur and eps\_next) else 0
 peg = pe\_fwd / (cagr \* 100) if cagr > 0 else float("inf")
 digest = (
 math.log(pe\_fwd / 30) / math.log(1 + cagr)
 if pe\_fwd > 30 and cagr > 0 else 0
 )

 return {
 "name": vals\[1\],
 "price": price,
 "mcap\_yi": mcap,
 "pe\_ttm": pe\_ttm,
 "pb": pb,
 "eps\_cur": eps\_cur,
 "eps\_next": eps\_next,
 "pe\_fwd": round(pe\_fwd, 1) if eps\_cur else None,
 "cagr\_pct": round(cagr \* 100, 0) if cagr else None,
 "peg": round(peg, 2) if peg != float("inf") else None,
 "digest\_years": round(digest, 1),
 "analyst\_count": analyst\_count,
 }

\# 用法
result = full\_valuation("688017")
print(result)
\`\`\`

\### 流程 B: 批量估值对比

\`\`\`python
stocks = \["688017", "300308", "300476", "002463"\]
for code in stocks:
 try:
 r = full\_valuation(code)
 print(f"{r\['name'\]}({code}): PE\_fwd={r\['pe\_fwd'\]}x PEG={r\['peg'\]} 消化={r\['digest\_years'\]}年 覆盖={r\['analyst\_count'\]}家")
 except Exception as e:
 print(f"{code}: 失败 - {e}")
\`\`\`

\### 流程 C: 主题研报批量检索

\`\`\`python
\# Step 1: iwencai 多 query 语义搜索
queries = \[\
 "人形机器人产业链深度 2026",\
 "人形机器人减速器 丝杠",\
 "特斯拉Optimus 国产供应链",\
\]
seen\_uids = set()
all\_articles = \[\]
for q in queries:
 arts = iwencai\_search(q, channel="report", size=50)
 for a in arts:
 uid = a.get("uid", "")
 if uid not in seen\_uids:
 seen\_uids.add(uid)
 all\_articles.append(a)
print(f"共 {len(all\_articles)} 篇去重后研报")

\# Step 2: 东财补充同标的研报 + PDF
for a in all\_articles\[:10\]:
 stocks = a.get("stock\_infos") or \[\]
 for s in stocks:
 stock\_code = s.get("code", "")
 if stock\_code:
 em = eastmoney\_reports(stock\_code, max\_pages=1)
 print(f" {stock\_code}: 东财 {len(em)} 篇")
\`\`\`

\### 流程 D: 新标的快速调研（V3.0 增强版）

\`\`\`python
code = "688017"

\# 1\. 有无机构覆盖？
forecast = ths\_eps\_forecast(code)
print(f"机构覆盖: {'有' if not forecast.empty else '无'}")

\# 2\. 实时估值
quotes = tencent\_quote(\[code\])
q = quotes\[code\]
print(f"PE={q\['pe\_ttm'\]} PB={q\['pb'\]} 市值={q\['mcap\_yi'\]}亿")

\# 3\. PE消化 → 用 full\_valuation()
\# 4\. PEG校验

\# 5\. 概念板块归属
blocks = eastmoney\_concept\_blocks(code)
print(f"板块: {', '.join(blocks\['concept\_tags'\]\[:10\])}")

\# 6\. 资金流向（分钟级，当日盘中）
flow = eastmoney\_fund\_flow\_minute(code)
if flow:
 total = sum(f\["main\_net"\] for f in flow)
 print(f"当日主力累计净流入: {total/1e4:.0f}万")

\# 7\. 资金流向（东财120日）
flow\_120 = stock\_fund\_flow\_120d(code)
if flow\_120:
 total = sum(d\["main\_net"\] for d in flow\_120\[-20:\])
 print(f"近20日主力累计净流入: {total/1e8:.2f}亿")

\# 8\. 龙虎榜
dtb = dragon\_tiger\_board(code, "2026-05-17")
print(f"近30日上龙虎榜: {len(dtb\['records'\])} 次")

\# 9\. 解禁预警
lockup = lockup\_expiry(code, "2026-05-17")
print(f"未来90天待解禁: {len(lockup\['upcoming'\])} 批")

\# 10\. 融资融券
margin = margin\_trading(code, page\_size=5)
if margin:
 print(f"最新融资余额: {margin\[0\]\['rzye'\]/1e8:.2f}亿")

\# 11\. 股东户数
holders = holder\_num\_change(code)
if holders:
 print(f"最新股东数: {holders\[0\]\['holder\_num'\]} 环比{holders\[0\]\['change\_ratio'\]}%")
\`\`\`

\-\-\-

\## 数据源优先级

\| 优先级 \| 数据源 \| 用途 \| 可靠性 \| 封IP风险 \|
\|--------\|--------\|------\|--------\|---------\|
\| 1 \| \*\*mootdx\*\* (TCP) \| K线+五档盘口+逐笔成交+财务快照+F10 \| 极稳定 \| 极低 \|
\| 2 \| \*\*腾讯财经\*\* (HTTP) \| 实时PE/PB/市值/换手率/涨跌停/指数/ETF \| 稳定 \| 低 \|
\| 3 \| \*\*东财 datacenter\*\* (HTTP) \| 龙虎榜/解禁/融资融券/大宗交易/股东户数/分红/个股信息 \| 稳定 \| 低 \|
\| 4 \| \*\*东财 push2/push2his\*\* (HTTP) \| 行业板块/个股资金流分钟级+120日 \| 稳定 \| 低 \|
\| 5 \| \*\*iwencai\*\* (OpenAPI) \| NL主题搜索研报(唯一能力) \| 需X-Claw Header \| 低 \|
\| 6 \| \*\*东财 reportapi/PDF\*\* (HTTP) \| 完整研报图表、评级 \| 稳定 \| 低 \|
\| 7 \| \*\*同花顺热点\*\* (HTTP) \| 当日强势股+题材归因 reason tags \| 稳定 73ms \| 极低（零鉴权） \|
\| 8 \| \*\*同花顺 hsgtApi\*\* (HTTP) \| 北向资金分钟级+自缓存历史 \| 稳定 \| 极低（零鉴权） \|
\| 9 \| \*\*百度股市通\*\* (HTTP) \| 概念板块+K线带MA \| 稳定 \| 极低（零鉴权） \|
\| 10 \| \*\*新浪财经\*\* (HTTP) \| 资产负债表/利润表/现金流量表 \| 稳定 \| 低 \|
\| 11 \| \*\*同花顺 basic\*\* (HTTP) \| 一致预期EPS \| 稳定(需UA) \| 低 \|
\| 12 \| \*\*财联社\*\* (HTTP) \| 全市场实时电报 \| 稳定 \| 低 \|
\| 13 \| \*\*巨潮 cninfo\*\* (HTTP) \| 公告全文检索+下载 \| 稳定 \| 低 \|
\| 14 \| \*\*上交所官方\*\* (HTTP，备胎) \| 龙虎榜全文/实时五档（主源被封时用） \| 稳定（一手权威） \| 极低（零鉴权） \|
\| 15 \| \*\*深交所官方\*\* (HTTP，备胎) \| 龙虎榜/公告+PDF/实时五档（主源被封时用） \| 稳定（一手权威） \| 极低（零鉴权） \|

\\*\\*原则：\\*\\* 行情走 mootdx+腾讯（不封IP），研报走东财+iwencai，资金面走东财 datacenter+push2，\*\*信号层走同花顺+百度+东财直连接口\*\*。全部直连 HTTP，零第三方数据封装依赖。

\\*\\*降级：\\*\\* 任一主源被封/失效时，先查下方「备用源速查 & 降级策略」——每类数据都备有一条\*\*不同域名、不同风控面\*\*的独立备胎（交易所官方/新浪/同花顺），东财被封时它们不受牵连。

\-\-\-

\## 备用源速查 & 降级策略（东财/主源被封时用）

\\*\\*何时用：\\*\\* 主源报错 403/连接重置（东财 IP 级风控）、返回空、或需权威一手数据交叉验证时。\*\*东财系接口共用同一风控面，某台住宅 IP 被封会成片失联\*\*——下表给\*\*十类核心数据\*\*各一条独立备胎（不同域名、不同风控面；打板/期权/舆情三层暂无独立备胎）。表内端点均经 2026-07-11 实测存活、零鉴权可用，其中 3 个备胎函数另以真实数据完整跑通。

\| 数据类型 \| 主源(本 skill) \| 独立备胎 \| 备胎端点 / 说明 \|
\|---\|---\|---\|---\|
\| 实时行情+五档 \| mootdx/腾讯 \| 交易所官方 \| 沪 \`yunhq.sse.com.cn:32041/v1/sh1/snap/{code}\`、深 \`szse.cn/api/market/ssjjhq/getTimeData?marketId=1&code={code}\`（一手五档） \|
\| K线(全历史) \| mootdx/百度/腾讯 \| 同花顺 \| \`d.10jqka.com.cn/v6/line/hs\_{code}/01/last.js\`（01日/11周/21月/30/60分；2001至今；JSONP剥壳） \|
\| 龙虎榜 \| 东财 datacenter \| 沪深交易所官方 \| \`dragon\_tiger\_backup()\`（见下，含营业部席位） \|
\| 个股资金流 \| 东财 push2 \| 新浪 \| \`fund\_flow\_backup()\`（见下，日度四档单净额） \|
\| 公告 \| 巨潮 \| 深交所官方/东财 \| \`announcements\_backup()\`（见下，深市深交所+PDF，沪市东财+PDF） \|
\| 财务三表 \| 新浪/mootdx \| 同花顺 F10 \| \`basic.10jqka.com.cn/api/stock/finance/{code}\_debt.json\`（\`\_benefit\`利润/\`\_cash\`现金流；仅 UA，5连发不封） \|
\| 个股新闻 \| 东财 search \| 新浪7x24 \| \`zhibo.sina.com.cn/api/zhibo/feed?zhibo\_id=152&page\_size=20&dire=f\`（\`ext.stocks\` 带个股关联可过滤） \|
\| 快讯 \| 东财7x24(§5.3) \| 财联社(§5.2) \| 两条已互备；再加金十 \`jin10.com/flash\_newest.js\` \|
\| 券商评级+目标价 \| 同花顺一致预期 \| 巨潮 webapi \| \`p\_sysapi1089?tdate=YYYY-MM-DD\`，需头 \`Accept-Enckey\`=base64(AES-128-CBC(unix秒, key=iv=\`1234567887654321\`)) \|
\| 北向(权威) \| 同花顺 hexin \| HKEX 官方 \| \`hkex.com.hk/chi/csm/DailyStat/data\_tab\_daily\_{YYYYMMDD}c.js\`（成交额/额度/十大活跃股） \|

\> ⛔ \*\*已死透别用\*\*（2026-07 实测）：网易财经(126.net 整站下线)、和讯、凤凰行情、腾讯资金流(ff\_ 已死)、雪球免登录深度数据(需 token)。mootdx \*\*库\*\*已烂尾(2024 停更)但\*\*通达信 TCP 协议本身照常\*\*——继续用，装不上就用 \`tdx\_client()\`。

\`\`\`python
import json, urllib.request, ssl
\_ctx = ssl.create\_default\_context(); \_ctx.check\_hostname = False; \_ctx.verify\_mode = ssl.CERT\_NONE

def dragon\_tiger\_backup(trade\_date: str) -> dict:
 """龙虎榜官方备用源（东财被封时用）：上交所+深交所官方，零鉴权权威一手，含营业部席位。"""
 out = {"date": trade\_date, "sse\_raw": "", "szse": \[\]}
 su = (f"https://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON"
 f"&CATALOGID=1842\_xxpl&TABKEY=tab1&txtStart={trade\_date}&txtEnd={trade\_date}&random=0.9")
 req = urllib.request.Request(su, headers={"User-Agent": UA,
 "Referer": "https://www.szse.cn/disclosure/supervision/dealinfo/index.html"})
 with urllib.request.urlopen(req, timeout=15, context=\_ctx) as r:
 d = json.loads(r.read())
 for row in d\[0\].get("data", \[\]):
 out\["szse"\].append({"code": row.get("zqdm"), "name": row.get("zqjc"),
 "amount": row.get("cjje"), "reason": row.get("plyy")})
 eu = (f"https://query.sse.com.cn/infodisplay/showTradePublicFile.do?"
 f"jsonCallBack=cb&isPagination=false&dateTx={trade\_date}")
 req = urllib.request.Request(eu, headers={"User-Agent": UA,
 "Referer": "https://www.sse.com.cn/disclosure/diclosure/public/"})
 with urllib.request.urlopen(req, timeout=15) as r:
 t = r.read().decode("utf-8", "ignore")
 out\["sse\_raw"\] = "\\n".join(json.loads(t\[t.index("(")+1:t.rindex(")")\]).get("fileContents", \[\]))
 return out

def fund\_flow\_backup(code: str, days: int = 60) -> list:
 """个股资金流备用源（东财被封时用）：新浪，日度四档单净额。"""
 pre = ("sh" if code.startswith(("6", "9")) else "bj" if code.startswith("8") else "sz") + code
 u = (f"https://vip.stock.finance.sina.com.cn/quotes\_service/api/json\_v2.php/"
 f"MoneyFlow.ssl\_qsfx\_zjlrqs?page=1&num={days}&sort=opendate&asc=0&daima={pre}")
 req = urllib.request.Request(u, headers={"User-Agent": UA, "Referer": "https://finance.sina.com.cn/"})
 with urllib.request.urlopen(req, timeout=15) as r:
 t = r.read().decode("utf-8", "ignore")
 arr = json.loads(t\[t.index("\["):t.rindex("\]")+1\])
 return \[{"date": x.get("opendate"), "close": x.get("trade"),\
 "net\_amount": x.get("netamount"), "turnover": x.get("turnover")} for x in arr\]

def announcements\_backup(code: str, page\_size: int = 20) -> list:
 """公告备用源（巨潮被封时用）：深市走深交所官方，沪市走东财，均带 PDF 直链。"""
 if code.startswith(("0", "3")):
 body = json.dumps({"channelCode": \["listedNotice\_disc"\], "pageSize": page\_size,
 "pageNum": 1, "stock": \[code\]}).encode()
 req = urllib.request.Request("https://www.szse.cn/api/disc/announcement/annList", data=body,
 headers={"User-Agent": UA, "Content-Type": "application/json",
 "Referer": "https://www.szse.cn/disclosure/listed/notice/index.html"})
 with urllib.request.urlopen(req, timeout=15, context=\_ctx) as r:
 d = json.loads(r.read())
 return \[{"title": a.get("title"), "time": a.get("publishTime", "")\[:10\],\
 "pdf": "https://disc.static.szse.cn/download" + a.get("attachPath", "")}\
 for a in d.get("data", \[\])\]
 u = (f"https://np-anotice-stock.eastmoney.com/api/security/ann?sr=-1&page\_size={page\_size}"
 f"&page\_index=1&ann\_type=A&client\_source=web&stock\_list={code}&f\_node=0&s\_node=0")
 req = urllib.request.Request(u, headers={"User-Agent": UA})
 with urllib.request.urlopen(req, timeout=15) as r:
 d = json.loads(r.read())
 return \[{"title": a.get("title"), "time": a.get("notice\_date", "")\[:10\],\
 "pdf": f"https://pdf.dfcfw.com/pdf/H2\_{a.get('art\_code','')}\_1.pdf"}\
 for a in d.get("data", {}).get("list", \[\])\]

\# 用法（主源失败时降级）
lhb = dragon\_tiger\_backup("2026-07-10") # 深市结构化 + 沪市全文(含营业部)
flow = fund\_flow\_backup("600519", 60) # 近60日资金流
anns = announcements\_backup("000858") # 深市走深交所, 沪市走东财
\`\`\`

\-\-\-

\## FAQ

\### Q: 东财接口 403 / 连接重置，是被封了吗，怎么办？
A: 东财系接口（datacenter/push2/push2ex/reportapi/search/np-weblist）共用同一套风控，IP 被封会成片失联。三步处理：① 停止请求等 30-60 分钟（IP 级临时封通常自动解除），或换网络（手机热点）立刻恢复；② 长批任务确认全部走 \`em\_get()\`，并调大 \`EM\_MIN\_INTERVAL\`；③ 数据不能等 → 用上方「备用源速查 & 降级策略」的独立备胎（交易所官方/新浪/同花顺，不同风控面，东财被封时不受牵连）。

\### Q: 财联社快讯不是 V3.2 标注下线了吗？
A: 已复活（V3.4.0，见 §5.2）。2026-05 死的是旧 \`nodeapi\` 系接口；官方新版 \`v1/roll/get\_roll\_list\` 一直可用，只是强制 \`sign\` 校验——而 sign 纯本地可算（\`md5(sha1(按 key 字典序拼接的 query 串))\`），零 key。与 §5.3 东财 7×24 互为独立备份。

\### Q: mootdx 库听说停更了，还能用吗？
A: 库确实烂尾（最后 commit 2024-07，官网下线，BESTIP bug 无官方修复），但\*\*通达信 TCP 协议本身照常运行\*\*——烂尾的是封装库，不是数据源。本 skill 的 \`tdx\_client()\` 已内置 IP 探测绕开 BESTIP bug，继续用没问题。若未来 mootdx 装不上，社区活跃替代是 easy\_tdx（同协议，日常维护中）。

\### Q: mootdx 和腾讯有什么区别？
A: 互补关系。mootdx = 交易层（价格+盘口+K线），腾讯 = 估值层（PE/PB/市值/换手率/涨跌停价）。两者都不封IP。

\### Q: V3.0 为什么移除 akshare？
A: akshare 本质是对东财/同花顺/新浪等公开 API 的封装，中间层增加了故障点（版本兼容 bug、pandas 3.0 ArrowInvalid 等）。V3.0 直连底层 HTTP API，零中间依赖，更稳定可控。

\### Q: iwencai 返回 401
A: 检查两点：(1) API Key 是否有效 (2) 是否携带了 X-Claw-\* Headers。SkillHub 2.0 后必须带 X-Claw Headers，否则一律 401。

\### Q: 同花顺一致预期 ths\_eps\_forecast 返回空
A: 该股票无机构覆盖。小盘/次新/ST 股常见。可 fallback 到东财 reportapi 里的 predictThisYearEps 字段。

\### Q: 东财 PDF 下载 403
A: 必须带 \`Referer: https://data.eastmoney.com/\` header。

\### Q: 腾讯 API 返回乱码
A: 编码是 GBK，必须 \`decode("gbk")\`。

\### Q: 腾讯 API 字段 43 是 PB 吗？
A: \*\*不是！\*\* 43=振幅%，46=PB。网上很多教程写错了，这里是实测校准结果。

\### Q: iwencai search 返回条数太少
A: \`size\` 参数默认 10，调到 50。隐藏参数，文档未写明但实测可用。

\### Q: 哪些数据源需要 API Key？
A: 只有 iwencai 需要。mootdx / 腾讯 / 东财 / 同花顺 / 百度股市通 / 新浪 / 巨潮 / 财联社全部免费无 key。

\### Q: 同花顺热点接口需要 cookie 吗？
A: \*\*不需要\*\*。仅 User-Agent 即可，零鉴权 73ms 拿到 ~125 只当日强势股。但\*\*不要去打 search.10jqka.com.cn 的 iwencai NL 选股接口\*\* —— 那个有 hexin-v cookie JS 签名鉴权，跟热点接口完全两码事。

\### Q: 百度股市通 ResultCode 有时是 0 有时是 "0"？
A: 已知坑。\`ResultCode\` 返回类型不稳定——有时 int，有时 string。代码里必须用 \`str(d.get("ResultCode", -1)) != "0"\` 统一比较。

\### Q: 北向资金历史数据为什么只有最近几天？
A: 本地自缓存模式。eastmoney 全系北向数据自 2024-08 起断供（净买额字段返回 NaN/0）。每次调用实时 API 后自动写入本地 CSV，历史越跑越丰富。

\### Q: 行业板块为什么从同花顺换成东财？
A: 同花顺 \`stock\_board\_industry\_summary\_ths\` 接口 2026 年初加了反爬 401（需要登录态）。东财 push2 行业板块数据（\`m:90+t:2\`）是完美替代，零鉴权且字段更丰富。

\### Q: 在海外服务器跑，mootdx 接口超时？
A: mootdx 走 TCP 直连通达信行情服务器，需国内 IP 才稳定。海外环境建议走代理。腾讯财经和百度股市通不受影响。

\### Q: 不用 Claude Code，能用吗？
A: 能。SKILL.md 本质是 Markdown + 内嵌 Python 代码。Codex、OpenClaw 或任何 AI 编程助手都能读取。你也可以直接把 Python 代码段复制出来在自己的脚本里跑。

\-\-\-

\## 安装说明

\`\`\`bash
\# 1\. 创建 skill 目录
mkdir -p ~/.claude/skills/a-stock-data

\# 2\. 将本文件复制为 SKILL.md
cp SKILL.md ~/.claude/skills/a-stock-data/SKILL.md

\# 3\. 安装 Python 依赖
pip install mootdx requests pandas stockstats

\# 4\. (可选) 配置 iwencai API Key
export IWENCAI\_API\_KEY="your\_key\_here"

\# 5\. 启动 Claude Code，说"查一下688017的估值"即可自动激活
\`\`\`

\-\-\-

\> 📦 https://github.com/simonlin1212/a-stock-data — Star ⭐ 是最好的支持