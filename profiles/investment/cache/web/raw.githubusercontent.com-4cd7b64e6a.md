"""Mootdx loader: A-share OHLCV via TCP-direct 通达信 servers (no IP ban).

Mootdx (https://github.com/mootdx/mootdx) talks the native 通达信 binary
protocol over TCP and is not subject to the HTTP scraping rate limits that
periodically break the akshare → East Money path. Public market data only,
no token required, no per-IP throttling.

Scope: A-share OHLCV only (沪/深/京 auto-detected from symbol). Mootdx's
extended-market endpoint (futures/options) is upstream-broken as of
v0.11.7 — falls through to tushare/akshare for those markets.
"""

from \_\_future\_\_ import annotations

import logging
from typing import Dict, List, Optional

import pandas as pd

from backtest.loaders.base import cached\_loader\_fetch, validate\_date\_range
from backtest.loaders.registry import register

logger = logging.getLogger(\_\_name\_\_)

\# Mootdx frequency codes (see mootdx.consts).
\_INTRADAY\_FREQ: dict\[str, int\] = {
 "1m": 8,
 "5m": 0,
 "15m": 1,
 "30m": 2,
 "1H": 3,
}
\_DAILY\_FREQ: dict\[str, int\] = {
 "1D": 4,
 "1W": 5,
 "1M": 6,
}

\# bars() returns one page of N rows ending at the latest bar. Pages older
\# than this need to be requested with \`\`start=offset\_into\_history\`\`. We cap
\# pagination at MAX\_PAGES so a wildly out-of-range request can't grind for
\# minutes against the TDX server.
\_BARS\_PAGE = 800
\_MAX\_PAGES = 25 # 25 × 800 = 20 000 bars (~10y daily, ~5y 1H, ~3mo 1m)

def \_is\_a\_share(code: str) -> bool:
 """Accept either explicit \`.SH/.SZ/.BJ\` suffix or bare 6-digit ticker."""
 upper = code.upper()
 if upper.endswith((".SH", ".SZ", ".BJ")):
 return True
 return len(code) == 6 and code.isdigit()

def \_is\_bj(code: str) -> bool:
 """Detect 北交所 symbols. Mootdx std factory does not serve BJ data
 (get\_k\_data raises KeyError, bars() returns empty), so the loader logs
 a warning and skips these instead of silently returning nothing."""
 upper = code.upper()
 if upper.endswith(".BJ"):
 return True
 # 4xxxxx / 8xxxxx are BJ prefixes (bare 6-digit form).
 return len(code) == 6 and code.isdigit() and code\[0\] in ("4", "8")

@register
class DataLoader:
 """Mootdx-backed A-share OHLCV loader (TCP-direct, no auth)."""

 name = "mootdx"
 markets = {"a\_share"}
 requires\_auth = False

 def \_\_init\_\_(self) -> None:
 self.\_client = None

 def is\_available(self) -> bool:
 """Available if mootdx is installed."""
 try:
 import mootdx # noqa: F401
 return True
 except ImportError:
 return False

 def \_get\_client(self):
 if self.\_client is None:
 from mootdx.quotes import Quotes
 self.\_client = Quotes.factory(market="std")
 return self.\_client

 def fetch(
 self,
 codes: List\[str\],
 start\_date: str,
 end\_date: str,
 \*,
 interval: str = "1D",
 fields: Optional\[List\[str\]\] = None,
 ) -\> Dict\[str, pd.DataFrame\]:
 """Fetch A-share OHLCV via mootdx.

 Args:
 codes: Symbol list. \`.SH/.SZ/.BJ\` suffix or bare 6-digit
 tickers; non-A-share symbols are silently skipped.
 start\_date: YYYY-MM-DD.
 end\_date: YYYY-MM-DD.
 interval: One of \`\`1m / 5m / 15m / 30m / 1H / 1D / 1W / 1M\`\`.
 fields: Ignored.

 Returns:
 Mapping symbol -> OHLCV DataFrame.

 Raises:
 ValueError: If \`\`interval\`\` is not in the supported set.
 """
 validate\_date\_range(start\_date, end\_date)
 if interval not in \_DAILY\_FREQ and interval not in \_INTRADAY\_FREQ:
 raise ValueError(
 f"Unsupported interval for mootdx: {interval!r}. "
 f"Supported: {sorted(\_DAILY\_FREQ) + sorted(\_INTRADAY\_FREQ)}"
 )

 result: Dict\[str, pd.DataFrame\] = {}
 for code in codes:
 if not \_is\_a\_share(code):
 logger.debug("mootdx: skipping non-A-share symbol %s", code)
 continue
 if \_is\_bj(code):
 logger.warning(
 "mootdx: 北交所 (%s) not supported upstream; use akshare/tushare",
 code,
 )
 continue
 try:
 df = cached\_loader\_fetch(
 source=self.name,
 symbol=code,
 timeframe=interval,
 start\_date=start\_date,
 end\_date=end\_date,
 fields=None,
 fetch=lambda code=code: self.\_fetch\_one(code, start\_date, end\_date, interval),
 )
 if df is not None and not df.empty:
 result\[code\] = df
 except Exception as exc:
 logger.warning("mootdx failed for %s: %s", code, exc)
 return result

 def \_fetch\_one(
 self, code: str, start\_date: str, end\_date: str, interval: str,
 ) -\> Optional\[pd.DataFrame\]:
 symbol = code.split(".")\[0\]
 client = self.\_get\_client()

 # Daily has a native date-range API; intraday and weekly/monthly
 # only expose offset-from-latest, so we page back through history
 # until the first row of the page is older than start\_date.
 if interval == "1D":
 df = client.get\_k\_data(code=symbol, start\_date=start\_date, end\_date=end\_date)
 return self.\_normalize\_daily(df)

 freq = \_DAILY\_FREQ.get(interval) or \_INTRADAY\_FREQ\[interval\]
 return self.\_fetch\_bars\_paginated(client, symbol, freq, start\_date, end\_date)

 @staticmethod
 def \_fetch\_bars\_paginated(
 client, symbol: str, freq: int, start\_date: str, end\_date: str,
 ) -\> Optional\[pd.DataFrame\]:
 """Walk backward through \`\`bars()\`\` pages until the requested
 window is covered, then clip and concatenate.

 Mootdx \`\`bars()\`\` returns the latest \`\`\_BARS\_PAGE\`\` rows by default;
 \`\`start=N\`\` skips the newest N rows. We page until the oldest row
 in a page is at or before \`\`start\_date\`\`, or until \`\`\_MAX\_PAGES\`\`
 is exhausted (very old or thinly-traded symbols).
 """
 start\_ts = pd.Timestamp(start\_date)
 chunks: list\[pd.DataFrame\] = \[\]
 for page in range(\_MAX\_PAGES):
 df = client.bars(
 symbol=symbol,
 frequency=freq,
 start=page \* \_BARS\_PAGE,
 offset=\_BARS\_PAGE,
 )
 if df is None or df.empty:
 break
 chunks.append(df)
 first\_dt = pd.to\_datetime(df\["datetime"\].iloc\[0\])
 if first\_dt <= start\_ts:
 break
 else:
 raise ValueError(
 "incomplete mootdx history: "
 f"{symbol} frequency={freq} hit {\_MAX\_PAGES} pages "
 f"without reaching {start\_date}"
 )
 if not chunks:
 return None
 combined = pd.concat(chunks, ignore\_index=False)
 return DataLoader.\_normalize\_bars(combined, start\_date, end\_date)

 @staticmethod
 def \_normalize\_daily(df: Optional\[pd.DataFrame\]) -> Optional\[pd.DataFrame\]:
 """Normalize \`get\_k\_data()\` output to the OHLCV contract.

 get\_k\_data returns columns \`\`\[open, close, high, low, vol, amount,\
 date, code\]\`\` with \`\`date\`\` as the index name.
 """
 if df is None or df.empty:
 return None
 out = df.rename(columns={"vol": "volume"}).copy()
 out.index = pd.to\_datetime(out.index)
 out.index.name = "trade\_date"
 for col in ("open", "high", "low", "close", "volume"):
 out\[col\] = pd.to\_numeric(out\[col\], errors="coerce")
 out = out\[\["open", "high", "low", "close", "volume"\]\].dropna(
 subset=\["open", "high", "low", "close"\]
 )
 return out.sort\_index() if not out.empty else None

 @staticmethod
 def \_normalize\_bars(
 df: Optional\[pd.DataFrame\], start\_date: str, end\_date: str,
 ) -\> Optional\[pd.DataFrame\]:
 """Normalize \`bars()\` output and clip to the requested window.

 bars() returns \`\`\[open, close, high, low, vol, amount, year, month,\
 day, hour, minute, datetime, volume\]\`\` with a datetime index.
 \`\`volume\`\` (lowercase, last column) is the canonical share count;
 \`\`vol\`\` is a historical alias kept by mootdx for compatibility.
 """
 if df is None or df.empty:
 return None
 out = df.copy()
 if "datetime" in out.columns:
 out\["trade\_date"\] = pd.to\_datetime(out\["datetime"\])
 out = out.set\_index("trade\_date")
 else:
 out.index = pd.to\_datetime(out.index)
 out.index.name = "trade\_date"
 out = out.sort\_index()
 for col in ("open", "high", "low", "close", "volume"):
 out\[col\] = pd.to\_numeric(out\[col\], errors="coerce")
 out = out\[\["open", "high", "low", "close", "volume"\]\].dropna(
 subset=\["open", "high", "low", "close"\]
 )
 # Inclusive end-of-day so a \`2025-02-01\` window keeps the 15:00 bar.
 end\_ts = pd.Timestamp(end\_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
 out = out.loc\[pd.Timestamp(start\_date):end\_ts\]
 return out if not out.empty else None