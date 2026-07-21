-- Fund Dashboard D1 Schema
-- Cloudflare D1 (SQLite-based)
-- Tables for investment system data warehouse

-- ============================================
-- 1. 持仓快照 (每日)
-- ============================================
CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,                        -- 日期 YYYY-MM-DD
    fund_code TEXT NOT NULL,                   -- 基金代码
    fund_name TEXT NOT NULL,                   -- 基金名称
    shares REAL NOT NULL DEFAULT 0,            -- 持有份额
    cost REAL NOT NULL DEFAULT 0,              -- 成本价
    nav REAL,                                  -- 当日净值
    estimated_value REAL,                      -- 估算市值
    profit_pct REAL,                           -- 盈亏百分比
    profit_amount REAL,                        -- 盈亏金额
    sector TEXT,                               -- 所属板块
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(date, fund_code)
);

-- ============================================
-- 2. 基金历史净值
-- ============================================
CREATE TABLE IF NOT EXISTS fund_values (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code TEXT NOT NULL,
    date TEXT NOT NULL,
    nav REAL NOT NULL,                         -- 单位净值
    acc_nav REAL,                              -- 累计净值
    estimated_nav REAL,                        -- 估算净值 (盘中)
    change_pct REAL,                           -- 涨跌幅
    source TEXT DEFAULT 'eastmoney',           -- 数据源
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(fund_code, date)
);

-- ============================================
-- 3. 操作记录
-- ============================================
CREATE TABLE IF NOT EXISTS operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,                        -- 操作日期
    fund_code TEXT NOT NULL,
    fund_name TEXT NOT NULL,
    operation_type TEXT NOT NULL,              -- buy / sell / switch
    amount REAL NOT NULL,                      -- 操作金额
    shares REAL,                               -- 操作份额
    nav_at_operation REAL,                     -- 操作时净值
    reason TEXT,                               -- 操作理由
    strategy_ref TEXT,                         -- 关联策略
    created_at TEXT DEFAULT (datetime('now'))
);

-- ============================================
-- 4. KOL信号
-- ============================================
CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id TEXT UNIQUE,                     -- 原始信号ID
    source TEXT NOT NULL,                      -- 来源 (weibo/rss/...)
    author TEXT NOT NULL,                      -- 博主名
    publish_time TEXT NOT NULL,                -- 发布时间
    content TEXT,                              -- 原始内容
    direction TEXT,                            -- 看多/看空/中性
    target_sector TEXT,                        -- 目标板块
    target_code TEXT,                          -- 目标标的
    confidence REAL,                           -- LLM置信度
    accuracy INTEGER,                          -- 验证结果 1/0/-1
    verified_at TEXT,                          -- 验证时间
    created_at TEXT DEFAULT (datetime('now'))
);

-- ============================================
-- 5. LLM分析报告
-- ============================================
CREATE TABLE IF NOT EXISTS analysis_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL,                 -- morning/noon/closing/weekly
    date TEXT NOT NULL,
    summary TEXT,                              -- 摘要
    full_content TEXT,                         -- 全文
    llm_model TEXT,                            -- 使用的模型
    token_count INTEGER,                       -- 消耗token数
    created_at TEXT DEFAULT (datetime('now'))
);

-- ============================================
-- 6. 市场数据
-- ============================================
CREATE TABLE IF NOT EXISTS market_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    data_type TEXT NOT NULL,                   -- index/sector/fundflow/northbound
    symbol TEXT,                               -- 代码/名称
    value REAL,                                -- 数值
    change_pct REAL,                           -- 涨跌幅
    extra_json TEXT,                           -- 扩展数据 (JSON)
    created_at TEXT DEFAULT (datetime('now'))
);

-- ============================================
-- 索引
-- ============================================
CREATE INDEX IF NOT EXISTS idx_portfolio_date ON portfolio_snapshots(date);
CREATE INDEX IF NOT EXISTS idx_portfolio_code ON portfolio_snapshots(fund_code);
CREATE INDEX IF NOT EXISTS idx_fund_values_code_date ON fund_values(fund_code, date);
CREATE INDEX IF NOT EXISTS idx_operations_date ON operations(date);
CREATE INDEX IF NOT EXISTS idx_signals_author ON signals(author);
CREATE INDEX IF NOT EXISTS idx_signals_time ON signals(publish_time);
CREATE INDEX IF NOT EXISTS idx_analysis_date_type ON analysis_reports(date, report_type);
CREATE INDEX IF NOT EXISTS idx_market_date_type ON market_data(date, data_type);
