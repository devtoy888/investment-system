# 数据来源与分析陷阱（实战提炼）

> 本文件沉淀自减仓/板块筛选实战。覆盖：可用数据源、限流处理、ETF联接陷阱、重叠计算、公平对比、减持时机、R2上传命令。

## 一、数据源矩阵（A股基金/指数，实测可用）

| 需求 | 数据源 | 调用方式 | 坑 |
|:----|:----|:----|:----|
| 指数历史K线(日) | 腾讯 `web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,START,END,250,qfq` | docker内curl，单进程串行，每次间隔2.5s | 循环连发必限流(返回空)。用 `docker exec hermes-main curl` 单发，逐支间隔≥2.5s |
| 指数历史K线 | AKShare `ak.stock_zh_index_daily(symbol='sh000688')` | docker内python | 稳定，推荐首选 |
| 基金净值历史 | AKShare `ak.fund_open_fund_info_em(symbol='003096', indicator='单位净值走势')` | docker内python | 大输出不要靠 stdout 传 JSON（会被截断）— 在容器内写 `/tmp/xxx.json` 再读 |
| 基金实时估值 | 腾讯 `http://qt.gtimg.cn/q=f_{code}` | docker内curl | 格式 `v_f_xxxx="代码~名称~..."`，字段4=净值 字段6=估算涨跌 |
| 基金前十大持仓 | 天天基金 `https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}&topline=10` | docker内curl，单发间隔5s，失败重试3次 | 限流极严，循环/批量必失败。单支间隔≥5s，重试sleep 8s |
| 基金持仓(AKShare) | `ak.fund_portfolio_hold_em` / `ak.fund_portfolio_industry_allocation_em` | docker内python | 个股持仓接口连东财同限流；行业配置接口(`industry_allocation_em`)能通 |

东财限流特征：连续请求返回空或 502/429。破解=单进程+长延迟(5s)+缓存文件避免重复拉。

## 二、ETF联接基金陷阱（关键分析坑）

011613 华夏科创50ETF联接C、024418 华夏半导体材料设备ETF联接C 是被动指数基金。其"前十大持仓"表内是目标ETF的成分股，权重极低(0.01%~8.68%)，不能直接按个股权重算重叠。

- 真实暴露 = 跟踪指数：011613≈科创50(半导体40%+光伏20%+AI软件15%+医药10%)；024418=纯半导体材料设备
- 024418(半导体材料) ⊆ 011613(科创50半导体部分) → 减024418不影响半导体敞口，011613已覆盖
- 主动基金(大摩系列)才是真个股权重，重叠用个股名比对

## 三、持仓重叠计算方法

1. 拉每支基金实际前十大（东财单发或AKShare行业配置兜底）
2. 逐对比对共同股票 + 重叠侧仓位权重：重叠仓位 = Σ(共同股票占该基金净值比)
3. 标注每支"被其他基金共同持有的股票数"=冗余度
4. ETF联接用指数成分替代个股

## 四、公平对比铁律

绝不用"成立以来"收益跨基金比（成立日不同→样本期不同→失真）。必须切到同一时间窗口再比。例：026449(2026-01-27成立) vs 017103，把017103也截到2026-01-27起比，结果026449 +44.6% vs 017103 +69.4%（同窗内017103仍强，但差距从"349% vs 44%"的假象收窄到24.7个百分点）。

## 五、减持时机原则

等反弹减，不在急跌砍（行为金融：急跌流动性最差、恐慌溢价最高，卖出实现亏损最大化；反弹时买盘回归，减少实际亏损）。若次日科技反弹(+2%+)是更好卖点；若继续跌可观望或减一部分。减仓是"结构性调仓"(86.7%→45%)，非止损离场。

## 六、R2上传（实测可用命令）

r2_uploader.py 在 /opt/data/（不在 scripts/）。r2_upload_and_verify.py 不可用（引用缺失模块+CLI参数顺序错）。

```bash
cd /opt/data
export $(grep -E '^R2_' /opt/data/profiles/investment/.env | xargs)
PYTHONPATH=/opt/data python3 r2_uploader.py <本地文件> <remote-key> 'text/markdown; charset=utf-8'
# 例: fund-system/reports/xxx.md  /  fund-system/reports/xxx.html 'text/html; charset=utf-8'
```
验证：HTTP 200 + Content-Type含utf-8 + 中文可读。

## 七、报告交付规范

- 基金编号必须带完整ETF名称，如 `011613 · 华夏科创50ETF联接C`
- 同步生成 .md + 同名 .html（深色自适应UI，fetch .md + marked.js 渲染）
- 上传R2后返回两个URL供预览
