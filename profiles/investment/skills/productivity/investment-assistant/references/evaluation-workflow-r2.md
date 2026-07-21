# 投资评估工作流铁律 + R2 上传实操（2026-07 会话沉淀）

## 1. 全行业筛选，不举例
用户要求"扩展全行业筛选评估"时，**必须拉全市场指数 ≥18 个板块的 6 个月数据排序**，不能只评用户点名的几个（如机器人/商业航天）。

- 指数源：AKShare `ak.stock_zh_index_daily(symbol='sh000688')`，逐指数串行拉（间隔 2s），腾讯 `web.ifzq.gtimg.cn` 连续请求会限流返回空，AKShare 更稳。
- 必算指标：6月累计、近20天、最大回撤、年化波动（`statistics.pstdev(rets)*(252**0.5)`）。
- 用户目标若为"最大化挣钱"，排序后优先看收益+近期动量，而非仅防御。

## 2. KOL 信号 × 实际数据 交叉验证
减仓/调仓方案须同时给出：
(a) 全行业收益数据（客观）
(b) 主任微博实际赛道提及（主观观点）
二者对照。若用户方案含主任**从未提及**的赛道（医药/机器人/卫星），须明确标注"属用户独立判断，主任不反对也不支持"——避免把用户自己想法误植为 KOL 背书。

## 3. R2 上传正确调用（曾踩坑）
- 脚本位置：`/opt/data/r2_uploader.py`（**不在 scripts/**，在根目录）。
- CLI 用法：`python3 r2_uploader.py <file_path> <key> [content_type]` —— **无 upload 子命令**（曾误传 `upload` 导致把参数当文件路径）。
- 凭证加载：脚本读 `.env`，但当前 shell 未 export。需先：
  `export $(grep -E '^R2_' /opt/data/profiles/investment/.env | xargs)`
- 中文防乱码：content_type 必须带 `charset=utf-8`（如 `'text/markdown; charset=utf-8'`）。
- 验证：上传后 `urllib.request` 回读，确认 HTTP 200 + 解码 utf-8 中文可读。

## 4. 报告双交付
每份评估同时生成 `.md` + 同名 `.html`（深色自适应，fetch md + marked.js 渲染），一并传 R2 供手机预览。HTML 模板套路：`header` 写标题/日期/源链接 + `marked.parse(fetch(md))` 注入 `.md-content` 容器。
