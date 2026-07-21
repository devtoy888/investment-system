# Signal Engine YAML 规则格式

> `signal_rules.yaml` 定义信号规则，`signal_engine.py` 读取并批量评估。
> 新增规则只需改 yaml，不碰代码。

## 结构

```yaml
rules:
  - id: "rule-id"                    # 唯一ID
    name: "规则名称"                  # 人类可读
    fund_code: "017103"              # 基金代码
    benchmark_code: "sz159813"       # 可选: 关联ET科技参考
    description: "触发条件说明"
    conditions:
      - type: "estimated_change"     # 条件类型
        operator: ">"                # > / >= / < / <= / ==
        value: 0.5                   # 阈值
      - type: "benchmark_change"     # 第二个条件(AND)
        operator: "<"
        value: 1.0
    message: "📊 基金名: 净值{nav}→{enav} ({ec:+.2f}%)\n✅ 触发消息正文"
```

## 条件类型

| type | 含义 | 数据来源 |
|:-----|:-----|:---------|
| `estimated_change` | 基金估算涨跌幅(%) | `get_fund_value()` |
| `benchmark_price` | 关联ETF价格 | `get_tencent_quote()` |
| `benchmark_change` | 关联ETF涨跌幅(%) | 同上 |
| `benchmark_amplitude` | 关联ETF振幅(%) | 同上的high/low/prev_close |

## 消息模板变量

| 变量 | 含义 |
|:-----|:-----|
| `{nav}` | 基金最新净值 |
| `{enav}` | 基金估算净值 |
| `{ec}` | 估算涨跌幅 |
| `{bk_price}` | 基准ET科技价格 |
| `{bk_pct}` | 基准涨跌幅 |
| `{bk_amp}` | 基准振幅 |

## 关键点

- 多条conditions之间是 **AND** 关系（全部满足才触发）
- 同一基金可以有多个id（不同条件组合），按顺序评估
- 评估器自动跳过无数据基金（get_fund_value返回None时跳过该规则）
- message中用 `\n` 换行
- 需要Hermes venv的python执行（含yaml模块）
