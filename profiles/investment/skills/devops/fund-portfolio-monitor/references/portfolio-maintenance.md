# Portfolio Maintenance Reference

## Current Holdings (as of 2026-07-07)

| Code | Fund | Shares | Cost | Value | Group |
|:----|:----|:-----:|:----:|:-----:|:-----:|
| 009478 | 中银上海金ETF联接C | 214.27 | 2.0162 | ~432 | 黄金 |
| 011613 | 华夏科创50ETF联接C | 400 | ~1.50 | ~620 | 科技/AI |
| 024418 | 华夏科创板半导体材料设备ETF联接C | 300 | ~2.80 | ~834 | 科技/AI |
| 026449 | 大摩沪港深科技混合C | 250 | ~1.46 | ~365 | 科技/AI |
| 014871 | 大摩科技领先混合C | 300 | ~3.57 | ~1071 | 科技/AI |
| 020233 | 大摩景气智选混合C | 250 | ~1.68 | ~420 | 科技/AI |
| **017103** | **大摩数字经济混合C** | **121.66** | **4.3921** | **~538** | **科技/AI** |
| 011712 | 大摩万众创新混合C | 200 | ~1.63 | ~326 | 科技/AI |
| 163302 | 大摩资源优选混合(LOF) | 300 | ~1.15 | ~345 | 资源/周期 |
| 025857 | 华夏中证电网设备ETF联接C | 200 | ~1.34 | ~268 | 资源/周期 |
| **012329** | **天弘中证新能源指数增强C** | **296.42** | **0.7925** | **~235** | **新能源** |
| **011103** | **天弘中证光伏C** | **189.73** | **0.8994** | **~171** | **新能源** |
| 001551 | 天弘中证医药100C | 323 | ~0.74 | ~239 | 医药 |
| 014565 | 天弘中证创新药产业ETF联接C | 100 | ~1.20 | ~120 | 医药 |

**Total Est. Value:** ~5,967 元

**Bold** = shares confirmed by user. Others are estimates — user needs to provide exact counts.

## Transaction Log

### 2026-07-06 (After Close)
**Action:** 减持 (3 funds, settle at 7/7 closing NAV)

| Fund | Before | Reduction | Remaining | % Reduced |
|:----|:------:|:---------:|:---------:|:---------:|
| 017103 大摩数字经济C | 162.22份 @4.3921 | 40.56份 | **121.66份** | 25% |
| 012329 天弘新能源C | 592.85份 @0.7925 | 296.43份 | **296.42份** | 50% |
| 011103 天弘光伏C | 379.47份 @0.8994 | 189.74份 | **189.73份** | 50% |

## Update Commands (copy-paste for next trade)

```python
from fund_tools import load_user_portfolio, save_user_portfolio

# Read current
p = load_user_portfolio()

# Update shares after trade
# e.g. p['017103']['shares'] = 121.66

# Save
save_user_portfolio(p)
```
