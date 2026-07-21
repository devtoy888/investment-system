"""Shadow Account — multi-market backtest driver + delta-PnL attribution.

Responsibilities:
 1\. Pick representative symbols per market based on the user's preferred
 markets (with a liquid-basket fallback).
 2\. Render a run\_dir (via \`\`codegen.write\_run\_dir\`\`) and call
 \`\`src.tools.backtest\_tool.run\_backtest\`\`.
 3\. Parse the emitted artifacts (metrics JSON / equity CSV) back into a
 \`\`ShadowBacktestResult\`\`.
 4\. Compute attribution: noise trades, missed signals, early/late exits,
 overtrading — each as signed PnL.

The attribution algorithm is deliberately arithmetic-only: no LLM, no
simulation rebuild. This keeps the numbers auditable and reproducible.
"""

from \_\_future\_\_ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

from src.shadow\_account.codegen import write\_run\_dir
from src.shadow\_account.models import (
 AttributionBreakdown,
 ShadowBacktestResult,
 ShadowProfile,
)
from src.shadow\_account.storage import runs\_dir
from src.tools.trade\_journal\_parsers import parse\_file, records\_to\_dataframe
from src.tools.trade\_journal\_tool import pair\_trades\_fifo

logger = logging.getLogger(\_\_name\_\_)

SUPPORTED\_MARKETS: tuple\[str, ...\] = ("china\_a", "hk", "us", "crypto")

\_LIQUID\_BASKETS: dict\[str, list\[str\]\] = {
 "china\_a": \["600519.SH", "000858.SZ", "300750.SZ", "600036.SH", "000001.SZ"\],
 "hk": \["00700.HK", "09988.HK", "03690.HK", "00388.HK", "01810.HK"\],
 "us": \["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"\],
 "crypto": \["BTC-USDT", "ETH-USDT", "SOL-USDT", "BNB-USDT", "XRP-USDT"\],
}

\# ---------------- Code selection ----------------

def select\_multi\_market\_codes(
 profile: ShadowProfile,
 \*,
 per\_market\_count: int = 5,
 markets: tuple\[str, ...\] = SUPPORTED\_MARKETS,
) -\> dict\[str, list\[str\]\]:
 """Pick representative tickers for each target market.

 Priority:
 1\. If the profile's source\_market is in the target set and is in the
 liquid basket, surface it first.
 2\. Fill remaining markets from their liquid basket.

 Args:
 profile: Shadow profile (source\_market guides prioritization).
 per\_market\_count: Cap per market (clamped to basket size).
 markets: Markets to include.

 Returns:
 Dict market → list of codes, non-empty for every requested market
 that has a known basket.
 """
 selection: dict\[str, list\[str\]\] = {}
 for market in markets:
 basket = \_LIQUID\_BASKETS.get(market)
 if not basket:
 continue
 selection\[market\] = basket\[: max(1, per\_market\_count)\]
 return selection

def flatten\_codes(selection: dict\[str, list\[str\]\]) -> list\[str\]:
 """Flatten per-market selection into a unique, order-preserving code list."""
 seen: set\[str\] = set()
 out: list\[str\] = \[\]
 for codes in selection.values():
 for c in codes:
 if c not in seen:
 out.append(c)
 seen.add(c)
 return out

\# ---------------- Backtest execution ----------------

def run\_shadow\_backtest(
 profile: ShadowProfile,
 \*,
 window\_start: str,
 window\_end: str,
 markets: tuple\[str, ...\] = SUPPORTED\_MARKETS,
 per\_market\_count: int = 5,
 source: str = "auto",
 initial\_capital: float = 1\_000\_000.0,
 journal\_path: str \| Path \| None = None,
 run\_backtest\_fn: Any \| None = None,
) -\> ShadowBacktestResult:
 """Drive a multi-market backtest from a ShadowProfile.

 Args:
 profile: ShadowProfile to replay.
 window\_start / window\_end: ISO dates.
 markets: Target market buckets.
 per\_market\_count: Codes per market.
 source: Loader source (\`\`auto\`\` routes by suffix).
 initial\_capital: Starting cash.
 journal\_path: Original journal path (used to compute attribution
 against the user's realized trades). Attribution is skipped if
 None or the file is missing.
 run\_backtest\_fn: Injection point for tests — callable(run\_dir\_str)
 returning the same JSON payload as
 \`\`src.tools.backtest\_tool.run\_backtest\`\`. Defaults to the real
 entrypoint.

 Returns:
 ShadowBacktestResult with per-market + combined metrics, equity
 curves (when emitted), and attribution (zeros when unavailable).
 """
 selection = select\_multi\_market\_codes(
 profile, per\_market\_count=per\_market\_count, markets=markets,
 )
 codes = flatten\_codes(selection)
 if not codes:
 raise ValueError("No codes available for requested markets.")

 run\_dir = runs\_dir(profile.shadow\_id)
 write\_run\_dir(
 profile,
 run\_dir,
 codes=codes,
 start\_date=window\_start,
 end\_date=window\_end,
 source=source,
 initial\_capital=initial\_capital,
 )

 backtest\_fn = run\_backtest\_fn or \_default\_run\_backtest\_fn()
 payload = json.loads(backtest\_fn(str(run\_dir)))

 per\_market, combined, equity\_curves = \_summarize\_artifacts(
 payload=payload, run\_dir=run\_dir, selection=selection,
 )

 attribution, shadow\_pnl, real\_pnl = \_attribution\_or\_zero(
 profile=profile,
 journal\_path=journal\_path,
 combined=combined,
 )

 result = ShadowBacktestResult(
 shadow\_id=profile.shadow\_id,
 per\_market=per\_market,
 combined=combined,
 equity\_curves=equity\_curves,
 attribution=attribution,
 shadow\_total\_pnl=shadow\_pnl,
 real\_total\_pnl=real\_pnl,
 delta\_pnl=round(shadow\_pnl - real\_pnl, 2),
 )
 \_cache\_result(run\_dir, result)
 return result

def load\_cached\_result(shadow\_id: str) -> ShadowBacktestResult \| None:
 """Load the last cached backtest result for a shadow, if any."""
 cache\_path = runs\_dir(shadow\_id) / "shadow\_result.json"
 if not cache\_path.exists():
 return None
 try:
 data = json.loads(cache\_path.read\_text(encoding="utf-8"))
 except (OSError, json.JSONDecodeError):
 return None
 attr = data.get("attribution") or {}
 return ShadowBacktestResult(
 shadow\_id=data\["shadow\_id"\],
 per\_market=data.get("per\_market") or {},
 combined=data.get("combined") or {},
 equity\_curves={
 k: \[(str(pt\[0\]), float(pt\[1\])) for pt in v\]
 for k, v in (data.get("equity\_curves") or {}).items()
 },
 attribution=AttributionBreakdown(
 missed\_signals\_pnl=float(attr.get("missed\_signals\_pnl", 0.0)),
 noise\_trades\_pnl=float(attr.get("noise\_trades\_pnl", 0.0)),
 early\_exit\_pnl=float(attr.get("early\_exit\_pnl", 0.0)),
 late\_exit\_pnl=float(attr.get("late\_exit\_pnl", 0.0)),
 overtrading\_pnl=float(attr.get("overtrading\_pnl", 0.0)),
 counterfactual\_trades=tuple(attr.get("counterfactual\_trades") or ()),
 ),
 shadow\_total\_pnl=float(data.get("shadow\_total\_pnl", 0.0)),
 real\_total\_pnl=float(data.get("real\_total\_pnl", 0.0)),
 delta\_pnl=float(data.get("delta\_pnl", 0.0)),
 )

def \_cache\_result(run\_dir: Path, result: ShadowBacktestResult) -> None:
 """Persist a ShadowBacktestResult so downstream tools don't re-backtest."""
 from dataclasses import asdict as \_asdict

 payload = \_asdict(result)
 try:
 (run\_dir / "shadow\_result.json").write\_text(
 json.dumps(payload, ensure\_ascii=False, indent=2, default=str),
 encoding="utf-8",
 )
 except OSError as exc: # pragma: no cover — disk failure is non-fatal
 logger.warning("Failed to cache shadow result: %s", exc)

def \_default\_run\_backtest\_fn():
 from src.tools.backtest\_tool import run\_backtest
 return run\_backtest

\# ---------------- Artifact parsing ----------------

def \_summarize\_artifacts(
 \*,
 payload: dict\[str, Any\],
 run\_dir: Path,
 selection: dict\[str, list\[str\]\],
) -\> tuple\[dict\[str, dict\[str, float\]\], dict\[str, float\], dict\[str, list\[tuple\[str, float\]\]\]\]:
 """Turn raw backtest output into (per\_market, combined, equity\_curves).

 Gracefully degrades when artifacts are missing (e.g. data fetch failed):
 returns empty dicts and a combined dict containing the error reason.
 """
 artifacts = payload.get("artifacts") or {}
 status = payload.get("status", "error")

 combined = \_load\_metrics(artifacts, run\_dir)
 equity\_points = \_load\_equity\_curve(artifacts, run\_dir)

 # Only surface an error when we genuinely have no metrics. A non-ok
 # status with usable metrics typically means a transient data-source
 # warning (e.g. yfinance flaked on one market) — downgrading to ok is
 # more faithful to what the user actually has.
 if not combined and status != "ok":
 combined = {"error": payload.get("stderr", "")\[-200:\] or "backtest failed"}

 per\_market = \_per\_market\_breakdown(combined, selection)
 equity\_curves = {"combined": equity\_points} if equity\_points else {}
 return per\_market, combined, equity\_curves

def \_load\_metrics(artifacts: dict\[str, str\], run\_dir: Path) -> dict\[str, float\]:
 """Pull a numeric metrics dict from the run\_dir.

 Looks for \`\`metrics.json\`\` first (preferred), then \`\`metrics.csv\`\`.
 Unknown shape → empty dict (caller treats as failure).
 """
 for key in ("metrics.json", "metrics", "metrics.csv"):
 path\_str = artifacts.get(key)
 if not path\_str:
 continue
 path = Path(path\_str)
 if not path.exists():
 continue
 try:
 if path.suffix == ".json":
 data = json.loads(path.read\_text(encoding="utf-8"))
 return \_coerce\_numeric(data)
 if path.suffix == ".csv":
 df = pd.read\_csv(path)
 if df.empty:
 return {}
 row = df.iloc\[-1\].to\_dict()
 return \_coerce\_numeric(row)
 except (OSError, json.JSONDecodeError, ValueError) as exc:
 logger.warning("Failed to parse metrics %s: %s", path, exc)

 # Fallback: scan run\_dir for a metrics file.
 for path in run\_dir.glob("\*\*/metrics.\*"):
 try:
 if path.suffix == ".json":
 return \_coerce\_numeric(json.loads(path.read\_text(encoding="utf-8")))
 if path.suffix == ".csv":
 df = pd.read\_csv(path)
 if not df.empty:
 return \_coerce\_numeric(df.iloc\[-1\].to\_dict())
 except Exception:
 continue
 return {}

def \_load\_equity\_curve(artifacts: dict\[str, str\], run\_dir: Path) -> list\[tuple\[str, float\]\]:
 """Load the equity curve as \[(iso\_date, equity), ...\]."""
 candidates: list\[Path\] = \[\]
 for key in ("equity.csv", "equity", "equity\_curve.csv"):
 path\_str = artifacts.get(key)
 if path\_str:
 candidates.append(Path(path\_str))
 candidates.extend(run\_dir.glob("\*\*/equity\*.csv"))

 seen: set\[Path\] = set()
 for path in candidates:
 if path in seen or not path.exists():
 continue
 seen.add(path)
 try:
 df = pd.read\_csv(path)
 except (OSError, pd.errors.ParserError) as exc:
 logger.warning("Failed to read equity csv %s: %s", path, exc)
 continue
 if df.empty:
 continue
 date\_col = next((c for c in df.columns if c.lower() in ("date", "datetime", "timestamp")), df.columns\[0\])
 equity\_col = next(
 (c for c in df.columns if c.lower() in ("equity", "equity\_curve", "value", "net\_value")),
 df.columns\[-1\],
 )
 return \[(str(row\[date\_col\]), float(row\[equity\_col\])) for \_, row in df.iterrows()\]
 return \[\]

def \_coerce\_numeric(data: dict\[str, Any\]) -> dict\[str, float\]:
 """Keep only the scalar numeric fields from a metrics dict."""
 out: dict\[str, float\] = {}
 for key, value in data.items():
 if isinstance(value, bool):
 continue
 if isinstance(value, (int, float)):
 out\[str(key)\] = float(value)
 return out

def \_per\_market\_breakdown(
 combined: dict\[str, float\],
 selection: dict\[str, list\[str\]\],
) -\> dict\[str, dict\[str, float\]\]:
 """Project the combined metrics into each requested market.

 v1 limitation: the runner emits a single combined metrics file regardless
 of cross-market composition, so per-market rows reuse the combined
 metrics. This is faithful (same backtest) but intentionally lossy; a
 follow-up can split equity by market attribution.
 """
 if not combined:
 return {market: {} for market in selection}
 return {market: dict(combined) for market in selection}

\# ---------------- Attribution ----------------

def \_attribution\_or\_zero(
 \*,
 profile: ShadowProfile,
 journal\_path: str \| Path \| None,
 combined: dict\[str, float\],
) -\> tuple\[AttributionBreakdown, float, float\]:
 """Compute attribution if the journal is available, else return zeros."""
 shadow\_pnl = float(combined.get("total\_return\_abs") or combined.get("total\_pnl") or 0.0)
 if not journal\_path:
 return \_zero\_attribution(), shadow\_pnl, 0.0
 path = Path(journal\_path)
 if not path.exists():
 return \_zero\_attribution(), shadow\_pnl, 0.0

 try:
 \_, records = parse\_file(path)
 trades\_df = records\_to\_dataframe(records)
 roundtrips = pair\_trades\_fifo(trades\_df)
 except Exception as exc:
 logger.warning("Attribution skipped — journal parse failed: %s", exc)
 return \_zero\_attribution(), shadow\_pnl, 0.0

 if not roundtrips:
 return \_zero\_attribution(), shadow\_pnl, 0.0

 return \_compute\_attribution(profile=profile, roundtrips=roundtrips, shadow\_pnl=shadow\_pnl)

def \_zero\_attribution() -> AttributionBreakdown:
 return AttributionBreakdown(
 missed\_signals\_pnl=0.0,
 noise\_trades\_pnl=0.0,
 early\_exit\_pnl=0.0,
 late\_exit\_pnl=0.0,
 overtrading\_pnl=0.0,
 counterfactual\_trades=(),
 )

def \_compute\_attribution(
 \*,
 profile: ShadowProfile,
 roundtrips: list\[dict\[str, Any\]\],
 shadow\_pnl: float,
) -\> tuple\[AttributionBreakdown, float, float\]:
 """Attribute the delta between user's real PnL and shadow PnL.

 Decomposition (signed — positive means shadow would have earned more):

 noise\_trades\_pnl = -Σ realized\_pnl on rule-violating trades
 (user's unexplained losses that shadow avoids)
 early\_exit\_pnl = +Σ shortfall on winning trades exited before
 the median rule holding range
 late\_exit\_pnl = +Σ excess loss on losing trades held past the
 median rule holding range
 overtrading\_pnl = -Σ realized\_pnl on trades beyond the shadow's
 expected trade budget (1 trade per 2\*hold\_days)
 missed\_signals\_pnl = shadow\_pnl - real\_pnl - (noise+early+late+over)
 (residual — everything the above can't explain)

 \`\`counterfactual\_trades\`\` lists the top-5 \|impact\| roundtrips for
 Section 6 of the report.
 """
 rule\_hold\_lo, rule\_hold\_hi = \_aggregate\_holding\_range(profile)
 noise = 0.0
 early = 0.0
 late = 0.0
 real\_pnl = 0.0
 counterfactuals: list\[dict\[str, Any\]\] = \[\]

 for rt in roundtrips:
 pnl = float(rt\["pnl"\])
 real\_pnl += pnl
 hold = float(rt\["hold\_days"\])
 within\_rule = rule\_hold\_lo <= hold <= rule\_hold\_hi
 impact = 0.0
 reason = ""
 if not within\_rule:
 noise += -pnl
 impact += -pnl
 reason = "rule\_violation"
 if pnl > 0 and hold < rule\_hold\_lo:
 shortfall = pnl \* max(0.0, (rule\_hold\_lo - hold) / max(rule\_hold\_lo, 1))
 early += shortfall
 impact += shortfall
 reason = reason or "early\_exit"
 if pnl < 0 and hold > rule\_hold\_hi:
 excess = -pnl \* max(0.0, (hold - rule\_hold\_hi) / max(rule\_hold\_hi, 1))
 late += excess
 impact += excess
 reason = reason or "late\_exit"
 if impact != 0.0:
 counterfactuals.append({
 "symbol": rt\["symbol"\],
 "buy\_dt": str(rt\["buy\_dt"\]),
 "sell\_dt": str(rt\["sell\_dt"\]),
 "hold\_days": hold,
 "pnl": round(pnl, 2),
 "impact": round(impact, 2),
 "reason": reason,
 })

 overtrading = \_overtrading\_pnl(profile=profile, roundtrips=roundtrips)
 explained = noise + early + late + overtrading
 missed = round(shadow\_pnl - real\_pnl - explained, 2)

 counterfactuals.sort(key=lambda r: abs(r\["impact"\]), reverse=True)
 top5 = tuple(counterfactuals\[:5\])

 return (
 AttributionBreakdown(
 missed\_signals\_pnl=round(missed, 2),
 noise\_trades\_pnl=round(noise, 2),
 early\_exit\_pnl=round(early, 2),
 late\_exit\_pnl=round(late, 2),
 overtrading\_pnl=round(overtrading, 2),
 counterfactual\_trades=top5,
 ),
 round(shadow\_pnl, 2),
 round(real\_pnl, 2),
 )

def \_aggregate\_holding\_range(profile: ShadowProfile) -> tuple\[float, float\]:
 """Union holding-day ranges across all rules (lo=min, hi=max)."""
 if not profile.rules:
 return (1.0, 30.0)
 los = \[r.holding\_days\_range\[0\] for r in profile.rules\]
 his = \[r.holding\_days\_range\[1\] for r in profile.rules\]
 return (float(min(los)), float(max(his)))

def \_overtrading\_pnl(
 \*,
 profile: ShadowProfile,
 roundtrips: list\[dict\[str, Any\]\],
) -\> float:
 """Excess-frequency PnL: trades beyond the shadow's expected budget.

 Shadow runs roughly 1 trade per \`\`2 \* median\_hold\_days\`\` bars. We
 compare against the user's actual roundtrip count over the same span.
 Excess trades' PnL is totaled with a negative sign (shadow would've
 skipped them, so real PnL — positive or negative — is "noise").
 """
 if not roundtrips:
 return 0.0
 median\_hold, \_ = profile.typical\_holding\_days
 if median\_hold <= 0:
 return 0.0
 span\_days = (
 pd.Timestamp(roundtrips\[-1\]\["sell\_dt"\]) - pd.Timestamp(roundtrips\[0\]\["buy\_dt"\])
 ).total\_seconds() / 86400.0
 expected = max(1.0, span\_days / max(2 \* median\_hold, 1.0))
 actual = len(roundtrips)
 if actual <= expected:
 return 0.0
 # Penalize the cheapest (lowest \|pnl\|) extras — those look like noise.
 extras = sorted(roundtrips, key=lambda rt: abs(float(rt\["pnl"\])))
 extra\_count = int(actual - expected)
 extra\_pnl = sum(float(rt\["pnl"\]) for rt in extras\[:extra\_count\])
 return -extra\_pnl

\_\_all\_\_ = \[\
 "SUPPORTED\_MARKETS",\
 "flatten\_codes",\
 "load\_cached\_result",\
 "run\_shadow\_backtest",\
 "select\_multi\_market\_codes",\
\]