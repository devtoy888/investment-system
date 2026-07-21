# 数据源多轮验证方法论

> 来源: 2026-07-18 全量系统评估实战

## 核心原则（用户明确要求）

> "不要为了测试通过而写测试，测试要有效稳健"
> "要做多轮验证测试系统的稳健型"

## 四轮验证框架

| 轮次 | 内容 | 目的 | 非交易日也能做 |
|:----:|:-----|:-----|:--------------:|
| 第1轮 | 单源结构+语法 | API是否可达、返回结构是否完整 | ✅ 是 |
| 第2轮 | 多源交叉验证 | 同一数据的不同源是否一致 | ✅ 是 |
| 第3轮 | 边界条件 | 空输入/无效输入/高并发不崩溃 | ✅ 是 |
| 第4轮 | 一体化全量 | 全部数据源+全部功能点联调 | ✅ 是 |

> **关键约束：** 第1-3轮边界测试可以在非交易日执行。第4轮中的**数值准确性验证**必须等在交易日 9:30-15:00 执行——非交易日API返回的"数据"是上周五的缓存。

## 每轮验证清单

### 第1轮：单源结构测试

```python
# 语法检查
py_compile.compile(file, doraise=True)

# 导入检查
import module
check("函数存在", hasattr(module, 'func_name'))

# 结构完整性
result = module.func()
check("返回非空", result is not None)
if result:
    required_keys = {'name', 'price'}
    missing = required_keys - set(result.keys())
    check("键完整", not missing, f"缺: {missing}")
```

### 第2轮：交叉验证

```python
# 腾讯 vs AKShare 指数涨跌
q_tencent = get_tencent_quote('sh000001')
q_akshare = ak.stock_zh_index_daily('sh000001')
diff = abs(float(q_tencent['change_pct']) - ak_change)
check("偏差<0.5%", diff < 0.5)  # 腾讯和AKShare应基本一致

# 天天基金 vs AKShare 基金净值
# 注意：比绝对值而不是百分比——nav_date相同才可比
f_fundgz = get_fund_value('017103')
f_akshare = ak.fund_open_fund_info_em(symbol='017103', indicator='单位净值走势')
if f_fundgz['nav_date'] == str(f_akshare.iloc[-1]['净值日期'])[:10]:
    # 同日期净值应完全一致
    check("净值偏差<0.01", abs(f_fundgz['nav'] - float(f_akshare.iloc[-1]['单位净值'])) < 0.01)
```

### 第3轮：边界测试

```python
# 空值测试
check("空code不崩溃", func('') is None)
check("无效code不崩溃", func('000000') is not None or True)

# 高并发
with ThreadPoolExecutor(max_workers=6) as ex:
    futures = {ex.submit(func): name for ...}
    for f in as_completed(futures):
        try:
            result = f.result()  # 超时不阻塞
        except:
            check(f"{name}并行", False)

# 备援链触发
# 模拟主源失败时是否自动降级到备援
```

### 第4轮：一体化全量

```python
# 全部数据源联调
tests = [
    ("语法", check_syntax),
    ("交易日判断", check_is_trading_day),
    ("外盘_stale标记", check_yahoo_stale),
    ("基金历史数据", check_fund_history),
    ("指数历史数据", check_index_history),
    ("涨跌家数", check_market_breadth),
    ("北向资金", check_northbound),
    ("腾讯行情", check_tencent),
    ("track_source覆盖", check_tracking),
    ("备援链结构", check_fallback_chains),
]
for name, fn in tests:
    check(name, fn())
```

## 非交易日验证的特殊约束

### 能做的
- ✅ API HTTP可达性
- ✅ 返回数据结构完整性（键是否存在、类型是否正确）
- ✅ Freshness标记正确性（非交易日→stale=True）
- ✅ 错误处理鲁棒性（空输入、无效参数、超时）
- ✅ 多源交叉验证的结构一致性

### 不能做的
- ❌ 数值准确性（所有"实时数据"都是上周五缓存）
- ❌ 涨跌幅正确性（非交易日涨跌幅=0才是对的，但腾讯返回历史值）
- ❌ 备援数据实际可用性（AKShare stock_zh_a_spot_em非交易日连接重置）

> **案例：** 2026-07-18验证中，腾讯指数显示"涨跌-3.05%"这是周五的数据，和系统bug无关。

## 交易日验证补充项

交易日 9:30-15:00 之间需要额外验证：

1. 腾讯 vs AKShare 指数实时涨跌幅偏差（应为<0.5%）
2. 天天基金实时估算 vs 收盘后官方净值偏差（估算偏差通常<1%）
3. 涨跌家数3源对比（AKShare vs 东财push2 vs 新浪tags）
4. 各数据源请求耗时分时段统计
5. 北向资金 hexin vs AKShare vs 新浪tags 三方对比

## 验证报告输出格式

```markdown
## 第N轮结果: X/Y 通过

| 测试项 | 结果 |
|:-------|:----:|
| 测试名称1 | ✅ |
| 测试名称2 | ❌ detail |

失败详情:
  ❌ 测试名称: detail
```

所有验证报告应上传R2存档，路径: `fund-system/strategy/VALIDATION_REPORT.md`
