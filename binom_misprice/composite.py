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
    if not (0 <= w_call <= 1 and 0 <= w_put <= 1 and abs(w_call + w_put - 1) < 1e-6):
        raise ValueError("Weights must be between 0 and 1 and sum to 1")

    cdf = compute_call_mispricing(
        symbol, expiry, sigma, r, steps, american, valuation_date
    )
    pdf = compute_put_mispricing(
        symbol, expiry, sigma, r, steps, american, valuation_date
    )

    merged = pd.merge(cdf, pdf, on="strike", suffixes=("_c", "_p"))
    merged["mispricing"] = w_call * merged["mispricing_c"] + w_put * merged["mispricing_p"]
    return merged[["strike", "mispricing"]]


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
    # validate dates & factor...
    sd = datetime.strptime(start_date, "%Y-%m-%d").date()
    ed = datetime.strptime(end_date, "%Y-%m-%d").date()
    if ed < sd:
        raise ValueError("end_date must be on or after start_date")
    if factor not in ("call", "put", "composite"):
        raise ValueError("factor must be 'call','put', or 'composite'")

    frames = []
    curr = sd
    while curr <= ed:
        val_str = curr.strftime("%Y-%m-%d")
        try:
            if factor == "call":
                df = compute_call_mispricing(symbol, expiry, sigma, r, steps, american, val_str)
            elif factor == "put":
                df = compute_put_mispricing(symbol, expiry, sigma, r, steps, american, val_str)
            else:
                df = compute_composite_mispricing(
                    symbol, expiry, sigma, r, steps,
                    american, w_call, w_put, val_str
                )
            df["valuation_date"] = val_str
            frames.append(df)
        except Exception:
            pass
        curr += timedelta(days=1)

    if not frames:
        raise ValueError("No data returned for given date range")
    result = pd.concat(frames, ignore_index=True)
    if output_path:
        result.to_csv(output_path, index=False)
    return result
