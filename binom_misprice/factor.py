import warnings
import numpy as np
import pandas as pd
from datetime import datetime
import yfinance as yf
from .data import fetch_option_chain
from .tree import binomial_tree_price

def compute_call_mispricing(
    symbol: str,
    expiry: str,
    sigma: float = None,
    r: float = 0.03,
    steps: int = 2,
    american: bool = False,
    valuation_date: str = None
) -> pd.DataFrame:
    """
    Compute call mispricing: (market_price - theoretical_price) / theoretical_price
    If impliedVolatility is missing, falls back to 60-day historical vol (with a warning).
    Accepts an override `sigma` for volatility if provided.
    """
    # 1) Valuation date
    if valuation_date:
        try:
            val_date = datetime.strptime(valuation_date, "%Y-%m-%d").date()
        except:
            raise ValueError("valuation_date must be 'YYYY-MM-DD'")
    else:
        val_date = datetime.now().date()

    # 2) Fetch option chain & spot
    chain, spot = fetch_option_chain(symbol, expiry)

    # 3) Dividend yield (q) fallback
    ticker = yf.Ticker(symbol)
    info = ticker.info
    q = info.get("dividendYield") or 0.0
    if q <= 0:
        divs = ticker.dividends
        last_year = divs.last("365D").sum()
        q = (last_year / spot) if (spot and last_year>0) else 0.0

    # 4) Build DataFrame
    df = chain.calls.copy()
    if df.empty:
        raise ValueError("No call options for expiry")
    strikes = df["strike"].values
    market  = df["lastPrice"].values

    # 5) Time to expiration
    expd = datetime.strptime(expiry, "%Y-%m-%d").date()
    if expd <= val_date:
        raise ValueError("expiry must be after valuation_date")
    T = (expd - val_date).days / 252.0

    # 6) Implied-vol array with fallback to historical vol
    if "impliedVolatility" in df.columns:
        ivs = df["impliedVolatility"].fillna(0.0).values
    else:
        ivs = np.zeros(len(df))

    # User override for sigma?
    if sigma is not None:
        ivs = np.full_like(ivs, sigma, dtype=float)
    else:
        # compute 60-day historical vol
        hist = ticker.history(period="60d")["Close"].pct_change().dropna()
        hist_vol = float(hist.std() * np.sqrt(252)) if not hist.empty else 0.0

        # identify missing IVs
        missing = (ivs <= 0) | (~np.isfinite(ivs))
        if missing.any():
            missing_strikes = strikes[missing].tolist()
            warnings.warn(
                f"{symbol} {expiry}: impliedVolatility missing for strikes {missing_strikes}; "
                f"falling back to historical vol={hist_vol:.4f}",
                UserWarning
            )
            ivs[missing] = hist_vol

    # 7) Compute theoretical prices per strike
    theo_list = []
    for K, iv in zip(strikes, ivs):
        price = binomial_tree_price(
            S=spot,
            strikes=[K],
            T=T,
            r=r,
            sigma=iv,
            steps=steps,
            opt_type='c',
            american=american,
            q=q
        )[0]
        theo_list.append(price)
    theo = np.array(theo_list)

    # 8) Safe mispricing calc
    with np.errstate(divide='ignore', invalid='ignore'):
        mis = (market - theo) / theo
    mis = np.where(theo <= 0, np.nan, mis)

    out = pd.DataFrame({
        "strike":       strikes,
        "market_price": market,
        "theo_price":   theo,
        "mispricing":   mis
    })
    return out[out["theo_price"] > 0].reset_index(drop=True)


def compute_put_mispricing(
    symbol: str,
    expiry: str,
    sigma: float = None,
    r: float = 0.03,
    steps: int = 2,
    american: bool = False,
    valuation_date: str = None
) -> pd.DataFrame:
    """
    Compute put mispricing: (market_price - theoretical_price) / theoretical_price
    If impliedVolatility is missing, falls back to 60-day historical vol (with a warning).
    Accepts an override `sigma` for volatility if provided.
    """
    # 1) Valuation date
    if valuation_date:
        try:
            val_date = datetime.strptime(valuation_date, "%Y-%m-%d").date()
        except:
            raise ValueError("valuation_date must be 'YYYY-MM-DD'")
    else:
        val_date = datetime.now().date()

    # 2) Fetch option chain & spot
    chain, spot = fetch_option_chain(symbol, expiry)

    # 3) Dividend yield (q) fallback
    ticker = yf.Ticker(symbol)
    info = ticker.info
    q = info.get("dividendYield") or 0.0
    if q <= 0:
        divs = ticker.dividends
        last_year = divs.last("365D").sum()
        q = (last_year / spot) if (spot and last_year>0) else 0.0

    # 4) Build DataFrame
    df = chain.puts.copy()
    if df.empty:
        raise ValueError("No put options for expiry")
    strikes = df["strike"].values
    market  = df["lastPrice"].values

    # 5) Time to expiration
    expd = datetime.strptime(expiry, "%Y-%m-%d").date()
    if expd <= val_date:
        raise ValueError("expiry must be after valuation_date")
    T = (expd - val_date).days / 252.0

    # 6) Implied-vol array with fallback to historical vol
    if "impliedVolatility" in df.columns:
        ivs = df["impliedVolatility"].fillna(0.0).values
    else:
        ivs = np.zeros(len(df))

    # User override for sigma?
    if sigma is not None:
        ivs = np.full_like(ivs, sigma, dtype=float)
    else:
        # compute 60-day historical vol
        hist = ticker.history(period="60d")["Close"].pct_change().dropna()
        hist_vol = float(hist.std() * np.sqrt(252)) if not hist.empty else 0.0

        # identify missing IVs
        missing = (ivs <= 0) | (~np.isfinite(ivs))
        if missing.any():
            missing_strikes = strikes[missing].tolist()
            warnings.warn(
                f"{symbol} {expiry}: impliedVolatility missing for strikes {missing_strikes}; "
                f"falling back to historical vol={hist_vol:.4f}",
                UserWarning
            )
            ivs[missing] = hist_vol

    # 7) Compute theoretical prices per strike
    theo_list = []
    for K, iv in zip(strikes, ivs):
        price = binomial_tree_price(
            S=spot,
            strikes=[K],
            T=T,
            r=r,
            sigma=iv,
            steps=steps,
            opt_type='p',
            american=american,
            q=q
        )[0]
        theo_list.append(price)
    theo = np.array(theo_list)

    # 8) Safe mispricing calc
    with np.errstate(divide='ignore', invalid='ignore'):
        mis = (market - theo) / theo
    mis = np.where(theo <= 0, np.nan, mis)

    out = pd.DataFrame({
        "strike":       strikes,
        "market_price": market,
        "theo_price":   theo,
        "mispricing":   mis
    })
    return out[out["theo_price"] > 0].reset_index(drop=True)
