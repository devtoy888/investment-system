# 行业ETF代码（腾讯行情 · 已验证 2026-06-30）

每个代码均通过 `https://qt.gtimg.cn/q={code}` 实际验证返回的ETF名称。
**注意：** `sz159766` 是旅游ETF（非光伏），`sz159857` 才是光伏ETF。

| 板块 | 代码 | 场内简称（已验证） |
|------|------|-------------------|
| 半导体 | `sz159813` | 半导体ETF鹏华 |
| 新能源 | `sz159752` | 新能源ETF申万菱信 |
| 光伏 | `sz159857` | 光伏ETF天弘 |
| 军工 | `sh512660` | 军工ETF国泰 |
| 医药 | `sh512170` | 医疗ETF华宝 |
| 消费 | `sh510150` | 消费ETF招商 |
| 券商 | `sh512880` | 证券ETF国泰 |
| 恒生科技ETF | `sz159740` | 恒生科技ETF大成 |
| 通信 | `sh515050` | 通信ETF华夏 |
| 有色金属 | `sh512400` | 有色金属ETF南方 |

## 备用/补充

| 板块 | 代码 | 场内简称 |
|------|------|---------|
| 煤炭 | `sh515220` | 煤炭ETF国泰 |
| 红利 | `sh510880` | 红利ETF华泰柏瑞 |
| 房地产 | `sh512200` | 房地产ETF南方 |
| 上证50 | `sh510050` | 上证50ETF |
| 科创50ETF | `sh588000` | 科创50ETF |
| 黄金ETF(沪) | `sh518880` | 黄金ETF |
| 黄金ETF(深) | `sz159934` | 黄金ETF基金 |

## 批量查询用法

```python
import requests

codes = [
    'sz159813', 'sz159752', 'sz159857', 'sh512660',
    'sh512170', 'sh510150', 'sh512880', 'sz159740',
    'sh515050', 'sh512400',
]

url = f"https://qt.gtimg.cn/q={','.join(codes)}"
r = requests.get(url, timeout=8)
lines = r.text.strip().rstrip(';').split(';')

results = {}
for line in lines:
    if '=\"' not in line:
        continue
    parts = line.split('=\"')[1].rstrip('\"').split('~')
    if len(parts) < 32:
        continue
    code_num = parts[2]  # 纯数字，不带sh/sz！
    change = float(parts[32])
    results[code_num] = {
        'name': parts[1],
        'price': parts[3],
        'change_pct': change,
    }

# 用 .endswith() 做匹配
SECTOR_MAP = {
    'sz159813': '半导体', 'sz159752': '新能源', 'sz159857': '光伏',
    'sh512660': '军工',  'sh512170': '医药',   'sh510150': '消费',
    'sh512880': '券商',  'sz159740': '恒生科技', 'sh515050': '通信',
    'sh512400': '有色金属',
}

for full_code, sector in SECTOR_MAP.items():
    # Tencent返回纯数字，去掉sh/sz前缀匹配
    for returned_code, data in results.items():
        if full_code.endswith(returned_code):
            print(f"{sector}: {data['change_pct']:+.2f}%")
```

## 常见陷阱

1. **代码去前缀**：腾讯批量查询返回的`parts[2]`是纯数字（如`159813`），需要用 `.endswith()` 匹配 `SECTOR_ETFS` 中的完整代码（如`sz159813`）。直接 `==` 比较会全失败。
2. **ETF更名/退市风险**：以上代码验证于2026-06-30，使用前建议用单个查询确认名称匹配。
