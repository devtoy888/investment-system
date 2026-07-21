---
title: Vibe-Trading MCP 插件与生态集成
created: 2026-07-12
updated: 2026-07-12
type: concept
tags: [finance, ai-agent, mcp, api, reference]
sources:
  - https://github.com/HKUDS/Vibe-Trading
  - https://vibetrading.wiki/docs/
---

# MCP 插件与生态集成

## MCP 服务器（外供工具）

Vibe-Trading 暴露 **54 个 MCP 工具**，可被任何 MCP 兼容客户端调用。

### Claude Desktop
在 `claude_desktop_config.json` 添加：
```json
{
  "mcpServers": {
    "vibe-trading": {
      "command": "vibe-trading-mcp"
    }
  }
}
```

### OpenClaw
在 `~/.openclaw/config.yaml` 添加：
```yaml
skills:
  - name: vibe-trading
    command: vibe-trading-mcp
```

### Cursor / Windsurf
```bash
vibe-trading-mcp                  # stdio（默认）
vibe-trading-mcp --transport sse  # SSE（Web 客户端）
```

### ClawHub 一键安装
```bash
npx clawhub@latest install vibe-trading --force
```

> `--force` 必要，因为技能引用外部 API 会触发 VirusTotal 自动扫描。代码完全开源，可安全审查。

### 54 MCP 工具分类

| 类别 | 工具 |
|------|------|
| **技能管理** | `list_skills`, `load_skill` |
| **研究目标** | `start_research_goal`, `get_research_goal`, `add_goal_evidence`, `update_research_goal_status` |
| **回测分析** | `backtest`, `factor_analysis`, `analyze_options`, `pattern_recognition` |
| **数据获取** | `read_url`, `read_document`, `web_search`, `get_market_data`, `get_fund_flow` |
| **文件操作** | `write_file`, `read_file` |
| **交易连接** | `trading_connections`, `trading_select_connection`, `trading_check`, `trading_account`, `trading_positions`, `trading_orders`, `trading_quote`, `trading_history` |
| **Swarm** | `list_swarm_presets`, `run_swarm`, `get_swarm_status`, `get_run_result`, `list_runs` |
| **A 股特色** | `get_dragon_tiger`, `get_northbound_flow`, `get_margin_trading`, `get_block_trades`, `get_shareholder_count`, `get_lockup_expiry`, `get_sector_info` |
| **研究与基本面** | `get_research_reports`, `get_stock_news`, `get_sec_filings`, `get_financial_statements`, `get_options_chain`, `get_stock_profile`, `screen_market`, `search_symbol`, `get_macro_series`, `iwencai_search` |
| **Shadow Account** | `analyze_trade_journal`, `extract_shadow_strategy`, `run_shadow_backtest`, `render_shadow_report`, `scan_shadow_signals` |

### OpenSpace — 自进化技能

Vibe-Trading 的 86 个金融技能已发布到 [open-space.cloud](https://open-space.cloud)，通过 OpenSpace 的自进化引擎自动演进。

## 外部 MCP 客户端模式

> **与 MCP 插件方向相反**：此功能让 Vibe-Trading 内置 Agent 调用你的外部 MCP 服务器。

### 快速配置

创建 `~/.vibe-trading/agent.json`（JSON 或 YAML）：

```json
{
  "mcpServers": {
    "my-server": {
      "command": "uvx",
      "args": ["my-mcp-server"]
    }
  }
}
```

### IBKR 官方只读 MCP

```json
{
  "mcpServers": {
    "ibkr": {
      "type": "streamableHttp",
      "url": "https://api.ibkr.com/v1/api/mcp",
      "auth": {
        "type": "oauth",
        "scopes": ["mcp.read"],
        "clientName": "Vibe-Trading",
        "cacheDir": "~/.vibe-trading/live/ibkr/oauth"
      },
      "enabledTools": ["*"]
    }
  }
}
```

工具命名规则：`mcp_<server>_<tool>`（如 `mcp_my_server_tool_name`）

### v1 限制
- 传输：stdio、SSE、streamable HTTP
- 执行：串行（不进入并行只读路径）
- 范围：仅 tools（不暴露 resources 和 prompts）
- 热加载：不支持，需重启进程
- Swarm：MCP 工具暂不在 Swarm worker 注册表中可用

## IM 频道（16 个适配器）

支持适配器：WebSocket、Telegram、Slack、Discord、Matrix、WhatsApp、Signal、QQ/NapCat、WeChat/WeCom、飞书/Lark、钉钉、Teams、email、Mochat

```bash
vibe-trading channels status
vibe-trading channels start
```

SDK 适配器需额外安装：`pip install "vibe-trading-ai[telegram]"` 或 `pip install "vibe-trading-ai[channels]"`

## 定时研究（Scheduler）

```bash
VIBE_TRADING_ENABLE_SCHEDULER=1 vibe-trading serve --port 8899

# 每 6 小时扫描 CSI300
curl -X POST http://localhost:8899/scheduled-runs \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Scan CSI300 for momentum breakouts","schedule":"0 */6 * * *"}'
```

定时任务持久化在 `~/.vibe-trading/`，重启后保留。

## 券商连接器

支持 10 个券商 SDK 连接器，**默认只读**：

| 连接器 | 状态 |
|--------|------|
| Robinhood | v0.1.0+ |
| Trading 212 | v0.1.11 新增 |
| IBKR（官方 MCP 只读） | v0.1.10+ |
| IBKR（本地 TWS/IB Gateway） | v0.1.10+ |
| Longbridge | 已支持 |

```bash
vibe-trading connector list
vibe-trading connector use ibkr-paper-local
vibe-trading connector check
vibe-trading connector account
vibe-trading connector positions
vibe-trading connector quote AAPL
```

**安全机制**：
- 双确认对话框（v0.1.11）
- Kill switch 可随时停止
- PreTradeAdvisoryInterface 记录建议但不绕过授权门
- 券商连接器工具统一为 `trading_*` 命名空间

## 相关页面
- [[concepts/vibe-trading/安装与使用]]
- [[concepts/vibe-trading/技术架构]]
- [[concepts/vibe-trading/项目总览]]
