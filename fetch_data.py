import pandas as pd
import yfinance as yf
from binom_misprice import compute_mispricing_batch

def fetch_dividend_yield(symbol: str) -> float:
    """
    Returns the current dividend yield for `symbol`, or
    falls back to (last 60 trading days of dividends) / spot price.
    """
    tk = yf.Ticker(symbol)
    info = tk.info or {}
    q = info.get("dividendYield", 0.0) or 0.0

    if q == 0.0:
        # fallback: sum dividends over last 60 trading days
        hist = tk.dividends
        if hasattr(hist, "last"):
            last_year = hist.last("60D").sum()
        else:
            # crude fallback if .last isn't available
            last_year = hist[-60:].sum()
        spot = tk.history(period="1d")["Close"].iloc[-1]
        q = (last_year / spot) if (spot and last_year > 0) else 0.0

    return q

def main():
    # 1. Define your universe & parameters
    symbols    = [
      "AAPL","MSFT","NVDA","GOOG","GOOGL","META",
      "ORCL","INTC","CSCO","ADBE","CRM",
      "UNH","JNJ","PFE","MRK","ABBV","LLY","ABT","MDT","DHR",
      "BRK-B","JPM","V","MA","BAC","WFC","C","GS","SPGI",
      "PG","KO","PEP",
      "WMT","COST","MCD","SBUX","NKE",
      "XOM","CVX","COP",
      "CAT","MMM","HON","UNP","UPS","FDX",
      "PLD","AMT",
      "VZ","T"
    ]
    start_date = "2025-01-01"
    end_date   = "2025-03-31"
    expiry     = "2025-06-20"
    w_call     = 0.5
    w_put      = 0.5

    # 2. Compute composite mispricing for all symbols in parallel
    df = compute_mispricing_batch(
        tickers     = symbols,
        expiry      = expiry,
        start_date  = start_date,
        end_date    = end_date,
        factor      = "composite",
        sigma       = None,
        r           = 0.03,
        steps       = 3,
        american    = True,
        w_call      = w_call,
        w_put       = w_put,
        max_workers = 8,
        output_path = None    # we’ll save after adding yields
    )

    # 3. Fetch per-symbol dividend yields
    q_map = {}
    for sym in df['symbol'].unique():
        try:
            q_map[sym] = fetch_dividend_yield(sym)
        except Exception:
            q_map[sym] = 0.0

    # 4. Attach to your DataFrame
    df['dividend_yield'] = df['symbol'].map(q_map)

    # 5. Save final CSV
    df.to_csv("mispricing_Q1_2025_with_yields.csv", index=False)
    print(f"Saved mispricing_Q1_2025_with_yields.csv ({len(df)} rows)")

if __name__ == "__main__":
    main()
