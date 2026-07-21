"""Trade Journal Analyzer tool.

Parses a broker CSV/Excel export and produces:
 \- profile: holding days, trade frequency, win rate, PnL ratio, cumulative
 PnL, max drawdown, top symbols, market/hourly distribution
 \- behavior (Phase 4b): disposition effect, overtrading, chasing momentum,
 anchoring — each with severity + numeric evidence

Strategy extraction → backtest bridge still pending (Phase 4c).
"""

from \_\_future\_\_ import annotations

import json
import logging
from collections import defaultdict, deque
from typing import Any

import pandas as pd

from src.agent.tools import BaseTool
from src.tools.path\_utils import safe\_user\_path
from src.tools.trade\_journal\_parsers import (
 parse\_file,
 records\_to\_dataframe,
)

logger = logging.getLogger(\_\_name\_\_)

\_ALLOWED\_EXT = {".csv", ".xlsx", ".xls"}

def pair\_trades\_fifo(df: pd.DataFrame) -> list\[dict\[str, Any\]\]:
 """Pair buys and sells per symbol using FIFO to compute per-roundtrip PnL.

 Args:
 df: Standardized DataFrame (datetime-sorted).

 Returns:
 List of dicts: symbol, buy\_dt, sell\_dt, qty, buy\_price, sell\_price,
 hold\_days, pnl, pnl\_pct. Unmatched positions are ignored.
 """
 queues: dict\[str, deque\] = defaultdict(deque)
 roundtrips: list\[dict\[str, Any\]\] = \[\]

 for row in df.itertuples(index=False):
 if row.side == "buy":
 queues\[row.symbol\].append({
 "dt": row.datetime,
 "qty": row.quantity,
 "price": row.price,
 "fee": row.fee,
 })
 continue

 # sell: match against oldest buys
 remaining = row.quantity
 q = queues\[row.symbol\]
 while remaining > 1e-9 and q:
 lot = q\[0\]
 take = min(lot\["qty"\], remaining)
 hold = (row.datetime - lot\["dt"\]).total\_seconds() / 86400.0
 gross = (row.price - lot\["price"\]) \* take
 # Proportional fee allocation
 buy\_fee = lot\["fee"\] \* (take / lot\["qty"\]) if lot\["qty"\] else 0.0
 sell\_fee = row.fee \* (take / row.quantity) if row.quantity else 0.0
 pnl = gross - buy\_fee - sell\_fee
 cost = lot\["price"\] \* take
 pnl\_pct = pnl / cost if cost else 0.0
 roundtrips.append({
 "symbol": row.symbol,
 "buy\_dt": lot\["dt"\],
 "sell\_dt": row.datetime,
 "qty": take,
 "buy\_price": lot\["price"\],
 "sell\_price": row.price,
 "hold\_days": round(hold, 2),
 "pnl": round(pnl, 2),
 "pnl\_pct": round(pnl\_pct, 4),
 })
 lot\["qty"\] -= take
 remaining -= take
 if lot\["qty"\] <= 1e-9:
 q.popleft()
 return roundtrips

def \_safe\_div(a: float, b: float) -> float:
 return float(a) / float(b) if b else 0.0

def \_compute\_profile(df: pd.DataFrame) -> dict\[str, Any\]:
 """Build the trading profile dict.

 Args:
 df: Standardized DataFrame (datetime parsed, sorted).

 Returns:
 Dict with avg\_holding\_days, trade\_frequency\_per\_week, win\_rate,
 profit\_loss\_ratio, total\_pnl, max\_drawdown, top\_symbols,
 market\_distribution, hourly\_distribution, roundtrips\_sample.
 """
 if df.empty:
 return {"error": "empty trade journal"}

 rts = pair\_trades\_fifo(df)
 rts\_df = pd.DataFrame(rts)

 total\_trades = len(df)
 span\_days = max(1, (df\["datetime"\].max() - df\["datetime"\].min()).days)
 freq\_per\_week = round(total\_trades / span\_days \* 7, 2)

 if not rts\_df.empty:
 wins = rts\_df\[rts\_df\["pnl"\] > 0\]
 losses = rts\_df\[rts\_df\["pnl"\] < 0\]
 avg\_win = wins\["pnl"\].mean() if len(wins) else 0.0
 avg\_loss = losses\["pnl"\].mean() if len(losses) else 0.0
 win\_rate = round(len(wins) / len(rts\_df), 4)
 pnl\_ratio = round(\_safe\_div(avg\_win, abs(avg\_loss)), 2) if avg\_loss else float("inf") if avg\_win else 0.0
 avg\_hold = round(rts\_df\["hold\_days"\].mean(), 2)
 total\_pnl = round(rts\_df\["pnl"\].sum(), 2)
 # Cumulative PnL → max drawdown
 cum = rts\_df.sort\_values("sell\_dt")\["pnl"\].cumsum()
 running\_max = cum.cummax()
 drawdown = (cum - running\_max).min()
 max\_drawdown = round(float(drawdown), 2) if pd.notna(drawdown) else 0.0
 else:
 win\_rate = pnl\_ratio = avg\_hold = total\_pnl = max\_drawdown = 0.0

 top\_symbols = (
 df.groupby("symbol")
 .agg(trades=("symbol", "count"), total\_amount=("amount", "sum"))
 .sort\_values("total\_amount", ascending=False)
 .head(10)
 .round(2)
 .reset\_index()
 .to\_dict(orient="records")
 )

 market\_dist = df\["market"\].value\_counts().to\_dict()
 hourly\_dist = df\["datetime"\].dt.hour.value\_counts().sort\_index().to\_dict()
 hourly\_dist = {int(h): int(c) for h, c in hourly\_dist.items()}

 sample = rts\_df.head(5).copy()
 if not sample.empty:
 sample\["buy\_dt"\] = sample\["buy\_dt"\].astype(str)
 sample\["sell\_dt"\] = sample\["sell\_dt"\].astype(str)
 roundtrips\_sample = sample.to\_dict(orient="records")
 else:
 roundtrips\_sample = \[\]

 return {
 "total\_trades": total\_trades,
 "total\_roundtrips": len(rts\_df),
 "avg\_holding\_days": avg\_hold,
 "trade\_frequency\_per\_week": freq\_per\_week,
 "win\_rate": win\_rate,
 "profit\_loss\_ratio": pnl\_ratio,
 "total\_pnl": total\_pnl,
 "max\_drawdown": max\_drawdown,
 "top\_symbols": top\_symbols,
 "market\_distribution": market\_dist,
 "hourly\_distribution": hourly\_dist,
 "roundtrips\_sample": roundtrips\_sample,
 }

def \_severity(score: float, thresholds: tuple\[float, float\]) -> str:
 """Map a numeric score to low/medium/high given (med\_cutoff, high\_cutoff)."""
 med, high = thresholds
 if score >= high:
 return "high"
 if score >= med:
 return "medium"
 return "low"

def \_disposition\_effect(rts\_df: pd.DataFrame) -> dict\[str, Any\]:
 """Detect disposition effect: holding losers longer than winners.

 Metric = avg\_loss\_hold / avg\_win\_hold. A ratio > 1 means the user holds
 losing positions longer than winning ones — the classic disposition bias.
 """
 if rts\_df.empty:
 return {"severity": "low", "evidence": "no closed roundtrips"}
 wins = rts\_df\[rts\_df\["pnl"\] > 0\]
 losses = rts\_df\[rts\_df\["pnl"\] < 0\]
 if wins.empty or losses.empty:
 return {
 "severity": "low",
 "evidence": "not enough winners and losers to compare holding times",
 }
 win\_hold = float(wins\["hold\_days"\].mean())
 loss\_hold = float(losses\["hold\_days"\].mean())
 ratio = loss\_hold / win\_hold if win\_hold > 0 else float("inf")
 severity = \_severity(ratio, (1.2, 1.5))
 return {
 "severity": severity,
 "ratio\_loss\_to\_win\_hold": round(ratio, 2),
 "avg\_winner\_hold\_days": round(win\_hold, 2),
 "avg\_loser\_hold\_days": round(loss\_hold, 2),
 "evidence": (
 f"Losing roundtrips held {loss\_hold:.1f}d vs winning "
 f"{win\_hold:.1f}d (ratio {ratio:.2f}). "
 \+ ("Classic disposition pattern." if severity == "high"
 else "Mild hold-losers-longer tendency." if severity == "medium"
 else "Hold times roughly symmetric.")
 ),
 }

def \_overtrading(df: pd.DataFrame, rts\_df: pd.DataFrame) -> dict\[str, Any\]:
 """Detect overtrading: high-activity days produce worse PnL.

 Buckets trading days into top-quartile (busy) and bottom-quartile (quiet)
 by trade count, then compares the realized PnL of roundtrips whose sell
 lands on each bucket.
 """
 if df.empty or rts\_df.empty:
 return {"severity": "low", "evidence": "insufficient data"}

 daily\_trades = df.groupby(df\["datetime"\].dt.date).size()
 if len(daily\_trades) < 4:
 return {"severity": "low", "evidence": "fewer than 4 trading days"}

 busy\_cut = daily\_trades.quantile(0.75)
 quiet\_cut = daily\_trades.quantile(0.25)
 busy\_days = set(daily\_trades\[daily\_trades >= busy\_cut\].index)
 quiet\_days = set(daily\_trades\[daily\_trades <= quiet\_cut\].index)

 rts\_df = rts\_df.copy()
 rts\_df\["sell\_date"\] = pd.to\_datetime(rts\_df\["sell\_dt"\]).dt.date
 busy\_pnl = rts\_df\[rts\_df\["sell\_date"\].isin(busy\_days)\]\["pnl"\]
 quiet\_pnl = rts\_df\[rts\_df\["sell\_date"\].isin(quiet\_days)\]\["pnl"\]
 if busy\_pnl.empty or quiet\_pnl.empty:
 return {"severity": "low", "evidence": "roundtrips not spread across busy/quiet days"}

 busy\_avg = float(busy\_pnl.mean())
 quiet\_avg = float(quiet\_pnl.mean())

 # severity rule: busy-day PnL must be meaningfully worse than quiet-day
 gap = quiet\_avg - busy\_avg
 base = abs(quiet\_avg) if quiet\_avg != 0 else 1.0
 severity = \_severity(gap / base, (0.3, 1.0)) if busy\_avg < quiet\_avg else "low"

 return {
 "severity": severity,
 "busy\_day\_avg\_pnl": round(busy\_avg, 2),
 "quiet\_day\_avg\_pnl": round(quiet\_avg, 2),
 "busy\_day\_trade\_threshold": round(float(busy\_cut), 1),
 "evidence": (
 f"On busy days (≥{busy\_cut:.0f} trades) avg PnL {busy\_avg:+.0f}; "
 f"on quiet days (≤{quiet\_cut:.0f}) avg PnL {quiet\_avg:+.0f}. "
 \+ ("High activity hurts returns." if severity == "high"
 else "Some drag from busy-day trading." if severity == "medium"
 else "Activity level does not materially hurt PnL.")
 ),
 }

def \_chasing\_momentum(df: pd.DataFrame) -> dict\[str, Any\]:
 """Detect chasing: buys concentrated after recent price rises in the same symbol.

 For each BUY, look at the user's own last 3 trades of that symbol. If the
 price trended upward (last trade price > 3rd-prior by > 3%), count the buy
 as a chase. Ratio of chasing buys → severity.
 """
 buys = df\[df\["side"\] == "buy"\].sort\_values(\["symbol", "datetime"\]).copy()
 if buys.empty:
 return {"severity": "low", "evidence": "no buys"}

 buys\["prev3\_price"\] = buys.groupby("symbol")\["price"\].shift(3)
 matured = buys.dropna(subset=\["prev3\_price"\])
 if matured.empty:
 return {
 "severity": "low",
 "evidence": "not enough repeat buys per symbol to evaluate chasing",
 }
 chased = matured\[matured\["price"\] > matured\["prev3\_price"\] \* 1.03\]
 ratio = len(chased) / len(matured)
 severity = \_severity(ratio, (0.4, 0.6))
 return {
 "severity": severity,
 "chase\_ratio": round(ratio, 3),
 "buys\_evaluated": int(len(matured)),
 "evidence": (
 f"{len(chased)}/{len(matured)} buys ({ratio:.0%}) came after a >3% "
 "price run-up in the same symbol. "
 \+ ("Strong chasing pattern." if severity == "high"
 else "Some chasing tendency." if severity == "medium"
 else "No clear chasing bias.")
 ),
 }

def \_anchoring(df: pd.DataFrame) -> dict\[str, Any\]:
 """Detect price anchoring: repeated trades cluster in a narrow price band.

 For each symbol with ≥5 trades, compute σ(price)/mean(price). A low ratio
 (<0.05) means the user consistently trades the same price area, suggesting
 they are anchored to a reference price rather than reacting to moves.
 """
 grouped = df.groupby("symbol")
 rows: list\[dict\[str, Any\]\] = \[\]
 for sym, sub in grouped:
 if len(sub) < 5:
 continue
 mean = float(sub\["price"\].mean())
 std = float(sub\["price"\].std())
 if mean == 0:
 continue
 cv = std / mean
 rows.append({"symbol": sym, "trades": len(sub), "mean\_price": round(mean, 2), "cv": round(cv, 4)})

 if not rows:
 return {"severity": "low", "evidence": "no symbol has ≥5 trades to evaluate anchoring"}

 anchored = \[r for r in rows if r\["cv"\] < 0.05\]
 ratio = len(anchored) / len(rows)
 severity = \_severity(ratio, (0.33, 0.66))
 return {
 "severity": severity,
 "anchored\_symbol\_ratio": round(ratio, 3),
 "symbols\_evaluated": len(rows),
 "anchored\_symbols": anchored\[:5\],
 "evidence": (
 f"{len(anchored)}/{len(rows)} frequently-traded symbols stayed in a "
 "narrow price band (CV<5%). "
 \+ ("Strong anchoring — repeated trades at the same price." if severity == "high"
 else "Some anchoring on select symbols." if severity == "medium"
 else "Prices vary naturally across repeat trades.")
 ),
 }

def \_compute\_behavior(df: pd.DataFrame) -> dict\[str, Any\]:
 """Run all 4 behavior diagnostics.

 Args:
 df: Standardized DataFrame (datetime-sorted).

 Returns:
 Dict with disposition\_effect / overtrading / chasing\_momentum /
 anchoring keys, each {severity, evidence, ...metrics}.
 """
 if df.empty:
 return {"error": "empty trade journal"}
 rts\_df = pd.DataFrame(pair\_trades\_fifo(df))
 return {
 "disposition\_effect": \_disposition\_effect(rts\_df),
 "overtrading": \_overtrading(df, rts\_df),
 "chasing\_momentum": \_chasing\_momentum(df),
 "anchoring": \_anchoring(df),
 }

def \_apply\_filter(df: pd.DataFrame, expr: str) -> pd.DataFrame:
 """Filter DataFrame by a simple expression.

 Supports:
 \- "YYYY-MM to YYYY-MM" or "YYYY-MM-DD to YYYY-MM-DD" (date range)
 \- "symbol=XXX" (exact match)
 \- "market=china\_a\|us\|hk\|crypto"

 Args:
 df: Standardized DataFrame.
 expr: Filter expression.

 Returns:
 Filtered DataFrame (may be empty).
 """
 expr = expr.strip()
 if not expr:
 return df

 if " to " in expr:
 try:
 lo\_raw, hi\_raw = (p.strip() for p in expr.split(" to ", 1))
 lo = pd.to\_datetime(lo\_raw)
 hi = pd.to\_datetime(hi\_raw) + pd.Timedelta(days=1)
 return df\[(df\["datetime"\] >= lo) & (df\["datetime"\] < hi)\]
 except Exception as exc:
 logger.warning("filter date parse failed: %s", exc)
 return df

 if "=" in expr:
 key, val = (p.strip() for p in expr.split("=", 1))
 if key in df.columns:
 return df\[df\[key\].astype(str).str.upper() == val.upper()\]
 return df

def analyze\_trade\_journal(file\_path: str, analysis\_type: str = "full", filter\_expr: str = "") -> str:
 """Parse a trade journal and return a JSON analysis.

 Args:
 file\_path: Path to CSV/Excel file.
 analysis\_type: "full" \| "profile" \| "behavior" \| "strategy".
 "profile" and "behavior" are fully implemented; "strategy" still
 returns a Phase 4c placeholder.
 filter\_expr: Optional filter. Examples: "2026-01 to 2026-03",
 "symbol=600519.SH", "market=china\_a".

 Returns:
 JSON string. Keys: status, file, format\_detected, total\_records,
 date\_range, market, profile / behavior (when applicable).
 """
 try:
 path = safe\_user\_path(file\_path)
 except ValueError as exc:
 return json.dumps({"status": "error", "error": str(exc)}, ensure\_ascii=False)
 if not path.exists():
 return json.dumps({"status": "error", "error": f"File not found: {file\_path}"}, ensure\_ascii=False)
 if path.suffix.lower() not in \_ALLOWED\_EXT:
 return json.dumps(
 {"status": "error", "error": f"Unsupported extension {path.suffix}. Expected .csv/.xlsx/.xls"},
 ensure\_ascii=False,
 )

 try:
 fmt, records = parse\_file(path)
 except (ValueError, FileNotFoundError) as exc:
 return json.dumps({"status": "error", "error": str(exc)}, ensure\_ascii=False)

 if not records:
 return json.dumps(
 {"status": "error", "error": "No trade records parsed"}, ensure\_ascii=False
 )

 df = records\_to\_dataframe(records)
 filtered = \_apply\_filter(df, filter\_expr)

 result: dict\[str, Any\] = {
 "status": "ok",
 "file": path.name,
 "format\_detected": fmt,
 "total\_records": len(filtered),
 "date\_range": \_format\_range(filtered),
 "symbols\_count": int(filtered\["symbol"\].nunique()) if not filtered.empty else 0,
 "market": \_pick\_dominant\_market(filtered),
 }
 if filter\_expr:
 result\["filter\_applied"\] = filter\_expr

 if analysis\_type in {"full", "profile"}:
 result\["profile"\] = \_compute\_profile(filtered)

 if analysis\_type in {"full", "behavior"}:
 result\["behavior"\] = \_compute\_behavior(filtered)

 if analysis\_type in {"full", "strategy"}:
 result\["strategy\_features"\] = {
 "status": "pending",
 "note": "Strategy extraction → backtest bridging lands in Phase 4c.",
 }

 return json.dumps(result, ensure\_ascii=False, default=str)

def \_format\_range(df: pd.DataFrame) -> str:
 """Return 'YYYY-MM-DD ~ YYYY-MM-DD' or empty."""
 if df.empty:
 return ""
 return f"{df\['datetime'\].min().date()} ~ {df\['datetime'\].max().date()}"

def \_pick\_dominant\_market(df: pd.DataFrame) -> str:
 """Return the most-traded market; empty when df is empty."""
 if df.empty:
 return ""
 return df\["market"\].value\_counts().idxmax()

class TradeJournalTool(BaseTool):
 """Trade journal analyzer tool (registered via auto-discovery)."""

 name = "analyze\_trade\_journal"
 description = (
 "Analyze a user's trade journal (CSV/Excel broker export). "
 "Parses 同花顺/东方财富/富途/generic formats. Returns: "
 "(1) trading profile — holding days, frequency, win rate, PnL ratio, "
 "top symbols, market/hourly distribution; "
 "(2) behavior diagnostics — disposition effect, overtrading, chasing "
 "momentum, anchoring (each with severity + numeric evidence)."
 )
 parameters = {
 "type": "object",
 "properties": {
 "file\_path": {
 "type": "string",
 "description": "Path to the uploaded CSV/Excel file.",
 },
 "analysis\_type": {
 "type": "string",
 "enum": \["full", "profile", "behavior", "strategy"\],
 "description": "Which analysis to run. 'full' = profile (behavior/strategy are Phase 4b placeholders).",
 "default": "full",
 },
 "filter\_expr": {
 "type": "string",
 "description": "Optional filter, e.g. '2026-01 to 2026-03', 'symbol=600519.SH', 'market=china\_a'.",
 "default": "",
 },
 },
 "required": \["file\_path"\],
 }
 repeatable = True

 def execute(self, \*\*kwargs: Any) -> str:
 return analyze\_trade\_journal(
 file\_path=kwargs\["file\_path"\],
 analysis\_type=kwargs.get("analysis\_type", "full"),
 filter\_expr=kwargs.get("filter\_expr", ""),
 )