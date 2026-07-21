"""Shadow Account — strategy extraction from profitable roundtrips.

Pipeline:
 trades\_df → FIFO pair → filter (pnl > 0) → feature engineer
 → KMeans cluster (k auto 2-5) → per-cluster decision tree (max\_depth=3)
 → path extraction → structured entry\_condition dict
 → LLM-light natural-language translation (template fallback if no LLM)

Design constraints:
 \\* No \*mandatory\* external price-data calls. Journal-derived features
 (holding\_days, pnl\_pct, entry hour/weekday, market) always work offline.
 Price-context features (entry\_rsi14, prior\_5d\_return) are read as-of the
 buy date via the backtest loader registry and degrade to NaN — dropped
 from the feature matrix — whenever price data is unavailable.
 \\* Must survive tiny samples: <5 profitable roundtrips → explicit error.
 <2 clusters → degrade to a single-cluster heuristic rule.
 \\* Rules are immutable ShadowRule objects — codegen's only input.
"""

from \_\_future\_\_ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.shadow\_account.models import PRICE\_FEATURES, ShadowProfile, ShadowRule
from src.shadow\_account.storage import hash\_journal, new\_shadow\_id, now\_iso
from src.tools.trade\_journal\_parsers import parse\_file, records\_to\_dataframe
from src.tools.trade\_journal\_tool import pair\_trades\_fifo

logger = logging.getLogger(\_\_name\_\_)

MIN\_PROFITABLE\_ROUNDTRIPS = 5
DEFAULT\_MAX\_RULES = 5
DEFAULT\_MIN\_SUPPORT = 3
\_NUMERIC\_FEATURES = ("holding\_days", "pnl\_pct", "entry\_hour", "entry\_weekday")
\_CATEGORICAL\_FEATURES = ("market",)

\# Price-context features attached as-of buy\_dt (NaN when price data unavailable).
\# Names live on the data-contract boundary (models.PRICE\_FEATURES) so the
\# extractor, codegen, and scanner cannot drift; aliased here for local use.
\_PRICE\_FEATURES = PRICE\_FEATURES
\_RSI\_PERIOD = 14
\_PRIOR\_RETURN\_WINDOW = 5
\# Calendar buffer added before the earliest buy\_dt so the RSI warmup has enough
\# trading bars even across weekends/holidays.
\_PRICE\_LOOKBACK\_DAYS = 40

\# Journal market label → backtest loader-registry market key. Labels with no
\# mapping (e.g. "other") skip the price fetch and degrade to NaN.
\_MARKET\_KEY\_MAP = {
 "china\_a": "a\_share",
 "us": "us\_equity",
 "hk": "hk\_equity",
 "crypto": "crypto",
}

\# ---------------- Public API ----------------

def extract\_shadow\_profile(
 journal\_path: str \| Path,
 \*,
 min\_support: int = DEFAULT\_MIN\_SUPPORT,
 max\_rules: int = DEFAULT\_MAX\_RULES,
 llm\_translator: Any \| None = None,
) -\> ShadowProfile:
 """Extract a ShadowProfile from a broker journal file.

 Args:
 journal\_path: CSV/Excel exported from a supported broker.
 min\_support: Minimum profitable roundtrips backing any single rule.
 max\_rules: Cap on the number of rules returned.
 llm\_translator: Optional callable (dict) -> str for translating
 structured entry\_condition into natural-language text. If None,
 a deterministic f-string fallback is used.

 Returns:
 ShadowProfile (not yet persisted — caller decides whether to save).

 Raises:
 ValueError: Fewer than MIN\_PROFITABLE\_ROUNDTRIPS profitable roundtrips.
 """
 path = Path(journal\_path)
 fmt, records = parse\_file(path)
 if not records:
 raise ValueError(f"No trade records parsed from {path} (format={fmt})")
 trades\_df = records\_to\_dataframe(records)

 roundtrips = pair\_trades\_fifo(trades\_df)
 total = len(roundtrips)
 if total == 0:
 raise ValueError("No complete buy→sell roundtrips found in journal.")

 profitable = \[rt for rt in roundtrips if rt\["pnl"\] > 0\]
 if len(profitable) < MIN\_PROFITABLE\_ROUNDTRIPS:
 raise ValueError(
 f"Insufficient profitable roundtrips: {len(profitable)} "
 f"(need ≥{MIN\_PROFITABLE\_ROUNDTRIPS}).",
 )

 features\_df = \_compute\_features(profitable, trades\_df)
 rules = \_extract\_rules(
 features\_df,
 min\_support=min\_support,
 max\_rules=max\_rules,
 llm\_translator=llm\_translator,
 )

 source\_market = \_dominant(trades\_df\["market"\])
 preferred\_markets = tuple(trades\_df\["market"\].value\_counts().index.tolist())
 hold = features\_df\["holding\_days"\].dropna()
 typical\_holding = (
 round(float(hold.median()), 2) if len(hold) else 0.0,
 round(float(hold.quantile(0.75)), 2) if len(hold) else 0.0,
 )
 date\_range = (
 str(trades\_df\["datetime"\].min()),
 str(trades\_df\["datetime"\].max()),
 )
 profile\_text = \_render\_profile\_text(
 total\_profitable=len(profitable),
 total\_all=total,
 typical\_holding=typical\_holding,
 source\_market=source\_market,
 preferred\_markets=preferred\_markets,
 )

 return ShadowProfile(
 shadow\_id=new\_shadow\_id(),
 created\_at=now\_iso(),
 journal\_hash=hash\_journal(path),
 source\_market=source\_market,
 profitable\_roundtrips=len(profitable),
 total\_roundtrips=total,
 date\_range=date\_range,
 profile\_text=profile\_text,
 rules=tuple(rules),
 preferred\_markets=preferred\_markets,
 typical\_holding\_days=typical\_holding,
 )

\# ---------------- Feature engineering ----------------

def \_compute\_rsi(close: pd.Series, period: int = \_RSI\_PERIOD) -> pd.Series:
 """Causal Wilder-EWM RSI.

 Mirrors the shape of \`\`compute\_rsi\`\` in
 \`\`agent/src/skills/technical-basic/example\_signal\_engine.py:13\`\` — that
 module lives under a hyphenated (non-importable) skills directory, so the
 formula is re-implemented here rather than imported. Causal by construction:
 \`\`RSI\[t\]\`\` depends only on closes dated \`\`<= t\`\`.

 Args:
 close: Close-price series indexed by date.
 period: RSI lookback period.

 Returns:
 RSI series (0-100), NaN for the warmup window.
 """
 delta = close.diff()
 gain = delta.clip(lower=0)
 loss = (-delta).clip(lower=0)
 avg\_gain = gain.ewm(alpha=1 / period, min\_periods=period).mean()
 avg\_loss = loss.ewm(alpha=1 / period, min\_periods=period).mean()
 rs = avg\_gain / avg\_loss
 return 100 - 100 / (1 + rs)

def \_fetch\_price\_history(
 symbol: str,
 market: str,
 \*,
 start: pd.Timestamp,
 end: pd.Timestamp,
) -\> pd.DataFrame \| None:
 """Fetch daily OHLCV for one symbol via the backtest loader registry.

 Uses the same access path as the backtest runner (\`\`resolve\_loader\`\` +
 the loader \`\`fetch\`\` protocol). Any failure — unmapped market, no available
 source, empty result, symbol absent from the returned map — degrades to
 \`\`None\`\` so the caller can drop the price features rather than raise.

 Args:
 symbol: Journal symbol, passed to the loader as-is (no cross-market
 normalization in v1).
 market: Journal market label (e.g. \`\`"china\_a"\`\`).
 start: Inclusive fetch start (already buffered for indicator warmup).
 end: Inclusive fetch end — never later than the roundtrip's buy\_dt, so
 look-ahead is structurally impossible.

 Returns:
 A \`\`trade\_date\`\`-indexed OHLCV frame, or \`\`None\`\` when unavailable.
 """
 market\_key = \_MARKET\_KEY\_MAP.get(market)
 if market\_key is None:
 return None
 try:
 from backtest.loaders.base import NoAvailableSourceError
 from backtest.loaders.registry import resolve\_loader

 loader = resolve\_loader(market\_key)
 data\_map = loader.fetch(
 \[symbol\],
 start.strftime("%Y-%m-%d"),
 end.strftime("%Y-%m-%d"),
 interval="1D",
 )
 except NoAvailableSourceError as exc:
 logger.debug("No price source for %s (%s): %s", symbol, market, exc)
 return None
 except Exception as exc: # pragma: no cover — loader/network edge cases
 logger.debug("Price fetch failed for %s (%s): %s", symbol, market, exc)
 return None

 frame = data\_map.get(symbol)
 if frame is None or frame.empty or "close" not in frame.columns:
 return None
 return frame

def \_as\_of\_index(frame: pd.DataFrame, buy\_dt: pd.Timestamp) -> pd.DataFrame:
 """Slice a price frame to bars dated on or before \*buy\_dt\*.

 The loader frame is indexed by a tz-naive \`\`DatetimeIndex\`\` at day
 granularity; \`\`buy\_dt\`\` carries a time-of-day and may be tz-aware. Normalize
 to a tz-naive date before slicing, otherwise the \`\`.loc\`\` comparison raises.
 """
 as\_of = pd.Timestamp(buy\_dt)
 if as\_of.tzinfo is not None:
 as\_of = as\_of.tz\_localize(None)
 as\_of = as\_of.normalize()
 return frame.loc\[:as\_of\]

def \_price\_features\_as\_of(
 frame: pd.DataFrame \| None,
 buy\_dt: pd.Timestamp,
) -\> dict\[str, float\]:
 """Compute price-context features as-of \*buy\_dt\* from a price frame.

 Every value is read from bars dated \`\`<= buy\_dt\`\` only; bars in the
 \`\`(buy\_dt, sell\_dt\]\`\` exit window are never consulted. Insufficient history
 leaves the affected feature as \`\`NaN\`\`.
 """
 out: dict\[str, float\] = {name: float("nan") for name in \_PRICE\_FEATURES}
 if frame is None:
 return out

 history = \_as\_of\_index(frame, buy\_dt)
 close = history\["close"\].dropna()
 if close.empty:
 return out

 if len(close) >= \_RSI\_PERIOD:
 rsi = \_compute\_rsi(close).iloc\[-1\]
 out\["entry\_rsi14"\] = float(rsi) if pd.notna(rsi) else float("nan")

 if len(close) >= \_PRIOR\_RETURN\_WINDOW + 1:
 ret = close.pct\_change(\_PRIOR\_RETURN\_WINDOW).iloc\[-1\]
 out\["prior\_5d\_return"\] = float(ret) if pd.notna(ret) else float("nan")

 return out

def \_attach\_price\_features(
 rows: list\[dict\[str, Any\]\],
) -\> None:
 """Attach price-context features in place, batching one fetch per symbol.

 Groups roundtrips by symbol, fetches each symbol's price window once over
 \`\`\[min(buy\_dt) - buffer, max(buy\_dt)\]\`\`, then reads each roundtrip's
 features as-of its own buy\_dt. Mutates each row dict with the price-feature
 keys (NaN when unavailable).
 """
 by\_symbol: dict\[str, list\[dict\[str, Any\]\]\] = {}
 for row in rows:
 by\_symbol.setdefault(row\["symbol"\], \[\]).append(row)

 for symbol, sym\_rows in by\_symbol.items():
 market = sym\_rows\[0\]\["market"\]
 buy\_dts = \[pd.Timestamp(r\["buy\_dt"\]) for r in sym\_rows\]
 end = max(buy\_dts)
 start = min(buy\_dts) - pd.Timedelta(days=\_PRICE\_LOOKBACK\_DAYS)
 if end.tzinfo is not None:
 end = end.tz\_localize(None)
 if start.tzinfo is not None:
 start = start.tz\_localize(None)
 frame = \_fetch\_price\_history(symbol, market, start=start, end=end)
 for row in sym\_rows:
 row.update(\_price\_features\_as\_of(frame, pd.Timestamp(row\["buy\_dt"\])))

def \_compute\_features(
 roundtrips: list\[dict\[str, Any\]\],
 trades\_df: pd.DataFrame,
) -\> pd.DataFrame:
 """Compute a features row per profitable roundtrip.

 Columns: symbol, market, holding\_days, pnl, pnl\_pct, entry\_hour,
 entry\_weekday, buy\_dt, sell\_dt, plus price-context features (entry\_rsi14,
 prior\_5d\_return) read as-of buy\_dt — NaN when price data is unavailable.
 """
 market\_by\_symbol = (
 trades\_df.drop\_duplicates("symbol").set\_index("symbol")\["market"\].to\_dict()
 )
 rows: list\[dict\[str, Any\]\] = \[\]
 for rt in roundtrips:
 buy\_dt = pd.Timestamp(rt\["buy\_dt"\])
 sell\_dt = pd.Timestamp(rt\["sell\_dt"\])
 rows.append({
 "symbol": rt\["symbol"\],
 "market": market\_by\_symbol.get(rt\["symbol"\], "other"),
 "holding\_days": float(rt\["hold\_days"\]),
 "pnl": float(rt\["pnl"\]),
 "pnl\_pct": float(rt\["pnl\_pct"\]),
 "entry\_hour": int(buy\_dt.hour),
 "entry\_weekday": int(buy\_dt.weekday()),
 "buy\_dt": buy\_dt,
 "sell\_dt": sell\_dt,
 })
 \_attach\_price\_features(rows)
 return pd.DataFrame(rows)

\# ---------------- Cluster + decision-tree rule extraction ----------------

def \_promoted\_numeric\_features(
 features\_df: pd.DataFrame,
 \*,
 min\_support: int,
) -\> tuple\[str, ...\]:
 """Return the numeric feature set used for clustering.

 Always includes the journal-derived \`\`\_NUMERIC\_FEATURES\`\`. A price feature
 joins only when it is present (non-NaN) for at least \`\`min\_support\`\` rows —
 too-sparse price features are excluded so clustering behaves exactly as the
 journal-only baseline when price data is largely unavailable.
 """
 promoted = list(\_NUMERIC\_FEATURES)
 for name in \_PRICE\_FEATURES:
 if name in features\_df.columns and features\_df\[name\].notna().sum() >= min\_support:
 promoted.append(name)
 return tuple(promoted)

def \_extract\_rules(
 features\_df: pd.DataFrame,
 \*,
 min\_support: int,
 max\_rules: int,
 llm\_translator: Any \| None,
) -\> list\[ShadowRule\]:
 """Cluster profitable roundtrips, derive one rule per dense cluster."""
 available\_price\_features = tuple(
 f for f in \_PRICE\_FEATURES if f in features\_df.columns
 )
 if len(features\_df) < min\_support:
 return \[\
 \_heuristic\_single\_rule(\
 features\_df,\
 min\_support,\
 llm\_translator,\
 price\_features=available\_price\_features,\
 )\
 \]

 numeric\_features = \_promoted\_numeric\_features(features\_df, min\_support=min\_support)
 promoted\_price\_features = tuple(
 f for f in numeric\_features if f in \_PRICE\_FEATURES
 )
 cluster\_labels = \_auto\_cluster(
 features\_df, max\_k=min(max\_rules, 5), numeric\_features=numeric\_features,
 )
 rules: list\[ShadowRule\] = \[\]
 total\_profitable = len(features\_df)
 used\_markets: set\[str\] = set()

 for cluster\_id in sorted(set(cluster\_labels)):
 cluster\_mask = cluster\_labels == cluster\_id
 cluster\_df = features\_df\[cluster\_mask\]
 if len(cluster\_df) < min\_support:
 continue
 rule = \_cluster\_to\_rule(
 cluster\_df=cluster\_df,
 rule\_index=len(rules) + 1,
 total\_profitable=total\_profitable,
 llm\_translator=llm\_translator,
 price\_features=promoted\_price\_features,
 )
 # Deduplicate near-identical rules (same market + same holding band)
 key = (rule.entry\_condition.get("market"), rule.holding\_days\_range)
 if key in used\_markets:
 continue
 used\_markets.add(key)
 rules.append(rule)
 if len(rules) >= max\_rules:
 break

 if not rules:
 rules = \[\
 \_heuristic\_single\_rule(\
 features\_df,\
 min\_support,\
 llm\_translator,\
 price\_features=promoted\_price\_features,\
 )\
 \]
 return rules

def \_auto\_cluster(
 features\_df: pd.DataFrame,
 \*,
 max\_k: int,
 numeric\_features: tuple\[str, ...\] = \_NUMERIC\_FEATURES,
) -\> np.ndarray:
 """Pick a cluster count via simple silhouette heuristic (fallback k=2).

 Uses the supplied numeric features; scales by z-score to avoid any single
 feature dominating. Promoted price features may carry NaNs for rows whose
 price data was unavailable; those are median-imputed so the KMeans input is
 complete and stays row-aligned with \`\`features\_df\`\` (StandardScaler/KMeans
 reject NaN). Imputation only affects \*grouping\* — \`\`\_cluster\_to\_rule\`\` never
 reads price features — so a neutral median cannot distort rule bounds.
 """
 from sklearn.cluster import KMeans
 from sklearn.preprocessing import StandardScaler

 numeric\_df = features\_df\[list(numeric\_features)\].astype(float)
 numeric\_df = numeric\_df.fillna(numeric\_df.median(numeric\_only=True))
 # A feature that is all-NaN stays NaN after median fill — drop such columns.
 numeric\_df = numeric\_df.dropna(axis=1, how="all")
 numeric = numeric\_df.to\_numpy()
 if len(numeric) <= 2 or max\_k < 2 or numeric.shape\[1\] == 0:
 return np.zeros(len(numeric), dtype=int)
 scaled = StandardScaler().fit\_transform(numeric)

 best\_k, best\_score = 2, -1.0
 try:
 from sklearn.metrics import silhouette\_score
 for k in range(2, min(max\_k, len(numeric) - 1) + 1):
 labels = KMeans(n\_clusters=k, n\_init=5, random\_state=42).fit\_predict(scaled)
 if len(set(labels)) < 2:
 continue
 score = silhouette\_score(scaled, labels)
 if score > best\_score:
 best\_k, best\_score = k, score
 except Exception as exc: # pragma: no cover — sklearn edge cases
 logger.debug("silhouette selection failed, fallback k=2: %s", exc)

 return KMeans(n\_clusters=best\_k, n\_init=5, random\_state=42).fit\_predict(scaled)

def \_cluster\_to\_rule(
 \*,
 cluster\_df: pd.DataFrame,
 rule\_index: int,
 total\_profitable: int,
 llm\_translator: Any \| None,
 price\_features: tuple\[str, ...\] = (),
) -\> ShadowRule:
 """Summarize a cluster as one ShadowRule.

 Entry condition uses p10–p90 numeric bounds + dominant market. This is
 lighter than a decision tree and stays interpretable with tiny samples;
 we can swap to DecisionTreeClassifier in v2 when features widen.
 """
 market = \_dominant(cluster\_df\["market"\])
 hold\_days = cluster\_df\["holding\_days"\]
 hold\_lo = max(1, int(round(float(hold\_days.quantile(0.10)))))
 hold\_hi = max(hold\_lo, int(round(float(hold\_days.quantile(0.90)))))
 hours = cluster\_df\["entry\_hour"\]
 hour\_lo = int(round(float(hours.quantile(0.10))))
 hour\_hi = int(round(float(hours.quantile(0.90))))

 entry\_condition: dict\[str, Any\] = {
 "market": market,
 "entry\_hour": {"min": hour\_lo, "max": hour\_hi},
 }
 for feature in price\_features:
 if feature in cluster\_df.columns:
 series = cluster\_df\[feature\].dropna()
 if len(series) >= 2:
 # 4 decimals: RSI bounds tolerate it and return-type features
 # (prior\_5d\_return ~ ±0.0x) would lose meaningful precision at 2.
 lo = float(round(series.quantile(0.10), 4))
 hi = float(round(series.quantile(0.90), 4))
 entry\_condition\[feature\] = {"min": lo, "max": hi}
 exit\_condition: dict\[str, Any\] = {
 "holding\_days": {"min": hold\_lo, "max": hold\_hi},
 }

 samples = tuple(
 f"{row.symbol}@{pd.Timestamp(row.buy\_dt).date().isoformat()}"
 for row in cluster\_df.head(3).itertuples(index=False)
 )
 support = int(len(cluster\_df))
 coverage = round(support / max(total\_profitable, 1), 3)

 human = \_translate\_rule(
 entry\_condition=entry\_condition,
 exit\_condition=exit\_condition,
 holding\_range=(hold\_lo, hold\_hi),
 translator=llm\_translator,
 )

 return ShadowRule(
 rule\_id=f"R{rule\_index}",
 human\_text=human,
 entry\_condition=entry\_condition,
 exit\_condition=exit\_condition,
 holding\_days\_range=(hold\_lo, hold\_hi),
 support\_count=support,
 coverage\_rate=coverage,
 sample\_trades=samples,
 )

def \_heuristic\_single\_rule(
 features\_df: pd.DataFrame,
 min\_support: int,
 llm\_translator: Any \| None,
 \*,
 price\_features: tuple\[str, ...\] = (),
) -\> ShadowRule:
 """Degenerate fallback when clustering/tree yield nothing usable.

 Forwards \`\`price\_features\`\` so the single-rule path carries the same
 RSI/return bounds as the multi-cluster path; \`\`\_cluster\_to\_rule\`\` already
 guards on column presence and \`\`len(series) >= 2\`\`, so sparse data simply
 yields a behavior-only rule.
 """
 return \_cluster\_to\_rule(
 cluster\_df=features\_df,
 rule\_index=1,
 total\_profitable=max(len(features\_df), min\_support),
 llm\_translator=llm\_translator,
 price\_features=price\_features,
 )

\# ---------------- Natural-language translation ----------------

\_MARKET\_LABELS = {
 "china\_a": "China A-share",
 "us": "US equity",
 "hk": "HK equity",
 "crypto": "Crypto",
 "other": "Other",
}

RULE\_TEXT\_MAX = 80

def \_translate\_rule(
 \*,
 entry\_condition: dict\[str, Any\],
 exit\_condition: dict\[str, Any\],
 holding\_range: tuple\[int, int\],
 translator: Any \| None,
) -\> str:
 """Turn a structured rule dict into a concise English sentence (<=80 chars)."""
 if translator is not None:
 try:
 text = translator({
 "entry\_condition": entry\_condition,
 "exit\_condition": exit\_condition,
 "holding\_range": holding\_range,
 })
 if isinstance(text, str) and text.strip():
 return text.strip()\[:RULE\_TEXT\_MAX\]
 except Exception as exc: # pragma: no cover — LLM failure, fallback
 logger.warning("LLM rule translator failed, falling back: %s", exc)

 market\_label = \_MARKET\_LABELS.get(entry\_condition.get("market", "other"), "Other")
 hour\_range = entry\_condition.get("entry\_hour", {})
 hour\_text = ""
 if hour\_range:
 lo, hi = hour\_range.get("min"), hour\_range.get("max")
 hour\_text = f" at {lo}:00" if lo == hi else f" between {lo}:00-{hi}:00"
 hold\_lo, hold\_hi = holding\_range
 hold\_text = f"hold {hold\_lo}-{hold\_hi}d" if hold\_lo != hold\_hi else f"hold {hold\_lo}d"
 entry\_text = f"Enter {market\_label}{hour\_text}"
 return f"{entry\_text}, {hold\_text}"\[:RULE\_TEXT\_MAX\]

\# ---------------- Utilities ----------------

def \_dominant(series: pd.Series) -> str:
 """Most frequent value in a series, or the first if tied."""
 if series.empty:
 return "other"
 return str(series.value\_counts().idxmax())

def \_render\_profile\_text(
 \*,
 total\_profitable: int,
 total\_all: int,
 typical\_holding: tuple\[float, float\],
 source\_market: str,
 preferred\_markets: tuple\[str, ...\],
) -\> str:
 """Build the Section 1 one-paragraph portrait (English)."""
 median, p75 = typical\_holding
 markets\_label = ", ".join(\_MARKET\_LABELS.get(m, m) for m in preferred\_markets\[:3\])
 source\_label = \_MARKET\_LABELS.get(source\_market, source\_market)
 return (
 f"{total\_profitable} of your {total\_all} closed roundtrips were profitable. "
 f"Primary market: {source\_label} (also active in {markets\_label}). "
 f"Median holding period {median:.1f}d; most positions closed within {p75:.1f}d."
 )