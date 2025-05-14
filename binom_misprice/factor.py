import warnings
import numpy as np
import pandas as pd
from datetime import datetime
import yfinance as yf
from .data import fetch_option_chain
from .tree import binomial_tree_price

def _normalize_ivs(ivs: np.ndarray) -> np.ndarray:
    """
    If any volatility > 1.0 (i.e. expressed as percent like 50.0),
    rescale by 100 to get decimal form (0.50). Leave values ≤ 1.0 unchanged.
    """
    return np.where(ivs > 1.0, ivs / 100.0, ivs)


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
    expiry : str
        "YYYY-MM-DD"
    sigma : float, optional
        Flat vol override; if None, use per-strike IV with hist‑vol fallback.
    r : float, default=0.03
    steps : int, default=2
    american : bool, default=False
    valuation_date : str, optional
        "YYYY-MM-DD"; defaults to today.

    Returns
    -------
    DataFrame[strike, market_price, theo_price, mispricing]
    """
    # 1) Determine valuation date
    if valuation_date:
        try:
            val_date = datetime.strptime(valuation_date, "%Y-%m-%d").date()
        except Exception:
            raise ValueError("valuation_date must be 'YYYY-MM-DD'")
    else:
        val_date = datetime.now().date()

    # 2) Fetch chain & spot
    chain, spot = fetch_option_chain(symbol, expiry)

    # 3) Compute dividend yield q
    tk = yf.Ticker(symbol)
    info = tk.info or {}
    q = info.get("dividendYield", 0.0) or 0.0
    if q == 0.0:
        divs = tk.dividends
        last_year = divs.last("365D").sum() if hasattr(divs, "last") else 0.0
        q = (last_year / spot) if (spot and last_year > 0) else 0.0

    # 4) Prepare market DataFrame and compute mid-price
    df = chain.calls.copy()
    if df.empty:
        raise ValueError("No call options found for expiry")
    # drop illiquid
    df = df[(df["bid"] > 0) & (df["ask"] > 0)].reset_index(drop=True)
    if df.empty:
        raise ValueError("All call bids or asks were zero")
    strikes = df["strike"].values
    market  = ((df["bid"] + df["ask"]) / 2).values

    # 5) Time to expiry in years
    expd = datetime.strptime(expiry, "%Y-%m-%d").date()
    if expd <= val_date:
        raise ValueError("expiry must be after valuation_date")
    T = (expd - val_date).days / 252.0

    # 6) Build IV array, normalize >100%, then fallback if missing
    if "impliedVolatility" in df.columns:
        ivs = df["impliedVolatility"].fillna(0.0).values
    else:
        ivs = np.zeros(len(df), dtype=float)

    ivs = _normalize_ivs(ivs)

    if sigma is not None:
        ivs[:] = sigma
    else:
        hist = tk.history(period="60d")["Close"].pct_change().dropna()
        hist_vol = float(hist.std() * np.sqrt(252)) if not hist.empty else 0.0

        missing = (ivs <= 0) | (~np.isfinite(ivs))
        if missing.any():
            missing_strikes = strikes[missing].tolist()
            warnings.warn(
                f"{symbol} {expiry}: impliedVol missing for strikes {missing_strikes}; "
                f"falling back to hist-vol={hist_vol:.4f}",
                UserWarning
            )
            ivs[missing] = hist_vol

    # 7) Compute theoretical prices via binomial tree
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
            american=american,
            q=q
        )[0]

    # 8) Compute mispricing safely
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
    Same IV‑normalization and fallback behavior as calls.
    """
    # 1) Determine valuation date
    if valuation_date:
        try:
            val_date = datetime.strptime(valuation_date, "%Y-%m-%d").date()
        except Exception:
            raise ValueError("valuation_date must be 'YYYY-MM-DD'")
    else:
        val_date = datetime.now().date()

    # 2) Fetch chain & spot
    chain, spot = fetch_option_chain(symbol, expiry)

    # 3) Compute dividend yield q
    tk = yf.Ticker(symbol)
    info = tk.info or {}
    q = info.get("dividendYield", 0.0) or 0.0
    if q == 0.0:
        divs = tk.dividends
        last_year = divs.last("365D").sum() if hasattr(divs, "last") else 0.0
        q = (last_year / spot) if (spot and last_year > 0) else 0.0

    # 4) Prepare market DataFrame and compute mid-price
    df = chain.puts.copy()
    if df.empty:
        raise ValueError("No put options found for expiry")
    # drop illiquid
    df = df[(df["bid"] > 0) & (df["ask"] > 0)].reset_index(drop=True)
    if df.empty:
        raise ValueError("All put bids or asks were zero")
    strikes = df["strike"].values
    market  = ((df["bid"] + df["ask"]) / 2).values

    # 5) Time to expiry
    expd = datetime.strptime(expiry, "%Y-%m-%d").date()
    if expd <= val_date:
        raise ValueError("expiry must be after valuation_date")
    T = (expd - val_date).days / 365.0

    # 6) Build IV array, normalize >100%, then fallback
    if "impliedVolatility" in df.columns:
        ivs = df["impliedVolatility"].fillna(0.0).values
    else:
        ivs = np.zeros(len(df), dtype=float)

    ivs = _normalize_ivs(ivs)

    if sigma is not None:
        ivs[:] = sigma
    else:
        hist = tk.history(period="60d")["Close"].pct_change().dropna()
        hist_vol = float(hist.std() * np.sqrt(252)) if not hist.empty else 0.0

        missing = (ivs <= 0) | (~np.isfinite(ivs))
        if missing.any():
            missing_strikes = strikes[missing].tolist()
            warnings.warn(
                f"{symbol} {expiry}: impliedVol missing for strikes {missing_strikes}; "
                f"falling back to hist-vol={hist_vol:.4f}",
                UserWarning
            )
            ivs[missing] = hist_vol

    # 7) Compute theoretical prices via binomial tree
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
            american=american,
            q=q
        )[0]

    # 8) Compute mispricing safely
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
