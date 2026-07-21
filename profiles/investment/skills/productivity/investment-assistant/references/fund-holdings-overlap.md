# 基金持仓重叠分析 — 实战手册

> 来源: 2026-07-15 全量减仓评估会话。用户要求"减持哪个必须拿出与哪个基金持仓重叠的具体事实"。

## 一、抓取单支基金前十大持仓（实际可行路径）

东财 `fundf10` 接口免费、无需 token，但从容器内连续请求会被限流（返回空/302）。
逐支单独 `docker exec curl` + 间隔 3~5 秒可稳定拿到。

```python
import subprocess, re, time

def curl_holdings(code, retries=4):
    url = f"https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}&topline=10&year=&month="
    for i in range(retries):
        try:
            r = subprocess.run(
                ["docker", "exec", "hermes-main", "curl", "-s", "--max-time", "15", url,
                 "-H", "User-Agent: Mozilla/5.0", "-H", "Referer: http://fundf10.eastmoney.com/"],
                capture_output=True, timeout=20)
            txt = r.stdout.decode('utf-8', errors='replace')
            m = re.search(r'content:"(.*?)",', txt, re.DOTALL)
            if m:
                raw = m.group(1).replace('\\r','').replace('\\n','\n').replace('\\t','\t').replace('\\"','"')
                raw = raw.encode('utf-8').decode('unicode_escape')
                try: raw = raw.encode('latin-1').decode('utf-8')   # 修复中文乱码
                except: pass
                stocks = []
                rows = re.findall(r'<tr[^>]*>(.*?)</tr>', raw, re.DOTALL)
                for row in rows[1:]:
                    cols = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
                    clean = [re.sub(r'<[^>]+>','',c).strip() for c in cols]
                    if len(clean) >= 3 and clean[0].isdigit():
                        stocks.append({'name': clean[2], 'pct': clean[-2] if len(clean)>6 else ''})
                if stocks: return stocks
        except: pass
        time.sleep(5)
    return None
```

### 限流兜底数据源
- 指数历史K线：腾讯 `https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,2026-01-15,2026-07-15,250,qfq` （返回 `data[code].day` 数组 [日期,开,收,高,低,量]，close 在 index 2）。
- 基金历史净值：AKShare `fund_open_fund_info_em(symbol, indicator='单位净值走势')`；stdout 截断时改 `Path(...).write_text(json.dumps(...))` 再读文件。
- 基金行业配置：AKShare `fund_portfolio_industry_allocation_em(symbol, date='2026')`（东财限流时个股接口 `fund_portfolio_hold_em` 报错，行业配置接口仍可用）。
- 腾讯 `qt.gtimg.cn/q=f_{code}` 实时估值当日不稳定（返回 `v_pv_none_match`），勿依赖。

## 二、⚠️ ETF联接基金的致命陷阱（本会话核心修正）

**011613 华夏科创50ETF联接、024418 华夏半导体材料设备ETF联接** 是被动指数基金。
其"前十大持仓"表是**目标 ETF 的成分股**，权重极低（0.01%~8.68%），
**绝不能和主动基金（大摩系列）按个股权重逐支比重叠**。

正确做法——看真实指数暴露：
- 011613 = 科创50 指数 ≈ 半导体40% + 光伏20% + AI软件15% + 医药10% + 其他15%
- 024418 = 半导体材料设备全指（中微/拓荆/华海清科/沪硅产业…）
- 结论：**024418 ⊆ 011613**（纯半导体材料设备 是 科创50 半导体部分的子集）→ 减 024418 不削弱半导体敞口，011613 已覆盖。

主动基金之间（大摩 017103/014871/011712/020233/026449）才适合做个股级重叠比对。

## 三、逐对重叠聚合（可复用骨架）

```python
import itertools
# holdings = {fund_key: {stock_name: weight_pct, ...}, ...}
pairs = []
for a, b in itertools.combinations(holdings, 2):
    overlap = set(holdings[a]) & set(holdings[b])
    if overlap:
        wa = sum(holdings[a][s] for s in overlap)
        wb = sum(holdings[b][s] for s in overlap)
        pairs.append((a, b, len(overlap), wa, wb, list(overlap)))
pairs.sort(key=lambda x: -(x[3]+x[4])/2)   # 按重叠仓位降序
```

## 四、业绩比较铁律（用户明确纠正）

**不要拿"成立以来"涨幅比不同成立日的基金**——成立早的自然累计长。
必须切到**同一时间窗口**再比：
```python
sub = [d for d in nav_series if d['date'] >= '2026-01-27']   # 较晚基金成立日
total_ret = (sub[-1]['nav'] / sub[0]['nav'] - 1) * 100
```
本例：026449(成立2026-01-27) vs 017103，同段(01-27→07-14) 017103 +69.37% > 026449 +44.66%，
即便公平对比 017103 仍更强 → 保留 017103、清仓 026449 有据。

## 五-B、⚠️ 致命错误：用行业指数收益率替代基金净值收益率

**用户纠正（2026-07-16）：** 分析某基金表现时，绝不能把"所属行业指数"的涨跌幅当成"该基金"的涨跌幅。

**真实案例：** 024418 华夏半导体材料设备ETF联接C，被误用"中证半导体指数6个月 -25%"当成基金收益，得出"今年-25%最弱、被011613完全包含"的错误结论。
**实际（AKShare `fund_open_fund_info_em` 拉真实净值）：** 024418 今年 **+101.2%**，是组合里涨最多的；011613 科创50联接 今年 +35.5%。两者不是包含关系，024418 涨得更好。

**铁律：**
1. 基金收益 = 该基金单位净值（AKShare `fund_open_fund_info_em(symbol, indicator='单位净值走势')`）算出的区间回报。
2. 行业指数（中证半导体/科创50/中证医疗…）只能用于**板块趋势背景**，绝不能当某支基金的实际收益。
3. ETF联接基金的"涨跌"由其目标ETF跟踪的指数决定，但仍要以**基金自身净值**为准，不要凭指数推断。
4. "被XX完全包含"这类结论必须基于实际持仓/指数暴露，不能凭主题名称臆断（024418半导体材料设备 ≠ 011613科创50的子集，前者涨更好）。

**正确算法：**
```python
import akshare as ak
from datetime import date
df = ak.fund_open_fund_info_em(symbol=code, indicator='单位净值走势')
rows = [(r[0], float(r[1])) for r in df.values.tolist() if r[0] >= date(2026,1,1)]
ytd = (rows[-1][1]/rows[0][1]-1)*100   # 今年收益，以基金净值算
```

## 五、减仓决策的事实支撑模板

用户要求每条减持都要有"具体与哪支基金重叠多少"的事实：
- 清仓 026449：与 017103 重叠5支(30.8%) / 与 020233 重叠4支 / 与 014871 重叠3支，9支冗余最高，规模最小(4.2%)。
- 减半 024418：被 011613 完全包含（ETF暴露视角），主题最窄，近1月 -6.09% 最弱。
- 减至20% 020233：与 014871 重叠4支(014871侧39.5%)，但留港股(腾讯+阿里)分散价值故不全清。
- 保留 011712：军工(火炬电子)独有敞口，其他6支均无。
