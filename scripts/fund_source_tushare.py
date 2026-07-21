# Tushare基金持仓接入 — 待完成

## 安装
```bash
pip install tushare
```

## 注册 token
1. 去 https://tushare.pro 注册（免费用户即可）
2. 获取 token（用户中心 → 接口TOKEN）
3. 填写 token 到环境变量 `.env`:
```
TUSHARE_TOKEN=你的token
```

## 能拿到的数据

| 数据 | API | 频率 | 说明 |
|:-----|:----|:----:|:-----|
| 基金持仓TOP10 | `fund_portfolio` | 季报 | 每支基金的前10大持仓，行业分布 |
| 基金净值 | `fund_nav` | 日频 | 每日实际净值（解决估算不准问题） |
| 基金经理 | `fund_manager` | - | 基金经理信息，从业年限 |
| 指数估值 | `index_dailybasic` | 日频 | PE/PB分位数，判断"越跌越贵" |

## 后续分析（拿到数据后）

- **重叠分析**: 7支科技基金的实际持仓重叠度
- **越跌越贵判断**: 科创50 PE分位数 vs 价格走势
- **减仓优先级**: 重叠度最高+估值最贵的优先减
