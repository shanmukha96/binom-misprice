import pandas as pd
from datetime import datetime, timedelta
from .factor import compute_call_mispricing, compute_put_mispricing

def compute_composite_mispricing(
    symbol: str,
    expiry: str,
    sigma: float = None,
    r: float = 0.03,
    steps: int = 2,
    american: bool = False,
    w_call: float = 0.5,
    w_put: float = 0.5,
    valuation_date: str = None
) -> pd.DataFrame:
    """
    Returns a DataFrame with columns:
      strike,
      market_call, theo_call, mispr_call,
      market_put,  theo_put,  mispr_put,
      market_composite, theo_composite, mispricing
    """
    # 1) Get call & put backtests
    cdf = compute_call_mispricing(
        symbol, expiry, sigma, r, steps, american, valuation_date
    ).rename(columns={
        "market_price": "market_call",
        "theo_price":   "theo_call",
        "mispricing":   "mispr_call"
    })

    pdf = compute_put_mispricing(
        symbol, expiry, sigma, r, steps, american, valuation_date
    ).rename(columns={
        "market_price": "market_put",
        "theo_price":   "theo_put",
        "mispricing":   "mispr_put"
    })

    # 2) Merge on strike
    merged = pd.merge(cdf, pdf, on="strike", how="inner")

    # 3) Composite prices & mispricing
    merged["market_composite"]  = w_call * merged["market_call"] + w_put * merged["market_put"]
    merged["theo_composite"]    = w_call * merged["theo_call"]   + w_put * merged["theo_put"]
    merged["mispricing"]        = (merged["market_composite"] - merged["theo_composite"]) / merged["theo_composite"]

    # 4) Attach symbol & valuation_date if present
    merged["symbol"] = symbol
    if valuation_date:
        merged["valuation_date"] = valuation_date

    # 5) Return desired columns
    return merged[[
        "symbol","valuation_date","strike",
        "market_call","theo_call","mispr_call",
        "market_put", "theo_put", "mispr_put",
        "market_composite","theo_composite","mispricing"
    ]]


def compute_mispricing_range(
    symbol: str,
    expiry: str,
    start_date: str,
    end_date: str,
    factor: str = "composite",
    sigma: float = None,
    r: float = 0.03,
    steps: int = 2,
    american: bool = False,
    w_call: float = 0.5,
    w_put: float = 0.5,
    output_path: str = None
) -> pd.DataFrame:
    # validate inputs
    sd = datetime.strptime(start_date, "%Y-%m-%d").date()
    ed = datetime.strptime(end_date,   "%Y-%m-%d").date()
    if ed < sd:
        raise ValueError("end_date must be on or after start_date")
    if factor not in ("call","put","composite"):
        raise ValueError("factor must be 'call', 'put', or 'composite'")

    frames = []
    curr = sd
    while curr <= ed:
        val_str = curr.strftime("%Y-%m-%d")
        try:
            if factor == "call":
                df = compute_call_mispricing(
                    symbol, expiry, sigma, r, steps, american, val_str
                )
                df["symbol"] = symbol
                df["valuation_date"] = val_str

            elif factor == "put":
                df = compute_put_mispricing(
                    symbol, expiry, sigma, r, steps, american, val_str
                )
                df["symbol"] = symbol
                df["valuation_date"] = val_str

            else:  # composite
                df = compute_composite_mispricing(
                    symbol, expiry, sigma, r, steps,
                    american, w_call, w_put, val_str
                )

            frames.append(df)

        except Exception:
            # skip dates/symbols with no data
            pass

        curr += timedelta(days=1)

    if not frames:
        raise ValueError("No data returned for given date range")

    result = pd.concat(frames, ignore_index=True)

    if output_path:
        result.to_csv(output_path, index=False)

    return result
