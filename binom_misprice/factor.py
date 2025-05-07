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

    Parameters
    ----------
    symbol : str
        Ticker symbol, e.g. "AAPL"
    expiry : str
        Expiration date, "YYYY-MM-DD"
    sigma : float, optional
        Flat volatility override. If None, uses impliedVolatility from yfinance,
        falling back to 60-day historical vol if missing.
    r : float, default=0.03
        Risk-free rate (annual, continuous compounding).
    steps : int, default=2
        Number of binomial‐tree steps.
    american : bool, default=False
        If True, allow early exercise (American option).
    valuation_date : str, optional
        Valuation date "YYYY-MM-DD". If None, uses today.

    Returns
    -------
    DataFrame
        strike | market_price | theo_price | mispricing
    """
    # 1) valuation date
    if valuation_date:
        try:
            val_date = datetime.strptime(valuation_date, "%Y-%m-%d").date()
        except:
            raise ValueError("valuation_date must be 'YYYY-MM-DD'")
    else:
        val_date = datetime.now().date()

    # 2) fetch chain + spot
    chain, spot = fetch_option_chain(symbol, expiry)

    # 3) dividend yield q
    tk = yf.Ticker(symbol)
    info = tk.info or {}
    q = info.get("dividendYield", 0.0) or 0.0
    if q == 0.0:
        divs = tk.dividends
        last_year = divs.last("365D").sum() if hasattr(divs, "last") else 0.0
        q = (last_year / spot) if (spot and last_year > 0) else 0.0

    # 4) build market DataFrame
    df = chain.calls.copy()
    if df.empty:
        raise ValueError("No call options for expiry")
    strikes = df["strike"].values
    market  = df["lastPrice"].values

    # 5) time to expiration (in years, 252 trading days)
    expd = datetime.strptime(expiry, "%Y-%m-%d").date()
    if expd <= val_date:
        raise ValueError("expiry must be after valuation_date")
    T = (expd - val_date).days / 252.0

    # 6) implied‐vol array with fallback
    if "impliedVolatility" in df.columns:
        ivs = df["impliedVolatility"].fillna(0.0).values
    else:
        ivs = np.zeros(len(df), dtype=float)

    # override if sigma provided
    if sigma is not None:
        ivs[:] = sigma
    else:
        # compute 60d hist vol
        hist = tk.history(period="60d")["Close"].pct_change().dropna()
        hist_vol = float(hist.std() * np.sqrt(252)) if not hist.empty else 0.0

        missing = (ivs <= 0) | (~np.isfinite(ivs))
        if missing.any():
            missing_strikes = strikes[missing].tolist()
            warnings.warn(
                f"{symbol} {expiry}: impliedVolatility missing for strikes "
                f"{missing_strikes}; falling back to historical vol={hist_vol:.4f}",
                UserWarning
            )
            ivs[missing] = hist_vol

    # 7) compute theoretical prices
    # we have to loop because sigmas may differ per strike
    theo = np.empty_like(ivs)
    for i, (K, iv) in enumerate(zip(strikes, ivs)):
        theo[i] = binomial_tree_price(
            S=spot,
            strikes=[K],
            T=T,
            r=r,
            sigma=iv,
            steps=steps,
            opt_type='c',
            american=american
        )[0]

    # 8) mispricing, with safe divide
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
    Same fallback behavior for implied vol and sigma override.
    """
    if valuation_date:
        try:
            val_date = datetime.strptime(valuation_date, "%Y-%m-%d").date()
        except:
            raise ValueError("valuation_date must be 'YYYY-MM-DD'")
    else:
        val_date = datetime.now().date()

    chain, spot = fetch_option_chain(symbol, expiry)

    tk = yf.Ticker(symbol)
    info = tk.info or {}
    q = info.get("dividendYield", 0.0) or 0.0
    if q == 0.0:
        divs = tk.dividends
        last_year = divs.last("365D").sum() if hasattr(divs, "last") else 0.0
        q = (last_year / spot) if (spot and last_year > 0) else 0.0

    df = chain.puts.copy()
    if df.empty:
        raise ValueError("No put options for expiry")
    strikes = df["strike"].values
    market  = df["lastPrice"].values

    expd = datetime.strptime(expiry, "%Y-%m-%d").date()
    if expd <= val_date:
        raise ValueError("expiry must be after valuation_date")
    T = (expd - val_date).days / 252.0

    if "impliedVolatility" in df.columns:
        ivs = df["impliedVolatility"].fillna(0.0).values
    else:
        ivs = np.zeros(len(df), dtype=float)

    if sigma is not None:
        ivs[:] = sigma
    else:
        hist = tk.history(period="60d")["Close"].pct_change().dropna()
        hist_vol = float(hist.std() * np.sqrt(252)) if not hist.empty else 0.0

        missing = (ivs <= 0) | (~np.isfinite(ivs))
        if missing.any():
            missing_strikes = strikes[missing].tolist()
            warnings.warn(
                f"{symbol} {expiry}: impliedVolatility missing for strikes "
                f"{missing_strikes}; falling back to historical vol={hist_vol:.4f}",
                UserWarning
            )
            ivs[missing] = hist_vol

    theo = np.empty_like(ivs)
    for i, (K, iv) in enumerate(zip(strikes, ivs)):
        theo[i] = binomial_tree_price(
            S=spot,
            strikes=[K],
            T=T,
            r=r,
            sigma=iv,
            steps=steps,
            opt_type='p',
            american=american
        )[0]

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
