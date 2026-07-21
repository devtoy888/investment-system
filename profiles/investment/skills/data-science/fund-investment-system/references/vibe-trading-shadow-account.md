# Vibe-Trading Shadow Account 深度分析

> 2026-07-15 完成。对 Vibe-Trading `agent/src/shadow_account/` 模块的源码级分析及对基金决策系统的参考价值。

## 模块概览

Shadow Account 是从个人交割单 → 盈利模式规则 → 代码生成 → 多市场回测 → 差值归因 → HTML/PDF报告的**全自动流水线**。8个核心文件 + 2个Jinja2模板 + 配套SKILL.md。

## 完整 Pipeline

### Phase 1: 交易流水导入 (trade_journal_parsers.py)
- 4种格式: 同花顺/东方财富/富途/generic CSV
- 编码兼容链: utf-8 → gbk → gb2312
- 标准化为 TradeRecord: datetime, symbol, side, quantity, price, amount, fee, market
- FIFO配对: 按symbol分组，先进先出，比例手续费分配

### Phase 2: 行为诊断 (trade_journal_tool.py)
四题偏差检测，每题severity(low/medium/high)+numeric evidence:
- **处置效应**: avg_loss_hold / avg_win_hold ≥1.5 high
- **过度交易**: 繁忙日(Q75)vs安静日(Q25)PnL差距
- **追涨**: 同标的前3笔涨>3%时买入比例 ≥60% high
- **锚定**: σ(price)/mean(price) <5%标的占比

### Phase 3: 规则提取 (extractor.py)
```
Profitable Roundtrips → Feature Engineering → KMeans(k=2-5, auto-select)
  → Per-cluster Decision Tree(max_depth=3) → Path Extraction
  → Structured entry_condition dict → LLM-light自然语言翻译(f-string降级)
```
- 基础特征: holding_days, pnl_pct, entry_hour, entry_weekday
- 价格上下文(PIT-safe as-of buy_dt): entry_rsi14, prior_5d_return
- profitable roundtrips < 5 → 直接raise ValueError，不编造

### Phase 4: 代码生成 (codegen.py)
- Jinja2模板 → signal_engine.py(AST验证)
- 条件入场: RSI范围 + prior-return范围 + 时段窗口，三条件AND
- PRICE_FEATURES集中定义 → extractor/codegen/scanner三模块防漂移

### Phase 5: 多市场回测 (backtester.py)
- 四市场: china_a/hk/us/crypto，各5个流动性篮子标的
- 委托现有backtest runner
- **5维纯算术归因**(零LLM，可审计):

| 归因项 | 公式 | 正值含义 |
|--------|------|---------|
| noise_trades_pnl | 不命中任何规则的真实交易PnL取反 | 影子避开了这些亏损 |
| early_exit_pnl | 盈利但持仓<规则下限，按比例折算 | 早卖少赚了 |
| late_exit_pnl | 亏损且持仓>规则上限，按比例折算 | 影子避免了放大亏损 |
| overtrading_pnl | 超出规则频率的交易PnL取反 | 影子避开了无效交易 |
| missed_signals_pnl | shadow_pnl - real_pnl - 四项之和 | 无法被以上解释的残差 |

### Phase 6: 报告渲染 (reporter.py)
8-section结构: Shadow Profile → Rules → Combined Backtest → By Market → Delta Attribution → Counterfactual Top 5 → Today's Scan → Confidence & Caveats
- matplotlib图表: 权益曲线/Sharpe柱状图/归因瀑布图
- Jinja2 HTML + weasyprint PDF(CJK字体支持)
- weasyprint失败自动降级HTML-only

### Phase 7: 信号扫描 (scanner.py)
- 评估每条规则的入场条件在今日的匹配情况
- 强制附带"仅研究用，非买入建议"免责声明

## 对基金系统决策日志+3天验证的直接借鉴

### 映射关系

```
Shadow Account 模块              → 基金决策版映射
──────────────────────────────────────────────────
trade_journal_parsers.py       → 决策日志解析器
pair_trades_fifo()             → 决策-验证配对器(决策日→3天后验证日)
extractor.py (KMeans+DT)       → 成功决策模式提取器
codegen.py (signal_engine)     → 决策规则引擎
backtester.py (attribution)    → 3天验证归因(系统执行vs实际执行)
reporter.py (8-section)        → 决策复盘报告
scanner.py                     → (不需要，基金系统不产生今日信号)
```

### 可裁剪的5项核心框架

1. **决策-验证配对器**: 类`pair_trades_fifo()`——决策日+3天窗口配对
2. **PIT-safe特征**: 所有条件as-of决策日读取→天然满足3天验证的look-ahead禁止
3. **5维算术归因**: shadow vs real的delta_pnl可分解为可审计偏差类别
4. **合同稳定性**: `PRICE_FEATURES`模式→决策日志字段schema集中定义
5. **KMeans+决策树提取模式**: 从"验证通过的决策"中提炼共性条件

### 不适合照搬

- 散户行为诊断(处置效应/追涨/锚定)→替换为机构级(风格漂移/基准偏离)
- 个人交割单格式→多角色决策日志schema(基金经理/投委会/系统信号)
- KMeans对类别特征处理需增强(基金多维度决策条件)
