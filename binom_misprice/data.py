import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

def fetch_option_chain(symbol: str, expiry: str):
    """
    Fetch option chain and the underlying spot price (last available Close
    on or before the requested expiry date). Raises ValueError on invalid input
    or missing data.
    """
    # 1) Validate inputs
    if not isinstance(symbol, str):
        raise ValueError("symbol must be a string")
    try:
        expd = datetime.strptime(expiry, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("expiry must be in 'YYYY-MM-DD' format")

    # 2) Instantiate ticker and check history
    tk = yf.Ticker(symbol)
    try:
        hist_check = tk.history(period="1d")
    except Exception as e:
        raise ValueError(f"Ticker '{symbol}' returned no historical prices: {e}")
    if hist_check.empty:
        raise ValueError(f"Ticker '{symbol}' returned no historical prices")

    # 3) Pick the expiry date (fallback to nearest if not listed)
    options = tk.options
    if not options:
        raise ValueError(f"No option expirations found for {symbol}")
    if expiry in options:
        chosen = expiry
    else:
        avail    = [datetime.strptime(d, "%Y-%m-%d").date() for d in options]
        closest  = min(avail, key=lambda d: abs((d - expd).days))
        chosen   = closest.isoformat()

    # 4) Fetch the option chain
    try:
        chain = tk.option_chain(chosen)
    except Exception as e:
        raise ValueError(f"Failed to fetch option chain for {symbol} on {chosen}: {e}")

    # 5) Grab the last 7 calendar days of history, drop tz info
    try:
        hist = tk.history(period="30d")
    except Exception as e:
        raise ValueError(f"No price history for {symbol}: {e}")
    if hist.empty or "Close" not in hist.columns:
        raise ValueError(f"No recent closing data for {symbol}")
    hist.index = hist.index.tz_localize(None)

    # 6) Filter to dates ≤ expiry, pick last close
    closes = hist["Close"]
    expiry_ts = pd.to_datetime(expiry)
    closes_up_to = closes.loc[:expiry_ts]
    if closes_up_to.empty:
        raise ValueError(f"No closing price for {symbol} on or before {expiry}")
    spot = float(closes_up_to.iloc[-1])

    return chain, spot
