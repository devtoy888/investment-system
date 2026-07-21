# 🗺 投资实用看板 · 完整设计&开发方案

> 评估日期：2026-07-21
> 参考项目：Vibe-Research（UI/UX）、Vibe-Trading（策略框架）
> 当前系统：cron触发式推送 + 静态dashboard + R2存储

---

## 目录

1. [现状全量盘点](#1-现状全量盘点)
2. [参考项目拆解](#2-参考项目拆解)
3. [核心差距分析](#3-核心差距分析)
4. [看板设计原则](#4-看板设计原则)
5. [页面体系（完整规格）](#5-页面体系完整规格)
6. [数据流设计](#6-数据流设计)
7. [技术方案选型](#7-技术方案选型)
8. [分阶段实施路线](#8-分阶段实施路线)
9. [开发规范](#9-开发规范)
10. [附录：与现有系统的集成点](#10-附录与现有系统的集成点)

---

## 1. 现状全量盘点

### 1.1 已建设施（什么是好的）

| 模块 | 状态 | 优势 |
|------|------|------|
| 数据采集层 | ✅ 稳定 | 腾讯行情 ~2s、天天基金 ~3-8s、外盘 Yahoo ~3s、板块+成交额+涨跌家数 |
| 推送系统（早/午/收/周末） | ✅ 已验证 | 8:00/11:35/16:00/周六09:00/周日20:00，5段推送全覆盖 |
| 风险预警 | ✅ 已验证 | risk_warning.py 单日>5%暴跌+连跌3日检测 |
| 偏离度检测 | ✅ 已验证 | check_allocation.py 科技/AI占比86%🔴 |
| 信号引擎 | ✅ 已验证 | signal_engine.py + YAML规则，已集成加仓信号监控 |
| KOL系统 | ✅ 已验证 | 唐史主任+小浣熊双源，看门狗自动续凭据 |
| 决策验证 | ✅ 已上线 | decisions.jsonl + daily-snapshots.jsonl + 3天验证 |
| 持仓管理 | ✅ 已上线 | seed_portfolio.json + 每日portfolio快照 + 操作记录 |
| LLM分析 | ✅ 已接入 | DeepSeek v4 Flash，每份推送带AI分析 |
| R2归档 | ✅ 稳定 | 所有报告+数据自动上传，手机可查看 |

### 1.2 现有Dashboard（什么是差的）

当前 `dashboard.html` （`/opt/data/fund_system_data/reports/dashboard.html`）：

**功能清单**：5张摘要卡 + 5份报告质量卡 + 预测准确率柱状图 + 操作信号格

**缺陷**：
- ❌ 纯文本摘要，没有实时行情展示
- ❌ 预测准确率全是同一天的数据（07-21重复23次），数据源bug
- ❌ 没有持仓盈亏视图
- ❌ 没有板块热度图
- ❌ 没有KOL信号聚合时间线
- ❌ 没有操作建议的可追溯性（"买入1次"但不知道是什么）
- ❌ 静态HTML，无交互（只有暗色模式切换）
- ❌ 手机端排版简陋，不是真SPA
- ❌ 无导航体系，只有一个页面

### 1.3 当前系统技术约束

```
├── 服务器: Oracle ARM (2C11G45G)
├── 前端部署: R2静态存储 (CDN)
├── 数据更新: cron驱动，非实时WebSocket
├── 推送渠道: QQ Bot (纯文字+emoji)
├── 报告载体: md+html成对上传R2
├── 核心约束: 不引入Node.js/Python后端新服务
└── 用户习惯: 手机浏览器查看R2页面
```

---

## 2. 参考项目拆解

### 2.1 Vibe-Research（UI/UX参考）

**仓库**：github.com/simonlin1212/Vibe-Research

**页面体系**（React+TypeScript+Tailwind）：

| 页面 | 核心内容 | 可借鉴点 |
|------|---------|---------|
| `DailyReview.tsx` | 大盘指数+全球市场+自选行情+短线情绪+成交额TOP20+板块资金+AI复盘 | ✅ 板块资金轮动可视化 ✅ 一屏看全的设计 ✅ 暗色玻璃主题 |
| `Intel.tsx` | 12赛道108个公开RSS源+AI提炼 | ❌ 对我们不适用（我们有KOL信号替代） |
| `Portfolio.tsx` | 持仓录入+成本+盈亏+清仓记录 | ✅ 盈亏可视化 ✅ 成本精度 |
| `StockData.tsx` | 个股估值+财报+资金面 | ✅ 估值分位设计 ✅ 多维tab布局 |
| `Sectors.tsx` | 板块+产业链 | ✅ 板块热度可视化 |
| `Watchlist.tsx` | 批量加自选+表格总览 | ✅ 表格数据展示规范 |
| `Notes.tsx` | 研究记录沉淀 | 轻量化 |

**设计亮点**：
- 侧栏导航 + 子路由，一级功能平铺
- 玻璃暖橙主题（`#f59e0b`暖色系）
- 数据卡片都是`rounded-xl + shadow-sm`风格
- 暗色模式系统偏好检测
- 表格列宽优化、数字右对齐、涨跌色

**技术栈**：React 19 + TypeScript + Vite + Tailwind + shadcn/ui

### 2.2 Vibe-Trading（策略参考）

**仓库**：github.com/HKUDS/Vibe-Trading

**可借鉴策略模块**：

| 模块 | 我们是否已有 | 可借鉴点 |
|------|-------------|---------|
| Signal Engine (YAML配置化) | ✅ 已有 `signal_engine.py` | 信号强度/置信度分级 |
| 因子算子库 | ⚠️ 有`fund_factors.py` | 扩展因子（夏普/卡玛/索提诺） |
| 基准对比 | ✅ 已有 `check_benchmark.py` | Benchmark多维度化 |
| 组合优化器 | ❌ | MPT有效前沿、最大夏普等 |
| Shadow Account | ❌ | 行为诊断（当前可忽略，资金量小） |
| 交易费用模型 | ✅ 已有 `fund_fee_model.py` | C类赎回费梯度已实现 |
| 回测引擎 | ❌ | 可轻量实现（信号→模拟收益） |

**关键启发**：VT-1~VT-8已评估并部分实现。新看板应该**聚焦展示层**，不重复造策略轮子。

---

## 3. 核心差距分析

### 3.1 用户真正需要什么

当前系统**数据充裕但视觉贫瘠**：

```
数据层  →  cron脚本  →  QQ推送  ✅ 几乎完美
数据层  →  cron脚本  →  R2报告  ✅ 可用但不够直观
数据层  →  现有dashboard  →  手机查看  ❌ 信息密度和交互不足
```

用户需要的**实用看板**是：
1. **一屏看清所有持仓**的盈亏状态（当前靠QQ推送一条条翻）
2. **趋势可视化**——K线/曲线代替数字
3. **操作回溯**——为什么买/为什么卖、结果如何
4. **决策支持**——不替代LLM分析，但提供数据上下文
5. **手机优先**——所有页面在手机上流畅操作

### 3.2 不应该做什么

| 不要做 | 原因 |
|--------|------|
| ❌ 实时WebSocket行情 | 服务器不跑node，且需要维护长连接 |
| ❌ 注册登录系统 | 个人用，不需要 |
| ❌ 个股/行业全量搜索 | A股4000+只，不是我们的场景（只关注14支基金） |
| ❌ AI对话式看板 | LLM分析已经集成在推送中，看板是数据展示 |
| ❌ 回测引擎 | 资金量小(~6426元)，回测没有实际意义 |
| ❌ 从零搭React/Vue全家桶 | 增加维护负担，静态SPA+JS就够了 |

### 3.3 应该做什么

| 要做 | 优先级 | 说明 |
|------|--------|------|
| ✅ 持仓总览（含盈亏） | P0 | 核心需求，替代QQ翻看 |
| ✅ 板块热度可视化 | P0 | 辅助判断轮动 |
| ✅ 操作记录时间线 | P0 | 可追溯 |
| ✅ 大盘+外盘实时行情 | P0 | 开屏第一眼 |
| ✅ 组合偏离度仪表 | P0 | 84%科技超配的警示 |
| ✅ 预测准确率追踪 | P1 | 已有数据，展示改进 |
| ✅ KOL信号时间线 | P1 | 已采集394条，可视化 |
| ✅ 基金详情页 | P1 | 单支基金深度数据 |
| ✅ 信号引擎状态 | P1 | 哪些信号触发了 |
| ✅ 系统健康状态 | P2 | 数据源可用率 |

---

## 4. 看板设计原则

### 4.1 核心理念

```
数据驱动     →  每个数字都可追溯来源
手机优先     →  320px~430px宽度完美展示
策略感知     →  84%超配/深套>25%/建仓期→看板给出上下文
静态SPA     →  HTML+CSS+JS，无需构建工具
增量更新     →  数据通过JSON注入，页面无需重新生成
暗色优先     →  金融类应用中暗色是默认体验
```

### 4.2 品牌与配色

**色系**：深蓝底 + 琥珀暖色 + 绿红涨跌

```
背景: #0a0e1a（深蓝黑）
卡片: #111827/80（半透明）
强调: #f59e0b（琥珀色，用于标题/活跃元素）
涨: #22c55e（绿色）
跌: #ef4444（红色）
平/中性: #6b7280（灰色）
文字: #f3f4f6（主文字）
文字辅: #9ca3af（辅助文字）
```

### 4.3 布局规范

```
手机 (320-430px):
  单列流式布局
  卡片宽100%，间距12px
  表格横向滚动

平板 (768-1024px):
  两列网格
  左侧留边栏

桌面 (1280px+):
  三列网格
  侧栏永久可见
```

### 4.4 交互原则

- 所有图表用 `Canvas` 或 `SVG` 手绘（不引入第三方库）
- 页面间导航用 hash routing（`#portfolio`, `#market`）
- 数据刷新：页面加载时 fetch `/fund-system/data/dashboard.json`
- 自动暗色模式（system preference + 手动切换按钮）

---

## 5. 页面体系（完整规格）

### 5.1 页面地图

```
📊 投资实用看板 (index.html)
├── 🏠 总览 Dashboard (默认页)
│   ├── 大盘天气 (6大指数实时)
│   ├── 组合速览 (总投入/市值/盈亏/偏离度/建仓进度)
│   ├── 今日推送摘要 (最近一次推送内容)
│   ├── 操作记录时间线 (最近5条)
│   ├── 板块热度 (10行业涨跌)
│   └── 风险提示 (预警项目)
│
├── 💼 持仓详情 (#portfolio)
│   ├── 持仓盈亏表 (14基金×成本/现价/盈亏/占比)
│   ├── 偏离度仪表 (科技/AI vs 目标65%)
│   ├── 建仓进度 (003096+013403)
│   ├── 组合结构饼图 (行业分布)
│   └── 历史盈亏曲线 (累计收益)
│
├── 📈 板块轮动 (#sectors)
│   ├── 日涨跌排行 (10行业)
│   ├── 近5日趋势 (迷你线图)
│   ├── 资金流向模拟 (腾讯数据)
│   └── 板块-持仓关联 (我的基金分布在哪些板块)
│
├── 📜 操作记录 (#operations)
│   ├── 操作时间线 (完整列表)
│   ├── 操作类型统计 (买入/加仓/持有)
│   ├── 单次操作详情 (金额/基金/原因)
│   └── 操作-结果关联 (之后N日收益)
│
├── 🤖 信号系统 (#signals)
│   ├── 信号引擎状态 (活跃规则数)
│   ├── 最近触发信号
│   ├── KOL信号时间线 (唐主任+小浣熊)
│   └── 信号-操作关联
│
├── 📊 数据验证 (#verify)
│   ├── 预测准确率趋势
│   ├── 数据源可用率
│   ├── 决策验证结果
│   └── 系统健康检查
│
└── 🔧 系统管理 (#system)
    ├── cron任务状态
    ├── R2文件索引
    ├── 进化版本历史
    └── 手动触发按钮
```

### 5.2 页面详细设计

#### P1: 🏠 总览 Dashboard（默认页）

**布局**：从上到下全单列

```
┌─────────────────────────────┐
│ 📊 投资看板 · 2026-07-21    │  ← 顶栏(日期+刷新)
├─────────────────────────────┤
│ 🔴 沪深300: 3921 ▼1.2%     │  ← 大盘天气卡片
│ 🔴 科创50: 1002 ▼0.8%      │     6个指数，带涨跌色
│ 🟢 恒生: 18923 ▲0.5%       │
│ ⬜ 道琼斯: 40820 -(-)       │     外盘显示昨收
├─────────────────────────────┤
│ 总投入 ¥6,426                │  ← 组合速览卡片
│ 当前市值 ¥4,817              │     大号数字
│ 总盈亏 -¥1,609 (-25%)        │     亏损红色
│ 科技占比 84% 🔴              │     超配警示
│ 建仓进度 43% ██████░░░░░     │     进度条
├─────────────────────────────┤
│ 最新推送: 收盘复盘 16:00      │  ← 推送摘要卡片
│ "今日沪深300下跌1.2%，        │     直接从JSONL读取
│  科创50跌幅收窄..."           │     可点击展开全文
├─────────────────────────────┤
│ 📜 最近操作                    │  ← 操作时间线
│ 07-16  买入  003096  +¥160   │     最近5条
│ 07-16  买入  013403  +¥150   │
│ 07-15  持有  011613          │
├─────────────────────────────┤
│ 📊 板块热度                    │  ← 10行业涨跌
│ 🔴 半导体 -2.3% ████████░░   │     带渐变条
│ 🟢 黄金 +1.2% ████░░░░░░░   │
│ 🔴 光伏 -1.8% ██████░░░░░    │
├─────────────────────────────┤
│ ⚠️ 风险提示                    │  ← 自动预警
│ • 科技超配84%(目标<65%) 🟡   │
│ • 011613跌幅>30%深套          │
│ • 今日无加仓信号              │
└─────────────────────────────┘
```

**数据来源**：
- 大盘天气 → `fund_tools.py` get_market_indexes()
- 组合速览 → 读取最新 `portfolio-YYYY-MM-DD.csv` + `seed_portfolio.json`
- 推送摘要 → 读取最新 `closing-reviews.jsonl` 或 `morning-briefs.jsonl`
- 操作时间线 → 读取 `operations/` 目录最新md
- 板块热度 → `fund_tools.py` get_sector_performance()
- 风险提示 → 调用/读取 `risk_warning.py` 或 `check_allocation.py` 最近输出

#### P2: 💼 持仓详情 (`#portfolio`)

**核心功能**：14支基金的完整持仓表

| 基金代码 | 基金名称 | 成本 | 现价/估算净值 | 份额 | 市值 | 盈亏(%) | 占比 | 状态 |
|---------|---------|------|-------------|------|------|---------|------|------|
| 011613 | 华夏科创50C | 1401.98 | 0.8321 | 1120 | 932 | -33.5%🔴 | 20.3% | 深套 |
| 024418 | 华夏半导体C | 1325.37 | 0.8524 | 1050 | 895 | -32.5%🔴 | 19.4% | 深套 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
| 003096 | 中欧医疗C | 160.00 | 0.5542 | 288 | 159 | -0.3%🟡 | 3.3% | 建仓中 |
| 013403 | 恒生科技C | 150.00 | 0.9821 | 153 | 150 | 0%🟡 | 3.1% | 建仓中 |

**附加视图**：
- 饼图（不带三方库，SVG手绘）：
  - 按行业分类(css实现的饼图)
  - 按基金类型
- 偏离度仪表：环形进度条形式
- 建仓进度：两个进度条

**数据来源**：
- 基金成本 → `seed_portfolio.json` + `operations/` 增量
- 估算净值 → `fund_tools.py` get_fund_value()（14支）
- 份额计算 → 成本÷(申赎调整后单位净值)

#### P3: 📈 板块轮动 (`#sectors`)

**10个跟踪行业**：

| 行业 | 代码 | 今日涨跌 | 5日趋势 | 关联基金 |
|------|------|---------|---------|---------|
| 半导体 | 990001 | -2.3% | 📉📉📉📉📉 | 024418(华夏半导体C) |
| 科创50 | 000688 | -0.8% | 📉📈📉📉📈 | 011613(华夏科创50C) |
| 数字经济 | 931380 | -1.5% | 📉📈📉📉📉 | 017103(大摩数字经济C) |
| 新能源 | 000941 | +0.3% | 📉📈📉📈📈 | 012329(天弘新能源C) |
| 光伏 | 931151 | -1.8% | 📉📉📉📈📉 | 011103(天弘光伏C) |
| 中证医疗 | 399989 | +0.5% | 📈📉📈📉📈 | 003096(中欧医疗C) |
| 黄金 | AU99 | +1.2% | 📈📈📈📈📉 | 009478(中银黄金C) |
| 恒生科技 | HSTECH | +0.3% | 📉📈📈📉📈 | 013403(恒生科技C) |
| 电网设备 | 931693 | -0.7% | 📉📉📈📉📉 | 025857(华夏电网C) |
| 军工/资源 | 399959 | -0.2% | 📉📈📉📉📈 | 163302(大摩资源C) |

**数据来源**：
- `fund_tools.py` get_sector_performance()
- 5日趋势：从 `fund-daily-trend.jsonl` 或 `daily-snapshots.jsonl` 提取
- 关联基金：手动映射（代码固定）

#### P4: 📜 操作记录 (`#operations`)

**时间线视图**：

```
2026-07-16
  ├── 🟢 买入 003096 中欧医疗C  ¥160 (建仓累计: 160/370)
  └── 🟢 买入 013403 恒生科技C  ¥150 (建仓累计: 150/300)
2026-06-28
  └── 🟡 持有观望  (信号: 无触发)
...
```

**数据来源**：
- `operations/operation_YYYY-MM-DD.md` 解析
- `trade_decisions.jsonl` 读取

#### P5: 🤖 信号系统 (`#signals`)

**卡片布局**：

```
┌─────────────────┐  ┌─────────────────┐
│ 信号引擎状态      │  │ KOL信号时间线    │
│ 规则: 6条活跃     │  │ 07-21 唐主任:   │
│ 今日触发: 0条     │  │ "存" → 半导体📉 │
│ 最近触发: 07-18   │  │ 07-20 小浣熊:   │
│ 天弘新能源信号    │  │ "风险" → 提示   │
└─────────────────┘  └─────────────────┘
┌─────────────────┐  ┌─────────────────┐
│ 信号-操作关联     │  │ 规则配置快照     │
│ 07-15加仓信号→   │  │ signal_rules.yaml│
│ 未操作(超配限制)  │  │ 最新rule列表    │
└─────────────────┘  └─────────────────┘
```

**数据来源**：
- `signals.jsonl` + `signal_engine.py` 状态
- `signals-resolved.jsonl`（解析后）
- KOL信号 `kol_verify.py` 输出

#### P6: 📊 数据验证 (`#verify`)

**组成部分**：
1. 预测准确率趋势 → `accuracy.jsonl` 读取
2. 数据源可用率 → `_source_availability.jsonl`
3. 决策验证 → `verify_decisions.py` 输出
4. 系统健康 → `system_health_audit.py` 输出

### 5.3 数据更新频率

| 数据 | 更新频率 | 方式 |
|------|---------|------|
| 大盘指数 | 交易日每30min | cron采集→写JSON→R2同步 |
| 基金估算净值 | 交易日14:30/16:00 | 随推送采集 |
| 组合快照 | 交易日16:10 | `portfolio_snapshot.py` |
| 板块热度 | 交易日11:30/15:00 | 随午/收盘采集 |
| 操作记录 | 操作发生时 | 随`execute_today_plan.py` |
| KOL信号 | 交易日每4h | 随采集更新 |
| 系统健康 | 周六10:30 | 周度 |
| 预测准确率 | 交易日16:10 | 随收盘验证 |

---

## 6. 数据流设计

### 6.1 数据管道

```
cron脚本 (数据采集)
    │
    ▼
fund_tools.py → JSONL / CSV / JSON (本地)
    │
    ▼
r2_uploader.py → R2 (CDN)
    │
    ▼
dashboard.html (静态SPA)
    │
    ▼
fetch('/fund-system/data/dashboard.json')  ← 核心数据聚合文件
    │
    ▼
JavaScript渲染所有卡片/图表
```

### 6.2 核心数据文件

**主数据文件**：`fund-system/data/dashboard.json`

```json
{
  "date": "2026-07-21",
  "market": {
    "indexes": [
      {"code": "000001", "name": "上证指数", "price": 3125.42, "change": -1.23, "change_pct": -1.23},
      {"code": "399001", "name": "深证成指", "price": 10234.56, "change": -0.87, "change_pct": -0.87},
      {"code": "000688", "name": "科创50", "price": 1002.34, "change": -0.85, "change_pct": -0.85},
      {"code": "399006", "name": "创业板指", "price": 2134.56, "change": -0.45, "change_pct": -0.45},
      {"code": "HSI", "name": "恒生指数", "price": 18923.45, "change": 98.23, "change_pct": 0.52},
      {"code": "DJI", "name": "道琼斯", "price": 40820.50, "change": 0, "change_pct": 0}
    ]
  },
  "portfolio": {
    "total_cost": 6426.00,
    "current_value": 4817.35,
    "total_profit": -1608.65,
    "total_profit_pct": -25.04,
    "tech_ratio": 84.2,
    "building_progress": 43,
    "funds": [...]
  },
  "sectors": [...],
  "operations": [...],
  "signals": {...},
  "push_summary": {...},
  "risks": [...],
  "accuracy": {...},
  "updated_at": "2026-07-21T16:10:00+08:00"
}
```

**生成方式**：新增 `generate_dashboard_data.py` 
- 在每日收盘推送后运行
- 从现有 JSONL/CSV/JSON 聚合
- 输出到本地 + 上传R2

### 6.3 与现有系统的集成点

| 现有系统 | 数据输出 | 看板消费方式 |
|---------|---------|-------------|
| `fund_tools.py` | 实时行情(console) | 采集时写JSON |
| `portfolio_snapshot.py` | portfolio-YYYY-MM-DD.csv/html/md | 读取最新CSV |
| `operations/operation_*.md` | 操作记录文件 | 解析md |
| `signals.jsonl` | 信号流 | 读取最近N条 |
| `signals-resolved.jsonl` | 解析后信号 | 读取最近N条 |
| `accuracy.jsonl` | 预测准确率 | 读取全量 |
| `_source_availability.jsonl` | 数据源可用率 | 读取 |
| `daily-snapshots.jsonl` | 每日价格快照 | 趋势曲线 |
| `check_allocation.py` 输出 | 偏离度结果 | 读取最近 |
| `risk_warning.py` 输出 | 风险项 | 读取最近 |
| `system_health_audit.py` 输出 | 健康检查报告 | 读取最近 |

---

## 7. 技术方案选型

### 7.1 推荐方案：纯HTML/CSS/JS SPA

**理由**：
- 零构建步骤，直接上传R2
- 无需Node.js/npm，维护成本最低
- 符合当前技术栈（md+html模式已经跑通）
- RSS Cloudflare Workers可加，但非必需

**架构**：

```
fund-system/
├── dashboard/                     ← 新建的看板目录
│   ├── index.html                ← SPA入口（所有页面都在一个HTML）
│   ├── css/
│   │   └── style.css             ← 全站样式（暗色主题+响应式）
│   ├── js/
│   │   ├── app.js                ← 路由+初始化
│   │   ├── data.js               ← fetch数据+缓存
│   │   ├── views/
│   │   │   ├── dashboard.js      ← 总览页面
│   │   │   ├── portfolio.js      ← 持仓详情
│   │   │   ├── sectors.js        ← 板块轮动
│   │   │   ├── operations.js     ← 操作记录
│   │   │   ├── signals.js        ← 信号系统
│   │   │   └── verify.js         ← 数据验证
│   │   └── charts/
│   │       ├── pie.js            ← SVG饼图
│   │       ├── bar.js            ← 柱状图/进度条
│   │       ├── line.js           ← 迷你趋势线
│   │       └── gauge.js          ← 环形仪表
│   └── assets/
│       └── icons.svg             ← 内置图标
├── data/
│   ├── dashboard.json            ← 核心数据（cron生成）
│   ├── portfolio-2026-07-21.csv  ← 每日持仓
│   └── ...                        ← 其他数据
└── reports/                       ← 已有报告
```

### 7.2 为什么不选React/Vue

| 方案 | 优势 | 劣势 | 结论 |
|------|------|------|------|
| React/Vite全家桶 | 组件化、生态好 | 需要构建、node_modules 200+MB | ❌ 过度 |
| Vue+CDN | 渐进式、体积小 | 仍需构建工具 | ⚠️ 可用但不必要 |
| **纯HTML+JS模块** | **零依赖、R2直传** | 手写组件稍多 | ✅ **推荐** |
| Tailwind CDN | 快速样式 | 大文件(300KB+)、学习成本 | ❌ 不如手写 |

### 7.3 核心依赖（仅CDN引用）

```html
<!-- 零前端框架！ -->
<style>/* 全部手写CSS，约2-3KB */</style>
<script type="module">
  // ES Module方式组织，无打包
  // import { renderDashboard } from './js/views/dashboard.js'
</script>
```

### 7.4 为什么不需要构建工具

**当前模式已经证明可行**：

```
写代码  →  上传R2  →  CDN分发  →  用户手机访问
```

cron生成 `dashboard.json` + 静态SPA读取 → 无需后端、无需构建

---

## 8. 分阶段实施路线

### 阶段一：数据基建（1-2天）

**目标**：打通看板的数据管道

| 任务 | 产出 | 依赖 |
|------|------|------|
| 1.1 编写 `generate_dashboard_data.py` | `dashboard.json` 聚合脚本 | 现有JSONL/CSV |
| 1.2 集成到收盘推送后 | 交易日16:15自动生成 | cron |
| 1.3 上传到R2 | `fund-system/data/dashboard.json` | r2_uploader.py |
| 1.4 基础数据校验 | curl验证JSON完整性 | — |

**验证标准**：
```bash
curl https://hermes-main-media.devtoy.xyz/fund-system/data/dashboard.json
# 返回完整JSON，包含market/portfolio/sectors/operations/signals/risks
```

### 阶段二：核心看板（2-3天）

**目标**：总览页 + 持仓页可用

| 任务 | 产出 | 说明 |
|------|------|------|
| 2.1 index.html骨架 | SPA入口+路由+暗色主题 | 单HTML文件 |
| 2.2 style.css | 全站样式（~500行） | 深色主题+响应式 |
| 2.3 charts基础模块 | pie.js + bar.js + gauge.js | SVG手绘，无三方 |
| 2.4 Dashboard总览页 | 大盘+组合+操作+板块+风险 | 默认页 |
| 2.5 持仓详情页 | 14基金表+饼图+偏离度+建仓进度 | P0核心 |

**验证标准**：
- 手机浏览器打开 `https://.../fund-system/dashboard/index.html` 
- 总览页显示6个指数、组合盈亏、板块热度、最近操作
- 点击"持仓详情"导航到持仓表格

### 阶段三：扩展页面（1-2天）

| 任务 | 产出 | 说明 |
|------|------|------|
| 3.1 板块轮动页 | 10行业+5日趋势+基金关联 | 可排序表格 |
| 3.2 操作记录页 | 完整时间线+统计 | 按日期分组 |
| 3.3 信号系统页 | 信号引擎+KOL时间线 | 从JSONL读取 |
| 3.4 数据验证页 | 准确率趋势+数据源可用率 | 从已有数据读 |

### 阶段四：打磨与自动化（1天）

| 任务 | 说明 |
|------|------|
| 4.1 CRON自动更新dashboard.json | 交易日16:15自动 |
| 4.2 页面加载动画 | skeleton loading |
| 4.3 离线缓存策略 | Service Worker（可选） |
| 4.4 滚动性能优化 | 虚拟滚动（长列表） |
| 4.5 手机touch优化 | 左滑右滑切换页面 |

### 总工作量预估

```
阶段一: 1-2天  (数据管道)
阶段二: 2-3天  (核心页面)
阶段三: 1-2天  (扩展页面)
阶段四: 1天    (打磨)
────────────────
总计:   5-8天  (4阶段完成)
```

---

## 9. 开发规范

### 9.1 样式规范

```css
/* 设计系统 */
:root {
  --bg-body: #0a0e1a;
  --bg-card: rgba(17, 24, 39, 0.8);
  --bg-card-hover: rgba(17, 24, 39, 0.95);
  --border: rgba(255, 255, 255, 0.06);
  --text-primary: #f3f4f6;
  --text-secondary: #9ca3af;
  --text-muted: #6b7280;
  --accent: #f59e0b;
  --up: #22c55e;
  --down: #ef4444;
  --flat: #6b7280;
  --danger: #ef4444;
  --warning: #f59e0b;
  --info: #3b82f6;
  --radius: 12px;
  --shadow: 0 1px 3px rgba(0,0,0,0.3);
}

/* 响应式断点 */
@media (max-width: 430px) { /* 手机 */ }
@media (min-width: 768px) { /* 平板 */ }
@media (min-width: 1280px) { /* 桌面 */ }
```

### 9.2 代码规范

- 文件名：小写+连字符（`dashboard.js`，`pie.js`）
- 模块化：ES Module（`export function renderDashboard()`）
- DOM操作：纯原生 `document.createElement` + `innerHTML`
- 数据流：全局 `window.__DATA` + 刷新函数
- 图表：全部手写SVG/Canvas，不引入Chart.js/ECharts

### 9.3 命名约定

```javascript
// 视图函数命名
renderDashboard(viewData)   // 渲染总览
renderPortfolio(viewData)   // 渲染持仓
renderSectors(viewData)     // 渲染板块
renderOperations(data)      // 渲染操作
renderSignals(data)         // 渲染信号
renderVerify(data)          // 渲染验证

// 图表函数
drawPieChart(container, data, options)
drawBarChart(container, data, options)
drawMiniLine(container, data, options)
drawGauge(container, value, options)

// 工具函数
formatMoney(n)     // ¥1,234.56
formatPct(n)       // +1.23% / -1.23%
formatDate(d)      // 07-21
getChangeColor(n)  // 'up' | 'down' | 'flat'
```

### 9.4 数据格式契约

所有视图函数接受统一数据格式：

```javascript
// dashboard.json 结构 (TypeScript类型描述)
interface DashboardData {
  date: string;                    // "2026-07-21"
  market: {
    indexes: Array<{
      code: string; name: string;
      price: number; change: number; change_pct: number;
    }>;
    time: string;                  // 数据采集时间
  };
  portfolio: {
    total_cost: number;
    current_value: number;
    total_profit: number;
    total_profit_pct: number;
    tech_ratio: number;            // 0-100
    building_progress: number;     // 0-100
    funds: Array<FundItem>;
  };
  sectors: Array<SectorItem>;
  operations: Array<OperationItem>;
  signals: SignalData;
  push_summary: { type: string; time: string; content: string };
  risks: Array<{ level: string; message: string }>;
  accuracy: { recent: number; trend: string; detail: Array };
  updated_at: string;
}
```

---

## 10. 附录：与现有系统的集成点

### 10.1 新增脚本

**`scripts/generate_dashboard_data.py`** — 每日数据聚合

```python
# 读取现有数据源 → 输出 dashboard.json
# 运行时机：交易日16:15（收盘推送后）
# 数据源：
#   - fund_tools.py (实时行情)
#   - portfolio-YYYY-MM-DD.csv (持仓快照)
#   - seed_portfolio.json (成本基线)
#   - operations/ (操作记录)
#   - signals.jsonl (信号)
#   - signals-resolved.jsonl (解析信号)
#   - accuracy.jsonl (准确率)
#   - risk_warning.py 输出 (风险)
#   - check_allocation.py 输出 (偏离度)
```

### 10.2 需要修改的现有脚本

| 脚本 | 修改 | 原因 |
|------|------|------|
| `portfolio_snapshot.py` | 增加JSON输出 | 方便dashboard直接读取 |
| `run_closing.py` | 末尾调用 `generate_dashboard_data.py` | 收盘后自动更新看板 |
| `r2_upload_and_verify.py` | 增加dashboard目录同步 | 确保数据同步 |

### 10.3 R2目录结构变更

```
fund-system/
├── dashboard/                    ← 🆕 看板页面目录
│   ├── index.html               ← SPA入口
│   ├── css/style.css
│   └── js/...
├── data/
│   ├── dashboard.json           ← 🆕 聚合数据
│   ├── portfolio-*.csv
│   └── ...
├── reports/                     ← 已有报告
├── evolution/                   ← 已有进化文档
└── strategy/                    ← 已有策略文档
```

---

## 总结：一句话方案

**保持cron数据管道不变**，新增 `generate_dashboard_data.py` 聚合所有现有数据为一个 `dashboard.json`，上传R2；同时开发一个**纯HTML/CSS/JS的SPA**（零依赖），通过fetch该JSON渲染6个手机优先的页面（总览/持仓/板块/操作/信号/验证），实现从"数据充裕但视觉贫瘠"到"一目了然的决策看板"的跃迁。

---

*本方案由「投资助手」全量评估后生成，基于当前系统实际能力，不做过度设计。*
