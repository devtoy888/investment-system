#!/usr/bin/env python3
"""
AKShare 数据源适配器 — 作为天天基金/东财的免费备援
无需注册token，pip install akshare 即用

如果 akshare 未安装，所有函数返回 None，不影响主流程。

AKShare 安装方式（二选一）:
  pip install akshare                                   # 装到Hermes venv（更新会丢）
  pip install --target /opt/data/akshare-deps akshare   # 装到持久化目录（推荐）
"""
from __future__ import annotations
import sys, os, json
from datetime import date, timedelta
from typing import Any

# ── AKShare 查找路径（支持独立目录安装）──
_AKSHARE_DEPS = "/opt/data/akshare-deps"
if os.path.isdir(_AKSHARE_DEPS) and _AKSHARE_DEPS not in sys.path:
    sys.path.insert(0, _AKSHARE_DEPS)

# 关掉 akshare 内部的进度条（非交互环境不需要）
os.environ["AKSHARE_RAISE_ERR"] = "False"
os.environ["TQDM_DISABLE"] = "1"

try:
    import akshare as ak
    HAS_AKSHARE = True
except ImportError:
    HAS_AKSHARE = False

AKSHARE_HINT = "pip install akshare 后可启用此数据源"

def _ak_available() -> bool:
    if not HAS_AKSHARE:
        print(f"  ⚠️ AKShare未安装, {AKSHARE_HINT}")
    return HAS_AKSHARE

# ── 基金实时估值（替代天天基金）──
def get_fund_realtime(code: str) -> dict | None:
    """
    获取单只基金实时估值
    优先: fund_value_estimation_em(全量但慢) → 备援: fund_open_fund_info_em(历史净值)
    
    2026-07-18 修复: 去掉了硬编码日期(2026-07-15)，改为动态匹配列名
    """
    if not _ak_available():
        return None
    
    today_str = date.today().isoformat()
    
    # 方案A: 实时估值（可能慢，设10秒超时）
    try:
        import signal
        class TimeoutError(Exception): pass
        def _handler(signum, frame): raise TimeoutError()
        signal.signal(signal.SIGALRM, _handler)
        signal.alarm(10)
        
        df = ak.fund_value_estimation_em()
        signal.alarm(0)
        if df is not None and not df.empty:
            row = df[df["基金代码"] == code]
            if not row.empty:
                r = row.iloc[0]
                # 动态匹配列名（避免硬编码日期）:
                # AKShare列名格式: "2026-07-17-估算数据-估算增长率"
                est_col = [c for c in df.columns if "估算增长率" in c]
                est_val_col = [c for c in df.columns if "估算值" in c and "202" in c]
                nav_col_dyn = [c for c in df.columns if "单位净值" in c and today_str[:7] in c]
                if not nav_col_dyn:
                    nav_col_dyn = [c for c in df.columns if "单位净值" in c]
                
                est_change_str = r.get(est_col[0], "0") if est_col else "0"
                try:
                    est_change = float(str(est_change_str).replace("%", ""))
                except (ValueError, TypeError):
                    est_change = 0.0
                
                result = {
                    "code": code,
                    "name": r.get("基金名称", ""),
                    "nav": float(r.get(nav_col_dyn[0], 0) or 0) if nav_col_dyn else 0,
                    "estimated_nav": float(r.get(est_val_col[0], 0) or 0) if est_val_col else 0,
                    "estimated_change": est_change,
                    "source": "akshare_est",
                }
                return result
    except Exception as e:
        print(f"  ⚠️ AKShare实时估值[{code}]: {type(e).__name__}: {e}", file=__import__('sys').stderr)
        pass

    # 方案B: 历史净值（快，但只给昨日数据）
    try:
        df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) >= 2 else None
            change = 0.0
            if prev is not None:
                try:
                    change = round(float(latest.get("日增长率", 0) or 0), 2)
                except (ValueError, TypeError):
                    change = 0.0
            return {
                "code": code,
                "name": "",
                "nav": float(latest.get("单位净值", 0) or 0),
                "estimated_nav": None,
                "estimated_change": change,
                "nav_date": str(latest.get("净值日期", "")),
                "source": "akshare_hist",
            }
    except Exception as e:
        print(f"  ⚠️ AKShare基金历史[{code}]: {e}")
    
    return None


def get_funds_batch_realtime(codes: list[str]) -> dict[str, dict]:
    """批量获取基金实时估值（注意：此函数只返回场内ETF，场外基金请逐个调get_fund_realtime）"""
    if not _ak_available():
        return {}
    try:
        df = ak.fund_etf_spot_em()
        if df is None or df.empty:
            return {}
        result = {}
        for code in codes:
            row = df[df['代码'] == code]
            if not row.empty:
                r = row.iloc[0]
                result[code] = {
                    "code": code,
                    "name": r.get("名称", ""),
                    "nav": float(r.get("单位净值", 0) or 0),
                    "estimated_nav": float(r.get("估算净值", 0) or 0),
                    "estimated_change": float(r.get("估算涨跌幅", "0").replace("%", "") or 0),
                }
        return result
    except Exception as e:
        print(f"  ⚠️ AKShare批量估值: {e}")
        return {}

# ── 北向资金（替代hexin/新浪tags）──
def get_northbound_flow() -> dict | None:
    """获取北向资金实时数据（使用stock_hsgt_fund_flow_summary_em）"""
    if not _ak_available():
        return None
    try:
        df = ak.stock_hsgt_fund_flow_summary_em()
        if df is None or df.empty:
            return None
        # 筛选北向资金（沪股通+深股通）
        north_df = df[(df['资金方向'] == '北向')]
        if north_df.empty:
            return None
        total = 0.0
        hgt = 0.0
        sgt = 0.0
        for _, row in north_df.iterrows():
            net = float(row.get('成交净买额', 0) or 0)
            total += net
            if '沪' in str(row.get('板块', '')):
                hgt += net
            elif '深' in str(row.get('板块', '')):
                sgt += net
        latest_date = str(north_df.iloc[0].get('交易日', ''))
        return {
            "total": round(total, 2),
            "hgt": round(hgt, 2),
            "sgt": round(sgt, 2),
            "date": latest_date,
            "source": "akshare",
        }
    except Exception as e:
        print(f"  ⚠️ AKShare北向: {e}")
        return None

# ── 板块资金流向（新增能力）──
def get_sector_flow_rank() -> list[dict] | None:
    """获取行业板块资金流向排名"""
    if not _ak_available():
        return None
    try:
        df = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="行业资金流向")
        if df is None or df.empty:
            return None
        result = []
        for _, row in df.iterrows():
            result.append({
                "name": row.get("名称", ""),
                "change_pct": float(row.get("涨跌幅", "0").replace("%", "") or 0),
                "main_flow": float(row.get("主力净流入-净额", 0) or 0),
                "rank": int(row.get("序号", 0) or 0),
            })
        return result
    except Exception as e:
        print(f"  ⚠️ AKShare板块资金流向: {e}")
        return None

# ── 基金历史净值（用于决策验证/因子分析）──
def get_fund_history(code: str, days: int = 60) -> list[dict] | None:
    """获取基金历史净值序列"""
    if not _ak_available():
        return None
    try:
        df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
        if df is None or df.empty:
            return None
        df = df.tail(days)
        result = []
        for _, row in df.iterrows():
            result.append({
                "date": str(row.get("净值日期", "")),
                "nav": float(row.get("单位净值", 0) or 0),
                "acc_nav": float(row.get("累计净值", 0) or 0),
            })
        return result
    except Exception as e:
        print(f"  ⚠️ AKShare历史净值[{code}]: {e}")
        return None

# ── A股全市场涨跌家数（替代东财push2）──
def get_market_breadth_akshare() -> dict | None:
    """
    通过AKShare获取A股涨跌家数
    返回: {'rise_count': int, 'fall_count': int, 'source': 'akshare'}
    失败返回 None
    """
    if not _ak_available():
        return None
    try:
        df = ak.stock_zh_a_spot_em()
        if df is None or df.empty:
            return None
        rise = len(df[df['涨跌幅'] > 0])
        fall = len(df[df['涨跌幅'] < 0])
        flat = len(df) - rise - fall
        if rise + fall < 100:  # 数据异常过滤
            return None
        return {
            "rise_count": int(rise),
            "fall_count": int(fall),
            "flat_count": int(flat),
            "source": "akshare",
        }
    except Exception as e:
        print(f"  ⚠️ AKShare涨跌家数: {e}")
        return None
