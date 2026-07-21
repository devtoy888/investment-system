---
title: Vibe-Trading 因子库与 Alpha 研究
created: 2026-07-12
updated: 2026-07-12
type: concept
tags: [finance, quant, data-source]
sources:
  - https://github.com/HKUDS/Vibe-Trading
  - https://vibetrading.wiki/alpha-library/
  - https://vibetrading.wiki/research-lab/
---

# Alpha 因子库（Alpha Zoo）

## 概览

Vibe-Trading 内置 **460 个预构建量化因子**，横跨 5 个因子家族。一行 CLI 命令即可在整个标的空间上评测。

| Zoo | 数量 | 来源 | 许可证 |
|-----|------|------|--------|
| **qlib158** | 154 | Microsoft Qlib | Apache-2.0 |
| **alpha101** | 101 | Kakushadze (2015) | 数学内容 |
| **gtja191** | 191 | 国泰君安 (2014) | 数学内容 |
| **academic** | 10 | 学术资产定价文献 | 学术引用 |
| **fundamental** (v0.1.11) | 4 | SEC 基本面因子 | MIT |

## CLI 使用

```bash
# 列出 zoo 中所有因子
vibe-trading alpha list --zoo gtja191

# 评测一个 zoo
vibe-trading alpha bench --zoo gtja191 --universe csi300 --period 2020-2025 --top 20

# 比较不同 zoo 的因子表现
vibe-trading alpha compare --zoos qlib158,gtja191 --universe csi300 --period 2018-2025

# 查看因子详情
vibe-trading alpha show --alpha KDJ_001
```

## 因子分类法

### qlib158（154 个）
Microsoft Qlib 的生产级因子套件，移植到 Vibe-Trading 的 panel API。

### alpha101（101 个）
Kakushadze (2015) 短周期公式化因子，覆盖多种市场微观结构信号。

### gtja191（191 个）
国泰君安 2014 年发布的 191 个 A 股微观结构与成交量因子。2026 年 5 月研究实验室发布的《Which of the 191 GTJA alphas still work in 2026?》对其在 CSI300 (2018-2025) 上进行了评测。

### fundamental（v0.1.11 新增）
PIT 安全的 SEC 基本面因子：
- `fund:*` 面板列
- 以提交日期锚定，带重述和 YTD 框架保护
- 4 个质量/价值因子

## 技术实现

### 19 个基础算子
```
rank, scale, ts_*, delta, decay_linear, safe_div, vwap 等
```

### 评测引擎 (`bench_runner.py`)
- **IC**（信息系数）评测
- **alive/reversed/dead** 三级分类
- 并行计算避免重复面板载荷
- `bottleneck`/NumPy 快速路径（v0.1.11 加速）

### Alpha 浏览器 API
| 端点 | 方法 | 说明 |
|------|------|------|
| `/alpha/list` | GET | 按 zoo/主题/标的空间筛选 |
| `/alpha/{alpha_id}` | GET | 元数据 + 源码 |
| `/alpha/bench` | POST | 启动评测任务 |
| `/alpha/bench/{job_id}/stream` | GET | SSE 进度流 |

### 在线浏览
所有因子可在线查看源码和公式：
- https://vibetrading.wiki/alpha-library/content/qlib158/index.html
- https://vibetrading.wiki/alpha-library/content/alpha101/index.html
- https://vibetrading.wiki/alpha-library/content/gtja191/index.html
- https://vibetrading.wiki/alpha-library/content/academic/index.html

## 研究实验室

https://vibetrading.wiki/research-lab/ 提供长文分析和可复现回测。每个结论都可以通过一条 CLI 命令复现。

**已发布研究**：2026-05-17 — *Which of the 191 GTJA alphas still work in 2026?*（CSI300, 2018-2025）

## 相关页面
- [[concepts/vibe-trading/项目总览]]
- [[concepts/vibe-trading/数据源与回测]]
- [[concepts/vibe-trading/技术架构]]
- [[concepts/vibe-trading/安装与使用]]
