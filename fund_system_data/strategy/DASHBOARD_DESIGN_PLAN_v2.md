# 📊 投资实用看板 · 完整设计方案 v2

> 评估日期：2026-07-21 | 参考：Vibe-Research + Vibe-Trading  
> **v1→v2核心变化**：从"静态今日看板"升级为"全栈持续优化平台"

---

## 目录

1. [v1方案的4个盲区](#1-v1方案的4个盲区)
2. [全新架构总览](#2-全新架构总览)
3. [Cloudflare D1 — 历史数据的基石](#3-cloudflare-d1--历史数据的基石)
4. [Git版本控制 + 部署策略](#4-git版本控制--部署策略)
5. [页面体系（完整规格）](#5-页面体系完整规格)
6. [时间维度设计](#6-时间维度设计)
7. [实施路线](#7-实施路线)
8. [变更清单](#8-变更清单)
9. [开发计划](#9-开发计划)

---

## 1. v1方案的4个盲区

| # | 盲区 | v1方案 | v2改进 |
|---|------|--------|--------|
| 1️⃣ | **历史数据** | 只看当日 | 支持日期导航 + 趋势对比 |
| 2️⃣ | **数据存储** | 纯JSON在R2 | D1结构化数据库 + R2并存 |
| 3️⃣ | **版本控制** | 没提git | 全量入库 + Pages自动部署 |
| 4️⃣ | **部署平台** | R2静态 | Cloudflare Pages + Workers API |

**核心认知修正**：这不是"做一个页面"，这是**一个持续2年+的投资工具平台**。数据会积累、策略会迭代、脚本会更改——必须从一开始就用正轨架构。

---

## 2. 全新架构总览

```
┌─────────────────────────────────────────────────────────┐
│              Oracle ARM Server（你的服务器）              │
│                                                          │
│  /opt/data/scripts/  ← 155个Python采集脚本               │
│  │                                                       │
│  ├── fund_tools.py         行情采集                       │
│  ├── portfolio_snapshot.py 持仓快照 → CSV                │
│  ├── signal_engine.py      信号引擎                       │
│  ├── collect_morning.py    早报数据采集                    │
│  ├── .py (155个)           其他脚本                       │
│  │                                                       │
│  └── git push → GitHub/Gitee                             │
└────────────────────────────┬────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                              ▼
    ┌──────────────────┐       ┌──────────────────────────┐
    │  R2 (对象存储)     │       │  Cloudflare Ecosystem    │
    │                   │       │                          │
    │  reports/         │       │  D1 (SQLite数据库) 🆕    │
    │  data/            │       │  ├── portfolio_history   │
    │  evolution/       │       │  ├── fund_value_history  │
    │  strategy/        │       │  ├── operations_log      │
    │  dashboard.json   │       │  ├── signals_history     │
    └──────────────────┘       │  └── kol_posts            │
                               │                          │
                               │  Pages（前端SPA） 🆕      │
                               │  ├── Auto-deploy from git│
                               │  └── Custom domain        │
                               │                          │
                               │  Workers（API层） 🆕      │
                               │  ├── /api/dashboard       │
                               │  ├── /api/history/:days   │
                               │  ├── /api/portfolio/:date │
                               │  └── /api/sectors/:range  │
                               └──────────────────────────┘
```

### 数据流的两种路径

```
路径A：实时展示（当天）
  cron采集 → fund_tools.py → dashboard.json → R2
  → 前端fetch → 渲染

路径B：历史查询（过去N天）
  cron采集 → 数据写入 → D1
  → Worker SQL查询 → JSON返回
  → 前端fetch → 渲染K线/趋势

路径C：静态文件（报告/文档）
  cron生成 → md/html → R2
  → 直接访问
```

---

## 3. Cloudflare D1 — 历史数据的基石

### 3.1 为什么需要D1

当前系统的历史数据躺在 JSONL/CSV 里，查询历史趋势只能：
- ❌ 读整个JSONL文件到内存 → 随着数据增长不可行
- ❌ 用Python脚本聚合 → 每次查询都要触发服务器
- ❌ 纯R2 JSON → 不支持跨日期查询

D1（Cloudflare的Serverless SQLite）解决：
- ✅ SQL查询历史：`SELECT * FROM portfolio WHERE date BETWEEN '2026-07-01' AND '2026-07-21'`
- ✅ 免费5GB：足够存储数年数据
- ✅ Worker直连：毫秒级查询延迟
- ✅ 零维护：Cloudflare托管

### 3.2 D1 Schema设计

```sql
-- 持仓快照表（每日一条）
CREATE TABLE portfolio_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL,              -- '2026-07-21'
  total_cost REAL NOT NULL,        -- 总投入
  total_value REAL NOT NULL,       -- 总市值
  total_profit REAL NOT NULL,      -- 总盈亏
  profit_pct REAL NOT NULL,        -- 盈亏百分比
  tech_ratio REAL NOT NULL,        -- 科技占比
  building_progress REAL,          -- 建仓进度
  details TEXT,                    -- JSON: 各基金明细
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX idx_portfolio_date ON portfolio_snapshots(date);

-- 基金净值历史表
CREATE TABLE fund_values (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT NOT NULL,              -- 基金代码
  date TEXT NOT NULL,              -- 日期
  estimated_nav REAL,              -- 估算净值
  confirmed_nav REAL,              -- 确认净值
  change_pct REAL,                 -- 涨跌幅
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE(code, date)
);
CREATE INDEX idx_fund_code_date ON fund_values(code, date);

-- KOL信号表
CREATE TABLE kol_signals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,            -- 博主名
  weibo_id TEXT UNIQUE,            -- 微博ID（去重）
  created_at TEXT NOT NULL,        -- 发博时间
  content TEXT,                    -- 内容摘要
  direction TEXT,                  -- 看多/看空/中性
  topics TEXT,                     -- JSON: 涉及主题
  parsed_fund_code TEXT,           -- 自动关联的基金
  fetched_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX idx_kol_date ON kol_signals(created_at);

-- 操作记录表
CREATE TABLE operations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL,
  fund_code TEXT NOT NULL,
  fund_name TEXT,
  action TEXT NOT NULL,            -- buy/sell/hold
  amount REAL,                     -- 金额
  reason TEXT,                     -- 操作原因
  linked_signal_id INTEGER,        -- 关联信号
  result_pct REAL,                 -- N日后收益（延迟写入）
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX idx_op_date ON operations(date);
CREATE INDEX idx_op_code ON operations(fund_code);

-- 数据源可用率表
CREATE TABLE source_availability (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL,
  source_name TEXT NOT NULL,
  success_count INTEGER,
  fail_count INTEGER,
  avg_latency_ms REAL,
  created_at TEXT DEFAULT (datetime('now'))
);

-- 预测准确率表
CREATE TABLE prediction_accuracy (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL,
  total_predictions INTEGER,
  correct_predictions INTEGER,
  accuracy_pct REAL,
  details TEXT,                    -- JSON
  created_at TEXT DEFAULT (datetime('now'))
);
```

### 3.3 数据同步策略

**不是实时同步**，而是**批量回写**：

```
步骤1：服务器cron采集 → 写入本地JSONL/CSV（现有流程不变）
步骤2：交易日16:20 → sync_to_d1.py 运行
步骤3：读取本地JSONL → 解析 → 批量INSERT到D1
步骤4：D1 API通过Worker暴露 → 前端查询
```

**为什么不是实时写D1**？
- 当前系统（JSONL/CSV）已经稳定运行
- 服务器不一定每次都能访问D1（网络波动）
- 本地文件是真相源（source of truth），D1是查询副本
- 批量写入比逐条写入快100倍

### 3.4 D1 vs 继续用JSONL的对比

| 维度 | 纯JSONL/CSV | + D1 |
|------|-------------|------|
| 查询效率 | 全量读到内存 | SQL索引查询 |
| 历史趋势 | 手动写Python脚本 | `SELECT date, value WHERE code=X` |
| 前端支持 | 前端自己处理 | Worker直接返回 |
| 维护成本 | 零 | 需要同步脚本 |
| 免费额度 | 无限(R2) | 5GB（够用5年+） |
| 网络依赖 | 无 | 需要服务器能访问CF API |

**结论**：JSONL/CSV作为数据主存储（真相源），D1作为查询加速层（可选依赖）。D1挂了也不影响数据完整性。

---

## 4. Git版本控制 + 部署策略

### 4.1 Git仓库结构

```
fund-dashboard/                    ← GitHub/Gitee 仓库
├── scripts/                       ← 采集脚本（定期同步自服务器）
│   ├── fund_tools.py
│   ├── portfolio_snapshot.py
│   ├── signal_engine.py
│   ├── ...（155个脚本）
│   └── sync_to_d1.py             ← 🆕 新增：D1同步
│
├── dashboard/                     ← 前端SPA（Cloudflare Pages）
│   ├── public/
│   │   ├── index.html            ← SPA入口
│   │   ├── css/style.css
│   │   └── js/
│   └── _worker.js                ← API层（Workers）
│
├── schema.sql                    ← D1表结构
├── wrangler.toml                 ← Cloudflare配置
├── package.json                  ← 构建配置
└── README.md
```

### 4.2 为什么需要Git

| 场景 | 没Git | 有Git |
|------|-------|-------|
| 改坏了脚本 | ❌ 手动备份回退 | ✅ git revert |
| 想看看之前的版本 | ❌ 靠记忆 | ✅ git log |
| 多设备同步 | ❌ scp | ✅ git push/pull |
| 追溯修改原因 | ❌ ？？ | ✅ commit message |
| 协作开发 | ❌ 不能 | ✅ PR review |

### 4.3 服务器→Git同步策略

```
# 不是每次修改都git push，而是定期批量同步
# 方式：服务器作为数据源，git作为代码存档

cron 每日 04:00（非交易时段）
  → cd /opt/data/scripts
  → 自动commit + push到远程仓库
```

**不频繁推的原因**：
- 大多数修改是通过Hermes agent完成的（对话式修改）
- 服务器上的脚本每天变化不大
- 重要的是**存档 + 回滚能力**
- 不想每次agent改一行就弹个git操作

### 4.4 推荐的Git仓库位置

两个选项：

| 选项 | 优点 | 缺点 |
|------|------|------|
| **GitHub** | 生态好、Pages原生支持 | 国外，可能DNS问题 |
| **Gitee/腾讯工蜂** | 国内快、Push快 | Pages集成弱 |
| **自建Gitea** | 完全可控 | 多维护一个服务 |

**推荐**：GitHub（主要）+ Gitee（镜像），兼顾速度和可靠性。

### 4.5 Cloudflare Pages部署策略

```
Git push → GitHub → Cloudflare Pages自动检测
    │
    ▼
自动构建（~30秒）
    │
    ▼
部署到 Pages（自带CDN + HTTPS）
    │
    ├── https://fund-dashboard.pages.dev    ← Pages默认域名
    └── https://your-custom-domain.com      ← 自定义域名（可选）
```

**Pages + Workers配置（wrangler.toml）**：

```toml
name = "fund-dashboard"
compatibility_date = "2026-07-21"

pages_build_output_dir = "dashboard"

[[d1_databases]]
binding = "DB"
database_name = "fund-system-db"
database_id = "xxx-xxx-xxx"

[env.production.routes]
pattern = "fund-dashboard.pages.dev/*"
```

### 4.6 为什么不推荐在服务器上跑Node后端

当前架构**不需要**在Oracle服务器上跑任何额外服务：
- 采集脚本：已经在跑cron
- 前端SPA：Cloudflare Pages
- API层：Cloudflare Workers（零服务器）
- 数据库：Cloudflare D1（零服务器）

**零新增服务器开销**，完全利用Cloudflare免费额度。
你目前的Oracle ARM服务器只负责**数据采集**，所有对外服务都走Cloudflare。

---

## 5. 页面体系（完整规格）

### 5.1 页面地图（v2新增日期维度）

```
📊 投资实用看板 ── [日期选择器] ← 🆕 每个页面都有
│
├── 🏠 总览 Dashboard（默认页）
│   ├── 大盘天气（6大指数实时）
│   ├── 组合速览（投入/市值/盈亏/偏离度）
│   │   └── 📅 趋势卡片：近7日/30日盈亏曲线 ← 🆕
│   ├── 推送摘要（最近一次）
│   ├── 操作时间线（最近5条）
│   ├── 板块热度
│   └── 风险提示
│
├── 💼 持仓详情 (#portfolio?date=2026-07-21) ← 🆕 可带日期参数
│   ├── 14基金完整盈亏表
│   ├── 偏离度仪表
│   ├── 建仓进度
│   ├── 行业饼图
│   ├── 历史盈亏曲线（可切换7/30/90天） ← 🆕
│   └── 单基金深度（点击展开历史净值） ← 🆕
│
├── 📈 板块轮动 (#sectors?range=30d) ← 🆕 可带时间范围
│   ├── 日涨跌排行
│   ├── 近N日趋势（迷你线图）
│   ├── 板块轮动热力图 ← 🆕 日历热力图
│   └── 板块-持仓关联
│
├── 📅 历史趋势 (#history) ← 🆕 新增页面
│   ├── 组合净值曲线（1月/3月/半年/全部）
│   ├── 各基金涨跌贡献排名
│   ├── 板块轮动时间线
│   └── 可对比不同时间区间
│
├── 📜 操作记录 (#operations?from=2026-07-01)
│   ├── 完整时间线（带日期筛选） ← 🆕
│   ├── 操作类型统计
│   └── 操作后N日收益验证 ← 🆕
│
├── 🤖 信号系统 (#signals?days=30)
│   ├── 信号引擎状态
│   ├── KOL信号时间线（可筛选日期范围） ← 🆕
│   └── 信号-操作关联（时间对齐） ← 🆕
│
└── 📊 系统状态 (#system)
    ├── 预测准确率趋势
    ├── 数据源可用率
    ├── cron任务状态
    └── R2文件索引
```

### 5.2 新增核心功能：历史趋势页

这是v2新增的最重要页面：

```
┌──────────────────────────────────────┐
│ 📅 组合历史趋势                      │
│ [7天] [30天] [90天] [全部] ← 时间切换 │
├──────────────────────────────────────┤
│ ┌──────────────────────────────────┐ │
│ │    组合净值曲线 (SVG Area Chart)  │ │
│ │  ┌────┐                          │ │
│ │  │    │       ┌──┐               │ │
│ │  │    │  ┌────┘  │               │ │
│ │  │    └──┘       └──┐            │ │
│ │  └───────────────────┴──          │ │
│ │  07-01   07-10    07-20          │ │
│ └──────────────────────────────────┘ │
│                                      │
│ 区间收益: -5.2%　最大回撤: -8.3%      │
│ 日均波动: 1.2%　  同期沪深300: -3.1% │
│                                      │
│ 单基金贡献排行:                        │
│ 🥇 011613 华夏科创50C   -¥32.5 📉     │
│ 🥈 024418 华夏半导体C   -¥28.1 📉     │
│ 🥉 017103 大摩数字经济C  -¥12.3 📉     │
│ ...                                   │
└──────────────────────────────────────┘
```

**数据来源**：D1的 `portfolio_snapshots` 表 + `fund_values` 表

### 5.3 新增组件：日期选择器

每个页面顶部新增日期控件：

```html
<!-- 全局日期选择器 -->
<div class="date-nav">
  <button onclick="prevDay()">‹</button>
  <input type="date" id="datePicker" value="2026-07-21">
  <button onclick="nextDay()">›</button>
  <span class="date-label">交易日</span>
</div>

<!-- 时间范围选择器（历史页面） -->
<div class="range-nav">
  <button class="active">7天</button>
  <button>30天</button>
  <button>90天</button>
  <button>全部</button>
</div>
```

---

## 6. 时间维度设计

### 6.1 数据积累路径

```
                       现在的数据
                          │
                    2026-07-15  ← 系统上线日
                    2026-07-16
                    2026-07-17
                    ...（交易日积累）
                          │
                    1年后：~250个交易日数据
                    2年后：~500个交易日数据
```

### 6.2 各页面时间维度

| 页面 | 视图类型 | 时间范围 | 数据来源 |
|------|---------|---------|---------|
| 🏠 总览 | 当前快照 | 今天 | R2 dashboard.json |
| 💼 持仓 | 当前+趋势 | 今天+7/30/90天 | D1 |
| 📈 板块 | 趋势+热力图 | 1/5/20/60天 | D1 |
| 📅 历史 | 全量 | 可选任意区间 | D1 |
| 📜 操作 | 时间线 | 可选任意区间 | D1 |
| 🤖 信号 | 时间线 | 可选任意区间 | D1 |

### 6.3 1年后的数据规模估算

| 表 | 日增量 | 年数据量 | D1占用 |
|----|--------|---------|--------|
| portfolio_snapshots | 1行 | ~250行 | ~50KB |
| fund_values | 14行 | ~3,500行 | ~500KB |
| kol_signals | ~10行 | ~2,500行 | ~1MB |
| operations | ~1行 | ~250行 | ~100KB |
| **总计** | | | **~2MB** |

D1免费5GB，用1000年才满。✅

---

## 7. 实施路线

### 阶段一：基础设施搭建（2-3天）

| 任务 | 产出 | 说明 |
|------|------|------|
| 1.1 创建GitHub仓库 | `fund-dashboard` 仓库 | 包含scripts/、dashboard/、schema.sql |
| 1.2 服务器git init | `/opt/data/scripts/` 纳入版本控制 | 初始导入155个脚本 |
| 1.3 注册Cloudflare D1 | `fund-system-db` 创建 | 免费5GB |
| 1.4 执行schema.sql | 6张表创建完成 | D1控制台或wrangler CLI |
| 1.5 编写 `sync_to_d1.py` | 读取本地JSONL/CSV → 批量写入D1 | 交易日16:20自动运行 |
| 1.6 首次全量同步 | D1中拥有全部历史数据 | 让看板"有数据可看" |

### 阶段二：Worker API层（1-2天）

| 任务 | 产出 | 说明 |
|------|------|------|
| 2.1 Worker `/api/dashboard` | 返回今日聚合数据 | 替代R2 JSON直接fetch |
| 2.2 Worker `/api/history` | 接受?days=参数返回趋势 | D1 SQL查询 |
| 2.3 Worker `/api/portfolio` | 接受?date=参数返回持仓 | D1 SQL查询 |
| 2.4 Worker `/api/sectors` | 接受?range=参数返回板块 | D1 SQL查询 |
| 2.5 wrangler.toml配置 | D1 binding + 路由 | Pages + Workers集成 |

### 阶段三：前端SPA开发（3-4天）

| 任务 | 产出 | 说明 |
|------|------|------|
| 3.1 SPA骨架 | index.html + 路由 + 暗色主题 | 纯HTML/CSS/JS |
| 3.2 总览页 | 大盘 + 组合 + 推送 + 操作 + 板块 + 风险 | 默认页 |
| 3.3 持仓页 | 14基金表 + 饼图 + 偏离度 + 建仓进度 | P0 |
| 3.4 历史趋势页 | 净值曲线 + 区间统计 + 单基金排行 | 🆕 v2新增 |
| 3.5 操作记录页 | 时间线 + 类型统计 + 结果验证 | 🆕 v2新增 |
| 3.6 板块轮动页 | 热力图 + 趋势线 + 基金关联 | 🆕 v2新增 |
| 3.7 信号系统页 | KOL时间线 + 信号-操作关联 | 🆕 v2新增 |

### 阶段四：自动化与打磨（2天）

| 任务 | 说明 |
|------|------|
| 4.1 cron自动同步D1 | 交易日16:20运行 sync_to_d1.py |
| 4.2 cron自动git push | 每日04:00提交脚本变更 |
| 4.3 Pages自动部署 | Git push触发 |
| 4.4 手机体验优化 | touch事件、加载动画 |
| 4.5 离线缓存 | Service Worker（可选） |

### 总工作量：8-11天

---

## 8. 变更清单

### 8.1 新增文件

| 文件 | 路径 | 说明 |
|------|------|------|
| `sync_to_d1.py` | `/opt/data/scripts/` | JSONL/CSV → D1 同步 |
| `schema.sql` | 仓库根目录 | D1 6张表定义 |
| `wrangler.toml` | 仓库根目录 | Cloudflare配置 |
| `dashboard/` 全目录 | 仓库下 | 前端SPA (10+文件) |
| `_worker.js` | `dashboard/`下 | Workers API（5个端点） |

### 8.2 修改现有文件

| 文件 | 修改内容 | 工作量 |
|------|---------|--------|
| `run_closing.py` | 末尾调用 sync_to_d1.py | ~3行 |
| `portfolio_snapshot.py` | 增加JSON格式输出 | ~10行 |
| `r2_upload_and_verify.py` | 增加dashboard目录同步 | ~5行 |

### 8.3 R2目录结构变更

```
fund-system/
├── dashboard/                    ← 🆕 看板页面
├── data/
│   ├── dashboard.json           ← 今日聚合（备用，主走Worker）
│   └── ...
├── reports/                     ← 已有
├── evolution/                   ← 已有
└── strategy/                    ← 已有
```

---

## 9. 开发计划

### 9.1 为什么不一次性做完

8-11天的工作量，建议分3轮迭代：

**迭代1：基础设施（2-3天）**
```
Git仓库建立 → D1创建 → schema执行 → sync_to_d1.py完成
→ 验证D1有数据 → 基础Worker写完
```

**迭代2：核心看板（3-4天）**
```
SPA骨架 → 总览页 → 持仓页 → 历史趋势页 → Pages部署
→ 手机上能用
```

**迭代3：扩展完善（3-4天）**
```
操作记录页 → 板块轮动页 → 信号系统页 → 自动化
→ 打磨体验
```

每轮都是**可独立交付的版本**，不是"全部做完才能用"。

### 9.2 风险 & 应对

| 风险 | 概率 | 应对 |
|------|------|------|
| D1创建/配置不顺利 | 低 | jsonl→R2方案保底 |
| sync_to_d1.py网络不通 | 中 | 本地重试队列+次日补推 |
| Cloudflare Pages域名被墙 | 低 | R2直连作为备用入口 |
| 前端手机兼容问题 | 中 | 阶段三重点测试 |
| git push不习惯 | 中 | 自动commit脚本+手动review |

---

## 总结：v1 → v2变化

```
v1: 静态今日看板 + R2纯JSON
     ↓
v2: 全栈持续优化平台 + Git + D1 + Pages + Workers
     ↓
核心不变：服务器只做采集，前端零依赖
新增：
  🆕 日期间导航（所有页面可查历史）
  🆕 Cloudflare D1（可SQL查询的历史数据库）
  🆕 Git版本控制（可回滚、可追溯）
  🆕 Cloudflare Pages（自动构建、CDN分发）
  🆕 Workers API（数据查询层）
```

*本方案由「投资助手」全量评估后生成，基于当前系统实际能力，不做过度设计。*
