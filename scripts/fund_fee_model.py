#!/usr/bin/env python3
"""
基金交易费用模型

费率来源: 各基金招募说明书/天天基金公示
C类: 申购0%, 赎回0%(≥7天), 管理费+托管费已含在净值中
LOF(163302): 申购0.15%(折扣后), 赎回0.5%(≥7天), 管理费+托管费已含

使用场景:
  - 持仓盈亏中显示"净盈亏(扣费后)"
  - 预警: 持有<7天赎回会扣1.5%(C类) / 0.5%(LOF)
  - 决策日志中记录真实PnL
"""
from __future__ import annotations
from typing import Optional
from datetime import date, timedelta

# ── 基金费率表 ──
FEE_TABLE = {
    # C类: 申购0%, 赎回0%(≥7天), 管理费+托管费已含在净值日变动中
    "009478": {"type": "C",  "buy_pct": 0.0,  "sell_pct_lt7d": 1.5,  "sell_pct_ge7d": 0.0, "name": "中银上海金ETF联接C"},
    "011613": {"type": "C",  "buy_pct": 0.0,  "sell_pct_lt7d": 1.5,  "sell_pct_ge7d": 0.0, "name": "华夏科创50ETF联接C"},
    "024418": {"type": "C",  "buy_pct": 0.0,  "sell_pct_lt7d": 1.5,  "sell_pct_ge7d": 0.0, "name": "华夏上证科创板半导体ETF联接C"},
    "026449": {"type": "C",  "buy_pct": 0.0,  "sell_pct_lt7d": 1.5,  "sell_pct_ge7d": 0.0, "name": "大摩沪港深科技混合C"},
    "014871": {"type": "C",  "buy_pct": 0.0,  "sell_pct_lt7d": 1.5,  "sell_pct_ge7d": 0.0, "name": "大摩科技领先混合C"},
    "020233": {"type": "C",  "buy_pct": 0.0,  "sell_pct_lt7d": 1.5,  "sell_pct_ge7d": 0.0, "name": "大摩景气智选混合C"},
    "017103": {"type": "C",  "buy_pct": 0.0,  "sell_pct_lt7d": 1.5,  "sell_pct_ge7d": 0.0, "name": "大摩数字经济混合C"},
    "011712": {"type": "C",  "buy_pct": 0.0,  "sell_pct_lt7d": 1.5,  "sell_pct_ge7d": 0.0, "name": "大摩万众创新混合C"},
    "025857": {"type": "C",  "buy_pct": 0.0,  "sell_pct_lt7d": 1.5,  "sell_pct_ge7d": 0.0, "name": "华夏中证电网设备ETF联接C"},
    "012329": {"type": "C",  "buy_pct": 0.0,  "sell_pct_lt7d": 1.5,  "sell_pct_ge7d": 0.0, "name": "天弘中证新能源指数增强C"},
    "011103": {"type": "C",  "buy_pct": 0.0,  "sell_pct_lt7d": 1.5,  "sell_pct_ge7d": 0.0, "name": "天弘中证光伏C"},
    # LOF: 有申购费, 赎回0.5%
    "163302": {"type": "LOF", "buy_pct": 0.15, "sell_pct_lt7d": 1.5, "sell_pct_ge7d": 0.5, "name": "大摩资源优选混合(LOF)"},
}

def fee_info(code: str) -> Optional[dict]:
    """获取基金费率信息"""
    return FEE_TABLE.get(code)

def get_sell_fee_pct(code: str, held_days: int) -> float:
    """获取赎回费率(%)。held_days=持有天数"""
    info = FEE_TABLE.get(code)
    if not info:
        return 0.0
    if held_days < 7:
        return info["sell_pct_lt7d"]
    return info["sell_pct_ge7d"]

def get_buy_fee_pct(code: str) -> float:
    """获取申购费率(%)"""
    info = FEE_TABLE.get(code)
    return info["buy_pct"] if info else 0.0

def calc_net_pnl(
    code: str, shares: float, buy_nav: float, current_nav: float, held_days: int
) -> dict:
    """计算含费用的真实盈亏

    Args:
        code: 基金代码
        shares: 持有份额
        buy_nav: 买入净值
        current_nav: 当前净值
        held_days: 持有天数

    Returns:
        gross_pnl: 毛盈亏(元)
        gross_pnl_pct: 毛盈亏(%)
        fee_pct: 赎回费率(%)
        fee_amount: 赎回费(元)
        net_pnl: 净盈亏(元)
        net_pnl_pct: 净盈亏(%)
        has_short_term_risk: 是否持有不足7天
    """
    info = FEE_TABLE.get(code)
    if not info or shares <= 0 or buy_nav <= 0:
        return {
            "gross_pnl": 0.0, "gross_pnl_pct": 0.0,
            "fee_pct": 0.0, "fee_amount": 0.0,
            "net_pnl": 0.0, "net_pnl_pct": 0.0,
            "has_short_term_risk": False,
        }

    # 当前市值 = 份额 × 当前净值
    market_value = shares * current_nav
    cost_value = shares * buy_nav
    gross_pnl = market_value - cost_value
    gross_pnl_pct = (current_nav / buy_nav - 1.0) * 100 if buy_nav > 0 else 0.0

    # 赎回费
    sell_fee_pct = get_sell_fee_pct(code, held_days)
    fee_amount = market_value * sell_fee_pct / 100.0
    net_pnl = gross_pnl - fee_amount
    net_pnl_pct = gross_pnl_pct - sell_fee_pct  # 近似

    return {
        "gross_pnl": round(gross_pnl, 2),
        "gross_pnl_pct": round(gross_pnl_pct, 2),
        "fee_pct": sell_fee_pct,
        "fee_amount": round(fee_amount, 2),
        "net_pnl": round(net_pnl, 2),
        "net_pnl_pct": round(net_pnl_pct, 2),
        "has_short_term_risk": held_days < 7,
    }

def check_short_term_risk(trade_records: list[dict]) -> list[dict]:
    """检查所有持仓是否有短期赎回费风险

    Args:
        trade_records: [{code, buy_date, shares, buy_nav}, ...]

    Returns:
        [{code, name, held_days, fee_pct, suggestion}, ...]
    """
    today = date.today()
    alerts = []
    for r in trade_records:
        code = r.get("code", "")
        info = FEE_TABLE.get(code)
        if not info:
            continue
        buy_date = r.get("buy_date")
        if isinstance(buy_date, str):
            buy_date = date.fromisoformat(buy_date)
        held_days = (today - buy_date).days
        fee_pct = get_sell_fee_pct(code, held_days)
        if fee_pct > 0:
            alerts.append({
                "code": code,
                "name": info["name"],
                "held_days": held_days,
                "fee_pct": fee_pct,
                "suggestion": f"持有{held_days}天, 赎回扣{fee_pct}%手续费, "
                    f"建议{'再等{0}天' if held_days < 7 else '直接赎回'}".format(7 - held_days if held_days < 7 else 0)
                    if held_days < 7 else f"持有{held_days}天, 赎回扣{fee_pct}%手续费",
            })
    return alerts
