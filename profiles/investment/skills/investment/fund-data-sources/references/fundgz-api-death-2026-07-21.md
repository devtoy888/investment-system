# fundgz API 失效 & get_fund_value() 静默失败修复记录

## 日期
2026-07-21

## 现象
所有基金估算涨跌为0.0%，但 `get_fund_value()` 不报错。

## 根因

### 1. fundgz API 已死
`https://fundgz.1234567.com.cn/js/{code}.js` 返回 HTTP 301 → 
`https://fund.eastmoney.com/notfound.html` (404)。
响应内容为HTML而非JSONP，但HTTP状态码是200。
`requests.get()` 默认follow redirects，最终得到200+HTML。

### 2. get_fund_value() 备援缺陷
原代码结构：
```python
try:
    r = requests.get(fundgz_url)
    if 'jsonpgz(' in txt:
        # 解析并返回
except Exception as e:
    if _retry: time.sleep(0.5); return get_fund_value(code, _retry=False)
    # 备援AKShare仅在这里
    try: ak_data = get_fund_realtime(code)
    except: pass
    print(f"⚠️ get_fund({code}: {e}")
return None  # ← fundgz返回404HTML时，从这离开！
```

fundgz返回200但HTML不含`jsonpgz(` → `if`不进入 → 不抛异常 → 不走`except` → 直接`return None`。
AKShare备援从未被调用。

### 3. AKShare线程冲突
`fund_source_akshare.get_fund_realtime()` 使用 `signal.SIGALRM` (10秒超时)。
从子线程调用时抛 `ValueError: signal only works in main thread of the main interpreter`。
降级到 `fund_open_fund_info_em()` (历史净值) → 每个基金~30秒。

## 修复

### get_fund_value() 备援逻辑
将AKShare备援从except块内移到函数末尾无条件执行：

```python
# /opt/data/scripts/fund_tools.py 中修改
try:
    url = f"https://fundgz.1234567.com.cn/js/{fund_code}.js"
    r = requests.get(url, timeout=8, headers={'Referer': 'https://fund.eastmoney.com/'})
    txt = r.text.strip()
    if 'jsonpgz(' in txt:
        # ... 正常解析返回
except Exception as e:
    if _retry:
        time.sleep(0.5)
        return get_fund_value(fund_code, _retry=False)
# ★★★ 新：fundgz未返回JSONP，直接走AKShare备援 ★★★
try:
    from fund_source_akshare import get_fund_realtime
    ak_data = get_fund_realtime(fund_code)
    if ak_data:
        return {
            'code': fund_code,
            'name': ak_data.get('name', ''),
            'nav': ak_data.get('nav', 0),
            'estimated_change': ak_data.get('estimated_change', 0),
            'nav_date': ak_data.get('nav_date', date.today().isoformat()),
            'change_source': ak_data.get('source', 'akshare'),
        }
except Exception:
    pass
return None
```

### AKShare线程冲突应对
不要对 `get_fund_value()` 做顺序调用（单只30秒×14只=7分钟）。
改用 `fund_tools.get_all_funds()`（内部5线程并行，~90秒完成14只）：

```python
from fund_tools import get_all_funds
fund_values = get_all_funds()  # 5线程并行
for code, info in merged.items():
    fv = fund_values.get(code, {})
    ec = float(fv.get('estimated_change', 0)) if fv else 0.0
    ...
```

## 影响范围
所有依赖 `get_fund_value()` 的脚本：
- `execute_today_plan.py` (14:30决策) ← 最严重，全0%
- `collect_noon_data.py` / `collect_morning_data.py` ← 自动受益
- `portfolio_snapshot.py` ← 自动受益

## 预防措施
在输出操作建议前应校验数据完整性：

```python
def validate_portfolio(portfolio):
    zero_count = sum(1 for v in portfolio.values() if abs(v['est_change']) < 0.01 and v['cost'] > 0)
    if zero_count >= len(portfolio):
        return ["[严重] 全部基金估算涨跌为0%"]
    return []
```
