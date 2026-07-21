#!/usr/bin/env python3
"""
基金因子算子库 — 适用于日频净值序列的因子计算工具

依赖: numpy, pandas (通过 /opt/data/akshare-deps 加载)
如依赖不可用，导入时 HAS_FACTORS=False，所有函数返回 None

使用场景:
  - 净值动量/反转信号
  - 波动率/风险度量  
  - 板块轮动相关性
  - KOL信号有效性验证
"""
from __future__ import annotations
import sys, os
from typing import Any

# ── 从 akshare-deps 加载 numpy/pandas ──
_DEPS = "/opt/data/akshare-deps"
if os.path.isdir(_DEPS) and _DEPS not in sys.path:
    sys.path.insert(0, _DEPS)

try:
    import numpy as np
    import pandas as pd
    HAS_FACTORS = True
except ImportError:
    HAS_FACTORS = False
    np = None
    pd = None

def _check() -> bool:
    if not HAS_FACTORS:
        print("  ⚠️ fund_factors: numpy/pandas 未安装, 跳过因子计算")
    return HAS_FACTORS

# ══════════════════════════════════════════
# 截面算子（Cross-Sectional）
# ══════════════════════════════════════════

def rank(s: pd.Series) -> pd.Series:
    """横截面百分位排名 [0, 100]"""
    return s.rank(pct=True) * 100

def zscore(s: pd.Series) -> pd.Series:
    """横截面Z分数 (x - mean) / std"""
    if not _check(): return None
    std = s.std()
    if std == 0 or pd.isna(std):
        return pd.Series(0.0, index=s.index)
    return (s - s.mean()) / std

def scale(s: pd.Series, target: float = 1.0) -> pd.Series:
    """L1归一化: sum(|x|) = target"""
    if not _check(): return None
    abssum = s.abs().sum()
    if abssum == 0 or pd.isna(abssum):
        return pd.Series(0.0, index=s.index)
    return s / abssum * target

# ══════════════════════════════════════════
# 时间序列算子
# ══════════════════════════════════════════

def ts_mean(s: pd.Series, window: int) -> pd.Series:
    """滚动窗口均值"""
    if not _check(): return None
    return s.rolling(window=window, min_periods=max(2, window // 2)).mean()

def ts_std(s: pd.Series, window: int) -> pd.Series:
    """滚动窗口标准差"""
    if not _check(): return None
    return s.rolling(window=window, min_periods=max(2, window // 2)).std()

def ts_max(s: pd.Series, window: int) -> pd.Series:
    """滚动窗口最大值"""
    if not _check(): return None
    return s.rolling(window=window, min_periods=window).max()

def ts_min(s: pd.Series, window: int) -> pd.Series:
    """滚动窗口最小值"""
    if not _check(): return None
    return s.rolling(window=window, min_periods=window).min()

def ts_corr(a: pd.Series, b: pd.Series, window: int) -> pd.Series:
    """滚动窗口相关性"""
    if not _check(): return None
    return a.rolling(window=window, min_periods=max(5, window // 2)).corr(b)

def delta(s: pd.Series, d: int = 1) -> pd.Series:
    """滞后差分: X(t) - X(t-d)。d>=1 防窥视"""
    if not _check(): return None
    assert d >= 1, "delta: d must be >= 1"
    return s.diff(periods=d)

def decay_linear(s: pd.Series, window: int) -> pd.Series:
    """线性衰减加权平均: 近者权重高"""
    if not _check(): return None
    w = np.arange(1, window + 1, dtype=float)
    w /= w.sum()
    return s.rolling(window=window, min_periods=window).apply(
        lambda x: np.dot(x, w) if len(x) == window else np.nan, raw=True
    )

def signed_power(s: pd.Series, power: float) -> pd.Series:
    """带符号幂变换: sign(x) * |x|^power"""
    if not _check(): return None
    return np.sign(s) * np.abs(s) ** power

# ══════════════════════════════════════════
# 基金专用组合算子
# ══════════════════════════════════════════

def returns(nav: pd.Series) -> pd.Series:
    """日收益率: nav(t) / nav(t-1) - 1"""
    if not _check(): return None
    return nav.pct_change()

def momentum(nav: pd.Series, short: int = 20, long: int = 60) -> pd.Series:
    """净值动量比: 短期均值 / 长期均值 - 1"""
    if not _check(): return None
    return ts_mean(nav, short) / ts_mean(nav, long) - 1.0

def volatility(returns_s: pd.Series, window: int = 20) -> pd.Series:
    """年化波动率: 日收益率标准差 × sqrt(252)"""
    if not _check(): return None
    return ts_std(returns_s, window) * np.sqrt(252)

def drawdown(nav: pd.Series) -> pd.Series:
    """回撤: 当前净值 / 历史最高净值 - 1"""
    if not _check(): return None
    return nav / nav.expanding().max() - 1.0

def sharpe_ratio(returns_s: pd.Series, window: int = 60) -> pd.Series:
    """滚动夏普比率"""
    if not _check(): return None
    mr = returns_s.rolling(window=window, min_periods=max(10, window // 2)).mean()
    sr = returns_s.rolling(window=window, min_periods=max(10, window // 2)).std()
    return mr / sr.where(sr > 1e-10, np.nan) * np.sqrt(252)

# ══════════════════════════════════════════
# 信号生成辅助
# ══════════════════════════════════════════

def cross_over(a: pd.Series, b: pd.Series) -> pd.Series:
    """金叉: a上穿b"""
    if not _check(): return None
    return (a > b) & (a.shift(1) <= b.shift(1))

def cross_under(a: pd.Series, b: pd.Series) -> pd.Series:
    """死叉: a下穿b"""
    if not _check(): return None
    return (a < b) & (a.shift(1) >= b.shift(1))

def quantile_signal(s: pd.Series, high: float = 0.8, low: float = 0.2) -> pd.Series:
    """分位数信号: 1(超买) / -1(超卖) / 0(中性)"""
    if not _check(): return None
    r = s.rank(pct=True)
    sig = pd.Series(0, index=s.index, dtype=int)
    sig[r > high] = 1
    sig[r < low] = -1
    return sig

# ══════════════════════════════════════════
# 因子验证（IC/IR）
# ══════════════════════════════════════════

def ic(factor: pd.Series, forward_return: pd.Series) -> float:
    """信息系数: 因子与未来收益的Spearman相关"""
    if not _check(): return 0.0
    from scipy.stats import spearmanr
    v = pd.concat([factor, forward_return], axis=1).dropna()
    if len(v) < 10:
        return 0.0
    rho, _ = spearmanr(v.iloc[:, 0], v.iloc[:, 1])
    return rho if not np.isnan(rho) else 0.0

def ir(ic_series_s: pd.Series) -> float:
    """信息比率: mean(IC) / std(IC)"""
    if not _check(): return 0.0
    std = ic_series_s.std()
    return ic_series_s.mean() / std if std > 1e-10 else 0.0
