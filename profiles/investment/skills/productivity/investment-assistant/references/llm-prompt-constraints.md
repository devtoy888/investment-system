# LLM Prompt 约束 — 持仓限定规则

> 来源: 2026-07-21 盘中报告修正。AI推荐的基金不在用户持仓中（推荐了博时黄金、广发高端制造等未持仓基金），因为prompt只说"值得关注3支"没说"从持仓中选"。

## 根本原因

prompt中关于操作建议的指令过于模糊：

```
× 错误写法：
5.【午后操作方向】a)值得关注3支:逐支给名称/代码/判断理由/操作方向/仓位建议 b)需警惕3支

→ AI会自由发挥，推荐非持仓基金、编造代码
```

## 修正方案

### 1. 把实际持仓动态注入prompt

```python
from fund_tools import FUND_CODES
from llm_analysis_v2 import BUILDING_FUNDS

portfolio_list_lines = []
for code, name in FUND_CODES.items():
    flag = "🏗️建仓期" if code in BUILDING_FUNDS else ""
    portfolio_list_lines.append(f"  {code} {name} {flag}")
portfolio_list = "\n".join(portfolio_list_lines)
```

### 2. 在prompt中加入持仓约束段

```
## 【持仓约束 — 必须遵守】
以下是你的全部持仓(N支)，**所有操作建议必须基于以下持仓**：
{portfolio_list}

> ⚠️ **严禁推荐非持仓基金！** 不得推荐上述列表之外的任何基金。
> ⚠️ 推荐基金时**必须使用正确的基金代码**，不得编造或写错代码。
> ⚠️ 建仓期基金仅允许"持有"或"加仓"，在任何情况下都不能建议卖出。
```

### 3. 操作建议指令明确限定范围

```
√ 正确写法：
5.【午后操作方向】a)从已有持仓中选3支最值得关注的...
```

## 适用场景

- 所有调用LLM做基金推荐的场景（早报/午报/收盘/决策）
- prompt中涉及基金代码、基金名称的地方，必须用变量注入而非硬编码
- `FUND_CODES` 和 `BUILDING_FUNDS` 是单点维护源，修改持仓后自动反映
