---
name: fund-decision-verify
title: 基金决策验证与策略理论系统
category: investment
triggers:
  - User asks about decision verification / 回测 / 决策验证
  - User asks about strategy theory / 策略理论 / 策略依据
  - Developing or modifying execute_today_plan.py
  - Evaluating past buy/sell decisions
  - 基金代码截断 / 代码不完整 / code[-4:]
  - 建仓策略 / 双轨策略 / 追涨追跌
  - 减仓逻辑不合理 / 死扛 / 等反弹
  - 板块代理估算 / 基金实时估值失效 / sector proxy
  - 策略标签 / 策略优先级 / 自校验 / self-validate
  - 报告管线数据同步 / report pipeline / closing_review.py / send_closing.py
description: 基金决策推送的三大核心：多日趋势判定 + 策略理论库 + 历史决策验证闭环
---

# 基金决策验证与策略理论系统

## 系统架构

```
execute_today_plan.py (no_agent cron, 9:35/14:30)
  ├── ① 交易日判定 → AKShare tool_trade_date_hist_sina()
  ├── ② 持仓构建 → seed_portfolio.json + operations/operation_*.md
  ├── ③ 多日趋势 → AKShare fund_open_fund_info_em() 近3/5日逐日涨跌
  ├── ④ 策略建议 → 减仓/建仓决策 + 策略理论引用
  ├── ⑤ 验证闭环 → verify_past_decisions() 历史买入回溯
  ├── ⑥ 日志记录 → trade_decisions.jsonl 存快照供未来验证
  └── ⑦ QQ推送 → send_qq_bot.send_markdown() msg_type:2 直推送

存于: /opt/data/scripts/execute_today_plan.py
cron: 基金决策-开盘后(9:35) + 基金决策-14:30决策点 (均为 no_agent)
```

## v2 LLM深度分析集成

自2026-07-20起，`execute_today_plan.py` 在规则系统之上叠加 **v2 LLM分析**（`llm_analysis_v2.py`）。

**时段切换**：14:30→`generate_v2('decision')`，09:35→`generate_v2('morning')`

**v2增量能力**：
- KOL观点交叉验证（主任/小浣熊）
- 市场新闻（RSS 30+源，分类标签🤖⚡🏛️🥇）
- 5日指数趋势表（daily-snapshots.jsonl）
- 实时持仓盈亏（成本/市值/盈亏率）
- 置信度评分（每个判断1-10）
- 情景推演（3种+概率）
- 昨日预测回溯验证

**降级链**：进化引擎双阶段→单次DeepSeek→静默降级（规则系统照常）

**输出流程**：规则系统→print(advice) → stdout + v2 LLM→print(format_block()) → stdout → cron no_agent 捕获 → QQ Bot

## 调用方式

**自动调用**（无需手动触发）：
- 工作日 9:35 → 开盘后决策推送（仅观察，不出建议）
- 工作日 14:30 → 尾盘决策推送（出具体操作建议）
- 脚本内用 `send_qq_bot.send_markdown()` 以 `msg_type: 2` 推送（主力）
- cron stdout 交付为备援（纯文本，不渲染表格）

**手动调用**：
```bash
cd /opt/data && python3 /opt/data/scripts/execute_today_plan.py
```

**手动操作净值更新**：
```bash
timeout 60 python3 /opt/data/profiles/investment/scripts/update_operation_nav.py
```

**验证历史决策**（独立调用）：
```python
from execute_today_plan import verify_past_decisions
results = verify_past_decisions()
# 返回 [{code, name, buy_date, days_held, buy_nav, cur_nav, ret, bench_ret, verdict}]
```

## 时段策略（T+1基金适配）

| 时段 | 模式 | 行为 |
|:----|:----|:-----|
| 🕤 **09:35** | 盘前观察 | 仅看市场方向，**不出具体操作建议**。提示等14:30 |
| 🕝 **14:30** | 午后决策 | 基于全天趋势给出买入/卖出推荐 |

**核心原则**：基金T+1以15:00净值确认，早盘操作与午后操作按同一净值结算。早盘不需要操作。

**9:35推送**：大盘趋势 + 持仓诊断 + 减仓建议（仅回撤提示）+ 建仓进度 + 统一标注等14:30
**14:30推送**：同上 + 今日判定出具体买入/减仓建议

### 14:30报告双轨设计原则（2026-07-21用户纠正，最终版）

**核心原则：QQ=概览（30秒读完），R2=翔实（同早报级别含AI分析）。** 14:30是操作时间，但操作建议需要AI分析来支撑依据。两者不是二选一，而是不同层级的信息。

| 层级 | 目标 | 内容 |
|:----|:-----|:-----|
| 📱 **QQ消息** | 30秒读完，可执行 | 市场快照3行 + 关键操作(只列有动作的基金) + AI一句话理由(取第一段去换行限150字) + MD/HTML链接 |
| 🖥️ **R2报告** | 完整可查阅，含依据 | 行情表 + 板块排行 + 量价分析 + 北向 + 持仓全表(14支) + 操作表 + AI深度分析(v2 4步) |

**QQ消息标准模板**（2026-07-21最终版）：
```
📊 07/21 14:30 决策
📊 上证 3819 🔴0.62% | 科创 1837 🔴6.94% | 创业板 3622 🔴5.20% | 沪深 4679 🔴1.76%
🔥 半导体+8.3% 通信+6.2% 新能源+3.4%
🌊 北向资金: 沪+16亿 深+37亿 合计+53亿

⚡ 操作: 163302 大摩资源→📉减半(~108元)

💡 今日市场大幅反弹，但主要持仓仍深套，未触发止盈条件，仅对回撤较小且连跌的大摩资源执行减半…

📄 https://.../decision_2026-07-21.md
🌐 https://.../decision_2026-07-21.html
```

**R2报告内容**（翔实版，与早报同级别，必须包含以下6个章节）：
| 章节 | 来源 |
|:----|:-----|
| 盘中行情（指数表+涨跌幅🔴🟢） | `/tmp/fund_data/_noon_market.txt` |
| 板块表现（10行业+排行） | `/tmp/fund_data/_noon_sector.txt` |
| 量价分析（11品种量价信号表） | `/tmp/fund_data/_noon_volume.txt` |
| 北向资金（沪/深/合计） | `/tmp/fund_data/_noon_northbound.txt` |
| 持仓与操作（全14支基金3日/高点回撤+操作表） | `execute_today_plan.py` 完整stdout |
| AI深度分析（全市场画像→赛道诊断→逐基金评分→风险检查） | `generate_v2("decision")` 输出 |

### 实现方式（run_execute_plan.py wrapper）

```python
# Step 1: 规则引擎 → 操作建议
r = subprocess.run(['execute_today_plan.py'], capture_output=True, text=True, timeout=300)
clean = [l for l in stdout.split('\n') if not l.strip().startswith(('⚠️','✅','❌'))]
full_advice = '\n'.join(clean)

# Step 2: AI深度分析
from llm_analysis_v2 import generate_v2
analysis = generate_v2("decision", use_cache=True) or generate_v2("decision", use_cache=False)

# Step 3: 静默上传R2
from push_report_r2 import push_report
import io
old_stdout = sys.stdout
sys.stdout = io.StringIO()
md, html = push_report("decision", title, data_tables + '\n\n## 操作建议\n\n' + advice, analysis)
sys.stdout = old_stdout

# Step 4: QQ概览
qq = [f"📊 {today} 14:30 决策"]
for l in lines:
    if l.startswith(('📊','🔥','🌊')): qq.append(l)
actions = [a for a in lines if '|' in a and ('📉' in a or '📈' in a)][:3]
if actions: qq.append(f"⚡ 操作: ...")
if analysis:
    first = analysis.split('\n\n')[0]
    short = re.sub(r'#+\s*', '', first).replace('**','').replace('\n',' ')[:150]
    qq.append(f"💡 {short}")
qq.extend([f"📄 {md}", f"🌐 {html}"])
_output('\n'.join(qq))
```

**关键技术细节**：
- push_report内部摘要用 `sys.stdout = io.StringIO()` 抑制
- AI理由取第一段，去#号/去换行/限150字
- 过滤AKShare预警行（fund_source_akshare的print走stderr，但get_all_funds的✅/❌走stdout）
- 非交易日跳过（`date.today().weekday() >= 5`）

### Prompt设计原则（2026-07-21用户纠正）

**不要硬编码持仓数据。** 从FUND_CODES和seed_portfolio.json动态读取。

**不要过度约束AI判断。** 给AI完整数据，让AI自己分析。约束只保留事实性规则（建仓基金不能卖、代码不准编造）。

```python
# ✅ 动态读取持仓
from fund_tools import FUND_CODES
from llm_analysis_v2 import BUILDING_FUNDS
for code, name in FUND_CODES.items():
    flag = "🏗️建仓期" if code in BUILDING_FUNDS else ""
    portfolio_list_lines.append(f"  {code} {name} {flag}")
```

**对比：**
| 错误做法 | 正确做法 |
|:---------|:---------|
| 硬编码fund_names字典 | 从FUND_CODES动态读取 |
| ❌「严禁推荐非持仓基金」 | ✅「推荐新基金需标注+给理由+用正确代码」 |

## 减仓原则（趋势+回撤+仓位集中度 三维判定）

**不要写死规则，要让LLM分析数据后自行判断。** 用户明确指出：「操作规则不应该写死，应该是经过LLM实际分析才给的」。

| 错误（以前做的） | 正确（用户要求的） |
|:----------------|:-----------------|
| ❌ 写死「累计亏损>8%→减半仓」 | ✅ 给LLM完整数据，让它自己判断阈值 |
| ❌ 写死「单日暴跌8%+不要追卖」 | ✅ 给LLM市场数据+持仓P&L，由它分析极端超卖 |
| ❌ 写死「赛道配比45%/15%/10%」 | ✅ 作为参考方向，让LLM基于市场变化动态调整 |

### 只保留的约束（事实性规则，不可变）
- 15:00前下单按今日收盘净值成交（净值收盘后公布，下单时未知）
- 15:00后下单按下个交易日净值成交
- 份额T+1到账，赎回资金T+2到账
- 建仓期基金(003096/013403)仅允许持有或可加仓
- 估算净值≠实际成交净值
- **深套约束**：回撤超过20%的基金，严禁建议"止盈/减仓/卖出"。回撤超过25%的基金，只允许「持有不动」
- **超配约束**：科技占比超过65%时，严禁建议加仓任何科技类基金。即使在深套状态下，正确路径是"持有不动，等待反弹至-15%以内再评估减仓"。禁止回调补仓行为。

### 框架性指导（作为分析视角，不写具体数字）
| 分析视角 | 含义 |
|:---------|:-----|
| 趋势跟踪 | 单日≠趋势，结合量价判断方向 |
| 风险控制 | 注意分散和系统性风险 |
| 仓位管理 | 分批操作，避免满仓 |
| 再平衡 | 关注偏离度，优先增量资金调整 |
| 组合监控 | 定期复盘，避免频繁交易 |

**实现方式**（execute_today_plan.py）：
- 遍历全部14只基金
- 每只检查 drawdown + 3日趋势 + 科技占比
- 减仓段与今日操作段共享同一份判断代码（避免输出矛盾）
- 深度套牢基金即使科技超配也标记为"不动"

### 旧逻辑缺陷修复（2026-07-20）
| 旧问题 | 修复 |
|:-------|:-----|
| 仅检查3只基金 | 遍历全部14只 |
| 仅凭drawdown单一维度 | 三维联合判断 |
| 减仓段与操作段矛盾 | 共享同一份判断代码 |

## QQ Bot 推送代码模式

必须主动调用 API，不能依赖 cron 的纯文本交付：

```python
try:
    sys.path.insert(0, '/opt/data/scripts')
    from send_qq_bot import send_markdown
    ok = send_markdown(advice)
except Exception as e:
    print(f"[QQ推送失败: {e}]", file=sys.stderr)
```

**QQ Bot Markdown 支持格式**: `#`标题 `##`子标题 `**粗体**` `_斜体_` `>引用` `---`分割线 `-`列表 `|表格|`

## 策略理论库

每条操作建议附带策略理论依据：

```python
STRATEGY = {
    '建仓（新买入）':   '仅新建仓基金。分批建仓：首仓→观察→确认→补仓',
    '加仓（追加买入）': '已有持仓且趋势向上、净值相对低位时。给出建议金额',
    '持有（不动）':     '方向不明或趋势中性。大部分时间应该持有',
    '减仓（部分卖出）': '趋势走坏、需降低风险敞口。给出建议比例（如减30%）',
    '清仓（全部卖出）': '累计亏损>15%、赛道逻辑彻底破坏、长期垫底。注意资金T+2到账',
    '金字塔建仓':     '等回调3-5%金字塔分批—单批≤1/3',
    '止盈防回撤':     'YTD涨超50%部分止盈—回撤15%暂停加仓',
    '同质化减仓':     '同基金经理多支重叠→名义分散实则集中',
    '等反弹再减':     '回撤较深，等反弹至-10%以内再执行',
    '大跌观望':       '单日跌>3%不买不卖—急跌易惯性下探',
    '反弹减仓':       '科创50反弹≥+2%执行减仓—高流动性窗口',
    '云厂对冲':       '主任配了点云厂做对冲→港股科技替代',
    '趋势跟踪':       '连续3日下跌合计>-5%走弱减仓；上涨>+5%持有',
}
```

### 止损/止盈原则（框架性参考）

**一天暴跌8%和一周阴跌8%是完全不同的场景，不能套同一个规则。** LLM应基于实际数据判断。把每支基金的实时P&L、多日趋势、市场环境都给LLM。

### 基金评分系统（三维度+总分）

| 维度 | 范围 | 依据 |
|:----|:----:|:-----|
| 技术分 | 1-10 | 当日涨跌、量价关系、位置 |
| 资金分 | 1-10 | 北向态度、成交额变化 |
| 趋势分 | 1-10 | 多日趋势方向 |
| 总分 | 1-10 | (技术+资金+趋势)/3 |

### 同赛道基金对比与冗余优化

周度复盘中检查组合冗余度。清理原则：保留表现最好的2-3支，清仓最差的。

## 历史决策验证

评判标准（考虑大盘基准）：
- `ret > 0` → ✅ 正收益
- `ret - bench > -2` → 🟡 和大盘接近
- `ret - bench < -5` → ❌ 远差于大盘

## 关键文件

| 文件 | 路径 | 说明 |
|:----|:----|:-----|
| 主脚本 | `/opt/data/scripts/execute_today_plan.py` | no_agent cron |
| 净值更新 | `/opt/data/scripts/update_operation_nav.py` | 确认买入份额 |
| 部署陷阱 | `references/deployment-pitfalls.md` | 10条已踩过的坑 |
| R2推送方案 | `references/r2-report-push.md` | MD+HTML R2推送 |
| v4策略引擎 | `references/v4-strategy-engine.md` | FUND_SECTOR_MAP + 策略优先级 + 自校验 |

## 数据计算坑

**近1月/近1周数据用前推法，不用固定日期法。** 固定日期法在基金先涨后跌时会抵消涨跌幅。

**必须同时计算 1周/1月/3月/今年 四个维度。**

**基金持仓金额必须用真实成本数据**（trade_decisions.jsonl的cost字段），不能估算。

## 操作记录目录（operations/）的依赖性

`parse_ops()` 必须能扫到 operation_*.md 文件，否则建仓追踪始终为0%。

**常见故障：R2同步失败** — 用户操作记录在R2但本地未同步。从R2下载修复。

## 持仓构建 — 从seed_portfolio.json动态读取

**已从硬编码base字典迁移到动态seed文件模式。** seed文件包含初始成本 + 建仓计划。操作记录叠加。

### seed_portfolio.json 结构
```json
{
    "funds": {
        "011613": {"name": "华夏科创50ETF联接C", "cost": 1401.98},
        "003096": {"name": "中欧医疗健康混合C", "cost": 0}
    },
    "building_plan": {
        "003096": {"name": "中欧医疗健康混合C", "target": 370},
        "013403": {"name": "华夏恒生科技ETF联接(QDII)C", "target": 300}
    }
}
```

**基金名称必须与 FUND_CODES 完全一致。** 024418/013403曾在2026-07-21修复过名称不一致。新加基金时三处同步：FUND_CODES + seed_portfolio.json + FUND_SECTOR_MAP。

## v4 规则引擎架构（2026-07-21）

### 四链路数据管线

```
链路A(最优): AKShare全量实时估算 ← 主线程调用 fund_value_estimation_em() (~20秒)
链路B(主用): 板块代理 ← 中午采集 /tmp/fund_data/_noon_sector.txt
链路C(辅助): 昨日市值基线 ← daily-snapshots.jsonl
链路D(备援): 历史净值 ← AKShare fund_open_fund_info_em(60日)
```

**基金实时估算优先顺序：AKShare > 板块代理 > 0%**

### AKShare实时估算统一接入规范

所有需要基金当日实时估算的脚本必须按此模式接入：

```python
import akshare as ak
df = ak.fund_value_estimation_em()  # 一次性20000+基金，~20秒
est_col = [c for c in df.columns if '估算增长率' in c]
if est_col:
    for _, row in df.iterrows():
        code = str(row['基金代码'])
        if code in FUND_CODES:
            val = str(row.get(est_col[0], '0')).replace('%', '').strip()
            fund_realtime[code] = float(val) if val and val != '---' else 0.0
```

**规则：**
1. 必须在主线程调用（不在ThreadPoolExecutor内）
2. 一次性调用全量API后过滤，不逐只获取
3. 覆盖所有旧数据，不检查旧值（旧数据可能非0但来自历史净值）

**已接入脚本：**
- `execute_today_plan.py` — `build_portfolio()` 中 `get_all_funds()` 后AKShare覆盖
- `closing_review.py` — `funds_now = get_all_funds()` 后立即覆盖
- `llm_analysis_v2.py` — `build_closing_data_v2()` 和 `build_decision_data_v2()` 内

### 板块代理估算（链路B备援）

```python
FUND_SECTOR_MAP = {
    '009478': '黄金ETF市场价',  '011613': '科创50',   '024418': '半导体',
    '026449': '恒生科技ETF',    '014871': '半导体',   '020233': '半导体',
    '017103': '通信',           '011712': '通信',     '163302': '有色金属',
    '025857': '新能源',         '012329': '新能源',   '011103': '光伏',
    '003096': '医药',           '013403': '恒生科技ETF',
}
```

### 组合市值计算

**正确**：`今日市值 = 昨日市值(daily-snapshots.jsonl) × (1 + AKShare估算变动%)`
**错误**（已废弃）：`今日市值 = 成本 × (1 + 估算变动%)`（忽略前几日累积亏损，虚高）

### group_funds() code注入
`fund_tools.py` 的 `group_funds()` 在循环内注入 `v['code'] = code`（2026-07-21修复），解决下游报表持仓表基金名称为空的问题。下游用 `FUND_CODES.get(f.get('code', ''), f.get('name', '?'))` 取全名。

### 策略引擎v4：策略标签 + 优先级排序

| 策略 | 标签 | 触发条件 | 操作 |
|:----|:----|:---------|:-----|
| 回撤阶梯 | `[回撤阶梯]` | drawdown -8%~-15% + d3<-3% | 📉减半 |
| 回撤阶梯 | `[回撤阶梯]` | drawdown -15%~-25% + d3<-5% | 🟡持有(设-10%止盈) |
| 回撤阶梯 | `[回撤阶梯]` | drawdown < -25% | 🟡深套等反弹 |
| 科技再平衡 | `[科技再平衡]` | tech_pct>65% + ec>=0 + drawdown>=-15% | 📉减1/3 |
| 建仓双轨 | `[建仓双轨]` | 建仓基金 + ec<-4% | 📈加仓(均值回归) |
| 建仓双轨 | `[建仓双轨]` | 建仓基金 + ec>+5% | 📈加仓(追强) |
| 趋势跟踪 | `[趋势跟踪]` | 3日累计<-8% | 🟡持有(等企稳) |
| 安全 | `[安全]` | 无触发 | 🟡持有 |

优先级：建仓双轨 > -25%深套 > -15%止盈 > -8%连跌 > 科技再平衡 > 安全。

### 自校验系统

`self_validate(portfolio, advice)` 检查：基金数量、AKShare覆盖率、操作表全量覆盖、建仓基金出现、科技>65%策略预警。stderr输出校验结果，stdout只输出建议。

### ⚠️ 推送前自验证检查清单（2026-07-21用户核心纠正）

每次声称"修好了/已完成"前，必须执行以下自验证：

### 1. 查看实际渲染输出
不要只看原始数据/日志。必须抓取HTML/MD在线URL，肉眼确认每个字段渲染正确。

### 2. 逻辑自洽性（最重要的检查）
- AI建议是否符合持仓实际状态？（如深套-33%的基金不能推荐"止盈"）
- 数据表与AI分析的涨跌数据是否一致？
- 同一份报告里的操作建议与数据表有无矛盾？

### 3. CDN缓存验证
修复R2报告后，必须：
```bash
# 用curl直接验证（不用web_extract，它有自身缓存层）
curl -s 'https://...report.html' | grep '关键数据字段'

# 检查last-modified是否更新
curl -s -D- 'https://...report.html' | grep -i 'last-modified'

# 如有需要，强制上传刷新CDN
python3 -c "from fund_tools import upload_to_r2 as up; up(str(local_path), 'r2-key', 'mime')"
```

### 4. 交叉验证
- 对比上下游数据一致性（data_tables vs AI分析的基金涨跌是否匹配）
- 多数据源横向对比（板块ETF vs 基金估算 vs AKShare实时）

### 5. 异常值扫描
检查报告中 None/NULL/0.00%/空字符串 等占位符是否合理。
- 估算净值None → 是否已手动计算？（nav × (1+est_change%)）
- 基金名称为空 → group_funds注入code了吗？

### 6. 逐基金核对
每支基金检查四条数据：代码正确 / 名称完整 / 估算涨跌合理 / 操作建议与回撤匹配

### 7. 全量推送前
修好代码后，不要只跑一次就催用户"请检查"。**自己跑一次完整流程**，确认输出正确再通知用户。

参考脚本：`/opt/data/scripts/verify_data_sources.py`

## ⚠️ 验证方法论（2026-07-21用户纠正）

不要只检查「数据存在与否」就声称修好了。必须执行表层→逻辑层验证：

1. **查看实际渲染输出**（HTML/MD），确认每个字段显示正确，而非只看原始数据
2. **逻辑自洽性检查**：AI建议是否符合持仓实际状态（如深套-33%的基金不能推荐止盈）
3. **交叉验证**：对比上下游数据一致性（data_tables vs AI分析的基金涨跌是否匹配）
4. **扫描异常值**：检查报告中 None/NULL/0.00% 等占位符是否合理
5. **逐基金核对**：验证每支基金的 代码/名称/估算涨跌/操作建议 四条数据正确

参考脚本：`verify_data_sources.py`。

## 收盘复盘AI分析的深套约束（2026-07-21关键修复）

**问题场景**：CLOSING_PROMPT_V2 没告知AI持仓深套状态。AI看到024418涨+15.8%就建议"减仓止盈"，但该基金实际回撤-33.3%。

**修复方法**：在 CLOSING_PROMPT_V2 步骤3后增加约束段落，明确回撤阈值对应的禁止操作：
```
⚠️ 【持仓状态约束 — 必须遵守】
对于回撤超过20%的基金，严禁建议"止盈/减仓/卖出"。
只允许："持有等待反弹至-15%以内再评估" 或 "继续持有，观望"
对于回撤超过25%的基金，只允许「持有不动」。
```
同时 `build_closing_data_v2()` 注入每支基金的回撤数据供AI参考。

**验证**：检查 AI分析中「止盈+深套基金代码」是否同时出现：`'止盈' in analysis and '024418' in analysis` → 验证失败。

## 收盘复盘数据管线（closing_review.py）

与 execute_today_plan.py 共享同样的修复：

| 修复点 | 文件 | 说明 |
|:-------|:-----|:------|
| AKShare全量覆盖 | closing_review.py | get_all_funds() 后用 bulk API 无条件覆盖14支 |
| estimated_nav计算 | closing_review.py + llm_analysis_v2.py | nav × (1+est_change%) |
| 基金名注入 | fund_tools.py | group_funds() 注入 v['code'] = code |
| AI深套约束 | llm_analysis_v2.py | CLOSING_PROMPT_V2 + build_closing_data_v2() |

详见 `references/closing-report-deep-drawdown-fix.md`。

## 建仓策略：双轨策略

用60日收盘数据计算日波动率σ，设定1σ双轨：跌穿下轨→DCA买入，突破上轨→追强买入。

恐慌期（科技1周跌>10%）阈值翻倍：正常期1σ→恐慌期2σ。恐慌缓解后恢复。

## 推送渲染陷阱

- `<br>` 标签在QQ Bot不渲染：替换为 `\n`
- `format_block(title, content)` 签名不能变
- `generate_v2()` 走进化引擎可能超时（~70s），改为直接 `call_ds()` (~20s)

## LLM输出截断解决方案

1. 精简prompt（去掉冗长框架，用紧凑格式）
2. 前简后详（前面的步骤简洁，关键步骤详细）
3. 紧凑指令（一行一个步骤）

## R2报告推送方案

`push_report(report_type, title, data_tables, analysis)` → MD+HTML上传R2。QQ推短摘要+链接。HTML需卡片布局+颜色标记+自适应。

## 数据源交叉验证

```bash
cd /opt/data/scripts && python3 verify_data_sources.py
```
检查：基金数量一致性(14支)、名称匹配、操作记录全覆盖。

## 部署陷阱速查

详见 `references/deployment-pitfalls.md`:

1. **CRON文件路径** — profiles下不要用symlink。用wrapper脚本。
2. **新增基金遗漏** — 5处同步更新
3. **同名cron冗余** — 修改后检查同名旧任务
4. **AKShare超时** — 必须ThreadPoolExecutor并行
5. **深跌减仓** — 加入drawdown回撤保护
6. **9:35不建议** — T+1早盘=午后，只观察
7. **QQ渲染** — 必须send_qq_bot.send_markdown()非cron交付
8. **基金代码截断** — 禁止`code[-4:]`，必须完整6位
9. **建仓基金排除减仓区** — BUILDING_CODES跳过
