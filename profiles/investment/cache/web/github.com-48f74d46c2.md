[Skip to content](https://github.com/simonlin1212/Vibe-Research/tree/main/backend#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/simonlin1212/Vibe-Research/tree/main/backend) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/simonlin1212/Vibe-Research/tree/main/backend) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/simonlin1212/Vibe-Research/tree/main/backend) to refresh your session.Dismiss alert

{{ message }}

[simonlin1212](https://github.com/simonlin1212)/ **[Vibe-Research](https://github.com/simonlin1212/Vibe-Research)** Public

- [Notifications](https://github.com/login?return_to=%2Fsimonlin1212%2FVibe-Research) You must be signed in to change notification settings
- [Fork\\
208](https://github.com/login?return_to=%2Fsimonlin1212%2FVibe-Research)
- [Star\\
931](https://github.com/login?return_to=%2Fsimonlin1212%2FVibe-Research)


## Collapse file tree

## Files

main

Search this repository(forward slash)` forward slash/`

/

# backend

/

Copy path

## Directory actions

## More options

More options

## Directory actions

## More options

More options

## Latest commit

[![simonlin1212](https://avatars.githubusercontent.com/u/166034225?v=4&size=40)](https://github.com/simonlin1212)[simonlin1212](https://github.com/simonlin1212/Vibe-Research/commits?author=simonlin1212)

[chore: a-stock-data 数据源 3.3.0→3.4.0 + 版本号 0.1.2→0.1.3](https://github.com/simonlin1212/Vibe-Research/commit/352d0a40d467f79e31fa90262c8342431d813c07)

Open commit details

last weekJul 11, 2026

[352d0a4](https://github.com/simonlin1212/Vibe-Research/commit/352d0a40d467f79e31fa90262c8342431d813c07) · last weekJul 11, 2026

## History

[History](https://github.com/simonlin1212/Vibe-Research/commits/main/backend)

Open commit details

[View commit history for this file.](https://github.com/simonlin1212/Vibe-Research/commits/main/backend) History

/

# backend

/

Copy path

Top

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ### parent directory<br> [..](https://github.com/simonlin1212/Vibe-Research/tree/main) |
| [tests](https://github.com/simonlin1212/Vibe-Research/tree/main/backend/tests "tests") | [tests](https://github.com/simonlin1212/Vibe-Research/tree/main/backend/tests "tests") | [fix: ETF 行情、持仓成本精度、用户数据防丢迁移 (](https://github.com/simonlin1212/Vibe-Research/commit/155e2eb0b0a516a948e33babfb772afe3da6fa8c "fix: ETF 行情、持仓成本精度、用户数据防丢迁移 (#10 #12 #13)  - #10 沪市 ETF（51/56/58 开头）行情前缀误判 sz 导致现价为 0，get_prefix 补 5 开头→sh - #13 加仓合并成本保留 4 位小数；持仓页现价/成本/清仓价显示放宽到 4 位，市值与手算对得上账 - #12 持仓/研报默认存储从仓库内 backend/.cache/ 迁到用户目录 ~/.vibe-research/   （VR_DATA_DIR 可覆盖），重新下载/覆盖项目文件夹不再丢数据；旧数据首次启动自动迁移   （临时文件+原子改名，中断可重试，原文件保留）；测试全程隔离到临时目录，不碰真实用户数据") [#10](https://github.com/simonlin1212/Vibe-Research/issues/10) [#12](https://github.com/simonlin1212/Vibe-Research/issues/12) [#13](https://github.com/simonlin1212/Vibe-Research/issues/13) [)](https://github.com/simonlin1212/Vibe-Research/commit/155e2eb0b0a516a948e33babfb772afe3da6fa8c "fix: ETF 行情、持仓成本精度、用户数据防丢迁移 (#10 #12 #13)  - #10 沪市 ETF（51/56/58 开头）行情前缀误判 sz 导致现价为 0，get_prefix 补 5 开头→sh - #13 加仓合并成本保留 4 位小数；持仓页现价/成本/清仓价显示放宽到 4 位，市值与手算对得上账 - #12 持仓/研报默认存储从仓库内 backend/.cache/ 迁到用户目录 ~/.vibe-research/   （VR_DATA_DIR 可覆盖），重新下载/覆盖项目文件夹不再丢数据；旧数据首次启动自动迁移   （临时文件+原子改名，中断可重试，原文件保留）；测试全程隔离到临时目录，不碰真实用户数据") | 2 weeks agoJul 10, 2026 |
| [.env.example](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/.env.example ".env.example") | [.env.example](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/.env.example ".env.example") | [feat: 首次发布 Vibe-Research —— 普通人的 AI 投研看板](https://github.com/simonlin1212/Vibe-Research/commit/2c60f2a73d0589f180f38258865b54e2bbff7189 "feat: 首次发布 Vibe-Research —— 普通人的 AI 投研看板  数据配齐、方向由你自己的 AI 给。不荐股 · 不预测 · 无倾向。  - A 股全栈数据（a-stock-data 自带即用，40 端点）+ 全球资讯（investment-news） - 每日复盘 / 资讯雷达 / 个股专业聚合页 / 我的持仓 / 研究记录 - 接入 AI：订阅 CLI + API 多模型 + MCP，全链路流式 - 投研分析框架焊入系统提示词；合规：只客观呈现、不荐股不预测") | 2 weeks agoJul 5, 2026 |
| [.gitignore](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/.gitignore ".gitignore") | [.gitignore](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/.gitignore ".gitignore") | [feat: 首次发布 Vibe-Research —— 普通人的 AI 投研看板](https://github.com/simonlin1212/Vibe-Research/commit/2c60f2a73d0589f180f38258865b54e2bbff7189 "feat: 首次发布 Vibe-Research —— 普通人的 AI 投研看板  数据配齐、方向由你自己的 AI 给。不荐股 · 不预测 · 无倾向。  - A 股全栈数据（a-stock-data 自带即用，40 端点）+ 全球资讯（investment-news） - 每日复盘 / 资讯雷达 / 个股专业聚合页 / 我的持仓 / 研究记录 - 接入 AI：订阅 CLI + API 多模型 + MCP，全链路流式 - 投研分析框架焊入系统提示词；合规：只客观呈现、不荐股不预测") | 2 weeks agoJul 5, 2026 |
| [README.md](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/README.md "README.md") | [README.md](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/README.md "README.md") | [feat: 首次发布 Vibe-Research —— 普通人的 AI 投研看板](https://github.com/simonlin1212/Vibe-Research/commit/2c60f2a73d0589f180f38258865b54e2bbff7189 "feat: 首次发布 Vibe-Research —— 普通人的 AI 投研看板  数据配齐、方向由你自己的 AI 给。不荐股 · 不预测 · 无倾向。  - A 股全栈数据（a-stock-data 自带即用，40 端点）+ 全球资讯（investment-news） - 每日复盘 / 资讯雷达 / 个股专业聚合页 / 我的持仓 / 研究记录 - 接入 AI：订阅 CLI + API 多模型 + MCP，全链路流式 - 投研分析框架焊入系统提示词；合规：只客观呈现、不荐股不预测") | 2 weeks agoJul 5, 2026 |
| [app.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/app.py "app.py") | [app.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/app.py "app.py") | [chore: a-stock-data 数据源 3.3.0→3.4.0 + 版本号 0.1.2→0.1.3](https://github.com/simonlin1212/Vibe-Research/commit/352d0a40d467f79e31fa90262c8342431d813c07 "chore: a-stock-data 数据源 3.3.0→3.4.0 + 版本号 0.1.2→0.1.3  - bundle a-stock-data/ 整包刷新到 v3.4.0（端点 40→43、数据源 13→15） - fix(解禁): lockup_expiry 随东财 2026 改列名更新字段——旧 LIMITED_STOCK_TYPE/FREE_SHARES_NUM 已废致 type/shares 恒空，改 FREE_SHARES_TYPE/FREE_SHARES 并新增 able_shares；前端 LockupRow 接口同步 - fix(行业排名): industry_comparison 补 fid=f3，top/bottom 按涨跌幅真实降序") | last weekJul 11, 2026 |
| [astock.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/astock.py "astock.py") | [astock.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/astock.py "astock.py") | [chore: a-stock-data 数据源 3.3.0→3.4.0 + 版本号 0.1.2→0.1.3](https://github.com/simonlin1212/Vibe-Research/commit/352d0a40d467f79e31fa90262c8342431d813c07 "chore: a-stock-data 数据源 3.3.0→3.4.0 + 版本号 0.1.2→0.1.3  - bundle a-stock-data/ 整包刷新到 v3.4.0（端点 40→43、数据源 13→15） - fix(解禁): lockup_expiry 随东财 2026 改列名更新字段——旧 LIMITED_STOCK_TYPE/FREE_SHARES_NUM 已废致 type/shares 恒空，改 FREE_SHARES_TYPE/FREE_SHARES 并新增 able_shares；前端 LockupRow 接口同步 - fix(行业排名): industry_comparison 补 fid=f3，top/bottom 按涨跌幅真实降序") | last weekJul 11, 2026 |
| [chat.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/chat.py "chat.py") | [chat.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/chat.py "chat.py") | [feat: 自选股批量添加+独立分栏、我的研报归档、AI 支持美股/港股/韩股](https://github.com/simonlin1212/Vibe-Research/commit/06d3fe961b92cb8b2c028038edc4e86a3e64a921 "feat: 自选股批量添加+独立分栏、我的研报归档、AI 支持美股/港股/韩股  粉丝反馈批量修复（GitHub issues #1/#3/#6/#7/#8）+ 全量审计加固：  - 接入AI：移除已停止支持的 Gemini CLI；DeepSeek 升 V4（flash/pro，旧别名 7/24 弃用） - 个股/AI：新增 query_global_stock，AI 可分析美股/港股/韩股（韩股走 .KS 后缀，如 005930.KS）；   修 gstock 韩元小数位缩放与美股财务守卫 - 自选股：新增独立侧栏分栏，支持批量粘贴代码添加 + 一屏表格总览 - 我的研报：拖拽/多选上传归档、按文件名自动分行业（存本地/不上传/不进仓库） - 我的持仓：成本价放开正负限制（按结果算盈亏） - 修复：Vite 默认代理 localhost→127.0.0.1（IPv6 连接失败）；清仓日期格式校验 - 安全（审计加固）：chat baseURL 防 SSRF（本地放行本机/公网姿态挡内网）；   研报索引原子写 + 锁；data:URI 无逗号守卫 - 测试：新增 tests/test_reports_and_security.py，离线 38 passed") | 2 weeks agoJul 7, 2026 |
| [cli\_runtime.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/cli_runtime.py "cli_runtime.py") | [cli\_runtime.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/cli_runtime.py "cli_runtime.py") | [feat: 自选股批量添加+独立分栏、我的研报归档、AI 支持美股/港股/韩股](https://github.com/simonlin1212/Vibe-Research/commit/06d3fe961b92cb8b2c028038edc4e86a3e64a921 "feat: 自选股批量添加+独立分栏、我的研报归档、AI 支持美股/港股/韩股  粉丝反馈批量修复（GitHub issues #1/#3/#6/#7/#8）+ 全量审计加固：  - 接入AI：移除已停止支持的 Gemini CLI；DeepSeek 升 V4（flash/pro，旧别名 7/24 弃用） - 个股/AI：新增 query_global_stock，AI 可分析美股/港股/韩股（韩股走 .KS 后缀，如 005930.KS）；   修 gstock 韩元小数位缩放与美股财务守卫 - 自选股：新增独立侧栏分栏，支持批量粘贴代码添加 + 一屏表格总览 - 我的研报：拖拽/多选上传归档、按文件名自动分行业（存本地/不上传/不进仓库） - 我的持仓：成本价放开正负限制（按结果算盈亏） - 修复：Vite 默认代理 localhost→127.0.0.1（IPv6 连接失败）；清仓日期格式校验 - 安全（审计加固）：chat baseURL 防 SSRF（本地放行本机/公网姿态挡内网）；   研报索引原子写 + 锁；data:URI 无逗号守卫 - 测试：新增 tests/test_reports_and_security.py，离线 38 passed") | 2 weeks agoJul 7, 2026 |
| [conftest.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/conftest.py "conftest.py") | [conftest.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/conftest.py "conftest.py") | [fix: ETF 行情、持仓成本精度、用户数据防丢迁移 (](https://github.com/simonlin1212/Vibe-Research/commit/155e2eb0b0a516a948e33babfb772afe3da6fa8c "fix: ETF 行情、持仓成本精度、用户数据防丢迁移 (#10 #12 #13)  - #10 沪市 ETF（51/56/58 开头）行情前缀误判 sz 导致现价为 0，get_prefix 补 5 开头→sh - #13 加仓合并成本保留 4 位小数；持仓页现价/成本/清仓价显示放宽到 4 位，市值与手算对得上账 - #12 持仓/研报默认存储从仓库内 backend/.cache/ 迁到用户目录 ~/.vibe-research/   （VR_DATA_DIR 可覆盖），重新下载/覆盖项目文件夹不再丢数据；旧数据首次启动自动迁移   （临时文件+原子改名，中断可重试，原文件保留）；测试全程隔离到临时目录，不碰真实用户数据") [#10](https://github.com/simonlin1212/Vibe-Research/issues/10) [#12](https://github.com/simonlin1212/Vibe-Research/issues/12) [#13](https://github.com/simonlin1212/Vibe-Research/issues/13) [)](https://github.com/simonlin1212/Vibe-Research/commit/155e2eb0b0a516a948e33babfb772afe3da6fa8c "fix: ETF 行情、持仓成本精度、用户数据防丢迁移 (#10 #12 #13)  - #10 沪市 ETF（51/56/58 开头）行情前缀误判 sz 导致现价为 0，get_prefix 补 5 开头→sh - #13 加仓合并成本保留 4 位小数；持仓页现价/成本/清仓价显示放宽到 4 位，市值与手算对得上账 - #12 持仓/研报默认存储从仓库内 backend/.cache/ 迁到用户目录 ~/.vibe-research/   （VR_DATA_DIR 可覆盖），重新下载/覆盖项目文件夹不再丢数据；旧数据首次启动自动迁移   （临时文件+原子改名，中断可重试，原文件保留）；测试全程隔离到临时目录，不碰真实用户数据") | 2 weeks agoJul 10, 2026 |
| [gstock.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/gstock.py "gstock.py") | [gstock.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/gstock.py "gstock.py") | [feat: 自选股批量添加+独立分栏、我的研报归档、AI 支持美股/港股/韩股](https://github.com/simonlin1212/Vibe-Research/commit/06d3fe961b92cb8b2c028038edc4e86a3e64a921 "feat: 自选股批量添加+独立分栏、我的研报归档、AI 支持美股/港股/韩股  粉丝反馈批量修复（GitHub issues #1/#3/#6/#7/#8）+ 全量审计加固：  - 接入AI：移除已停止支持的 Gemini CLI；DeepSeek 升 V4（flash/pro，旧别名 7/24 弃用） - 个股/AI：新增 query_global_stock，AI 可分析美股/港股/韩股（韩股走 .KS 后缀，如 005930.KS）；   修 gstock 韩元小数位缩放与美股财务守卫 - 自选股：新增独立侧栏分栏，支持批量粘贴代码添加 + 一屏表格总览 - 我的研报：拖拽/多选上传归档、按文件名自动分行业（存本地/不上传/不进仓库） - 我的持仓：成本价放开正负限制（按结果算盈亏） - 修复：Vite 默认代理 localhost→127.0.0.1（IPv6 连接失败）；清仓日期格式校验 - 安全（审计加固）：chat baseURL 防 SSRF（本地放行本机/公网姿态挡内网）；   研报索引原子写 + 锁；data:URI 无逗号守卫 - 测试：新增 tests/test_reports_and_security.py，离线 38 passed") | 2 weeks agoJul 7, 2026 |
| [market.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/market.py "market.py") | [market.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/market.py "market.py") | [feat: 接入 global-stock-data —— 多市场（美股 / 港股）](https://github.com/simonlin1212/Vibe-Research/commit/fc2d3960023b67eb1a872c68f9b30ae19962a6e8 "feat: 接入 global-stock-data —— 多市场（美股 / 港股）  - 每日复盘加「全球市场」栏：隔夜美股（道指/标普/纳指）+ 港股（恒指/恒生科技） - 个股页支持美股/港股代码（AAPL / 00700）：行情 + 关键财务指标 - 后端 gstock.py 移植东财域内合规子集，复用 astock.em_get 直连；push2→push2delay 兜底 - global-stock-data v1.0.1 整包 bundle 进仓库，README/架构/致谢/相关生态同步") | 2 weeks agoJul 5, 2026 |
| [mcp\_server.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/mcp_server.py "mcp_server.py") | [mcp\_server.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/mcp_server.py "mcp_server.py") | [chore: a-stock-data 数据源 3.3.0→3.4.0 + 版本号 0.1.2→0.1.3](https://github.com/simonlin1212/Vibe-Research/commit/352d0a40d467f79e31fa90262c8342431d813c07 "chore: a-stock-data 数据源 3.3.0→3.4.0 + 版本号 0.1.2→0.1.3  - bundle a-stock-data/ 整包刷新到 v3.4.0（端点 40→43、数据源 13→15） - fix(解禁): lockup_expiry 随东财 2026 改列名更新字段——旧 LIMITED_STOCK_TYPE/FREE_SHARES_NUM 已废致 type/shares 恒空，改 FREE_SHARES_TYPE/FREE_SHARES 并新增 able_shares；前端 LockupRow 接口同步 - fix(行业排名): industry_comparison 补 fid=f3，top/bottom 按涨跌幅真实降序") | last weekJul 11, 2026 |
| [myreports.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/myreports.py "myreports.py") | [myreports.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/myreports.py "myreports.py") | [fix: ETF 行情、持仓成本精度、用户数据防丢迁移 (](https://github.com/simonlin1212/Vibe-Research/commit/155e2eb0b0a516a948e33babfb772afe3da6fa8c "fix: ETF 行情、持仓成本精度、用户数据防丢迁移 (#10 #12 #13)  - #10 沪市 ETF（51/56/58 开头）行情前缀误判 sz 导致现价为 0，get_prefix 补 5 开头→sh - #13 加仓合并成本保留 4 位小数；持仓页现价/成本/清仓价显示放宽到 4 位，市值与手算对得上账 - #12 持仓/研报默认存储从仓库内 backend/.cache/ 迁到用户目录 ~/.vibe-research/   （VR_DATA_DIR 可覆盖），重新下载/覆盖项目文件夹不再丢数据；旧数据首次启动自动迁移   （临时文件+原子改名，中断可重试，原文件保留）；测试全程隔离到临时目录，不碰真实用户数据") [#10](https://github.com/simonlin1212/Vibe-Research/issues/10) [#12](https://github.com/simonlin1212/Vibe-Research/issues/12) [#13](https://github.com/simonlin1212/Vibe-Research/issues/13) [)](https://github.com/simonlin1212/Vibe-Research/commit/155e2eb0b0a516a948e33babfb772afe3da6fa8c "fix: ETF 行情、持仓成本精度、用户数据防丢迁移 (#10 #12 #13)  - #10 沪市 ETF（51/56/58 开头）行情前缀误判 sz 导致现价为 0，get_prefix 补 5 开头→sh - #13 加仓合并成本保留 4 位小数；持仓页现价/成本/清仓价显示放宽到 4 位，市值与手算对得上账 - #12 持仓/研报默认存储从仓库内 backend/.cache/ 迁到用户目录 ~/.vibe-research/   （VR_DATA_DIR 可覆盖），重新下载/覆盖项目文件夹不再丢数据；旧数据首次启动自动迁移   （临时文件+原子改名，中断可重试，原文件保留）；测试全程隔离到临时目录，不碰真实用户数据") | 2 weeks agoJul 10, 2026 |
| [news\_sources.json](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/news_sources.json "news_sources.json") | [news\_sources.json](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/news_sources.json "news_sources.json") | [feat: 首次发布 Vibe-Research —— 普通人的 AI 投研看板](https://github.com/simonlin1212/Vibe-Research/commit/2c60f2a73d0589f180f38258865b54e2bbff7189 "feat: 首次发布 Vibe-Research —— 普通人的 AI 投研看板  数据配齐、方向由你自己的 AI 给。不荐股 · 不预测 · 无倾向。  - A 股全栈数据（a-stock-data 自带即用，40 端点）+ 全球资讯（investment-news） - 每日复盘 / 资讯雷达 / 个股专业聚合页 / 我的持仓 / 研究记录 - 接入 AI：订阅 CLI + API 多模型 + MCP，全链路流式 - 投研分析框架焊入系统提示词；合规：只客观呈现、不荐股不预测") | 2 weeks agoJul 5, 2026 |
| [newsradar.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/newsradar.py "newsradar.py") | [newsradar.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/newsradar.py "newsradar.py") | [feat: 首次发布 Vibe-Research —— 普通人的 AI 投研看板](https://github.com/simonlin1212/Vibe-Research/commit/2c60f2a73d0589f180f38258865b54e2bbff7189 "feat: 首次发布 Vibe-Research —— 普通人的 AI 投研看板  数据配齐、方向由你自己的 AI 给。不荐股 · 不预测 · 无倾向。  - A 股全栈数据（a-stock-data 自带即用，40 端点）+ 全球资讯（investment-news） - 每日复盘 / 资讯雷达 / 个股专业聚合页 / 我的持仓 / 研究记录 - 接入 AI：订阅 CLI + API 多模型 + MCP，全链路流式 - 投研分析框架焊入系统提示词；合规：只客观呈现、不荐股不预测") | 2 weeks agoJul 5, 2026 |
| [portfolio.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/portfolio.py "portfolio.py") | [portfolio.py](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/portfolio.py "portfolio.py") | [fix: ETF 行情、持仓成本精度、用户数据防丢迁移 (](https://github.com/simonlin1212/Vibe-Research/commit/155e2eb0b0a516a948e33babfb772afe3da6fa8c "fix: ETF 行情、持仓成本精度、用户数据防丢迁移 (#10 #12 #13)  - #10 沪市 ETF（51/56/58 开头）行情前缀误判 sz 导致现价为 0，get_prefix 补 5 开头→sh - #13 加仓合并成本保留 4 位小数；持仓页现价/成本/清仓价显示放宽到 4 位，市值与手算对得上账 - #12 持仓/研报默认存储从仓库内 backend/.cache/ 迁到用户目录 ~/.vibe-research/   （VR_DATA_DIR 可覆盖），重新下载/覆盖项目文件夹不再丢数据；旧数据首次启动自动迁移   （临时文件+原子改名，中断可重试，原文件保留）；测试全程隔离到临时目录，不碰真实用户数据") [#10](https://github.com/simonlin1212/Vibe-Research/issues/10) [#12](https://github.com/simonlin1212/Vibe-Research/issues/12) [#13](https://github.com/simonlin1212/Vibe-Research/issues/13) [)](https://github.com/simonlin1212/Vibe-Research/commit/155e2eb0b0a516a948e33babfb772afe3da6fa8c "fix: ETF 行情、持仓成本精度、用户数据防丢迁移 (#10 #12 #13)  - #10 沪市 ETF（51/56/58 开头）行情前缀误判 sz 导致现价为 0，get_prefix 补 5 开头→sh - #13 加仓合并成本保留 4 位小数；持仓页现价/成本/清仓价显示放宽到 4 位，市值与手算对得上账 - #12 持仓/研报默认存储从仓库内 backend/.cache/ 迁到用户目录 ~/.vibe-research/   （VR_DATA_DIR 可覆盖），重新下载/覆盖项目文件夹不再丢数据；旧数据首次启动自动迁移   （临时文件+原子改名，中断可重试，原文件保留）；测试全程隔离到临时目录，不碰真实用户数据") | 2 weeks agoJul 10, 2026 |
| [requirements-dev.txt](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/requirements-dev.txt "requirements-dev.txt") | [requirements-dev.txt](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/requirements-dev.txt "requirements-dev.txt") | [feat: 首次发布 Vibe-Research —— 普通人的 AI 投研看板](https://github.com/simonlin1212/Vibe-Research/commit/2c60f2a73d0589f180f38258865b54e2bbff7189 "feat: 首次发布 Vibe-Research —— 普通人的 AI 投研看板  数据配齐、方向由你自己的 AI 给。不荐股 · 不预测 · 无倾向。  - A 股全栈数据（a-stock-data 自带即用，40 端点）+ 全球资讯（investment-news） - 每日复盘 / 资讯雷达 / 个股专业聚合页 / 我的持仓 / 研究记录 - 接入 AI：订阅 CLI + API 多模型 + MCP，全链路流式 - 投研分析框架焊入系统提示词；合规：只客观呈现、不荐股不预测") | 2 weeks agoJul 5, 2026 |
| [requirements.txt](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/requirements.txt "requirements.txt") | [requirements.txt](https://github.com/simonlin1212/Vibe-Research/blob/main/backend/requirements.txt "requirements.txt") | [feat: 首次发布 Vibe-Research —— 普通人的 AI 投研看板](https://github.com/simonlin1212/Vibe-Research/commit/2c60f2a73d0589f180f38258865b54e2bbff7189 "feat: 首次发布 Vibe-Research —— 普通人的 AI 投研看板  数据配齐、方向由你自己的 AI 给。不荐股 · 不预测 · 无倾向。  - A 股全栈数据（a-stock-data 自带即用，40 端点）+ 全球资讯（investment-news） - 每日复盘 / 资讯雷达 / 个股专业聚合页 / 我的持仓 / 研究记录 - 接入 AI：订阅 CLI + API 多模型 + MCP，全链路流式 - 投研分析框架焊入系统提示词；合规：只客观呈现、不荐股不预测") | 2 weeks agoJul 5, 2026 |
| View all files |

## [README.md](https://github.com/simonlin1212/Vibe-Research/tree/main/backend\#readme)

Outline

# Vibe-Research Backend

[Permalink: Vibe-Research Backend](https://github.com/simonlin1212/Vibe-Research/tree/main/backend#vibe-research-backend)

A股数据层 + 可插拔 AI 层。全部只读、无状态；不预置任何标的、不推荐、不预测。

## 安装

[Permalink: 安装](https://github.com/simonlin1212/Vibe-Research/tree/main/backend#%E5%AE%89%E8%A3%85)

```
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

> 行情 \+ 研报只需 `fastapi / uvicorn / requests`（秒装、必可用）。
> 一致预期 / 新闻 / 公告需 `akshare`，K线 / 财务需 `mootdx`；未装时对应端点返回 501 + 安装提示，不影响其余功能。

## 1\. HTTP API（给网页前端 + 系统 AI）

[Permalink: 1. HTTP API（给网页前端 + 系统 AI）](https://github.com/simonlin1212/Vibe-Research/tree/main/backend#1-http-api%E7%BB%99%E7%BD%91%E9%A1%B5%E5%89%8D%E7%AB%AF--%E7%B3%BB%E7%BB%9F-ai)

```
.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8900
```

| 端点 | 说明 | 依赖 |
| --- | --- | --- |
| `GET /api/health` | 健康检查 | — |
| `GET /api/indices` | 大盘指数实时行情 | stdlib |
| `GET /api/quote?codes=600519,000858` | 实时行情（PE/PB/市值/涨跌停…） | stdlib |
| `GET /api/valuation?code=600519` | 完整估值（前向PE/PEG/消化年数） | requests+akshare |
| `GET /api/valuation/percentile?code=600519` | 估值历史分位（近5年·百度股市通） | akshare |
| `GET /api/financials?code=600519` | 财务关键指标（同花顺摘要，最新报告期，前端个股页用） | akshare |
| `GET /api/reports?code=600519` | 个股研报列表（含 PDF 链接） | requests |
| `GET /api/announcements?code=600519` | 近期公告（东财） | requests |
| `GET /api/news?code=600519` | 个股新闻 | akshare |
| `GET /api/kline?code=600519` | K线 | mootdx |
| `GET /api/finance?code=600519` | 季报财务快照（mootdx，前端未用 / 备用） | mootdx |
| **资金面·筹码·信号（v3.3）** | `/api/margin` · `/block-trade` · `/holders` · `/dividend` · `/fund-flow` · `/dragon-tiger` · `/lockup` · `/blocks` · `/hot-concepts` · `/investor-qa` · `/industry` | requests |
| `GET /api/market/overview` · `/api/radar` | 市场情绪+板块资金 · 资讯雷达 | akshare / stdlib |
| `POST /api/chat` | 系统 AI 对话（function calling，AI 自己调数据工具） | requests |

> 上表为主要端点；完整路由清单见 `app.py`。要更全量的 A 股数据（打板 / ETF期权 / 全市场行业排名等），用根目录 [`a-stock-data/`](https://github.com/simonlin1212/Vibe-Research/blob/main/a-stock-data/SKILL.md) 工具箱。

`/api/chat` 请求体：

```
{
  "messages": [{"role": "user", "content": "茅台估值贵不贵？"}],
  "context": "本页上下文（可空）",
  "llm": {"baseURL": "https://api.deepseek.com", "apiKey": "sk-…", "model": "deepseek-chat"}
}
```

`llm` 由前端从本地配置随请求带上，后端不持久化 key。

## 2\. MCP Server（给 Claude Code / 高手 agent）

[Permalink: 2. MCP Server（给 Claude Code / 高手 agent）](https://github.com/simonlin1212/Vibe-Research/tree/main/backend#2-mcp-server%E7%BB%99-claude-code--%E9%AB%98%E6%89%8B-agent)

零第三方依赖，复用同一套数据工具。挂进 Claude Code：

```
claude mcp add vibe-research -- \
  "$(pwd)/.venv/bin/python" "$(pwd)/mcp_server.py"
```

挂上后，你的 agent 直接拥有 `query_quote / query_valuation / query_reports / query_news` 四个工具，
用你自己的订阅额度调数据、多步分析——无需 API key、不占本产品成本。

### 完整 A 股数据工具箱（随仓库自带）

[Permalink: 完整 A 股数据工具箱（随仓库自带）](https://github.com/simonlin1212/Vibe-Research/tree/main/backend#%E5%AE%8C%E6%95%B4-a-%E8%82%A1%E6%95%B0%E6%8D%AE%E5%B7%A5%E5%85%B7%E7%AE%B1%E9%9A%8F%E4%BB%93%E5%BA%93%E8%87%AA%E5%B8%A6)

MCP 的 4 个工具是「零配置、开箱即用」的常用项。若 agent 需要更全的 A 股数据（龙虎榜 / 融资融券 / 大宗交易 / 股东户数 / 分红 / 资金流 / 解禁 / 概念板块 / 打板情绪 / ETF 期权 / 互动易 / 全市场行业排名 …共 **40 个端点**），本仓库根目录 **自带完整数据源** [`a-stock-data/`](https://github.com/simonlin1212/Vibe-Research/blob/main/a-stock-data/SKILL.md)（a-stock-data v3.3）：

- 要调哪个接口，直接看 [`a-stock-data/SKILL.md`](https://github.com/simonlin1212/Vibe-Research/blob/main/a-stock-data/SKILL.md)——每个端点都有 copy-paste 即用的代码（内嵌全部调用逻辑，零第三方数据封装依赖，东财接口已内置限流防封）。
- 运行依赖：`pip install mootdx requests pandas stockstats`（自包含，v3.0 起已移除 akshare）。
- 上游与更新： [github.com/simonlin1212/a-stock-data](https://github.com/simonlin1212/a-stock-data)（不更新也能一直用，自带的是固定可用快照）。
- 分工： **MCP 4 工具** = 网页 / 轻量常用； **自带数据源 40+ 端点** = agent 深度自助调研的全量工具箱。二者同源，按需取用。

## 合规

[Permalink: 合规](https://github.com/simonlin1212/Vibe-Research/tree/main/backend#%E5%90%88%E8%A7%84)

- 数据端点只返回客观行情/研报/财报/新闻，不含任何建议、排名、预测。
- `/api/chat` 的 system prompt 内置中立红线：不荐股、不预测涨跌、不给买卖时机、不构成投资建议。
- 分析结论一律由用户配置的模型 / agent 给出，本产品只提供数据与工具。

You can’t perform that action at this time.