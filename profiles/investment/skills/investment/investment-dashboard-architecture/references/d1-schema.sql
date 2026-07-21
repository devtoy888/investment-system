# D1 Database Schema — 基金投资系统

## portfolio_snapshots（每日持仓快照）

```sql
CREATE TABLE portfolio_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL,              -- '2026-07-21'
  total_cost REAL NOT NULL,        -- 总投入
  total_value REAL NOT NULL,       -- 总市值
  total_profit REAL NOT NULL,      -- 总盈亏
  profit_pct REAL NOT NULL,        -- 盈亏百分比
  tech_ratio REAL NOT NULL,        -- 科技占比
  building_progress REAL,          -- 建仓进度 0-100
  details TEXT,                    -- JSON: 各基金明细
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX idx_portfolio_date ON portfolio_snapshots(date);
```

## fund_values（基金净值历史）

```sql
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
```

## kol_signals（KOL信号）

```sql
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
```

## operations（操作记录）

```sql
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
```

## source_availability（数据源可用率）

```sql
CREATE TABLE source_availability (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL,
  source_name TEXT NOT NULL,
  success_count INTEGER,
  fail_count INTEGER,
  avg_latency_ms REAL,
  created_at TEXT DEFAULT (datetime('now'))
);
```

## prediction_accuracy（预测准确率）

```sql
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

## 同步策略

```
服务器cron → JSONL/CSV（本地真相源）
          → sync_to_d1.py（交易日16:20批量写入）
          → D1（查询副本）

D1挂了不影响数据完整性——本地文件是保险。
```
